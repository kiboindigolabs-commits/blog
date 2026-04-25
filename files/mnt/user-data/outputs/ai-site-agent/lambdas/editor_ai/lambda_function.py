import json
import os
import boto3
import anthropic

s3 = boto3.client("s3")
ssm = boto3.client("ssm")
S3_BUCKET = os.environ["S3_BUCKET"]
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
WP_URL = os.environ.get("WP_URL", "https://reslabo.jp")
GENRE = os.environ.get("GENRE", "AI tools and services")


def get_api_key():
    resp = ssm.get_parameter(Name="/ai-site/claude/api_key", WithDecryption=True)
    return resp["Parameter"]["Value"]


def lambda_handler(event, context):
    date = event["date"]
    raw_key = event["s3_key"]

    obj = s3.get_object(Bucket=S3_BUCKET, Key=raw_key)
    raw_data = json.loads(obj["Body"].read())

    products = raw_data["products"]
    products_text = "\n".join(
        f"- {p['title']} ({p['source']}): {p['description']}" for p in products
    )

    client = anthropic.Anthropic(api_key=get_api_key())

    prompt = f"""あなたはAI専門メディアのエディターです。
サイトURL: {WP_URL}
ジャンル: {GENRE}
対象読者: AIに興味を持つ日本語話者（初心者〜中級者）

以下の最新AIトレンド情報をもとに、1本の記事アウトラインを作成してください。

【収集したトレンド情報】
{products_text}

以下のJSON形式で回答してください（他のテキストは不要）：
{{
  "title": "記事タイトル（SEO最適化・40文字以内）",
  "meta_description": "メタディスクリプション（120文字以内）",
  "target_reader": "ターゲット読者像",
  "main_topic": "主テーマとなるAIツール/サービス名",
  "keywords": ["キーワード1", "キーワード2", "キーワード3"],
  "sections": [
    {{"heading": "H2見出し", "points": ["書くべきポイント1", "書くべきポイント2"]}},
    {{"heading": "H2見出し", "points": ["書くべきポイント1", "書くべきポイント2"]}},
    {{"heading": "H2見出し", "points": ["書くべきポイント1", "書くべきポイント2"]}}
  ],
  "cta": "記事末尾のCTA文（読者への呼びかけ）",
  "source_url": "参考にしたトレンド情報のURL"
}}"""

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    outline = json.loads(raw_text)
    outline["date"] = date

    outline_key = f"outlines/{date}.json"
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=outline_key,
        Body=json.dumps(outline, ensure_ascii=False, indent=2),
        ContentType="application/json",
    )
    print(f"Outline saved: {outline['title']}")

    return {"date": date, "s3_key": outline_key, "title": outline["title"]}
