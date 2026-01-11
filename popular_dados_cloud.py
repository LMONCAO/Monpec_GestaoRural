#!/usr/bin/env python3
import os
import sys
import django

# Configurações do Cloud SQL
CLOUD_SQL_HOST = '34.9.51.178'
CLOUD_SQL_PORT = '5432'
CLOUD_SQL_DB = 'monpec_db'
CLOUD_SQL_USER = 'postgres'
CLOUD_SQL_PASSWORD = 'L6171r12@@jjms'

# Configurar Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'sistema_rural.settings_gcp'
os.environ['CLOUD_SQL_CONNECTION_NAME'] = 'monpec-sistema-rural:us-central1:monpec-db'
os.environ['DB_HOST'] = CLOUD_SQL_HOST
os.environ['DB_PORT'] = CLOUD_SQL_PORT
os.environ['DB_NAME'] = CLOUD_SQL_DB
os.environ['DB_USER'] = CLOUD_SQL_USER
os.environ['DB_PASSWORD'] = CLOUD_SQL_PASSWORD
os.environ['SECRET_KEY'] = 'django-insecure-monpec-gcp-2025-secret-key-production'
os.environ['DEBUG'] = 'False'

django.setup()

from django.core.management import call_command
from gestao_rural.models import ProdutorRural, Propriedade
from django.contrib.auth import get_user_model

print('📊 Populando dados da demonstração...')

try:
    # Executar script de população de dados
    call_command('popular_fazenda_demonstracao_simples')

    # Verificar se foi criado
    propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
    if propriedade:
        print(f'✅ Propriedade criada: {propriedade.nome_propriedade}')
        print(f'📍 Localização: {propriedade.municipio}, {propriedade.uf}')
        print(f'🏞️ Área: {propriedade.area_total_ha} hectares')

        # Contar animais
        animal_count = propriedade.animalindividual_set.count()
        print(f'🐄 Animais cadastrados: {animal_count}')

    else:
        print('❌ Propriedade não foi criada')

    print('🎉 Dados populados com sucesso!')

except Exception as e:
    print(f'❌ Erro ao popular dados: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)




