#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para LIMPAR lançamentos antigos e RECRIAR apenas os corretos
Faturamento: R$ 14-16 milhões/ano
Saldo Líquido: 2022=1.7M, 2023=1.1M, 2024=1.4M, 2025=1.7M
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

# Faturamento TOTAL por ano
FATURAMENTO_TOTAL_ANUAL = {
    2022: Decimal('15000000.00'),
    2023: Decimal('14000000.00'),
    2024: Decimal('15000000.00'),
    2025: Decimal('16000000.00'),
}

# Saldo líquido TOTAL por ano
SALDO_LIQUIDO_TOTAL_ANUAL = {
    2022: Decimal('1700000.00'),
    2023: Decimal('1100000.00'),
    2024: Decimal('1400000.00'),
    2025: Decimal('1700000.00'),
}

NUM_PROPRIEDADES = 4
PAGAMENTO_TRIMESTRAL = Decimal('1500000.00')


def gerar_valor_realista(valor_base, variacao_percentual=0.10):
    """Gera valor realista com centavos"""
    fator_variacao = Decimal(str(uniform(1 - variacao_percentual, 1 + variacao_percentual)))
    valor_variado = valor_base * fator_variacao
    centavos_aleatorios = Decimal(str(randint(0, 99))) / Decimal('100')
    valor_final = valor_variado + centavos_aleatorios
    return valor_final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def limpar_e_recriar_tudo(propriedades, ano_inicio, ano_fim):
    """Limpa e recria todos os lançamentos corretamente"""
    print("=" * 80)
    print("LIMPEZA E RECRIAÇÃO DE LANÇAMENTOS - DADOS CORRETOS")
    print("=" * 80)
    print()
    
    # Buscar categorias
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
    
    canta_galo = propriedades.filter(nome_propriedade__icontains='Canta Galo').first()
    
    # LIMPAR todos os lançamentos dos anos 2022-2025 (incluindo pagamentos duplicados)
    print("Limpando lançamentos antigos...")
    
    # Limpar receitas e despesas operacionais
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE gestao_rural_lancamentofinanceiro 
            SET valor = 0.00 
            WHERE propriedade_id IN (
                SELECT id FROM gestao_rural_propriedade 
                WHERE produtor_id IN (
                    SELECT id FROM gestao_rural_produtorrural 
                    WHERE nome LIKE '%Marcelo Sanguino%'
                )
            )
            AND strftime('%Y', data_competencia) BETWEEN '2022' AND '2025'
            AND categoria_id NOT IN (
                SELECT id FROM gestao_rural_categoriafinanceira 
                WHERE nome IN ('Pagamento de Financiamento', 'Pagamento como Avalista')
            )
        """)
    
    # Limpar pagamentos duplicados (manter apenas os corretos)
    print("Limpando pagamentos de financiamento duplicados...")
    for ano in range(ano_inicio, ano_fim + 1):
        meses_pagamento = [1, 4, 7, 10]
        if ano == ano_fim:
            meses_pagamento = [1, 4, 7]  # Até outubro
        
        for mes in meses_pagamento:
            if ano == ano_fim and mes > 10:
                continue
            
            # Deletar pagamentos duplicados, manter apenas 1
            pagamentos = LancamentoFinanceiro.objects.filter(
                propriedade=canta_galo,
                categoria=categoria_pagamento_financiamento,
                data_competencia__year=ano,
                data_competencia__month=mes,
                tipo=CategoriaFinanceira.TIPO_DESPESA
            )
            
            if pagamentos.count() > 1:
                primeiro = pagamentos.first()
                ids_para_deletar = list(pagamentos.exclude(id=primeiro.id).values_list('id', flat=True))
                if ids_para_deletar:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"DELETE FROM gestao_rural_lancamentofinanceiro WHERE id IN ({','.join(map(str, ids_para_deletar))})"
                        )
        
        # Pagamento avalista (2024, outubro)
        if ano == 2024:
            pagamentos_avalista = LancamentoFinanceiro.objects.filter(
                propriedade=canta_galo,
                categoria=categoria_avalista,
                data_competencia__year=2024,
                data_competencia__month=10,
                tipo=CategoriaFinanceira.TIPO_DESPESA
            )
            
            if pagamentos_avalista.count() > 1:
                primeiro = pagamentos_avalista.first()
                ids_para_deletar = list(pagamentos_avalista.exclude(id=primeiro.id).values_list('id', flat=True))
                if ids_para_deletar:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            f"DELETE FROM gestao_rural_lancamentofinanceiro WHERE id IN ({','.join(map(str, ids_para_deletar))})"
                        )
    
    print("Lançamentos antigos limpos")
    print()
    
    for ano in range(ano_inicio, ano_fim + 1):
        faturamento_total = FATURAMENTO_TOTAL_ANUAL.get(ano, FATURAMENTO_TOTAL_ANUAL[2022])
        saldo_liquido_desejado = SALDO_LIQUIDO_TOTAL_ANUAL.get(ano, SALDO_LIQUIDO_TOTAL_ANUAL[2022])
        
        # Pagamentos (apenas Canta Galo)
        meses_pagamento = [1, 4, 7, 10]
        total_pagamentos_financiamento = PAGAMENTO_TRIMESTRAL * Decimal('4')
        if ano == ano_fim:
            total_pagamentos_financiamento = PAGAMENTO_TRIMESTRAL * Decimal('3')
        
        total_pagamentos_avalista = Decimal('0.00')
        if ano == 2024:
            total_pagamentos_avalista = Decimal('2478000.00')
        
        # Despesas operacionais = Receita - Saldo Líquido - Pagamentos
        despesa_operacional_total = faturamento_total - saldo_liquido_desejado - total_pagamentos_financiamento - total_pagamentos_avalista
        
        receita_por_propriedade = faturamento_total / NUM_PROPRIEDADES
        despesa_operacional_por_propriedade = despesa_operacional_total / NUM_PROPRIEDADES
        
        print(f"ANO {ano}:")
        print(f"  Faturamento: R$ {faturamento_total:,.2f}")
        print(f"  Despesa Operacional: R$ {despesa_operacional_total:,.2f}")
        print(f"  Pagamentos: R$ {total_pagamentos_financiamento + total_pagamentos_avalista:,.2f}")
        print(f"  Saldo Liquido: R$ {saldo_liquido_desejado:,.2f}")
        print()
        
        for propriedade in propriedades:
            # ========== RECEITAS ==========
            receita_mensal_base = receita_por_propriedade / Decimal('12')
            valores_receita = []
            total_receita_calc = Decimal('0.00')
            
            for mes in range(1, 13):
                if ano == ano_fim and mes > 10:
                    continue
                
                if mes >= 7:
                    fator_mes = Decimal('1.15')
                else:
                    fator_mes = Decimal('0.85')
                
                receita_mes_base = receita_mensal_base * fator_mes
                receita_mes = gerar_valor_realista(receita_mes_base, 0.10)
                valores_receita.append((mes, receita_mes))
                total_receita_calc += receita_mes
            
            # Ajustar proporcionalmente, mas adicionar pequena variação de centavos
            if total_receita_calc > 0:
                fator = receita_por_propriedade / total_receita_calc
                # Adicionar pequena variação aleatória de centavos para não ser exato
                variacao_centavos = Decimal(str(randint(-500, 500))) / Decimal('100')  # ±R$ 5,00
                receita_ajustada = receita_por_propriedade + variacao_centavos
                fator_ajustado = receita_ajustada / total_receita_calc
                valores_receita = [(mes, (v * fator_ajustado).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) for mes, v in valores_receita]
            
            # Criar/atualizar receitas
            total_receita_atual = Decimal('0.00')
            for mes, receita_mes in valores_receita:
                data_comp = date(ano, mes, 15)
                
                # Buscar lançamentos existentes
                lancamentos_existentes = LancamentoFinanceiro.objects.filter(
                    propriedade=propriedade,
                    categoria=categoria_receita_vendas,
                    data_competencia__year=ano,
                    data_competencia__month=mes,
                    tipo=CategoriaFinanceira.TIPO_RECEITA
                )
                
                if lancamentos_existentes.exists():
                    # Atualizar o primeiro e deletar os demais
                    primeiro = lancamentos_existentes.first()
                    primeiro.valor = receita_mes
                    primeiro.descricao = f'Vendas de gado - {mes:02d}/{ano}'
                    primeiro.data_competencia = data_comp
                    primeiro.data_vencimento = data_comp
                    primeiro.data_quitacao = data_comp
                    primeiro.status = LancamentoFinanceiro.STATUS_QUITADO
                    primeiro.save()
                    
                    # Deletar os demais (se houver)
                    if lancamentos_existentes.count() > 1:
                        # Usar raw SQL para evitar problema com anexos
                        from django.db import connection
                        with connection.cursor() as cursor:
                            ids_para_deletar = list(lancamentos_existentes.exclude(id=primeiro.id).values_list('id', flat=True))
                            if ids_para_deletar:
                                cursor.execute(
                                    f"DELETE FROM gestao_rural_lancamentofinanceiro WHERE id IN ({','.join(map(str, ids_para_deletar))})"
                                )
                    
                    total_receita_atual += receita_mes
                else:
                    # Criar novo
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
            
            # Ajustar proporcionalmente, mas adicionar pequena variação de centavos
            if total_despesa_calc > 0:
                fator = despesa_operacional_por_propriedade / total_despesa_calc
                # Adicionar pequena variação aleatória de centavos para não ser exato
                variacao_centavos = Decimal(str(randint(-500, 500))) / Decimal('100')  # ±R$ 5,00
                despesa_ajustada = despesa_operacional_por_propriedade + variacao_centavos
                fator_ajustado = despesa_ajustada / total_despesa_calc
                valores_despesa = [(mes, (v * fator_ajustado).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)) for mes, v in valores_despesa]
            
            # Criar/atualizar despesas operacionais
            total_despesa_atual = Decimal('0.00')
            for mes, despesa_mes in valores_despesa:
                data_comp = date(ano, mes, 15)
                
                # Buscar lançamentos existentes
                lancamentos_existentes = LancamentoFinanceiro.objects.filter(
                    propriedade=propriedade,
                    categoria=categoria_despesa_operacional,
                    data_competencia__year=ano,
                    data_competencia__month=mes,
                    tipo=CategoriaFinanceira.TIPO_DESPESA
                )
                
                if lancamentos_existentes.exists():
                    # Atualizar o primeiro e deletar os demais
                    primeiro = lancamentos_existentes.first()
                    primeiro.valor = despesa_mes
                    primeiro.descricao = f'Despesas operacionais - {mes:02d}/{ano}'
                    primeiro.data_competencia = data_comp
                    primeiro.data_vencimento = data_comp
                    primeiro.data_quitacao = data_comp
                    primeiro.status = LancamentoFinanceiro.STATUS_QUITADO
                    primeiro.save()
                    
                    # Deletar os demais (se houver)
                    if lancamentos_existentes.count() > 1:
                        from django.db import connection
                        with connection.cursor() as cursor:
                            ids_para_deletar = list(lancamentos_existentes.exclude(id=primeiro.id).values_list('id', flat=True))
                            if ids_para_deletar:
                                cursor.execute(
                                    f"DELETE FROM gestao_rural_lancamentofinanceiro WHERE id IN ({','.join(map(str, ids_para_deletar))})"
                                )
                    
                    total_despesa_atual += despesa_mes
                else:
                    # Criar novo
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
            
            # Calcular saldo
            pagamentos_prop = Decimal('0.00')
            if propriedade == canta_galo:
                for mes in meses_pagamento:
                    if ano == ano_fim and mes > 10:
                        continue
                    pagamentos_prop += PAGAMENTO_TRIMESTRAL
                if ano == 2024:
                    pagamentos_prop += Decimal('2478000.00')
            
            saldo_liquido_prop = total_receita_atual - total_despesa_atual - pagamentos_prop
            
            print(f"  {propriedade.nome_propriedade}:")
            print(f"    Receita: R$ {total_receita_atual:,.2f}")
            print(f"    Despesa Op: R$ {total_despesa_atual:,.2f}")
            print(f"    Pagamentos: R$ {pagamentos_prop:,.2f}")
            print(f"    Saldo: R$ {saldo_liquido_prop:,.2f}")
            print()
    
    print("=" * 80)
    print("LANÇAMENTOS RECRIADOS!")
    print("=" * 80)


def verificar_final(propriedades, ano_inicio, ano_fim):
    """Verificação final"""
    print("=" * 80)
    print("VERIFICAÇÃO FINAL")
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
        receitas = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            categoria=categoria_receita_vendas,
            data_competencia__year=ano,
            tipo=CategoriaFinanceira.TIPO_RECEITA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        )
        total_receitas = sum(r.valor for r in receitas)
        
        despesas_op = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            categoria=categoria_despesa_operacional,
            data_competencia__year=ano,
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        )
        total_despesas_op = sum(d.valor for d in despesas_op)
        
        pagamentos = LancamentoFinanceiro.objects.filter(
            propriedade__in=propriedades,
            categoria__in=[categoria_pagamento_financiamento, categoria_avalista],
            data_competencia__year=ano,
            tipo=CategoriaFinanceira.TIPO_DESPESA,
            status=LancamentoFinanceiro.STATUS_QUITADO
        )
        total_pagamentos = sum(p.valor for p in pagamentos)
        
        saldo_liquido_real = total_receitas - total_despesas_op - total_pagamentos
        saldo_liquido_desejado = SALDO_LIQUIDO_TOTAL_ANUAL.get(ano, SALDO_LIQUIDO_TOTAL_ANUAL[2022])
        
        print(f"ANO {ano}:")
        print(f"  Receitas: R$ {total_receitas:,.2f}")
        print(f"  Despesas Op: R$ {total_despesas_op:,.2f}")
        print(f"  Pagamentos: R$ {total_pagamentos:,.2f}")
        print(f"  Saldo Liquido: R$ {saldo_liquido_real:,.2f} (desejado: R$ {saldo_liquido_desejado:,.2f})")
        print(f"  {'OK' if abs(saldo_liquido_real - saldo_liquido_desejado) < 100000 else 'AJUSTAR'}")
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
    
    limpar_e_recriar_tudo(propriedades, ano_inicio, ano_fim)
    verificar_final(propriedades, ano_inicio, ano_fim)
    
    print("=" * 80)
    print("[OK] PROCESSO CONCLUÍDO!")
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

