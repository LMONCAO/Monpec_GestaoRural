#!/bin/bash

# Entrypoint simplificado para MONPEC
export PORT=${PORT:-8080}

echo "🚀 Iniciando MONPEC..."

SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-sistema_rural.settings_gcp}"
echo "Settings: $SETTINGS_MODULE"

# Migrações essenciais
echo "🔄 Executando migrações..."
python manage.py migrate admin --noinput --settings="$SETTINGS_MODULE" || echo "Admin failed"
python manage.py migrate auth --noinput --settings="$SETTINGS_MODULE" || echo "Auth failed"
python manage.py migrate contenttypes --noinput --settings="$SETTINGS_MODULE" || echo "Contenttypes failed"
python manage.py migrate sessions --noinput --settings="$SETTINGS_MODULE" || echo "Sessions failed"
python manage.py migrate --noinput --settings="$SETTINGS_MODULE" || echo "Migrate failed"

# Criar admin
echo "👤 Criando admin..."
python manage.py shell --settings="$SETTINGS_MODULE" -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@monpec.com.br', 'L6171r12@@')
    print('Admin criado')
else:
    print('Admin existe')
"

# Iniciar servidor
echo "✅ Iniciando servidor..."
exec gunicorn sistema_rural.wsgi:application --bind 0.0.0.0:8080 --workers 2 --threads 2 --timeout 600

# Executar migrações
echo "🔄 Executando migrações..."

# PRIMEIRO: Marcar migrações problemáticas como fake ANTES de executar qualquer outra migração
# Isso resolve problemas de campos/tabelas que já foram alteradas
echo "📋 Marcando migrações problemáticas como fake..."
python manage.py migrate gestao_rural 0034_financeiro_reestruturado --fake --settings="$SETTINGS_MODULE" 2>/dev/null || {
    echo "⚠️ Migração 0034 já aplicada ou não existe, continuando..."
}
python manage.py migrate gestao_rural 0103_remover_campos_stripe --fake --settings="$SETTINGS_MODULE" 2>/dev/null || {
    echo "⚠️ Migração 0103 já aplicada ou não existe, continuando..."
}

# SEGUNDO: Executar migrações básicas do Django (admin, auth, sessions, etc.)
echo "📋 Aplicando migrações básicas do Django..."
python manage.py migrate admin --noinput --settings="$SETTINGS_MODULE" || echo "⚠️ Migrações admin falharam"
python manage.py migrate auth --noinput --settings="$SETTINGS_MODULE" || echo "⚠️ Migrações auth falharam"
python manage.py migrate contenttypes --noinput --settings="$SETTINGS_MODULE" || echo "⚠️ Migrações contenttypes falharam"
python manage.py migrate sessions --noinput --settings="$SETTINGS_MODULE" || echo "⚠️ Migrações sessions falharam"

# TERCEIRO: Forçar execução específica da migração 0045 (SessaoSegura)
echo "🔧 Forçando execução da migração 0045 (SessaoSegura)..."
python manage.py migrate gestao_rural 0045 --settings="$SETTINGS_MODULE" || {
    echo "⚠️ Migração 0045 falhou, tentando continuar..."
}

# QUARTO: Executar todas as outras migrações
echo "📋 Aplicando todas as migrações restantes..."
python manage.py migrate --noinput --settings="$SETTINGS_MODULE" || {
    echo "❌ ERRO: Algumas migrações falharam!"
    echo "⚠️ Verifique os logs acima"
    echo "⚠️ Tentando continuar mesmo assim..."
}

# Executar migrações (simplificado)
echo "🔄 Executando migrações..."
python manage.py migrate --noinput --settings="$SETTINGS_MODULE"
MIGRATE_EXIT_CODE=$?

if [ $MIGRATE_EXIT_CODE -ne 0 ]; then
    echo "❌ ERRO: Migrações falharam com código $MIGRATE_EXIT_CODE"
    echo "⚠️ Continuando mesmo assim..."
fi

# Carregar dados iniciais (categorias de animais)
echo "📦 Carregando dados iniciais..."
python manage.py carregar_categorias --settings="$SETTINGS_MODULE" || {
    echo "⚠️ Carregamento de categorias falhou, mas continuando..."
}

# Garantir que existe usuário admin
echo "👤 Garantindo usuário admin..."
python manage.py garantir_admin --settings="$SETTINGS_MODULE" || {
    echo "⚠️ Criação de admin falhou, mas continuando..."
}

# Popular dados da demonstração
echo "📊 Populando dados da demonstração..."
python popular_dados_producao.py || {
    echo "⚠️ População de dados falhou, mas continuando..."
    echo "Dados podem ser populados manualmente depois"
}

# Criar admin (simplificado)
echo "👨‍💼 Criando administrador..."
python manage.py shell --settings="$SETTINGS_MODULE" -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@monpec.com.br', 'L6171r12@@')
    print('Admin criado: admin / L6171r12@@')
else:
    print('Admin já existe')
"

# Verificar se dados foram populados
echo "🔍 Verificando dados populados..."
python manage.py shell -c "
from gestao_rural.models import Propriedade, AnimalIndividual
try:
    prop = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
    if prop:
        animais = AnimalIndividual.objects.filter(propriedade=prop).count()
        print(f'Dados OK: {animais} animais na propriedade demo')
    else:
        print('Propriedade demo nao encontrada')
except Exception as e:
    print(f'Erro na verificacao: {e}')
" --settings="$SETTINGS_MODULE" || {
    echo "⚠️ Verificação de dados falhou, mas continuando..."
}

# Iniciar o servidor Gunicorn
echo "✅ Iniciando servidor Gunicorn..."
# Reduzir workers para 2 para debug - aumentar timeout e adicionar preload
exec gunicorn sistema_rural.wsgi:application --bind 0.0.0.0:8080 --workers 2 --threads 2 --timeout 600 --access-logfile - --error-logfile - --log-level info
