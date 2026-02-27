# Nettoyage du projet pour copier-coller
# Supprime : node_modules, __pycache__, venv, dist, coverage, .cursor, desktop.ini

$root = $PSScriptRoot

@(
    "docling-pwa\node_modules",
    "node_modules",
    ".pytest_cache",
    "venv",
    ".venv",
    "docling-pwa\dist",
    "dist",
    "coverage",
    "docling-pwa\coverage",
    ".cursor"
) | ForEach-Object {
    $path = Join-Path $root $_
    if (Test-Path $path) {
        Remove-Item -Recurse -Force $path -ErrorAction SilentlyContinue
        Write-Host "Supprimé: $_"
    }
}

Get-ChildItem -Path $root -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Write-Host "Supprimé: __pycache__"

Get-ChildItem -Path $root -Recurse -Filter "desktop.ini" -ErrorAction SilentlyContinue | Remove-Item -Force
Write-Host "Supprimé: desktop.ini"

Write-Host "`nNettoyage terminé. Le dossier est prêt pour copier-coller."
