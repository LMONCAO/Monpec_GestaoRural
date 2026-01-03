#!/bin/bash
# ========================================
# MONPEC - INICIAR SERVIDOR (Linux/Mac)
# ========================================

echo "========================================"
echo "  MONPEC - INICIAR SERVIDOR"
echo "  Sistema de Gestão Rural"
echo "========================================"
echo

cd "$(dirname "$0")"
echo "[INFO] Diretório: $(pwd)"
echo

# ========================================
# PARAR SERVIDORES ANTERIORES
# ========================================
echo "[1/4] Parando servidores anteriores..."
pkill -f "manage.py runserver" 2>/dev/null
sleep 2
echo "[OK] Servidores anteriores parados"
echo

# ========================================
# VERIFICAR PYTHON
# ========================================
echo "[2/4] Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "[ERRO] Python não encontrado!"
    exit 1
fi

$PYTHON_CMD --version
echo

# ========================================
# VERIFICAR SISTEMA
# ========================================
echo "[3/4] Verificando sistema..."
$PYTHON_CMD manage.py check --deploy >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[AVISO] Alguns avisos encontrados (pode ser normal)"
else
    echo "[OK] Sistema verificado"
fi
echo

# ========================================
# INICIAR SERVIDOR
# ========================================
echo "[4/4] Iniciando servidor Django..."
echo
echo "========================================"
echo "  SERVIDOR INICIANDO"
echo "========================================"
echo
echo "[INFO] Servidor: http://localhost:8000"
echo "[INFO] Login: admin / Senha: admin"
echo
echo "[INFO] Pressione Ctrl+C para parar o servidor"
echo
echo "========================================"
echo

$PYTHON_CMD manage.py runserver 0.0.0.0:8000

if [ $? -ne 0 ]; then
    echo
    echo "[ERRO] Servidor parou com erro!"
    echo
    exit 1
fi





















