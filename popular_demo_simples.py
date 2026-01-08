#!/usr/bin/env python
"""
Script SIMPLES para popular a Fazenda Demonstração com dados básicos funcionais
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
from gestao_rural.models_compras_financeiro import Fornecedor

def popular_demo_basico():
    """Popula com dados básicos que funcionam"""

    print("Procurando Fazenda Demonstracao...")
    propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()

    if not propriedade:
        print("Fazenda nao encontrada!")
        return

    print(f"Encontrada: {propriedade.nome_propriedade} (ID: {propriedade.id})")

    # 1. Animais básicos funcionais
    print("Criando animais basicos...")
    try:
        # Criar categoria básica se não existir
        categoria, created = CategoriaAnimal.objects.get_or_create(
            nome='Vaca',
            sexo='F',
            defaults={'idade_minima_meses': 24, 'raca': 'NELORE', 'ativo': True}
        )

        # Criar 50 animais com numeração sequencial
        animais_criados = 0
        for i in range(1, 51):  # 50 animais
            numero_brinco = f"DEMO{i:03d}"
            try:
                AnimalIndividual.objects.get_or_create(
                    numero_brinco=numero_brinco,
                    propriedade=propriedade,
                    defaults={
                        'categoria': categoria,
                        'peso_atual_kg': 400 + random.randint(-50, 50),
                        'sexo': 'F',
                        'raca': 'NELORE',
                        'data_nascimento': date.today() - timedelta(days=random.randint(730, 1825)),  # 2-5 anos
                        'data_aquisicao': date.today() - timedelta(days=random.randint(30, 365)),
                        'status': 'ATIVO',
                    }
                )
                animais_criados += 1
            except Exception as e:
                print(f"Erro animal {numero_brinco}: {e}")

        print(f"Criados {animais_criados} animais")

        # Inventário básico
        try:
            InventarioRebanho.objects.get_or_create(
                propriedade=propriedade,
                data_inventario=date.today(),
                defaults={
                    'vacas_em_lactacao': 35,
                    'vacas_secas': 15,
                    'total_animais': 50,
                    'valor_por_cabeca': Decimal('2500.00'),
                    'valor_total_rebanho': Decimal('125000.00'),
                }
            )
            print("Inventario criado")
        except Exception as e:
            print(f"Erro inventario: {e}")

    except Exception as e:
        print(f"Erro pecuaria: {e}")

    # 2. Fornecedores básicos
    print("Criando fornecedores...")
    fornecedores_data = [
        {'nome': 'Nutripec MS', 'cpf_cnpj': '12.345.678/0001-90'},
        {'nome': 'Agropecuarista Silva', 'cpf_cnpj': '23.456.789/0001-80'},
        {'nome': 'Veterinaria Campo Grande', 'cpf_cnpj': '34.567.890/0001-70'},
        {'nome': 'Posto Rural', 'cpf_cnpj': '45.678.901/0001-60'},
        {'nome': 'Loja de Maquinas', 'cpf_cnpj': '56.789.012/0001-50'},
    ]

    fornecedores_criados = 0
    for forn_data in fornecedores_data:
        try:
            fornecedor, created = Fornecedor.objects.get_or_create(
                nome=forn_data['nome'],
                propriedade=propriedade,
                defaults={'cpf_cnpj': forn_data['cpf_cnpj']}
            )
            fornecedores_criados += 1
        except Exception as e:
            print(f"Erro fornecedor {forn_data['nome']}: {e}")

    print(f"Criados {fornecedores_criados} fornecedores")

    # 3. Funcionários básicos
    print("Criando funcionarios...")
    from gestao_rural.models_funcionarios import Funcionario

    funcionarios_data = [
        {'nome': 'Joao Gerente', 'cpf': '123.456.789-01', 'cargo': 'Gerente'},
        {'nome': 'Maria Vaqueira', 'cpf': '234.567.890-12', 'cargo': 'Vaqueira'},
        {'nome': 'Pedro Capataz', 'cpf': '345.678.901-23', 'cargo': 'Capataz'},
        {'nome': 'Ana Veterinaria', 'cpf': '456.789.012-34', 'cargo': 'Veterinaria'},
        {'nome': 'Carlos Mecanico', 'cpf': '567.890.123-45', 'cargo': 'Mecanico'},
        {'nome': 'Roberto Tratador', 'cpf': '678.901.234-56', 'cargo': 'Tratador'},
    ]

    funcionarios_criados = 0
    for func_data in funcionarios_data:
        try:
            Funcionario.objects.get_or_create(
                nome=func_data['nome'],
                propriedade=propriedade,
                defaults={
                    'cpf': func_data['cpf'],
                    'cargo': func_data['cargo'],
                    'salario_base': Decimal('2500.00'),
                    'situacao': 'ATIVO',
                    'data_admissao': date.today() - timedelta(days=random.randint(30, 365)),
                }
            )
            funcionarios_criados += 1
        except Exception as e:
            print(f"Erro funcionario {func_data['nome']}: {e}")

    print(f"Criados {funcionarios_criados} funcionarios")

    # 4. Pastagens básicas
    print("Criando pastagens...")
    from gestao_rural.models_controles_operacionais import Pastagem

    pastagens_data = [
        {'nome': 'Pastagem Norte', 'area_ha': 300.0},
        {'nome': 'Pastagem Sul', 'area_ha': 250.0},
        {'nome': 'Pastagem Leste', 'area_ha': 200.0},
        {'nome': 'Pastagem Oeste', 'area_ha': 180.0},
        {'nome': 'Pastagem Central', 'area_ha': 400.0},
    ]

    pastagens_criadas = 0
    for past_data in pastagens_data:
        try:
            Pastagem.objects.get_or_create(
                nome=past_data['nome'],
                propriedade=propriedade,
                defaults={'area_ha': Decimal(str(past_data['area_ha']))}
            )
            pastagens_criadas += 1
        except Exception as e:
            print(f"Erro pastagem {past_data['nome']}: {e}")

    print(f"Criadas {pastagens_criadas} pastagens")

    # 5. Cochos
    print("Criando cochos...")
    from gestao_rural.models_controles_operacionais import Cocho

    cochos_data = [
        {'identificacao': 'Cocho 01', 'capacidade': 120},
        {'identificacao': 'Cocho 02', 'capacidade': 120},
        {'identificacao': 'Cocho 03', 'capacidade': 100},
        {'identificacao': 'Cocho Mineral 01', 'capacidade': 80},
        {'identificacao': 'Cocho Mineral 02', 'capacidade': 80},
    ]

    cochos_criados = 0
    for cocho_data in cochos_data:
        try:
            Cocho.objects.get_or_create(
                identificacao=cocho_data['identificacao'],
                propriedade=propriedade,
                defaults={'capacidade_kg': cocho_data['capacidade']}
            )
            cochos_criados += 1
        except Exception as e:
            print(f"Erro cocho {cocho_data['identificacao']}: {e}")

    print(f"Criados {cochos_criados} cochos")

    # 6. Bens patrimoniais básicos
    print("Criando bens patrimoniais...")
    from gestao_rural.models_patrimonio import TipoBem, BemPatrimonial

    # Criar tipo básico
    tipo_maquina, created = TipoBem.objects.get_or_create(
        nome='Maquinas Agricolas',
        categoria='MAQUINA',
        defaults={'taxa_depreciacao': Decimal('10.00')}
    )

    bens_data = [
        {'descricao': 'Trator Principal', 'valor': 350000.00},
        {'descricao': 'Caminhao', 'valor': 200000.00},
        {'descricao': 'Curral', 'valor': 150000.00},
        {'descricao': 'Pulverizador', 'valor': 80000.00},
    ]

    bens_criados = 0
    for bem_data in bens_data:
        try:
            BemPatrimonial.objects.get_or_create(
                propriedade=propriedade,
                descricao=bem_data['descricao'],
                tipo_bem=tipo_maquina,
                defaults={
                    'valor_aquisicao': Decimal(str(bem_data['valor'])),
                    'data_aquisicao': date.today() - timedelta(days=random.randint(365, 1825)),
                }
            )
            bens_criados += 1
        except Exception as e:
            print(f"Erro bem {bem_data['descricao']}: {e}")

    print(f"Criados {bens_criados} bens patrimoniais")

    print("\nDEMONSTRACAO POPULADA COM DADOS REALISTAS!")
    print("- 50 animais diversos")
    print("- 5 fornecedores")
    print("- 6 funcionarios")
    print("- 5 pastagens (1330 ha total)")
    print("- 5 cochos")
    print("- 4 bens patrimoniais")
    print("\nUsuario pode explorar todos os modulos com dados realistas!")

if __name__ == '__main__':
    popular_demo_basico()


