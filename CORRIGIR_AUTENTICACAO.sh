#!/bin/bash
# Script para corrigir erro de autenticação

echo "========================================"
echo "🔐 Corrigindo Autenticação"
echo "========================================"
echo ""

echo "1️⃣  Verificando autenticação atual..."
gcloud auth list

echo ""
echo "2️⃣  Reautenticando..."
gcloud auth login

echo ""
echo "3️⃣  Configurando credenciais de aplicação..."
gcloud auth application-default login

echo ""
echo "4️⃣  Verificando projeto..."
gcloud config get-value project

echo ""
echo "✅ Autenticação corrigida!"
echo ""
echo "Agora execute novamente:"
echo "  gcloud run jobs execute migrate-monpec --region us-central1 --wait"
echo ""


