#!/bin/bash
# Script para atualizar o site MONPEC em produção
# Execute: bash atualizar_producao.sh

set -e  # Parar em caso de erro

echo "=========================================="
echo "ATUALIZANDO SITE MONPEC EM PRODUÇÃO"
echo "=========================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se está no diretório correto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Erro: manage.py não encontrado!${NC}"
    echo "Execute este script no diretório raiz do projeto Django."
    exit 1
fi

# Ativar virtualenv se existir
if [ -d "venv" ]; then
    echo -e "${YELLOW}📦 Ativando virtualenv...${NC}"
    source venv/bin/activate
fi

# Coletar arquivos estáticos
echo -e "${YELLOW}📁 Coletando arquivos estáticos...${NC}"
python manage.py collectstatic --noinput

# Criar/corrigir usuário admin
echo -e "${YELLOW}👤 Criando/corrigindo usuário admin...${NC}"
python criar_admin_fix.py

# Aplicar migrações (se houver)
echo -e "${YELLOW}🗄️  Verificando migrações...${NC}"
python manage.py migrate --noinput

# Verificar se as imagens existem
echo -e "${YELLOW}🖼️  Verificando imagens...${NC}"
if [ -d "static/site" ]; then
    IMAGE_COUNT=$(ls -1 static/site/foto*.jpeg 2>/dev/null | wc -l)
    if [ $IMAGE_COUNT -gt 0 ]; then
        echo -e "${GREEN}✅ Encontradas $IMAGE_COUNT imagens${NC}"
    else
        echo -e "${RED}⚠️  Nenhuma imagem encontrada em static/site/${NC}"
    fi
else
    echo -e "${RED}⚠️  Diretório static/site não encontrado${NC}"
fi

# Verificar permissões dos arquivos estáticos
if [ -d "/var/www/monpec.com.br/static" ]; then
    echo -e "${YELLOW}🔐 Ajustando permissões...${NC}"
    sudo chown -R www-data:www-data /var/www/monpec.com.br/static 2>/dev/null || true
    sudo chmod -R 755 /var/www/monpec.com.br/static 2>/dev/null || true
fi

# Reiniciar servidor (descomente a linha apropriada)
echo -e "${YELLOW}🔄 Reiniciando servidor...${NC}"
echo "Escolha o método de reinicialização:"
echo "1) systemd (gunicorn)"
echo "2) supervisor"
echo "3) Pular reinicialização"
read -p "Opção (1-3): " option

case $option in
    1)
        sudo systemctl restart gunicorn || sudo systemctl restart monpec
        echo -e "${GREEN}✅ Servidor reiniciado via systemd${NC}"
        ;;
    2)
        sudo supervisorctl restart monpec
        echo -e "${GREEN}✅ Servidor reiniciado via supervisor${NC}"
        ;;
    3)
        echo -e "${YELLOW}⚠️  Reinicialização pulada - reinicie manualmente${NC}"
        ;;
    *)
        echo -e "${YELLOW}⚠️  Opção inválida - reinicie manualmente${NC}"
        ;;
esac

echo ""
echo -e "${GREEN}=========================================="
echo "✅ ATUALIZAÇÃO CONCLUÍDA!"
echo "==========================================${NC}"
echo ""
echo "Próximos passos:"
echo "1. Testar o site em https://monpec.com.br"
echo "2. Verificar menu mobile no celular"
echo "3. Verificar se as imagens aparecem"
echo "4. Testar formulário de demonstração"
echo "5. Testar login com admin (senha: L6171r12@@)"
echo ""










