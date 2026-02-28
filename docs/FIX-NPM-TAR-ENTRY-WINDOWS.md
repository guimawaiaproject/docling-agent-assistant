# Fix npm TAR_ENTRY_ERROR ENOENT — Windows

## Erreur

```
npm warn tar TAR_ENTRY_ERROR ENOENT: no such file or directory, open '...\node_modules\lodash\fp\differenceBy.js'
```

## Signification

- **tar** : npm extrait les paquets au format tar
- **ENOENT** : fichier ou dossier introuvable lors de l'écriture
- **Cause** : chemins trop longs (limite Windows 260 caractères) ou cache/node_modules corrompu

## Solution recommandée (ordre obligatoire)

### 1. Activer les chemins longs (Windows)

```powershell
# À la racine du projet
git config core.longpaths true
```

### 2. Nettoyer et réinstaller

```powershell
cd docling-pwa

# Supprimer l'existant
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item package-lock.json -ErrorAction SilentlyContinue

# Vider le cache npm
npm cache clean --force

# Réinstaller
npm install
```

### 3. Build

```powershell
$env:VITE_API_URL = "http://localhost:8000"
$env:VITE_AUTH_REQUIRED = "true"
npm run build
```

## Script tout-en-un (PowerShell)

```powershell
# Depuis la racine du projet
Set-Location (Split-Path -Parent $PSScriptRoot)
git config core.longpaths true

Set-Location docling-pwa
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item package-lock.json -ErrorAction SilentlyContinue
npm cache clean --force
npm install

$env:VITE_API_URL = "http://localhost:8000"
$env:VITE_AUTH_REQUIRED = "true"
npm run build
```

## Erreur npm cache ENOTEMPTY

Si `npm cache clean --force` échoue avec `ENOTEMPTY` : fermer tous les terminaux/IDE qui utilisent npm, puis réessayer. Ou ignorer cette étape et faire directement `npm install` après suppression de node_modules.

## Alternative : pnpm (recommandé — évite TAR_ENTRY sur Windows)

pnpm évite les erreurs TAR_ENTRY. Avec `node-linker=hoisted`, structure compatible npm :

```powershell
npm install -g pnpm
cd docling-pwa
# Créer .npmrc avec : node-linker=hoisted
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
pnpm install
$env:VITE_API_URL = "http://localhost:8000"; $env:VITE_AUTH_REQUIRED = "true"
pnpm run build
```

**Ou exécuter** : `.\scripts\fix-npm-windows.ps1`

## Alternative : WSL (Linux)

Si npm échoue systématiquement sur Windows, utiliser WSL :

```bash
cd /mnt/c/Users/guima/Desktop/docling/docling-pwa
rm -rf node_modules package-lock.json
npm install
VITE_API_URL=http://localhost:8000 VITE_AUTH_REQUIRED=true npm run build
```

## Si ça persiste

- **Vérifier Node/npm** : `node -v` (20+), `npm -v` (10+)
- **Désactiver antivirus** temporairement sur le dossier projet (peut bloquer l'écriture)
- **Déplacer le projet** dans un chemin plus court (ex. `C:\dev\docling`)

## Erreur common-tags / vite-plugin-pwa

Si le build échoue avec `Cannot find module '...\common-tags\lib'` : le package est incomplet (TAR_ENTRY). Réinstaller :

```powershell
cd docling-pwa
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json -ErrorAction SilentlyContinue
npm install
```

## Voir aussi

- [docs/FIX-BUILD-TAILWIND.md](FIX-BUILD-TAILWIND.md) — erreur `Cannot find module 'autoprefixer'`
