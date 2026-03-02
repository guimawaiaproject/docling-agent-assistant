# Review code — ruff + gito (si configuré)
# L'agent EXÉCUTE ce script pour reviewer

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== Ruff ===" -ForegroundColor Cyan
Push-Location apps\api; uv run ruff check . ../../scripts; Pop-Location

Write-Host "=== Gito (si configuré) ===" -ForegroundColor Cyan
if (Get-Command gito -ErrorAction SilentlyContinue) {
  try { gito review } catch { Write-Host "Gito non configuré — skip" }
} else {
  Write-Host "Gito non installé — skip"
}
