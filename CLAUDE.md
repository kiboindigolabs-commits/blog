# Claude Code メモリ

## セッション情報
- 初回セッション: 2026-04-25 〜 2026-05-01
- 最終更新: 2026-05-09

---

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
| ネタ管理（同期対象外） | `C:\obsidian-vault\blog\_ideas\` |
| Gitリポジトリ | `C:\projects\blog` (junction → `G:\マイドライブ\cursor\blog`) |
| 同期スクリプト | `C:\projects\blog\scripts\sync-posts.ps1` |

### リポジトリ構成
```
blog/
├── .github/workflows/deploy.yml      # 自動デプロイ
├── archetypes/default.md             # Hugo記事テンプレート
├── assets/css/extended/custom.css   # アフィリエイト向けカスタムCSS ✅
├── content/posts/                    # 同期先（直接編集しない）
├── layouts/shortcodes/               # ショートコード ✅
│   ├── btn.html                      # アフィリエイトボタン
│   ├── box.html                      # コンテンツボックス
│   ├── card.html                     # 商品カード（btncolor対応）
│   └── ranking.html                  # ランキング表示（btncolor対応）
├── templates/新規記事.md              # Obsidianテンプレート
├── scripts/sync-posts.ps1            # ← 公開するときに実行するスクリプト
├── static/                           # 画像などの静的ファイル
├── themes/PaperMod/                  # テーマ（セットアップ済み）✅
├── hugo.toml                         # Hugo設定
└── CLAUDE.md                         # このファイル
```

---

## アフィリエイト向けショートコード ✅ 完了

### ① アフィリエイトボタン
```
{{</* btn url="https://..." text="無料で試す" color="orange" */>}}
```
color: `orange` / `amazon` / `blue` / `green` / `red` / `purple` / `moshimo`

### ② 商品カード
```
{{</* card name="ツール名" stars="5" price="月額3,000円" url="https://..." btncolor="moshimo" */>}}
特徴の説明文
{{</* /card */>}}
```
btncolor省略時はデフォルト（amazon色）。もしもアフィリエイト経由は `btncolor="moshimo"` を指定。

### ③ コンテンツボックス
```
{{</* box type="good" title="タイトル" */>}}
内容
{{</* /box */>}}
```
type: `info`💡 / `warn`⚠️ / `good`✅ / `bad`❌ / `point`📌 / `memo`📝

### ④ ランキング
```
{{</* ranking rank="1" name="ツール名" stars="5" url="https://..." btncolor="moshimo" */>}}
説明文
{{</* /ranking */>}}
```
btncolor省略時はデフォルト（orange）。もしもアフィリエイト経由は `btncolor="moshimo"` を指定。

---

## もしもアフィリエイト ✅ ショートコード対応済み

### 登録手順（ユーザーが実行すること）

1. **もしもアフィリエイトに登録**
   - サイト: https://www.moshimo.com/
   - 無料登録 → 審査なし（一般ASP比較で審査が緩め）
   - 本名・住所・振込先口座の入力が必要

2. **広告プログラムに申請する**
   - ログイン後「広告プログラムを探す」で紹介したいサービスを検索
   - 「提携申請」ボタンをクリック（即時承認のものも多い）

3. **アフィリエイトリンクを取得する**
   - 提携承認後、広告一覧から「リンク作成」
   - 「テキストリンク」か「バナー」を選び、リンクコードをコピー
   - `https://af.moshimo.com/af/c/click?a_id=XXXXX&...` の形式のURLを取得

4. **ショートコードに貼り付ける**
   ```
   {{</* btn url="https://af.moshimo.com/af/c/click?a_id=XXXXX&..." text="無料で登録する" color="moshimo" */>}}
   ```
   または商品カード形式:
   ```
   {{</* card name="ツール名" stars="5" price="月額0円〜" url="https://af.moshimo.com/af/c/click?a_id=XXXXX&..." btncolor="moshimo" */>}}
   おすすめポイント
   {{</* /card */>}}
   ```

### もしもアフィリエイトの特徴
- 審査なしで始められるプログラムが多い（初心者向け）
- Amazon・楽天の商品も掲載可能（W報酬制度あり）
- 支払いサイクル: 毎月末締め・翌月末払い
- 最低支払い金額: 1,000円

