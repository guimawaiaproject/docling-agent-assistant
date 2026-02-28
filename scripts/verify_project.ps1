# verify_project.ps1 — Vérification complète du projet Docling
# Aligné sur Audit Bêton (AUDIT_BETON/10_RAPPORT_FINAL.md)
# Usage: .\scripts\verify_project.ps1
# Exit 0 = OK, Exit 1 = Échec

$ErrorActionPreference = "Continue"
$root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
Set-Location $root

$results = @{}
$failed = $false

function Test-Step {
    param([string]$Id, [string]$Name, [scriptblock]$Cmd, [switch]$Optional)
    Write-Host "`n[$Id] $Name" -ForegroundColor Cyan
    try {
        $out = & $Cmd 2>&1
        if ($LASTEXITCODE -ne 0 -and $null -ne $LASTEXITCODE) {
            Write-Host "  [FAIL] exit $LASTEXITCODE" -ForegroundColor Red
            $script:results[$Id] = "FAIL"
            if (-not $Optional) { $script:failed = $true }
            return $false
        }
        Write-Host "  [OK]" -ForegroundColor Green
        $script:results[$Id] = "OK"
        return $true
    } catch {
        Write-Host "  [FAIL] $_" -ForegroundColor Red
        $script:results[$Id] = "FAIL"
        if (-not $Optional) { $script:failed = $true }
        return $false
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  DOCLING - VERIFICATION PROJET COMPLETE" -ForegroundColor Yellow
Write-Host "  (Audit Beton + SonarQube-ready)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# ─── PRÉREQUIS ─────────────────────────────────────────────────────────────
Write-Host "=== PRÉREQUIS ===" -ForegroundColor Magenta

if (-not (Test-Path ".env")) {
    Write-Host "[SKIP] .env absent - certaines verifications seront ignorees" -ForegroundColor Yellow
} else {
    $envContent = Get-Content ".env" -Raw -ErrorAction SilentlyContinue
    if ($envContent -notmatch "JWT_SECRET=.+") {
        Write-Host "[WARN] JWT_SECRET manquant - tests backend JWT peuvent echouer" -ForegroundColor Yellow
    }
}

# JWT pour pytest (requis par auth_service)
if (-not $env:JWT_SECRET) {
    $env:JWT_SECRET = "test-secret-32-chars-minimum-for-pytest"
}

# ─── BACKEND ───────────────────────────────────────────────────────────────
Write-Host "`n=== BACKEND ===" -ForegroundColor Magenta

Test-Step "B1" "Import api (python -c 'import api')" {
    python -c "import api; print('OK')"
}

Test-Step "B2" "Lint backend (ruff)" {
    ruff check api.py backend/ scripts/ tests/ migrations/
}

Test-Step "B3" "Tests backend (pytest)" {
    python -m pytest tests/01_unit -v --tb=short -q -x
}

# ─── FRONTEND ──────────────────────────────────────────────────────────────
Write-Host "`n=== FRONTEND ===" -ForegroundColor Magenta

$env:VITE_API_URL = "http://localhost:8000"
$env:VITE_AUTH_REQUIRED = "true"

$usePnpm = Test-Path "docling-pwa\pnpm-lock.yaml"

Test-Step "F1" "Lint frontend (eslint)" {
    Push-Location docling-pwa
    if ($usePnpm) { pnpm run lint } else { npm run lint }
    Pop-Location
} -Optional

Test-Step "F2" "Build frontend (vite)" {
    Push-Location docling-pwa
    if ($usePnpm) { pnpm run build } else { npm run build }
    Pop-Location
}

Test-Step "F3" "Tests frontend (vitest)" {
    Push-Location docling-pwa
    if ($usePnpm) { pnpm exec vitest run --reporter=dot } else { npx vitest run --reporter=dot }
    Pop-Location
}

# ─── QUALITÉ ───────────────────────────────────────────────────────────────
Write-Host "`n=== QUALITÉ ===" -ForegroundColor Magenta

Test-Step "Q1" "Validate skills" {
    python scripts/validate_skills.py
} -Optional

Test-Step "Q2" "Validate env" {
    python scripts/validate_env.py
} -Optional

# ─── DÉPLOIEMENT (Audit Bêton bloqueurs) ────────────────────────────────────
Write-Host "`n=== DÉPLOIEMENT (Audit Bêton) ===" -ForegroundColor Magenta

# D1: render.yaml — DATABASE_URL, JWT_SECRET
if (Test-Path "render.yaml") {
    $render = Get-Content "render.yaml" -Raw
    $d1 = $true
    if ($render -notmatch "DATABASE_URL") {
        Write-Host "[D1] [WARN] render.yaml : DATABASE_URL manquant" -ForegroundColor Yellow
        $d1 = $false
    }
    if ($render -notmatch "JWT_SECRET") {
        Write-Host "[D1] [WARN] render.yaml : JWT_SECRET manquant" -ForegroundColor Yellow
        $d1 = $false
    }
    if ($d1) { Write-Host "[D1] render.yaml : OK (DATABASE_URL, JWT_SECRET présents)" -ForegroundColor Green }
    else { $script:results["D1"] = "WARN" }
} else {
    Write-Host "[D1] render.yaml absent - skip" -ForegroundColor Gray
}

# D2: deploy.yml — condition secrets
if (Test-Path ".github\workflows\deploy.yml") {
    $deploy = Get-Content ".github\workflows\deploy.yml" -Raw
    if ($deploy -match "secrets\.DEPLOY_PROVIDER\s*==\s*'render'") {
        Write-Host "[D2] [WARN] deploy.yml : condition secrets.DEPLOY_PROVIDER invalide (utiliser vars)" -ForegroundColor Yellow
        $script:results["D2"] = "WARN"
    } else {
        Write-Host "[D2] deploy.yml : OK" -ForegroundColor Green
        $script:results["D2"] = "OK"
    }
}

# ─── SÉCURITÉ (pip-audit si dispo) ──────────────────────────────────────────
Write-Host "`n=== SÉCURITÉ ===" -ForegroundColor Magenta

$pipAudit = Get-Command pip-audit -ErrorAction SilentlyContinue
if ($pipAudit) {
    Write-Host "`n[S1] pip-audit (CVE)" -ForegroundColor Cyan
    $auditOut = pip-audit 2>&1 | Out-String
    if ($auditOut -match "VULNERABLE|critical|high") {
        Write-Host "  [WARN] Vulnerabilites detectees" -ForegroundColor Yellow
        Write-Host $auditOut
        $results["S1"] = "WARN"
    } else {
        Write-Host "  [OK]" -ForegroundColor Green
        $results["S1"] = "OK"
    }
} else {
    Write-Host "`n[S1] pip-audit non installe - skip (pip install pip-audit)" -ForegroundColor Gray
}

# ─── RAPPORT FINAL ──────────────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  RAPPORT" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

$ok = ($results.Values | Where-Object { $_ -eq "OK" }).Count
$fail = ($results.Values | Where-Object { $_ -eq "FAIL" }).Count
$warn = ($results.Values | Where-Object { $_ -eq "WARN" }).Count

foreach ($k in ($results.Keys | Sort-Object)) {
    $v = $results[$k]
    $color = switch ($v) { "OK" { "Green" } "FAIL" { "Red" } "WARN" { "Yellow" } default { "Gray" } }
    Write-Host "  $k : $v" -ForegroundColor $color
}

Write-Host ""
Write-Host "  OK: $ok | FAIL: $fail | WARN: $warn" -ForegroundColor $(if ($fail -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($failed) {
    Write-Host "  VERDICT : ECHEC - Corriger les erreurs avant commit/deploiement." -ForegroundColor Red
    Write-Host "  Référence : AUDIT_BETON/10_RAPPORT_FINAL.md" -ForegroundColor Gray
    Write-Host "========================================`n" -ForegroundColor Red
    exit 1
} else {
    Write-Host "  VERDICT : OK - Projet pret pour commit." -ForegroundColor Green
    if ($warn -gt 0) {
        Write-Host "  Recommandations : corriger les WARN (render.yaml, deploy.yml) avant prod." -ForegroundColor Yellow
    }
    Write-Host "========================================`n" -ForegroundColor Green
    exit 0
}
