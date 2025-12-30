#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para ajustar lançamentos financeiros com valores realistas:
- Variação para cima e para baixo
- Valores com centavos (não redondos)
- Mais realista
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

# Faturamento por propriedade (dividido entre as 4 propriedades)
FATURAMENTO_TOTAL_ANUAL = {
    2022: Decimal('15000000.00'),  # R$ 15 milhões
    2023: Decimal('14000000.00'),  # R$ 14 milhões
    2024: Decimal('15000000.00'),  # R$ 15 milhões
    2025: Decimal('16000000.00'),  # R$ 16 milhões
}

NUM_PROPRIEDADES = 4


def gerar_valor_realista(valor_base, variacao_percentual=0.15):
    """
    Gera um valor realista com centavos e variação
    variacao_percentual: 15% de variação para cima ou para baixo
    """
    # Variação aleatória entre -variacao_percentual e +variacao_percentual
    fator_variacao = Decimal(str(uniform(1 - variacao_percentual, 1 + variacao_percentual)))
    valor_variado = valor_base * fator_variacao
    
    # Adicionar centavos aleatórios (0 a 99 centavos)
    centavos_aleatorios = Decimal(str(randint(0, 99))) / Decimal('100')
    valor_final = valor_variado + centavos_aleatorios
    
    # Arredondar para 2 casas decimais
    valor_final = valor_final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    return valor_final


def ajustar_lancamentos_receita(propriedades, ano_inicio, ano_fim):
    """Ajusta lançamentos de receita com valores realistas e variados"""
    print("=" * 80)
    print("AJUSTANDO LANÇAMENTOS DE RECEITA - VALORES REALISTAS")
    print("=" * 80)
    print()
    
    categoria_receita_vendas, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Vendas de Gado',
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        defaults={'descricao': 'Receita com vendas de gado'}
    )
    
    for ano in range(ano_inicio, ano_fim + 1):
        faturamento_total = FATURAMENTO_TOTAL_ANUAL.get(ano, FATURAMENTO_TOTAL_ANUAL[2022])
        faturamento_por_propriedade = faturamento_total / NUM_PROPRIEDADES
        
        for propriedade in propriedades:
            # Receita mensal base
            receita_mensal_base = faturamento_por_propriedade / Decimal('12')
            
            # Lista para armazenar valores mensais e ajustar no final
            valores_mensais = []
            total_calculado = Decimal('0.00')
            
            # Primeiro, gerar valores variados para cada mês
            for mes in range(1, 13):
                if ano == ano_fim and mes > 10:  # Até outubro de 2025
                    continue
                
                # Ajustar por mês (2º semestre 15% acima, 1º semestre 15% abaixo)
                if mes >= 7:
                    fator_mes = Decimal('1.15')
                else:
                    fator_mes = Decimal('0.85')
                
                receita_mes_base = receita_mensal_base * fator_mes
                
                # Gerar valor realista com variação e centavos
                receita_mes = gerar_valor_realista(receita_mes_base, variacao_percentual=0.12)
                valores_mensais.append((mes, receita_mes))
                total_calculado += receita_mes
            
            # Ajustar proporcionalmente para garantir que a soma seja exata
            if total_calculado > 0:
                fator_ajuste = faturamento_por_propriedade / total_calculado
                valores_mensais_ajustados = []
                for mes, valor in valores_mensais:
                    valor_ajustado = (valor * fator_ajuste).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    valores_mensais_ajustados.append((mes, valor_ajustado))
                valores_mensais = valores_mensais_ajustados
            
            # Atualizar ou criar lançamentos
            total_atualizado = Decimal('0.00')
            for mes, receita_mes in valores_mensais:
                data_competencia = date(ano, mes, 15)
                
                # Buscar lançamentos existentes para este mês
                lancamentos_mes = LancamentoFinanceiro.objects.filter(
                    propriedade=propriedade,
                    categoria=categoria_receita_vendas,
                    data_competencia__year=ano,
                    data_competencia__month=mes,
                    tipo=CategoriaFinanceira.TIPO_RECEITA
                )
                
                if lancamentos_mes.exists():
                    # Atualizar o primeiro
                    primeiro = lancamentos_mes.first()
                    primeiro.valor = receita_mes
                    primeiro.descricao = f'Vendas de gado - {mes:02d}/{ano}'
                    primeiro.save()
                    total_atualizado += receita_mes
                else:
                    # Criar novo
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
                    total_atualizado += receita_mes
            
            print(f"[OK] {ano}: {propriedade.nome_propriedade}")
            print(f"     Total: R$ {total_atualizado:,.2f} (objetivo: R$ {faturamento_por_propriedade:,.2f})")
    
    print()
    print("Lançamentos de receita ajustados com valores realistas!")
    print()


