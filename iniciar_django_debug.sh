#!/bin/bash

echo "🐛 INICIANDO DJANGO EM MODO DEBUG"
echo "================================="

# Parar tudo
pkill -f python
sleep 2

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se o ambiente está correto
echo "🔍 Verificando ambiente:"
which python
python --version

# Verificar configuração
echo "🔍 Verificando configuração Django:"
python manage.py check --settings=sistema_rural.settings_producao

# Verificar se consegue importar o módulo
echo "🔍 Testando importação:"
python -c "import sistema_rural.settings_producao; print('Configuração OK')"

# Iniciar Django com debug
echo "🚀 Iniciando Django com debug..."
python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao --verbosity=2


