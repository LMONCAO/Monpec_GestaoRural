#!/bin/bash

# Entrypoint limpo e corrigido para MONPEC
export PORT=${PORT:-8080}

echo "🚀 Iniciando MONPEC..."

SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-sistema_rural.settings_gcp}"
echo "Settings: $SETTINGS_MODULE"

# PRIMEIRO: Marcar migrações problemáticas como fake ANTES de executar qualquer outra migração
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

# TERCEIRO: Executar todas as outras migrações
echo "📋 Aplicando todas as migrações restantes..."
python manage.py migrate --noinput --settings="$SETTINGS_MODULE" || {
    echo "❌ ERRO: Algumas migrações falharam!"
    echo "⚠️ Verifique os logs acima"
    echo "⚠️ Tentando continuar mesmo assim..."
}

# QUARTO: Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings="$SETTINGS_MODULE" || {
    echo "⚠️ Coleta de estáticos falhou, mas continuando..."
}

# QUINTO: Criar administrador
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

# SEXTO: Popular dados completos da demonstração (1300 animais + planejamento)
echo "📊 Populando dados completos da demonstração..."
echo "⚠️ Populando dados (pode demorar alguns minutos)..."
timeout 600 python popular_dados_producao_completo.py || {
    echo "⚠️ População de dados falhou ou timeout, mas continuando..."
    echo "Dados podem ser populados manualmente depois via admin"
}

# SÉTIMO: Verificar se dados foram populados
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

# OITAVO: Iniciar o servidor Gunicorn
echo "✅ Iniciando servidor Gunicorn..."
exec gunicorn sistema_rural.wsgi:application --bind 0.0.0.0:8080 --workers 2 --threads 2 --timeout 600 --access-logfile - --error-logfile - --log-level info
