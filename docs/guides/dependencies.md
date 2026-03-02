# Mise à jour des dépendances

## Audit sécurité

```bash
make audit-deps       # pip-audit + pnpm audit
# ou: powershell -File scripts/audit-deps.ps1
```

## Python (uv)

En mode dev, installer toutes les deps (dont dev) :
```bash
cd apps/api && uv sync --all-extras
```

```bash
# apps/api — mettre à jour vers dernières versions compatibles
cd apps/api && uv lock --upgrade

# Racine — idem
uv lock --upgrade
```

## Node (pnpm)

```bash
# apps/pwa — mises à jour mineures/patch (sûres)
cd apps/pwa && pnpm update

# Vérifier les obsolètes
pnpm outdated
```

### Mises à jour majeures (à tester)

| Package | Version actuelle | Dernière | Risque |
|---------|------------------|----------|--------|
| Tailwind | 3.4.x | 4.x | Migration config v4 |
| Vite | 5.x | 7.x | Breaking changes |
| vitest | 3.x | 4.x | API changée |
| react-dropzone | 14.x | 15.x | API changée |

**Recommandation :** Garder les versions actuelles (stables). Pour les majeures, créer une branche dédiée et tester avant merge.
