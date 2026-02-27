# Fix Build PostCSS/Tailwind — Docling Agent v3

## Diagnostic

| Élément | État |
|---------|------|
| Version Tailwind cible | v3.4.17 (PostCSS natif) |
| @tailwindcss/postcss | Non utilisé (v4) |
| postcss.config.cjs | `tailwindcss` seul |
| index.css | `@tailwind base/components/utilities` |
| tailwind.config.js | Format v3 (content, theme) |

## Problème connu

- **Erreur** : `Cannot find module 'autoprefixer'` ou `tailwindcss PostCSS plugin has moved`
- **Cause** : Chemin avec espace (`docling-agent-assistant 1`) + résolution npm sur Windows
- **Solution** : Déplacer le projet dans un chemin sans espace OU exécuter depuis la racine du repo

## Fix manuel (recommandé)

```bash
# 1. Dans un terminal, aller dans docling-pwa
cd docling-pwa

# 2. Nettoyer et réinstaller
rm -rf node_modules package-lock.json   # Linux/Mac
# OU sur Windows PowerShell :
Remove-Item -Recurse -Force node_modules; Remove-Item package-lock.json

npm install

# 3. Vérifier que tailwindcss v3 est installé
npm ls tailwindcss
# Doit afficher tailwindcss@3.4.17

# 4. Build
VITE_API_URL=https://api.example.com VITE_AUTH_REQUIRED=true npm run build
```

## Configuration finale

**package.json** (devDependencies) :
```json
"autoprefixer": "^10.4.27",
"postcss": "^8.5.6",
"tailwindcss": "3.4.17",
```

**postcss.config.cjs** :
```javascript
module.exports = {
  plugins: [
    require('tailwindcss'),
    require('autoprefixer'),
  ],
}
```

**src/index.css** :
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

**tailwind.config.js** : Format v3 avec `content`, `theme`, `plugins`.

## Alternative : Tailwind v4 + @tailwindcss/vite

Si vous préférez Tailwind v4 :

1. `npm install tailwindcss@4 @tailwindcss/vite@4`
2. Supprimer `postcss.config.cjs`
3. Dans `vite.config.js` : `import tailwindcss from '@tailwindcss/vite'` et ajouter `tailwindcss()` aux plugins
4. Dans `index.css` : `@import "tailwindcss";`

**Note** : Sur certains environnements Windows avec chemins contenant des espaces, `@tailwindcss/vite` peut ne pas se résoudre correctement.
