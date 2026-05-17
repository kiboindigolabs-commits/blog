# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## セッション情報
- 最終更新: 2026-05-17
- 開発ブランチ: `claude/continue-previous-work-o1h7y`
- **main ブランチは保護されている** → 必ず開発ブランチで作業し、GitHub MCP の `create_pull_request` + `merge_pull_request` でマージする

---

## システム構成

```
Obsidian (C:\obsidian-vault\blog\posts\) ← 記事を書く場所
  ↓ scripts/sync-posts.ps1 を実行
content/posts/ へコピー
  ↓ git push → main ブランチ
GitHub Actions → Hugo --minify でビルド
  ↓
Cloudflare Pages → https://reslabo.jp (本番) ✅ 確認済み
```

**ローカルプレビュー（Linux環境）:**
```bash
hugo server -D   # http://localhost:1313
```

---

## リポジトリ構成（カスタム部分のみ）

```
blog/
├── hugo.toml                          # サイト設定
├── assets/css/extended/custom.css    # 全カスタムスタイル（ここを編集）
├── layouts/
│   ├── list.html                      # 記事一覧（entry-body ラッパーあり）
│   ├── single.html                    # 記事詳細（post-with-sidebar グリッド）
│   └── partials/
│       ├── extend_head.html           # フォント・theme-color・読書進捗バー
│       ├── sidebar.html               # 著者・注目記事・カテゴリ・タグ
│       ├── related-posts.html         # 関連記事グリッド（4件）
│       └── comments.html             # Formspreeシンプルフォーム（日本語）
├── layouts/shortcodes/               # アフィリエイト用ショートコード
│   ├── btn.html                       # アフィリエイトボタン
│   ├── box.html                       # コンテンツボックス
│   ├── card.html                      # 商品カード
│   └── ranking.html                   # ランキング表示
├── static/images/
│   ├── hero-pattern.svg              # ヒーロー背景のニューラルネット風パターン
│   └── logo.svg                       # サイドバー著者アバター
└── scripts/
    ├── generate-article.py            # Claude API で記事自動生成
    ├── collect-ideas.py               # ネタ自動収集（月・木 22:30）
    └── sync-posts.ps1                 # Obsidian → content/posts/ 同期
```

---

## デザインシステム（custom.css）

### カラー変数
```css
--primary:       #0d8a94;   /* ティール（メインアクセント）*/
--primary-dark:  #0a6b73;
--primary-light: #e0f7f8;
--accent:        #f59e0b;   /* アンバー */
--main-width:    1100px;    /* PaperMod デフォルト 720px から拡張 */
```

### レイアウト構造
- **2カラムグリッド**: `post-with-sidebar` / `list-with-sidebar` → `1fr 280px`
- **記事カード（横並び）**: `.post-entry` → flexbox、`.entry-cover`（180px固定）+ `.entry-body`（flex:1）
  - `list.html` に `<div class="entry-body">` ラッパーがあることが前提
  - モバイル（768px以下）は縦並びにフォールバック
- **ヒーローセクション**: 12秒アニメーショングラデーション + `hero-pattern.svg` オーバーレイ

### 記事カードの DOM 構造（list.html）
```html
<article class="post-entry">
  <figure class="entry-cover">...</figure>   <!-- カバー画像（なければ省略）-->
  <div class="entry-body">                   <!-- テキスト側ラッパー -->
    <header class="entry-header"><h2>...</h2></header>
    <div class="entry-content">...</div>
    <footer class="entry-footer">...</footer>
  </div>
  <a class="entry-link" ...></a>             <!-- カード全体リンク overlay -->
</article>
```

---

## アフィリエイト向けショートコード

### ① ボタン
```
{{</* btn url="https://..." text="無料で試す" color="orange" */>}}
```
`color`: `orange` / `amazon` / `blue` / `green` / `red` / `purple` / `teal`

### ② 商品カード
```
{{</* card name="ツール名" stars="5" price="月額3,000円" url="https://..." btncolor="moshimo" */>}}
説明文
{{</* /card */>}}
```

### ③ コンテンツボックス
```
{{</* box type="point" title="タイトル" */>}}
内容
{{</* /box */>}}
```
`type`: `info` / `warn` / `good` / `bad` / `point` / `memo`

### ④ ランキング
```
{{</* ranking rank="1" name="ツール名" stars="5" url="https://..." btncolor="moshimo" */>}}
説明文
{{</* /ranking */>}}
```

