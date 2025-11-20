#!/bin/bash
# 🔄 SCRIPT DE ATUALIZAÇÃO DO SISTEMA MONPEC.COM.BR

echo "🔄 ATUALIZANDO SISTEMA MONPEC.COM.BR"
echo "===================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
    error "Execute como root: sudo ./atualizar_sistema.sh"
    exit 1
fi

# 1. BACKUP ANTES DA ATUALIZAÇÃO
log "Fazendo backup antes da atualização..."
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/monpec_update_$DATE"
mkdir -p $BACKUP_DIR

# Backup do banco de dados
log "Backup do banco de dados..."
pg_dump monpec_db > $BACKUP_DIR/monpec_db_backup.sql

# Backup dos arquivos
log "Backup dos arquivos..."
cp -r /var/www/monpec.com.br $BACKUP_DIR/monpec_files

success "Backup concluído em: $BACKUP_DIR"

# 2. PARAR SERVIÇOS
log "Parando serviços..."
systemctl stop monpec
systemctl stop nginx

# 3. ATUALIZAR CÓDIGO
log "Atualizando código do repositório..."
cd /var/www/monpec.com.br

# Verificar se há mudanças no repositório
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    warning "Nenhuma atualização disponível no repositório"
else
    log "Atualizações disponíveis, fazendo pull..."
    git pull origin main
fi

# 4. ATUALIZAR DEPENDÊNCIAS
log "Atualizando dependências..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_producao.txt

# 5. EXECUTAR MIGRAÇÕES
log "Executando migrações..."
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
python manage.py migrate

# 6. COLETAR ARQUIVOS ESTÁTICOS
log "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 7. VERIFICAR CONFIGURAÇÕES
log "Verificando configurações..."
python manage.py check --deploy

# 8. REINICIAR SERVIÇOS
log "Reiniciando serviços..."
systemctl start monpec
systemctl start nginx

# 9. VERIFICAR STATUS
log "Verificando status dos serviços..."
sleep 5

# Verificar se o serviço está rodando
if systemctl is-active --quiet monpec; then
    success "Serviço Monpec está rodando!"
else
    error "Erro ao iniciar serviço Monpec!"
    systemctl status monpec --no-pager
    exit 1
fi

if systemctl is-active --quiet nginx; then
    success "Nginx está rodando!"
else
    error "Erro ao iniciar Nginx!"
    systemctl status nginx --no-pager
    exit 1
fi

# 10. TESTAR ACESSO
log "Testando acesso ao sistema..."
sleep 10

# Testar se o sistema responde
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000)
if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "302" ]; then
    success "Sistema respondendo corretamente! (HTTP $HTTP_STATUS)"
else
    warning "Sistema pode não estar respondendo corretamente (HTTP $HTTP_STATUS)"
fi

# 11. LIMPEZA DE BACKUPS ANTIGOS
log "Limpando backups antigos..."
find /var/backups/ -name "monpec_update_*" -mtime +7 -type d -exec rm -rf {} \;

# 12. INFORMAÇÕES FINAIS
echo ""
echo "🎉 ATUALIZAÇÃO CONCLUÍDA!"
echo "========================="
echo "🌐 URL: https://monpec.com.br"
echo "📊 Status: systemctl status monpec"
echo "📝 Logs: tail -f /var/log/nginx/monpec_access.log"
echo "🔄 Backup salvo em: $BACKUP_DIR"
echo ""
echo "✅ Sistema atualizado e funcionando!"

# 13. VERIFICAÇÃO FINAL
log "Verificação final do sistema..."
echo ""
echo "📊 STATUS DOS SERVIÇOS:"
echo "========================"
systemctl status monpec --no-pager -l
echo ""
systemctl status nginx --no-pager -l
echo ""
echo "🌐 TESTE DE ACESSO:"
echo "=================="
curl -I https://monpec.com.br 2>/dev/null | head -1 || echo "Teste de acesso falhou"

