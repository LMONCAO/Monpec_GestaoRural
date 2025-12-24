#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ajustar despesas para saldo líquido realista por ano
Faturamento: R$ 14-16 milhões/ano
Saldo Líquido desejado:
- 2022: R$ 1,7 milhões
- 2023: R$ 1,1 milhões
- 2024: R$ 1,4 milhões
- 2025: R$ 1,7 milhões
"""
import os
import sys
import django
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from random import uniform, randint

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade
from gestao_rural.models_financeiro import (
    LancamentoFinanceiro, CategoriaFinanceira, ReceitaAnual
)

# Faturamento total por ano
FATURAMENTO_TOTAL_ANUAL = {
    2022: Decimal('15000000.00'),  # R$ 15 milhões
    2023: Decimal('14000000.00'),  # R$ 14 milhões
    2024: Decimal('15000000.00'),  # R$ 15 milhões
    2025: Decimal('16000000.00'),  # R$ 16 milhões
}

# Saldo líquido desejado por ano
SALDO_LIQUIDO_ANUAL = {
    2022: Decimal('1700000.00'),  # R$ 1,7 milhões
    2023: Decimal('1100000.00'),  # R$ 1,1 milhões
    2024: Decimal('1400000.00'),  # R$ 1,4 milhões
    2025: Decimal('1700000.00'),  # R$ 1,7 milhões
}

NUM_PROPRIEDADES = 4


def gerar_valor_realista(valor_base, variacao_percentual=0.10):
    """Gera valor realista com centavos e variação"""
    fator_variacao = Decimal(str(uniform(1 - variacao_percentual, 1 + variacao_percentual)))
    valor_variado = valor_base * fator_variacao
    centavos_aleatorios = Decimal(str(randint(0, 99))) / Decimal('100')
    valor_final = valor_variado + centavos_aleatorios
    return valor_final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def ajustar_receitas_e_despesas(propriedades, ano_inicio, ano_fim):
    """Ajusta receitas e despesas para saldo líquido realista"""
    print("=" * 80)
    print("AJUSTANDO RECEITAS E DESPESAS - SALDO LÍQUIDO REALISTA")
    print("=" * 80)
    print()
    
    categoria_receita_vendas, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Vendas de Gado',
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        defaults={'descricao': 'Receita com vendas de gado'}
    )
    
    categoria_despesa_operacional, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Despesas Operacionais',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Despesas operacionais da propriedade'}
    )
    
    for ano in range(ano_inicio, ano_fim + 1):
        faturamento_total = FATURAMENTO_TOTAL_ANUAL.get(ano, FATURAMENTO_TOTAL_ANUAL[2022])
        saldo_liquido_desejado = SALDO_LIQUIDO_ANUAL.get(ano, SALDO_LIQUIDO_ANUAL[2022])
        
        # Calcular despesa total necessária
        despesa_total_necessaria = faturamento_total - saldo_liquido_desejado
        
        # Por propriedade
        receita_por_propriedade = faturamento_total / NUM_PROPRIEDADES
        despesa_por_propriedade = despesa_total_necessaria / NUM_PROPRIEDADES
        
        print(f"ANO {ano}:")
        print(f"  Faturamento Total: R$ {faturamento_total:,.2f}")
        print(f"  Despesa Total: R$ {despesa_total_necessaria:,.2f}")
        print(f"  Saldo Líquido: R$ {saldo_liquido_desejado:,.2f}")
        print(f"  Por Propriedade - Receita: R$ {receita_por_propriedade:,.2f}, Despesa: R$ {despesa_por_propriedade:,.2f}")
        print()
        
        for propriedade in propriedades:
            # ========== RECEITAS ==========
            receita_mensal_base = receita_por_propriedade / Decimal('12')
            valores_receita_mensais = []
            total_receita_calculado = Decimal('0.00')
            
            # Gerar valores mensais variados
            for mes in range(1, 13):
                if ano == ano_fim and mes > 10:
                    continue
                
                # Sazonalidade: 2º semestre 15% acima
                if mes >= 7:
                    fator_mes = Decimal('1.15')
                else:
                    fator_mes = Decimal('0.85')
                
                receita_mes_base = receita_mensal_base * fator_mes
                receita_mes = gerar_valor_realista(receita_mes_base, variacao_percentual=0.10)
                valores_receita_mensais.append((mes, receita_mes))
                total_receita_calculado += receita_mes
            
            # Ajustar proporcionalmente
            if total_receita_calculado > 0:
                fator_ajuste = receita_por_propriedade / total_receita_calculado
                valores_receita_mensais = [
                    (mes, (valor * fator_ajuste).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                    for mes, valor in valores_receita_mensais
                ]
            
            # Atualizar receitas
            total_receita_atualizado = Decimal('0.00')
            for mes, receita_mes in valores_receita_mensais:
                data_competencia = date(ano, mes, 15)
                
                lancamentos_mes = LancamentoFinanceiro.objects.filter(
                    propriedade=propriedade,
                    categoria=categoria_receita_vendas,
                    data_competencia__year=ano,
                    data_competencia__month=mes,
                    tipo=CategoriaFinanceira.TIPO_RECEITA
                )
                
                if lancamentos_mes.exists():
                    primeiro = lancamentos_mes.first()
                    primeiro.valor = receita_mes
                    primeiro.descricao = f'Vendas de gado - {mes:02d}/{ano}'
                    primeiro.save()
                    total_receita_atualizado += receita_mes
                else:
                    LancamentoFinanceiro.objects.create(
                        propriedade=propriedade,
                        categoria=categoria_receita_vendas,
                        tipo=CategoriaFinanceira.TIPO_RECEITA,
                        descricao=f'Vendas de gado - {mes:02d}/{ano}',
                        valor=receita_mes,
                        data_competencia=data_competencia,
                        data_vencimento=data_competencia,
                        data_quitacao=data_competencia,
                        status=LancamentoFinanceiro.STATUS_QUITADO,
                    )
                    total_receita_atualizado += receita_mes
            
            # ========== DESPESAS ==========
            despesa_mensal_base = despesa_por_propriedade / Decimal('12')
            valores_despesa_mensais = []
            total_despesa_calculado = Decimal('0.00')
            
            # Gerar valores mensais variados
            for mes in range(1, 13):
                if ano == ano_fim and mes > 10:
                    continue
                
                # Variação mensal (alguns meses maiores)
                if mes in [1, 2, 6, 7, 8]:  # Meses com mais despesas
                    fator_mes = Decimal('1.08')
                elif mes in [3, 4, 5]:
                    fator_mes = Decimal('1.00')
                else:
                    fator_mes = Decimal('0.92')
                
                despesa_mes_base = despesa_mensal_base * fator_mes
                despesa_mes = gerar_valor_realista(despesa_mes_base, variacao_percentual=0.12)
                valores_despesa_mensais.append((mes, despesa_mes))
                total_despesa_calculado += despesa_mes
            
            # Ajustar proporcionalmente
            if total_despesa_calculado > 0:
                fator_ajuste = despesa_por_propriedade / total_despesa_calculado
                valores_despesa_mensais = [
                    (mes, (valor * fator_ajuste).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                    for mes, valor in valores_despesa_mensais
                ]
            
            # Atualizar despesas
            total_despesa_atualizado = Decimal('0.00')
            for mes, despesa_mes in valores_despesa_mensais:
                data_competencia = date(ano, mes, 15)
                
                lancamentos_mes = LancamentoFinanceiro.objects.filter(
                    propriedade=propriedade,
                    categoria=categoria_despesa_operacional,
                    data_competencia__year=ano,
                    data_competencia__month=mes,
                    tipo=CategoriaFinanceira.TIPO_DESPESA
                )
                
                if lancamentos_mes.exists():
                    primeiro = lancamentos_mes.first()
                    primeiro.valor = despesa_mes
                    primeiro.descricao = f'Despesas operacionais - {mes:02d}/{ano}'
                    primeiro.save()
                    total_despesa_atualizado += despesa_mes
                else:
                    LancamentoFinanceiro.objects.create(
                        propriedade=propriedade,
                        categoria=categoria_despesa_operacional,
                        tipo=CategoriaFinanceira.TIPO_DESPESA,
                        descricao=f'Despesas operacionais - {mes:02d}/{ano}',
                        valor=despesa_mes,
                        data_competencia=data_competencia,
                        data_vencimento=data_competencia,
                        data_quitacao=data_competencia,
                        status=LancamentoFinanceiro.STATUS_QUITADO,
                    )
                    total_despesa_atualizado += despesa_mes
            
            # Calcular saldo líquido real
            saldo_liquido_real = total_receita_atualizado - total_despesa_atualizado
            
            print(f"  {propriedade.nome_propriedade}:")
            print(f"    Receita: R$ {total_receita_atualizado:,.2f}")
            print(f"    Despesa: R$ {total_despesa_atualizado:,.2f}")
            print(f"    Saldo Líquido: R$ {saldo_liquido_real:,.2f}")
            print()
    
    print("=" * 80)
    print("RECEITAS E DESPESAS AJUSTADAS!")
    print("=" * 80)


def atualizar_receitas_anuais_dre(propriedades, ano_inicio, ano_fim):
    """Atualiza ReceitaAnual com valores corretos para DRE"""
    print("=" * 80)
    print("ATUALIZANDO RECEITAS ANUAIS E DRE")
    print("=" * 80)
    print()
    
    from gestao_rural.models_financeiro import ReceitaAnual
    
    for ano in range(ano_inicio, ano_fim + 1):
        faturamento_total = FATURAMENTO_TOTAL_ANUAL.get(ano, FATURAMENTO_TOTAL_ANUAL[2022])
        saldo_liquido_desejado = SALDO_LIQUIDO_ANUAL.get(ano, SALDO_LIQUIDO_ANUAL[2022])
        receita_por_propriedade = faturamento_total / NUM_PROPRIEDADES
        
        # Deduções (15% da receita bruta)
        icms = receita_por_propriedade * Decimal('0.08')  # 8%
        funrural = receita_por_propriedade * Decimal('0.05')  # 5%
        outros_impostos = receita_por_propriedade * Decimal('0.02')  # 2%
        
        receita_liquida = receita_por_propriedade - icms - funrural - outros_impostos
        
        # CPV (50% da receita líquida)
        cpv = receita_liquida * Decimal('0.50')
        lucro_bruto = receita_liquida - cpv
        
        # Despesas operacionais (ajustadas para saldo líquido)
        despesas_operacionais = receita_liquida - cpv - (saldo_liquido_desejado / NUM_PROPRIEDADES)
        
        # Despesas financeiras (5% da receita líquida)
        despesas_financeiras = receita_liquida * Decimal('0.05')
        
        # Resultado antes de impostos
        resultado_antes_ir = lucro_bruto - despesas_operacionais - despesas_financeiras
        
        # Impostos (15% do resultado antes de impostos)
        impostos = resultado_antes_ir * Decimal('0.15')
        lucro_liquido = resultado_antes_ir - impostos
        
        for propriedade in propriedades:
            receita_anual, created = ReceitaAnual.objects.update_or_create(
                propriedade=propriedade,
                ano=ano,
                defaults={
                    'valor_receita': receita_por_propriedade,
                    'icms_vendas': icms,
                    'funviral_vendas': funrural,
                    'outros_impostos_vendas': outros_impostos,
                    'custo_produtos_vendidos': cpv,
                    'retirada_labore': despesas_operacionais * Decimal('0.20'),
                    'depreciacao_amortizacao': despesas_operacionais * Decimal('0.10'),
                    'despesas_financeiras': despesas_financeiras,
                    'csll': Decimal('0.00'),  # Pessoa física
                    'irpj': impostos,
                }
            )
            
            if not created:
                # Atualizar valores
                receita_anual.valor_receita = receita_por_propriedade
                receita_anual.icms_vendas = icms
                receita_anual.funviral_vendas = funrural
                receita_anual.outros_impostos_vendas = outros_impostos
                receita_anual.custo_produtos_vendidos = cpv
                receita_anual.retirada_labore = despesas_operacionais * Decimal('0.20')
                receita_anual.depreciacao_amortizacao = despesas_operacionais * Decimal('0.10')
                receita_anual.despesas_financeiras = despesas_financeiras
                receita_anual.csll = Decimal('0.00')
                receita_anual.irpj = impostos
                receita_anual.save()
            
            print(f"[OK] {ano}: {propriedade.nome_propriedade}")
            print(f"     Receita Bruta: R$ {receita_por_propriedade:,.2f}")
            print(f"     Lucro Líquido: R$ {lucro_liquido:,.2f}")
    
    print()


def calcular_capacidade_pagamento(propriedades, ano):
    """Calcula capacidade de pagamento para comprovação bancária"""
    print("=" * 80)
    print(f"CÁLCULO DE CAPACIDADE DE PAGAMENTO - ANO {ano}")
    print("=" * 80)
    print()
    
    from gestao_rural.models_financeiro import LancamentoFinanceiro
    from gestao_rural.models import SCRBancoCentral, DividaBanco
    
    # Receitas do ano
    receitas = LancamentoFinanceiro.objects.filter(
        propriedade__in=propriedades,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        status=LancamentoFinanceiro.STATUS_QUITADO
    )
    total_receitas = sum(r.valor for r in receitas)
    
    # Despesas do ano
    despesas = LancamentoFinanceiro.objects.filter(
        propriedade__in=propriedades,
        data_competencia__year=ano,
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        status=LancamentoFinanceiro.STATUS_QUITADO
    )
    total_despesas = sum(d.valor for d in despesas)
    
    # Saldo líquido
    saldo_liquido = total_receitas - total_despesas
    
    # Dívidas SCR
    produtor = propriedades.first().produtor if propriedades.exists() else None
    total_dividas = Decimal('0.00')
    if produtor:
        scr = SCRBancoCentral.objects.filter(produtor=produtor).order_by('-data_referencia_scr').first()
        if scr:
            dividas = DividaBanco.objects.filter(scr=scr)
            total_dividas = sum(d.valor_total for d in dividas)
    
    # Capacidade de pagamento
    capacidade_pagamento_anual = saldo_liquido
    capacidade_pagamento_mensal = capacidade_pagamento_anual / Decimal('12')
    
    # Cobertura de dívidas (anos para pagar)
    anos_para_pagar = total_dividas / capacidade_pagamento_anual if capacidade_pagamento_anual > 0 else Decimal('999')
    
    print(f"Receitas Totais: R$ {total_receitas:,.2f}")
    print(f"Despesas Totais: R$ {total_despesas:,.2f}")
    print(f"Saldo Líquido: R$ {saldo_liquido:,.2f}")
    print(f"Dívidas Totais (SCR): R$ {total_dividas:,.2f}")
    print()
    print(f"Capacidade de Pagamento Anual: R$ {capacidade_pagamento_anual:,.2f}")
    print(f"Capacidade de Pagamento Mensal: R$ {capacidade_pagamento_mensal:,.2f}")
    print(f"Anos para Pagar Dívidas: {anos_para_pagar:.1f} anos")
    print()
    
    # Indicadores de segurança
    if capacidade_pagamento_anual > 0:
        cobertura_dividas = (capacidade_pagamento_anual / total_dividas * 100) if total_dividas > 0 else 0
        print(f"Cobertura de Dívidas: {cobertura_dividas:.2f}%")
        print(f"Margem de Segurança: {'✅ BOA' if cobertura_dividas > 10 else '⚠️ ATENÇÃO' if cobertura_dividas > 5 else '❌ BAIXA'}")
    
    print("=" * 80)


def main():
    """Função principal"""
    from gestao_rural.models import ProdutorRural
    
    produtor = ProdutorRural.objects.filter(nome__icontains='Marcelo Sanguino').first()
    if not produtor:
        print("[ERRO] Produtor não encontrado!")
        return
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    ano_inicio = 2022
    ano_fim = 2025
    
    # 1. Ajustar receitas e despesas
    ajustar_receitas_e_despesas(propriedades, ano_inicio, ano_fim)
    
    # 2. Atualizar Receitas Anuais e DRE
    atualizar_receitas_anuais_dre(propriedades, ano_inicio, ano_fim)
    
    # 3. Calcular capacidade de pagamento para cada ano
    for ano in range(ano_inicio, ano_fim + 1):
        calcular_capacidade_pagamento(propriedades, ano)
    
    print("=" * 80)
    print("[OK] AJUSTE COMPLETO CONCLUÍDO!")
    print("=" * 80)
    print()
    print("Resumo dos Saldos Líquidos por Ano:")
    for ano, saldo in SALDO_LIQUIDO_ANUAL.items():
        print(f"  {ano}: R$ {saldo:,.2f}")
    print()
    print("✅ Dados ajustados para comprovação bancária")
    print("✅ Capacidade de pagamento calculada")
    print("✅ Valores realistas com centavos")
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

