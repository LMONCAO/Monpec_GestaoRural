#!/bin/bash
# Script para agendar backup automático diário
# Configura cron job para fazer backup automático todos os dias

echo "📅 Configurando backup automático diário..."
echo ""

# Verificar se estamos na raiz do projeto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Execute este script na raiz do projeto Django"
    exit 1
fi

# Obter caminho absoluto do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_SCRIPT="$PROJECT_ROOT/scripts/backup_automatico_integrado.sh"

# Tornar script executável
chmod +x "$BACKUP_SCRIPT"

# Criar entrada no crontab
CRON_JOB="0 2 * * * cd $PROJECT_ROOT && $BACKUP_SCRIPT completo true >> $PROJECT_ROOT/logs/backup_automatico.log 2>&1"

# Verificar se já existe
if crontab -l 2>/dev/null | grep -q "$BACKUP_SCRIPT"; then
    echo "⚠️  Backup automático já está agendado!"
    echo ""
    echo "Para remover, execute:"
    echo "  crontab -e"
    echo "  (remova a linha com backup_automatico_integrado.sh)"
    exit 0
fi

# Adicionar ao crontab
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ Backup automático configurado!"
echo ""
echo "📋 Detalhes:"
echo "   - Horário: Todos os dias às 02:00"
echo "   - Tipo: Backup completo comprimido"
echo "   - Retenção: 7 dias"
echo "   - Log: $PROJECT_ROOT/logs/backup_automatico.log"
echo ""
echo "Para verificar:"
echo "  crontab -l"
echo ""
echo "Para remover:"
echo "  crontab -e"
echo "  (remova a linha correspondente)"









