#!/bin/bash
# Script para configurar variáveis de ambiente no Cloud Run
# Execute após o deploy inicial

PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="monpec"
REGION="us-central1"

echo "========================================"
echo "Configurando variáveis de ambiente"
echo "========================================"
echo ""

# IMPORTANTE: Configure estas variáveis com seus valores reais
# Substitua os valores abaixo pelos seus dados de produção

read -p "MERCADOPAGO_ACCESS_TOKEN: " MP_ACCESS_TOKEN
read -p "MERCADOPAGO_PUBLIC_KEY: " MP_PUBLIC_KEY
read -sp "SECRET_KEY (não será exibido): " SECRET_KEY
echo ""
read -p "DB_NAME: " DB_NAME
read -p "DB_USER: " DB_USER
read -sp "DB_PASSWORD (não será exibido): " DB_PASSWORD
echo ""
read -p "DB_HOST: " DB_HOST

echo ""
echo "Atualizando variáveis de ambiente..."

gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --update-env-vars "MERCADOPAGO_ACCESS_TOKEN=$MP_ACCESS_TOKEN,MERCADOPAGO_PUBLIC_KEY=$MP_PUBLIC_KEY,SECRET_KEY=$SECRET_KEY,DB_NAME=$DB_NAME,DB_USER=$DB_USER,DB_PASSWORD=$DB_PASSWORD,DB_HOST=$DB_HOST"

echo ""
echo "Variáveis de ambiente configuradas com sucesso!"
echo ""





















