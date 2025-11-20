#!/bin/bash
# Script para aplicar navegação inteligente com cores

cd /var/www/monpec.com.br

echo "🎨 APLICANDO NAVEGAÇÃO INTELIGENTE COM CORES..."

# 1. Parar Django
echo "⏹️  Parando Django..."
pkill -9 python
sleep 2

# 2. Fazer backup dos templates atuais
echo "💾 Backup dos templates atuais..."
mkdir -p backup_templates_$(date +%Y%m%d_%H%M%S)
cp -r templates/ backup_templates_$(date +%Y%m%d_%H%M%S)/

# 3. Atualizar views.py para usar os novos templates
echo "🔧 Atualizando views para templates inteligentes..."

# Atualizar view do dashboard
sed -i "s/'gestao_rural\/dashboard.html'/'dashboard_navegacao_inteligente.html'/g" gestao_rural/views.py

# Atualizar view de propriedades
sed -i "s/'gestao_rural\/propriedades_lista.html'/'propriedades_navegacao_inteligente.html'/g" gestao_rural/views.py

# Atualizar view de módulos da propriedade  
sed -i "s/'gestao_rural\/propriedade_modulos.html'/'propriedade_modulos_coloridos.html'/g" gestao_rural/views.py

echo "✅ Views atualizadas!"

# 4. Verificar Django
echo "🔍 Verificando configuração..."
source venv/bin/activate
python manage.py check

if [ $? -eq 0 ]; then
    echo "✅ Configuração Django OK!"
else
    echo "❌ Erro na configuração Django!"
    exit 1
fi

# 5. Iniciar Django
echo "🚀 Iniciando Django com navegação inteligente..."
python manage.py runserver 127.0.0.1:8000 > /tmp/django_inteligente.log 2>&1 &
sleep 5

# 6. Testar se está rodando
if ps aux | grep -q "manage.py runserver"; then
    echo "✅ Django rodando!"
    
    # Testar resposta
    echo "🧪 Testando resposta..."
    response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/)
    
    if [ "$response" = "200" ]; then
        echo "🎉 NAVEGAÇÃO INTELIGENTE ATIVA!"
        echo ""
        echo "📱 RECURSOS IMPLEMENTADOS:"
        echo "   ✅ Menu lateral com 8 cores diferentes"
        echo "   ✅ Cards coloridos por módulo:"
        echo "      🟢 Pecuária (Verde)"
        echo "      🟡 Agricultura (Amarelo)" 
        echo "      🔵 Bens e Patrimônio (Azul)"
        echo "      🔴 Financeiro (Vermelho)"
        echo "      🟣 Projetos (Roxo)"
        echo "      🟠 Relatórios (Laranja)"
        echo "      🟢 Categorias (Verde-água)"
        echo "      ⚫ Configurações (Cinza)"
        echo ""
        echo "   ✅ Menu desabilitado fora da propriedade"
        echo "   ✅ Status da propriedade no canto superior"
        echo "   ✅ Breadcrumbs inteligentes"
        echo "   ✅ Animações suaves"
        echo "   ✅ Navegação hierárquica:"
        echo "      Dashboard → Produtor → Propriedades → MÓDULOS ATIVOS"
        echo ""
        echo "🌐 TESTE AGORA: http://191.252.225.106"
        echo ""
    else
        echo "⚠️  Django rodando mas resposta HTTP: $response"
    fi
else
    echo "❌ Erro ao iniciar Django!"
    echo "Log do erro:"
    tail -20 /tmp/django_inteligente.log
fi

echo ""
echo "📊 PROCESSOS DJANGO ATIVOS:"
ps aux | grep python | grep -v grep

echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "1. Acesse: http://191.252.225.106"
echo "2. Login: admin / 123456"
echo "3. Selecione um PRODUTOR"
echo "4. Clique em 'Ver Propriedades'" 
echo "5. Clique em 'ACESSAR MÓDULOS'"
echo "6. 🎨 MENU LATERAL COLORIDO ATIVADO!"
