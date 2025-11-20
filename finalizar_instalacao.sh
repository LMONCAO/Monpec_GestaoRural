#!/bin/bash

echo "🚀 FINALIZANDO INSTALAÇÃO DO MONPEC"
echo "===================================="

# Ir para o diretório do projeto
cd /var/www/monpec.com.br

# Verificar se os arquivos foram transferidos
echo "📋 Verificando arquivos transferidos..."
ls -la

# Ativar ambiente virtual
echo "🐍 Ativando ambiente virtual..."
source venv/bin/activate

# Configurar Django
echo "⚙️ Configurando Django..."
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao

# Executar migrações
echo "🔄 Executando migrações..."
python manage.py makemigrations
python manage.py migrate

# Criar superusuário
echo "👤 Criando superusuário..."
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@monpec.com.br', '123456')" | python manage.py shell

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Testar Django
echo "🧪 Testando Django..."
python manage.py check

# Iniciar servidor
echo "🚀 Iniciando servidor Django..."
python manage.py runserver 0.0.0.0:8000 &

echo "✅ INSTALAÇÃO FINALIZADA!"
echo "🌐 Acesse: http://191.252.225.106:8000"
echo "👤 Login: admin / 123456"

