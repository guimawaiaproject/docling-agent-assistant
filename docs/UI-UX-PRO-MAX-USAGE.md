# UI/UX Pro Max — Guide Docling

[UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) est intégré à Cursor pour fournir une **intelligence design** lors de la création d'interfaces (landing, dashboard, PWA, etc.).

## Installation

Déjà installé via :

```bash
npx uipro-cli init --ai cursor
```

Emplacement : `.cursor/skills/ui-ux-pro-max/`

## Quand l'utiliser

| Contexte | Action |
|----------|--------|
| Créer une nouvelle page | Générer un design system avec `--design-system` |
| Refonte visuelle | Consulter styles, couleurs, typographie |
| Dashboard / analytics | Rechercher `--domain chart` |
| Accessibilité | Rechercher `--domain ux` |
| Stack React + Tailwind | Utiliser `--stack react` ou `html-tailwind` |

## Commandes Docling

### Générer un design system

```bash
# Design system pour Docling (catalogue BTP, factures)
python .cursor/skills/ui-ux-pro-max/scripts/search.py "SaaS BTP catalogue factures" --design-system -p "Docling" -f markdown

# Persister pour réutilisation (crée design-system/docling/MASTER.md)
python .cursor/skills/ui-ux-pro-max/scripts/search.py "SaaS BTP catalogue" --design-system --persist -p "Docling"
```

### Recherches ciblées

```bash
# Styles (glassmorphism, dark mode, bento...)
python .cursor/skills/ui-ux-pro-max/scripts/search.py "dark mode dashboard" --domain style

# Typographie
python .cursor/skills/ui-ux-pro-max/scripts/search.py "modern professional" --domain typography

# UX et accessibilité
python .cursor/skills/ui-ux-pro-max/scripts/search.py "animation accessibility" --domain ux

# Stack React + Tailwind (Docling PWA)
python .cursor/skills/ui-ux-pro-max/scripts/search.py "form layout responsive" --stack react
```

## Make

```bash
make design-system   # Génère design-system/docling/MASTER.md pour Docling
```

## Flux recommandé

1. **Avant de coder** : `make design-system` ou lancer le script avec `--design-system --persist`
2. **Lire** `design-system/docling/MASTER.md` pour les règles (couleurs, typo, effets)
3. **Implémenter** en respectant le Pre-Delivery Checklist du skill

## Ressources

- [Repo GitHub](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- [Site officiel](https://uupm.cc)
- Skill Cursor : `.cursor/skills/ui-ux-pro-max/SKILL.md`
