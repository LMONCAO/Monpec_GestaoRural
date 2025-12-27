#!/bin/bash
# 🔄 SCRIPT COMPLETO: LIMPAR E INSTALAR DO ZERO
# Executa limpeza completa seguida de instalação do zero
# Projeto: monpec-sistema-rural

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo ""
echo "========================================"
echo "🔄 LIMPAR E INSTALAR DO ZERO - MONPEC"
echo "========================================"
echo ""
warning "Este script vai:"
echo "  1. DELETAR todos os recursos antigos do GCP"
echo "  2. INSTALAR tudo do zero com configurações corretas"
echo ""
warning "ATENÇÃO: Todos os dados do banco serão perdidos!"
echo ""

# Verificar se os scripts existem
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIMPAR_SCRIPT="$SCRIPT_DIR/LIMPAR_RECURSOS_GCP.sh"
INSTALAR_SCRIPT="$SCRIPT_DIR/INSTALAR_DO_ZERO.sh"

if [ ! -f "$LIMPAR_SCRIPT" ]; then
    error "Script de limpeza não encontrado: $LIMPAR_SCRIPT"
    exit 1
fi

if [ ! -f "$INSTALAR_SCRIPT" ]; then
    error "Script de instalação não encontrado: $INSTALAR_SCRIPT"
    exit 1
fi

# Confirmação final
read -p "Tem CERTEZA que deseja continuar? Digite 'CONFIRMAR TUDO' para prosseguir: " CONFIRM
if [ "$CONFIRM" != "CONFIRMAR TUDO" ]; then
    error "Operação cancelada!"
    exit 1
fi
echo ""

# PARTE 1: LIMPEZA
echo ""
echo "========================================"
log "PARTE 1: LIMPEZA DE RECURSOS"
echo "========================================"
echo ""

# Dar permissão de execução
chmod +x "$LIMPAR_SCRIPT"

# Executar script de limpeza
bash "$LIMPAR_SCRIPT"

if [ $? -ne 0 ]; then
    error "Erro durante a limpeza!"
    exit 1
fi

success "Limpeza concluída!"
echo ""

# Aguardar um pouco para garantir que recursos foram deletados
log "Aguardando 10 segundos para garantir que recursos foram deletados..."
sleep 10
echo ""

# PARTE 2: INSTALAÇÃO
echo ""
echo "========================================"
log "PARTE 2: INSTALAÇÃO DO ZERO"
echo "========================================"
echo ""

# Dar permissão de execução
chmod +x "$INSTALAR_SCRIPT"

# Executar script de instalação
bash "$INSTALAR_SCRIPT"

if [ $? -ne 0 ]; then
    error "Erro durante a instalação!"
    exit 1
fi

# RESUMO FINAL
echo ""
echo "========================================"
success "PROCESSO COMPLETO CONCLUÍDO!"
echo "========================================"
echo ""
log "O que foi feito:"
echo "  ✅ Recursos antigos deletados"
echo "  ✅ Instância Cloud SQL criada"
echo "  ✅ Banco de dados criado"
echo "  ✅ Imagem Docker criada"
echo "  ✅ Serviço Cloud Run deployado"
echo "  ✅ Migrações aplicadas"
echo "  ✅ Arquivos estáticos coletados"
echo ""
success "Sistema pronto para uso! 🎉"
echo ""
















