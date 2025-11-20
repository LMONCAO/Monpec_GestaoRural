#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="python"
USUARIO="admin"
ANO="$(date +%Y)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    --usuario)
      USUARIO="$2"
      shift 2
      ;;
    --ano)
      ANO="$2"
      shift 2
      ;;
    *)
      echo "Parâmetro desconhecido: $1" >&2
      exit 1
      ;;
  esac
done

echo "==> Aplicando migrações (manage.py migrate)"
$PYTHON_BIN manage.py migrate

echo "==> Executando seed do planejamento (usuario=$USUARIO ano=$ANO)"
$PYTHON_BIN manage.py seed_planejamento --usuario "$USUARIO" --ano "$ANO"

echo ""
echo "Rotina finalizada. Inicie o servidor com 'python manage.py runserver' e acesse o painel."










