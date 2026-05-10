# AI Blogネタ自動収集タスクをWindowsタスクスケジューラに登録するスクリプト
# 管理者権限は不要（現在のユーザーで登録）
#
# 使い方:
#   .\scripts\register-scheduler.ps1
#
# 登録内容:
#   - タスク名: AiBlogCollectIdeas
#   - 実行日時: 毎週月曜・木曜 22:30
#   - 実行: python scripts/collect-ideas.py

param(
    [string]$PythonPath = "python",
    [string]$BlogRoot = "C:\projects\blog",
    [string]$ApiKeyEnvVar = "ANTHROPIC_API_KEY"
)

$TaskName = "AiBlogCollectIdeas"
$ScriptPath = Join-Path $BlogRoot "scripts\collect-ideas.py"

# APIキーの確認
$ApiKey = [System.Environment]::GetEnvironmentVariable($ApiKeyEnvVar, "User")
if (-not $ApiKey) {
    $ApiKey = [System.Environment]::GetEnvironmentVariable($ApiKeyEnvVar, "Machine")
}
if (-not $ApiKey) {
    Write-Warning "環境変数 $ApiKeyEnvVar が見つかりません。"
    Write-Warning "タスク登録後に手動で設定してください:"
    Write-Warning "  [システムのプロパティ] > [環境変数] > ユーザー変数に追加"
    Write-Warning "  または: `$env:ANTHROPIC_API_KEY = 'sk-ant-...' を永続化"
}

# 実行コマンド（環境変数を引き継いで実行するラッパー）
$Command = $PythonPath
$Arguments = "`"$ScriptPath`""

# トリガー: 毎週月曜 22:30
$TriggerMonday = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Monday `
    -At "22:30"

# トリガー: 毎週木曜 22:30
$TriggerThursday = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek Thursday `
    -At "22:30"

# アクション
$Action = New-ScheduledTaskAction `
    -Execute $Command `
    -Argument $Arguments `
    -WorkingDirectory $BlogRoot

# 設定
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30) `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# 既存タスクがあれば削除
$existing = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existing) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "既存タスクを削除しました: $TaskName"
}

# タスク登録
Register-ScheduledTask `
    -TaskName $TaskName `
    -Trigger $TriggerMonday, $TriggerThursday `
    -Action $Action `
    -Settings $Settings `
    -Description "AI Blogネタ自動収集（週2回 月・木 22:30）" `
    -RunLevel Limited | Out-Null

Write-Host ""
Write-Host "✅ タスクスケジューラへの登録が完了しました！" -ForegroundColor Green
Write-Host ""
Write-Host "   タスク名 : $TaskName"
Write-Host "   実行日時 : 毎週月曜・木曜 22:30"
Write-Host "   スクリプト: $ScriptPath"
Write-Host ""
Write-Host "確認方法:"
Write-Host "   Get-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "手動でテスト実行:"
Write-Host "   Start-ScheduledTask -TaskName '$TaskName'"
Write-Host ""
Write-Host "登録解除:"
Write-Host "   Unregister-ScheduledTask -TaskName '$TaskName'"
