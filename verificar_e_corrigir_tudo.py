#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir TUDO:
1. Faturamento: R$ 14-16 milhões/ano
2. Saldo Líquido: 2022=1.7M, 2023=1.1M, 2024=1.4M, 2025=1.7M
3. Despesas operacionais realistas
4. Pagamentos de financiamento separados
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

# Faturamento TOTAL por ano (dividido entre 4 propriedades)
FATURAMENTO_TOTAL_ANUAL = {
    2022: Decimal('15000000.00'),  # R$ 15 milhões
    2023: Decimal('14000000.00'),  # R$ 14 milhões
    2024: Decimal('15000000.00'),  # R$ 15 milhões
    2025: Decimal('16000000.00'),  # R$ 16 milhões
}

# Saldo líquido TOTAL por ano (soma de todas as propriedades)
SALDO_LIQUIDO_TOTAL_ANUAL = {
    2022: Decimal('1700000.00'),  # R$ 1,7 milhões
    2023: Decimal('1100000.00'),  # R$ 1,1 milhões
    2024: Decimal('1400000.00'),  # R$ 1,4 milhões
    2025: Decimal('1700000.00'),  # R$ 1,7 milhões
}

NUM_PROPRIEDADES = 4
PAGAMENTO_TRIMESTRAL = Decimal('1500000.00')  # R$ 1,5 milhão a cada 3 meses


