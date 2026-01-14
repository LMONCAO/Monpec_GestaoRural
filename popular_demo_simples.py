#!/usr/bin/env python
"""
Script simples para popular a Fazenda Demonstracao com dados basicos
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date, datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth import get_user_model
from gestao_rural.models import (
    Propriedade, AnimalIndividual, CategoriaAnimal, InventarioRebanho
)
from gestao_rural.models_financeiro import (
    CategoriaFinanceira, ContaFinanceira, LancamentoFinanceiro
)

def popular_demo():
    """Popula dados basicos para demonstracao"""

    print("Procurando Fazenda Demonstracao...")
    try:
        propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
        if not propriedade:
            print("Fazenda Demonstracao nao encontrada!")
            return

        print(f"Encontrada: {propriedade.nome_propriedade} (ID: {propriedade.id})")

        # 1. Criar animais (meta: 1138)
        print("Criando animais...")
        criar_animais_simples(propriedade)

        # 2. Criar dados financeiros
        print("Criando dados financeiros...")
        criar_financeiro_simples(propriedade)

        print("Demonstracao populada com sucesso!")

    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

def criar_animais_simples(propriedade):
    """Cria animais de forma simples"""

    # Criar categorias basicas se nao existirem
    categorias_data = [
        {'nome': 'Vaca em Lactacao', 'sexo': 'F', 'idade_minima_meses': 24},
        {'nome': 'Vaca Seca', 'sexo': 'F', 'idade_minima_meses': 24},
        {'nome': 'Novilha', 'sexo': 'F', 'idade_minima_meses': 12},
        {'nome': 'Bezerro', 'sexo': 'M', 'idade_minima_meses': 0},
        {'nome': 'Bezerra', 'sexo': 'F', 'idade_minima_meses': 0},
        {'nome': 'Touro', 'sexo': 'M', 'idade_minima_meses': 24},
    ]

    categorias = {}
    for cat_data in categorias_data:
        cat, created = CategoriaAnimal.objects.get_or_create(
            nome=cat_data['nome'],
            sexo=cat_data['sexo'],
            defaults={
                'idade_minima_meses': cat_data['idade_minima_meses'],
                'raca': 'NELORE',
                'ativo': True
            }
        )
        categorias[cat_data['nome']] = cat

    # Distribuicao simples para chegar a 1138 animais
    distribuicao = {
        'Vaca em Lactacao': 300,
        'Vaca Seca': 250,
        'Novilha': 200,
        'Bezerro': 150,
        'Bezerra': 150,
        'Touro': 88,  # Total: 300+250+200+150+150+88 = 1138
    }

    numero_brinco = 1000
    total_criados = 0

    for categoria_nome, quantidade in distribuicao.items():
        categoria = categorias[categoria_nome]

        for i in range(quantidade):
            # Peso baseado na categoria
            if 'Vaca' in categoria_nome:
                peso = random.randint(400, 550)
            elif 'Novilha' in categoria_nome:
                peso = random.randint(300, 450)
            elif 'Bezerro' in categoria_nome or 'Bezerra' in categoria_nome:
                peso = random.randint(120, 200)
            else:  # Touro
                peso = random.randint(700, 950)

            try:
                AnimalIndividual.objects.get_or_create(
                    numero_brinco=f'DEMO{numero_brinco:04d}',
                    propriedade=propriedade,
                    defaults={
                        'categoria': categoria,
                        'peso_atual_kg': peso,
                        'sexo': categoria.sexo,
                        'raca': 'NELORE',
                        'data_nascimento': date.today() - timedelta(days=random.randint(365, 1825)),
                        'data_aquisicao': date.today() - timedelta(days=random.randint(30, 365)),
                        'status': 'ATIVO',
                    }
                )
                numero_brinco += 1
                total_criados += 1
            except Exception as e:
                print(f"Erro animal {numero_brinco}: {e}")

    # Criar inventario basico (apenas campos que existem)
    try:
        InventarioRebanho.objects.get_or_create(
            propriedade=propriedade,
            data_inventario=date.today(),
            defaults={
                'categoria': categorias['Vaca em Lactacao'],  # Usar categoria existente
                'quantidade': 1138,
                'valor_por_cabeca': Decimal('2500.00'),
            }
        )
    except Exception as e:
        print(f"Erro inventario: {e}")

    print(f"Criados {total_criados} animais")

def criar_financeiro_simples(propriedade):
    """Cria dados financeiros basicos"""

    # Criar categorias
    categorias_receita = ['Venda de Gado', 'Leite']
    categorias_despesa = ['Racao', 'Combustivel', 'Salarios', 'Manutencao']

    categorias = {}

    for cat_nome in categorias_receita + categorias_despesa:
        tipo = 'RECEITA' if cat_nome in categorias_receita else 'DESPESA'
        cat, created = CategoriaFinanceira.objects.get_or_create(
            nome=cat_nome,
            tipo=tipo,
            propriedade=propriedade,
            defaults={}
        )
        categorias[cat_nome] = cat

    # Criar conta bancaria
    conta, created = ContaFinanceira.objects.get_or_create(
        nome='Conta Corrente Banco do Brasil',
        propriedade=propriedade,
        defaults={
            'tipo': 'CORRENTE',
            'banco': 'Banco do Brasil',
            'agencia': '1234-5',
            'saldo_inicial': Decimal('100000.00'),
        }
    )

    # Criar lancamentos financeiros (200 no total)
    lancamentos_criados = 0

    # Receitas (100 lancamentos)
    for i in range(100):
        categoria = random.choice(['Venda de Gado', 'Leite'])
        valor = random.randint(2000, 8000) if categoria == 'Venda de Gado' else random.randint(800, 1500)

        try:
            LancamentoFinanceiro.objects.get_or_create(
                propriedade=propriedade,
                categoria=categorias[categoria],
                descricao=f'{categoria} - Cliente {i+1}',
                valor=Decimal(str(valor)),
                data_competencia=date.today() - timedelta(days=random.randint(1, 365)),
                data_vencimento=date.today() - timedelta(days=random.randint(1, 365)),
                forma_pagamento='PIX',
                status='QUITADO',
                conta_destino=conta,
                defaults={}
            )
            lancamentos_criados += 1
        except Exception as e:
            print(f"Erro receita {i}: {e}")

    # Despesas (100 lancamentos)
    for i in range(100):
        categoria = random.choice(['Racao', 'Combustivel', 'Salarios', 'Manutencao'])
        valor = random.randint(500, 3000)

        try:
            LancamentoFinanceiro.objects.get_or_create(
                propriedade=propriedade,
                categoria=categorias[categoria],
                descricao=f'{categoria} - Fornecedor {i+1}',
                valor=Decimal(str(valor)),
                data_competencia=date.today() - timedelta(days=random.randint(1, 365)),
                data_vencimento=date.today() - timedelta(days=random.randint(1, 365)),
                forma_pagamento='BOLETO',
                status='QUITADO',
                conta_origem=conta,
                defaults={}
            )
            lancamentos_criados += 1
        except Exception as e:
            print(f"Erro despesa {i}: {e}")

    print(f"Criados {lancamentos_criados} lancamentos financeiros")

if __name__ == '__main__':
    popular_demo()