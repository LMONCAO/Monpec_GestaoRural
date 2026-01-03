#!/bin/bash
# ========================================
# MONPEC - ATUALIZAR DO GITHUB (Linux/Mac)
# ========================================

echo "========================================"
echo "  MONPEC - ATUALIZAR DO GITHUB"
echo "  Sistema de Gestão Rural"
echo "========================================"
echo

cd "$(dirname "$0")"
echo "[INFO] Diretório: $(pwd)"
echo

# ========================================
# VERIFICAR GIT
# ========================================
echo "[1/5] Verificando Git..."
if ! command -v git &> /dev/null; then
    echo "[ERRO] Git não encontrado!"
    echo "Por favor, instale o Git: sudo apt-get install git"
    exit 1
fi
echo "[OK] Git encontrado"
git --version
echo

# ========================================
# VERIFICAR STATUS
# ========================================
echo "[2/5] Verificando status do repositório..."
git status --short
echo

# ========================================
# FAZER BACKUP LOCAL
# ========================================
echo "[3/5] Criando backup local..."
BACKUP_DIR="backups/backup_antes_atualizacao_$(date +%Y%m%d_%H%M%S)"

mkdir -p backups
if [ -f "db.sqlite3" ]; then
    cp "db.sqlite3" "${BACKUP_DIR}_db.sqlite3"
    echo "[OK] Backup do banco criado"
fi
echo

# ========================================
# ATUALIZAR DO GITHUB
# ========================================
echo "[4/5] Atualizando do GitHub..."
echo "[INFO] Fazendo fetch do repositório remoto..."
git fetch origin
if [ $? -ne 0 ]; then
    echo "[ERRO] Falha ao fazer fetch!"
    exit 1
fi

echo "[INFO] Verificando atualizações disponíveis..."
if git log HEAD..origin/master --oneline >/dev/null 2>&1; then
    echo "[INFO] Atualizações encontradas!"
    echo
    echo "Últimas atualizações:"
    git log HEAD..origin/master --oneline -5
    echo
    echo "[INFO] Fazendo pull do GitHub..."
    git pull origin master
    if [ $? -ne 0 ]; then
        echo "[ERRO] Falha ao fazer pull!"
        echo "[INFO] Pode haver conflitos. Verifique manualmente."
        exit 1
    fi
    echo "[OK] Código atualizado do GitHub"
else
    echo "[INFO] Nenhuma atualização disponível"
    echo "[INFO] Sistema já está atualizado"
fi
echo

# ========================================
# ATUALIZAR SISTEMA
# ========================================
echo "[5/5] Atualizando sistema..."

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

# Aplicar migrações
echo "[INFO] Aplicando migrações..."
$PYTHON_CMD manage.py migrate --noinput
if [ $? -ne 0 ]; then
    echo "[AVISO] Algumas migrações podem ter falhado"
else
    echo "[OK] Migrações aplicadas"
fi

# Coletar arquivos estáticos
echo "[INFO] Coletando arquivos estáticos..."
$PYTHON_CMD manage.py collectstatic --noinput --clear >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[AVISO] Falha ao coletar estáticos (pode ser normal)"
else
    echo "[OK] Arquivos estáticos atualizados"
fi
echo

echo "========================================"
echo "  ATUALIZAÇÃO CONCLUÍDA!"
echo "========================================"
echo
echo "Próximos passos:"
echo "1. Execute ./INICIAR.sh para iniciar o servidor"
echo "2. Ou execute ./ATUALIZAR_E_INICIAR.sh para atualizar e iniciar"
echo
echo "========================================"









