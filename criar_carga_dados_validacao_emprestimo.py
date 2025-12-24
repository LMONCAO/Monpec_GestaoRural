#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para criar carga de dados completa para validação de empréstimo de R$ 20 milhões
Inclui: Fornecedores, Clientes, Movimentações de Gado, Receitas, Despesas e DRE completo
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, date, timedelta
from random import randint, choice, uniform

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho,
    MovimentacaoProjetada, BemImobilizado
)
from gestao_rural.models_financeiro import (
    LancamentoFinanceiro, CategoriaFinanceira
)
from gestao_rural.models_cadastros import Cliente, FornecedorCadastro
from gestao_rural.models_financeiro import (
    ReceitaAnual, DespesaConfigurada, GrupoDespesa
)

# Valor do empréstimo solicitado
VALOR_EMPRESTIMO = Decimal('20000000.00')  # R$ 20 milhões

# Meta de cobertura (patrimônio deve ser pelo menos 2x o empréstimo)
META_COBERTURA_PATRIMONIAL = Decimal('40000000.00')  # R$ 40 milhões (200% de cobertura)

# Meta de receita anual (deve ser pelo menos 1.5x o empréstimo para boa cobertura)
META_RECEITA_ANUAL = Decimal('30000000.00')  # R$ 30 milhões (150% de cobertura)

# Meta de lucro líquido (margem de 15-20% sobre receita)
META_LUCRO_LIQUIDO = Decimal('4500000.00')  # R$ 4.5 milhões (15% de margem)


def calcular_necessidades():
    """Calcula quanto precisa de receita e despesas para validar o empréstimo"""
    print("=" * 80)
    print("ANÁLISE DE NECESSIDADES PARA VALIDAÇÃO DE EMPRÉSTIMO")
    print("=" * 80)
    print()
    print(f"Valor do Empréstimo: R$ {VALOR_EMPRESTIMO:,.2f}")
    print()
    
    # Cobertura Patrimonial
    print("1. COBERTURA PATRIMONIAL:")
    print(f"   Meta: R$ {META_COBERTURA_PATRIMONIAL:,.2f} (200% do empréstimo)")
    print(f"   - Rebanho: ~R$ {META_COBERTURA_PATRIMONIAL * Decimal('0.60'):,.2f} (60%)")
    print(f"   - Bens Imobilizados: ~R$ {META_COBERTURA_PATRIMONIAL * Decimal('0.40'):,.2f} (40%)")
    print()
    
    # Cobertura por Receitas
    print("2. COBERTURA POR RECEITAS:")
    print(f"   Meta: R$ {META_RECEITA_ANUAL:,.2f} (150% do empréstimo)")
    print(f"   - Receita Bruta: R$ {META_RECEITA_ANUAL:,.2f}")
    print(f"   - Deduções (15%): R$ {META_RECEITA_ANUAL * Decimal('0.15'):,.2f}")
    print(f"   - Receita Líquida: R$ {META_RECEITA_ANUAL * Decimal('0.85'):,.2f}")
    print()
    
    # Estrutura de Despesas (DRE)
    print("3. ESTRUTURA DE DESPESAS (DRE):")
    receita_liquida = META_RECEITA_ANUAL * Decimal('0.85')
    cpv = receita_liquida * Decimal('0.50')  # 50% da receita líquida
    lucro_bruto = receita_liquida - cpv
    despesas_operacionais = receita_liquida * Decimal('0.25')  # 25% da receita líquida
    resultado_operacional = lucro_bruto - despesas_operacionais
    despesas_financeiras = receita_liquida * Decimal('0.05')  # 5% da receita líquida
    lair = resultado_operacional - despesas_financeiras
    impostos = lair * Decimal('0.15')  # 15% de impostos
    lucro_liquido = lair - impostos
    
    print(f"   Receita Líquida: R$ {receita_liquida:,.2f}")
    print(f"   (-) CPV: R$ {cpv:,.2f} (50%)")
    print(f"   (=) Lucro Bruto: R$ {lucro_bruto:,.2f}")
    print(f"   (-) Despesas Operacionais: R$ {despesas_operacionais:,.2f} (25%)")
    print(f"   (=) Resultado Operacional: R$ {resultado_operacional:,.2f}")
    print(f"   (-) Despesas Financeiras: R$ {despesas_financeiras:,.2f} (5%)")
    print(f"   (=) LAIR: R$ {lair:,.2f}")
    print(f"   (-) Impostos (15%): R$ {impostos:,.2f}")
    print(f"   (=) Lucro Líquido: R$ {lucro_liquido:,.2f} ({lucro_liquido/receita_liquida*100:.1f}%)")
    print()
    
    # Indicadores
    print("4. INDICADORES FINANCEIROS:")
    cobertura_patrimonial = (META_COBERTURA_PATRIMONIAL / VALOR_EMPRESTIMO) * 100
    cobertura_receitas = (META_RECEITA_ANUAL / VALOR_EMPRESTIMO) * 100
    margem_lucro = (lucro_liquido / META_RECEITA_ANUAL) * 100
    
    print(f"   Cobertura Patrimonial: {cobertura_patrimonial:.1f}%")
    print(f"   Cobertura por Receitas: {cobertura_receitas:.1f}%")
    print(f"   Margem de Lucro: {margem_lucro:.1f}%")
    print()
    
    return {
        'receita_bruta': META_RECEITA_ANUAL,
        'receita_liquida': receita_liquida,
        'cpv': cpv,
        'lucro_bruto': lucro_bruto,
        'despesas_operacionais': despesas_operacionais,
        'despesas_financeiras': despesas_financeiras,
        'lucro_liquido': lucro_liquido,
        'patrimonio_necessario': META_COBERTURA_PATRIMONIAL,
    }


