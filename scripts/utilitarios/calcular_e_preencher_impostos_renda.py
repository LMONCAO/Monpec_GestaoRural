#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para calcular e preencher Impostos de Renda (IRPJ) para pessoa física
Baseado no lucro líquido anual
"""
import os
import sys
import django
from decimal import Decimal, ROUND_HALF_UP

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, ProdutorRural
from gestao_rural.models_financeiro import ReceitaAnual, LancamentoFinanceiro, CategoriaFinanceira

# Tabela progressiva de IR para Pessoa Física (2022-2025)
# Base de cálculo anual (lucro líquido)
TABELA_IR_PF = [
    {'faixa_inicio': Decimal('0.00'), 'faixa_fim': Decimal('22847.76'), 'aliquota': Decimal('0.00'), 'deducao': Decimal('0.00')},
    {'faixa_inicio': Decimal('22847.77'), 'faixa_fim': Decimal('33919.80'), 'aliquota': Decimal('7.50'), 'deducao': Decimal('1713.58')},
    {'faixa_inicio': Decimal('33919.81'), 'faixa_fim': Decimal('45012.60'), 'aliquota': Decimal('15.00'), 'deducao': Decimal('4257.57')},
    {'faixa_inicio': Decimal('45012.61'), 'faixa_fim': Decimal('55976.16'), 'aliquota': Decimal('22.50'), 'deducao': Decimal('7633.51')},
    {'faixa_inicio': Decimal('55976.17'), 'faixa_fim': Decimal('999999999.99'), 'aliquota': Decimal('27.50'), 'deducao': Decimal('10432.32')},
]


def calcular_ir_pessoa_fisica(lucro_liquido):
    """
    Calcula o Imposto de Renda para Pessoa Física baseado na tabela progressiva
    """
    if lucro_liquido <= 0:
        return Decimal('0.00')
    
    # Encontrar a faixa correspondente
    for faixa in TABELA_IR_PF:
        if faixa['faixa_inicio'] <= lucro_liquido <= faixa['faixa_fim']:
            # Calcular IR: (base * aliquota / 100) - deducao
            ir_calculado = (lucro_liquido * faixa['aliquota'] / Decimal('100')) - faixa['deducao']
            return max(Decimal('0.00'), ir_calculado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    # Se não encontrou faixa, usar a última (maior)
    ultima_faixa = TABELA_IR_PF[-1]
    ir_calculado = (lucro_liquido * ultima_faixa['aliquota'] / Decimal('100')) - ultima_faixa['deducao']
    return max(Decimal('0.00'), ir_calculado.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


def calcular_lucro_liquido_por_propriedade(propriedade, ano):
    """
    Calcula o lucro líquido de uma propriedade em um ano
    Baseado nas receitas e despesas do ano
    """
    # Receitas
    categoria_receita, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Vendas de Gado',
        tipo=CategoriaFinanceira.TIPO_RECEITA
    )
    
    receitas = LancamentoFinanceiro.objects.filter(
        propriedade=propriedade,
        categoria=categoria_receita,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        status=LancamentoFinanceiro.STATUS_QUITADO
    )
    total_receitas = sum(r.valor for r in receitas)
    
    # Despesas operacionais
    categoria_despesa, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Despesas Operacionais',
        tipo=CategoriaFinanceira.TIPO_DESPESA
    )
    
    despesas_operacionais = LancamentoFinanceiro.objects.filter(
        propriedade=propriedade,
        categoria=categoria_despesa,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        status=LancamentoFinanceiro.STATUS_QUITADO
    )
    total_despesas_operacionais = sum(d.valor for d in despesas_operacionais)
    
    # Pagamentos de financiamento (não são dedutíveis para IR)
    categoria_pagamento, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Pagamento de Financiamento',
        tipo=CategoriaFinanceira.TIPO_DESPESA
    )
    
    categoria_avalista, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Pagamento como Avalista',
        tipo=CategoriaFinanceira.TIPO_DESPESA
    )
    
    # Lucro líquido = Receitas - Despesas Operacionais
    # (Pagamentos de financiamento não são dedutíveis)
    lucro_liquido = total_receitas - total_despesas_operacionais
    
    return lucro_liquido


def calcular_ir_consolidado(propriedades, ano):
    """
    Calcula o IR consolidado de todas as propriedades
    """
    lucro_liquido_total = Decimal('0.00')
    
    for propriedade in propriedades:
        lucro_prop = calcular_lucro_liquido_por_propriedade(propriedade, ano)
        lucro_liquido_total += lucro_prop
    
    # Calcular IR sobre o lucro líquido total
    ir_total = calcular_ir_pessoa_fisica(lucro_liquido_total)
    
    return {
        'lucro_liquido_total': lucro_liquido_total,
        'ir_total': ir_total,
        'lucro_por_propriedade': {
            prop.nome_propriedade: calcular_lucro_liquido_por_propriedade(prop, ano)
            for prop in propriedades
        }
    }


def preencher_impostos_renda(propriedades, ano_inicio, ano_fim):
    """
    Preenche os impostos de renda nas Receitas Anuais
    """
    print("=" * 80)
    print("CALCULANDO E PREENCHENDO IMPOSTOS DE RENDA")
    print("=" * 80)
    print()
    
    for ano in range(ano_inicio, ano_fim + 1):
        print(f"ANO {ano}:")
        print("-" * 80)
        
        # Calcular IR consolidado
        ir_consolidado = calcular_ir_consolidado(propriedades, ano)
        
        print(f"  Lucro Líquido Total: R$ {ir_consolidado['lucro_liquido_total']:,.2f}")
        print(f"  IR Calculado: R$ {ir_consolidado['ir_total']:,.2f}")
        print()
        
        # Distribuir IR proporcionalmente entre as propriedades
        lucro_total = ir_consolidado['lucro_liquido_total']
        ir_total = ir_consolidado['ir_total']
        
        if lucro_total > 0:
            for propriedade in propriedades:
                lucro_prop = ir_consolidado['lucro_por_propriedade'][propriedade.nome_propriedade]
                percentual_prop = lucro_prop / lucro_total if lucro_total > 0 else Decimal('0.00')
                ir_prop = ir_total * percentual_prop
                
                # Atualizar ReceitaAnual
                receita_anual, created = ReceitaAnual.objects.get_or_create(
                    propriedade=propriedade,
                    ano=ano,
                    defaults={'valor_receita': Decimal('0.00')}
                )
                
                receita_anual.irpj = ir_prop.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                receita_anual.csll = Decimal('0.00')  # Pessoa física não paga CSLL
                receita_anual.save()
                
                print(f"  {propriedade.nome_propriedade}:")
                print(f"    Lucro Líquido: R$ {lucro_prop:,.2f}")
                print(f"    IR: R$ {ir_prop:,.2f} ({percentual_prop * 100:.2f}%)")
        else:
            # Se não há lucro, IR é zero
            for propriedade in propriedades:
                receita_anual, created = ReceitaAnual.objects.get_or_create(
                    propriedade=propriedade,
                    ano=ano,
                    defaults={'valor_receita': Decimal('0.00')}
                )
                receita_anual.irpj = Decimal('0.00')
                receita_anual.csll = Decimal('0.00')
                receita_anual.save()
        
        print()
    
    print("=" * 80)
    print("IMPOSTOS DE RENDA PREENCHIDOS!")
    print("=" * 80)


def main():
    """Função principal"""
    produtor = ProdutorRural.objects.filter(nome__icontains='Marcelo Sanguino').first()
    if not produtor:
        print("[ERRO] Produtor não encontrado!")
        return
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    ano_inicio = 2022
    ano_fim = 2025
    
    preencher_impostos_renda(propriedades, ano_inicio, ano_fim)
    
    print()
    print("Resumo da Tabela de IR Pessoa Física:")
    print("-" * 80)
    for faixa in TABELA_IR_PF:
        print(f"  Faixa: R$ {faixa['faixa_inicio']:,.2f} a R$ {faixa['faixa_fim']:,.2f}")
        print(f"    Alíquota: {faixa['aliquota']}% | Dedução: R$ {faixa['deducao']:,.2f}")
    print("=" * 80)


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"[ERRO] Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

