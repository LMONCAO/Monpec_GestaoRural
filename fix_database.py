#!/usr/bin/env python
"""
Script para criar estruturas faltantes no banco de dados
Execute via: python fix_database.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.db import connection

cursor = connection.cursor()

print('🔧 Verificando e criando estruturas faltantes...')
print('')

# 1. Coluna mercadopago_customer_id
try:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_assinaturacliente' AND column_name='mercadopago_customer_id'")
    if not cursor.fetchone():
        print('Criando coluna mercadopago_customer_id...')
        cursor.execute('ALTER TABLE gestao_rural_assinaturacliente ADD COLUMN mercadopago_customer_id VARCHAR(255) NULL')
        cursor.execute('CREATE INDEX IF NOT EXISTS gestao_rura_mercado_1a0de9_idx ON gestao_rural_assinaturacliente(mercadopago_customer_id)')
        print('✅ mercadopago_customer_id criada!')
    else:
        print('✅ mercadopago_customer_id já existe')
except Exception as e:
    print(f'⚠️ Erro ao criar mercadopago_customer_id: {e}')

# 2. Coluna mercadopago_subscription_id
try:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_assinaturacliente' AND column_name='mercadopago_subscription_id'")
    if not cursor.fetchone():
        print('Criando coluna mercadopago_subscription_id...')
        cursor.execute('ALTER TABLE gestao_rural_assinaturacliente ADD COLUMN mercadopago_subscription_id VARCHAR(255) NULL')
        cursor.execute('CREATE INDEX IF NOT EXISTS gestao_rura_mercado_3577a7_idx ON gestao_rural_assinaturacliente(mercadopago_subscription_id)')
        print('✅ mercadopago_subscription_id criada!')
    else:
        print('✅ mercadopago_subscription_id já existe')
except Exception as e:
    print(f'⚠️ Erro ao criar mercadopago_subscription_id: {e}')

# 3. Coluna certificado_digital
try:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_produtorrural' AND column_name='certificado_digital'")
    if not cursor.fetchone():
        print('Criando coluna certificado_digital...')
        cursor.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN certificado_digital VARCHAR(100) NULL')
        print('✅ certificado_digital criada!')
    else:
        print('✅ certificado_digital já existe')
except Exception as e:
    print(f'⚠️ Erro ao criar certificado_digital: {e}')

# 4. Coluna senha_certificado
try:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_produtorrural' AND column_name='senha_certificado'")
    if not cursor.fetchone():
        print('Criando coluna senha_certificado...')
        cursor.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN senha_certificado VARCHAR(255) NULL')
        print('✅ senha_certificado criada!')
    else:
        print('✅ senha_certificado já existe')
except Exception as e:
    print(f'⚠️ Erro ao criar senha_certificado: {e}')

# 5. Coluna certificado_valido_ate
try:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_produtorrural' AND column_name='certificado_valido_ate'")
    if not cursor.fetchone():
        print('Criando coluna certificado_valido_ate...')
        cursor.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN certificado_valido_ate DATE NULL')
        print('✅ certificado_valido_ate criada!')
    else:
        print('✅ certificado_valido_ate já existe')
except Exception as e:
    print(f'⚠️ Erro ao criar certificado_valido_ate: {e}')

# 6. Coluna certificado_tipo
try:
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='gestao_rural_produtorrural' AND column_name='certificado_tipo'")
    if not cursor.fetchone():
        print('Criando coluna certificado_tipo...')
        cursor.execute('ALTER TABLE gestao_rural_produtorrural ADD COLUMN certificado_tipo VARCHAR(10) NULL')
        print('✅ certificado_tipo criada!')
    else:
        print('✅ certificado_tipo já existe')
except Exception as e:
    print(f'⚠️ Erro ao criar certificado_tipo: {e}')

# 7. Tabela UsuarioAtivo
try:
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name='gestao_rural_usuarioativo')")
    if not cursor.fetchone()[0]:
        print('Criando tabela UsuarioAtivo...')
        cursor.execute('''
            CREATE TABLE gestao_rural_usuarioativo (
                id BIGSERIAL NOT NULL PRIMARY KEY,
                nome_completo VARCHAR(255) NOT NULL,
                email VARCHAR(254) NOT NULL,
                telefone VARCHAR(20),
                primeiro_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                ultimo_acesso TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                total_acessos INTEGER NOT NULL DEFAULT 0,
                ativo BOOLEAN NOT NULL DEFAULT true,
                criado_em TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                usuario_id BIGINT NOT NULL UNIQUE,
                CONSTRAINT gestao_rural_usuarioativo_usuario_id_fkey 
                FOREIGN KEY (usuario_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS gestao_rural_usuarioativo_usuario_id_idx ON gestao_rural_usuarioativo(usuario_id)')
        cursor.execute("INSERT INTO django_migrations (app, name, applied) VALUES ('gestao_rural', '0081_add_usuario_ativo', NOW()) ON CONFLICT (app, name) DO NOTHING")
        print('✅ Tabela UsuarioAtivo criada!')
    else:
        print('✅ Tabela UsuarioAtivo já existe')
except Exception as e:
    print(f'⚠️ Erro ao criar UsuarioAtivo: {e}')

print('')
print('✅ Concluído!')


