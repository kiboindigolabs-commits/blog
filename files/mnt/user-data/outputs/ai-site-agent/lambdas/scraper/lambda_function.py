import json
import os
import boto3
import urllib.request
import urllib.error
from datetime import datetime, timezone

s3 = boto3.client("s3")
S3_BUCKET = os.environ["S3_BUCKET"]


def fetch_producthunt_ai():
    """Product Hunt の AI カテゴリからトレンド商品を取得"""
    url = "https://www.producthunt.com/feed?category=artificial-intelligence"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")
        return parse_rss(content)
    except Exception as e:
        print(f"ProductHunt fetch error: {e}")
        return []


def parse_rss(xml_content):
    items = []
    import re
    titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", xml_content)
    links = re.findall(r"<link>(https?://[^<]+)</link>", xml_content)
    descriptions = re.findall(r"<description><!\[CDATA\[(.*?)\]\]></description>", xml_content, re.DOTALL)

    for i, title in enumerate(titles[1:6], 0):  # 最大5件、先頭（フィードタイトル）をスキップ
        items.append({
            "title": title.strip(),
            "url": links[i + 1] if i + 1 < len(links) else "",
            "description": descriptions[i][:300].strip() if i < len(descriptions) else "",
            "source": "Product Hunt",
            "category": "AI tools",
        })
    return items


def fetch_hackernews_ai():
    """Hacker News から AI 関連のトップ記事を取得"""
    try:
        with urllib.request.urlopen("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10) as resp:
            story_ids = json.loads(resp.read())[:30]

        items = []
        for sid in story_ids:
            with urllib.request.urlopen(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=5) as resp:
                story = json.loads(resp.read())
            if story and story.get("type") == "story":
                title = story.get("title", "").lower()
                if any(kw in title for kw in ["ai", "llm", "gpt", "claude", "gemini", "openai", "machine learning"]):
                    items.append({
                        "title": story.get("title", ""),
                        "url": story.get("url", f"https://news.ycombinator.com/item?id={sid}"),
                        "description": f"Hacker News score: {story.get('score', 0)}",
                        "source": "Hacker News",
                        "category": "AI news",
                    })
                    if len(items) >= 5:
                        break
        return items
    except Exception as e:
        print(f"HackerNews fetch error: {e}")
        return []


def lambda_handler(event, context):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    products = []
    products.extend(fetch_producthunt_ai())
    products.extend(fetch_hackernews_ai())

    if not products:
        raise RuntimeError("スクレイプ結果が0件です。ソースを確認してください。")

    payload = {
        "date": today,
        "products": products,
        "count": len(products),
    }

    key = f"raw/{today}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(payload, ensure_ascii=False, indent=2),
        ContentType="application/json",
    )
    print(f"Saved {len(products)} items to s3://{S3_BUCKET}/{key}")

    return {"date": today, "s3_key": key, "count": len(products)}
