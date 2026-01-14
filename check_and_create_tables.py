#!/usr/bin/env python
"""
Script para verificar e criar tabelas faltantes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import connection

def check_and_create_tables():
    """Verifica e cria tabelas faltantes"""
    print("INICIANDO VERIFICAÇÃO DE TABELAS...")
    with connection.cursor() as cursor:
        try:
            # Verificar se as tabelas existem
            tables_to_check = [
                'gestao_rural_planoassinatura',
                'gestao_rural_assinaturacliente'
            ]

            for table_name in tables_to_check:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name} LIMIT 1")
                    print(f"[OK] Tabela {table_name} existe")
                except Exception as e:
                    print(f"[ERRO] Tabela {table_name} não existe: {e}")

                    # Criar tabelas se não existirem
                    if table_name == 'gestao_rural_planoassinatura':
                        print(f"Tabela {table_name} já existe, recriando com estrutura correta...")

                        # Dropar e recriar a tabela
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
                                mercadopago_preapproval_id VARCHAR(120),
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

                        # Inserir dados básicos
                        cursor.execute("""
                            INSERT INTO gestao_rural_planoassinatura (
                                nome, slug, descricao, mercadopago_preapproval_id,
                                preco_mensal_referencia, max_usuarios, modulos_disponiveis,
                                recursos, ativo, popular, recomendado, ordem_exibicao,
                                criado_em, atualizado_em
                            ) VALUES
                            (
                                'Básico', 'basico', 'Plano básico para pequenos produtores', '',
                                49.90, 1, '["dashboard_pecuaria", "curral", "cadastro", "pecuaria", "financeiro", "relatorios"]',
                                '{"pecuaria": true, "financeiro": true, "relatorios": true}', true, false, false, 1,
                                NOW(), NOW()
                            ),
                            (
                                'Profissional', 'profissional', 'Plano completo para produtores', '',
                                99.90, 5, '["dashboard_pecuaria", "curral", "cadastro", "planejamento", "pecuaria", "rastreabilidade", "reproducao", "pesagem", "movimentacoes", "patrimonio", "nutricao", "compras", "vendas", "operacoes", "financeiro", "projetos", "relatorios", "categorias", "configuracoes"]',
                                '{"pecuaria": true, "financeiro": true, "relatorios": true, "projetos_bancarios": true}', true, true, true, 2,
                                NOW(), NOW()
                            ),
                            (
                                'Empresarial', 'empresarial', 'Plano empresarial para grandes propriedades', '',
                                199.90, 20, '["dashboard_pecuaria", "curral", "cadastro", "planejamento", "pecuaria", "rastreabilidade", "reproducao", "pesagem", "movimentacoes", "patrimonio", "nutricao", "compras", "vendas", "operacoes", "financeiro", "projetos", "relatorios", "categorias", "configuracoes"]',
                                '{"pecuaria": true, "financeiro": true, "relatorios": true, "projetos_bancarios": true, "multi_propriedade": true}', true, false, false, 3,
                                NOW(), NOW()
                            )
                        """)

                    elif table_name == 'gestao_rural_assinaturacliente':
                        print(f"Criando tabela {table_name}...")
                        cursor.execute("""
                            CREATE TABLE gestao_rural_assinaturacliente (
                                id BIGSERIAL PRIMARY KEY,
                                usuario_id INTEGER NOT NULL REFERENCES auth_user(id),
                                produtor_id INTEGER REFERENCES gestao_rural_produtorrural(id),
                                plano_id BIGINT REFERENCES gestao_rural_planoassinatura(id),
                                status VARCHAR(20) DEFAULT 'PENDENTE',
                                mercadopago_customer_id VARCHAR(120),
                                mercadopago_subscription_id VARCHAR(120),
                                gateway_pagamento VARCHAR(50) DEFAULT 'mercadopago',
                                ultimo_checkout_id VARCHAR(120),
                                current_period_end TIMESTAMP WITH TIME ZONE,
                                cancelamento_agendado BOOLEAN DEFAULT FALSE,
                                metadata JSONB DEFAULT '{}',
                                data_liberacao DATE,
                                criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                                atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                                UNIQUE(usuario_id)
                            )
                        """)

                    print(f"[OK] Tabela {table_name} criada com sucesso")

            # Verificar e criar tabelas importantes que podem estar faltando
            important_tables = [
                ('gestao_rural_planejamentoanual', """
                    CREATE TABLE gestao_rural_planejamentoanual (
                        id BIGSERIAL PRIMARY KEY,
                        propriedade_id INTEGER NOT NULL REFERENCES gestao_rural_propriedade(id),
                        codigo VARCHAR(20) UNIQUE,
                        ano INTEGER NOT NULL,
                        descricao VARCHAR(255),
                        status VARCHAR(15) DEFAULT 'RASCUNHO',
                        data_criacao TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        data_atualizacao TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        data_inicio DATE,
                        data_fim DATE,
                        observacoes TEXT
                    )
                """),
                ('gestao_rural_verificacaoemail', """
                    CREATE TABLE gestao_rural_verificacaoemail (
                        id BIGSERIAL PRIMARY KEY,
                        usuario_id INTEGER NOT NULL REFERENCES auth_user(id),
                        token VARCHAR(64) NOT NULL UNIQUE,
                        email_verificado BOOLEAN DEFAULT FALSE,
                        token_expira_em TIMESTAMP WITH TIME ZONE NOT NULL,
                        tentativas_verificacao INTEGER DEFAULT 0,
                        criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        verificado_em TIMESTAMP WITH TIME ZONE,
                        UNIQUE(usuario_id)
                    )
                """),
                ('gestao_rural_usuarioativo', """
                    CREATE TABLE gestao_rural_usuarioativo (
                        id BIGSERIAL PRIMARY KEY,
                        usuario_id INTEGER NOT NULL REFERENCES auth_user(id),
                        nome_completo VARCHAR(255) NOT NULL,
                        email VARCHAR(254) NOT NULL,
                        telefone VARCHAR(20),
                        primeiro_acesso TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        ultimo_acesso TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        total_acessos INTEGER DEFAULT 0,
                        ativo BOOLEAN DEFAULT TRUE,
                        criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        UNIQUE(usuario_id)
                    )
                """)
            ]

            for table_name_check, create_sql in important_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name_check} LIMIT 1")
                    print(f"[OK] Tabela {table_name_check} já existe, recriando...")

                    # Drop table and recreate with correct structure
                    cursor.execute(f"DROP TABLE IF EXISTS {table_name_check} CASCADE")
                    print(f"[INFO] Tabela {table_name_check} removida")

                    cursor.execute(create_sql)
                    print(f"[OK] Tabela {table_name_check} recriada com sucesso")
                except Exception:
                    print(f"Criando tabela faltante: {table_name_check}")
                    try:
                        cursor.execute(create_sql)
                        print(f"[OK] Tabela {table_name_check} criada com sucesso")
                    except Exception as create_error:
                        print(f"[ERRO] Erro ao criar {table_name_check}: {create_error}")

        except Exception as e:
            print(f"[ERRO] Erro geral: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    check_and_create_tables()