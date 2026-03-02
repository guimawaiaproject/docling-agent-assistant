# Audit dépendances — Docling (pip-audit + pnpm audit)
# Usage: .\scripts\audit-deps.ps1

$ErrorActionPreference = "Continue"
$root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
Set-Location $root

Write-Host "`n=== DOCLING — AUDIT DÉPENDANCES ===" -ForegroundColor Cyan
Write-Host ""

$failed = $false

# 1. Python (pip-audit)
Write-Host "[1] Python (pip-audit)..." -ForegroundColor Yellow
$pipAudit = Get-Command pip-audit -ErrorAction SilentlyContinue
if ($pipAudit) {
    Push-Location apps/api
    $out = uv export --no-dev -o $env:TEMP\docling-req.txt 2>&1
    if ($LASTEXITCODE -eq 0) {
        pip-audit -r $env:TEMP\docling-req.txt 2>&1
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } else {
        pip-audit 2>&1
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    }
    Pop-Location
} else {
    Write-Host "  pip-audit non installé. pip install pip-audit" -ForegroundColor Gray
}

Write-Host ""

# 2. Node (pnpm audit)
Write-Host "[2] Node (pnpm audit)..." -ForegroundColor Yellow
if (Test-Path "apps\pwa\package.json") {
    Push-Location apps\pwa
    if (Get-Command pnpm -ErrorAction SilentlyContinue) {
        pnpm audit 2>&1
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    } else {
        npm audit 2>&1
        if ($LASTEXITCODE -ne 0) { $failed = $true }
    }
    Pop-Location
}

Write-Host ""
Write-Host "=== AUDIT TERMINÉ ===" -ForegroundColor $(if ($failed) { "Red" } else { "Green" })
if ($failed) {
    Write-Host "Vulnérabilités détectées. Voir ci-dessus." -ForegroundColor Yellow
}
Write-Host ""
exit $(if ($failed) { 1 } else { 0 })
