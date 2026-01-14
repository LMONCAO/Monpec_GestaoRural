#!/usr/bin/env python
"""
Script para criar registros de assinatura necessários
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import connection

def create_assinatura_records():
    """Cria registros necessários para as assinaturas"""
    print("Verificando e criando registros de assinatura...")

    with connection.cursor() as cursor:
        try:
            # 1. Verificar se existem planos
            cursor.execute("SELECT COUNT(*) FROM gestao_rural_planoassinatura")
            planos_count = cursor.fetchone()[0]
            print(f"Planos existentes: {planos_count}")

            # Sempre recriar a tabela com estrutura completa
            print("Recriando tabela de planos com estrutura completa...")

            # Dropar e recriar tabela
            try:
                cursor.execute("DROP TABLE IF EXISTS gestao_rural_planoassinatura CASCADE")
                print("Tabela antiga removida")
            except Exception as drop_error:
                print(f"Aviso ao remover tabela: {drop_error}")

            # Criar tabela com estrutura completa
            cursor.execute("""
                CREATE TABLE gestao_rural_planoassinatura (
                    id BIGSERIAL PRIMARY KEY,
                    nome VARCHAR(120) NOT NULL UNIQUE,
                    slug VARCHAR(120) NOT NULL UNIQUE,
                    descricao TEXT,
                    mercadopago_preapproval_id VARCHAR(120) DEFAULT '',
                    preco_mensal_referencia DECIMAL(10,2),
                    max_usuarios INTEGER DEFAULT 1,
                    modulos_disponiveis JSONB DEFAULT '[]',
                    recursos JSONB DEFAULT '{}',
                    ativo BOOLEAN DEFAULT TRUE,
                    popular BOOLEAN DEFAULT FALSE,
                    recomendado BOOLEAN DEFAULT FALSE,
                    ordem_exibicao INTEGER DEFAULT 0,
                    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            print("Tabela recriada com estrutura completa")

            # Inserir planos
            cursor.execute("""
                INSERT INTO gestao_rural_planoassinatura (
                    nome, slug, descricao, mercadopago_preapproval_id,
                    preco_mensal_referencia, max_usuarios, modulos_disponiveis,
                    recursos, ativo, popular, recomendado, ordem_exibicao,
                    criado_em, atualizado_em
                ) VALUES
                ('Plano Básico', 'basico', 'Plano básico para pequenos produtores', '',
                 49.90, 1, '["dashboard_pecuaria", "curral", "cadastro", "pecuaria", "financeiro", "relatorios"]',
                 '{"pecuaria": true, "financeiro": true, "relatorios": true}', true, false, false, 1,
                 NOW(), NOW()),
                ('Plano Profissional', 'profissional', 'Plano completo para produtores', '',
                 99.90, 5, '["dashboard_pecuaria", "curral", "cadastro", "planejamento", "pecuaria", "rastreabilidade", "reproducao", "pesagem", "movimentacoes", "patrimonio", "nutricao", "compras", "vendas", "operacoes", "financeiro", "projetos", "relatorios", "categorias", "configuracoes"]',
                 '{"pecuaria": true, "financeiro": true, "relatorios": true, "projetos_bancarios": true}', true, true, true, 2,
                 NOW(), NOW()),
                ('Plano Empresarial', 'empresarial', 'Plano empresarial para grandes propriedades', '',
                 199.90, 20, '["dashboard_pecuaria", "curral", "cadastro", "planejamento", "pecuaria", "rastreabilidade", "reproducao", "pesagem", "movimentacoes", "patrimonio", "nutricao", "compras", "vendas", "operacoes", "financeiro", "projetos", "relatorios", "categorias", "configuracoes"]',
                 '{"pecuaria": true, "financeiro": true, "relatorios": true, "projetos_bancarios": true, "multi_propriedade": true}', true, false, false, 3,
                 NOW(), NOW())
            """)
            print("Planos criados com sucesso")

            # 2. Verificar usuários
            cursor.execute("SELECT id, username FROM auth_user WHERE is_active = true")
            users = cursor.fetchall()
            print(f"Usuários ativos encontrados: {len(users)}")

            for user_id, username in users:
                print(f"Verificando usuário: {username} (ID: {user_id})")

                # Verificar se já existe assinatura para este usuário
                cursor.execute("SELECT COUNT(*) FROM gestao_rural_assinaturacliente WHERE usuario_id = %s", [user_id])
                assinatura_count = cursor.fetchone()[0]

                if assinatura_count == 0:
                    print(f"Criando assinatura pendente para usuário {username}...")

                    # Buscar primeiro produtor do usuário
                    cursor.execute("""
                        SELECT id FROM gestao_rural_produtorrural
                        WHERE usuario_responsavel_id = %s
                        LIMIT 1
                    """, [user_id])

                    produtor_row = cursor.fetchone()
                    produtor_id = produtor_row[0] if produtor_row else None

                    # Criar assinatura pendente
                    cursor.execute("""
                        INSERT INTO gestao_rural_assinaturacliente (
                            usuario_id, produtor_id, plano_id, status,
                            mercadopago_customer_id, mercadopago_subscription_id,
                            gateway_pagamento, ultimo_checkout_id, current_period_end,
                            cancelamento_agendado, metadata, data_liberacao,
                            criado_em, atualizado_em
                        ) VALUES (
                            %s, %s, 1, 'PENDENTE',
                            '', '', 'mercadopago', '', NULL,
                            false, '{}', NULL,
                            NOW(), NOW()
                        )
                    """, [user_id, produtor_id])

                    print(f"Assinatura pendente criada para {username}")
                else:
                    print(f"Usuário {username} já tem assinatura")

            # 3. Verificar se há outras tabelas necessárias
            required_tables = [
                'gestao_rural_verificacaoemail',
                'gestao_rural_usuarioativo'
            ]

            for table_name in required_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} LIMIT 1")
                    print(f"Tabela {table_name} existe")
                except Exception:
                    print(f"Criando tabela {table_name}...")

                    if table_name == 'gestao_rural_verificacaoemail':
                        cursor.execute("""
                            CREATE TABLE gestao_rural_verificacaoemail (
                                id BIGSERIAL PRIMARY KEY,
                                usuario_id INTEGER NOT NULL REFERENCES auth_user(id),
                                codigo_verificacao VARCHAR(100) NOT NULL,
                                criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                                usado BOOLEAN DEFAULT FALSE,
                                expira_em TIMESTAMP WITH TIME ZONE NOT NULL,
                                UNIQUE(usuario_id)
                            )
                        """)
                    elif table_name == 'gestao_rural_usuarioativo':
                        cursor.execute("""
                            CREATE TABLE gestao_rural_usuarioativo (
                                id BIGSERIAL PRIMARY KEY,
                                usuario_id INTEGER NOT NULL REFERENCES auth_user(id),
                                criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                                atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                                UNIQUE(usuario_id)
                            )
                        """)

                    print(f"Tabela {table_name} criada")

            print("✅ TODAS AS VERIFICAÇÕES E CRIAÇÕES CONCLUÍDAS!")

        except Exception as e:
            print(f"❌ ERRO GERAL: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_assinatura_records()