def criar_fornecedores_e_clientes(propriedades):
    """Cria fornecedores e clientes realistas"""
    print("=" * 80)
    print("CRIANDO FORNECEDORES E CLIENTES")
    print("=" * 80)
    print()
    
    # Fornecedores
    fornecedores_data = [
        {
            'nome': 'Agropecuária São Paulo Ltda',
            'cpf_cnpj': '12345678000190',
            'tipo': 'RAÇÃO',
            'telefone': '(11) 3456-7890',
            'email': 'vendas@agropecsp.com.br',
        },
        {
            'nome': 'Medicamentos Veterinários Brasil',
            'cpf_cnpj': '23456789000101',
            'tipo': 'MEDICAMENTOS',
            'telefone': '(11) 3456-7891',
            'email': 'contato@medvetbrasil.com.br',
        },
        {
            'nome': 'Máquinas Agrícolas do Sul',
            'cpf_cnpj': '34567890000112',
            'tipo': 'MAQUINAS',
            'telefone': '(11) 3456-7892',
            'email': 'vendas@maquinassul.com.br',
        },
        {
            'nome': 'Combustíveis e Lubrificantes Rural',
            'cpf_cnpj': '45678901000123',
            'tipo': 'COMBUSTIVEL',
            'telefone': '(11) 3456-7893',
            'email': 'pedidos@combustiveisrural.com.br',
        },
        {
            'nome': 'Sementes e Fertilizantes Premium',
            'cpf_cnpj': '56789012000134',
            'tipo': 'SEMENTES',
            'telefone': '(11) 3456-7894',
            'email': 'comercial@sementespremium.com.br',
        },
    ]
    
    fornecedores_criados = []
    for fornecedor_data in fornecedores_data:
        fornecedor, created = FornecedorCadastro.objects.get_or_create(
            cpf_cnpj=fornecedor_data['cpf_cnpj'],
            defaults={
                'nome': fornecedor_data['nome'],
                'telefone': fornecedor_data['telefone'],
                'email': fornecedor_data['email'],
                'cidade': 'São Paulo',
                'estado': 'SP',
            }
        )
        fornecedores_criados.append(fornecedor)
        if created:
            print(f"[OK] Fornecedor criado: {fornecedor.nome}")
        else:
            print(f"[OK] Fornecedor já existe: {fornecedor.nome}")
    
    print()
    
    # Clientes (Frigoríficos e compradores)
    clientes_data = [
        {
            'nome': 'Frigorífico JBS S.A.',
            'cpf_cnpj': '02916265000160',
            'tipo': 'FRIGORIFICO',
            'telefone': '(11) 3144-0000',
            'email': 'compras@jbs.com.br',
        },
        {
            'nome': 'Frigorífico Marfrig Global Foods',
            'cpf_cnpj': '14127666000150',
            'tipo': 'FRIGORIFICO',
            'telefone': '(11) 3144-1000',
            'email': 'compras@marfrig.com.br',
        },
        {
            'nome': 'Minerva Foods S.A.',
            'cpf_cnpj': '67743100000143',
            'tipo': 'FRIGORIFICO',
            'telefone': '(11) 3144-2000',
            'email': 'compras@minervafoods.com.br',
        },
        {
            'nome': 'Atacadista Carne Premium',
            'cpf_cnpj': '12345678000199',
            'tipo': 'ATACADISTA',
            'telefone': '(11) 3456-8000',
            'email': 'compras@atacadistacarne.com.br',
        },
        {
            'nome': 'Distribuidora Rural do Centro-Oeste',
            'cpf_cnpj': '23456789000188',
            'tipo': 'ATACADISTA',
            'telefone': '(11) 3456-8001',
            'email': 'vendas@distribuidorarural.com.br',
        },
    ]
    
    clientes_criados = []
    for cliente_data in clientes_data:
        cliente, created = Cliente.objects.get_or_create(
            cpf_cnpj=cliente_data['cpf_cnpj'],
            defaults={
                'nome': cliente_data['nome'],
                'tipo_cliente': cliente_data['tipo'],
                'tipo_pessoa': 'JURIDICA',
                'telefone': cliente_data['telefone'],
                'email': cliente_data['email'],
                'cidade': 'São Paulo',
                'estado': 'SP',
            }
        )
        clientes_criados.append(cliente)
        if created:
            print(f"[OK] Cliente criado: {cliente.nome}")
        else:
            print(f"[OK] Cliente já existe: {cliente.nome}")
    
    print()
    return fornecedores_criados, clientes_criados


