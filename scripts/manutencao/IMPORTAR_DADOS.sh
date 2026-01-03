#!/bin/bash
# ========================================
# MONPEC - IMPORTAR DADOS (Linux/Mac)
# ========================================

echo "========================================"
echo "  MONPEC - IMPORTAR DADOS"
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
# LISTAR BACKUPS DISPONÍVEIS
# ========================================
echo "[INFO] Procurando backups disponíveis..."
echo

if [ ! -d "backups" ]; then
    echo "[ERRO] Pasta de backups não encontrada!"
    exit 1
fi

echo "Backups disponíveis:"
echo
ls -d backups/export_* 2>/dev/null | sed 's|backups/||'
if [ $? -ne 0 ]; then
    echo "[AVISO] Nenhum backup encontrado na pasta backups"
    echo
    echo "Você pode:"
    echo "1. Copiar um arquivo db.sqlite3 para a raiz do projeto"
    echo "2. Ou usar um arquivo JSON de dados"
    echo
    exit 1
fi

echo
read -p "Digite o nome do backup (ou pressione Enter para usar db.sqlite3 da raiz): " BACKUP_SELECIONADO

# ========================================
# IMPORTAR BANCO DE DADOS
# ========================================
echo
echo "[1/2] Importando banco de dados..."

if [ -n "$BACKUP_SELECIONADO" ]; then
    if [ -f "backups/$BACKUP_SELECIONADO/db.sqlite3" ]; then
        echo "[INFO] Fazendo backup do banco atual..."
        if [ -f "db.sqlite3" ]; then
            cp "db.sqlite3" "db.sqlite3.backup_$(date +%Y%m%d)"
        fi
        cp "backups/$BACKUP_SELECIONADO/db.sqlite3" "db.sqlite3"
        echo "[OK] Banco de dados importado"
    else
        echo "[ERRO] Backup não encontrado!"
        exit 1
    fi
else
    if [ -f "db.sqlite3" ]; then
        echo "[INFO] Usando db.sqlite3 da raiz do projeto"
        echo "[OK] Banco de dados encontrado"
    else
        echo "[ERRO] Nenhum banco de dados encontrado!"
        exit 1
    fi
fi
echo

# ========================================
# IMPORTAR DADOS JSON (OPCIONAL)
# ========================================
echo "[2/2] Verificando dados JSON para importar..."
if [ -n "$BACKUP_SELECIONADO" ]; then
    if [ -f "backups/$BACKUP_SELECIONADO/dados_exportados.json" ]; then
        echo "[INFO] Importando dados JSON..."
        $PYTHON_CMD manage.py loaddata "backups/$BACKUP_SELECIONADO/dados_exportados.json" >/dev/null 2>&1
        if [ $? -ne 0 ]; then
            echo "[AVISO] Falha ao importar dados JSON (pode ser normal)"
        else
            echo "[OK] Dados JSON importados"
        fi
    fi
fi
echo

# ========================================
# APLICAR MIGRAÇÕES
# ========================================
echo "[EXTRA] Aplicando migrações..."
$PYTHON_CMD manage.py migrate --noinput
echo "[OK] Migrações aplicadas"
echo

echo "========================================"
echo "  IMPORTAÇÃO CONCLUÍDA!"
echo "========================================"
echo
echo "Próximos passos:"
echo "1. Execute ./INICIAR.sh para iniciar o servidor"
echo "2. Verifique se os dados foram importados corretamente"
echo
echo "========================================"





















