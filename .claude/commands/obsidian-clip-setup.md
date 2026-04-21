Explain in Japanese how to set up a complete Android Chrome → Obsidian web clipping workflow. Cover all the options below with pros/cons for each approach.

## Options to explain

### Option 1: Claude Code スキル（このスキル）
- `/obsidian-clip <URL>` でURLを渡すとAIが要約してMarkdownを生成
- 生成されたノートをObsidianにコピペして保存

### Option 2: Obsidian Web Clipper (公式)
- URL: https://obsidian.md/clipper
- Chrome拡張機能として提供
- AndroidのChromeでも動作（拡張機能対応版Chrome）
- ワンタップでObsidianに保存可能
- テンプレートカスタマイズ対応

### Option 3: Shortcut + Claude API（自動化）
Taskerまたは「Macrodroid」を使った自動化フロー：
1. Chrome共有ボタン → TaskerのURLインテントを受け取る
2. Tasker: HTTPリクエストでページ取得
3. Tasker: Claude API（claude-haiku-4-5）で要約生成
4. Tasker: Obsidian URIスキーム `obsidian://new?vault=MyVault&name=<title>&content=<note>` でノート作成

### Option 4: Android Sharesheet + Shortcuts
- ChromeのShareメニューからObsidianに直接共有（URLのみ）
- Obsidianの「URLから取得」プラグインと組み合わせ

## Tasker HTTP Action for Claude API example

Provide a concrete example of the Tasker action that calls Claude API:

```
HTTP Request:
  Method: POST
  URL: https://api.anthropic.com/v1/messages
  Headers:
    x-api-key: %claude_api_key
    anthropic-version: 2023-06-01
    content-type: application/json
  Body:
    {
      "model": "claude-haiku-4-5-20251001",
      "max_tokens": 1024,
      "messages": [{
        "role": "user",
        "content": "以下のウェブページの内容を日本語で要約し、Obsidian用のMarkdownノートを作成してください。\n\nURL: %clip_url\n\nページ内容: %page_content"
      }]
    }
```

## Obsidian URI scheme

Explain the `obsidian://` URI scheme for creating notes programmatically:
```
obsidian://new?vault=VaultName&name=NoteTitle&content=NoteContent
```

This can be called from Tasker, Shortcuts, or any Android automation tool to create a note directly in Obsidian.

Provide the full setup guide in a clear, step-by-step format in Japanese.
