# reslabo.jp AI自動ブログシステム 仕様書

作成日: 2026-04-25  
対象サイト: http://reslabo.jp/  
テーマ: AIを学ぶ情報メディア

---

## 1. プロジェクト概要

### 目的
Claude AI を活用してAI関連の技術記事を自動生成・投稿し、「AIを学ぶ」をコンセプトとしたブログメディアを無人運用する。

### コンセプト
- **ターゲット読者**: AIに興味を持つ初心者〜中級者
- **コンテンツ方針**: 最新AIツール・サービスのレビュー、使い方、トレンド解説
- **更新頻度**: 毎日1記事（自動）

---

## 2. 全体アーキテクチャ

```
┌─────────────────────────────────────────────────────────┐
│                    AWS クラウド                          │
│                                                         │
│  EventBridge (毎日6:00 JST)                             │
│       │                                                 │
│       ▼                                                 │
│  Step Functions (パイプライン制御)                       │
│       │                                                 │
│       ├─ 1. Scraper Lambda                              │
│       │      └─ AIトレンド情報収集 → S3(raw/)           │
│       │                                                 │
│       ├─ 2. Editor-AI Lambda (Claude Sonnet)            │
│       │      └─ 記事アウトライン生成 → S3(outlines/)    │
│       │                                                 │
│       ├─ 3. Writer-AI Lambda (Claude Sonnet)            │
│       │      └─ 本文HTML生成 → S3(drafts/)              │
│       │                                                 │
│       ├─ 4. Validator-AI Lambda (Claude Haiku)          │
│       │      ├─ PASS(≥0.85) → 次へ                     │
│       │      ├─ RETRY(<3回) → Writer-AIへ戻る           │
│       │      └─ MANUAL_REVIEW → SNS通知で終了           │
│       │                                                 │
│       └─ 5. WP-Publisher Lambda                         │
│              ├─ WordPress REST API で投稿               │
│              ├─ SNS投稿（将来拡張）                     │
│              └─ S3(published/) にアーカイブ             │
│                                                         │
│  SSM Parameter Store（シークレット管理）                 │
│  SNS（エラー通知・手動レビュー依頼）                    │
└─────────────────────────────────────────────────────────┘
                          │
                          │ WordPress REST API
                          ▼
             ┌────────────────────────┐
             │  reslabo.jp            │
             │  (お名前.com レンタル)  │
             │  WordPress             │
             └────────────────────────┘
```

---

## 3. コンポーネント詳細

### 3-1. Scraper Lambda

| 項目 | 内容 |
|------|------|
| 役割 | AIトレンド情報の収集 |
| 収集先候補 | Product Hunt (AI カテゴリ)、Hacker News、Zenn、Qiita |
| 出力 | `s3://[bucket]/raw/YYYY-MM-DD.json` |
| 保存期間 | 30日（S3ライフサイクル自動削除） |

**収集する情報:**
- AIツール・サービス名
- 概要・特徴
- URL
- カテゴリ（画像生成/文章生成/コーディング支援 等）

---

### 3-2. Editor-AI Lambda（Claude Sonnet）

| 項目 | 内容 |
|------|------|
| 役割 | 記事アウトライン・構成の生成 |
| モデル | claude-sonnet-4-6 |
| 入力 | raw JSON（スクレイプ結果） |
| 出力 | `s3://[bucket]/outlines/YYYY-MM-DD.json` |

**生成するアウトライン内容:**
- タイトル（SEO最適化）
- メタディスクリプション
- 見出し構成（H2/H3）
- キーワード
- ターゲット読者設定

---

### 3-3. Writer-AI Lambda（Claude Sonnet）

| 項目 | 内容 |
|------|------|
| 役割 | 本文HTML記事の生成 |
| モデル | claude-sonnet-4-6 |
| 入力 | アウトライン JSON |
| 出力 | `s3://[bucket]/drafts/YYYY-MM-DD.json` |

**生成する記事構成:**
- リード文（読者の課題提示）
- 各セクション本文（500〜800字/セクション）
- まとめ
- CTAセクション
- SNS投稿テキスト（X/Twitter用）

---

### 3-4. Validator-AI Lambda（Claude Haiku）

| 項目 | 内容 |
|------|------|
| 役割 | 品質・SEO・コンプライアンスチェック |
| モデル | claude-haiku-4-5-20251001（コスト最適化） |
| 合格スコア | 0.85以上 |
| 最大リトライ | 3回 |

**スコア項目:**

| チェック項目 | 配点 | 内容 |
|-------------|------|------|
| 事実正確性 | 40% | 誤情報・hallucination検出 |
| SEO構造 | 30% | 見出し構成・キーワード密度・文字数 |
| コンプライアンス | 30% | 著作権・アフィリエイト表記・薬機法等 |

---