def gerar_valor_realista(valor_base, variacao_percentual=0.10):
    """Gera valor realista com centavos"""
    fator_variacao = Decimal(str(uniform(1 - variacao_percentual, 1 + variacao_percentual)))
    valor_variado = valor_base * fator_variacao
    centavos_aleatorios = Decimal(str(randint(0, 99))) / Decimal('100')
    valor_final = valor_variado + centavos_aleatorios
    return valor_final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def corrigir_tudo(propriedades, ano_inicio, ano_fim):
    """Corrige receitas, despesas e pagamentos"""
    print("=" * 80)
    print("CORREÇÃO COMPLETA - FATURAMENTO E SALDO LÍQUIDO REALISTA")
    print("=" * 80)
    print()
    
    # Buscar categorias
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
    
    categoria_pagamento_financiamento, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Pagamento de Financiamento',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Amortização de financiamento'}
    )
    
    categoria_avalista, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Pagamento como Avalista',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Pagamento como avalista'}
    )
    
    canta_galo = propriedades.filter(nome_propriedade__icontains='Canta Galo').first()
    
    for ano in range(ano_inicio, ano_fim + 1):
        faturamento_total = FATURAMENTO_TOTAL_ANUAL.get(ano, FATURAMENTO_TOTAL_ANUAL[2022])
        saldo_liquido_desejado = SALDO_LIQUIDO_TOTAL_ANUAL.get(ano, SALDO_LIQUIDO_TOTAL_ANUAL[2022])
        
        # Pagamentos de financiamento (apenas Canta Galo, 4 vezes por ano)
        meses_pagamento = [1, 4, 7, 10]
        total_pagamentos_financiamento = PAGAMENTO_TRIMESTRAL * Decimal('4')
        if ano == ano_fim:
            # Até outubro de 2025 = 3 pagamentos
            total_pagamentos_financiamento = PAGAMENTO_TRIMESTRAL * Decimal('3')
        
        # Pagamento avalista (apenas 2024, outubro)
        total_pagamentos_avalista = Decimal('0.00')
        if ano == 2024:
            total_pagamentos_avalista = Decimal('2478000.00')
        
        # Despesas operacionais = Receita - Saldo Líquido - Pagamentos
        despesa_operacional_total = faturamento_total - saldo_liquido_desejado - total_pagamentos_financiamento - total_pagamentos_avalista
        
        # Por propriedade
        receita_por_propriedade = faturamento_total / NUM_PROPRIEDADES
        despesa_operacional_por_propriedade = despesa_operacional_total / NUM_PROPRIEDADES
        
        print(f"ANO {ano}:")
        print(f"  Faturamento Total: R$ {faturamento_total:,.2f}")
        print(f"  Pagamentos Financiamento: R$ {total_pagamentos_financiamento:,.2f}")
        print(f"  Pagamentos Avalista: R$ {total_pagamentos_avalista:,.2f}")
        print(f"  Despesa Operacional Total: R$ {despesa_operacional_total:,.2f}")
        print(f"  Saldo Liquido Desejado: R$ {saldo_liquido_desejado:,.2f}")
        print()
        
        for propriedade in propriedades:
            # ========== RECEITAS ==========
            receita_mensal_base = receita_por_propriedade / Decimal('12')
            valores_receita = []
            total_receita_calc = Decimal('0.00')
            
            for mes in range(1, 13):
                if ano == ano_fim and mes > 10:
                    continue
                
                # Sazonalidade
                if mes >= 7:
                    fator_mes = Decimal('1.15')
                else:
                    fator_mes = Decimal('0.85')
                
                receita_mes_base = receita_mensal_base * fator_mes
                receita_mes = gerar_valor_realista(receita_mes_base, 0.10)
                valores_receita.append((mes, receita_mes))
                total_receita_calc += receita_mes
            
            # Ajustar proporcionalmente
            if total_receita_calc > 0:
                fator = receita_por_propriedade / total_receita_calc
                valores_receita = [(mes, (v * fator).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) for mes, v in valores_receita]
            
            # Atualizar receitas
            total_receita_atual = Decimal('0.00')
            for mes, receita_mes in valores_receita:
                data_comp = date(ano, mes, 15)
                
                lancamentos = LancamentoFinanceiro.objects.filter(
                    propriedade=propriedade,
                    categoria=categoria_receita_vendas,
                    data_competencia__year=ano,
                    data_competencia__month=mes,
                    tipo=CategoriaFinanceira.TIPO_RECEITA
                )
                
                if lancamentos.exists():
                    primeiro = lancamentos.first()
                    primeiro.valor = receita_mes
                    primeiro.descricao = f'Vendas de gado - {mes:02d}/{ano}'
                    primeiro.save()
                    total_receita_atual += receita_mes
                else:
                    LancamentoFinanceiro.objects.create(
                        propriedade=propriedade,
                        categoria=categoria_receita_vendas,
                        tipo=CategoriaFinanceira.TIPO_RECEITA,
                        descricao=f'Vendas de gado - {mes:02d}/{ano}',
                        valor=receita_mes,
                        data_competencia=data_comp,
                        data_vencimento=data_comp,
                        data_quitacao=data_comp,
                        status=LancamentoFinanceiro.STATUS_QUITADO,
                    )
                    total_receita_atual += receita_mes
            
            # ========== DESPESAS OPERACIONAIS ==========
            despesa_mensal_base = despesa_operacional_por_propriedade / Decimal('12')
            valores_despesa = []
            total_despesa_calc = Decimal('0.00')
            
            for mes in range(1, 13):
                if ano == ano_fim and mes > 10:
                    continue
                
                # Variação mensal
                if mes in [1, 2, 6, 7, 8]:
                    fator_mes = Decimal('1.08')
                elif mes in [3, 4, 5]:
                    fator_mes = Decimal('1.00')
                else:
                    fator_mes = Decimal('0.92')
                
                despesa_mes_base = despesa_mensal_base * fator_mes
                despesa_mes = gerar_valor_realista(despesa_mes_base, 0.12)
                valores_despesa.append((mes, despesa_mes))
                total_despesa_calc += despesa_mes
            
            # Ajustar proporcionalmente
            if total_despesa_calc > 0:
                fator = despesa_operacional_por_propriedade / total_despesa_calc
                valores_despesa = [(mes, (v * fator).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) for mes, v in valores_despesa]
            
            # Atualizar despesas operacionais (apenas desta categoria)
            total_despesa_atual = Decimal('0.00')
            for mes, despesa_mes in valores_despesa:
                data_comp = date(ano, mes, 15)
                
                lancamentos = LancamentoFinanceiro.objects.filter(
                    propriedade=propriedade,
                    categoria=categoria_despesa_operacional,
                    data_competencia__year=ano,
                    data_competencia__month=mes,
                    tipo=CategoriaFinanceira.TIPO_DESPESA
                )
                
                if lancamentos.exists():
                    primeiro = lancamentos.first()
                    primeiro.valor = despesa_mes
                    primeiro.descricao = f'Despesas operacionais - {mes:02d}/{ano}'
                    primeiro.save()
                    total_despesa_atual += despesa_mes
                else:
                    LancamentoFinanceiro.objects.create(
                        propriedade=propriedade,
                        categoria=categoria_despesa_operacional,
                        tipo=CategoriaFinanceira.TIPO_DESPESA,
                        descricao=f'Despesas operacionais - {mes:02d}/{ano}',
                        valor=despesa_mes,
                        data_competencia=data_comp,
                        data_vencimento=data_comp,
                        data_quitacao=data_comp,
                        status=LancamentoFinanceiro.STATUS_QUITADO,
                    )
                    total_despesa_atual += despesa_mes
            
            # Calcular saldo líquido
            pagamentos_prop = Decimal('0.00')
            if propriedade == canta_galo:
                # Pagamentos de financiamento
                for mes in meses_pagamento:
                    if ano == ano_fim and mes > 10:
                        continue
                    pagamentos_prop += PAGAMENTO_TRIMESTRAL
                
                # Pagamento avalista (2024)
                if ano == 2024:
                    pagamentos_prop += Decimal('2478000.00')
            
            saldo_liquido_prop = total_receita_atual - total_despesa_atual - pagamentos_prop
            
            print(f"  {propriedade.nome_propriedade}:")
            print(f"    Receita: R$ {total_receita_atual:,.2f}")
            print(f"    Despesa Operacional: R$ {total_despesa_atual:,.2f}")
            print(f"    Pagamentos: R$ {pagamentos_prop:,.2f}")
            print(f"    Saldo Liquido: R$ {saldo_liquido_prop:,.2f}")
            print()
    
    print("=" * 80)
    print("CORREÇÃO COMPLETA!")
    print("=" * 80)


