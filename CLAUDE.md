# Claude Code メモリ

## セッション情報
- セッションURL: https://claude.ai/code/session_01Lzu36ZhTa1CGkWxSx5vQEJ
- 日付: 2026-04-25

## 調査・解決した問題

### AWS SAM ビルドエラー: UTF-8 デコードエラー

**エラー内容:**
```
Build Failed
Error: PythonPipBuilder:ResolveDependencies - 'utf-8' codec can't decode byte 0x83 in position 29: invalid start byte
```

**発生箇所:**
- パス: `G:\マイドライブ\cursor\blog\files\mnt\user-data\outputs\ai-site-agent\lambdas\scraper`
- ランタイム: Python 3.12, アーキテクチャ: x86_64
- 関数: ScrapeFunction

**原因:**
- プロジェクトパスに日本語（`マイドライブ`）が含まれている
- Windows が日本語パスを Shift-JIS (CP932) でエンコードするため、AWS SAM の PythonPipBuilder が UTF-8 として読もうとした際にデコード失敗する
- バイト `0x83` は Shift-JIS の文字コードだが UTF-8 では無効

**解決策:**
1. **推奨**: プロジェクトを日本語のないパスに移動（例: `C:\projects\blog\`）
2. requirements.txt が Shift-JIS の場合、UTF-8 に変換:
   ```powershell
   Get-Content requirements.txt -Encoding Default | Set-Content requirements.txt -Encoding UTF8
   ```
3. 一時対処として環境変数を設定:
   ```powershell
   $env:PYTHONUTF8 = 1
   sam build
   ```
