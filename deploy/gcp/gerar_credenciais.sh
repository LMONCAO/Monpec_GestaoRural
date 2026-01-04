#!/bin/bash
# Script para gerar credenciais necessárias para GitHub Secrets

echo "========================================"
echo "  GERAR CREDENCIAIS PARA GITHUB SECRETS"
echo "========================================"
echo ""

echo "▶ Gerando SECRET_KEY..."
SECRET_KEY=$(openssl rand -base64 50 | tr -d '=+/' | cut -c1-50)
echo "SECRET_KEY: $SECRET_KEY"
echo ""

echo "▶ Gerando DJANGO_SUPERUSER_PASSWORD..."
DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 32 | tr -d '=+/' | cut -c1-20)
echo "DJANGO_SUPERUSER_PASSWORD: $DJANGO_SUPERUSER_PASSWORD"
echo ""

echo "========================================"
echo "📋 VALORES PARA GITHUB SECRETS:"
echo "========================================"
echo ""
echo "1. SECRET_KEY:"
echo "   $SECRET_KEY"
echo ""
echo "2. DJANGO_SUPERUSER_PASSWORD:"
echo "   $DJANGO_SUPERUSER_PASSWORD"
echo ""
echo "========================================"
echo "⚠️  IMPORTANTE: Copie esses valores agora!"
echo "   Eles não serão mostrados novamente."
echo "========================================"
echo ""


