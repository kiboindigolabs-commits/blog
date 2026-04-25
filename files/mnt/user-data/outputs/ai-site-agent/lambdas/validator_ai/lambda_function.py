import json
import os
import boto3
import anthropic

s3 = boto3.client("s3")
ssm = boto3.client("ssm")
sns = boto3.client("sns")
S3_BUCKET = os.environ["S3_BUCKET"]
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
PASS_THRESHOLD = float(os.environ.get("PASS_THRESHOLD", "0.85"))
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")


def get_api_key():
    resp = ssm.get_parameter(Name="/ai-site/claude/api_key", WithDecryption=True)
    return resp["Parameter"]["Value"]


def lambda_handler(event, context):
    date = event["date"]
    draft_key = event["s3_key"]
    outline_key = event["outline_key"]
    retry_count = event.get("retry_count", 0)

    obj = s3.get_object(Bucket=S3_BUCKET, Key=draft_key)
    article = json.loads(obj["Body"].read())

    client = anthropic.Anthropic(api_key=get_api_key())

    prompt = f"""以下のブログ記事をチェックし、品質スコアを返してください。

【記事タイトル】
{article['title']}

【本文（HTML）】
{article['html_content'][:3000]}

以下の3項目を0.0〜1.0で評価し、JSON形式で回答してください（他のテキスト不要）：
{{
  "fact_accuracy": 0.0〜1.0（事実の正確性・誤情報がないか）,
  "seo_structure": 0.0〜1.0（見出し構成・文字数・キーワード活用）,
  "compliance": 0.0〜1.0（著作権・過度な誇張表現・薬機法等の問題がないか）,
  "total_score": 0.0〜1.0（上記3項目の加重平均: fact×0.4 + seo×0.3 + compliance×0.3）,
  "issues": ["指摘事項1", "指摘事項2"],
  "feedback": "ライターへのフィードバック（改善点の具体的なアドバイス）"
}}"""

    response = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = response.content[0].text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
    score = json.loads(raw_text)

    total = score["total_score"]
    print(f"Validation score: {total:.2f} (retry={retry_count})")
    print(f"Issues: {score.get('issues', [])}")

    if total >= PASS_THRESHOLD:
        result = "PASS"
    elif retry_count < MAX_RETRIES:
        result = "RETRY"
    else:
        result = "MANUAL_REVIEW"
        if SNS_TOPIC_ARN:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"[reslabo.jp] 手動レビュー依頼: {article['title']}",
                Message=(
                    f"記事が{MAX_RETRIES}回のリトライ後も基準スコアを満たしませんでした。\n\n"
                    f"タイトル: {article['title']}\n"
                    f"スコア: {total:.2f} (基準: {PASS_THRESHOLD})\n"
                    f"指摘事項: {score.get('issues', [])}\n"
                    f"フィードバック: {score.get('feedback', '')}\n"
                    f"下書きS3キー: s3://{S3_BUCKET}/{draft_key}"
                ),
            )

    return {
        "date": date,
        "s3_key": draft_key,
        "outline_key": outline_key,
        "retry_count": retry_count + 1,
        "validation_result": result,
        "score": score,
    }
