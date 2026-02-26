# Docling Agent v3 — Catalogue BTP Intelligent

Application d'extraction automatisée de factures fournisseurs pour le secteur BTP.

**Documentation complète :** [docs/README.md](docs/README.md)

## Tests (zéro mock)

**Prérequis :** `pip install -r tests/requirements-test.txt`

### Tests unitaires (sans serveur)
```bash
pytest tests/01_unit -v --tb=short
```

### Tests API (serveur + DB requis)
1. Démarrer l'API : `python api.py`
2. Configurer `.env.test` (voir `.env.test.example`)
3. Lancer : `pytest tests/03_api -v --tb=short`

### Tests E2E Playwright (PWA sur 5173)
```bash
playwright install chromium
pytest tests/04_e2e -v -m e2e
```

### Tests complets (sans slow/external)
```bash
pytest tests/ -v -m "not slow and not external"
```
