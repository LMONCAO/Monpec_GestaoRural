#!/bin/bash
# Rollback rápido do sistema em caso de emergência
# Uso: ./scripts/emergencia/rollback_rapido.sh

set -e  # Parar em caso de erro

echo "⚠️ =========================================="
echo "⚠️ ROLLBACK DE EMERGÊNCIA"
echo "⚠️ =========================================="
echo ""

# Verificar se estamos em um repositório Git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Erro: Não estamos em um repositório Git!"
    exit 1
fi

# 1. Listar backups disponíveis
echo "📦 Backups disponíveis (últimos 5):"
if [ -d "backups" ]; then
    ls -lt backups/backup_completo_*.zip 2>/dev/null | head -5 || echo "   Nenhum backup ZIP encontrado"
    echo ""
    ls -ltd backups/backup_completo_* 2>/dev/null | head -5 || echo "   Nenhum backup de diretório encontrado"
else
    echo "   ⚠️ Diretório de backups não encontrado"
fi

echo ""
echo "🏷️ Tags Git de backup disponíveis (últimas 5):"
git fetch --tags 2>/dev/null || true
git tag -l "backup-*" | tail -5 || echo "   Nenhuma tag de backup encontrada"

echo ""
echo "📝 Commits recentes (últimos 5):"
git log --oneline -5

echo ""
echo "=========================================="
read -p "Digite a tag Git ou hash do commit para restaurar (ou 'cancelar' para sair): " TAG

if [ "$TAG" = "cancelar" ] || [ -z "$TAG" ]; then
    echo "❌ Rollback cancelado."
    exit 0
fi

# Verificar se tag/commit existe
if ! git rev-parse "$TAG" > /dev/null 2>&1; then
    echo "❌ Tag/commit '$TAG' não encontrado!"
    exit 1
fi

# Confirmar ação
echo ""
echo "⚠️ ATENÇÃO: Você está prestes a reverter o código para: $TAG"
echo "⚠️ Isso irá descartar todas as mudanças após este ponto!"
read -p "Tem certeza? Digite 'SIM' para confirmar: " CONFIRMACAO

if [ "$CONFIRMACAO" != "SIM" ]; then
    echo "❌ Rollback cancelado."
    exit 0
fi

# Fazer backup do estado atual antes de reverter
echo ""
echo "💾 Fazendo backup do estado atual antes de reverter..."
CURRENT_BRANCH=$(git branch --show-current)
BACKUP_BRANCH="backup-antes-rollback-$(date +%Y%m%d_%H%M%S)"
git branch "$BACKUP_BRANCH" 2>/dev/null || true
echo "✅ Estado atual salvo na branch: $BACKUP_BRANCH"

# Fazer rollback do código
echo ""
echo "🔄 Revertendo código para: $TAG"
git checkout -b "rollback-emergencia-$(date +%Y%m%d_%H%M%S)" "$TAG" 2>/dev/null || git reset --hard "$TAG"

echo ""
echo "✅ Código revertido para: $TAG"

# Perguntar se precisa restaurar banco
echo ""
read -p "Restaurar banco de dados também? (s/N): " RESTAURAR_DB

if [ "$RESTAURAR_DB" = "s" ] || [ "$RESTAURAR_DB" = "S" ]; then
    echo ""
    echo "📦 Procurando backups de banco de dados..."
    
    # Procurar backups de banco
    DB_BACKUPS=$(find backups -name "db_principal_*.sqlite3" -type f 2>/dev/null | sort -r | head -5)
    
    if [ -z "$DB_BACKUPS" ]; then
        echo "⚠️ Nenhum backup de banco encontrado automaticamente."
        read -p "Digite o caminho completo do backup do banco: " BACKUP_DB
    else
        echo "Backups encontrados:"
        echo "$DB_BACKUPS" | nl
        echo ""
        read -p "Digite o número do backup ou caminho completo: " BACKUP_CHOICE
        
        # Se digitou número, pegar da lista
        if [[ "$BACKUP_CHOICE" =~ ^[0-9]+$ ]]; then
            BACKUP_DB=$(echo "$DB_BACKUPS" | sed -n "${BACKUP_CHOICE}p")
        else
            BACKUP_DB="$BACKUP_CHOICE"
        fi
    fi
    
    if [ -f "$BACKUP_DB" ]; then
        echo ""
        echo "🔄 Restaurando banco de dados de: $BACKUP_DB"
        
        # Fazer backup do banco atual
        if [ -f "db.sqlite3" ]; then
            BACKUP_ANTES="db.sqlite3.backup-antes-rollback-$(date +%Y%m%d_%H%M%S)"
            cp db.sqlite3 "$BACKUP_ANTES"
            echo "✅ Backup do banco atual criado: $BACKUP_ANTES"
        fi
        
        # Restaurar banco
        cp "$BACKUP_DB" db.sqlite3
        echo "✅ Banco de dados restaurado!"
    else
        echo "❌ Arquivo de backup não encontrado: $BACKUP_DB"
    fi
fi

echo ""
echo "=========================================="
echo "✅ ROLLBACK CONCLUÍDO!"
echo "=========================================="
echo ""
echo "📋 Próximos passos:"
echo "1. Testar o sistema: python manage.py runserver"
echo "2. Se estiver OK, fazer deploy:"
echo "   - Cloud Run: gcloud run deploy monpec"
echo "   - Ou seguir processo de deploy normal"
echo ""
echo "⚠️ LEMBRE-SE:"
echo "   - O código foi revertido para: $TAG"
echo "   - Estado anterior salvo em: $BACKUP_BRANCH"
echo "   - Se precisar voltar: git checkout $BACKUP_BRANCH"
echo ""









