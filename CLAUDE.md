# Claude Code メモリ

## セッション情報
- セッションURL: https://claude.ai/code/session_01Lzu36ZhTa1CGkWxSx5vQEJ
- 日付: 2026-04-25 〜 2026-05-01

## ブログシステム構成

### アーキテクチャ
```
Obsidian (C:\obsidian-vault または C:\projects\blog)
  ↓ Obsidian Git プラグインで自動同期
GitHub (kiboindigolabs-commits/blog)
  ↓ GitHub Actions (mainブランチへのpushで起動)
Hugo でビルド
  ↓
Cloudflare Pages (無料ホスティング)
```

### リポジトリ構成
```
blog/
├── .github/workflows/deploy.yml   # 自動デプロイ
├── archetypes/default.md          # Hugo記事テンプレート
├── content/posts/                 # ← ここに記事を書く
├── templates/新規記事.md           # Obsidianテンプレート
├── static/                        # 画像などの静的ファイル
├── themes/PaperMod/               # テーマ（要セットアップ）
├── hugo.toml                      # Hugo設定
└── CLAUDE.md                      # このファイル
```

### 使用技術
- **エディタ**: Obsidian
- **静的サイトジェネレータ**: Hugo + PaperMod テーマ
- **ホスティング**: Cloudflare Pages（無料）
- **バージョン管理**: GitHub

## セットアップ手順（ユーザーが実行すること）

### 1. Hugo のインストール（Windows）
```powershell
winget install Hugo.Hugo.Extended
```

### 2. PaperMod テーマを追加
```powershell
cd C:\projects\blog
git submodule add --depth=1 https://github.com/adityatelange/hugo-PaperMod.git themes/PaperMod
git submodule update --init --recursive
```

### 3. Cloudflare Pages の設定
1. https://pages.cloudflare.com/ でプロジェクト作成
2. GitHubリポジトリ `kiboindigolabs-commits/blog` を連携
3. ビルド設定:
   - フレームワーク: Hugo
   - ビルドコマンド: `hugo --minify`
   - 出力ディレクトリ: `public`
4. GitHub Secrets に追加:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`

### 4. Obsidian の設定
1. Obsidianでボルトとして `C:\projects\blog` を開く
2. プラグイン → コミュニティプラグイン → **Obsidian Git** をインストール
3. Obsidian Git 設定:
   - Auto pull interval: 5分
   - Auto push interval: 5分（または手動）
4. テンプレート設定:
   - 設定 → テンプレート → テンプレートフォルダの場所: `templates`

### 5. ローカルプレビュー
```powershell
cd C:\projects\blog
hugo server -D
# http://localhost:1313 で確認
```

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
