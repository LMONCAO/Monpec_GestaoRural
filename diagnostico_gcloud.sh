#!/bin/bash
# Script de diagnóstico para verificar configuração do gcloud

echo "=== DIAGNÓSTICO DO GCLOUD ==="
echo ""

echo "1. Verificando contas autenticadas:"
gcloud auth list
echo ""

echo "2. Verificando conta ativa:"
gcloud config get-value account
echo ""

echo "3. Verificando projeto configurado:"
gcloud config get-value project
echo ""

echo "4. Verificando configuração completa:"
gcloud config list
echo ""

echo "=== FIM DO DIAGNÓSTICO ==="

