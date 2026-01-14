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

# TERCEIRO: Aplicar migrações com tratamento de conflitos
echo "📋 Aplicando migrações com tratamento inteligente de conflitos..."

# Primeiro tentar aplicar normalmente
if python manage.py migrate --settings="$SETTINGS_MODULE" 2>&1; then
    echo "✅ Migrações aplicadas com sucesso!"
else
    echo "⚠️ Conflito detectado, tentando resolver marcando migrações como fake..."

    # Se falhar, marcar como fake as migrações problemáticas
    python manage.py migrate gestao_rural zero --settings="$SETTINGS_MODULE" --fake 2>/dev/null || echo "⚠️ Reset fake falhou"

    # Marcar migrações específicas como fake
    for mig in "0001_initial" "0002_propriedade_car_propriedade_incra_propriedade_nirf_and_more" "0003_produtorrural_anos_experiencia_and_more" "0004_alter_parametrosprojecaorebanho_percentual_venda_femeas_anual_and_more" "0005_propriedade_tipo_ciclo_pecuario" "0006_abastecimentocombustivel_ajusteorcamentocompra_and_more" "0007_add_windows_cert_fields"; do
        python manage.py migrate gestao_rural $mig --settings="$SETTINGS_MODULE" --fake 2>/dev/null || echo "⚠️ Migração $mig fake falhou"
    done

    # Tentar novamente aplicar as migrações restantes
    python manage.py migrate --settings="$SETTINGS_MODULE" || {
        echo "❌ FALHA CRÍTICA: Mesmo após tentar fake, migrações falharam!"
        echo "Verificando conexão com banco..."
        python manage.py dbshell --settings="$SETTINGS_MODULE" <<< "SELECT version();" 2>/dev/null || echo "❌ Conexão com banco falhou!"
        echo "Continuando mesmo assim para tentar iniciar o serviço..."
    }
fi

# QUARTO: Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --settings="$SETTINGS_MODULE" || {
    echo "⚠️ Coleta de estáticos falhou, mas continuando..."
}

# QUINTO: Criar registros de assinatura
echo "🛠️ Criando registros de assinatura necessários..."
python create_assinatura_records.py 2>&1 || echo "⚠️ Criação de registros falhou"

# SEXTO: Corrigir coluna faltante diretamente
echo "🔧 Corrigindo coluna mercadopago_preapproval_id..."
python manage.py shell --settings="$SETTINGS_MODULE" -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        # Verificar se a tabela existe
        cursor.execute(\"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_planoassinatura'\")
        if cursor.fetchone()[0] > 0:
            # Verificar se a coluna existe
            cursor.execute(\"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='public' AND table_name='gestao_rural_planoassinatura' AND column_name='mercadopago_preapproval_id'\")
            if cursor.fetchone()[0] == 0:
                print('Adicionando coluna mercadopago_preapproval_id...')
                cursor.execute('ALTER TABLE gestao_rural_planoassinatura ADD COLUMN mercadopago_preapproval_id VARCHAR(120)')
                print('✅ Coluna adicionada com sucesso')
            else:
                print('✅ Coluna já existe')
        else:
            print('❌ Tabela não existe')
except Exception as e:
    print(f'Erro: {e}')
"

# SÉTIMO: CORREÇÃO CRÍTICA - Forçar criação da coluna endereco na tabela propriedade
echo "🔧 CORREÇÃO CRÍTICA: Verificando e criando coluna 'endereco' na tabela propriedade..."
python manage.py shell --settings="$SETTINGS_MODULE" -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        # Verificar se a tabela gestao_rural_propriedade existe
        cursor.execute(\"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_propriedade'\")
        if cursor.fetchone()[0] > 0:
            print('Tabela gestao_rural_propriedade existe')

            # Verificar se a coluna endereco existe
            cursor.execute(\"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='public' AND table_name='gestao_rural_propriedade' AND column_name='endereco'\")
            if cursor.fetchone()[0] == 0:
                print('Adicionando coluna endereco...')
                cursor.execute('ALTER TABLE gestao_rural_propriedade ADD COLUMN endereco TEXT')
                print('✅ Coluna endereco adicionada com sucesso')
            else:
                print('✅ Coluna endereco já existe')

            # Verificar outras colunas que podem estar faltando
            colunas_a_verificar = ['cep', 'bairro', 'latitude', 'longitude', 'ponto_referencia']
            for coluna in colunas_a_verificar:
                cursor.execute(f\"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='public' AND table_name='gestao_rural_propriedade' AND column_name='{coluna}'\")
                if cursor.fetchone()[0] == 0:
                    print(f'Adicionando coluna {coluna}...')
                    if coluna in ['latitude', 'longitude']:
                        cursor.execute(f'ALTER TABLE gestao_rural_propriedade ADD COLUMN {coluna} DECIMAL(11,8) NULL')
                    else:
                        cursor.execute(f'ALTER TABLE gestao_rural_propriedade ADD COLUMN {coluna} VARCHAR(255) NULL')
                    print(f'✅ Coluna {coluna} adicionada com sucesso')
                else:
                    print(f'✅ Coluna {coluna} já existe')
        else:
            print('❌ Tabela gestao_rural_propriedade não existe')
except Exception as e:
    print(f'Erro ao verificar/corrigir colunas: {e}')
    import traceback
    traceback.print_exc()
"

# SEXTO: Criar administrador
echo "👨‍💼 Criando administrador..."
python manage.py shell --settings="$SETTINGS_MODULE" -c "
from django.contrib.auth import get_user_model
User = get_user_model()
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@monpec.com.br',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print('Admin criado: admin / admin123')
else:
    # Sempre definir a senha conhecida
    admin.set_password('admin123')
    admin.save()
    print('Admin atualizado: admin / admin123')
"

# SEXTO: Verificar e criar tabelas e dados essenciais
echo "🛠️ Verificando e criando tabelas e dados essenciais..."
python check_and_create_tables.py || echo "⚠️ Erro ao executar check_and_create_tables.py"

# SÉTIMO: Popular dados completos da demonstração (1300 animais + planejamento)
echo "📊 Populando dados completos da demonstração..."
echo "⚠️ Populando dados (pode demorar alguns minutos)..."
timeout 600 python popular_dados_producao_completo.py || {
    echo "⚠️ População de dados falhou ou timeout, mas continuando..."
    echo "Dados podem ser populados manualmente depois via admin"
}

# SÉTIMO: Popular dados completos da demonstração (1138 animais + financeiro realista)
echo "🚜 Populando dados completos da demonstração (1138 animais + financeiro realista)..."
python popular_fazenda_demonstracao_completa_1138.py --settings="$SETTINGS_MODULE" || {
    echo "⚠️ População de dados demo falhou, mas continuando..."
}

# OITAVO: Verificar se dados foram populados
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

# NONO: Iniciar o servidor Gunicorn
echo "✅ Iniciando servidor Gunicorn..."
exec gunicorn sistema_rural.wsgi:application --bind 0.0.0.0:8080 --workers 2 --threads 2 --timeout 600 --access-logfile - --error-logfile - --log-level info
