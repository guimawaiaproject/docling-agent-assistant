# Validation complète — à lancer après toute modification
# Usage: .\scripts\validate_all.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== 1. Lint backend ===" -ForegroundColor Cyan
ruff check api.py backend/ scripts/ tests/ migrations/

Write-Host "=== 2. Lint frontend ===" -ForegroundColor Cyan
Push-Location docling-pwa; npm run lint; Pop-Location

Write-Host "=== 2b. Build frontend (PostCSS/Tailwind) ===" -ForegroundColor Cyan
$env:VITE_API_URL = "http://localhost:8000"
$env:VITE_AUTH_REQUIRED = "true"
Push-Location docling-pwa
if (Test-Path "pnpm-lock.yaml") { pnpm run build } else { npm run build }
Pop-Location

Write-Host "=== 3. Validate skills ===" -ForegroundColor Cyan
python scripts/validate_skills.py

Write-Host "=== 4. Tests backend ===" -ForegroundColor Cyan
pytest tests/01_unit -v --tb=short -q

Write-Host "=== 5. Tests frontend ===" -ForegroundColor Cyan
Push-Location docling-pwa; npx vitest run --reporter=dot; Pop-Location

Write-Host "=== Validation OK ===" -ForegroundColor Green
