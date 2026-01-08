#!/usr/bin/env python
"""
Script para popular a Fazenda Demonstração com dados completos em todos os módulos
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
    Propriedade, ProdutorRural, AnimalIndividual, CategoriaAnimal,
    CurralLote, InventarioRebanho
)
from gestao_rural.models_financeiro import (
    CategoriaFinanceira, ContaFinanceira, LancamentoFinanceiro
)
from gestao_rural.models_compras_financeiro import Fornecedor
from gestao_rural.models_funcionarios import Funcionario, FolhaPagamento
from gestao_rural.models_controles_operacionais import Pastagem, Cocho
from gestao_rural.models_patrimonio import TipoBem, BemPatrimonial

User = get_user_model()

def criar_dados_completos_fazenda_demonstracao():
    """Cria dados completos para a Fazenda Demonstração Ltda"""

    print("Procurando Fazenda Demonstracao Ltda...")
    try:
        propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
        if not propriedade:
            print("❌ Fazenda Demonstração não encontrada!")
            return

        print(f"Encontrada propriedade: {propriedade.nome_propriedade} (ID: {propriedade.id})")
        print(f"   Usuario: {propriedade.produtor.usuario_responsavel.username}")

        # 1. Criar dados de Pecuária
        print("\nPopulando modulo Pecuaria...")
        criar_dados_pecuaria(propriedade)

        # 2. Criar dados Financeiros
        print("\nPopulando modulo Financeiro...")
        criar_dados_financeiro(propriedade)

        # 3. Criar dados de Compras
        print("\nPopulando modulo Compras...")
        criar_dados_compras(propriedade)

        # 4. Criar dados de Funcionários
        print("\nPopulando modulo Funcionarios...")
        criar_dados_funcionarios(propriedade)

        # 5. Criar dados Operacionais
        print("\nPopulando modulo Operacional...")
        criar_dados_operacional(propriedade)

        # 6. Criar dados de Patrimônio
        print("\nPopulando modulo Patrimonio...")
        criar_dados_patrimonio(propriedade)

        print("\nFazenda Demonstracao Ltda populada com sucesso!")
        print("Todos os módulos têm dados para demonstração.")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

def criar_dados_pecuaria(propriedade):
    """Cria dados de pecuária"""
    try:
        # Criar categorias se não existirem
        categorias_data = [
            {'nome': 'Vaca em Lactação', 'sexo': 'F', 'idade_minima_meses': 24, 'raca': 'NELORE'},
            {'nome': 'Vaca Seca', 'sexo': 'F', 'idade_minima_meses': 24, 'raca': 'NELORE'},
            {'nome': 'Novilha', 'sexo': 'F', 'idade_minima_meses': 12, 'raca': 'NELORE'},
            {'nome': 'Bezerro', 'sexo': 'M', 'idade_minima_meses': 0, 'raca': 'NELORE'},
            {'nome': 'Bezerra', 'sexo': 'F', 'idade_minima_meses': 0, 'raca': 'NELORE'},
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

        # Criar animais
        animais_data = [
            # Vacas em Lactação
            {'categoria': 'Vaca em Lactação', 'numero_brinco': 'DEMO001', 'peso': 450},
            {'categoria': 'Vaca em Lactação', 'numero_brinco': 'DEMO002', 'peso': 420},
            {'categoria': 'Vaca em Lactação', 'numero_brinco': 'DEMO003', 'peso': 480},
            {'categoria': 'Vaca em Lactação', 'numero_brinco': 'DEMO004', 'peso': 460},
            {'categoria': 'Vaca em Lactação', 'numero_brinco': 'DEMO005', 'peso': 440},

            # Vacas Secas
            {'categoria': 'Vaca Seca', 'numero_brinco': 'DEMO006', 'peso': 430},
            {'categoria': 'Vaca Seca', 'numero_brinco': 'DEMO007', 'peso': 410},
            {'categoria': 'Vaca Seca', 'numero_brinco': 'DEMO008', 'peso': 450},

            # Novilhas
            {'categoria': 'Novilha', 'numero_brinco': 'DEMO009', 'peso': 320},
            {'categoria': 'Novilha', 'numero_brinco': 'DEMO010', 'peso': 340},
            {'categoria': 'Novilha', 'numero_brinco': 'DEMO011', 'peso': 310},

            # Bezerros/Bezerras
            {'categoria': 'Bezerro', 'numero_brinco': 'DEMO012', 'peso': 180},
            {'categoria': 'Bezerra', 'numero_brinco': 'DEMO013', 'peso': 170},
            {'categoria': 'Bezerro', 'numero_brinco': 'DEMO014', 'peso': 190},

            # Touro
            {'categoria': 'Touro', 'numero_brinco': 'DEMO015', 'peso': 800},
        ]

        for animal_data in animais_data:
            try:
                AnimalIndividual.objects.get_or_create(
                    numero_brinco=animal_data['numero_brinco'],
                    propriedade=propriedade,
                    defaults={
                        'categoria': categorias[animal_data['categoria']],
                        'peso_atual_kg': animal_data['peso'],
                        'sexo': categorias[animal_data['categoria']].sexo,
                        'raca': categorias[animal_data['categoria']].raca,
                        'data_nascimento': date.today() - timedelta(days=random.randint(365, 1825)),
                        'data_aquisicao': date.today() - timedelta(days=random.randint(30, 365)),
                        'status': 'ATIVO',
                    }
                )
            except Exception as e:
                print(f"Erro ao criar animal {animal_data['numero_brinco']}: {e}")

        # Criar inventário do rebanho
        try:
            InventarioRebanho.objects.get_or_create(
                propriedade=propriedade,
                data_inventario=date.today(),
                defaults={
                    'vacas_em_lactacao': 5,
                    'vacas_secas': 3,
                    'novilhas': 3,
                    'bezerros': 2,
                    'bezerras': 1,
                    'touros': 1,
                    'total_animais': 15,
                    'valor_por_cabeca': Decimal('2500.00'),
                    'valor_total_rebanho': Decimal('37500.00'),
                }
            )
        except Exception as e:
            print(f"Erro ao criar inventário: {e}")

        print(f"✅ Criados {len(animais_data)} animais e inventário do rebanho")

    except Exception as e:
        print(f"❌ Erro em criar_dados_pecuaria: {e}")

def criar_dados_financeiro(propriedade):
    """Cria dados financeiros"""
    try:
        # Criar categorias financeiras
        categorias = {}
        cats_data = [
            {'nome': 'Venda de Gado', 'tipo': 'RECEITA'},
            {'nome': 'Leite', 'tipo': 'RECEITA'},
            {'nome': 'Ração', 'tipo': 'DESPESA'},
            {'nome': 'Combustível', 'tipo': 'DESPESA'},
            {'nome': 'Salários', 'tipo': 'DESPESA'},
            {'nome': 'Manutenção', 'tipo': 'DESPESA'},
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
                print(f"Erro ao criar categoria {cat_data['nome']}: {e}")

        # Criar contas
        try:
            conta_banco, created = ContaFinanceira.objects.get_or_create(
                nome='Conta Corrente Banco XYZ',
                propriedade=propriedade,
                defaults={
                    'tipo': 'CORRENTE',
                    'banco': 'Banco XYZ',
                    'agencia': '1234',
                    'conta': '56789-0',
                    'saldo_inicial': Decimal('15000.00'),
                    'ativo': True,
                }
            )
        except Exception as e:
            print(f"Erro ao criar conta: {e}")
            return

        # Criar lançamentos financeiros
        lancamentos_data = [
            {'categoria': 'Venda de Gado', 'valor': 12500.00, 'tipo': 'CREDITO', 'conta': conta_banco},
            {'categoria': 'Ração', 'valor': 2500.00, 'tipo': 'DEBITO', 'conta': conta_banco},
            {'categoria': 'Combustível', 'valor': 800.00, 'tipo': 'DEBITO', 'conta': conta_banco},
            {'categoria': 'Salários', 'valor': 3500.00, 'tipo': 'DEBITO', 'conta': conta_banco},
            {'categoria': 'Manutenção', 'valor': 1200.00, 'tipo': 'DEBITO', 'conta': conta_banco},
            {'categoria': 'Leite', 'valor': 2800.00, 'tipo': 'CREDITO', 'conta': conta_banco},
        ]

        for i, lanc_data in enumerate(lancamentos_data):
            try:
                LancamentoFinanceiro.objects.get_or_create(
                    propriedade=propriedade,
                    categoria=categorias[lanc_data['categoria']],
                    descricao=f'Lançamento demo {i+1}',
                    valor=Decimal(str(lanc_data['valor'])),
                    data_competencia=date.today() - timedelta(days=i*7),
                    data_vencimento=date.today() - timedelta(days=i*7),
                    forma_pagamento='PIX',
                    status='QUITADO',
                    defaults={
                        'conta_origem' if lanc_data['tipo'] == 'DEBITO' else 'conta_destino': conta_banco,
                    }
                )
            except Exception as e:
                print(f"Erro ao criar lançamento {i+1}: {e}")

        print("✅ Criadas categorias, conta e lançamentos financeiros")

    except Exception as e:
        print(f"❌ Erro em criar_dados_financeiro: {e}")

def criar_dados_compras(propriedade):
    """Cria dados de compras e fornecedores"""
    try:
        # Criar fornecedores
        fornecedores_data = [
            {'nome': 'Nutripec Alimentos', 'cnpj': '12.345.678/0001-90', 'telefone': '(67) 99999-0001'},
            {'nome': 'Agro Maquinas LTDA', 'cnpj': '23.456.789/0001-80', 'telefone': '(67) 99999-0002'},
            {'nome': 'Posto Rural', 'cnpj': '34.567.890/0001-70', 'telefone': '(67) 99999-0003'},
            {'nome': 'Vet Agro Veterinária', 'cnpj': '45.678.901/0001-60', 'telefone': '(67) 99999-0004'},
        ]

        fornecedores = []
        for forn_data in fornecedores_data:
            try:
                forn, created = Fornecedor.objects.get_or_create(
                    nome=forn_data['nome'],
                    propriedade=propriedade,
                    defaults={
                        'cnpj': forn_data['cnpj'],
                        'telefone': forn_data['telefone'],
                        'ativo': True,
                    }
                )
                fornecedores.append(forn)
            except Exception as e:
                print(f"Erro ao criar fornecedor {forn_data['nome']}: {e}")

        print(f"✅ Criados {len(fornecedores)} fornecedores")

    except Exception as e:
        print(f"❌ Erro em criar_dados_compras: {e}")

def criar_dados_funcionarios(propriedade):
    """Cria dados de funcionários"""
    try:
        # Criar funcionários
        funcionarios_data = [
            {'nome': 'João Silva', 'cargo': 'Gerente', 'salario': 4500.00},
            {'nome': 'Maria Santos', 'cargo': 'Vaqueira', 'salario': 2200.00},
            {'nome': 'Pedro Oliveira', 'cargo': 'Capataz', 'salario': 3200.00},
            {'nome': 'Ana Costa', 'cargo': 'Veterinária', 'salario': 3800.00},
            {'nome': 'Carlos Lima', 'cargo': 'Mecânico', 'salario': 2800.00},
        ]

        for func_data in funcionarios_data:
            try:
                func, created = Funcionario.objects.get_or_create(
                    nome=func_data['nome'],
                    propriedade=propriedade,
                    defaults={
                        'cargo': func_data['cargo'],
                        'salario_base': Decimal(str(func_data['salario'])),
                        'ativo': True,
                    }
                )
            except Exception as e:
                print(f"Erro ao criar funcionário {func_data['nome']}: {e}")

        print(f"✅ Criados {len(funcionarios_data)} funcionários")

    except Exception as e:
        print(f"❌ Erro em criar_dados_funcionarios: {e}")

def criar_dados_operacional(propriedade):
    """Cria dados operacionais"""
    try:
        # Criar pastagens
        pastagens_data = [
            {'nome': 'Pastagem Norte', 'area_ha': 50.5, 'capacidade': 80},
            {'nome': 'Pastagem Sul', 'area_ha': 45.2, 'capacidade': 70},
            {'nome': 'Pastagem Leste', 'area_ha': 38.8, 'capacidade': 60},
        ]

        for past_data in pastagens_data:
            try:
                past, created = Pastagem.objects.get_or_create(
                    nome=past_data['nome'],
                    propriedade=propriedade,
                    defaults={
                        'area_hectares': Decimal(str(past_data['area_ha'])),
                        'capacidade_animais': past_data['capacidade'],
                        'status': 'ATIVA',
                    }
                )
            except Exception as e:
                print(f"Erro ao criar pastagem {past_data['nome']}: {e}")

        # Criar cochos
        cochos_data = [
            {'identificacao': 'Cocho 01', 'capacidade': 50},
            {'identificacao': 'Cocho 02', 'capacidade': 40},
            {'identificacao': 'Cocho 03', 'capacidade': 35},
            {'identificacao': 'Cocho 04', 'capacidade': 45},
        ]

        for cocho_data in cochos_data:
            try:
                cocho, created = Cocho.objects.get_or_create(
                    identificacao=cocho_data['identificacao'],
                    propriedade=propriedade,
                    defaults={
                        'capacidade_kg': cocho_data['capacidade'],
                        'status': 'ATIVO',
                    }
                )
            except Exception as e:
                print(f"Erro ao criar cocho {cocho_data['identificacao']}: {e}")

        print(f"✅ Criadas {len(pastagens_data)} pastagens e {len(cochos_data)} cochos")

    except Exception as e:
        print(f"❌ Erro em criar_dados_operacional: {e}")

def criar_dados_patrimonio(propriedade):
    """Cria dados de patrimônio"""
    try:
        # Criar tipos de bem
        tipos_data = [
            {'nome': 'Máquinas e Equipamentos', 'categoria': 'MAQUINA', 'taxa_depreciacao': 10.00},
            {'nome': 'Veículos', 'categoria': 'VEICULO', 'taxa_depreciacao': 20.00},
            {'nome': 'Instalações e Construções', 'categoria': 'INSTALACAO', 'taxa_depreciacao': 5.00},
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
                print(f"Erro ao criar tipo de bem {tipo_data['nome']}: {e}")

        # Criar bens patrimoniais
        bens_data = [
            {'descricao': 'Trator John Deere', 'tipo': 'Máquinas e Equipamentos', 'valor': 350000.00},
            {'descricao': 'Caminhão Ford', 'tipo': 'Veículos', 'valor': 180000.00},
            {'descricao': 'Curral de Manejo', 'tipo': 'Instalações e Construções', 'valor': 150000.00},
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
                        'status': 'ATIVO',
                    }
                )
            except Exception as e:
                print(f"Erro ao criar bem patrimonial {bem_data['descricao']}: {e}")

        print(f"✅ Criados tipos de bem e {len(bens_data)} bens patrimoniais")

    except Exception as e:
        print(f"❌ Erro em criar_dados_patrimonio: {e}")

if __name__ == '__main__':
    criar_dados_completos_fazenda_demonstracao()
