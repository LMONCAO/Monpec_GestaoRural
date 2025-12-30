#!/bin/bash
# Script para corrigir TODOS os arquivos que importam openpyxl no topo

echo "=========================================="
echo "🔧 CORRIGINDO TODOS OS IMPORTS DE OPENPYXL"
echo "=========================================="
echo ""

# Lista de arquivos que podem ter imports de openpyxl
FILES=(
    "gestao_rural/views_relatorios_rastreabilidade.py"
    "gestao_rural/views_relatorios.py"
    "gestao_rural/exportar_excel_financeiro.py"
    "gestao_rural/exportar_dre_multi_anos_excel.py"
    "gestao_rural/views_financeiro_avancado.py"
    "gestao_rural/views_exportacao.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "Verificando $file..."
        if head -30 "$file" | grep -qE "^from openpyxl|^import openpyxl"; then
            echo "  ❌ Encontrado import de openpyxl no topo"
            echo "  Corrigindo..."
            # Criar backup
            cp "$file" "${file}.bak"
            # Remover imports do topo
            sed -i '/^from openpyxl/d' "$file"
            sed -i '/^import openpyxl/d' "$file"
            echo "  ✅ Corrigido"
        else
            echo "  ✅ OK (sem imports no topo)"
        fi
    else
        echo "  ⚠️ Arquivo não encontrado: $file"
    fi
done

echo ""
echo "✅ Correção concluída!"
echo ""
echo "⚠️ IMPORTANTE: As funções que usam openpyxl precisam ter lazy imports adicionados manualmente"
echo "   ou você precisa fazer commit/push dos arquivos corrigidos localmente."





