# -*- coding: utf-8 -*-
"""
Script para gerar despesas proporcionais baseadas nas receitas reais,
sem gerar receitas aleatórias.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from random import randint, choice, uniform, random
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum

from gestao_rural.models import Propriedade
from gestao_rural.models_financeiro import (
    CategoriaFinanceira, CentroCusto, ContaFinanceira, LancamentoFinanceiro
)
from gestao_rural.models_compras_financeiro import Fornecedor, NotaFiscal

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("GERAR DESPESAS PROPORCIONAIS BASEADAS NAS RECEITAS REAIS")
print("=" * 70)

# Buscar propriedade
propriedade = Propriedade.objects.first()
if not propriedade:
    print("ERRO: Nenhuma propriedade encontrada.")
    sys.exit(1)

print(f"\nPropriedade: {propriedade.nome_propriedade}")

# Calcular receitas reais de 2022
receitas_2022 = LancamentoFinanceiro.objects.filter(
    propriedade=propriedade,
    data_competencia__year=2022,
    tipo=CategoriaFinanceira.TIPO_RECEITA
).aggregate(total=Sum('valor'))['total'] or Decimal('0.00')

print(f"\nReceitas reais de 2022: R$ {receitas_2022:,.2f}")

if receitas_2022 == 0:
    print("\nERRO: Nenhuma receita encontrada para 2022.")
    print("Execute primeiro: python manage.py integrar_vendas_planejamento_financeiro --ano 2022")
    sys.exit(1)

# Calcular despesa média mensal (90% das receitas)
receita_media_mensal = receitas_2022 / 12
despesa_media_mensal = receita_media_mensal * Decimal('0.90')  # 90% das receitas

print(f"Receita media mensal: R$ {receita_media_mensal:,.2f}")
print(f"Despesa media mensal (90%%): R$ {despesa_media_mensal:,.2f}")

# Buscar/obter fornecedores, categorias, contas, centros de custo
# Se não existirem, criar básicos
fornecedores = list(Fornecedor.objects.filter(propriedade=propriedade))
if not fornecedores:
    print("\nCriando fornecedores básicos...")
    # Criar alguns fornecedores básicos
    fornecedores_basicos = [
        {'nome': 'Fornecedor Ração', 'tipo': 'RACAO'},
        {'nome': 'Fornecedor Medicamentos', 'tipo': 'MEDICAMENTO'},
        {'nome': 'Fornecedor Combustível', 'tipo': 'COMBUSTIVEL'},
        {'nome': 'Fornecedor Serviços', 'tipo': 'SERVICO'},
    ]
    for fb in fornecedores_basicos:
        fornecedor = Fornecedor.objects.create(
            propriedade=propriedade,
            nome=fb['nome'],
            tipo=fb['tipo'],
            telefone=f'(67) {randint(3000, 9999)}-{randint(1000, 9999)}',
        )
        fornecedores.append(fornecedor)
    print(f"[OK] {len(fornecedores)} fornecedores criados")

centros_custo = list(CentroCusto.objects.filter(propriedade=propriedade, ativo=True))
if not centros_custo:
    print("\nCriando centros de custo básicos...")
    centros_basicos = [
        'Alimentação',
        'Sanidade',
        'Reprodução',
        'Manejo',
        'Infraestrutura',
        'Administrativo',
    ]
    for nome in centros_basicos:
        centro = CentroCusto.objects.create(
            propriedade=propriedade,
            nome=nome,
            ativo=True,
        )
        centros_custo.append(centro)
    print(f"[OK] {len(centros_custo)} centros de custo criados")

categorias_despesas = list(CategoriaFinanceira.objects.filter(
    propriedade=propriedade,
    tipo=CategoriaFinanceira.TIPO_DESPESA,
    ativa=True
))
if not categorias_despesas:
    print("\nCriando categorias de despesa básicas...")
    categorias_basicas = [
        'Ração e Suplementos',
        'Medicamentos e Veterinário',
        'Combustível',
        'Serviços Terceirizados',
        'Manutenção de Equipamentos',
        'Mão de Obra',
        'Energia Elétrica',
        'Telefone e Internet',
    ]
    for nome in categorias_basicas:
        categoria = CategoriaFinanceira.objects.create(
            propriedade=propriedade,
            nome=nome,
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            ativa=True,
        )
        categorias_despesas.append(categoria)
    print(f"[OK] {len(categorias_despesas)} categorias criadas")

contas = list(ContaFinanceira.objects.filter(propriedade=propriedade, ativa=True))
if not contas:
    print("\nERRO: Nenhuma conta financeira encontrada.")
    print("Crie pelo menos uma conta financeira no sistema antes de continuar.")
    sys.exit(1)

print(f"\nFornecedores: {len(fornecedores)}")
print(f"Centros de custo: {len(centros_custo)}")
print(f"Categorias de despesa: {len(categorias_despesas)}")
print(f"Contas: {len(contas)}")

# Gerar despesas mensais
ano = 2022
total_despesas = Decimal('0.00')
lancamentos_criados = 0
notas_criadas = 0

print("\n" + "=" * 70)
print("GERANDO DESPESAS MENSais...")
print("=" * 70)

with transaction.atomic():
    for mes in range(1, 13):
        data_base = date(ano, mes, 1)
        ultimo_dia = (date(ano, mes + 1, 1) - timedelta(days=1)).day if mes < 12 else 31
        
        # Variação mensal: -20% a +30% para despesas
        variacao_despesa = uniform(0.80, 1.30)
        despesa_mes = despesa_media_mensal * Decimal(str(variacao_despesa))
        
        # Gerar 260-320 despesas por mês
        num_lancamentos = randint(260, 320)
        despesa_restante = despesa_mes
        
        for i in range(num_lancamentos):
            if i == num_lancamentos - 1:
                valor = despesa_restante
            else:
                percentual = uniform(0.001, 0.005)  # 0.1% a 0.5% por lançamento
                valor = despesa_mes * Decimal(str(percentual))
                despesa_restante -= valor
            
            dia = randint(1, ultimo_dia)
            data_competencia = date(ano, mes, dia)
            data_vencimento = data_competencia + timedelta(days=randint(0, 30))
            data_quitacao = data_vencimento + timedelta(days=randint(0, 10))
            
            categoria = choice(categorias_despesas)
            fornecedor = choice(fornecedores)
            
            # Criar nota fiscal (90% das despesas têm nota)
            nota = None
            numero_nota = None
            if random() > 0.1:
                numero_nota = f'{randint(1000, 9999)}{randint(100000, 999999)}'
                serie = '1'
                chave_acesso = ''.join([str(randint(0, 9)) for _ in range(44)])
                
                nota = NotaFiscal.objects.create(
                    propriedade=propriedade,
                    fornecedor=fornecedor,
                    tipo='ENTRADA',
                    numero=numero_nota,
                    serie=serie,
                    chave_acesso=chave_acesso,
                    data_emissao=data_competencia,
                    data_entrada=data_competencia,
                    valor_produtos=valor.quantize(Decimal('0.01')),
                    valor_total=valor.quantize(Decimal('0.01')),
                    status='AUTORIZADA',
                )
                notas_criadas += 1
            
            # Criar lançamento financeiro
            LancamentoFinanceiro.objects.create(
                propriedade=propriedade,
                categoria=categoria,
                centro_custo=choice(centros_custo) if random() > 0.3 else None,
                conta_origem=choice(contas),
                tipo=CategoriaFinanceira.TIPO_DESPESA,
                descricao=f'{categoria.nome} - {fornecedor.nome}',
                valor=valor.quantize(Decimal('0.01')),
                data_competencia=data_competencia,
                data_vencimento=data_vencimento,
                data_quitacao=data_quitacao,
                forma_pagamento=choice([
                    LancamentoFinanceiro.FORMA_PIX,
                    LancamentoFinanceiro.FORMA_BOLETO,
                    LancamentoFinanceiro.FORMA_TRANSFERENCIA,
                ]),
                status=LancamentoFinanceiro.STATUS_QUITADO,
                documento_referencia=f'NF {numero_nota}' if numero_nota else '',
            )
            lancamentos_criados += 1
            total_despesas += valor
        
        print(f'  Mes {mes:02d}/{ano}: Despesas R$ {despesa_mes:,.2f} ({num_lancamentos} lancamentos)')

print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
print(f"Lancamentos criados: {lancamentos_criados}")
print(f"Notas fiscais criadas: {notas_criadas}")
print(f"Total despesas: R$ {total_despesas:,.2f}")
print(f"Receitas reais: R$ {receitas_2022:,.2f}")
print(f"Saldo liquido: R$ {receitas_2022 - total_despesas:,.2f}")
print("=" * 70)

