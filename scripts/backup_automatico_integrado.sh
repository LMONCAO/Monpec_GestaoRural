#!/bin/bash
# Função de backup automático integrado
# Pode ser chamada de qualquer script de deploy

set -e

BACKUP_AUTOMATICO() {
    local TIPO="${1:-completo}"  # completo, rapido, apenas-db
    local COMPRIMIR="${2:-true}"  # true ou false
    
    echo ""
    echo "🔄 [BACKUP AUTOMÁTICO] Iniciando backup ($TIPO)..."
    echo ""
    
    # Verificar se estamos em um projeto Django
    if [ ! -f "manage.py" ]; then
        echo "⚠️  Erro: manage.py não encontrado. Não é um projeto Django?"
        return 1
    fi
    
    # Verificar se o comando existe
    if ! python manage.py backup_completo --help > /dev/null 2>&1; then
        echo "⚠️  Erro: Comando backup_completo não encontrado"
        return 1
    fi
    
    # Fazer backup conforme tipo
    case "$TIPO" in
        "rapido"|"apenas-db")
            echo "📦 Fazendo backup rápido (apenas banco de dados)..."
            python manage.py backup_completo --only-db --keep-days 7
            ;;
        "completo")
            if [ "$COMPRIMIR" = "true" ]; then
                echo "📦 Fazendo backup completo comprimido..."
                python manage.py backup_completo --compress --keep-days 7
            else
                echo "📦 Fazendo backup completo..."
                python manage.py backup_completo --keep-days 7
            fi
            ;;
        *)
            echo "⚠️  Tipo de backup desconhecido: $TIPO"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ [BACKUP AUTOMÁTICO] Backup concluído com sucesso!"
        
        # Criar tag Git se estiver em repositório Git
        if git rev-parse --git-dir > /dev/null 2>&1; then
            TAG_NAME="backup-$(date +%Y%m%d_%H%M%S)"
            git tag -a "$TAG_NAME" -m "Backup automático - $(date '+%Y-%m-%d %H:%M:%S')" 2>/dev/null || true
            echo "🏷️  Tag Git criada: $TAG_NAME"
        fi
        
        return 0
    else
        echo ""
        echo "❌ [BACKUP AUTOMÁTICO] Erro ao fazer backup!"
        return 1
    fi
}

# Se script for executado diretamente, fazer backup
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    BACKUP_AUTOMATICO "${1:-completo}" "${2:-true}"
fi






