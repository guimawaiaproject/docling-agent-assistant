# Pre-launch check - Verification complete avant de lancer l'app
# Usage: .\scripts\pre_launch_check.ps1
# Exit 0 = OK, Exit 1 = Echec (ne pas lancer)

$ErrorActionPreference = "Stop"
$root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
Set-Location $root

$failed = $false

function Test-Step {
    param([string]$Name, [scriptblock]$Cmd)
    Write-Host "`n=== $Name ===" -ForegroundColor Cyan
    try {
        & $Cmd
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            Write-Host "[FAIL] $Name (exit $LASTEXITCODE)" -ForegroundColor Red
            return $false
        }
        Write-Host "[OK] $Name" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "[FAIL] $Name : $_" -ForegroundColor Red
        return $false
    }
}

Write-Host "`n========================================" -ForegroundColor Yellow
Write-Host "  DOCLING - PRE-LAUNCH CHECK" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow

# 1. VENV
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[FAIL] venv manquant. Executer: python -m venv venv" -ForegroundColor Red
    exit 1
}
$env:Path = "$root\venv\Scripts;$env:Path"

# 2. Dependances frontend (node_modules)
$pwaDeps = @("docling-pwa\node_modules\vite", "docling-pwa\node_modules\autoprefixer", "docling-pwa\node_modules\tailwindcss", "docling-pwa\node_modules\vitest", "docling-pwa\node_modules\@eslint\js")
$missingDeps = $pwaDeps | Where-Object { -not (Test-Path $_) }
if ($missingDeps.Count -gt 0) {
    Write-Host "[FAIL] Dependances frontend manquantes. Executer: .\scripts\fix-npm-windows.ps1" -ForegroundColor Red
    exit 1
}

# 3. .env requis
if (-not (Test-Path ".env")) {
    Write-Host "[FAIL] .env manquant. Copier .env.example vers .env" -ForegroundColor Red
    exit 1
}
$envContent = Get-Content ".env" -Raw
if ($envContent -notmatch "JWT_SECRET=.+") {
    Write-Host "[FAIL] JWT_SECRET manquant dans .env" -ForegroundColor Red
    exit 1
}
if ($envContent -notmatch "DATABASE_URL=.+") {
    Write-Host "[FAIL] DATABASE_URL manquant dans .env" -ForegroundColor Red
    exit 1
}

# 4. Lint backend
if (-not (Test-Step "Lint backend" { ruff check api.py backend/ scripts/ tests/ migrations/ })) { $failed = $true }

# 5. Lint frontend
if (-not (Test-Step "Lint frontend" { Push-Location docling-pwa; if (Test-Path pnpm-lock.yaml) { pnpm run lint } else { npm run lint }; Pop-Location })) { $failed = $true }

# 6. BUILD frontend (CRITIQUE - detecte PostCSS/Tailwind)
if (-not (Test-Step "Build frontend (PostCSS/Tailwind)" { $env:VITE_API_URL = "http://localhost:8000"; $env:VITE_AUTH_REQUIRED = "true"; Push-Location docling-pwa; if (Test-Path pnpm-lock.yaml) { pnpm run build } else { npm run build }; Pop-Location })) { $failed = $true }

# 7. Tests backend
if (-not (Test-Step "Tests backend" { pytest tests/01_unit -v --tb=short -q -x })) { $failed = $true }

# 8. Tests frontend
if (-not (Test-Step "Tests frontend" { Push-Location docling-pwa; if (Test-Path pnpm-lock.yaml) { pnpm exec vitest run --reporter=dot } else { npx vitest run --reporter=dot }; Pop-Location })) { $failed = $true }

# 9. Validate skills
if (-not (Test-Step "Validate skills" { python scripts/validate_skills.py })) { $failed = $true }

Write-Host "`n========================================" -ForegroundColor $(if ($failed) { "Red" } else { "Green" })
if ($failed) {
    Write-Host "  PRE-LAUNCH CHECK : ECHEC" -ForegroundColor Red
    Write-Host "  Corriger les erreurs avant de lancer l'app." -ForegroundColor Red
    Write-Host "========================================`n" -ForegroundColor Red
    exit 1
} else {
    Write-Host "  PRE-LAUNCH CHECK : OK" -ForegroundColor Green
    Write-Host "  L'app peut etre lancee." -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
    exit 0
}
