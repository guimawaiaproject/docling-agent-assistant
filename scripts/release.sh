#!/usr/bin/env bash
# Release — Docling (bump version, tag git)
# Usage: ./scripts/release.sh [patch|minor|major]
# Défaut: patch (3.0.0 -> 3.0.1)

set -euo pipefail
IFS=$'\n\t'

cd "$(dirname "$0")/.."

bump="${1:-patch}"

# Vérifier état git
if [[ -n $(git status --porcelain) ]]; then
  echo "[ERROR] Working tree non propre. Commit ou stash les changements."
  exit 1
fi

# Lire version actuelle
current=$(grep -E '^version\s*=' pyproject.toml | head -1 | sed -E 's/.*"([^"]+)".*/\1/')
if [[ -z "$current" ]]; then
  echo "[ERROR] Version introuvable dans pyproject.toml"
  exit 1
fi

# Bump (simple)
IFS='.' read -r major minor patch <<< "$current"
case "$bump" in
  major) major=$((major + 1)); minor=0; patch=0 ;;
  minor) minor=$((minor + 1)); patch=0 ;;
  patch) patch=$((patch + 1)) ;;
  *)
    echo "[ERROR] Bump invalide. Utiliser: patch, minor, major"
    exit 1
    ;;
esac

new_version="$major.$minor.$patch"
echo ""
echo "=== RELEASE $new_version ==="
echo "  Actuel: $current"
echo "  Nouveau: $new_version"
echo ""

# Mettre à jour pyproject.toml (racine) — portable sed
sed "s/version = \"$current\"/version = \"$new_version\"/" pyproject.toml > pyproject.toml.tmp && mv pyproject.toml.tmp pyproject.toml

# apps/api/pyproject.toml
if [[ -f apps/api/pyproject.toml ]]; then
  sed "s/version = \"$current\"/version = \"$new_version\"/" apps/api/pyproject.toml > apps/api/pyproject.toml.tmp && mv apps/api/pyproject.toml.tmp apps/api/pyproject.toml
fi

# apps/pwa/package.json (avec jq si dispo, sinon sed)
if [[ -f apps/pwa/package.json ]]; then
  if command -v jq &>/dev/null; then
    jq --arg v "$new_version" '.version = $v' apps/pwa/package.json > apps/pwa/package.json.tmp
    mv apps/pwa/package.json.tmp apps/pwa/package.json
  else
    sed "s/\"version\": \"[^\"]*\"/\"version\": \"$new_version\"/" apps/pwa/package.json > apps/pwa/package.json.tmp && mv apps/pwa/package.json.tmp apps/pwa/package.json
  fi
fi

echo "[OK] Versions mises à jour"

# Tag git
tag="v$new_version"
git add pyproject.toml apps/api/pyproject.toml apps/pwa/package.json
git commit -m "chore: release $tag"
git tag -a "$tag" -m "Release $tag"

echo "[OK] Tag créé: $tag"
echo ""
echo "Prochaines étapes:"
echo "  1. Mettre à jour docs/changelog.md (section [Unreleased])"
echo "  2. git push origin main"
echo "  3. git push origin $tag"
echo ""
