# Intégration Bytez — Docling

> [Bytez](https://docs.bytez.com) : API unifiée pour 100 000+ modèles IA

## Configuration

1. **Clé API** : Ajoutez dans `.env` (jamais en dur dans le code) :
   ```
   BYTEZ_API_KEY=votre_cle_bytez
   ```

2. **Optionnel** : Pour les modèles Google via Bytez (fallback), `GEMINI_API_KEY` sert de `provider-key`.

## Intégrations réalisées

| Fonctionnalité | Fichier | Usage |
|----------------|---------|-------|
| **Fallback extraction** | `orchestrator.py` | Si Gemini échoue (rate limit, indispo) → Bytez document-QA / image-chat |
| **Service Bytez** | `bytez_service.py` | `document_qa_extract`, `image_chat_extract`, `extract_invoice_fallback` |

## Opportunités d'amélioration

### 1. Extraction factures (✅ partiel)
- **Fallback** : Bytez document-QA ou image-chat quand Gemini rate limit
- **Amélioration** : Modèle dédié document-QA multilingue (CA/ES/FR)

### 2. Feature Extraction — similarité catalogue
- **Task** : [feature-extraction](https://docs.bytez.com/model-api/docs/task/feature-extraction.md)
- **Usage** : Embeddings des désignations produits → recherche sémantique "ciment 42.5" ≈ "Ciment Portland 42.5R"
- **Impact** : Comparateur de prix plus intelligent, regroupement produits similaires

### 3. Sentence Similarity — matching fournisseurs
- **Task** : [sentence-similarity](https://docs.bytez.com/model-api/docs/task/sentence-similarity.md)
- **Usage** : Comparer `designation_fr` entre factures pour détecter doublons ou variantes
- **Impact** : Dédoublonnage catalogue, fusion produits

### 4. Translation — multilingue
- **Task** : [translation](https://docs.bytez.com/model-api/docs/task/translation.md)
- **Usage** : Traduction CA/ES → FR pour `designation_fr` si modèle extraction ne traduit pas
- **Impact** : Catalogue 100 % français

### 5. Text-to-Speech — accessibilité
- **Task** : [text-to-speech](https://docs.bytez.com/model-api/docs/task/text-to-speech.md)
- **Usage** : Lecture des lignes facture pour utilisateurs malvoyants
- **Impact** : PWA plus accessible

### 6. Summarization — synthèse facture
- **Task** : [summarization](https://docs.bytez.com/model-api/docs/task/summarization.md)
- **Usage** : Résumé automatique "Facture BigMat, 12 lignes, total 1 234 € HT"
- **Impact** : Historique plus lisible

### 7. Zero-shot classification — famille BTP
- **Task** : [zero-shot-classification](https://docs.bytez.com/model-api/docs/task/zero-shot-classification.md)
- **Usage** : Classifier `designation_fr` dans les familles BTP sans fine-tuning
- **Impact** : Meilleure catégorisation automatique

### 8. Chat multi-providers — coûts
- **Usage** : Tester OpenAI, Anthropic, Mistral via Bytez avec une seule clé
- **Impact** : Comparer coûts/qualité extraction, choisir le meilleur rapport

## Modèles recommandés

| Task | Modèle | Note |
|------|--------|------|
| Document QA | `cloudqi/CQI_Visual_Question_Awnser_PT_v0` | PT = Portugais, adapter prompt FR |
| Image-Chat | `google/gemma-3-4b-it` | Multimodal, nécessite provider-key Gemini |
| Feature Extraction | `sentence-transformers/all-MiniLM-L6-v2` | Embeddings légers |
| Translation | `Helsinki-NLP/opus-mt-es-fr` | ES→FR |

## Références

- [Documentation Bytez](https://docs.bytez.com/model-api/docs/welcome)
- [Index complet](https://docs.bytez.com/llms.txt)
- [Get started](https://docs.bytez.com/model-api/docs/get-started.md)
