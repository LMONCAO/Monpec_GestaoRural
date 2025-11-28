#!/bin/bash

echo "=========================================="
echo "EXPORTAR DADOS DO SISTEMA"
echo "=========================================="
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 não encontrado!"
    exit 1
fi

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Criar diretório de backup se não existir
mkdir -p backups

# Gerar nome do arquivo com data e hora
filename="backup_$(date +%Y%m%d_%H%M%S).json"

echo "[INFO] Exportando dados para: backups/$filename"
python manage.py dumpdata --indent 2 > "backups/$filename"

if [ $? -ne 0 ]; then
    echo "[ERRO] Falha ao exportar dados!"
    exit 1
fi

echo "[OK] Dados exportados com sucesso!"
echo "[INFO] Arquivo salvo em: backups/$filename"
echo ""

