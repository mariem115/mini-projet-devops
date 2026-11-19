#!/usr/bin/env bash
set -euo pipefail

errors=0
required=(
  app/app.py
  tests/test_app.py
  requirements.txt
  requirements-dev.txt
  .gitignore
  Dockerfile
  .dockerignore
  compose.yaml
  .env.example
)

echo "[CHECK] mini-projet DevOps"
for file in "${required[@]}"; do
  if [[ -f "$file" ]]; then
    echo "[OK] $file"
  else
    echo "[ERREUR] fichier absent: $file" >&2
    errors=$((errors + 1))
  fi
done

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git ls-files | grep -Eq '(^|/)\.env$'; then
    echo "[ERREUR] un fichier .env est suivi par Git" >&2
    errors=$((errors + 1))
  else
    echo "[OK] aucun .env suivi"
  fi
else
  echo "[ERREUR] le dossier n'est pas un depot Git" >&2
  errors=$((errors + 1))
fi

if [[ -f compose.yaml ]]; then
  docker compose config -q
  echo "[OK] compose.yaml"
fi

if [[ $errors -gt 0 ]]; then
  echo "[ECHEC] $errors erreur(s)" >&2
  exit 1
fi

PYTHON=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -m pytest --version >/dev/null 2>&1; then
    PYTHON=$candidate
    break
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo "[ERREUR] pytest introuvable: activez l'environnement du projet" >&2
  exit 1
fi

echo "[CHECK] pytest ($PYTHON)"
"$PYTHON" -m pytest
echo "[SUCCES] controles valides"
exit 0
