#!/bin/bash
# Backup rápido antes de deploy
# Uso: ./scripts/emergencia/backup_antes_deploy.sh

set -e  # Parar em caso de erro

echo "🔄 Fazendo backup antes de deploy..."
echo ""

# Fazer backup completo comprimido
python manage.py backup_completo --compress --keep-days 7

echo ""
echo "📦 Verificando Git..."

# Verificar se há mudanças não commitadas
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️ Há mudanças não commitadas. Fazendo commit automático..."
    git add .
    git commit -m "Backup automático antes de deploy - $(date +%Y%m%d_%H%M%S)" || true
else
    echo "✅ Nenhuma mudança pendente no Git"
fi

echo ""
echo "🏷️ Criando tag de backup..."
TAG_NAME="backup-$(date +%Y%m%d_%H%M%S)"
git tag -a "$TAG_NAME" -m "Backup automático antes de deploy - $(date '+%Y-%m-%d %H:%M:%S')" || true

# Tentar fazer push (pode falhar se não houver conexão, mas não é crítico)
echo "📤 Tentando enviar tag para repositório remoto..."
git push origin --tags 2>/dev/null || echo "⚠️ Não foi possível enviar tag (pode estar offline)"

echo ""
echo "✅ Backup concluído!"
echo "📁 Localização: backups/"
echo "🏷️ Tag criada: $TAG_NAME"
echo ""
echo "💡 Para fazer rollback, use:"
echo "   git reset --hard $TAG_NAME"
echo "   ou"
echo "   ./scripts/emergencia/rollback_rapido.sh"








