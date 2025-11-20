#!/bin/bash

# === SCRIPT PARA EXECUTAR NO SERVIDOR (Console Web Locaweb) ===
# Copie este arquivo para o servidor e execute: bash corrigir_502_servidor.sh

echo "🔥 CORREÇÃO AUTOMÁTICA DO ERRO 502 - MONPEC"
echo "============================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📋 Iniciando correção do erro 502...${NC}"

# 1. Parar todos os processos Python
echo -e "${BLUE}1. Parando processos Python...${NC}"
pkill -9 python
sleep 2
echo -e "${GREEN}✅ Processos Python parados${NC}"

# 2. Navegar para diretório
echo -e "${BLUE}2. Navegando para diretório...${NC}"
cd /var/www/monpec.com.br
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Diretório encontrado: $(pwd)${NC}"
else
    echo -e "${RED}❌ Erro: Diretório não encontrado${NC}"
    exit 1
fi

# 3. Fazer backup do urls.py
echo -e "${BLUE}3. Fazendo backup do urls.py...${NC}"
TIMESTAMP=$(date +%H%M%S)
cp gestao_rural/urls.py gestao_rural/urls.py.backup.$TIMESTAMP
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backup criado: urls.py.backup.$TIMESTAMP${NC}"
else
    echo -e "${YELLOW}⚠️ Aviso: Não foi possível fazer backup${NC}"
fi

# 4. Recriar urls.py limpo
echo -e "${BLUE}4. Recriando urls.py limpo...${NC}"
cat > gestao_rural/urls.py << 'EOF'
from django.urls import path
from . import views

app_name = 'gestao_rural'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('propriedades/', views.propriedades_lista, name='propriedades_lista'),
    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),
    path('propriedade/<int:propriedade_id>/pecuaria/', views.pecuaria_dashboard, name='pecuaria_dashboard'),
    path('propriedade/<int:propriedade_id>/financeiro/', views.financeiro_dashboard, name='financeiro_dashboard'),
    path('categorias/', views.categorias_lista, name='categorias_lista'),
    path('logout/', views.logout_view, name='logout'),
]
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ urls.py recriado com sucesso${NC}"
else
    echo -e "${RED}❌ Erro ao recriar urls.py${NC}"
    exit 1
fi

# 5. Verificar sintaxe do Django
echo -e "${BLUE}5. Verificando sintaxe do Django...${NC}"
python manage.py check
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Sintaxe OK - Sem erros encontrados${NC}"
else
    echo -e "${RED}❌ Erro de sintaxe encontrado${NC}"
    echo -e "${YELLOW}Executando verificação detalhada...${NC}"
    python manage.py check --verbosity=2
    exit 1
fi

# 6. Ativar ambiente virtual e iniciar Django
echo -e "${BLUE}6. Ativando ambiente virtual...${NC}"
source venv/bin/activate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Ambiente virtual ativado${NC}"
else
    echo -e "${RED}❌ Erro ao ativar ambiente virtual${NC}"
    exit 1
fi

echo -e "${BLUE}7. Iniciando servidor Django...${NC}"
nohup python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &
DJANGO_PID=$!

# 8. Aguardar e verificar se está rodando
echo -e "${BLUE}8. Verificando se Django está rodando...${NC}"
sleep 5

# Verificar processo
ps aux | grep python | grep runserver | grep -v grep
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Django está rodando (PID: $DJANGO_PID)${NC}"
else
    echo -e "${RED}❌ Django não está rodando${NC}"
    echo -e "${YELLOW}Verificando logs...${NC}"
    tail -10 /tmp/django.log
    exit 1
fi

# 9. Testar resposta HTTP
echo -e "${BLUE}9. Testando resposta do servidor...${NC}"
curl -I http://127.0.0.1:8000/ 2>/dev/null | head -1
if [ $? -eq 0 ]; then
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/)
    if [ "$RESPONSE" = "200" ]; then
        echo -e "${GREEN}✅ Servidor respondendo (HTTP 200)${NC}"
    else
        echo -e "${YELLOW}⚠️ Servidor respondeu com código: $RESPONSE${NC}"
    fi
else
    echo -e "${RED}❌ Erro ao testar servidor${NC}"
fi

echo ""
echo -e "${GREEN}🎉 CORREÇÃO CONCLUÍDA!${NC}"
echo "============================================="
echo -e "${BLUE}🌐 Acesse o sistema em: http://191.252.225.106${NC}"
echo -e "${BLUE}🔑 Login: admin / 123456${NC}"
echo ""
echo -e "${YELLOW}📊 Status dos serviços:${NC}"
echo "- Django: $(ps aux | grep python | grep runserver | grep -v grep | wc -l) processo(s)"
echo "- Logs: tail -f /tmp/django.log"
echo ""

# 10. Mostrar informações úteis
echo -e "${YELLOW}🔧 Comandos úteis:${NC}"
echo "- Parar Django: pkill -9 python"
echo "- Ver logs: tail -f /tmp/django.log"
echo "- Reiniciar: bash $0"
echo "- Status: ps aux | grep python | grep runserver"

exit 0

