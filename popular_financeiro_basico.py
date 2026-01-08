#!/usr/bin/env python
"""
Script para popular lançamentos financeiros básicos da Fazenda Demonstração
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade
from gestao_rural.models_financeiro import ContaFinanceira, CategoriaFinanceira

def main():
    print("="*60)
    print("POPULANDO FINANCEIRO BASICO - FAZENDA DEMONSTRACAO")
    print("="*60)

    # Buscar propriedade
    propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
    if not propriedade:
        print("ERRO: Propriedade Fazenda Demonstracao nao encontrada!")
        return

    print(f"Propriedade: {propriedade.nome_propriedade}")

    # Criar contas financeiras básicas usando SQL direto para evitar problemas
    from django.db import connection

    contas_data = [
        {'nome': 'Caixa Demonstracao', 'tipo': 'CAIXA', 'saldo': Decimal('15000.00')},
        {'nome': 'BB Conta Corrente', 'tipo': 'CORRENTE', 'saldo': Decimal('250000.00')},
        {'nome': 'CEF Conta Corrente', 'tipo': 'CORRENTE', 'saldo': Decimal('100000.00')},
    ]

    contas = []
    with connection.cursor() as cursor:
        for conta_data in contas_data:
            # Verificar se já existe
            cursor.execute(
                "SELECT id FROM gestao_rural_contafinanceira WHERE propriedade_id = %s AND nome = %s",
                [propriedade.id, conta_data['nome']]
            )
            if cursor.fetchone():
                conta = ContaFinanceira.objects.get(propriedade=propriedade, nome=conta_data['nome'])
                contas.append(conta)
                print(f"Conta existente: {conta.nome}")
                continue

            # Criar conta
            try:
                cursor.execute("""
                    INSERT INTO gestao_rural_contafinanceira
                    (propriedade_id, nome, tipo, moeda, saldo_inicial, data_saldo_inicial,
                     permite_negativo, ativa, criado_em, atualizado_em)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                """, [
                    propriedade.id,
                    conta_data['nome'],
                    conta_data['tipo'],
                    'BRL',
                    conta_data['saldo'],
                    date(2023, 1, 1),
                    False,
                    True
                ])
                conta_id = cursor.fetchone()[0]
                conta = ContaFinanceira.objects.get(id=conta_id)
                contas.append(conta)
                print(f"Conta criada: {conta.nome}")
            except Exception as e:
                print(f"Erro ao criar conta {conta_data['nome']}: {e}")

    # Criar categorias básicas
    categorias_data = [
        {'nome': 'Venda de Animais', 'tipo': 'RECEITA'},
        {'nome': 'Combustivel', 'tipo': 'DESPESA'},
        {'nome': 'Medicamentos e Vacinas', 'tipo': 'DESPESA'},
        {'nome': 'Salarios', 'tipo': 'DESPESA'},
    ]

    categorias = {}
    with connection.cursor() as cursor:
        for cat_data in categorias_data:
            # Verificar se já existe
            cursor.execute(
                "SELECT id FROM gestao_rural_categoriafinanceira WHERE nome = %s AND tipo = %s",
                [cat_data['nome'], cat_data['tipo']]
            )
            row = cursor.fetchone()
            if row:
                categoria_id = row[0]
            else:
                # Criar categoria
                try:
                    cursor.execute("""
                        INSERT INTO gestao_rural_categoriafinanceira
                        (nome, tipo, criado_em, atualizado_em)
                        VALUES (%s, %s, NOW(), NOW())
                        RETURNING id
                    """, [cat_data['nome'], cat_data['tipo']])
                    categoria_id = cursor.fetchone()[0]
                except Exception as e:
                    print(f"Erro ao criar categoria {cat_data['nome']}: {e}")
                    continue

            categoria = CategoriaFinanceira.objects.raw('SELECT * FROM gestao_rural_categoriafinanceira WHERE id = %s', [categoria_id])[0]
            categorias[cat_data['nome']] = categoria
            print(f"Categoria: {categoria.nome}")

    # Criar lançamentos básicos
    lancamentos_criados = 0

    # Receitas (vendas de animais)
    categoria_receita = categorias.get('Venda de Animais')
    if categoria_receita and contas:
        conta = contas[0]  # Usar primeira conta

        for ano in [2023, 2024]:
            for mes in range(1, 13):
                # 2-4 vendas por mês
                num_vendas = random.randint(2, 4)
                for _ in range(num_vendas):
                    dia = random.randint(1, 28)
                    data_venda = date(ano, mes, dia)
                    valor_venda = Decimal(str(random.randint(8000, 40000)))

                    try:
                        with connection.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO gestao_rural_lancamentofinanceiro
                                (propriedade_id, categoria_id, data, descricao, valor,
                                 forma_pagamento, pago, data_pagamento, criado_em, atualizado_em)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                            """, [
                                propriedade.id,
                                categoria_receita.id,
                                data_venda,
                                f'Venda de {random.randint(3, 15)} animais',
                                valor_venda,
                                'TRANSFERENCIA',
                                True,
                                data_venda + timedelta(days=random.randint(0, 7)),
                            ])
                        lancamentos_criados += 1
                    except Exception as e:
                        print(f"Erro lancamento receita: {e}")

    # Despesas básicas
    for cat_nome, categoria in categorias.items():
        if categoria.tipo == 'DESPESA' and contas:
            conta = random.choice(contas)

            for ano in [2023, 2024]:
                for mes in range(1, 13):
                    # 1-3 despesas por mês por categoria
                    num_despesas = random.randint(1, 3)
                    for _ in range(num_despesas):
                        dia = random.randint(1, 28)
                        data_despesa = date(ano, mes, dia)

                        if cat_nome == 'Combustivel':
                            valor = Decimal(str(random.randint(2000, 8000)))
                        elif cat_nome == 'Medicamentos e Vacinas':
                            valor = Decimal(str(random.randint(1500, 6000)))
                        else:  # Salarios
                            valor = Decimal(str(random.randint(15000, 30000)))

                        try:
                            with connection.cursor() as cursor:
                                cursor.execute("""
                                    INSERT INTO gestao_rural_lancamentofinanceiro
                                    (propriedade_id, categoria_id, data, descricao, valor,
                                     forma_pagamento, pago, data_pagamento, criado_em, atualizado_em)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                                """, [
                                    propriedade.id,
                                    categoria.id,
                                    data_despesa,
                                    f'{cat_nome} - {data_despesa.strftime("%m/%Y")}',
                                    valor,
                                    'TRANSFERENCIA',
                                    True,
                                    data_despesa + timedelta(days=random.randint(1, 30)),
                                ])
                            lancamentos_criados += 1
                        except Exception as e:
                            print(f"Erro lancamento despesa: {e}")

    print(f"\nLancamentos criados: {lancamentos_criados}")
    print("="*60)
    print("FINANCEIRO BASICO POPULADO COM SUCESSO!")
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