def criar_movimentacoes_gado(propriedades, ano, necessidades):
    """Cria movimentações de gado (vendas) com valores realistas"""
    print("=" * 80)
    print(f"CRIANDO MOVIMENTAÇÕES DE GADO - ANO {ano}")
    print("=" * 80)
    print()
    
    # Buscar categorias
    categorias_venda = CategoriaAnimal.objects.filter(
        nome__icontains='Boi'
    ) | CategoriaAnimal.objects.filter(
        nome__icontains='Garrote'
    ) | CategoriaAnimal.objects.filter(
        nome__icontains='Bezerro'
    )
    
    # Calcular receita necessária de vendas de gado
    # Assumindo que 60% da receita vem de vendas de gado
    receita_vendas_gado = necessidades['receita_bruta'] * Decimal('0.60')
    
    # Distribuir vendas ao longo do ano (mais vendas no segundo semestre)
    meses_vendas = [
        (3, 0.05),   # Março: 5%
        (4, 0.05),   # Abril: 5%
        (5, 0.08),   # Maio: 8%
        (6, 0.10),   # Junho: 10%
        (7, 0.12),   # Julho: 12%
        (8, 0.15),   # Agosto: 15%
        (9, 0.15),   # Setembro: 15%
        (10, 0.12),  # Outubro: 12%
        (11, 0.10),  # Novembro: 10%
        (12, 0.08),  # Dezembro: 8%
    ]
    
    movimentacoes_criadas = []
    total_vendas = Decimal('0.00')
    
    for propriedade in propriedades:
        for mes, percentual in meses_vendas:
            # Calcular valor da venda do mês
            valor_venda_mes = receita_vendas_gado * Decimal(str(percentual)) / len(propriedades)
            
            # Escolher categoria aleatória
            categoria = choice(list(categorias_venda))
            
            # Calcular quantidade baseada no valor médio por cabeça
            valor_medio_cabeca = Decimal('4200.00')  # R$ 4.200 por cabeça (boi gordo)
            quantidade = int(valor_venda_mes / valor_medio_cabeca)
            
            if quantidade > 0:
                data_venda = date(ano, mes, 15)
                
                # Criar movimentação de venda
                movimentacao = MovimentacaoProjetada.objects.create(
                    propriedade=propriedade,
                    data_movimentacao=data_venda,
                    tipo_movimentacao='VENDA',
                    categoria=categoria,
                    quantidade=quantidade,
                    valor_por_cabeca=valor_medio_cabeca,
                    valor_total=valor_venda_mes,
                    observacao=f'Venda mensal - {categoria.nome}'
                )
                
                movimentacoes_criadas.append(movimentacao)
                total_vendas += valor_venda_mes
                print(f"[OK] Venda criada: {propriedade.nome_propriedade} - {quantidade} {categoria.nome} - R$ {valor_venda_mes:,.2f} ({mes}/{ano})")
    
    print()
    print(f"Total de vendas criadas: {len(movimentacoes_criadas)}")
    print(f"Valor total de vendas: R$ {total_vendas:,.2f}")
    print()
    
    return movimentacoes_criadas


