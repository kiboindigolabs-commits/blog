#!/usr/bin/env python3
"""
AI Blogネタ自動収集スクリプト
4ジャンル（LLM/Agent/Prompt/News）のAI関連情報を週2回収集し、
Obsidianの_ideasフォルダに保存します。

使い方:
  python scripts/collect-ideas.py

Windowsタスクスケジューラで週2回（月曜・木曜 22:30）実行
register-scheduler.ps1 で自動登録可能
"""

import anthropic
import os
import re
import json
from datetime import datetime
from pathlib import Path

try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False

# 設定
VAULT_IDEAS_PATH = Path(r"C:\obsidian-vault\blog\_ideas")
SEEN_URLS_FILE = VAULT_IDEAS_PATH / "99_Archive" / "seen_urls.json"
MODEL = "claude-sonnet-4-6"
ITEMS_PER_GENRE = 2  # 各ジャンルの取得件数

# ジャンル設定（検索クエリ・Hugo分類・Obsidianカテゴリ）
GENRES = {
    "llm": {
        "name": "LLM",
        "category": "Cat_LLM",
        "hugo_category": "AI活用",
        "queries": [
            "大規模言語モデル 最新ニュース 2026",
            "LLM 日本語 新機能 リリース 2026",
            "GPT Claude Gemini 比較 最新",
        ],
    },
    "agent": {
        "name": "Agent",
        "category": "Cat_Agent",
        "hugo_category": "業務効率化",
        "queries": [
            "AIエージェント 自動化 最新 2026",
            "AI agent 活用事例 ビジネス",
            "自律型AI 導入 企業 最新情報",
        ],
    },
    "prompt": {
        "name": "Prompt",
        "category": "Cat_Prompt",
        "hugo_category": "プロンプト",
        "queries": [
            "プロンプトエンジニアリング テクニック 2026",
            "ChatGPT Claude プロンプト 効果的 使い方",
            "AI プロンプト 初心者 コツ",
        ],
    },
    "news": {
        "name": "News",
        "category": "Cat_News",
        "hugo_category": "ニュース",
        "queries": [
            "AI 人工知能 最新ニュース 今週",
            "AI 発表 リリース プロダクト 最新",
            "AI 規制 政策 日本 2026",
        ],
    },
}


def load_seen_urls() -> set:
    if SEEN_URLS_FILE.exists():
        with open(SEEN_URLS_FILE, encoding="utf-8") as f:
            data = json.load(f)
            return set(data.get("urls", []))
    return set()


def save_seen_urls(urls: set):
    SEEN_URLS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SEEN_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump({"urls": sorted(urls)}, f, ensure_ascii=False, indent=2)


def search_web(queries: list, seen_urls: set, max_per_query: int = 5) -> list:
    if not HAS_DDGS:
        print("  [スキップ] duckduckgo-search 未インストール")
        return []

    results = []
    seen_this_run = set()

    with DDGS() as ddgs:
        for query in queries:
            if len(results) >= ITEMS_PER_GENRE:
                break
            try:
                for r in ddgs.text(query, max_results=max_per_query, region="jp-jp"):
                    url = r.get("href", "")
                    if not url:
                        continue
                    if url in seen_urls:
                        print(f"  [重複スキップ] {url[:60]}...")
                        continue
                    if url in seen_this_run:
                        continue
                    seen_this_run.add(url)
                    results.append({
                        "url": url,
                        "title": r.get("title", "（タイトルなし）"),
                        "snippet": r.get("body", ""),
                    })
                    if len(results) >= ITEMS_PER_GENRE:
                        break
            except Exception as e:
                print(f"  [検索エラー] {query[:30]}... : {e}")

    return results[:ITEMS_PER_GENRE]


