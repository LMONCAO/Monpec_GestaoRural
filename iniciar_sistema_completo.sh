#!/bin/bash

echo "🚀 INICIANDO SISTEMA RURAL COMPLETO"
echo "==================================="

# Obter o diretório onde o script está localizado
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

echo "📁 Diretório do projeto: $PROJECT_DIR"

# Parar processos existentes
echo "⏹️ Parando processos existentes..."
pkill -f "python.*manage.py"
pkill -f gunicorn
systemctl stop nginx 2>/dev/null

# Aguardar
sleep 3

# Ir para o diretório do projeto
cd "$PROJECT_DIR"

# Verificar se manage.py existe
if [ ! -f "manage.py" ]; then
    echo "❌ ERRO: manage.py não encontrado em $PROJECT_DIR"
    echo "   Certifique-se de executar o script na raiz do projeto Django"
    exit 1
fi

# Ativar ambiente virtual (se existir)
if [ -d "venv/bin" ]; then
    echo "🔌 Ativando ambiente virtual..."
    source venv/bin/activate
elif [ -d ".venv/bin" ]; then
    echo "🔌 Ativando ambiente virtual..."
    source .venv/bin/activate
else
    echo "⚠️  Ambiente virtual não encontrado. Usando Python do sistema."
fi

# Verificar configuração (detectar qual usar)
if [ -f "sistema_rural/settings_producao.py" ]; then
    SETTINGS="sistema_rural.settings_producao"
    echo "🔍 Usando configurações de produção"
else
    SETTINGS="sistema_rural.settings"
    echo "🔍 Usando configurações padrão"
fi

# Verificar configuração
echo "🔍 Verificando configuração Django..."
python manage.py check --settings=$SETTINGS

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings=$SETTINGS

# Iniciar Django em background
echo "🚀 Iniciando Django..."
nohup python manage.py runserver 0.0.0.0:8000 --settings=$SETTINGS > /tmp/django.log 2>&1 &

# Aguardar inicialização
echo "⏳ Aguardando inicialização..."
sleep 8

# Verificar se está rodando
echo "📊 Verificando processo Django..."
ps aux | grep "python.*manage.py" | grep -v grep

# Verificar porta
echo "🔍 Verificando porta 8000..."
netstat -tlnp | grep :8000

# Testar localmente
echo "🌐 Testando conectividade local..."
curl -I http://localhost:8000

echo ""
echo "✅ SISTEMA INICIADO!"
echo "==================="
echo "📁 Diretório: $PROJECT_DIR"
echo "⚙️  Settings: $SETTINGS"
echo "🌐 Acesse: http://localhost:8000"
echo "📝 Logs: tail -f /tmp/django.log"
echo ""
echo "💡 Para verificar o IP externo:"
echo "   hostname -I | awk '{print \$1}'"


