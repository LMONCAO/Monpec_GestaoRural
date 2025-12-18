#!/bin/bash

echo "=========================================="
echo "INSTALADOR MONPEC GESTAO RURAL"
echo "=========================================="
echo ""

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python 3 não encontrado!"
    echo "Por favor, instale Python 3.8 ou superior."
    exit 1
fi

echo "[OK] Python encontrado"
python3 --version
echo ""

# Criar ambiente virtual (opcional, mas recomendado)
if [ ! -d "venv" ]; then
    echo "[INFO] Criando ambiente virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[AVISO] Não foi possível criar ambiente virtual. Continuando sem ele..."
    else
        echo "[OK] Ambiente virtual criado"
    fi
fi

# Ativar ambiente virtual
if [ -d "venv" ]; then
    echo "[INFO] Ativando ambiente virtual..."
    source venv/bin/activate
fi
echo ""

# Atualizar pip
echo "[INFO] Atualizando pip..."
pip install --upgrade pip
echo ""

# Instalar dependências
echo "[INFO] Instalando dependências do projeto..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[ERRO] Falha ao instalar dependências!"
    exit 1
fi
echo "[OK] Dependências instaladas"
echo ""

# Verificar se arquivo .env existe
if [ ! -f ".env" ]; then
    echo "[INFO] Arquivo .env não encontrado. Criando arquivo de exemplo..."
    cat > .env << EOF
# Configurações do Sistema
DEBUG=True
SECRET_KEY=django-insecure-change-in-production
ALLOWED_HOSTS=127.0.0.1,localhost

# Banco de Dados - SQLite (padrão para desenvolvimento)
DB_ENGINE=sqlite3

# Para usar PostgreSQL, descomente e configure:
# DB_ENGINE=postgresql
# DB_NAME=sistema_rural
# DB_USER=django_user
# DB_PASSWORD=sua_senha
# DB_HOST=localhost
# DB_PORT=5432
EOF
    echo "[OK] Arquivo .env criado. Configure conforme necessário."
else
    echo "[OK] Arquivo .env já existe"
fi
echo ""

# Verificar se banco de dados existe
if [ -f "db.sqlite3" ]; then
    echo "[INFO] Banco de dados SQLite encontrado"
else
    echo "[INFO] Banco de dados não encontrado. Criando..."
fi

# Executar migrações
echo "[INFO] Executando migrações do banco de dados..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "[ERRO] Falha ao executar migrações!"
    exit 1
fi
echo "[OK] Migrações executadas"
echo ""

# Coletar arquivos estáticos
echo "[INFO] Coletando arquivos estáticos..."
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
    echo "[AVISO] Não foi possível coletar arquivos estáticos. Continuando..."
fi
echo ""

# Verificar superusuário
echo "[INFO] Verificando se existe superusuário..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superusuário existe' if User.objects.filter(is_superuser=True).exists() else 'Nenhum superusuário encontrado')" 2>/dev/null
echo ""

echo "=========================================="
echo "INSTALAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Para iniciar o servidor, execute:"
echo "  ./INICIAR.sh"
echo ""
echo "Ou manualmente:"
echo "  python manage.py runserver"
echo ""






