def criar_receitas_e_despesas(propriedades, ano, necessidades, clientes):
    """Cria receitas e despesas mensais para validar DRE"""
    print("=" * 80)
    print(f"CRIANDO RECEITAS E DESPESAS - ANO {ano}")
    print("=" * 80)
    print()
    
    # Buscar ou criar categorias financeiras
    categoria_receita_vendas, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Vendas de Gado',
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        defaults={'descricao': 'Receita com vendas de gado'}
    )
    
    categoria_receita_outras, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Outras Receitas',
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        defaults={'descricao': 'Outras receitas operacionais'}
    )
    
    categoria_despesa_racao, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Ração e Alimentação',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Despesas com ração e alimentação do rebanho'}
    )
    
    categoria_despesa_medicamentos, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Medicamentos Veterinários',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Despesas com medicamentos e veterinários'}
    )
    
    categoria_despesa_manutencao, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Manutenção e Reparos',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Manutenção de máquinas e equipamentos'}
    )
    
    categoria_despesa_pessoal, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Pessoal e Encargos',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Salários e encargos sociais'}
    )
    
    # Distribuir receitas e despesas ao longo do ano
    receita_bruta_total = necessidades['receita_bruta']
    receita_por_propriedade = receita_bruta_total / len(propriedades)
    receita_mensal_por_propriedade = receita_por_propriedade / Decimal('12')
    
    # Despesas totais
    despesas_totais = necessidades['cpv'] + necessidades['despesas_operacionais']
    despesas_por_propriedade = despesas_totais / len(propriedades)
    despesas_mensais_por_propriedade = despesas_por_propriedade / Decimal('12')
    
    lancamentos_criados = []
    
    for propriedade in propriedades:
        print(f"Processando: {propriedade.nome_propriedade}")
        
        # Criar receitas mensais
        for mes in range(1, 13):
            data_competencia = date(ano, mes, 15)
            
            # Receita principal (vendas de gado)
            receita_vendas = receita_mensal_por_propriedade * Decimal('0.70')  # 70% vendas
            receita_outras = receita_mensal_por_propriedade * Decimal('0.30')  # 30% outras
            
            # Criar lançamentos de receita
            lancamento_vendas = LancamentoFinanceiro.objects.create(
                propriedade=propriedade,
                categoria=categoria_receita_vendas,
                tipo=CategoriaFinanceira.TIPO_RECEITA,
                descricao=f'Vendas de gado - {mes}/{ano}',
                valor=receita_vendas,
                data_competencia=data_competencia,
                data_vencimento=data_competencia,
                data_quitacao=data_competencia,
                status=LancamentoFinanceiro.STATUS_QUITADO,
            )
            lancamentos_criados.append(lancamento_vendas)
            
            if receita_outras > 0:
                lancamento_outras = LancamentoFinanceiro.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_receita_outras,
                    tipo=CategoriaFinanceira.TIPO_RECEITA,
                    descricao=f'Outras receitas - {mes}/{ano}',
                    valor=receita_outras,
                    data_competencia=data_competencia,
                    data_vencimento=data_competencia,
                    data_quitacao=data_competencia,
                    status=LancamentoFinanceiro.STATUS_QUITADO,
                )
                lancamentos_criados.append(lancamento_outras)
            
            # Criar despesas mensais
            despesa_racao = despesas_mensais_por_propriedade * Decimal('0.30')  # 30% ração
            despesa_medicamentos = despesas_mensais_por_propriedade * Decimal('0.20')  # 20% medicamentos
            despesa_manutencao = despesas_mensais_por_propriedade * Decimal('0.20')  # 20% manutenção
            despesa_pessoal = despesas_mensais_por_propriedade * Decimal('0.30')  # 30% pessoal
            
            # Criar lançamentos de despesa
            LancamentoFinanceiro.objects.create(
                propriedade=propriedade,
                categoria=categoria_despesa_racao,
                tipo=CategoriaFinanceira.TIPO_DESPESA,
                descricao=f'Ração e alimentação - {mes}/{ano}',
                valor=despesa_racao,
                data_competencia=data_competencia,
                data_vencimento=data_competencia,
                data_quitacao=data_competencia,
                status=LancamentoFinanceiro.STATUS_QUITADO,
            )
            
            LancamentoFinanceiro.objects.create(
                propriedade=propriedade,
                categoria=categoria_despesa_medicamentos,
                tipo=CategoriaFinanceira.TIPO_DESPESA,
                descricao=f'Medicamentos veterinários - {mes}/{ano}',
                valor=despesa_medicamentos,
                data_competencia=data_competencia,
                data_vencimento=data_competencia,
                data_quitacao=data_competencia,
                status=LancamentoFinanceiro.STATUS_QUITADO,
            )
            
            LancamentoFinanceiro.objects.create(
                propriedade=propriedade,
                categoria=categoria_despesa_manutencao,
                tipo=CategoriaFinanceira.TIPO_DESPESA,
                descricao=f'Manutenção e reparos - {mes}/{ano}',
                valor=despesa_manutencao,
                data_competencia=data_competencia,
                data_vencimento=data_competencia,
                data_quitacao=data_competencia,
                status=LancamentoFinanceiro.STATUS_QUITADO,
            )
            
            LancamentoFinanceiro.objects.create(
                propriedade=propriedade,
                categoria=categoria_despesa_pessoal,
                tipo=CategoriaFinanceira.TIPO_DESPESA,
                descricao=f'Pessoal e encargos - {mes}/{ano}',
                valor=despesa_pessoal,
                data_competencia=data_competencia,
                data_vencimento=data_competencia,
                data_quitacao=data_competencia,
                status=LancamentoFinanceiro.STATUS_QUITADO,
            )
        
        print(f"  [OK] Receitas e despesas criadas para {propriedade.nome_propriedade}")
    
    print()
    print(f"Total de lançamentos criados: {len(lancamentos_criados)}")
    print()
    
    return lancamentos_criados


