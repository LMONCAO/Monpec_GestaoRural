#!/bin/bash
# Backup Completo do Sistema - MonPEC Gestão Rural
# Uso: ./BACKUP_COMPLETO.sh

set -e

echo "========================================================================"
echo "BACKUP COMPLETO DO SISTEMA - MonPEC Gestão Rural"
echo "========================================================================"
echo ""
echo "Este script faz backup completo do sistema:"
echo "  - Banco de dados principal"
echo "  - Bancos de dados dos tenants"
echo "  - Arquivos media (uploads, certificados, etc.)"
echo "  - Arquivos static (opcional)"
echo ""

# Obter diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/../.." && pwd )"

cd "$PROJECT_DIR"

echo "[1/2] Executando backup completo..."
python manage.py backup_completo --compress

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================================================"
    echo "BACKUP CONCLUÍDO COM SUCESSO!"
    echo "========================================================================"
    echo ""
    echo "Os backups foram salvos no diretório: backups/"
    echo ""
else
    echo ""
    echo "========================================================================"
    echo "ERRO AO EXECUTAR BACKUP!"
    echo "========================================================================"
    echo ""
    echo "Verifique os logs acima para mais detalhes."
    echo ""
    exit 1
fi






