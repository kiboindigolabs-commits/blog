#!/usr/bin/env python3
"""
AI記事自動生成スクリプト
キーワードを入力するとClaude APIが記事を生成し、Obsidianに下書き保存します。

使い方:
  python generate-article.py "ChatGPT 使い方"
  python generate-article.py "おすすめ AIツール 無料"

事前準備:
  pip install -r scripts/requirements.txt
  環境変数 ANTHROPIC_API_KEY を設定すること
"""

import anthropic
import sys
import os
import re
from datetime import datetime
from pathlib import Path

# 設定
VAULT_POSTS_PATH = Path(r"C:\obsidian-vault\blog\posts")
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096

SYSTEM_PROMPT = """あなたはSEOに詳しい日本語ブログライターです。
AIツール・ガジェット・Web系のアフィリエイトブログ記事を書くことが得意です。
読者の悩みを解決する、わかりやすくて読みやすい記事を書いてください。"""

ARTICLE_PROMPT = """以下のキーワードについて、Hugoブログ用のmarkdown記事を書いてください。

キーワード: {keyword}

## 出力形式（必ずこの形式で出力すること）

```markdown
---
title: "【年号】キーワードを含んだ魅力的なタイトル"
date: {date}
draft: true
tags: ["タグ1", "タグ2", "タグ3"]
categories: ["AIツール紹介"]
description: "記事の概要を120文字以内で"
---

## はじめに
（読者の悩みに共感する導入文 200字程度）

{{{{< box type="point" title="この記事でわかること" >}}}}
- ポイント1
- ポイント2
- ポイント3
{{{{< /box >}}}}

## （メインコンテンツのh2見出し）

（本文）

## おすすめランキング

{{{{< ranking rank="1" name="ツール名" stars="5" url="https://example.com" btntext="無料で試す" >}}}}
ツールの特徴を2〜3行で説明
{{{{< /ranking >}}}}

{{{{< ranking rank="2" name="ツール名" stars="4" url="https://example.com" btntext="詳細を見る" >}}}}
ツールの特徴を2〜3行で説明
{{{{< /ranking >}}}}

## まとめ

{{{{< box type="good" title="結論" >}}}}
この記事のまとめをここに書く
{{{{< /box >}}}}

{{{{< btn url="https://example.com" text="おすすめツールを無料で試す" color="orange" >}}}}
```

## 条件
- 全体で2000〜3000文字程度
- h2/h3 見出しを使った読みやすい構成
- ショートコード（box, ranking, btn）を自然に使う
- アフィリエイトリンクのURLは実在する適切なURLを使う
- 日本語で書く
- コードブロック(```)の外側だけを出力すること
"""


def generate_article(keyword: str) -> str:
    """Claude APIで記事を生成する"""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    date_str = datetime.now().strftime("%Y-%m-%d")
    prompt = ARTICLE_PROMPT.format(keyword=keyword, date=date_str)

    print(f"  モデル: {MODEL}")
    print(f"  キーワード: {keyword}")

    message = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    content = message.content[0].text

    # コードブロックが含まれている場合は中身だけ取り出す
    code_match = re.search(r"```(?:markdown)?\n([\s\S]+?)```", content)
    if code_match:
        content = code_match.group(1).strip()

    print(f"  トークン使用量: 入力 {message.usage.input_tokens} / 出力 {message.usage.output_tokens}")
    return content


def make_filename(keyword: str) -> str:
    """キーワードからファイル名を生成する"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    # 日本語・スペースをハイフンに変換
    safe_keyword = re.sub(r"[^\w\s-]", "", keyword)
    safe_keyword = re.sub(r"[\s]+", "-", safe_keyword.strip())
    safe_keyword = safe_keyword[:40]  # 長すぎる場合は切り詰め
    return f"{date_str}-{safe_keyword}.md"


def save_to_obsidian(content: str, keyword: str) -> Path:
    """Obsidianのvaultに記事を保存する"""
    VAULT_POSTS_PATH.mkdir(parents=True, exist_ok=True)
    filename = make_filename(keyword)
    filepath = VAULT_POSTS_PATH / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def main():
    if len(sys.argv) < 2:
        print("使い方: python scripts/generate-article.py \"キーワード\"")
        print("例:     python scripts/generate-article.py \"ChatGPT 使い方 初心者\"")
        sys.exit(1)

    keyword = " ".join(sys.argv[1:])

    # APIキーチェック
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("エラー: 環境変数 ANTHROPIC_API_KEY が設定されていません")
        print("設定方法: $env:ANTHROPIC_API_KEY = \"sk-ant-...\"  (PowerShell)")
        sys.exit(1)

    print(f"\n🤖 記事を生成しています...")
    content = generate_article(keyword)

    print(f"💾 Obsidianに保存しています...")
    filepath = save_to_obsidian(content, keyword)

    print(f"\n✅ 完了！")
    print(f"   保存先: {filepath}")
    print(f"   次のステップ:")
    print(f"   1. Obsidianで記事を確認・編集する")
    print(f"   2. フロントマターの draft: true → draft: false に変更")
    print(f"   3. C:\\projects\\blog\\scripts\\sync-posts.ps1 を実行して公開")


if __name__ == "__main__":
    main()
