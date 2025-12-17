#!/bin/bash
# ========================================
# MONPEC - EXPORTAR DADOS (Linux/Mac)
# ========================================

echo "========================================"
echo "  MONPEC - EXPORTAR DADOS"
echo "  Sistema de Gestão Rural"
echo "========================================"
echo

cd "$(dirname "$0")"

# ========================================
# VERIFICAR PYTHON
# ========================================
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

# ========================================
# CRIAR PASTA DE BACKUP
# ========================================
BACKUP_DIR="backups/export_$(date +%Y%m%d_%H%M%S)"

mkdir -p backups
mkdir -p "$BACKUP_DIR"

echo "[INFO] Exportando dados para: $BACKUP_DIR"
echo

# ========================================
# EXPORTAR BANCO DE DADOS
# ========================================
echo "[1/3] Exportando banco de dados..."
if [ -f "db.sqlite3" ]; then
    cp "db.sqlite3" "$BACKUP_DIR/db.sqlite3"
    echo "[OK] Banco de dados exportado"
else
    echo "[AVISO] Banco de dados não encontrado"
fi
echo

# ========================================
# EXPORTAR DADOS VIA DJANGO
# ========================================
echo "[2/3] Exportando dados do sistema..."
$PYTHON_CMD manage.py dumpdata --indent 2 --output "$BACKUP_DIR/dados_exportados.json" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[AVISO] Falha ao exportar dados JSON"
else
    echo "[OK] Dados exportados em JSON"
fi
echo

# ========================================
# CRIAR ARQUIVO DE INFORMAÇÕES
# ========================================
echo "[3/3] Criando arquivo de informações..."
cat > "$BACKUP_DIR/INFO_EXPORTACAO.txt" << EOF
Data da Exportação: $(date)
Sistema: MONPEC Gestão Rural

Arquivos exportados:
- db.sqlite3
- dados_exportados.json

Para importar, use ./IMPORTAR_DADOS.sh
EOF
echo "[OK] Arquivo de informações criado"
echo

echo "========================================"
echo "  EXPORTAÇÃO CONCLUÍDA!"
echo "========================================"
echo
echo "Dados exportados para: $BACKUP_DIR"
echo
echo "========================================"















