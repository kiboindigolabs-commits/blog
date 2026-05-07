# Claude Code メモリ

## セッション情報
- セッションURL: https://claude.ai/code/session_01GmL2zRdXn6AtkX1SabLu9p
- 日付: 2026-04-25 〜 2026-05-07

## ブログシステム構成

### アーキテクチャ
```
Obsidian (C:\obsidian-vault\blog\posts\) ← ここで記事を書く
  ↓ sync-posts.ps1 を実行
C:\projects\blog\content\posts\ へコピー
  ↓ git push
GitHub (kiboindigolabs-commits/blog)
  ↓ GitHub Actions (mainブランチへのpushで起動)
Hugo でビルド
  ↓
Cloudflare Pages (無料ホスティング)
```

### パス構成
| 用途 | パス |
|------|------|
| Obsidian Vault | `C:\obsidian-vault` (junction → `G:\マイドライブ\obsidian`) |
| 記事を書く場所 | `C:\obsidian-vault\blog\posts\` |
| Gitリポジトリ | `C:\projects\blog` (junction → `G:\マイドライブ\cursor\blog`) |
| 同期スクリプト | `C:\projects\blog\scripts\sync-posts.ps1` |

### リポジトリ構成
```
blog/
├── .github/workflows/deploy.yml      # 自動デプロイ
├── archetypes/default.md             # Hugo記事テンプレート
├── assets/css/extended/custom.css   # アフィリエイト向けカスタムCSS ✅
├── content/
│   ├── posts/                        # 記事（直接編集しない）
│   ├── about.md                      # Aboutページ ✅
│   ├── archives.md                   # アーカイブページ ✅
│   ├── contact.md                    # お問い合わせ（Formspree連携済み）✅
│   ├── disclaimer.md                 # 免責事項 ✅
│   ├── privacy.md                    # プライバシーポリシー ✅
│   └── search.md                     # 検索ページ（Fuse.js）✅
├── layouts/
│   ├── 404.html                      # カスタム404ページ ✅
│   ├── partials/
│   │   ├── extend_head.html          # ファビコン・フォント
│   │   └── extend_footer.html        # フッターナビゲーション ✅
│   └── shortcodes/                   # ショートコード ✅
│       ├── btn.html
│       ├── box.html
│       ├── card.html
│       └── ranking.html
├── templates/新規記事.md              # Obsidianテンプレート
├── scripts/sync-posts.ps1            # ← 公開するときに実行するスクリプト
├── static/                           # 画像などの静的ファイル
├── themes/PaperMod/                  # テーマ（セットアップ済み）✅
├── hugo.toml                         # Hugo設定
└── CLAUDE.md                         # このファイル
```

## アフィリエイト向けショートコード ✅ 完了

### ① アフィリエイトボタン
```
{{</* btn url="https://..." text="無料で試す" color="orange" */>}}
```
color: `orange` / `amazon` / `blue` / `green` / `red` / `purple`

### ② 商品カード
```
{{</* card name="ツール名" stars="5" price="月額3,000円" url="https://..." */>}}
特徴の説明文
{{</* /card */>}}
```

### ③ コンテンツボックス
```
{{</* box type="good" title="タイトル" */>}}
内容
{{</* /box */>}}
```
type: `info`💡 / `warn`⚠️ / `good`✅ / `bad`❌ / `point`📌 / `memo`📝

### ④ ランキング
```
{{</* ranking rank="1" name="ツール名" stars="5" url="https://..." */>}}
説明文
{{</* /ranking */>}}
```

## AI記事自動生成パイプライン ✅ 完了

### 使い方

#### 初回セットアップ（1回だけ実行）
```powershell
# 1. Pythonライブラリをインストール
pip install -r C:\projects\blog\scripts\requirements.txt

