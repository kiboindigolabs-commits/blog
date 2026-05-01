# sync-posts.ps1
# Obsidian vault の記事を blog リポジトリに同期して自動デプロイ
#
# 使い方:
#   PowerShell で実行: .\scripts\sync-posts.ps1
#   または Obsidian の Shell commands プラグインから実行

$VaultPostsPath = "C:\obsidian-vault\blog\posts"
$BlogPostsPath  = "C:\projects\blog\content\posts"
$BlogRepoPath   = "C:\projects\blog"

# 記事フォルダが存在しなければ作成
if (-not (Test-Path $VaultPostsPath)) {
    New-Item -ItemType Directory -Force -Path $VaultPostsPath | Out-Null
    Write-Host "記事フォルダを作成しました: $VaultPostsPath" -ForegroundColor Green
}
if (-not (Test-Path $BlogPostsPath)) {
    New-Item -ItemType Directory -Force -Path $BlogPostsPath | Out-Null
}

# 記事を同期（vault → blog repo）
Write-Host "記事を同期中..." -ForegroundColor Cyan
Copy-Item -Path "$VaultPostsPath\*.md" -Destination $BlogPostsPath -Force -ErrorAction SilentlyContinue

# git commit & push
Set-Location $BlogRepoPath

$ChangedFiles = git status --porcelain
if ($ChangedFiles) {
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm"
    git add content/posts/
    git commit -m "記事を更新: $Timestamp"
    git push origin main
    Write-Host "デプロイ完了！GitHub Actions でビルドが始まります。" -ForegroundColor Green
} else {
    Write-Host "変更なし。デプロイをスキップしました。" -ForegroundColor Yellow
}
