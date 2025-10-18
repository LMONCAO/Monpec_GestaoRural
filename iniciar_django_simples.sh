#!/bin/bash

echo "🚀 INICIANDO DJANGO DE FORMA SIMPLES"
echo "===================================="

# Parar tudo
pkill -f python
sleep 2

# Ir para o diretório
cd /home/django/sistema-rural

# Ativar ambiente virtual
source venv/bin/activate

# Iniciar Django de forma simples
echo "🚀 Iniciando Django..."
python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao


