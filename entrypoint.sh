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

# Verificar e corrigir schema do banco se necessário
echo "🔧 Verificando schema do banco..."
python3 manage.py shell --settings="$DJANGO_SETTINGS_MODULE" -c "
from django.db import connection
try:
    with connection.cursor() as cursor:
        # Verificar se a tabela produtorrural existe
        cursor.execute(\"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_produtorrural'\")
        if cursor.fetchone()[0] > 0:
            print('Tabela produtorrural existe')
            # Verificar se a coluna certificado_thumbprint existe
            cursor.execute(\"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='public' AND table_name='gestao_rural_produtorrural' AND column_name='certificado_thumbprint'\")
            if cursor.fetchone()[0] == 0:
                print('Adicionando coluna certificado_thumbprint...')
                cursor.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN certificado_thumbprint VARCHAR(255)')
                print('✅ Coluna certificado_thumbprint adicionada')
            else:
                print('✅ Coluna certificado_thumbprint já existe')

            # Verificar coluna certificado_emissor
            cursor.execute(\"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='public' AND table_name='gestao_rural_produtorrural' AND column_name='certificado_emissor'\")
            if cursor.fetchone()[0] == 0:
                print('Adicionando coluna certificado_emissor...')
                cursor.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN certificado_emissor VARCHAR(255)')
                print('✅ Coluna certificado_emissor adicionada')
            else:
                print('✅ Coluna certificado_emissor já existe')

            # Verificar coluna certificado_data_validade
            cursor.execute(\"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='public' AND table_name='gestao_rural_produtorrural' AND column_name='certificado_data_validade'\")
            if cursor.fetchone()[0] == 0:
                print('Adicionando coluna certificado_data_validade...')
                cursor.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN certificado_data_validade DATE')
                print('✅ Coluna certificado_data_validade adicionada')
            else:
                print('✅ Coluna certificado_data_validade já existe')

        else:
            print('Tabela produtorrural não existe - será criada pelas migrações')
except Exception as e:
    print(f'Erro na verificação do schema: {e}')
" 2>/dev/null || echo "⚠️ Verificação de schema falhou"

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
