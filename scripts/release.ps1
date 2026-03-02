# Release — Docling (bump version, tag git)
# Usage: .\scripts\release.ps1 [patch|minor|major]
# Défaut: patch (3.0.0 -> 3.0.1)

param([string]$Bump = "patch")

$ErrorActionPreference = "Stop"
$root = if ($PSScriptRoot) { Split-Path -Parent $PSScriptRoot } else { (Get-Location).Path }
Set-Location $root

# Vérifier état git
$status = git status --porcelain
if ($status) {
    Write-Host "[ERROR] Working tree non propre. Commit ou stash les changements." -ForegroundColor Red
    exit 1
}

# Lire version actuelle
$py = Get-Content "pyproject.toml" -Raw
if ($py -match 'version\s*=\s*"([^"]+)"') {
    $current = $Matches[1]
} else {
    Write-Host "[ERROR] Version introuvable dans pyproject.toml" -ForegroundColor Red
    exit 1
}

# Bump
$parts = $current -split '\.'
$major = [int]$parts[0]
$minor = [int]$parts[1]
$patch = [int]$parts[2]

switch ($Bump.ToLower()) {
    "major" { $major++; $minor = 0; $patch = 0 }
    "minor" { $minor++; $patch = 0 }
    "patch" { $patch++ }
    default {
        Write-Host "[ERROR] Bump invalide. Utiliser: patch, minor, major" -ForegroundColor Red
        exit 1
    }
}

$newVersion = "$major.$minor.$patch"
Write-Host "`n=== RELEASE $newVersion ===" -ForegroundColor Cyan
Write-Host "  Actuel: $current"
Write-Host "  Nouveau: $newVersion"
Write-Host ""

# Mettre à jour pyproject.toml (racine)
(Get-Content "pyproject.toml") -replace "version = `"$current`"", "version = `"$newVersion`"" | Set-Content "pyproject.toml"

# Mettre à jour apps/api/pyproject.toml
if (Test-Path "apps\api\pyproject.toml") {
    (Get-Content "apps\api\pyproject.toml") -replace "version = `"$current`"", "version = `"$newVersion`"" | Set-Content "apps\api\pyproject.toml"
}

# Mettre à jour apps/pwa/package.json
$pkgPath = "apps\pwa\package.json"
if (Test-Path $pkgPath) {
    $pkg = Get-Content $pkgPath -Raw | ConvertFrom-Json
    $pkg.version = $newVersion
    $pkg | ConvertTo-Json -Depth 10 | Set-Content $pkgPath
}

Write-Host "[OK] Versions mises a jour" -ForegroundColor Green

# Tag git
$tag = "v$newVersion"
git add pyproject.toml apps/api/pyproject.toml apps/pwa/package.json
git commit -m "chore: release $tag"
git tag -a $tag -m "Release $tag"

Write-Host "[OK] Tag cree: $tag" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host "  1. Mettre a jour docs/changelog.md (section [Unreleased])"
Write-Host "  2. git push origin main"
Write-Host "  3. git push origin $tag"
Write-Host ""