def ajustar_lancamentos_despesas(propriedades, ano_inicio, ano_fim):
    """Ajusta lançamentos de despesas com valores realistas e variados"""
    print("=" * 80)
    print("AJUSTANDO LANÇAMENTOS DE DESPESAS - VALORES REALISTAS")
    print("=" * 80)
    print()
    
    categoria_despesa_operacional, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Despesas Operacionais',
        tipo=CategoriaFinanceira.TIPO_DESPESA,
        defaults={'descricao': 'Despesas operacionais da propriedade'}
    )
    
    for ano in range(ano_inicio, ano_fim + 1):
        faturamento_total = FATURAMENTO_TOTAL_ANUAL.get(ano, FATURAMENTO_TOTAL_ANUAL[2022])
        faturamento_por_propriedade = faturamento_total / NUM_PROPRIEDADES
        
        # Despesas = 60% da receita (aproximadamente)
        despesa_anual_por_propriedade = faturamento_por_propriedade * Decimal('0.60')
        despesa_mensal_base = despesa_anual_por_propriedade / Decimal('12')
        
        for propriedade in propriedades:
            # Lista para armazenar valores mensais
            valores_mensais = []
            total_calculado = Decimal('0.00')
            
            # Gerar valores variados para cada mês
            for mes in range(1, 13):
                if ano == ano_fim and mes > 10:  # Até outubro de 2025
                    continue
                
                # Variação mensal (alguns meses maiores, outros menores)
                if mes in [1, 2, 6, 7, 8]:  # Meses com mais despesas
                    fator_mes = Decimal('1.10')
                elif mes in [3, 4, 5]:  # Meses intermediários
                    fator_mes = Decimal('1.00')
                else:  # Meses com menos despesas
                    fator_mes = Decimal('0.90')
                
                despesa_mes_base = despesa_mensal_base * fator_mes
                
                # Gerar valor realista com variação e centavos
                despesa_mes = gerar_valor_realista(despesa_mes_base, variacao_percentual=0.15)
                valores_mensais.append((mes, despesa_mes))
                total_calculado += despesa_mes
            
            # Ajustar proporcionalmente
            if total_calculado > 0:
                fator_ajuste = despesa_anual_por_propriedade / total_calculado
                valores_mensais_ajustados = []
                for mes, valor in valores_mensais:
                    valor_ajustado = (valor * fator_ajuste).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                    valores_mensais_ajustados.append((mes, valor_ajustado))
                valores_mensais = valores_mensais_ajustados
            
            # Atualizar ou criar lançamentos
            total_atualizado = Decimal('0.00')
            for mes, despesa_mes in valores_mensais:
                data_competencia = date(ano, mes, 15)
                
                # Buscar lançamentos existentes
                lancamentos_mes = LancamentoFinanceiro.objects.filter(
                    propriedade=propriedade,
                    categoria=categoria_despesa_operacional,
                    data_competencia__year=ano,
                    data_competencia__month=mes,
                    tipo=CategoriaFinanceira.TIPO_DESPESA
                )
                
                if lancamentos_mes.exists():
                    # Atualizar o primeiro
                    primeiro = lancamentos_mes.first()
                    primeiro.valor = despesa_mes
                    primeiro.descricao = f'Despesas operacionais - {mes:02d}/{ano}'
                    primeiro.save()
                    total_atualizado += despesa_mes
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
                    total_atualizado += despesa_mes
            
            print(f"[OK] {ano}: {propriedade.nome_propriedade}")
            print(f"     Total Despesas: R$ {total_atualizado:,.2f}")
    
    print()
    print("Lançamentos de despesas ajustados com valores realistas!")
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
    
    # Ajustar receitas
    ajustar_lancamentos_receita(propriedades, ano_inicio, ano_fim)
    
    # Ajustar despesas
    ajustar_lancamentos_despesas(propriedades, ano_inicio, ano_fim)
    
    print("=" * 80)
    print("[OK] AJUSTE CONCLUÍDO!")
    print("=" * 80)
    print()
    print("Características dos valores:")
    print("  - Variação de ±12% nas receitas")
    print("  - Variação de ±15% nas despesas")
    print("  - Valores com centavos (não redondos)")
    print("  - Alguns meses maiores, outros menores")
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

