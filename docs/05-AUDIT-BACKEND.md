# Audit & Optimisations Backend — Docling Agent

Rapport basé sur une recherche des bonnes pratiques et nouveautés 2026 (FastAPI, Python asyncio, Gemini API, Neon).

**Voir aussi :**
- [09-TESTS.md](09-TESTS.md) pour l'audit de code complet (CORS, upload, auth)
- [12-EXPERT-REPORT.md](12-EXPERT-REPORT.md) pour les **risques critiques** : persistance des jobs (BackgroundTasks), circuit-breaker Gemini

---

## ✅ Implémenté

### 1. **asyncio.to_thread() — Vrai parallélisme (CRITIQUE)**

**Problème** : Le SDK `google-generativeai` utilise `generate_content()` **synchrone**. Chaque appel bloque l'event loop asyncio pendant 10–60 secondes. Avec 3 jobs "concurrents", ils s'exécutaient en fait **séquentiellement**.

**Solution** : Exécuter les appels bloquants dans un thread pool via `asyncio.to_thread()` :
- **Gemini** : `extract_from_bytes()` → thread pool
- **ImagePreprocessor** (OpenCV) : `preprocess_bytes()` → thread pool  
- **StorageService** (boto3) : `upload_file()` → thread pool

**Impact** : Les 3 extractions peuvent maintenant tourner en **vrai parallèle** (3 threads). Gain estimé : **~3× plus rapide** sur un batch de 10+ fichiers.

### 2. **Cache GeminiService** (déjà fait)
Une instance par `model_id` au lieu de réinitialiser à chaque fichier.

### 3. **Sémaphore d'extraction** (déjà fait)
Max 3 extractions Gemini concurrentes pour éviter le rate limit 429.

### 4. **Documentation Neon pooler**
Commentaires ajoutés : utiliser l'URL avec `-pooler` pour PgBouncer (jusqu'à 10k connexions).

---

## 🔮 Pistes futures (non implémentées)

### Gemini Batch API (Google 2025–2026)
- **Coût** : ~50 % moins cher que l’API standard
- **Usage** : Import massif, watchdog, traitements non urgents
- **Contrainte** : Délai de traitement ~24 h
- **Idée** : Mode "batch" optionnel pour le watchdog (fichiers déposés → traitement différé à moindre coût)

### Migration vers `google-genai` (nouveau SDK)
- Le SDK `google-genai` propose `client.aio.models.generate_content()` en **async natif**
- Éviterait `asyncio.to_thread()` et simplifierait le code
- Nécessite une migration et des tests

### aiometer pour rate limiting
- Bibliothèque pour limiter le débit des appels API
- Le sémaphore actuel suffit pour l’instant

### Uvicorn workers multiples
- `uvicorn api:app --workers 2` pour paralléliser les requêtes HTTP légères
- Le partage de `_jobs` en mémoire compliquerait l’architecture
- Pas prioritaire pour un usage actuel

---

## Références

- [FastAPI async best practices](https://fastapi.tiangolo.com/fr/async/)
- [Python asyncio 2026 — Mastering Async Patterns](https://dev.to/shehzan/mastering-python-async-patterns-a-complete-guide-to-asyncio-in-2026-10o6)
- [Gemini Batch API](https://ai.google.dev/gemini-api/docs/batch-mode)
- [Gemini Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Neon Connection Pooling](https://neon.tech/docs/connect/connection-pooling)
