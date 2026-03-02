# Nettoyage — Docling (cache, build, node_modules)
# Usage: .\scripts\clean.ps1 [--full]
# --full : supprime aussi node_modules (réinstaller avec pnpm install)

param([switch]$Full)

$ErrorActionPreference = "Stop"
$root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
Set-Location $root

Write-Host "`n=== DOCLING — NETTOYAGE ===" -ForegroundColor Cyan
Write-Host ""

$removed = 0

function Remove-IfExists {
    param([string]$Path, [string]$Label)
    if (Test-Path $Path) {
        Remove-Item -Recurse -Force $Path -ErrorAction SilentlyContinue
        Write-Host "[OK] Supprime: $Label" -ForegroundColor Green
        $script:removed++
    }
}

# Cache Python (pas .venv — conserver l'environnement)
Remove-IfExists "apps\api\.pytest_cache" ".pytest_cache"
Remove-IfExists "apps\api\.ruff_cache" ".ruff_cache"
Remove-IfExists "__pycache__" "__pycache__"
# __pycache__ : uniquement apps/api et scripts (evite node_modules = blocage)
@("apps\api", "scripts") | ForEach-Object {
    if (Test-Path $_) {
        Get-ChildItem -Path $_ -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
            Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
            if ($?) { $removed++; Write-Host "[OK] Supprime: $($_.FullName)" -ForegroundColor Green }
        }
    }
}

# Build frontend
Remove-IfExists "apps\pwa\dist" "dist"
Remove-IfExists "apps\pwa\coverage" "coverage"

# MkDocs
Remove-IfExists "site" "site (MkDocs)"

# Cache divers
Remove-IfExists ".turbo" ".turbo"
# tsbuildinfo : apps/api + racine apps/pwa uniquement (pas -Recurse dans pwa = evite node_modules)
@("apps\api", "scripts") | ForEach-Object {
    if (Test-Path $_) {
        Get-ChildItem -Path $_ -Recurse -Filter "*.tsbuildinfo" -File -ErrorAction SilentlyContinue | ForEach-Object {
            Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
            if ($?) { $removed++; Write-Host "[OK] Supprime: $($_.Name)" -ForegroundColor Green }
        }
    }
}
if (Test-Path "apps\pwa") {
    Get-ChildItem -Path "apps\pwa" -Filter "*.tsbuildinfo" -File -ErrorAction SilentlyContinue | ForEach-Object {
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
        if ($?) { $removed++; Write-Host "[OK] Supprime: $($_.Name)" -ForegroundColor Green }
    }
}

if ($Full) {
    Write-Host "`n[FULL] Suppression node_modules..." -ForegroundColor Yellow
    Remove-IfExists "apps\pwa\node_modules" "node_modules"

    Write-Host "`n[FULL] Suppression lock files (optionnel)..." -ForegroundColor Gray
    # Ne pas supprimer pnpm-lock par défaut - réinstall avec pnpm install
}

Write-Host "`n=== NETTOYAGE TERMINE ===" -ForegroundColor Green
if ($Full) {
    Write-Host "Reinstaller: cd apps/pwa && pnpm install" -ForegroundColor Gray
}
Write-Host ""
