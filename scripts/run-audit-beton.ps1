# run-audit-beton.ps1
# Lance l'Audit Bêton Docling — INIT + instructions pour Cursor
# Usage: .\scripts\run-audit-beton.ps1

$ErrorActionPreference = "Continue"
$ProjectRoot = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
if (-not (Test-Path (Join-Path $ProjectRoot "docling-pwa")) -and (Test-Path (Join-Path (Get-Location) "docling-pwa"))) {
    $ProjectRoot = Get-Location
}
Set-Location $ProjectRoot

$OutputDir = Join-Path $env:TEMP "audit-beton-init"
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AUDIT BETON - INIT Docling" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# INIT-1 : Cartographie brute
Write-Host "[INIT-1] Cartographie brute..." -ForegroundColor Yellow
$allFiles = Get-ChildItem -Path . -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch "\\\.git\\" -and $_.FullName -notmatch "\\node_modules\\" } |
    Select-Object -ExpandProperty FullName | Sort-Object
$allFiles | ForEach-Object { $_.Replace("$ProjectRoot\", "").Replace("\", "/") } | Set-Content -Path (Join-Path $OutputDir "all_files_raw.txt") -Encoding UTF8
$fileCount = ($allFiles | Measure-Object).Count
Write-Host "  -> Nombre total de fichiers : $fileCount" -ForegroundColor Green
Write-Host ""

# INIT-2 : Fichiers suspects
Write-Host '[INIT-2] Fichiers suspects - anciens audits' -ForegroundColor Yellow
$patterns = @("audit", "backup", "old", "v1", "v2", "draft", "temp", "ancien", "resultat", "result", "rapport", "report", "bak", "todo", "notes")
$suspects = $allFiles | Where-Object {
    $path = $_ -replace [regex]::Escape($ProjectRoot), ""
    $pathLower = $path.ToLower()
    $patterns | Where-Object { $pathLower -match $_ }
} | ForEach-Object { $_.Replace("$ProjectRoot\", "").Replace("\", "/") }
if ($suspects) {
    $suspects | ForEach-Object { Write-Host "  $_" }
    $suspects | Set-Content -Path (Join-Path $OutputDir "suspect_files.txt") -Encoding UTF8
    Write-Host "  -> $($suspects.Count) fichiers suspects -> 01_NETTOYAGE.md" -ForegroundColor Green
} else {
    Write-Host "  -> Aucun fichier suspect trouve" -ForegroundColor Green
}
Write-Host ""

# INIT-3 : Lignes de code
Write-Host "[INIT-3] Lignes de code réelles..." -ForegroundColor Yellow
$extensions = @("*.py", "*.js", "*.jsx", "*.ts", "*.tsx", "*.css")
$totalLines = 0
foreach ($ext in $extensions) {
    Get-ChildItem -Path . -Recurse -Filter $ext -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -notmatch "\\\.git\\" -and
            $_.FullName -notmatch "\\node_modules\\" -and
            $_.FullName -notmatch "\\dist\\"
        } | ForEach-Object {
            $totalLines += (Get-Content $_.FullName -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
        }
}
Write-Host "  -> Nombre total de lignes a analyser : $totalLines" -ForegroundColor Green
Write-Host ""

# INIT-4 : État du build
Write-Host "[INIT-4] État du build AVANT audit..." -ForegroundColor Yellow
$pwaPath = Join-Path $ProjectRoot "docling-pwa"
if (Test-Path $pwaPath) {
    Push-Location $pwaPath
    try {
        $buildOut = npm run build 2>&1 | Out-String
        $wCount = ([regex]::Matches($buildOut, "warn|warning", "IgnoreCase")).Count
        $eCount = ([regex]::Matches($buildOut, " error ", "IgnoreCase")).Count
        $color = if ($eCount -gt 0) { "Red" } else { "Green" }
        Write-Host "  Frontend build : $eCount erreurs, $wCount warnings" -ForegroundColor $color
    } catch {
        Write-Host "  Frontend build : $($_.Exception.Message)" -ForegroundColor Red
    }
    Pop-Location
} else {
    Write-Host "  docling-pwa/ non trouvé" -ForegroundColor Red
}

Push-Location $ProjectRoot
try {
    $pythonOut = python -c "import api" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Backend import : OK" -ForegroundColor Green
    } else {
        Write-Host "  Backend import : $pythonOut" -ForegroundColor Red
    }
} catch {
    Write-Host "  Backend import : $($_.Exception.Message)" -ForegroundColor Red
}
Pop-Location
Write-Host ""

# Résumé
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INIT terminé. Données dans : $OutputDir" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "PROCHAINE ETAPE - Lancer l'audit dans Cursor :" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Cmd/Ctrl + K" -ForegroundColor White
Write-Host "  2. Taper : audit beton" -ForegroundColor White
Write-Host "  3. Ou coller : @.cursor/commands/audit-beton.md (avec @)" -ForegroundColor White
Write-Host ""
Write-Host "La commande activera les agents spécialisés pour chaque phase :" -ForegroundColor Gray
Write-Host "  01 - context-specialist (Nettoyage)" -ForegroundColor Gray
Write-Host "  02 - context-specialist (Cartographie)" -ForegroundColor Gray
Write-Host "  03 - api-reviewer (Backend)" -ForegroundColor Gray
Write-Host "  04 - feature-developer (Frontend)" -ForegroundColor Gray
Write-Host "  05 - migration-assistant (BDD)" -ForegroundColor Gray
Write-Host "  06 - security-reviewer (Securite)" -ForegroundColor Gray
Write-Host "  07 - test-generator (Tests)" -ForegroundColor Gray
Write-Host "  08 - system-architect (Build)" -ForegroundColor Gray
Write-Host "  09 - context-specialist (Performance)" -ForegroundColor Gray
Write-Host "  10 - docs-writer (Rapport final)" -ForegroundColor Gray
Write-Host ""
