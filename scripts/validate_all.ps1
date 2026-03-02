# Validation complète — à lancer après toute modification (monorepo apps/)
# Usage: .\scripts\validate_all.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== 1. Lint backend (apps/api) ===" -ForegroundColor Cyan
Push-Location apps/api; uv run ruff check . ../../scripts; Pop-Location

Write-Host "=== 2. Lint frontend (apps/pwa) ===" -ForegroundColor Cyan
Push-Location apps/pwa; pnpm run lint; Pop-Location

Write-Host "=== 2b. Build frontend (PostCSS/Tailwind) ===" -ForegroundColor Cyan
$env:VITE_API_URL = "http://localhost:8000"
$env:VITE_AUTH_REQUIRED = "true"
Push-Location apps/pwa
pnpm run build
Pop-Location

Write-Host "=== 3. Validate skills ===" -ForegroundColor Cyan
python scripts/validate_skills.py

Write-Host "=== 4. Tests backend (apps/api) ===" -ForegroundColor Cyan
Push-Location apps/api; uv run pytest tests -v --tb=short; Pop-Location

Write-Host "=== 5. Tests frontend (apps/pwa) ===" -ForegroundColor Cyan
Push-Location apps/pwa; pnpm run test; Pop-Location

Write-Host "=== Validation OK ===" -ForegroundColor Green
