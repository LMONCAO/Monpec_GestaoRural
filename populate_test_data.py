#!/usr/bin/env python
"""
Script para popular o sistema com dados de teste para análise
"""
import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User
from gestao_rural.models import *

def create_test_data():
    print("🚀 Iniciando criação de dados de teste...")
    
    # 1. Criar usuário se não existir
    user, created = User.objects.get_or_create(
        username='teste',
        defaults={
            'email': 'teste@exemplo.com',
            'first_name': 'Usuário',
            'last_name': 'Teste',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('123456')
        user.save()
        print("✅ Usuário de teste criado")
    else:
        print("✅ Usuário de teste já existe")
    
    # 2. Criar Produtor Rural
    produtor, created = ProdutorRural.objects.get_or_create(
        cpf_cnpj='12345678901',
        defaults={
            'nome': 'João Silva',
            'usuario_responsavel': user,
            'telefone': '(11) 99999-9999',
            'email': 'joao@fazenda.com',
            'endereco': 'Fazenda São José, Zona Rural',
            'anos_experiencia': 15
        }
    )
    print("✅ Produtor Rural criado")
    
    # 3. Criar Propriedade
    propriedade, created = Propriedade.objects.get_or_create(
        nome_propriedade='Fazenda São José',
        defaults={
            'produtor': produtor,
            'municipio': 'Ribeirão Preto',
            'uf': 'SP',
            'area_total_ha': Decimal('500.00'),
            'tipo_operacao': 'MISTA',
            'tipo_ciclo_pecuario': ['CICLO_COMPLETO'],
            'tipo_propriedade': 'PROPRIA',
            'valor_hectare_proprio': Decimal('15000.00')
        }
    )
    print("✅ Propriedade criada")
    
    # 4. Criar Categorias de Animais
    categorias_data = [
        {'nome': 'Vacas Adultas', 'sexo': 'F', 'idade_minima': 24, 'idade_maxima': 120},
        {'nome': 'Touros', 'sexo': 'M', 'idade_minima': 24, 'idade_maxima': 120},
        {'nome': 'Bezerras', 'sexo': 'F', 'idade_minima': 0, 'idade_maxima': 12},
        {'nome': 'Bezerros', 'sexo': 'M', 'idade_minima': 0, 'idade_maxima': 12},
        {'nome': 'Novilhas', 'sexo': 'F', 'idade_minima': 12, 'idade_maxima': 24},
        {'nome': 'Novilhos', 'sexo': 'M', 'idade_minima': 12, 'idade_maxima': 24},
    ]
    
    for cat_data in categorias_data:
        categoria, created = CategoriaAnimal.objects.get_or_create(
            nome=cat_data['nome'],
            defaults=cat_data
        )
        if created:
            print(f"✅ Categoria {categoria.nome} criada")
    
    # 5. Criar Inventário de Rebanho
    print("📊 Criando inventário de rebanho...")
    for categoria in CategoriaAnimal.objects.all():
        inventario, created = InventarioRebanho.objects.get_or_create(
            propriedade=propriedade,
            categoria=categoria,
            data_inventario=date.today(),
            defaults={
                'quantidade': random.randint(10, 100),
                'valor_por_cabeca': Decimal(str(random.uniform(800, 3000))).quantize(Decimal('0.01'))
            }
        )
        if created:
            inventario.valor_total = inventario.quantidade * inventario.valor_por_cabeca
            inventario.save()
    
    print("✅ Inventário de rebanho criado")
    
    # 6. Criar Parâmetros de Projeção
    print("📈 Criando parâmetros de projeção...")
    parametros, created = ParametrosProjecao.objects.get_or_create(
        propriedade=propriedade,
        defaults={
            'taxa_natalidade': Decimal('0.85'),
            'taxa_mortalidade_adultos': Decimal('0.03'),
            'taxa_mortalidade_bezerros': Decimal('0.08'),
            'taxa_descarte': Decimal('0.15'),
            'idade_primeira_cria': 36,
            'intervalo_partos': 14,
            'peso_medio_venda': Decimal('450.00'),
            'preco_medio_venda': Decimal('180.00'),
            'custo_manutencao_por_cabeca': Decimal('120.00')
        }
    )
    print("✅ Parâmetros de projeção criados")
    
    # 7. Criar Custos Fixos
    print("💰 Criando custos fixos...")
    custos_fixos_data = [
        {'nome_custo': 'Mão de Obra', 'valor_mensal': Decimal('5000.00'), 'tipo_custo': 'MAO_OBRA'},
        {'nome_custo': 'Aluguel de Pasto', 'valor_mensal': Decimal('2000.00'), 'tipo_custo': 'PASTAGEM'},
        {'nome_custo': 'Energia Elétrica', 'valor_mensal': Decimal('800.00'), 'tipo_custo': 'ENERGIA'},
        {'nome_custo': 'Combustível', 'valor_mensal': Decimal('1200.00'), 'tipo_custo': 'COMBUSTIVEL'},
        {'nome_custo': 'Manutenção', 'valor_mensal': Decimal('1500.00'), 'tipo_custo': 'MANUTENCAO'},
    ]
    
    for custo_data in custos_fixos_data:
        custo, created = CustoFixo.objects.get_or_create(
            propriedade=propriedade,
            nome_custo=custo_data['nome_custo'],
            defaults=custo_data
        )
        if created:
            print(f"✅ Custo fixo {custo.nome_custo} criado")
    
    # 8. Criar Custos Variáveis
    print("📊 Criando custos variáveis...")
    custos_variaveis_data = [
        {'nome_custo': 'Ração', 'tipo_custo': 'ALIMENTACAO', 'valor_por_cabeca': Decimal('45.00')},
        {'nome_custo': 'Medicamentos', 'tipo_custo': 'SANEAMENTO', 'valor_por_cabeca': Decimal('15.00')},
        {'nome_custo': 'Sementes', 'tipo_custo': 'PASTAGEM', 'valor_por_cabeca': Decimal('8.00')},
        {'nome_custo': 'Inseminação', 'tipo_custo': 'REPRODUCAO', 'valor_por_cabeca': Decimal('25.00')},
    ]
    
    for custo_data in custos_variaveis_data:
        custo, created = CustoVariavel.objects.get_or_create(
            propriedade=propriedade,
            nome_custo=custo_data['nome_custo'],
            defaults=custo_data
        )
        if created:
            print(f"✅ Custo variável {custo.nome_custo} criado")
    
    # 9. Criar Financiamentos
    print("🏦 Criando financiamentos...")
    financiamentos_data = [
        {
            'nome_financiamento': 'Financiamento Rural - Banco do Brasil',
            'valor_principal': Decimal('150000.00'),
            'taxa_juros_anual': Decimal('8.5'),
            'prazo_meses': 60,
            'data_inicio': date.today() - timedelta(days=30),
            'tipo_financiamento': 'RURAL'
        },
        {
            'nome_financiamento': 'Empréstimo Pessoal - Caixa',
            'valor_principal': Decimal('50000.00'),
            'taxa_juros_anual': Decimal('12.0'),
            'prazo_meses': 24,
            'data_inicio': date.today() - timedelta(days=15),
            'tipo_financiamento': 'PESSOAL'
        }
    ]
    
    for fin_data in financiamentos_data:
        financiamento, created = Financiamento.objects.get_or_create(
            propriedade=propriedade,
            nome_financiamento=fin_data['nome_financiamento'],
            defaults=fin_data
        )
        if created:
            print(f"✅ Financiamento {financiamento.nome_financiamento} criado")
    
    # 10. Criar Bens Patrimoniais
    print("🏠 Criando bens patrimoniais...")
    try:
        from gestao_rural.models_patrimonio import TipoBem, BemPatrimonial
        
        # Criar tipos de bens
        tipos_bens = [
            {'nome': 'Trator', 'categoria': 'MAQUINARIA', 'vida_util_anos': 10},
            {'nome': 'Cerca', 'categoria': 'INFRAESTRUTURA', 'vida_util_anos': 15},
            {'nome': 'Curral', 'categoria': 'INFRAESTRUTURA', 'vida_util_anos': 20},
            {'nome': 'Caminhão', 'categoria': 'VEICULO', 'vida_util_anos': 8},
        ]
        
        for tipo_data in tipos_bens:
            tipo, created = TipoBem.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults=tipo_data
            )
            if created:
                print(f"✅ Tipo de bem {tipo.nome} criado")
        
        # Criar bens patrimoniais
        bens_data = [
            {'tipo': 'Trator', 'descricao': 'Trator John Deere 6110J', 'valor_aquisicao': Decimal('85000.00'), 'data_aquisicao': date.today() - timedelta(days=365)},
            {'tipo': 'Cerca', 'descricao': 'Cerca elétrica 2km', 'valor_aquisicao': Decimal('12000.00'), 'data_aquisicao': date.today() - timedelta(days=180)},
            {'tipo': 'Curral', 'descricao': 'Curral de manejo', 'valor_aquisicao': Decimal('25000.00'), 'data_aquisicao': date.today() - timedelta(days=90)},
            {'tipo': 'Caminhão', 'descricao': 'Caminhão Ford Cargo', 'valor_aquisicao': Decimal('45000.00'), 'data_aquisicao': date.today() - timedelta(days=30)},
        ]
        
        for bem_data in bens_data:
            tipo_bem = TipoBem.objects.get(nome=bem_data['tipo'])
            bem, created = BemPatrimonial.objects.get_or_create(
                propriedade=propriedade,
                tipo=tipo_bem,
                descricao=bem_data['descricao'],
                defaults={
                    'valor_aquisicao': bem_data['valor_aquisicao'],
                    'data_aquisicao': bem_data['data_aquisicao']
                }
            )
            if created:
                print(f"✅ Bem patrimonial {bem.descricao} criado")
                
    except ImportError:
        print("⚠️ Módulo de patrimônio não encontrado, pulando...")
    
    # 11. Criar Projetos Bancários
    print("📋 Criando projetos bancários...")
    try:
        from gestao_rural.models_projetos import ProjetoBancario
        
        projetos_data = [
            {
                'nome_projeto': 'Expansão do Rebanho',
                'tipo_projeto': 'EXPANSAO_REBANHO',
                'banco_solicitado': 'Banco do Brasil',
                'valor_solicitado': Decimal('200000.00'),
                'prazo_pagamento': 60,
                'taxa_juros': Decimal('8.5'),
                'data_solicitacao': date.today() - timedelta(days=30),
                'status': 'EM_ANALISE'
            },
            {
                'nome_projeto': 'Modernização da Infraestrutura',
                'tipo_projeto': 'INFRAESTRUTURA',
                'banco_solicitado': 'Caixa Econômica',
                'valor_solicitado': Decimal('150000.00'),
                'prazo_pagamento': 48,
                'taxa_juros': Decimal('9.0'),
                'data_solicitacao': date.today() - timedelta(days=15),
                'status': 'APROVADO',
                'data_aprovacao': date.today() - timedelta(days=5),
                'valor_aprovado': Decimal('150000.00')
            }
        ]
        
        for proj_data in projetos_data:
            projeto, created = ProjetoBancario.objects.get_or_create(
                propriedade=propriedade,
                nome_projeto=proj_data['nome_projeto'],
                defaults=proj_data
            )
            if created:
                print(f"✅ Projeto bancário {projeto.nome_projeto} criado")
                
    except ImportError:
        print("⚠️ Módulo de projetos bancários não encontrado, pulando...")
    
    # 12. Criar Indicadores Financeiros
    print("📊 Criando indicadores financeiros...")
    indicadores_data = [
        {'nome': 'Receita Bruta Anual', 'valor': Decimal('450000.00'), 'tipo': 'RECEITA', 'ano': 2024},
        {'nome': 'Custos Operacionais', 'valor': Decimal('280000.00'), 'tipo': 'CUSTO', 'ano': 2024},
        {'nome': 'Lucro Líquido', 'valor': Decimal('170000.00'), 'tipo': 'LUCRO', 'ano': 2024},
        {'nome': 'Margem de Lucro', 'valor': Decimal('37.78'), 'tipo': 'PERCENTUAL', 'ano': 2024},
        {'nome': 'ROI', 'valor': Decimal('15.5'), 'tipo': 'PERCENTUAL', 'ano': 2024},
    ]
    
    for ind_data in indicadores_data:
        indicador, created = IndicadorFinanceiro.objects.get_or_create(
            propriedade=propriedade,
            nome=ind_data['nome'],
            ano=ind_data['ano'],
            defaults=ind_data
        )
        if created:
            print(f"✅ Indicador {indicador.nome} criado")
    
    # 13. Criar Movimentações Projetadas
    print("📅 Criando movimentações projetadas...")
    movimentacoes_data = [
        {
            'data_movimentacao': date.today() + timedelta(days=30),
            'tipo_movimentacao': 'VENDA',
            'categoria': CategoriaAnimal.objects.filter(sexo='M').first(),
            'quantidade': 15,
            'valor_por_cabeca': Decimal('1800.00')
        },
        {
            'data_movimentacao': date.today() + timedelta(days=60),
            'tipo_movimentacao': 'NASCIMENTO',
            'categoria': CategoriaAnimal.objects.filter(sexo='F').first(),
            'quantidade': 25,
            'valor_por_cabeca': Decimal('0.00')
        },
        {
            'data_movimentacao': date.today() + timedelta(days=90),
            'tipo_movimentacao': 'COMPRA',
            'categoria': CategoriaAnimal.objects.filter(sexo='F').first(),
            'quantidade': 10,
            'valor_por_cabeca': Decimal('2500.00')
        }
    ]
    
    for mov_data in movimentacoes_data:
        if mov_data['categoria']:
            movimentacao, created = MovimentacaoProjetada.objects.get_or_create(
                propriedade=propriedade,
                data_movimentacao=mov_data['data_movimentacao'],
                tipo_movimentacao=mov_data['tipo_movimentacao'],
                categoria=mov_data['categoria'],
                defaults={
                    'quantidade': mov_data['quantidade'],
                    'valor_por_cabeca': mov_data['valor_por_cabeca'],
                    'valor_total': mov_data['quantidade'] * mov_data['valor_por_cabeca']
                }
            )
            if created:
                print(f"✅ Movimentação {movimentacao.get_tipo_movimentacao_display()} criada")
    
    print("\n🎉 Dados de teste criados com sucesso!")
    print(f"📊 Propriedade: {propriedade.nome_propriedade}")
    print(f"👤 Produtor: {produtor.nome}")
    print(f"🔗 Acesse: http://localhost:8000/propriedade/{propriedade.id}/pecuaria/")
    
    return propriedade

if __name__ == '__main__':
    try:
        propriedade = create_test_data()
        print(f"\n✅ Sistema populado com dados de teste!")
        print(f"🌐 Acesse: http://localhost:8000/propriedade/{propriedade.id}/pecuaria/")
    except Exception as e:
        print(f"❌ Erro ao criar dados de teste: {e}")
        import traceback
        traceback.print_exc()












