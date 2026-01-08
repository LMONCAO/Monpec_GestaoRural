#!/usr/bin/env python
"""
Script para popular a Fazenda Demonstração com dados REALISTAS e ABRANGENTES
Dados baseados em uma propriedade pecuária típica do Mato Grosso do Sul
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

User = get_user_model()

def criar_dados_realistas_fazenda_demonstracao():
    """Cria dados REALISTAS e ABRANGENTES para a Fazenda Demonstração"""

    print("Procurando Fazenda Demonstracao...")
    try:
        propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
        if not propriedade:
            print("Fazenda Demonstracao nao encontrada!")
            return

        print(f"Encontrada: {propriedade.nome_propriedade} (ID: {propriedade.id})")

        # 1. Criar dados de Pecuária REALISTAS
        print("Populando pecuaria com dados realistas...")
        criar_pecuaria_realista(propriedade)

        # 2. Criar dados Financeiros REALISTAS
        print("Populando financeiro com dados realistas...")
        criar_financeiro_realista(propriedade)

        # 3. Criar dados de Compras REALISTAS
        print("Populando compras com dados realistas...")
        criar_compras_realistas(propriedade)

        # 4. Criar dados de Funcionários REALISTAS
        print("Populando equipe completa...")
        criar_funcionarios_realistas(propriedade)

        # 5. Criar dados Operacionais REALISTAS
        print("Populando estrutura operacional...")
        criar_operacional_realista(propriedade)

        # 6. Criar dados de Patrimônio REALISTAS
        print("Populando patrimonio completo...")
        criar_patrimonio_realista(propriedade)

        print("\nFazenda Demonstracao populada com dados REALISTAS!")
        print("Dados baseados em propriedade tipica do Mato Grosso do Sul.")
        print("Usuario pode se identificar facilmente com os numeros.")

    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

def criar_pecuaria_realista(propriedade):
    """Cria dados de pecuária REALISTAS baseado em fazenda típica MS"""

    # Categorias de animais realistas
    categorias_data = [
        {'nome': 'Vaca em Lactação', 'sexo': 'F', 'idade_minima_meses': 24, 'raca': 'NELORE'},
        {'nome': 'Vaca Seca', 'sexo': 'F', 'idade_minima_meses': 24, 'raca': 'NELORE'},
        {'nome': 'Vaca Descansada', 'sexo': 'F', 'idade_minima_meses': 24, 'raca': 'NELORE'},
        {'nome': 'Novilha 24-30 meses', 'sexo': 'F', 'idade_minima_meses': 24, 'raca': 'NELORE'},
        {'nome': 'Novilha 30-36 meses', 'sexo': 'F', 'idade_minima_meses': 30, 'raca': 'NELORE'},
        {'nome': 'Bezerro', 'sexo': 'M', 'idade_minima_meses': 0, 'raca': 'NELORE'},
        {'nome': 'Bezerra', 'sexo': 'F', 'idade_minima_meses': 0, 'raca': 'NELORE'},
        {'nome': 'Garrote', 'sexo': 'M', 'idade_minima_meses': 12, 'raca': 'NELORE'},
        {'nome': 'Novilho', 'sexo': 'M', 'idade_minima_meses': 18, 'raca': 'NELORE'},
        {'nome': 'Touro', 'sexo': 'M', 'idade_minima_meses': 24, 'raca': 'NELORE'},
    ]

    categorias = {}
    for cat_data in categorias_data:
        cat, created = CategoriaAnimal.objects.get_or_create(
            nome=cat_data['nome'],
            sexo=cat_data['sexo'],
            defaults={
                'idade_minima_meses': cat_data['idade_minima_meses'],
                'raca': cat_data['raca'],
                'ativo': True
            }
        )
        categorias[cat_data['nome']] = cat

    # Animais realistas - distribuição típica de fazenda MS
    animais_data = [
        # Vacas em Lactação (20% do rebanho)
        *[(f'ML{i:03d}', 'Vaca em Lactação', 480 + random.randint(-30, 30)) for i in range(1, 31)],
        # Vacas Secas (15% do rebanho)
        *[(f'SC{i:03d}', 'Vaca Seca', 450 + random.randint(-25, 25)) for i in range(1, 23)],
        # Vacas Descansadas (10% do rebanho)
        *[(f'DC{i:03d}', 'Vaca Descansada', 460 + random.randint(-20, 20)) for i in range(1, 16)],
        # Novilhas 24-30 meses (15% do rebanho)
        *[(f'N1{i:03d}', 'Novilha 24-30 meses', 350 + random.randint(-30, 20)) for i in range(1, 23)],
        # Novilhas 30-36 meses (10% do rebanho)
        *[(f'N2{i:03d}', 'Novilha 30-36 meses', 380 + random.randint(-25, 25)) for i in range(1, 16)],
        # Bezerros (8% do rebanho)
        *[(f'BZ{i:03d}', 'Bezerro', 180 + random.randint(-20, 30)) for i in range(1, 13)],
        # Bezeras (7% do rebanho)
        *[(f'BR{i:03d}', 'Bezerra', 165 + random.randint(-15, 25)) for i in range(1, 11)],
        # Garrotes (6% do rebanho)
        *[(f'GR{i:03d}', 'Garrote', 220 + random.randint(-20, 30)) for i in range(1, 10)],
        # Novilhos (6% do rebanho)
        *[(f'NV{i:03d}', 'Novilho', 280 + random.randint(-25, 35)) for i in range(1, 10)],
        # Touros (3% do rebanho - 4 touros)
        *[(f'TR{i:03d}', 'Touro', 850 + random.randint(-50, 100)) for i in range(1, 5)],
    ]

    animais_criados = 0
    for numero_brinco, categoria_nome, peso in animais_data:
        try:
            AnimalIndividual.objects.get_or_create(
                numero_brinco=numero_brinco,
                propriedade=propriedade,
                defaults={
                    'categoria': categorias[categoria_nome],
                    'peso_atual_kg': peso,
                    'sexo': categorias[categoria_nome].sexo,
                    'raca': categorias[categoria_nome].raca,
                    'data_nascimento': date.today() - timedelta(days=random.randint(365, 1825)),
                    'data_aquisicao': date.today() - timedelta(days=random.randint(30, 365)),
                    'status': 'ATIVO',
                }
            )
            animais_criados += 1
        except Exception as e:
            print(f"Erro ao criar animal {numero_brinco}: {e}")

    # Inventário do rebanho realista
    try:
        InventarioRebanho.objects.get_or_create(
            propriedade=propriedade,
            data_inventario=date.today(),
            defaults={
                'vacas_em_lactacao': 30,
                'vacas_secas': 22,
                'vacas_descansadas': 15,
                'novilhas_24_30_meses': 22,
                'novilhas_30_36_meses': 15,
                'bezerros': 12,
                'bezerras': 10,
                'garrotes': 9,
                'novilhos': 9,
                'touros': 4,
                'total_animais': 148,  # Soma total
                'valor_por_cabeca': Decimal('2800.00'),  # Preço médio MS
                'valor_total_rebanho': Decimal('414400.00'),  # 148 * 2800
            }
        )
        print(f"✅ Criados {animais_criados} animais realistas + inventário completo")
    except Exception as e:
        print(f"Erro ao criar inventário: {e}")

def criar_financeiro_realista(propriedade):
    """Cria dados financeiros REALISTAS baseados em gestão típica"""

    # Categorias financeiras abrangentes
    categorias = {}
    cats_data = [
        # RECEITAS
        {'nome': 'Venda de Bois Gordo', 'tipo': 'RECEITA'},
        {'nome': 'Venda de Novilhas', 'tipo': 'RECEITA'},
        {'nome': 'Venda de Bezerros', 'tipo': 'RECEITA'},
        {'nome': 'Leite', 'tipo': 'RECEITA'},
        {'nome': 'Arrendamento de Pastagens', 'tipo': 'RECEITA'},
        {'nome': 'Adubação Verde', 'tipo': 'RECEITA'},

        # DESPESAS
        {'nome': 'Ração e Suplementos', 'tipo': 'DESPESA'},
        {'nome': 'Medicamentos Veterinários', 'tipo': 'DESPESA'},
        {'nome': 'Combustível', 'tipo': 'DESPESA'},
        {'nome': 'Manutenção de Máquinas', 'tipo': 'DESPESA'},
        {'nome': 'Salários', 'tipo': 'DESPESA'},
        {'nome': 'Energia Elétrica', 'tipo': 'DESPESA'},
        {'nome': 'Telefone/Internet', 'tipo': 'DESPESA'},
        {'nome': 'Contabilidade', 'tipo': 'DESPESA'},
        {'nome': 'Seguros', 'tipo': 'DESPESA'},
        {'nome': 'Impostos', 'tipo': 'DESPESA'},
    ]

    for cat_data in cats_data:
        try:
            cat, created = CategoriaFinanceira.objects.get_or_create(
                nome=cat_data['nome'],
                tipo=cat_data['tipo'],
                propriedade=propriedade,
                defaults={'ativo': True}
            )
            categorias[cat_data['nome']] = cat
        except Exception as e:
            print(f"Erro categoria {cat_data['nome']}: {e}")

    # Contas bancárias realistas
    contas = {}
    contas_data = [
        {'nome': 'Conta Corrente BB', 'tipo': 'CORRENTE', 'banco': 'Banco do Brasil', 'agencia': '1234', 'conta': '56789-0', 'saldo': 45000.00},
        {'nome': 'Conta Poupança BB', 'tipo': 'POUPANCA', 'banco': 'Banco do Brasil', 'agencia': '1234', 'conta': '98765-4', 'saldo': 120000.00},
    ]

    for conta_data in contas_data:
        try:
            conta, created = ContaFinanceira.objects.get_or_create(
                nome=conta_data['nome'],
                propriedade=propriedade,
                defaults={
                    'tipo': conta_data['tipo'],
                    'banco': conta_data['banco'],
                    'agencia': conta_data['agencia'],
                    'conta': conta_data['conta'],
                    'saldo_inicial': Decimal(str(conta_data['saldo'])),
                    'ativo': True,
                }
            )
            contas[conta_data['nome']] = conta
        except Exception as e:
            print(f"Erro conta {conta_data['nome']}: {e}")

    # Lançamentos financeiros realistas dos últimos 12 meses
    lancamentos_data = [
        # RECEITAS (mensais aproximadas)
        ('Venda de Bois Gordo', 45000.00, 'CREDITO', 'Conta Corrente BB', -30),
        ('Venda de Bois Gordo', 52000.00, 'CREDITO', 'Conta Corrente BB', -60),
        ('Venda de Bois Gordo', 38000.00, 'CREDITO', 'Conta Corrente BB', -90),
        ('Venda de Novilhas', 28000.00, 'CREDITO', 'Conta Corrente BB', -45),
        ('Venda de Bezerros', 15000.00, 'CREDITO', 'Conta Corrente BB', -15),
        ('Leite', 8500.00, 'CREDITO', 'Conta Corrente BB', -7),
        ('Leite', 9200.00, 'CREDITO', 'Conta Corrente BB', -37),
        ('Arrendamento de Pastagens', 3500.00, 'CREDITO', 'Conta Corrente BB', -20),

        # DESPESAS (fixas e variáveis)
        ('Ração e Suplementos', 12000.00, 'DEBITO', 'Conta Corrente BB', -10),
        ('Ração e Suplementos', 11500.00, 'DEBITO', 'Conta Corrente BB', -40),
        ('Medicamentos Veterinários', 3200.00, 'DEBITO', 'Conta Corrente BB', -25),
        ('Combustível', 4800.00, 'DEBITO', 'Conta Corrente BB', -8),
        ('Combustível', 5200.00, 'DEBITO', 'Conta Corrente BB', -38),
        ('Manutenção de Máquinas', 6800.00, 'DEBITO', 'Conta Corrente BB', -55),
        ('Salários', 15000.00, 'DEBITO', 'Conta Corrente BB', -30),
        ('Salários', 15000.00, 'DEBITO', 'Conta Corrente BB', -60),
        ('Energia Elétrica', 1200.00, 'DEBITO', 'Conta Corrente BB', -12),
        ('Telefone/Internet', 450.00, 'DEBITO', 'Conta Corrente BB', -10),
        ('Contabilidade', 800.00, 'DEBITO', 'Conta Corrente BB', -45),
        ('Seguros', 2400.00, 'DEBITO', 'Conta Corrente BB', -180),
        ('Impostos', 5800.00, 'DEBITO', 'Conta Corrente BB', -90),
    ]

    lancamentos_criados = 0
    for cat_nome, valor, tipo, conta_nome, dias_atras in lancamentos_data:
        try:
            conta = contas[conta_nome]
            categoria = categorias[cat_nome]

            LancamentoFinanceiro.objects.get_or_create(
                propriedade=propriedade,
                categoria=categoria,
                descricao=f'{cat_nome} - {date.today() + timedelta(days=dias_atras):%d/%m/%Y}',
                valor=Decimal(str(valor)),
                data_competencia=date.today() + timedelta(days=dias_atras),
                data_vencimento=date.today() + timedelta(days=dias_atras),
                forma_pagamento='PIX',
                status='QUITADO',
                conta_origem=conta if tipo == 'DEBITO' else None,
                conta_destino=conta if tipo == 'CREDITO' else None,
            )
            lancamentos_criados += 1
        except Exception as e:
            print(f"Erro lançamento {cat_nome}: {e}")

    print(f"✅ Criadas {len(categorias)} categorias + {len(contas)} contas + {lancamentos_criados} lançamentos realistas")

def criar_compras_realistas(propriedade):
    """Cria fornecedores REALISTAS baseados em supridores típicos MS"""

    fornecedores_data = [
        # Ração e Suplementos
        {'nome': 'Nutripec Alimentos Ltda', 'cpf_cnpj': '12.345.678/0001-90', 'tipo': 'RACAO', 'telefone': '(67) 3384-1234'},
        {'nome': 'Agropecuária São Francisco', 'cpf_cnpj': '23.456.789/0001-80', 'tipo': 'RACAO', 'telefone': '(67) 3384-5678'},
        {'nome': 'Suprepec Rações', 'cpf_cnpj': '34.567.890/0001-70', 'tipo': 'RACAO', 'telefone': '(67) 3384-9012'},

        # Medicamentos Veterinários
        {'nome': 'Vet Pharma MS', 'cpf_cnpj': '45.678.901/0001-60', 'tipo': 'MEDICAMENTO', 'telefone': '(67) 3385-1111'},
        {'nome': 'Agrovet Campo Grande', 'cpf_cnpj': '56.789.012/0001-50', 'tipo': 'MEDICAMENTO', 'telefone': '(67) 3385-2222'},

        # Equipamentos
        {'nome': 'John Deere Brasil', 'cpf_cnpj': '67.890.123/0001-40', 'tipo': 'EQUIPAMENTO', 'telefone': '(67) 3386-3333'},
        {'nome': 'Tratores e Máquinas MS', 'cpf_cnpj': '78.901.234/0001-30', 'tipo': 'EQUIPAMENTO', 'telefone': '(67) 3386-4444'},

        # Combustível
        {'nome': 'Posto Rural MS', 'cpf_cnpj': '89.012.345/0001-20', 'tipo': 'COMBUSTIVEL', 'telefone': '(67) 3387-5555'},
        {'nome': 'Auto Posto Pantanal', 'cpf_cnpj': '90.123.456/0001-10', 'tipo': 'COMBUSTIVEL', 'telefone': '(67) 3387-6666'},

        # Serviços
        {'nome': 'Contabilidade Rural MS', 'cpf_cnpj': '01.234.567/0001-00', 'tipo': 'SERVICO', 'telefone': '(67) 3388-7777'},
        {'nome': 'Manutenção de Máquinas Silva', 'cpf_cnpj': '12.345.678/0002-90', 'tipo': 'SERVICO', 'telefone': '(67) 3388-8888'},
    ]

    fornecedores_criados = 0
    for forn_data in fornecedores_data:
        try:
            fornecedor, created = Fornecedor.objects.get_or_create(
                nome=forn_data['nome'],
                propriedade=propriedade,
                defaults={
                    'cpf_cnpj': forn_data['cpf_cnpj'],
                    'tipo': forn_data['tipo'],
                }
            )
            fornecedores_criados += 1
        except Exception as e:
            print(f"Erro fornecedor {forn_data['nome']}: {e}")

    print(f"✅ Criados {fornecedores_criados} fornecedores realistas")

def criar_funcionarios_realistas(propriedade):
    """Cria equipe completa REALISTA para fazenda MS"""

    funcionarios_data = [
        # Administração
        {'nome': 'João Carlos Silva', 'cpf': '123.456.789-01', 'cargo': 'Administrador', 'salario': 4500.00, 'situacao': 'ATIVO', 'admissao': -730},
        {'nome': 'Maria Aparecida Santos', 'cpf': '234.567.890-12', 'cargo': 'Contadora', 'salario': 3200.00, 'situacao': 'ATIVO', 'admissao': -365},

        # Pecuária
        {'nome': 'José Roberto Oliveira', 'cpf': '345.678.901-23', 'cargo': 'Gerente Pecuário', 'salario': 3800.00, 'situacao': 'ATIVO', 'admissao': -545},
        {'nome': 'Antônio Ferreira Costa', 'cpf': '456.789.012-34', 'cargo': 'Vaqueiro Senior', 'salario': 2200.00, 'situacao': 'ATIVO', 'admissao': -180},
        {'nome': 'Pedro Henrique Lima', 'cpf': '567.890.123-45', 'cargo': 'Vaqueiro', 'salario': 2000.00, 'situacao': 'ATIVO', 'admissao': -90},
        {'nome': 'Carlos Eduardo Rocha', 'cpf': '678.901.234-56', 'cargo': 'Vaqueiro', 'salario': 2000.00, 'situacao': 'ATIVO', 'admissao': -60},
        {'nome': 'Roberto Silva Santos', 'cpf': '789.012.345-67', 'cargo': 'Tratador de Animais', 'salario': 1800.00, 'situacao': 'ATIVO', 'admissao': -30},

        # Veterinária
        {'nome': 'Dra. Ana Carolina Mendes', 'cpf': '890.123.456-78', 'cargo': 'Veterinária', 'salario': 4200.00, 'situacao': 'ATIVO', 'admissao': -365},

        # Manutenção
        {'nome': 'Marcos Vinícius Alves', 'cpf': '901.234.567-89', 'cargo': 'Mecânico', 'salario': 2800.00, 'situacao': 'ATIVO', 'admissao': -240},
        {'nome': 'Roberto Carlos Pereira', 'cpf': '012.345.678-90', 'cargo': 'Auxiliar de Manutenção', 'salario': 1600.00, 'situacao': 'ATIVO', 'admissao': -120},

        # Ex-funcionários (para mostrar histórico)
        {'nome': 'Francisco José Almeida', 'cpf': '123.456.789-02', 'cargo': 'Vaqueiro', 'salario': 1900.00, 'situacao': 'DEMITIDO', 'admissao': -400},
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
                    'salario_base': Decimal(str(func_data['salario'])),
                    'situacao': func_data['situacao'],
                    'data_admissao': date.today() + timedelta(days=func_data['admissao']),
                }
            )
            funcionarios_criados += 1
        except Exception as e:
            print(f"Erro funcionário {func_data['nome']}: {e}")

    print(f"✅ Criados {funcionarios_criados} funcionários realistas")

def criar_operacional_realista(propriedade):
    """Cria estrutura operacional REALISTA"""

    # Pastagens realistas para 1500 ha
    pastagens_data = [
        {'nome': 'Pastagem Norte - Braquiária', 'area_ha': 280.5, 'capacidade': 140},
        {'nome': 'Pastagem Sul - Tanzânia', 'area_ha': 320.2, 'capacidade': 160},
        {'nome': 'Pastagem Leste - Mombaça', 'area_ha': 250.8, 'capacidade': 125},
        {'nome': 'Pastagem Oeste - Colonião', 'area_ha': 198.3, 'capacidade': 99},
        {'nome': 'Pastagem Central - Capim Gordura', 'area_ha': 450.2, 'capacidade': 225},
    ]

    pastagens_criadas = 0
    for past_data in pastagens_data:
        try:
            Pastagem.objects.get_or_create(
                nome=past_data['nome'],
                propriedade=propriedade,
                defaults={
                    'area_ha': Decimal(str(past_data['area_ha'])),
                    'capacidade': past_data['capacidade'],
                }
            )
            pastagens_criadas += 1
        except Exception as e:
            print(f"Erro pastagem {past_data['nome']}: {e}")

    # Cochos para suplementação
    cochos_data = [
        {'identificacao': 'Cocho Principal 01', 'capacidade': 150},
        {'identificacao': 'Cocho Principal 02', 'capacidade': 150},
        {'identificacao': 'Cocho Suplementar Norte', 'capacidade': 100},
        {'identificacao': 'Cocho Suplementar Sul', 'capacidade': 100},
        {'identificacao': 'Cocho Mineral 01', 'capacidade': 80},
        {'identificacao': 'Cocho Mineral 02', 'capacidade': 80},
        {'identificacao': 'Cocho Bezerros', 'capacidade': 50},
    ]

    cochos_criados = 0
    for cocho_data in cochos_data:
        try:
            Cocho.objects.get_or_create(
                identificacao=cocho_data['identificacao'],
                propriedade=propriedade,
                defaults={
                    'capacidade_kg': cocho_data['capacidade'],
                }
            )
            cochos_criados += 1
        except Exception as e:
            print(f"Erro cocho {cocho_data['identificacao']}: {e}")

    print(f"✅ Criadas {pastagens_criadas} pastagens + {cochos_criados} cochos")

def criar_patrimonio_realista(propriedade):
    """Cria patrimônio REALISTA para fazenda MS"""

    # Tipos de bem
    tipos_data = [
        {'nome': 'Tratores', 'categoria': 'MAQUINA', 'taxa_depreciacao': 10.00},
        {'nome': 'Colheitadeiras', 'categoria': 'MAQUINA', 'taxa_depreciacao': 12.00},
        {'nome': 'Veículos', 'categoria': 'VEICULO', 'taxa_depreciacao': 20.00},
        {'nome': 'Instalações', 'categoria': 'INSTALACAO', 'taxa_depreciacao': 5.00},
        {'nome': 'Equipamentos', 'categoria': 'EQUIPAMENTO', 'taxa_depreciacao': 15.00},
    ]

    tipos_bem = {}
    for tipo_data in tipos_data:
        try:
            tipo, created = TipoBem.objects.get_or_create(
                nome=tipo_data['nome'],
                categoria=tipo_data['categoria'],
                defaults={'taxa_depreciacao': Decimal(str(tipo_data['taxa_depreciacao']))}
            )
            tipos_bem[tipo_data['nome']] = tipo
        except Exception as e:
            print(f"Erro tipo bem {tipo_data['nome']}: {e}")

    # Bens patrimoniais realistas
    bens_data = [
        # Tratores
        {'descricao': 'Trator John Deere 6630', 'tipo': 'Tratores', 'valor': 380000.00, 'aquisicao': -1095},
        {'descricao': 'Trator Massey Ferguson 4292', 'tipo': 'Tratores', 'valor': 295000.00, 'aquisicao': -730},

        # Colheitadeiras
        {'descricao': 'Colheitadeira Case IH 5130', 'tipo': 'Colheitadeiras', 'valor': 850000.00, 'aquisicao': -1825},

        # Veículos
        {'descricao': 'Caminhão Ford Cargo 2429', 'tipo': 'Veículos', 'valor': 280000.00, 'aquisicao': -545},
        {'descricao': 'Pickup Toyota Hilux', 'tipo': 'Veículos', 'valor': 180000.00, 'aquisicao': -365},
        {'descricao': 'Moto Honda CG 160', 'tipo': 'Veículos', 'valor': 12000.00, 'aquisicao': -180},

        # Instalações
        {'descricao': 'Curral de Manejo Completo', 'tipo': 'Instalações', 'valor': 250000.00, 'aquisicao': -1095},
        {'descricao': 'Galpão de Máquinas', 'tipo': 'Instalações', 'valor': 150000.00, 'aquisicao': -1825},
        {'descricao': 'Casa Sede Reformada', 'tipo': 'Instalações', 'valor': 350000.00, 'aquisicao': -2555},

        # Equipamentos
        {'descricao': 'Pulverizador Jacto PJB-16', 'tipo': 'Equipamentos', 'valor': 120000.00, 'aquisicao': -365},
        {'descricao': 'Grade Aradora', 'tipo': 'Equipamentos', 'valor': 45000.00, 'aquisicao': -730},
        {'descricao': 'Semeadeira a Vácuo', 'tipo': 'Equipamentos', 'valor': 95000.00, 'aquisicao': -545},
        {'descricao': 'Carreta Graneleira', 'tipo': 'Equipamentos', 'valor': 75000.00, 'aquisicao': -365},
    ]

    bens_criados = 0
    for bem_data in bens_data:
        try:
            BemPatrimonial.objects.get_or_create(
                propriedade=propriedade,
                descricao=bem_data['descricao'],
                tipo_bem=tipos_bem[bem_data['tipo']],
                defaults={
                    'valor_aquisicao': Decimal(str(bem_data['valor'])),
                    'data_aquisicao': date.today() + timedelta(days=bem_data['aquisicao']),
                }
            )
            bens_criados += 1
        except Exception as e:
            print(f"Erro bem patrimonial {bem_data['descricao']}: {e}")

    print(f"✅ Criados {len(tipos_bem)} tipos de bem + {bens_criados} bens patrimoniais realistas")

if __name__ == '__main__':
    criar_dados_realistas_fazenda_demonstracao()
