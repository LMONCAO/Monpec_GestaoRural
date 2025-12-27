#!/bin/bash
# Script para verificar se openpyxl está no requirements.txt e será instalado

echo "========================================"
echo "  VERIFICAR INSTALAÇÃO DO OPENPYXL"
echo "========================================"
echo ""

echo "▶ Verificando se openpyxl está no requirements.txt..."
if grep -q "^openpyxl" requirements.txt; then
    echo "✓ openpyxl encontrado no requirements.txt:"
    grep "^openpyxl" requirements.txt
else
    echo "❌ openpyxl NÃO encontrado no requirements.txt!"
    echo "Adicionando openpyxl ao requirements.txt..."
    echo "openpyxl>=3.1.5" >> requirements.txt
    echo "✓ openpyxl adicionado"
fi
echo ""

echo "▶ Verificando se há problemas no requirements.txt..."
if [ -f requirements.txt ]; then
    echo "✓ Arquivo requirements.txt existe"
    echo "Total de linhas: $(wc -l < requirements.txt)"
    echo ""
    echo "Primeiras 10 linhas:"
    head -10 requirements.txt
else
    echo "❌ Arquivo requirements.txt NÃO encontrado!"
    exit 1
fi
echo ""

echo "▶ Para testar localmente se o openpyxl seria instalado:"
echo "   pip install -r requirements.txt | grep openpyxl"
echo ""