def summarize_result(client: anthropic.Anthropic, result: dict, genre_key: str, today: str) -> tuple:
    genre = GENRES[genre_key]

    prompt = f"""以下のAI関連記事を日本語で要約し、ブログ記事アイデアを作成してください。

タイトル: {result['title']}
URL: {result['url']}
概要: {result['snippet']}

## 出力形式（2つのブロックを必ず出力すること）

### ソース記録
```source
---
date: {today}
url: {result['url']}
title: "{result['title']}"
genre: {genre['name']}
category: {genre['hugo_category']}
---

## 要約
（3〜5行の日本語要約。事実ベースで正確に）

## 初心者向けポイント
（このニュースがAI初心者にとってどう役立つか・なぜ重要かを2行で）

## 関連タグ
（ハッシュタグ3〜5個 例: #LLM #Claude #活用事例）
```

### 記事アイデア
```idea
---
date: {today}
genre: {genre['name']}
source_title: "{result['title']}"
source_url: {result['url']}
status: candidate
---

## 記事タイトル案
1. （SEO意識した日本語タイトル案）
2. （別角度のタイトル案）
3. （別角度のタイトル案）

## ターゲット読者
（1行：例「ChatGPTを使い始めたばかりのビジネスパーソン」）

## 記事の切り口
（初心者・ビジネスパーソン向けの角度から2〜3行）

## キーワード案
（5〜8個 カンマ区切り）
```
"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text
    source_match = re.search(r"```source\n([\s\S]+?)```", text)
    idea_match = re.search(r"```idea\n([\s\S]+?)```", text)

    source_content = source_match.group(1).strip() if source_match else text
    idea_content = idea_match.group(1).strip() if idea_match else ""

    return source_content, idea_content


def make_slug(title: str, idx: int) -> str:
    safe = re.sub(r"[^\w\s-]", "", title)
    safe = re.sub(r"[\s]+", "-", safe.strip())[:30]
    return safe if safe else f"item-{idx}"


def save_source(content: str, genre_key: str, idx: int, today: str):
    month_dir = VAULT_IDEAS_PATH / "20_Sources" / today[:7]
    month_dir.mkdir(parents=True, exist_ok=True)
    slug = make_slug(GENRES[genre_key]["name"], idx)
    filepath = month_dir / f"{today}-{genre_key}-{idx:02d}.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def save_idea(content: str, genre_key: str, idx: int, today: str):
    month_dir = VAULT_IDEAS_PATH / "10_Ideas" / today[:7]
    month_dir.mkdir(parents=True, exist_ok=True)
    filepath = month_dir / f"{today}-idea-{genre_key}-{idx:02d}.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def generate_weekly_review(client: anthropic.Anthropic, all_results: dict, today: str):
    year = today[:4]
    week_num = datetime.now().isocalendar()[1]
    review_dir = VAULT_IDEAS_PATH / "50_WeeklyReview" / year
    review_dir.mkdir(parents=True, exist_ok=True)
    filepath = review_dir / f"{today}-week{week_num:02d}.md"

    summaries = []
    for genre_key, results in all_results.items():
        genre_name = GENRES[genre_key]["name"]
        for r in results:
            summaries.append(f"- [{genre_name}] {r['title']} ({r['url']})")

    if not summaries:
        return None

    prompt = f"""以下の今週収集したAIニュース一覧から、週次サマリーを日本語で作成してください。

## 収集記事一覧
{chr(10).join(summaries)}

## 出力形式（markdownで出力）
---
date: {today}
week: {week_num}
---

## 今週のAIトレンドまとめ（{today}）

### 注目トピック3選
1. （最も重要なニュースと初心者向け解説）
2. （2番目に重要なニュースと解説）
3. （3番目に重要なニュースと解説）

### ジャンル別ひとこと
- **LLM**: （今週のLLM動向1行）
- **Agent**: （今週のAgent動向1行）
- **Prompt**: （今週のPrompt動向1行）
- **News**: （その他のAIニュース1行）

### 来週の注目ポイント
（今週の流れから来週注目すべき点2行）
"""

    message = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(message.content[0].text)

    return filepath


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("エラー: 環境変数 ANTHROPIC_API_KEY が設定されていません")
        print("設定方法: $env:ANTHROPIC_API_KEY = \"sk-ant-...\"  (PowerShell)")
        return

    if not HAS_DDGS:
        print("エラー: duckduckgo-search がインストールされていません")
        print("インストール: pip install duckduckgo-search")
        return

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.now().strftime("%Y-%m-%d")

    print(f"\n🔍 AIネタ自動収集を開始します ({today})")
    print(f"   各ジャンル {ITEMS_PER_GENRE} 件 / 合計 {ITEMS_PER_GENRE * len(GENRES)} 件\n")

    seen_urls = load_seen_urls()
    new_urls = set()
    all_results = {}
    total_saved = 0

    for genre_key, genre in GENRES.items():
        print(f"━━ {genre['name']} ━━")
        results = search_web(genre["queries"], seen_urls)
        all_results[genre_key] = results

        if not results:
            print(f"  取得件数: 0件（新規なし）")
            continue

        print(f"  取得件数: {len(results)}件")

        for i, result in enumerate(results, 1):
            print(f"  [{i}] {result['title'][:50]}...")
            try:
                source_content, idea_content = summarize_result(client, result, genre_key, today)
                src_path = save_source(source_content, genre_key, i, today)
                print(f"      → ソース保存: {src_path.name}")

                if idea_content:
                    idea_path = save_idea(idea_content, genre_key, i, today)
                    print(f"      → アイデア保存: {idea_path.name}")

                new_urls.add(result["url"])
                total_saved += 1
            except Exception as e:
                print(f"      [エラー] {e}")

        print()

    # 週次レビュー生成
    if total_saved > 0:
        print("📝 週次レビューを生成中...")
        try:
            review_path = generate_weekly_review(client, all_results, today)
            if review_path:
                print(f"   → {review_path.name}")
        except Exception as e:
            print(f"   [エラー] {e}")

    # 見済みURL更新
    seen_urls.update(new_urls)
    save_seen_urls(seen_urls)

    print(f"\n✅ 完了！ {total_saved}件保存しました")
    print(f"   ソース  : {VAULT_IDEAS_PATH / '20_Sources' / today[:7]}")
    print(f"   アイデア: {VAULT_IDEAS_PATH / '10_Ideas' / today[:7]}")
    print(f"   週次    : {VAULT_IDEAS_PATH / '50_WeeklyReview' / today[:4]}")


if __name__ == "__main__":
    main()
