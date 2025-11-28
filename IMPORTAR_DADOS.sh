#!/bin/bash

echo "=========================================="
echo "IMPORTAR DADOS PARA O SISTEMA"
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

# Verificar se diretório de backups existe
if [ ! -d "backups" ]; then
    echo "[ERRO] Diretório de backups não encontrado!"
    echo "Execute ./EXPORTAR_DADOS.sh primeiro."
    exit 1
fi

echo "[INFO] Arquivos de backup disponíveis:"
echo ""
ls -1 backups/*.json 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[ERRO] Nenhum arquivo de backup encontrado!"
    exit 1
fi
echo ""

read -p "Digite o nome do arquivo de backup (ex: backup_20250101_120000.json): " arquivo

if [ ! -f "backups/$arquivo" ]; then
    echo "[ERRO] Arquivo não encontrado: backups/$arquivo"
    exit 1
fi

echo ""
echo "[AVISO] Esta operação vai substituir os dados atuais do banco!"
read -p "Tem certeza que deseja continuar? (S/N): " confirmar

if [ "$confirmar" != "S" ] && [ "$confirmar" != "s" ]; then
    echo "[INFO] Operação cancelada."
    exit 0
fi

echo ""
echo "[INFO] Importando dados de: backups/$arquivo"
python manage.py loaddata "backups/$arquivo"

if [ $? -ne 0 ]; then
    echo "[ERRO] Falha ao importar dados!"
    exit 1
fi

echo "[OK] Dados importados com sucesso!"
echo ""

