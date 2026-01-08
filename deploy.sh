#!/bin/bash
# Script completo de deploy para produção
# Uso: bash deploy.sh [producao|gcp]

set -e

echo "=========================================="
echo "🚀 DEPLOY COMPLETO - MONPEC"
echo "=========================================="
echo ""

# Determinar ambiente
ENVIRONMENT="${1:-producao}"
if [ "$ENVIRONMENT" = "gcp" ]; then
    SETTINGS_MODULE="sistema_rural.settings_gcp"
    echo "☁️ Ambiente: Google Cloud Platform"
else
    SETTINGS_MODULE="sistema_rural.settings_producao"
    echo "🖥️ Ambiente: Produção Locaweb"
fi

echo "📋 Settings: $SETTINGS_MODULE"
echo ""

# PASSO 1: BACKUP
echo "[1/6] Fazendo backup do banco de dados..."
BACKUP_DIR="backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_deploy_${TIMESTAMP}.sql"

DB_NAME="${DB_NAME:-sistema_rural}"
DB_USER="${DB_USER:-monpec}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

if [ -n "$DB_PASSWORD" ]; then
    PGPASSWORD="$DB_PASSWORD" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE" 2>/dev/null || echo "⚠️ Backup falhou, mas continuando..."
    if [ -f "$BACKUP_FILE" ] && [ -s "$BACKUP_FILE" ]; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo "✅ Backup criado: $BACKUP_FILE ($BACKUP_SIZE)"
        gzip -f "$BACKUP_FILE" 2>/dev/null || true
    fi
else
    echo "⚠️ DB_PASSWORD não definido. Execute: pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup.sql"
fi
echo ""

# PASSO 2: Verificar migrações
echo "[2/6] Verificando migrações pendentes..."
python manage.py showmigrations --settings="$SETTINGS_MODULE" | grep "\[ \]" | head -5 || echo "✅ Nenhuma migração pendente"
echo ""

# PASSO 3: Executar migrações
echo "[3/6] Executando migrações..."
python manage.py migrate --noinput --settings="$SETTINGS_MODULE" || {
    echo "❌ Erro nas migrações!"
    exit 1
}
echo "✅ Migrações executadas"
echo ""

# PASSO 4: Coletar arquivos estáticos
echo "[4/6] Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings="$SETTINGS_MODULE" || {
    echo "❌ Erro ao coletar arquivos estáticos!"
    exit 1
}
echo "✅ Arquivos estáticos coletados"
echo ""

# PASSO 5: Verificar sintaxe
echo "[5/6] Verificando sintaxe..."
python -m py_compile gestao_rural/views.py 2>/dev/null && echo "✅ Sintaxe OK" || echo "⚠️ Verifique erros"
echo ""

# PASSO 6: Resumo
echo "=========================================="
echo "✅ DEPLOY PREPARADO COM SUCESSO!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "  1. Reiniciar o servidor"
echo "  2. Verificar logs: tail -f /var/log/monpec/django.log"
echo "  3. Acessar o sistema e verificar"
echo ""







