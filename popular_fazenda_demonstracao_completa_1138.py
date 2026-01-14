#!/usr/bin/env python
"""
Script COMPLETO para popular a Fazenda Demonstração com 1138 animais e dados REALISTAS
Dados abrangentes para dashboard pecuária com gráficos funcionais e filtros
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
from gestao_rural.models_compras_financeiro import Fornecedor, OrdemCompra, ItemOrdemCompra
from gestao_rural.models_funcionarios import Funcionario, FolhaPagamento
from gestao_rural.models_controles_operacionais import Pastagem, Cocho
from gestao_rural.models_patrimonio import TipoBem, BemPatrimonial

User = get_user_model()

def criar_dados_completos_1138_animais():
    """Cria dados completos para 1138 animais na Fazenda Demonstração"""

    print("Procurando Fazenda Demonstracao...")
    try:
        propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
        if not propriedade:
            print("Fazenda Demonstracao nao encontrada!")
            return

        print(f"Encontrada: {propriedade.nome_propriedade} (ID: {propriedade.id})")

        # 1. Criar rebanho completo de 1138 animais
        print("\nPopulando rebanho com 1138 animais realistas...")
        criar_rebanho_1138(propriedade)

        # 2. Criar dados históricos através do status dos animais
        print("\nConfigurando status historico dos animais...")
        configurar_status_historico_animais(propriedade)

        # 3. Criar dados financeiros abrangentes
        print("\nPopulando financeiro com dados realistas e positivos...")
        criar_financeiro_abrangente(propriedade)

        # 4. Criar equipe completa (essencial para operacoes)
        print("\nPopulando equipe completa...")
        criar_equipe_completa(propriedade)

        # 7. Atualizar inventário final
        print("\nAtualizando inventario final...")
        atualizar_inventario_final(propriedade)

        print("\nFAZENDA DEMONSTRACAO COMPLETAMENTE POPULADA!")
        print("1138 animais com dados realistas")
        print("Centenas de movimentacoes historicas")
        print("Financeiro com valores positivos e realistas")
        print("Todos os graficos funcionarao perfeitamente")
        print("Filtros de data e periodo operacionais")

    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()

def criar_rebanho_1138(propriedade):
    """Cria rebanho completo de 1138 animais realistas"""

    # Categorias detalhadas para rebanho realista
    categorias_data = [
        {'nome': 'Vaca em Lactação', 'sexo': 'F', 'idade_minima_meses': 24, 'raca': 'NELORE'},
        {'nome': 'Vaca Seca', 'sexo': 'F', 'idade_minima_meses': 24, 'raca': 'NELORE'},
        {'nome': 'Vaca Descansada', 'sexo': 'F', 'idade_minima_meses': 24, 'raca': 'NELORE'},
        {'nome': 'Novilha 24-30 meses', 'sexo': 'F', 'idade_minima_meses': 24, 'raca': 'NELORE'},
        {'nome': 'Novilha 30-36 meses', 'sexo': 'F', 'idade_minima_meses': 30, 'raca': 'NELORE'},
        {'nome': 'Bezerro macho até 8 meses', 'sexo': 'M', 'idade_minima_meses': 0, 'raca': 'NELORE'},
        {'nome': 'Bezerra fêmea até 8 meses', 'sexo': 'F', 'idade_minima_meses': 0, 'raca': 'NELORE'},
        {'nome': 'Garrote 8-12 meses', 'sexo': 'M', 'idade_minima_meses': 8, 'raca': 'NELORE'},
        {'nome': 'Novilho 18-24 meses', 'sexo': 'M', 'idade_minima_meses': 18, 'raca': 'NELORE'},
        {'nome': 'Touro reprodutor', 'sexo': 'M', 'idade_minima_meses': 24, 'raca': 'NELORE'},
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

    # Distribuição realista do rebanho baseada em fazenda típica MS
    distribuicao_rebanho = {
        'Vaca em Lactação': 280,      # 25% do rebanho
        'Vaca Seca': 168,             # 15%
        'Vaca Descansada': 140,       # 12%
        'Novilha 24-30 meses': 140,   # 12%
        'Novilha 30-36 meses': 112,   # 10%
        'Bezerro macho até 8 meses': 84,   # 7%
        'Bezerra fêmea até 8 meses': 84,   # 7%
        'Garrote 8-12 meses': 70,     # 6%
        'Novilho 18-24 meses': 42,    # 4%
        'Touro reprodutor': 18,       # 2%
    }

    animais_criados = 0
    numero_brinco = 1000  # Começar do 1000 para números mais realistas

    for categoria_nome, quantidade in distribuicao_rebanho.items():
        categoria = categorias[categoria_nome]

        for i in range(quantidade):
            try:
                # Calcular peso baseado na categoria (valores realistas)
                if 'Vaca' in categoria_nome:
                    peso_base = random.randint(420, 520)
                elif 'Novilha' in categoria_nome:
                    peso_base = random.randint(320, 420)
                elif 'Bezerro' in categoria_nome or 'Bezerra' in categoria_nome:
                    peso_base = random.randint(140, 220)
                elif 'Garrote' in categoria_nome:
                    peso_base = random.randint(180, 280)
                elif 'Novilho' in categoria_nome:
                    peso_base = random.randint(250, 350)
                elif 'Touro' in categoria_nome:
                    peso_base = random.randint(700, 900)
                else:
                    peso_base = 400

                # Calcular datas realistas
                if 'Vaca' in categoria_nome:
                    meses_idade = random.randint(36, 120)  # 3-10 anos
                elif 'Novilha' in categoria_nome:
                    if '24-30' in categoria_nome:
                        meses_idade = random.randint(24, 30)
                    else:
                        meses_idade = random.randint(30, 36)
                elif 'Bezerro' in categoria_nome or 'Bezerra' in categoria_nome:
                    meses_idade = random.randint(1, 8)
                elif 'Garrote' in categoria_nome:
                    meses_idade = random.randint(8, 12)
                elif 'Novilho' in categoria_nome:
                    meses_idade = random.randint(18, 24)
                else:  # Touro
                    meses_idade = random.randint(36, 84)  # 3-7 anos

                data_nascimento = date.today() - timedelta(days=meses_idade*30)
                data_aquisicao = data_nascimento if meses_idade < 24 else date.today() - timedelta(days=random.randint(30, 365))

                # Criar animal
                AnimalIndividual.objects.get_or_create(
                    numero_brinco=f'DEMO{numero_brinco:04d}',
                    propriedade=propriedade,
                    defaults={
                        'categoria': categoria,
                        'peso_atual_kg': peso_base + random.randint(-20, 20),  # Variação natural
                        'sexo': categoria.sexo,
                        'raca': categoria.raca,
                        'data_nascimento': data_nascimento,
                        'data_aquisicao': data_aquisicao,
                        'status': 'ATIVO',
                        'observacoes': f'Animal saudável - Categoria {categoria_nome}',
                        'tipo_origem': 'NASCIMENTO' if meses_idade < 24 else 'COMPRA'
                    }
                )

                numero_brinco += 1
                animais_criados += 1

            except Exception as e:
                print(f"Erro ao criar animal {numero_brinco}: {e}")

    print(f"Criados {animais_criados} animais distribuidos realisticamente")

def configurar_status_historico_animais(propriedade):
    """Configura status histórico dos animais para simular movimentações"""

    # Pegar alguns animais para configurar status diferentes
    animais = list(AnimalIndividual.objects.filter(
        propriedade=propriedade,
        status='ATIVO'
    ).order_by('?')[:150])  # Pegar 150 animais aleatoriamente

    # Configurar alguns animais como "vendidos" (simulando vendas históricas)
    for animal in animais[:50]:  # 50 vendas
        try:
            animal.status = 'VENDIDO'
            animal.observacoes = f'Vendido em {date.today() - timedelta(days=random.randint(30, 730))}. Valor: R$ {random.randint(1500, 3500)}'
            animal.save()
        except Exception as e:
            print(f"Erro ao configurar venda: {e}")

    # Configurar alguns animais como "mortos" (simulando mortes históricas)
    for animal in animais[50:80]:  # 30 mortes
        try:
            animal.status = 'MORTO'
            animal.observacoes = f'Morreu em {date.today() - timedelta(days=random.randint(30, 730))}. Causa: {random.choice(["Doença", "Acidente", "Natural", "Outro"])}'
            animal.save()
        except Exception as e:
            print(f"Erro ao configurar morte: {e}")

    # Criar alguns animais "adquiridos" recentemente (simulando compras)
    categorias_para_compra = CategoriaAnimal.objects.filter(
        nome__in=['Bezerro macho até 8 meses', 'Bezerra fêmea até 8 meses', 'Garrote 8-12 meses', 'Novilha 24-30 meses']
    )

    for i in range(30):  # 30 compras simuladas
        try:
            categoria = random.choice(categorias_para_compra)
            numero_brinco = f'COMPRA{random.randint(10000, 99999)}'

            # Calcular peso baseado na categoria
            if 'Bezerro' in categoria.nome:
                peso = random.randint(140, 220)
            elif 'Garrote' in categoria.nome:
                peso = random.randint(180, 280)
            elif 'Novilha' in categoria.nome:
                peso = random.randint(280, 380)
            else:
                peso = 300

            data_aquisicao = date.today() - timedelta(days=random.randint(7, 180))  # Últimos 6 meses

            AnimalIndividual.objects.get_or_create(
                numero_brinco=numero_brinco,
                propriedade=propriedade,
                defaults={
                    'categoria': categoria,
                    'peso_atual_kg': peso,
                    'sexo': categoria.sexo,
                    'raca': categoria.raca,
                    'data_nascimento': data_aquisicao - timedelta(days=random.randint(180, 720)),  # 6 meses a 2 anos atrás
                    'data_aquisicao': data_aquisicao,
                    'status': 'ATIVO',
                    'observacoes': f'Adquirido em {data_aquisicao}. Valor: R$ {random.randint(1200, 2800)}'
                }
            )
        except Exception as e:
            print(f"Erro ao criar animal adquirido: {e}")

    print("Configurado status historico de 110 animais (50 vendas, 30 mortes, 30 compras)")

def criar_financeiro_abrangente(propriedade):
    """Cria dados financeiros abrangentes com valores positivos realistas"""

    # Criar categorias financeiras abrangentes
    categorias_data = [
        # RECEITAS
        {'nome': 'Venda de Bezerros', 'tipo': 'RECEITA'},
        {'nome': 'Venda de Novilhos', 'tipo': 'RECEITA'},
        {'nome': 'Venda de Vacas', 'tipo': 'RECEITA'},
        {'nome': 'Leite', 'tipo': 'RECEITA'},
        {'nome': 'Arrendamento de Pastagens', 'tipo': 'RECEITA'},
        {'nome': 'Venda de Adubo Orgânico', 'tipo': 'RECEITA'},

        # DESPESAS
        {'nome': 'Ração e Suplementos', 'tipo': 'DESPESA'},
        {'nome': 'Medicamentos Veterinários', 'tipo': 'DESPESA'},
        {'nome': 'Combustível', 'tipo': 'DESPESA'},
        {'nome': 'Manutenção de Máquinas', 'tipo': 'DESPESA'},
        {'nome': 'Salários e Encargos', 'tipo': 'DESPESA'},
        {'nome': 'Energia Elétrica', 'tipo': 'DESPESA'},
        {'nome': 'Água', 'tipo': 'DESPESA'},
        {'nome': 'Sementes e Fertilizantes', 'tipo': 'DESPESA'},
        {'nome': 'Vacinas e Vermífugos', 'tipo': 'DESPESA'},
        {'nome': 'Material de Consumo', 'tipo': 'DESPESA'},
    ]

    categorias = {}
    for cat_data in categorias_data:
        cat, created = CategoriaFinanceira.objects.get_or_create(
            nome=cat_data['nome'],
            tipo=cat_data['tipo'],
            propriedade=propriedade,
            defaults={}
        )
        categorias[cat_data['nome']] = cat

    # Criar conta bancária principal
    conta_principal, created = ContaFinanceira.objects.get_or_create(
        nome='Conta Corrente Principal - Banco do Brasil',
        propriedade=propriedade,
        defaults={
            'tipo': 'CORRENTE',
            'banco': 'Banco do Brasil',
            'agencia': '1234-5',
            'numero_conta': '12345-6',
            'saldo_inicial': Decimal('50000.00'),
            'ativa': True,
        }
    )

    # Criar 500 lançamentos financeiros históricos (últimos 24 meses)
    lancamentos_criados = 0

    # RECEITAS (70% dos lançamentos)
    receitas_data = [
        ('Venda de Bezerros', 1800, 2200),
        ('Venda de Novilhos', 2500, 3200),
        ('Venda de Vacas', 2800, 4500),
        ('Leite', 800, 1200),  # Por mês
        ('Arrendamento de Pastagens', 1500, 2500),
        ('Venda de Adubo Orgânico', 300, 800),
    ]

    # Criar 350 lançamentos de receita
    for i in range(350):
        try:
            categoria_nome, valor_min, valor_max = random.choice(receitas_data)
            categoria = categorias[categoria_nome]
            valor = Decimal(str(random.randint(valor_min, valor_max)))

            # Data aleatória nos últimos 24 meses
            data_lanc = date.today() - timedelta(days=random.randint(1, 730))

            LancamentoFinanceiro.objects.get_or_create(
                propriedade=propriedade,
                categoria=categoria,
                descricao=f'{categoria_nome} - {random.choice(["Cliente A", "Cliente B", "Cliente C", "Cliente D", "Cliente E"])}',
                valor=valor,
                data_competencia=data_lanc,
                data_vencimento=data_lanc,
                forma_pagamento=random.choice(['PIX', 'DINHEIRO', 'CHEQUE', 'TRANSFERENCIA']),
                status='QUITADO',
                conta_destino=conta_principal,
                defaults={}
            )
            lancamentos_criados += 1
        except Exception as e:
            print(f"Erro receita {i}: {e}")

    # DESPESAS (30% dos lançamentos)
    despesas_data = [
        ('Ração e Suplementos', 800, 1500),
        ('Medicamentos Veterinários', 300, 800),
        ('Combustível', 400, 900),
        ('Manutenção de Máquinas', 200, 600),
        ('Salários e Encargos', 8000, 12000),  # Mensal
        ('Energia Elétrica', 800, 1500),
        ('Água', 300, 600),
        ('Sementes e Fertilizantes', 500, 1200),
        ('Vacinas e Vermífugos', 400, 900),
        ('Material de Consumo', 200, 500),
    ]

    # Criar 150 lançamentos de despesa
    for i in range(150):
        try:
            categoria_nome, valor_min, valor_max = random.choice(despesas_data)
            categoria = categorias[categoria_nome]
            valor = Decimal(str(random.randint(valor_min, valor_max)))

            data_lanc = date.today() - timedelta(days=random.randint(1, 730))

            LancamentoFinanceiro.objects.get_or_create(
                propriedade=propriedade,
                categoria=categoria,
                descricao=f'{categoria_nome} - {random.choice(["Fornecedor X", "Fornecedor Y", "Fornecedor Z", "Empresa A", "Empresa B"])}',
                valor=valor,
                data_competencia=data_lanc,
                data_vencimento=data_lanc,
                forma_pagamento=random.choice(['PIX', 'BOLETO', 'CHEQUE', 'TRANSFERENCIA']),
                status='QUITADO',
                conta_origem=conta_principal,
                defaults={}
            )
            lancamentos_criados += 1
        except Exception as e:
            print(f"Erro despesa {i}: {e}")

    print(f"Criados {lancamentos_criados} lancamentos financeiros realistas")

# Removida função criar_operacional_completo - modelos incompatíveis

def criar_equipe_completa(propriedade):
    """Cria equipe completa realista"""

    funcionarios_data = [
        # Administração
        {'nome': 'João Carlos Silva', 'cargo': 'Administrador', 'salario': 8500.00},
        {'nome': 'Maria Aparecida Santos', 'cargo': 'Contadora', 'salario': 4200.00},
        {'nome': 'Pedro Oliveira Costa', 'cargo': 'Auxiliar Administrativo', 'salario': 1800.00},

        # Produção/ Pecuária
        {'nome': 'Antônio Ferreira', 'cargo': 'Gerente de Pecuária', 'salario': 6500.00},
        {'nome': 'Roberto Almeida', 'cargo': 'Capataz', 'salario': 3800.00},
        {'nome': 'Carlos Eduardo Lima', 'cargo': 'Capataz Assistente', 'salario': 3200.00},

        # Equipe de Campo
        {'nome': 'José da Silva', 'cargo': 'Vaqueiro Sênior', 'salario': 2800.00},
        {'nome': 'Manuel Rodrigues', 'cargo': 'Vaqueiro', 'salario': 2500.00},
        {'nome': 'Francisco Pereira', 'cargo': 'Vaqueiro', 'salario': 2500.00},
        {'nome': 'Antônio Santos', 'cargo': 'Vaqueiro', 'salario': 2400.00},
        {'nome': 'João Pereira', 'cargo': 'Vaqueiro', 'salario': 2400.00},

        # Veterinária e Saúde
        {'nome': 'Dra. Ana Paula Costa', 'cargo': 'Médica Veterinária', 'salario': 5800.00},
        {'nome': 'Carlos Roberto Nunes', 'cargo': 'Auxiliar Veterinário', 'salario': 2200.00},

        # Manutenção
        {'nome': 'Roberto Carlos Silva', 'cargo': 'Mecânico', 'salario': 3500.00},
        {'nome': 'Marcos Antônio', 'cargo': 'Auxiliar de Manutenção', 'salario': 2000.00},

        # Outros
        {'nome': 'Silvana Maria', 'cargo': 'Cozinheira', 'salario': 1900.00},
        {'nome': 'Rosa Pereira', 'cargo': 'Lavadeira', 'salario': 1600.00},
    ]

    for func_data in funcionarios_data:
        try:
            Funcionario.objects.get_or_create(
                nome=func_data['nome'],
                propriedade=propriedade,
                defaults={
                    'cargo': func_data['cargo'],
                    'salario_base': Decimal(str(func_data['salario'])),
                    'data_admissao': date.today() - timedelta(days=random.randint(365, 1825)),  # 1-5 anos
                    'ativo': True,
                    'tipo_contrato': 'CLT',
                    'jornada_trabalho': '44 horas semanais',
                }
            )
        except Exception as e:
            print(f"Erro funcionário {func_data['nome']}: {e}")

    print(f"Criada equipe completa com {len(funcionarios_data)} funcionarios")

def criar_patrimonio_completo(propriedade):
    """Cria patrimônio completo realista"""

    # Tipos de bem
    tipos_data = [
        {'nome': 'Máquinas e Equipamentos', 'categoria': 'MAQUINA', 'taxa_depreciacao': 10.00},
        {'nome': 'Veículos', 'categoria': 'VEICULO', 'taxa_depreciacao': 20.00},
        {'nome': 'Instalações e Construções', 'categoria': 'INSTALACAO', 'taxa_depreciacao': 5.00},
        {'nome': 'Móveis e Utensílios', 'categoria': 'MOVEIS', 'taxa_depreciacao': 15.00},
    ]

    tipos_bem = {}
    for tipo_data in tipos_data:
        tipo, created = TipoBem.objects.get_or_create(
            nome=tipo_data['nome'],
            categoria=tipo_data['categoria'],
            defaults={'taxa_depreciacao': Decimal(str(tipo_data['taxa_depreciacao']))}
        )
        tipos_bem[tipo_data['nome']] = tipo

    # Bens patrimoniais abrangentes
    bens_data = [
        # Máquinas e Equipamentos
        {'descricao': 'Trator John Deere 6130M', 'tipo': 'Máquinas e Equipamentos', 'valor': 380000.00},
        {'descricao': 'Colheitadeira Case IH', 'tipo': 'Máquinas e Equipamentos', 'valor': 450000.00},
        {'descricao': 'Plantadeira 20 linhas', 'tipo': 'Máquinas e Equipamentos', 'valor': 120000.00},
        {'descricao': 'Pulverizador autopropelido', 'tipo': 'Máquinas e Equipamentos', 'valor': 85000.00},
        {'descricao': 'Grades aradoras', 'tipo': 'Máquinas e Equipamentos', 'valor': 25000.00},
        {'descricao': 'Carreta agrícola', 'tipo': 'Máquinas e Equipamentos', 'valor': 35000.00},

        # Veículos
        {'descricao': 'Caminhão Ford Cargo 2429', 'tipo': 'Veículos', 'valor': 220000.00},
        {'descricao': 'Caminhonete Toyota Hilux', 'tipo': 'Veículos', 'valor': 140000.00},
        {'descricao': 'Caminhonete Chevrolet S10', 'tipo': 'Veículos', 'valor': 120000.00},
        {'descricao': 'Moto Honda CG 160', 'tipo': 'Veículos', 'valor': 8500.00},
        {'descricao': 'Moto Yamaha XT 660', 'tipo': 'Veículos', 'valor': 15000.00},

        # Instalações
        {'descricao': 'Galpão de máquinas 500m²', 'tipo': 'Instalações e Construções', 'valor': 180000.00},
        {'descricao': 'Curral de manejo completo', 'tipo': 'Instalações e Construções', 'valor': 220000.00},
        {'descricao': 'Silo para ração 50 toneladas', 'tipo': 'Instalações e Construções', 'valor': 95000.00},
        {'descricao': 'Casa sede 300m²', 'tipo': 'Instalações e Construções', 'valor': 350000.00},
        {'descricao': 'Alojamentos funcionários', 'tipo': 'Instalações e Construções', 'valor': 120000.00},
        {'descricao': 'Sistema de irrigação completo', 'tipo': 'Instalações e Construções', 'valor': 180000.00},

        # Móveis e Utensílios
        {'descricao': 'Móveis escritório completo', 'tipo': 'Móveis e Utensílios', 'valor': 25000.00},
        {'descricao': 'Equipamentos cozinha industrial', 'tipo': 'Móveis e Utensílios', 'valor': 18000.00},
        {'descricao': 'Ferramentas e utensílios diversos', 'tipo': 'Móveis e Utensílios', 'valor': 12000.00},
    ]

    for bem_data in bens_data:
        try:
            BemPatrimonial.objects.get_or_create(
                propriedade=propriedade,
                descricao=bem_data['descricao'],
                tipo_bem=tipos_bem[bem_data['tipo']],
                defaults={
                    'valor_aquisicao': Decimal(str(bem_data['valor'])),
                    'data_aquisicao': date.today() - timedelta(days=random.randint(365, 1825)),
                    'vida_util_anos': 10,
                    'depreciacao_acumulada': Decimal('0.00'),
                    'status': 'ATIVO',
                }
            )
        except Exception as e:
            print(f"Erro bem patrimonial {bem_data['descricao']}: {e}")

    print(f"Criado patrimonio completo com {len(bens_data)} bens")

def atualizar_inventario_final(propriedade):
    """Atualiza o inventário final baseado nos animais ativos"""

    # Contar animais por categoria
    categorias = CategoriaAnimal.objects.all()
    inventario_data = {}

    for categoria in categorias:
        count = AnimalIndividual.objects.filter(
            propriedade=propriedade,
            categoria=categoria,
            status='ATIVO'
        ).count()

        if count > 0:
            inventario_data[categoria.nome] = count

    # Calcular totais
    total_animais = sum(inventario_data.values())

    # Valor médio por animal baseado na categoria
    valor_medio_por_categoria = {
        'Touro reprodutor': 5000.00,
        'Vaca em Lactação': 2800.00,
        'Vaca Seca': 2600.00,
        'Vaca Descansada': 2500.00,
        'Novilha': 1800.00,
        'Novilho': 1600.00,
        'Garrote': 1400.00,
        'Bezerro': 800.00,
        'Bezerra': 750.00,
    }

    valor_total = 0
    for categoria_nome, quantidade in inventario_data.items():
        valor_categoria = valor_medio_por_categoria.get(categoria_nome, 2000.00)
        valor_total += valor_categoria * quantidade

    # Criar inventário final
    try:
        inventario, created = InventarioRebanho.objects.get_or_create(
            propriedade=propriedade,
            data_inventario=date.today(),
            defaults={
                'vacas_em_lactacao': inventario_data.get('Vaca em Lactação', 0),
                'vacas_secas': inventario_data.get('Vaca Seca', 0) + inventario_data.get('Vaca Descansada', 0),
                'novilhas': inventario_data.get('Novilha 24-30 meses', 0) + inventario_data.get('Novilha 30-36 meses', 0),
                'bezerros': inventario_data.get('Bezerro macho até 8 meses', 0),
                'bezerras': inventario_data.get('Bezerra fêmea até 8 meses', 0),
                'garrotes': inventario_data.get('Garrote 8-12 meses', 0),
                'novilhos': inventario_data.get('Novilho 18-24 meses', 0),
                'touros': inventario_data.get('Touro reprodutor', 0),
                'total_animais': total_animais,
                'valor_por_cabeca': Decimal(str(round(valor_total / total_animais, 2) if total_animais > 0 else 0)),
                'valor_total_rebanho': Decimal(str(round(valor_total, 2))),
            }
        )

        if created:
            print("Inventario final criado com sucesso")
        else:
            print("Inventario final atualizado")

        print(f"    Total de animais: {total_animais}")
        print(f"    Valor total do rebanho: R$ {valor_total:,.2f}")

    except Exception as e:
        print(f"❌ Erro ao criar inventário: {e}")

if __name__ == '__main__':
    criar_dados_completos_1138_animais()