# 2. Anthropic APIキーを設定
#    https://console.anthropic.com/ でAPIキーを取得してから:
$env:ANTHROPIC_API_KEY = "sk-ant-ここにAPIキーを貼り付ける"
```

#### 記事を自動生成する
```powershell
cd C:\projects\blog
python scripts/generate-article.py "ChatGPT 使い方 初心者"
```

#### 生成後の流れ
1. `C:\obsidian-vault\blog\posts\` に下書きが保存される
2. Obsidianで記事を確認・編集する
3. フロントマターの `draft: true` → `draft: false` に変更
4. `C:\projects\blog\scripts\sync-posts.ps1` を実行して公開

### スクリプト構成
```
scripts/
├── generate-article.py   # AI記事生成メインスクリプト
├── requirements.txt      # Python依存ライブラリ（anthropic）
├── .env.example          # APIキー設定例
└── sync-posts.ps1        # 記事公開スクリプト
```

### 使用モデル
- `claude-sonnet-4-6`（速度と品質のバランス）
- 変更する場合は `generate-article.py` の `MODEL` を編集

## ブログ基本要素 ✅ 完了（2026-05-07）

| ページ | URL | 状態 |
|--------|-----|------|
| 検索 | `/search/` | ✅ Fuse.js全文検索 |
| アーカイブ | `/archives/` | ✅ 月別記事一覧 |
| About | `/about/` | ✅ ブログ紹介 |
| プライバシーポリシー | `/privacy/` | ✅ |
| 免責事項 | `/disclaimer/` | ✅ |
| お問い合わせ | `/contact/` | ✅ Formspree（ID: xbdwknjn）|
| 404ページ | - | ✅ カスタムデザイン |
| ファビコン | - | ✅ 🤖絵文字SVG |
| フッターナビ | - | ✅ 全重要ページへのリンク |

## 次の実装予定

- [ ] アフィリエイト: もしもアフィリエイト（初心者向けで最もおすすめ）への登録
- [ ] Google Analytics の設定（hugo.toml に gtag を追加）
- [ ] OGP用デフォルト画像の作成（static/images/og-default.png）

### 使用技術
- **エディタ**: Obsidian
- **静的サイトジェネレータ**: Hugo + PaperMod テーマ
- **ホスティング**: Cloudflare Pages（無料）
- **バージョン管理**: GitHub

## セットアップ手順（ユーザーが実行すること）

### 1. Hugo のインストール（Windows）✅ 完了
```powershell
winget install Hugo.Hugo.Extended
```

### 2. PaperMod テーマを追加 ✅ 完了
```powershell
cd C:\projects\blog
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
git submodule update --init --recursive
```

### 3. Cloudflare Pages の設定 ✅ 完了
- デプロイURL: `https://blog-19g.pages.dev`
- GitHubリポジトリ `kiboindigolabs-commits/blog` の main ブランチに連携済み
- ビルドコマンド: `hugo --minify` / 出力: `public`

### 4. Obsidian の設定
1. Obsidianのボルトは `C:\obsidian-vault` を使用（変更不要）
2. 記事は `C:\obsidian-vault\blog\posts\` フォルダに書く
3. テンプレート設定:
   - 設定 → テンプレート → テンプレートフォルダの場所: `blog\posts` 内に配置するか、
   - `C:\projects\blog\templates\新規記事.md` を参考にフロントマターをコピーして使う

### 5. 記事を公開するとき
```powershell
# PowerShell で実行（C:\projects\blog にいなくてもOK）
C:\projects\blog\scripts\sync-posts.ps1
```

### 6. ローカルプレビュー
```powershell
cd C:\projects\blog
hugo server -D
# http://localhost:1313 で確認
```

## 記事の書き方

### フロントマター（記事の先頭に必須）
```yaml
---
title: "記事タイトル"
date: 2026-05-01
draft: false      # true のままだと公開されない
tags: ["タグ1", "タグ2"]
categories: ["カテゴリ"]
description: "記事の説明"
---
```

### 注意点
- `draft: true` のままではデプロイしても公開されない → 公開時は `draft: false` に変更
- 記事ファイル名は英数字推奨（例: `2026-05-01-my-post.md`）
- 画像は `C:\projects\blog\static\images\` に置いて `![説明](/images/ファイル名)` で参照

## Windowsパス問題の解決（済み）

### Google Drive 日本語パスの回避（ジャンクション作成）
```powershell
# 管理者PowerShellで実行済み
New-Item -ItemType Junction -Path "C:\obsidian-vault" -Target "G:\マイドライブ\obsidian"
New-Item -ItemType Junction -Path "C:\projects\blog" -Target "G:\マイドライブ\cursor\blog"
```

## 調査・解決した問題

### AWS SAM ビルドエラー: UTF-8 デコードエラー

**エラー内容:**
```
Build Failed
Error: PythonPipBuilder:ResolveDependencies - 'utf-8' codec can't decode byte 0x83 in position 29: invalid start byte
```

**原因:**
- プロジェクトパス `G:\マイドライブ\...` に日本語が含まれている
- Windows が日本語パスを Shift-JIS (CP932) でエンコードするため、SAM がUTF-8として読めない

**解決策:**
- `C:\projects\blog` のジャンクションを使用してSAMを実行する
