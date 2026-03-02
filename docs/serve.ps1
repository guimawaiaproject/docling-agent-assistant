# Lance MkDocs depuis la racine du projet (MkDocs installé dans apps/api)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $scriptDir "..\apps\api")
uv run mkdocs serve -f (Join-Path (Split-Path $scriptDir -Parent) "mkdocs.yml")
