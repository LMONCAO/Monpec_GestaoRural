#!/bin/bash
# Script simples para fazer backup antes do deploy
# Uso: bash scripts/backup_antes_deploy_simples.sh

set -e

echo "=========================================="
echo "BACKUP ANTES DO DEPLOY"
echo "=========================================="
echo ""

# Configurações do banco (ajustar conforme necessário)
DB_NAME="${DB_NAME:-sistema_rural}"
DB_USER="${DB_USER:-monpec}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Criar diretório de backups se não existir
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"

# Nome do arquivo de backup com timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_antes_deploy_${TIMESTAMP}.sql"

echo "📦 Fazendo backup do banco de dados..."
echo "   Banco: $DB_NAME"
echo "   Usuário: $DB_USER"
echo "   Host: $DB_HOST:$DB_PORT"
echo ""

# Fazer backup
if [ -n "$DB_PASSWORD" ]; then
    # Se senha estiver em variável de ambiente
    PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"
else
    # Pedir senha interativamente
    pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"
fi

# Verificar se backup foi criado com sucesso
if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "✅ Backup criado com sucesso!"
    echo "   Arquivo: $BACKUP_FILE"
    echo "   Tamanho: $BACKUP_SIZE"
    echo ""
    
    # Comprimir backup (opcional)
    echo "🗜️ Comprimindo backup..."
    gzip -f "$BACKUP_FILE"
    COMPRESSED_FILE="${BACKUP_FILE}.gz"
    COMPRESSED_SIZE=$(du -h "$COMPRESSED_FILE" | cut -f1)
    echo "✅ Backup comprimido!"
    echo "   Arquivo: $COMPRESSED_FILE"
    echo "   Tamanho: $COMPRESSED_SIZE"
    echo ""
    
    echo "=========================================="
    echo "✅ BACKUP CONCLUÍDO COM SUCESSO!"
    echo "=========================================="
    echo ""
    echo "📁 Arquivo de backup: $COMPRESSED_FILE"
    echo ""
    echo "💡 Para restaurar este backup, use:"
    echo "   gunzip $COMPRESSED_FILE"
    echo "   psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME < ${BACKUP_FILE}"
    echo ""
else
    echo "❌ ERRO: Falha ao criar backup!"
    exit 1
fi







