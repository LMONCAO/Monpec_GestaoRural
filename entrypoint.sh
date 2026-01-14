#!/bin/bash

# VERSÃO FINAL: Django com Cloud SQL
export PORT=${PORT:-8080}

echo "🚀 MONPEC Cloud Run - VERSÃO FINAL"
echo "📍 Porta: $PORT"
echo "⏰ Hora: $(date)"

# Configurações Django
export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-sistema_rural.settings_gcp_deploy}"

# Verificações básicas
echo "🐍 Verificando Python..."
python3 -c "print('✅ Python OK')" || exit 1

echo "📦 Verificando Django..."
python3 -c "import django; print('✅ Django OK')" || exit 1

echo "🐴 Verificando Gunicorn..."
python3 -c "import gunicorn; print('✅ Gunicorn OK')" || exit 1

# Aguardar Cloud SQL ficar disponível (máximo 60 segundos)
echo "⏳ Aguardando Cloud SQL..."
for i in {1..60}; do
    if python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
import django
from django.conf import settings
django.setup()

from django.db import connections
from django.db.utils import OperationalError

try:
    conn = connections['default']
    conn.ensure_connection()
    print('✅ Banco OK')
    exit(0)
except OperationalError as e:
    print(f'⏳ Aguardando banco... {e}')
    exit(1)
"; then
        echo "✅ Cloud SQL conectado!"
        break
    fi

    if [ $i -eq 60 ]; then
        echo "❌ Timeout: Cloud SQL não disponível após 60 segundos"
        echo "📋 Verificando variáveis de ambiente..."
        env | grep -E "(DATABASE|DB_|DJANGO)" || echo "⚠️ Nenhuma variável DB encontrada"
        exit 1
    fi

    echo "⏳ Tentativa $i/60 - Aguardando 2 segundos..."
    sleep 2
done

# Aplicar migrações com estratégia robusta
echo "📋 Aplicando migrações..."

# Primeiro tentar migração normal
if python3 manage.py migrate --settings="$DJANGO_SETTINGS_MODULE" 2>&1; then
    echo "✅ Migrações aplicadas com sucesso"
else
    echo "⚠️ Migração normal falhou, tentando --run-syncdb..."
    if python3 manage.py migrate --run-syncdb --settings="$DJANGO_SETTINGS_MODULE" 2>&1; then
        echo "✅ Migrações syncdb aplicadas"
    else
        echo "⚠️ Mesmo syncdb falhou, tentando fake migrations..."
        # Marcar migrações problemáticas como fake
        python3 manage.py migrate gestao_rural 0007_add_windows_cert_fields --fake --settings="$DJANGO_SETTINGS_MODULE" 2>/dev/null || echo "⚠️ Fake migration falhou"
        python3 manage.py migrate gestao_rural 0103_remover_campos_stripe --fake --settings="$DJANGO_SETTINGS_MODULE" 2>/dev/null || echo "⚠️ Fake stripe falhou"

        # Tentar novamente
        python3 manage.py migrate --settings="$DJANGO_SETTINGS_MODULE" 2>/dev/null && echo "✅ Migrações OK após fake" || echo "❌ Migrações continuam falhando"
    fi
fi

# CORREÇÃO FORÇADA DO SCHEMA - Executar sempre
echo "🔧 CORREÇÃO FORÇADA: Adicionando colunas faltantes..."
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
import django
django.setup()
from django.db import connection

try:
    with connection.cursor() as cursor:
        print('🔍 Verificando e corrigindo schema...')

        # Forçar adição das colunas faltantes
        colunas_para_adicionar = [
            ('certificado_thumbprint', 'VARCHAR(255)'),
            ('certificado_emissor', 'VARCHAR(255)'),
            ('certificado_data_validade', 'DATE'),
        ]

        for coluna, tipo in colunas_para_adicionar:
            try:
                # Verificar se a coluna existe
                cursor.execute(f\"\"\"
                    SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_schema='public'
                    AND table_name='gestao_rural_produtorrural'
                    AND column_name='{coluna}'
                \"\"\")
                existe = cursor.fetchone()[0] > 0

                if not existe:
                    print(f'➕ Adicionando coluna {coluna}...')
                    cursor.execute(f'ALTER TABLE gestao_rural_produtorrural ADD COLUMN {coluna} {tipo}')
                    print(f'✅ Coluna {coluna} adicionada com sucesso!')
                else:
                    print(f'✅ Coluna {coluna} já existe')
            except Exception as e:
                print(f'⚠️ Erro ao verificar/adicionar {coluna}: {e}')

        print('🎯 Correção de schema concluída!')

except Exception as e:
    print(f'❌ ERRO GERAL na correção de schema: {e}')
    import traceback
    traceback.print_exc()
" || echo "❌ Falha crítica na correção de schema"

# TESTE FINAL: Django consegue carregar URLs?
echo "🧪 TESTANDO SE DJANGO CARREGA URLs..."
python3 -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '$DJANGO_SETTINGS_MODULE')
import django
django.setup()

try:
    from django.urls import reverse
    from django.conf import settings
    print('✅ Django URLs OK')
    print(f'📍 DEBUG: {settings.DEBUG}')
    print(f'🗄️ DATABASE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')

    # Tentar resolver algumas URLs importantes
    try:
        login_url = reverse('login')
        print(f'✅ URL login: {login_url}')
    except:
        print('⚠️ URL login não encontrada')

    try:
        landing_url = reverse('landing_page')
        print(f'✅ URL landing: {landing_url}')
    except:
        print('⚠️ URL landing não encontrada')

    # Verificar se consegue importar as views
    try:
        from gestao_rural import views
        print('✅ Views principais OK')
    except Exception as e:
        print(f'⚠️ Erro nas views: {e}')

except Exception as e:
    print(f'❌ ERRO ao carregar URLs: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

# Coletar estáticos (mínimo)
echo "📦 Coletando estáticos..."
python3 manage.py collectstatic --noinput --settings="$DJANGO_SETTINGS_MODULE" 2>/dev/null || echo "⚠️ Collectstatic falhou"

# Iniciar Django
echo "🚀 Iniciando Django na porta $PORT..."
exec gunicorn sistema_rural.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
