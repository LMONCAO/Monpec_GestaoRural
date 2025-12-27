#!/bin/bash
# Script rápido para deploy no servidor de produção
# Execute: bash DEPLOY_RAPIDO.sh

set -e

echo "=========================================="
echo "🚀 DEPLOY RÁPIDO - MONPEC.COM.BR"
echo "=========================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Erro: manage.py não encontrado!${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Coletando arquivos estáticos...${NC}"
python manage.py collectstatic --noinput

echo -e "${YELLOW}👤 Criando/corrigindo usuário admin...${NC}"
python criar_admin_fix.py

echo -e "${YELLOW}🗄️  Aplicando migrações...${NC}"
python manage.py migrate --noinput

echo -e "${YELLOW}🔐 Ajustando permissões...${NC}"
if [ -d "/var/www/monpec.com.br/static" ]; then
    sudo chown -R www-data:www-data /var/www/monpec.com.br/static 2>/dev/null || true
    sudo chmod -R 755 /var/www/monpec.com.br/static 2>/dev/null || true
fi

echo -e "${YELLOW}🔄 Reiniciando servidor...${NC}"
if systemctl is-active --quiet gunicorn; then
    sudo systemctl restart gunicorn
    echo -e "${GREEN}✅ Gunicorn reiniciado${NC}"
elif systemctl is-active --quiet monpec; then
    sudo systemctl restart monpec
    echo -e "${GREEN}✅ Serviço monpec reiniciado${NC}"
else
    echo -e "${YELLOW}⚠️  Serviço não encontrado. Reinicie manualmente.${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "✅ DEPLOY CONCLUÍDO!"
echo "==========================================${NC}"
echo ""
echo "Teste o site em: https://monpec.com.br"
echo ""
