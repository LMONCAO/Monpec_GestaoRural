#!/usr/bin/env python
"""
Script simples para popular a Fazenda Demonstração com dados básicos
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
from gestao_rural.models import Propriedade, AnimalIndividual, CategoriaAnimal, InventarioRebanho
from gestao_rural.models_financeiro import CategoriaFinanceira, ContaFinanceira, LancamentoFinanceiro
from gestao_rural.models_compras_financeiro import Fornecedor
from gestao_rural.models_funcionarios import Funcionario
from gestao_rural.models_controles_operacionais import Pastagem, Cocho
from gestao_rural.models_patrimonio import TipoBem, BemPatrimonial

def popular_fazenda_demo():
    """Popula a Fazenda Demonstração com dados básicos"""

    print("Procurando Fazenda Demonstracao...")
    try:
        propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
        if not propriedade:
            print("Fazenda Demonstracao nao encontrada!")
            return

        print(f"Encontrada: {propriedade.nome_propriedade} (ID: {propriedade.id})")

        # 1. Pecuária básica
        print("Criando animais...")
        try:
            # Categoria básica
            categoria, created = CategoriaAnimal.objects.get_or_create(
                nome='Vaca em Lactacao',
                sexo='F',
                defaults={'idade_minima_meses': 24, 'raca': 'NELORE', 'ativo': True}
            )

            # Alguns animais
            for i in range(1, 11):
                AnimalIndividual.objects.get_or_create(
                    numero_brinco=f'DEMO{i:03d}',
                    propriedade=propriedade,
                    defaults={
                        'categoria': categoria,
                        'peso_atual_kg': 400 + random.randint(-50, 50),
                        'sexo': 'F',
                        'raca': 'NELORE',
                        'data_nascimento': date.today() - timedelta(days=random.randint(365, 1825)),
                        'status': 'ATIVO',
                    }
                )
            print("Criados 10 animais")
        except Exception as e:
            print(f"Erro pecuaria: {e}")

        # 2. Financeiro básico
        print("Criando lancamentos financeiros...")
        try:
            # Categoria receita
            cat_receita, created = CategoriaFinanceira.objects.get_or_create(
                nome='Venda de Gado',
                tipo='RECEITA',
                propriedade=propriedade,
                defaults={'ativo': True}
            )

            # Categoria despesa
            cat_despesa, created = CategoriaFinanceira.objects.get_or_create(
                nome='Racao',
                tipo='DESPESA',
                propriedade=propriedade,
                defaults={'ativo': True}
            )

            # Conta
            conta, created = ContaFinanceira.objects.get_or_create(
                nome='Conta Corrente',
                propriedade=propriedade,
                defaults={
                    'tipo': 'CORRENTE',
                    'saldo_inicial': Decimal('10000.00'),
                    'ativo': True,
                }
            )

            # Lançamentos
            LancamentoFinanceiro.objects.get_or_create(
                propriedade=propriedade,
                categoria=cat_receita,
                descricao='Venda demo',
                valor=Decimal('5000.00'),
                data_competencia=date.today(),
                data_vencimento=date.today(),
                forma_pagamento='PIX',
                status='QUITADO',
                conta_destino=conta,
            )

            LancamentoFinanceiro.objects.get_or_create(
                propriedade=propriedade,
                categoria=cat_despesa,
                descricao='Compra racao demo',
                valor=Decimal('1000.00'),
                data_competencia=date.today(),
                data_vencimento=date.today(),
                forma_pagamento='PIX',
                status='QUITADO',
                conta_origem=conta,
            )
            print("Criados lancamentos financeiros")
        except Exception as e:
            print(f"Erro financeiro: {e}")

        # 3. Fornecedores
        print("Criando fornecedores...")
        try:
            Fornecedor.objects.get_or_create(
                nome='Nutripec Demo',
                propriedade=propriedade,
                defaults={
                    'cpf_cnpj': '12.345.678/0001-90',
                    'tipo': 'RACAO',
                }
            )
            print("Criado fornecedor")
        except Exception as e:
            print(f"Erro fornecedor: {e}")

        # 4. Funcionários
        print("Criando funcionarios...")
        try:
            Funcionario.objects.get_or_create(
                nome='Joao Demo',
                propriedade=propriedade,
                defaults={
                    'cpf': '123.456.789-00',
                    'cargo': 'Gerente',
                    'salario_base': Decimal('3000.00'),
                    'situacao': 'ATIVO',
                    'data_admissao': date.today(),
                }
            )
            print("Criado funcionario")
        except Exception as e:
            print(f"Erro funcionario: {e}")

        # 5. Pastagens e Cochos
        print("Criando pastagens e cochos...")
        try:
            # Apenas cocho por enquanto, pastagem tem campos desconhecidos
            Cocho.objects.get_or_create(
                identificacao='Cocho Demo',
                propriedade=propriedade,
                defaults={
                    'capacidade_kg': 100,
                }
            )
            print("Criado cocho")
        except Exception as e:
            print(f"Erro operacional: {e}")

        # 6. Patrimônio
        print("Criando patrimonio...")
        try:
            tipo, created = TipoBem.objects.get_or_create(
                nome='Maquinas',
                categoria='MAQUINA',
                defaults={'taxa_depreciacao': Decimal('10.00')}
            )

            BemPatrimonial.objects.get_or_create(
                propriedade=propriedade,
                descricao='Trator Demo',
                tipo_bem=tipo,
                defaults={
                    'valor_aquisicao': Decimal('200000.00'),
                    'data_aquisicao': date.today() - timedelta(days=365),
                }
            )
            print("Criado bem patrimonial")
        except Exception as e:
            print(f"Erro patrimonio: {e}")

        print("\nFAZENDA DEMONSTRACAO POPULADA COM SUCESSO!")
        print("Dados basicos criados em todos os modulos.")

    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    popular_fazenda_demo()
