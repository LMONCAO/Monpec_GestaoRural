#!/bin/bash

echo "=========================================="
echo "INICIANDO MONPEC GESTAO RURAL"
echo "=========================================="
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 não encontrado!"
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    echo "[INFO] Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "[AVISO] Arquivo .env não encontrado!"
    echo "Execute ./INSTALAR.sh primeiro para configurar o sistema."
    exit 1
fi

# Verificar se banco de dados existe
if [ ! -f "db.sqlite3" ]; then
    echo "[INFO] Banco de dados não encontrado. Executando migrações..."
    python manage.py migrate
fi

echo "[INFO] Iniciando servidor Django..."
echo "[INFO] Acesse: http://127.0.0.1:8000"
echo "[INFO] Pressione Ctrl+C para parar o servidor"
echo ""
python manage.py runserver

