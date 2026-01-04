#!/bin/bash
# Script bash para carregar dados do banco de dados
# Uso: ./scripts/carregar_dados_banco.sh sqlite backup/db_backup.sqlite3 1

set -e

# Verificar argumentos
if [ $# -lt 2 ]; then
    echo "Uso: $0 <fonte> <caminho> [usuario_id] [opcoes_adicionais]"
    echo ""
    echo "Fontes disponíveis:"
    echo "  sqlite      - Importar de arquivo SQLite"
    echo "  postgresql  - Importar de PostgreSQL"
    echo "  json        - Importar de arquivo JSON"
    echo "  csv         - Importar de arquivo CSV"
    echo "  sincronizar - Sincronizar dados existentes"
    echo ""
    echo "Exemplos:"
    echo "  $0 sqlite backup/db_backup.sqlite3 1"
    echo "  $0 json dados.json 1 --sobrescrever"
    echo "  $0 sincronizar '' 1"
    exit 1
fi

FONTE=$1
CAMINHO=$2
USUARIO_ID=${3:-1}
shift 3
OPCOES_ADICIONAIS="$@"

# Ativar ambiente virtual se existir
if [ -f "venv/bin/activate" ]; then
    echo "🔧 Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Construir comando
COMANDO="python manage.py carregar_dados_banco --fonte $FONTE"

if [ -n "$CAMINHO" ] && [ "$FONTE" != "sincronizar" ]; then
    COMANDO="$COMANDO --caminho \"$CAMINHO\""
fi

if [ -n "$USUARIO_ID" ]; then
    COMANDO="$COMANDO --usuario-id $USUARIO_ID"
fi

if [ -n "$OPCOES_ADICIONAIS" ]; then
    COMANDO="$COMANDO $OPCOES_ADICIONAIS"
fi

echo "🚀 Executando: $COMANDO"
echo ""

# Executar comando
eval $COMANDO

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Processo concluído com sucesso!"
else
    echo ""
    echo "❌ Erro durante a execução!"
    exit 1
fi


