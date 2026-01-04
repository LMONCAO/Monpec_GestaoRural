#!/bin/bash

# Script para resetar todos os dados do sistema
# Mantém apenas usuários admin e estruturas básicas

echo "========================================"
echo "  RESET COMPLETO DO SISTEMA"
echo "========================================"
echo ""
echo "Este script irá excluir:"
echo "  - Todas as fazendas (propriedades)"
echo "  - Todos os produtores rurais"
echo "  - Todos os animais e movimentações"
echo "  - Todas as vendas e compras"
echo "  - Todos os funcionários"
echo "  - Todos os dados financeiros"
echo "  - Todas as assinaturas e tenants"
echo ""
echo "Será mantido:"
echo "  - Usuários admin e superusers"
echo "  - Planos de assinatura (configurações)"
echo "  - Categorias padrão do sistema"
echo ""

read -p "Digite 'RESETAR' para confirmar (ou qualquer outra coisa para cancelar): " confirmacao

if [ "$confirmacao" != "RESETAR" ]; then
    echo "Operação cancelada."
    exit 0
fi

echo ""
echo "Executando reset do sistema..."
echo ""

# Executar o comando Django
python manage.py resetar_dados_sistema --confirmar

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "  RESET CONCLUÍDO COM SUCESSO!"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "  ERRO AO EXECUTAR RESET"
    echo "========================================"
    echo "Verifique os erros acima."
    exit 1
fi


