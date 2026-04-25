import json
import os
import base64
import urllib.request
import urllib.error
import boto3
from datetime import datetime, timezone

s3 = boto3.client("s3")
ssm = boto3.client("ssm")
sns = boto3.client("sns")
S3_BUCKET = os.environ["S3_BUCKET"]
WP_URL = os.environ.get("WP_URL", "https://reslabo.jp")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")


def get_wp_credentials():
    username = ssm.get_parameter(Name="/ai-site/wp/username", WithDecryption=True)["Parameter"]["Value"]
    password = ssm.get_parameter(Name="/ai-site/wp/app_password", WithDecryption=True)["Parameter"]["Value"]
    return username, password


def get_or_create_category(auth_header, category_name):
    """カテゴリを取得または作成してIDを返す"""
    url = f"{WP_URL}/wp-json/wp/v2/categories?search={urllib.parse.quote(category_name)}"
    req = urllib.request.Request(url, headers={"Authorization": auth_header})
    with urllib.request.urlopen(req, timeout=10) as resp:
        categories = json.loads(resp.read())
    if categories:
        return categories[0]["id"]

    data = json.dumps({"name": category_name}).encode()
    req = urllib.request.Request(
        f"{WP_URL}/wp-json/wp/v2/categories",
        data=data,
        headers={"Authorization": auth_header, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())["id"]


def get_or_create_tags(auth_header, tag_names):
    """タグを取得または作成してID一覧を返す"""
    import urllib.parse
    tag_ids = []
    for name in tag_names:
        url = f"{WP_URL}/wp-json/wp/v2/tags?search={urllib.parse.quote(name)}"
        req = urllib.request.Request(url, headers={"Authorization": auth_header})
        with urllib.request.urlopen(req, timeout=10) as resp:
            tags = json.loads(resp.read())
        if tags:
            tag_ids.append(tags[0]["id"])
        else:
            data = json.dumps({"name": name}).encode()
            req = urllib.request.Request(
                f"{WP_URL}/wp-json/wp/v2/tags",
                data=data,
                headers={"Authorization": auth_header, "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                tag_ids.append(json.loads(resp.read())["id"])
    return tag_ids


def lambda_handler(event, context):
    import urllib.parse

    date = event["date"]
    draft_key = event["s3_key"]

    obj = s3.get_object(Bucket=S3_BUCKET, Key=draft_key)
    article = json.loads(obj["Body"].read())

    username, app_password = get_wp_credentials()
    token = base64.b64encode(f"{username}:{app_password}".encode()).decode()
    auth_header = f"Basic {token}"

    category_id = get_or_create_category(auth_header, article.get("category", "AIツール"))
    tag_ids = get_or_create_tags(auth_header, article.get("tags", []))

    post_data = {
        "title": article["title"],
        "content": article["html_content"],
        "excerpt": article.get("excerpt", ""),
        "status": "publish",
        "categories": [category_id],
        "tags": tag_ids,
        "meta": {
            "_yoast_wpseo_metadesc": article.get("meta_description", ""),
            "_yoast_wpseo_focuskw": article.get("keywords", [""])[0],
        },
    }

    data = json.dumps(post_data, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{WP_URL}/wp-json/wp/v2/posts",
        data=data,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json; charset=utf-8",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        wp_response = json.loads(resp.read())

    post_id = wp_response["id"]
    post_url = wp_response["link"]
    print(f"Published: {article['title']} → {post_url}")

    published_key = f"published/{date}.json"
    article["wp_post_id"] = post_id
    article["wp_post_url"] = post_url
    article["published_at"] = datetime.now(timezone.utc).isoformat()
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=published_key,
        Body=json.dumps(article, ensure_ascii=False, indent=2),
        ContentType="application/json",
    )

    if SNS_TOPIC_ARN:
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"[reslabo.jp] 記事公開完了: {article['title']}",
            Message=f"記事が公開されました。\n\nタイトル: {article['title']}\nURL: {post_url}\n日付: {date}",
        )

    return {
        "date": date,
        "wp_post_id": post_id,
        "wp_post_url": post_url,
        "title": article["title"],
    }
