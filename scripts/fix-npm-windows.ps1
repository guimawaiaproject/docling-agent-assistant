# Fix npm TAR_ENTRY_ERROR sur Windows - utilise pnpm en alternative
# Usage: .\scripts\fix-npm-windows.ps1

$ErrorActionPreference = "Continue"
$root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
Set-Location $root

Write-Host "`n=== Fix npm Windows (TAR_ENTRY) ===" -ForegroundColor Cyan
Write-Host ""

# 1. git longpaths
Write-Host "[1] git config core.longpaths true" -ForegroundColor Yellow
git config core.longpaths true
Write-Host ""

# 2. Installer pnpm si absent
Write-Host "[2] Verifier pnpm..." -ForegroundColor Yellow
$pnpmOk = $false
try {
    $v = & pnpm --version 2>$null
    if ($v) { $pnpmOk = $true; Write-Host "  pnpm $v OK" -ForegroundColor Green }
}
catch { }
if (-not $pnpmOk) {
    Write-Host "  Installation pnpm..." -ForegroundColor Gray
    npm install -g pnpm 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { Write-Host "  pnpm installe" -ForegroundColor Green } else { Write-Host "  Echec pnpm, fallback npm" -ForegroundColor Yellow }
}

# 3. Nettoyer et installer
Write-Host "`n[3] Nettoyage docling-pwa..." -ForegroundColor Yellow
Push-Location (Join-Path $root "docling-pwa")
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item package-lock.json -ErrorAction SilentlyContinue
Remove-Item pnpm-lock.yaml -ErrorAction SilentlyContinue
Write-Host ""

# 4. Install (pnpm ou npm)
Write-Host "[4] Installation dependances..." -ForegroundColor Yellow
if ($pnpmOk -or (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    pnpm install 2>&1
} else {
    npm install 2>&1
}
$installOk = $LASTEXITCODE -eq 0
Pop-Location
Write-Host ""

# 5. Build
if ($installOk) {
    Write-Host "[5] Build frontend..." -ForegroundColor Yellow
    $env:VITE_API_URL = "http://localhost:8000"
    $env:VITE_AUTH_REQUIRED = "true"
    Push-Location (Join-Path $root "docling-pwa")
    if (Test-Path "pnpm-lock.yaml") {
        pnpm run build 2>&1
    } else {
        npm run build 2>&1
    }
    $buildOk = $LASTEXITCODE -eq 0
    Pop-Location
    Write-Host ""
    if ($buildOk) {
        Write-Host "=== BUILD OK ===" -ForegroundColor Green
    } else {
        Write-Host "=== BUILD ECHEC - voir docs/FIX-NPM-TAR-ENTRY-WINDOWS.md ===" -ForegroundColor Red
    }
} else {
    Write-Host "=== INSTALL ECHEC - essayer WSL ou pnpm ===" -ForegroundColor Red
    Write-Host "  Voir: docs/FIX-NPM-TAR-ENTRY-WINDOWS.md" -ForegroundColor Gray
}
Write-Host ""
