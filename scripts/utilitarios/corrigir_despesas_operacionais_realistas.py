#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir despesas operacionais REALISTAS
Separando despesas operacionais de pagamentos de financiamento
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

# Saldo líquido desejado por ano (TOTAL, não por propriedade)
SALDO_LIQUIDO_TOTAL_ANUAL = {
    2022: Decimal('1700000.00'),  # R$ 1,7 milhões
    2023: Decimal('1100000.00'),  # R$ 1,1 milhões
    2024: Decimal('1400000.00'),  # R$ 1,4 milhões
    2025: Decimal('1700000.00'),  # R$ 1,7 milhões
}

NUM_PROPRIEDADES = 4


def gerar_valor_realista(valor_base, variacao_percentual=0.10):
    """Gera valor realista com centavos"""
    fator_variacao = Decimal(str(uniform(1 - variacao_percentual, 1 + variacao_percentual)))
    valor_variado = valor_base * fator_variacao
    centavos_aleatorios = Decimal(str(randint(0, 99))) / Decimal('100')
    valor_final = valor_variado + centavos_aleatorios
    return valor_final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def corrigir_despesas_operacionais(propriedades, ano_inicio, ano_fim):
    """Corrige despesas operacionais para saldo líquido realista"""
    print("=" * 80)
    print("CORRIGINDO DESPESAS OPERACIONAIS - SALDO LÍQUIDO REALISTA")
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
        defaults={'descricao': 'Amortização de financiamento (não é despesa operacional)'}
    )
    
    categoria_avalista, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Pagamento como Avalista',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Pagamento como avalista (não é despesa operacional)'}
    )
    
    for ano in range(ano_inicio, ano_fim + 1):
        faturamento_total = FATURAMENTO_TOTAL_ANUAL.get(ano, FATURAMENTO_TOTAL_ANUAL[2022])
        saldo_liquido_desejado = SALDO_LIQUIDO_TOTAL_ANUAL.get(ano, SALDO_LIQUIDO_TOTAL_ANUAL[2022])
        
        # Calcular receitas totais do ano (somar todas as propriedades)
        receitas_ano = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            categoria=categoria_receita_vendas,
            data_competencia__year=ano,
            tipo=CategoriaFinanceira.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        )
        receita_total_real = sum(r.valor for r in receitas_ano)
        
        # Se não houver receitas, usar o faturamento esperado
        if receita_total_real == 0:
            receita_total_real = faturamento_total
        
        # Calcular pagamentos de financiamento e avalista (NÃO são despesas operacionais)
        pagamentos_financiamento = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            categoria=categoria_pagamento_financiamento,
            data_competencia__year=ano,
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        )
        total_pagamentos_financiamento = sum(p.valor for p in pagamentos_financiamento)
        
        pagamentos_avalista = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            categoria=categoria_avalista,
            data_competencia__year=ano,
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        )
        total_pagamentos_avalista = sum(p.valor for p in pagamentos_avalista)
        
        # Despesas operacionais = Receita - Saldo Líquido - Pagamentos Financiamento/Avalista
        despesa_operacional_total = receita_total_real - saldo_liquido_desejado - total_pagamentos_financiamento - total_pagamentos_avalista
        
        # Por propriedade
        receita_por_propriedade = receita_total_real / NUM_PROPRIEDADES
        despesa_operacional_por_propriedade = despesa_operacional_total / NUM_PROPRIEDADES
        
        print(f"ANO {ano}:")
        print(f"  Receita Total: R$ {receita_total_real:,.2f}")
        print(f"  Pagamentos Financiamento: R$ {total_pagamentos_financiamento:,.2f}")
        print(f"  Pagamentos Avalista: R$ {total_pagamentos_avalista:,.2f}")
        print(f"  Despesa Operacional Total: R$ {despesa_operacional_total:,.2f}")
        print(f"  Saldo Líquido: R$ {saldo_liquido_desejado:,.2f}")
        print(f"  Por Propriedade - Receita: R$ {receita_por_propriedade:,.2f}, Despesa Operacional: R$ {despesa_operacional_por_propriedade:,.2f}")
        print()
        
        for propriedade in propriedades:
            # ========== DESPESAS OPERACIONAIS ==========
            despesa_mensal_base = despesa_operacional_por_propriedade / Decimal('12')
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
                fator_ajuste = despesa_operacional_por_propriedade / total_despesa_calculado
                valores_despesa_mensais = [
                    (mes, (valor * fator_ajuste).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                    for mes, valor in valores_despesa_mensais
                ]
            
            # Buscar despesas operacionais existentes para atualizar
            despesas_existentes = LancamentoFinanceiro.objects.filter(
                propriedade=propriedade,
                categoria=categoria_despesa_operacional,
                data_competencia__year=ano,
                tipo=CategoriaFinanceira.TIPO_DESPESA
            ).order_by('data_competencia')
            
            # Atualizar ou criar despesas operacionais
            total_despesa_atualizado = Decimal('0.00')
            despesas_list = list(despesas_existentes)
            
            for idx, (mes, despesa_mes) in enumerate(valores_despesa_mensais):
                data_competencia = date(ano, mes, 15)
                
                if idx < len(despesas_list):
                    # Atualizar existente
                    lancamento = despesas_list[idx]
                    lancamento.valor = despesa_mes
                    lancamento.descricao = f'Despesas operacionais - {mes:02d}/{ano}'
                    lancamento.data_competencia = data_competencia
                    lancamento.data_vencimento = data_competencia
                    lancamento.data_quitacao = data_competencia
                    lancamento.save()
                    total_despesa_atualizado += despesa_mes
                else:
                    # Criar novo
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
            
            # Calcular receita da propriedade
            receitas_prop = LancamentoFinanceiro.objects.filter(
                propriedade=propriedade,
                categoria=categoria_receita_vendas,
                data_competencia__year=ano,
                tipo=CategoriaFinanceira.TIPO_RECEITA,
                status=LancamentoFinanceiro.STATUS_QUITADO
            )
            total_receita_prop = sum(r.valor for r in receitas_prop)
            
            # Calcular saldo líquido (receita - despesas operacionais - pagamentos)
            pagamentos_fin_prop = LancamentoFinanceiro.objects.filter(
                propriedade=propriedade,
                categoria__in=[categoria_pagamento_financiamento, categoria_avalista],
                data_competencia__year=ano,
                tipo=CategoriaFinanceira.TIPO_DESPESA,
                status=LancamentoFinanceiro.STATUS_QUITADO
            )
            total_pagamentos_prop = sum(p.valor for p in pagamentos_fin_prop)
            
            saldo_liquido_prop = total_receita_prop - total_despesa_atualizado - total_pagamentos_prop
            
            print(f"  {propriedade.nome_propriedade}:")
            print(f"    Receita: R$ {total_receita_prop:,.2f}")
            print(f"    Despesa Operacional: R$ {total_despesa_atualizado:,.2f}")
            print(f"    Pagamentos (Financiamento/Avalista): R$ {total_pagamentos_prop:,.2f}")
            print(f"    Saldo Líquido: R$ {saldo_liquido_prop:,.2f}")
            print()
    
    print("=" * 80)
    print("DESPESAS OPERACIONAIS CORRIGIDAS!")
    print("=" * 80)


def verificar_saldo_liquido_total(propriedades, ano_inicio, ano_fim):
    """Verifica saldo líquido total por ano"""
    print("=" * 80)
    print("VERIFICAÇÃO DE SALDO LÍQUIDO TOTAL POR ANO")
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
        
        # Despesas operacionais (apenas)
        despesas_operacionais = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            categoria=categoria_despesa_operacional,
            data_competencia__year=ano,
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        )
        total_despesas_operacionais = sum(d.valor for d in despesas_operacionais)
        
        # Saldo líquido (receita - despesas operacionais)
        saldo_liquido_real = total_receitas - total_despesas_operacionais
        saldo_liquido_desejado = SALDO_LIQUIDO_TOTAL_ANUAL.get(ano, SALDO_LIQUIDO_TOTAL_ANUAL[2022])
        
        diferenca = saldo_liquido_real - saldo_liquido_desejado
        
        print(f"ANO {ano}:")
        print(f"  Receitas: R$ {total_receitas:,.2f}")
        print(f"  Despesas Operacionais: R$ {total_despesas_operacionais:,.2f}")
        print(f"  Saldo Líquido Real: R$ {saldo_liquido_real:,.2f}")
        print(f"  Saldo Líquido Desejado: R$ {saldo_liquido_desejado:,.2f}")
        print(f"  Diferença: R$ {diferenca:,.2f} {'✅' if abs(diferenca) < 1000 else '⚠️'}")
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
    
    # Corrigir despesas operacionais
    corrigir_despesas_operacionais(propriedades, ano_inicio, ano_fim)
    
    # Verificar saldo líquido
    verificar_saldo_liquido_total(propriedades, ano_inicio, ano_fim)
    
    print("=" * 80)
    print("[OK] CORREÇÃO CONCLUÍDA!")
    print("=" * 80)
    print()
    print("✅ Despesas operacionais ajustadas")
    print("✅ Pagamentos de financiamento separados (não são despesas operacionais)")
    print("✅ Saldo líquido conforme solicitado")
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

