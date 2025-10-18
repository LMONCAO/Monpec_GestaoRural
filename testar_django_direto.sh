#!/bin/bash

echo "🧪 TESTANDO DJANGO DIRETAMENTE"
echo "============================="

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se o Django consegue iniciar
echo "🔍 Testando se Django consegue iniciar..."
timeout 10 python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao &
DJANGO_PID=$!

# Aguardar um pouco
sleep 5

# Verificar se está rodando
echo "📊 Verificando se Django está rodando..."
ps aux | grep $DJANGO_PID | grep -v grep

# Testar localmente
echo "🌐 Testando localmente..."
curl -I http://localhost:8000 2>/dev/null || echo "Erro na conexão local"

# Parar o processo
kill $DJANGO_PID 2>/dev/null

echo "✅ TESTE CONCLUÍDO!"