---

## AI記事自動生成

```powershell
# 環境変数を設定してから実行
$env:ANTHROPIC_API_KEY = "sk-ant-..."
python scripts/generate-article.py "ChatGPT 使い方 初心者"
# → content/posts/YYYY-MM-DD-keyword.md に draft: true で保存
```

**ペルソナ設定（generate-article.py の SYSTEM_PROMPT）:**
- 40代会社員（エンジニア・マーケター経験あり）
- AI初心者目線・副業志向・うさぎ&リス好き
- 「ですます」調・身近な例えで説明

使用モデル: `claude-sonnet-4-6`（`MODEL` 変数で変更可）

---

## hugo.toml 重要設定

```toml
baseURL = "https://reslabo.jp"
[params]
  ShowReadingTime = false   # 読書時間を非表示
  ShowWordCount   = false   # 文字数を非表示
  hideAuthor      = true    # 著者名を非表示（日付のみ表示）

[params.logo]
  logoText = "✨ AI Tools Lab"

[params.homeInfoParams]
  Title = "AIツールをもっと身近に ✨"

[params.analytics.google]
  SiteVerificationTag = "ghPKcsRx4Xynt70itX3tQ_hMvaKkgECxkFzacw0kKp8"  # reslabo.jp 用
```

---

## 記事フロントマター

```yaml
---
title: "記事タイトル"
date: 2026-05-15
draft: false
tags: ["タグ1", "タグ2"]
categories: ["AIツール紹介"]
description: "120文字以内の説明"
cover:
  image: "/images/cover.png"
  alt: "説明"
  relative: false
---
```

---

## 現状・次のアクション

### 完了済み ✅
- `reslabo.jp` カスタムドメイン設定・DNS反映確認
- Google Search Console 登録（reslabo.jp プロパティ、GSCタグ設定済み）
- デザイン刷新（ティールカラー・横並びカード・シンプルヘッダー）
- 記事メタ：日付のみ表示（読書時間・文字数・著者 非表示）
- ヒーローセクション背景：ニューラルネット風SVG + 12秒グラデーションアニメーション
- コメント欄：Utterances → Formspree日本語シンプルフォームに変更（エンドポイント: `xbdwknjn`）
- ボタン色調整：グラデーション＋text-shadowで視認性改善
- モバイルレイアウト修正：ヘッダー・コンテンツのズレを `overflow-x:hidden` + padding統一で修正
- 記事 24本公開済み
- もしもアフィリエイト提携承認済み ✅（審査通過・リンク取得可能な状態）
- アフィリエイトリンク追加済み：
  - 楽天市場書籍（`a_id=5567964`）: chatgpt-beginner-guide, prompt-engineering-basics, llm-explained-easy, ai-beginner-mistakes
  - ConoHa AI Canvas（`a_id=5571249`）: ai-image-generation-guide, ai-tools-ranking-2026, midjourney-beginner
  - Skill Hacks（`a_id=5571281`）: ai-coding-tools, ai-work-efficiency, ai-free-tools-2026
  - DMM WEBCAMP テキスト＋バナー（`a_id=5571278`, `pl_id=68018`）: ai-agent-introduction, generative-ai-for-business, chatgpt-plus-review
- サイドバーにDMM WEBCAMP 300×250バナー追加（`pl_id=20505`）✅
- generate-article.py: MAX_TOKENS 8192・記事目標4000〜6000字に拡張

### ユーザー操作が必要なもの
- **collect-ideas.py 初回テスト**：`python scripts/collect-ideas.py` で手動実行
- **モバイル表示確認**：reslabo.jp をスマホで確認してレイアウトのズレが解消されているか確認

### 代替ASP（もしも審査が通らない場合）
| ASP | 特徴 |
|-----|------|
| A8.net | 国内最大・審査緩め |
| Amazonアソシエイト | 即日審査 |
| アクセストレード | SaaS系に強い |

---

## Git 作業フロー

```bash
# 開発ブランチに切り替え（または作成）
git checkout claude/continue-previous-work-o1h7y

# 変更後にコミット・プッシュ
git add <files>
git commit -m "説明"
git push -u origin claude/continue-previous-work-o1h7y

# PRは GitHub MCP で作成・マージ
# mcp__github__create_pull_request → mcp__github__merge_pull_request
# コンフリクト時: git fetch origin main && git rebase origin/main && git push -f
```