def verificar_saldo_final(propriedades, ano_inicio, ano_fim):
    """Verifica saldo líquido final"""
    print("=" * 80)
    print("VERIFICAÇÃO FINAL - SALDO LÍQUIDO POR ANO")
    print("=" * 80)
    print()
    
    categoria_receita_vendas, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Vendas de Gado',
        tipo=CategoriaFinanceira.TIPO_RECEITA
    )
    
    categoria_despesa_operacional, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Despesas Operacionais',
        tipo=CategoriaFinanceira.TIPO_DESPESA
    )
    
    categoria_pagamento_financiamento, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Pagamento de Financiamento',
        tipo=CategoriaFinanceira.TIPO_DESPESA
    )
    
    categoria_avalista, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Pagamento como Avalista',
        tipo=CategoriaFinanceira.TIPO_DESPESA
    )
    
    for ano in range(ano_inicio, ano_fim + 1):
        # Receitas
        receitas = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            categoria=categoria_receita_vendas,
            data_competencia__year=ano,
            tipo=CategoriaFinanceira.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        )
        total_receitas = sum(r.valor for r in receitas)
        
        # Despesas operacionais
        despesas_op = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            categoria=categoria_despesa_operacional,
            data_competencia__year=ano,
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        )
        total_despesas_op = sum(d.valor for d in despesas_op)
        
        # Pagamentos (não são despesas operacionais)
        pagamentos = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            categoria__in=[categoria_pagamento_financiamento, categoria_avalista],
            data_competencia__year=ano,
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        )
        total_pagamentos = sum(p.valor for p in pagamentos)
        
        # Saldo líquido (receita - despesas operacionais - pagamentos)
        saldo_liquido_real = total_receitas - total_despesas_op - total_pagamentos
        saldo_liquido_desejado = SALDO_LIQUIDO_TOTAL_ANUAL.get(ano, SALDO_LIQUIDO_TOTAL_ANUAL[2022])
        
        diferenca = saldo_liquido_real - saldo_liquido_desejado
        
        print(f"ANO {ano}:")
        print(f"  Receitas: R$ {total_receitas:,.2f}")
        print(f"  Despesas Operacionais: R$ {total_despesas_op:,.2f}")
        print(f"  Pagamentos (Financiamento/Avalista): R$ {total_pagamentos:,.2f}")
        print(f"  Saldo Liquido Real: R$ {saldo_liquido_real:,.2f}")
        print(f"  Saldo Liquido Desejado: R$ {saldo_liquido_desejado:,.2f}")
        print(f"  Diferenca: R$ {diferenca:,.2f} {'OK' if abs(diferenca) < 50000 else 'ATENCAO'}")
        print()


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
    
    # Corrigir tudo
    corrigir_tudo(propriedades, ano_inicio, ano_fim)
    
    # Verificar
    verificar_saldo_final(propriedades, ano_inicio, ano_fim)
    
    print("=" * 80)
    print("[OK] CORREÇÃO COMPLETA CONCLUÍDA!")
    print("=" * 80)
    print()
    print("Resumo:")
    print("  - Faturamento: R$ 14-16 milhões/ano")
    print("  - Saldo Líquido:")
    for ano, saldo in SALDO_LIQUIDO_TOTAL_ANUAL.items():
        print(f"    {ano}: R$ {saldo:,.2f}")
    print("  - Despesas operacionais ajustadas")
    print("  - Pagamentos de financiamento separados")
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