def criar_receita_anual_dre(propriedades, ano, necessidades):
    """Cria ReceitaAnual com DRE completo conforme contabilidade brasileira"""
    print("=" * 80)
    print(f"CRIANDO RECEITA ANUAL E DRE - ANO {ano}")
    print("=" * 80)
    print()
    
    receita_por_propriedade = necessidades['receita_bruta'] / len(propriedades)
    
    for propriedade in propriedades:
        # Calcular deduções (15% da receita bruta)
        icms = receita_por_propriedade * Decimal('0.08')  # 8% ICMS
        funrural = receita_por_propriedade * Decimal('0.05')  # 5% Funrural
        outros_impostos = receita_por_propriedade * Decimal('0.02')  # 2% outros
        
        receita_liquida = receita_por_propriedade - icms - funrural - outros_impostos
        
        # CPV (50% da receita líquida)
        cpv = receita_liquida * Decimal('0.50')
        
        # Lucro bruto
        lucro_bruto = receita_liquida - cpv
        
        # Despesas operacionais (25% da receita líquida)
        despesas_operacionais = receita_liquida * Decimal('0.25')
        
        # Resultado operacional
        resultado_operacional = lucro_bruto - despesas_operacionais
        
        # Despesas financeiras (5% da receita líquida)
        despesas_financeiras = receita_liquida * Decimal('0.05')
        
        # LAIR
        lair = resultado_operacional - despesas_financeiras
        
        # Impostos (15% do LAIR)
        impostos = lair * Decimal('0.15')
        
        # Lucro líquido
        lucro_liquido = lair - impostos
        
        # Criar ReceitaAnual
        receita_anual, created = ReceitaAnual.objects.get_or_create(
            propriedade=propriedade,
            ano=ano,
            defaults={
                'valor_receita': receita_por_propriedade,
                'icms_vendas': icms,
                'funviral_vendas': funrural,
                'outros_impostos_vendas': outros_impostos,
                'custo_produtos_vendidos': cpv,
                'retirada_labore': despesas_operacionais * Decimal('0.20'),  # 20% das despesas operacionais
                'depreciacao_amortizacao': despesas_operacionais * Decimal('0.10'),  # 10%
                'despesas_financeiras': despesas_financeiras,
            }
        )
        
        if created:
            print(f"[OK] ReceitaAnual criada para {propriedade.nome_propriedade}")
            print(f"     Receita Bruta: R$ {receita_por_propriedade:,.2f}")
            print(f"     Receita Líquida: R$ {receita_liquida:,.2f}")
            print(f"     Lucro Líquido: R$ {lucro_liquido:,.2f}")
        else:
            print(f"[OK] ReceitaAnual já existe para {propriedade.nome_propriedade}")
    
    print()


