# PowerShell Script to easily push to GitHub

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "  TRAFFIC INTELLIGENCE SYSTEM - GITHUB PUSHER" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Ask the user for their GitHub Repository URL
$repoUrl = Read-Host "Please paste your GitHub Repository URL (e.g., https://github.com/username/repo.git)"

if ([string]::IsNullOrWhiteSpace($repoUrl)) {
    Write-Error "Invalid URL. Exiting..."
    Start-Sleep -Seconds 3
    exit
}

Write-Host ""
Write-Host "Linking local repository with $repoUrl..." -ForegroundColor Yellow

# 2. Check if git remote 'origin' already exists
$existingRemote = git remote | Where-Object { $_ -eq "origin" }

if ($existingRemote) {
    # If it exists, update it
    git remote set-url origin $repoUrl
} else {
    # If not, add it
    git remote add origin $repoUrl
}

Write-Host ""
Write-Host "Pushing code to GitHub main branch..." -ForegroundColor Yellow
Write-Host "(If prompted, please authenticate in the browser window or credentials prompt.)" -ForegroundColor Gray
Write-Host ""

# 3. Push to main branch
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Green
    Write-Host "  SUCCESS! Project pushed to GitHub successfully!" -ForegroundColor Green
    Write-Host "==================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "==================================================" -ForegroundColor Red
    Write-Host "  Push failed. Please check the error details above." -ForegroundColor Red
    Write-Host "==================================================" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = [Console]::ReadKey($true)
