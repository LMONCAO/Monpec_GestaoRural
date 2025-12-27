#!/bin/bash
# Script completo de deploy para produção - Sistema MONPEC
# Execute este script no servidor Linux para fazer o deploy completo

set -e  # Parar em caso de erro

echo "========================================"
echo "DEPLOY COMPLETO - SISTEMA MONPEC"
echo "========================================"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# 1. Verificar se está no diretório correto
print_info "Verificando diretório do projeto..."
if [ ! -f "manage.py" ]; then
    print_error "manage.py não encontrado! Execute este script no diretório raiz do projeto."
    exit 1
fi
print_success "Diretório correto"

# 2. Ativar ambiente virtual se existir
print_info "Verificando ambiente virtual..."
if [ -d "venv" ]; then
    print_info "Ativando ambiente virtual..."
    source venv/bin/activate
    print_success "Ambiente virtual ativado"
elif [ -d ".venv" ]; then
    print_info "Ativando ambiente virtual (.venv)..."
    source .venv/bin/activate
    print_success "Ambiente virtual ativado"
else
    print_info "Ambiente virtual não encontrado, usando Python do sistema"
fi

# 3. Verificar Python e Django
print_info "Verificando Python e Django..."
python --version
python -c "import django; print(f'Django {django.get_version()}')" || {
    print_error "Django não está instalado!"
    exit 1
}
print_success "Python e Django OK"

# 4. Instalar/atualizar dependências
print_info "Instalando dependências..."
if [ -f "requirements.txt" ]; then
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    print_success "Dependências instaladas"
else
    print_error "requirements.txt não encontrado!"
    exit 1
fi

# 5. Verificar arquivo .env_producao
print_info "Verificando configurações de ambiente..."
if [ ! -f ".env_producao" ]; then
    print_error ".env_producao não encontrado!"
    print_info "Criando arquivo .env_producao de exemplo..."
    cat > .env_producao << EOF
# Configurações de Produção - Sistema MONPEC
DEBUG=False
SECRET_KEY=django-insecure-sistema-rural-ia-2025-producao-segura-123456789
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=Monpec2025!
DB_HOST=localhost
DB_PORT=5432
EOF
    print_info "Arquivo .env_producao criado. POR FAVOR, EDITE COM AS CONFIGURAÇÕES CORRETAS!"
fi

# 6. Criar diretórios necessários
print_info "Criando diretórios necessários..."
mkdir -p staticfiles
mkdir -p media
mkdir -p logs
if [ ! -d "/var/www/monpec.com.br" ]; then
    sudo mkdir -p /var/www/monpec.com.br/static
    sudo mkdir -p /var/www/monpec.com.br/media
    sudo chown -R $USER:$USER /var/www/monpec.com.br
fi
if [ ! -d "/var/log/monpec" ]; then
    sudo mkdir -p /var/log/monpec
    sudo chown -R $USER:$USER /var/log/monpec
fi
print_success "Diretórios criados"

# 7. Aplicar migrações
print_info "Aplicando migrações do banco de dados..."
python manage.py migrate --settings=sistema_rural.settings_producao --noinput
print_success "Migrações aplicadas"

# 8. Coletar arquivos estáticos
print_info "Coletando arquivos estáticos..."
python manage.py collectstatic --settings=sistema_rural.settings_producao --noinput --clear
print_success "Arquivos estáticos coletados"

# 9. Verificar configurações
print_info "Verificando configurações..."
python manage.py check --settings=sistema_rural.settings_producao --deploy || {
    print_error "Erros encontrados nas configurações!"
    print_info "Verifique os erros acima"
}

# 10. Executar diagnóstico
print_info "Executando diagnóstico..."
if [ -f "diagnosticar_erro_producao.py" ]; then
    python diagnosticar_erro_producao.py
fi

# 11. Criar superusuário se não existir
print_info "Verificando superusuário..."
python manage.py shell --settings=sistema_rural.settings_producao << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print("Nenhum superusuário encontrado. Execute:")
    print("python manage.py createsuperuser --settings=sistema_rural.settings_producao")
else:
    print("Superusuário(s) encontrado(s)")
EOF

echo ""
echo "========================================"
print_success "DEPLOY CONCLUÍDO!"
echo "========================================"
echo ""
echo "Próximos passos:"
echo "1. Configure o servidor web (Apache/Nginx) para usar:"
echo "   - DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao"
echo "   - WSGI: sistema_rural.wsgi.application"
echo ""
echo "2. Reinicie o servidor web:"
echo "   sudo systemctl restart apache2  # ou nginx"
echo ""
echo "3. Teste o acesso em http://monpec.com.br"
echo ""
echo "4. Verifique os logs em /var/log/monpec/django.log"
echo ""









