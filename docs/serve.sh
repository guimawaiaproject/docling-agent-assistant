#!/bin/bash
# Lance MkDocs depuis la racine du projet (MkDocs installé dans apps/api)
cd "$(dirname "$0")/../apps/api" && uv run mkdocs serve -f ../../mkdocs.yml
