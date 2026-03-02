# Échantillons PDF de test

Ce dossier contient les PDF de factures pour les tests (extraction, validation, pipeline IA).

## Convention

- `data/samples/*.pdf` est ignoré par défaut (voir `.gitignore`)
- Pour versionner 1–2 échantillons légers, ajouter une exception dans `.gitignore` :
  ```gitignore
  !data/samples/sample-light.pdf
  ```
- Les dossiers `PDF Test/` et `Docling_Factures/` à la racine restent exclus (données volumineuses)
