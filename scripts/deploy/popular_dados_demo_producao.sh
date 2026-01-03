#!/bin/bash
# Script para popular dados demo após deploy no Google Cloud Run
# Este script executa via Cloud Run Jobs

set -e

echo "=========================================="
echo "POPULAR DADOS DEMO PARA PRODUÇÃO"
echo "=========================================="
echo ""

# Executar migrações primeiro (garantido pelo Dockerfile, mas executar novamente por segurança)
echo "📊 Executando migrações..."
python manage.py migrate --noinput || echo "⚠️ Aviso: Algumas migrações podem ter falhado"

# Criar usuário admin
echo ""
echo "👤 Garantindo usuário admin..."
python manage.py garantir_admin --senha ${DJANGO_SUPERUSER_PASSWORD:-L6171r12@@} || echo "⚠️ Aviso: Não foi possível garantir admin"

# Popular dados demo (usando comando existente)
echo ""
echo "📦 Popular dados demo para propriedades..."
python manage.py popular_monpec1_demo --force || echo "⚠️ Aviso: Não foi possível popular dados demo"

echo ""
echo "=========================================="
echo "✅ PROCESSO CONCLUÍDO!"
echo "=========================================="



