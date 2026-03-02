# Setup initial — Docling (première installation)
# Usage: .\scripts\setup.ps1 [-Build] [-Migrate] [-NoLaunch]
#   -Build    : build frontend (pnpm run build)
#   -Migrate  : alembic upgrade head
#   -NoLaunch : ne pas lancer l'app a la fin (par defaut: lance run_local.bat)

param(
    [switch]$Build,
    [switch]$Migrate,
    [switch]$NoLaunch  # Empeche le lancement a la fin (par defaut: lance)
)

$ErrorActionPreference = "Stop"
$root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
Set-Location $root

Write-Host "`n=== DOCLING — SETUP INITIAL ===" -ForegroundColor Cyan
Write-Host ""

# 1. .env
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "[OK] .env cree depuis .env.example" -ForegroundColor Green
        Write-Host "     Remplir GEMINI_API_KEY, DATABASE_URL, JWT_SECRET dans .env" -ForegroundColor Yellow
    } else {
        Write-Host "[WARN] .env.example absent" -ForegroundColor Yellow
    }
} else {
    Write-Host "[OK] .env existe" -ForegroundColor Green
}

# 2. Backend (uv sync)
Write-Host "`n[2] Backend (apps/api)..." -ForegroundColor Cyan
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "[FAIL] uv manquant. https://docs.astral.sh/uv/" -ForegroundColor Red
    exit 1
}
# Desactiver VIRTUAL_ENV si venv racine active (evite conflit avec apps/api/.venv)
$env:VIRTUAL_ENV = $null
Push-Location apps/api
uv sync --all-extras
Pop-Location
Write-Host "[OK] uv sync (deps + dev)" -ForegroundColor Green

# 3. Frontend (pnpm install)
Write-Host "`n[3] Frontend (apps/pwa)..." -ForegroundColor Cyan
if (Test-Path "apps/pwa/package.json") {
    Push-Location apps/pwa
    if (Get-Command pnpm -ErrorAction SilentlyContinue) {
        pnpm install
        Write-Host "[OK] pnpm install" -ForegroundColor Green
    } else {
        Write-Host "[WARN] pnpm manquant. npm install -g pnpm" -ForegroundColor Yellow
    }
    Pop-Location
}

# 4. Migrations (optionnel)
if ($Migrate) {
    Write-Host "`n[4] Migrations..." -ForegroundColor Cyan
    Push-Location apps/api
    uv run alembic upgrade head
    Pop-Location
    Write-Host "[OK] alembic upgrade head" -ForegroundColor Green
}

# 5. Build frontend (optionnel)
if ($Build) {
    Write-Host "`n[5] Build frontend..." -ForegroundColor Cyan
    $env:VITE_API_URL = "http://localhost:8000"
    $env:VITE_AUTH_REQUIRED = "true"
    Push-Location apps/pwa
    pnpm run build
    Pop-Location
    Write-Host "[OK] pnpm run build" -ForegroundColor Green
}

Write-Host "`n=== SETUP TERMINE ===" -ForegroundColor Green
if (-not $NoLaunch) {
    Write-Host "Lancement de l'app (nouvelle fenetre)..." -ForegroundColor Yellow
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c", "`"$root\run_local.bat`"" -WorkingDirectory $root
} else {
    Write-Host "Lancer: run_local.bat" -ForegroundColor Gray
    Write-Host "Ou relancer setup sans -NoLaunch" -ForegroundColor Gray
}
Write-Host "Si pnpm affiche 'Ignored build scripts': cd apps/pwa && pnpm approve-builds" -ForegroundColor DarkGray
Write-Host ""
