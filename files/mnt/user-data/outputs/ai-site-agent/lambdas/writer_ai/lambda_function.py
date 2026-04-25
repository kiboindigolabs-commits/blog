import json
import os
import boto3
import anthropic

s3 = boto3.client("s3")
ssm = boto3.client("ssm")
S3_BUCKET = os.environ["S3_BUCKET"]
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
WP_URL = os.environ.get("WP_URL", "https://reslabo.jp")


def get_api_key():
    resp = ssm.get_parameter(Name="/ai-site/claude/api_key", WithDecryption=True)
    return resp["Parameter"]["Value"]


def lambda_handler(event, context):
    date = event["date"]
    outline_key = event["s3_key"]
    retry_count = event.get("retry_count", 0)

    obj = s3.get_object(Bucket=S3_BUCKET, Key=outline_key)
    outline = json.loads(obj["Body"].read())

    sections_text = "\n".join(
        f"## {s['heading']}\n" + "\n".join(f"  - {p}" for p in s["points"])
        for s in outline["sections"]
    )

    client = anthropic.Anthropic(api_key=get_api_key())

    prompt = f"""あなたはAI専門メディアのライターです。
以下のアウトラインをもとに、日本語のブログ記事をHTML形式で書いてください。

【記事情報】
タイトル: {outline['title']}
対象読者: {outline['target_reader']}
キーワード: {', '.join(outline['keywords'])}
参考URL: {outline.get('source_url', '')}

【アウトライン】
{sections_text}

【執筆ルール】
- 全体で2000〜3000文字
- 各H2セクションは400〜600文字
- 語尾は「です・ます」調
- 専門用語には簡単な説明を添える
- 読者が行動したくなる具体的な情報を含める
- CTA（記事末尾）: {outline['cta']}

以下のJSON形式で回答してください（他のテキストは不要）：
{{
  "title": "{outline['title']}",
  "html_content": "<h2>...</h2><p>...</p>...",
  "excerpt": "記事の抜粋（150文字以内）",
  "tags": ["タグ1", "タグ2", "タグ3"],
  "category": "AIツール",
  "sns_text": "X(Twitter)投稿用テキスト（140文字以内・ハッシュタグ含む）"
}}"""

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=6000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    article = json.loads(raw_text)
    article["date"] = date
    article["retry_count"] = retry_count
    article["meta_description"] = outline.get("meta_description", "")
    article["keywords"] = outline.get("keywords", [])

    draft_key = f"drafts/{date}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=draft_key,
        Body=json.dumps(article, ensure_ascii=False, indent=2),
        ContentType="application/json",
    )
    print(f"Draft saved: {article['title']} (retry={retry_count})")

    return {"date": date, "s3_key": draft_key, "outline_key": outline_key, "retry_count": retry_count}
