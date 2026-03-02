# Déploiement — Docling

Séquence de déploiement staging et production.

---

## Prérequis

- Compte Neon avec le projet Docling Agent
- Compte Render (ou autre PaaS) pour le backend
- Compte Netlify pour la PWA
- Accès au repo GitHub

---

## 1. Créer la branche Neon staging

```bash
# Via le dashboard Neon → Branches → Create Branch
# Nom : staging
# Parent : main
# Cela crée une copie complète du schéma sans les données de prod
```

Récupérer la `DATABASE_URL` de la branche staging (avec `-pooler` pour PgBouncer).

---

## 2. Variables d'environnement staging

Copier `.env.staging` et renseigner les vrais secrets :

| Variable | Source |
|----------|--------|
| `DATABASE_URL` | Dashboard Neon → branche staging → Connection string |
| `GEMINI_API_KEY` | Console Google AI Studio |
| `JWT_SECRET` | `openssl rand -hex 32` (différent de la prod) |
| `STORJ_*` | Dashboard Storj → bucket `docling-factures-staging` |
| `SENTRY_DSN` | Projet Sentry dédié staging (optionnel) |

---

## 3. Séquence de déploiement

```
local → CI → staging → smoke test → prod
```

### Étape 1 : Local

```bash
make test
make lint
```

### Étape 2 : CI (automatique)

Push sur la branche → GitHub Actions exécute tests, lint backend et frontend.

### Étape 3 : Staging

```bash
git checkout staging
git merge main
git push origin staging
```

Le déploiement staging se déclenche automatiquement sur Render/Netlify.

### Étape 4 : Smoke test staging

Checklist manuelle :

- [ ] `GET /health` retourne `{"status": "ok", "db": "connected"}`
- [ ] Login/Register fonctionne
- [ ] Upload d'une facture PDF → extraction IA → résultat correct
- [ ] Catalogue affiche les produits extraits
- [ ] Export CSV/Excel fonctionne
- [ ] PWA installable (manifest + service worker)

### Étape 5 : Production

```bash
git checkout main
git merge staging
git push origin main
```

---

## 4. Rollback

- **Backend** : rollback Render au déploiement précédent (dashboard)
- **DB** : `make migrate-down`
- **Frontend** : rollback Netlify au build précédent (dashboard)

---

## 5. Branches Neon

| Branche | Usage | DATABASE_URL |
|---------|-------|--------------|
| `main` | Production | `ep-xxx-pooler.*.neon.tech/docling` |
| `staging` | Pré-prod | `ep-xxx-staging-pooler.*.neon.tech/docling_staging` |

---

## Bonnes pratiques

- Ne jamais copier les données de prod vers staging (RGPD)
- Utiliser des factures de test anonymisées en staging
- Les migrations Alembic doivent passer en staging avant la prod
- Garder les secrets staging différents de la prod