### 3-5. WP-Publisher Lambda

| 項目 | 内容 |
|------|------|
| 役割 | WordPress への投稿・アーカイブ |
| 認証 | WordPress アプリケーションパスワード |
| エンドポイント | `http://reslabo.jp/wp-json/wp/v2/posts` |
| 投稿ステータス | `publish`（即時公開）または `draft`（要確認） |

**投稿内容:**
- タイトル
- 本文（HTML）
- カテゴリ・タグ（自動付与）
- アイキャッチ画像（将来拡張）
- メタディスクリプション（SEO Pluginへ）

---

## 4. シークレット管理（SSM Parameter Store）

| パラメータ名 | 内容 |
|-------------|------|
| `/ai-site/claude/api_key` | Anthropic API キー |
| `/ai-site/wp/username` | WordPress ユーザー名 |
| `/ai-site/wp/app_password` | WordPress アプリケーションパスワード |
| `/ai-site/wp/url` | `http://reslabo.jp` |

---

## 5. S3 バケット構成

```
s3://[bucket-name]/
├── raw/           # スクレイプ生データ（30日後自動削除）
├── outlines/      # 記事アウトライン
├── drafts/        # 生成された下書き記事
└── published/     # 公開済み記事アーカイブ（90日後Glacierへ移行）
```

---

## 6. 通知・モニタリング

| 通知タイミング | 内容 |
|--------------|------|
| パイプラインエラー | SNS → メール通知 |
| MANUAL_REVIEW | SNS → メール通知（記事URLを添付） |
| 正常完了 | ログのみ（通知なし） |

**モニタリング:**
- `files/dashboard.html` をブラウザで開くと状況確認可能
- CloudWatch Logs で各Lambda の詳細ログ確認

---

## 7. 実装ロードマップ

### Phase 1: 基盤構築（優先）
- [ ] WordPress REST API の有効化・アプリケーションパスワード取得
- [ ] AWS アカウント設定・IAM ロール作成
- [ ] SSM Parameter Store へシークレット登録
- [ ] S3 バケット作成
- [ ] `template.yaml` (SAM) 作成

### Phase 2: Lambda 実装
- [ ] Scraper Lambda（AI系サイトのスクレイピング）
- [ ] Editor-AI Lambda（Claude Sonnet）
- [ ] Writer-AI Lambda（Claude Sonnet）
- [ ] Validator-AI Lambda（Claude Haiku）
- [ ] WP-Publisher Lambda

### Phase 3: パイプライン統合
- [ ] Step Functions ステートマシン（pipeline.json）
- [ ] EventBridge スケジュール設定（毎日6:00 JST）
- [ ] SAM ビルド・デプロイ

### Phase 4: 品質向上
- [ ] ダッシュボード（dashboard.html）整備
- [ ] アイキャッチ画像の自動生成（Stable Diffusion等）
- [ ] SNS自動投稿（X/Twitter）
- [ ] 記事カテゴリの自動分類精度向上

---

## 8. コスト試算（月額概算）

| サービス | 用途 | 概算 |
|---------|------|------|
| AWS Lambda | 5関数 × 30日 | ~$1 |
| AWS Step Functions | 30実行/月 | ~$0.01 |
| S3 | データ保存 | ~$0.5 |
| EventBridge | スケジュール | 無料枠内 |
| SSM Parameter Store | シークレット管理 | 無料枠内 |
| Claude Sonnet API | editor + writer (30記事) | ~$5〜10 |
| Claude Haiku API | validator (30記事) | ~$0.5 |
| **合計** | | **~$7〜12/月** |

※ Claude APIの費用はトークン数により変動

---

## 9. WordPress 側の事前準備

1. **REST APIの有効化確認**  
   `http://reslabo.jp/wp-json/wp/v2/` にアクセスしてJSONが返ることを確認

2. **アプリケーションパスワードの取得**  
   WordPress管理画面 → ユーザー → プロフィール → アプリケーションパスワード

3. **推奨プラグイン**
   - Yoast SEO または Rank Math（メタディスクリプション設定用）
   - WP REST API の認証確認

---

## 10. ファイル構成（実装後）

```
blog/
├── CLAUDE.md
├── SPEC.md                          # この仕様書
├── files/
│   ├── template.yaml                # SAM テンプレート
│   ├── pipeline.json                # Step Functions 定義
│   ├── dashboard.html               # 監視ダッシュボード
│   └── mnt/user-data/outputs/ai-site-agent/lambdas/
│       ├── scraper/
│       │   └── lambda_function.py
│       ├── editor_ai/
│       │   └── lambda_function.py
│       ├── writer_ai/
│       │   └── lambda_function.py
│       ├── validator_ai/
│       │   └── lambda_function.py
│       └── wp_publisher/
│           └── lambda_function.py
└── README.md
```