def main():
    """Função principal"""
    print("=" * 80)
    print("CARGA DE DADOS PARA VALIDAÇÃO DE EMPRÉSTIMO")
    print("=" * 80)
    print()
    
    # 1. Calcular necessidades
    necessidades = calcular_necessidades()
    
    # 2. Buscar propriedades do Marcelo Sanguino
    produtor = ProdutorRural.objects.filter(nome__icontains='Marcelo Sanguino').first()
    if not produtor:
        print("[ERRO] Produtor Marcelo Sanguino não encontrado!")
        print("Execute primeiro: python configurar_propriedades_marcelo_sanguino.py")
        return
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    if not propriedades.exists():
        print("[ERRO] Nenhuma propriedade encontrada!")
        return
    
    print(f"[OK] Produtor encontrado: {produtor.nome}")
    print(f"[OK] Propriedades encontradas: {propriedades.count()}")
    for prop in propriedades:
        print(f"     - {prop.nome_propriedade}")
    print()
    
    # 3. Criar fornecedores e clientes
    fornecedores, clientes = criar_fornecedores_e_clientes(propriedades)
    
    # 4. Criar movimentações de gado
    ano = 2025
    movimentacoes = criar_movimentacoes_gado(propriedades, ano, necessidades)
    
    # 5. Criar receitas e despesas mensais
    lancamentos = criar_receitas_e_despesas(propriedades, ano, necessidades, clientes)
    
    # 6. Criar ReceitaAnual com DRE completo
    criar_receita_anual_dre(propriedades, ano, necessidades)
    
    print("=" * 80)
    print("[OK] CARGA DE DADOS CONCLUÍDA!")
    print("=" * 80)
    print()
    print("Resumo:")
    print(f"  - Fornecedores criados: {len(fornecedores)}")
    print(f"  - Clientes criados: {len(clientes)}")
    print(f"  - Movimentações de gado: {len(movimentacoes)}")
    print(f"  - Lançamentos financeiros: {len(lancamentos)}")
    print()
    print("Próximos passos:")
    print("  1. Acesse o relatório de empréstimo no sistema")
    print("  2. Verifique os indicadores de cobertura")
    print("  3. Valide o DRE completo")
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"[ERRO] Erro ao criar carga de dados: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