---

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

---

## AI Blogネタ収集システム（設計確定・構造構築済み）

### 概要
AI関連ブログのネタを自動収集し、Obsidianで管理しながら記事化・公開まで繋ぐシステム。

### Obsidian _ideas フォルダ構造（構築済み）
```
C:\obsidian-vault\blog\_ideas\       ← Hugo同期対象外（先頭 _ で明示）
├── _進捗ログ.md                      ← セッション引き継ぎ用ドキュメント
├── 00_MOC/
│   ├── AI_Blog_MOC.md               ← トップハブ
│   ├── Cat_LLM.md
│   ├── Cat_Agent.md
│   ├── Cat_Prompt.md
│   └── Cat_News.md
├── 10_Ideas/2026-05/                ← 記事化候補ネタ
├── 20_Sources/2026-05/              ← 元ネタ集約（出典URL・要約）
├── 30_Drafts/                       ← ここで執筆 → 完成後 blog/posts/ へ
├── 40_PublishedLog/                 ← 公開済み記録
├── 50_WeeklyReview/2026/            ← 週次サマリ
├── 90_Templates/                    ← 各種テンプレート
│   ├── Idea_Template.md
│   ├── Draft_Template.md            ← Hugo互換フロントマター
│   ├── Source_Template.md
│   └── WeeklyReview_Template.md
└── 99_Archive/
```

### 確定した設計事項
| 項目 | 決定内容 |
|------|----------|
| 読者層 | AI初心者・一般読者 ＋ ビジネスパーソン・経営層 |
| 内部ジャンル | LLM / Agent / Prompt / News（4分類） |
| 自動収集頻度 | 月曜朝・木曜朝（週2回） |
| ファイル名規約 | `YYYY-MM-DD-slug.md`（英数字slug） |
| ドラフト位置 | `_ideas/30_Drafts/` で執筆 → 完成後 `blog/posts/` に移動 |
| Hugo categoriesマッピング | 業務効率化 / AI活用 / ニュース / プロンプト |

### 設計書（参照先）
- `C:\obsidian-vault\memo\AI開発\AI_Blog設計書_v2.md`

---

## 次の実装予定

### 優先度 高
- [ ] **自動収集タスクの登録**（週2回 月曜朝・木曜朝）
  - 確認待ち: 実行時刻（何時か）、1回あたりの取得件数（各ジャンル何件か）、重複URL検出の要否
  - 出力先: `20_Sources/YYYY-MM/`・`10_Ideas/YYYY-MM/`・`50_WeeklyReview/YYYY/`
  - 処理: 4ジャンル（llm/agent/prompt/news）それぞれWeb検索 → 初心者向け切り口で要約 → Markdown化
- [ ] **初回テスト実行**（自動収集タスク登録後に手動トリガ → 品質確認）

### 優先度 中
- [ ] **archetypes/default.md との整合確認**（30_Drafts → blog/posts/ 移行用変換テンプレに反映）
- [ ] **月次フォルダ追加**（`10_Ideas/2026-06/`・`20_Sources/2026-06/` を来月頭に作成）

### 優先度 低
- [ ] **MOCの動的化**（Dataviewプラグイン導入でAI_Blog_MOC.mdを自動クエリ化）

---

## 使用技術
- **エディタ**: Obsidian
- **静的サイトジェネレータ**: Hugo + PaperMod テーマ
- **ホスティング**: Cloudflare Pages（無料）
- **バージョン管理**: GitHub

---

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
3. ネタ管理は `C:\obsidian-vault\blog\_ideas\` を使う（Hugo同期対象外）
4. テンプレート参照: `C:\projects\blog\templates\新規記事.md`

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

---

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

---

## Windowsパス問題の解決（済み）

### Google Drive 日本語パスの回避（ジャンクション作成）
```powershell
# 管理者PowerShellで実行済み
New-Item -ItemType Junction -Path "C:\obsidian-vault" -Target "G:\マイドライブ\obsidian"
New-Item -ItemType Junction -Path "C:\projects\blog" -Target "G:\マイドライブ\cursor\blog"
```

---

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
