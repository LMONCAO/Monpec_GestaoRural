#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para atualizar lançamentos financeiros com novo faturamento
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date

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


def atualizar_lancamentos_receita(propriedades, ano_inicio, ano_fim):
    """Atualiza lançamentos de receita para refletir novo faturamento"""
    print("=" * 80)
    print("ATUALIZANDO LANÇAMENTOS DE RECEITA")
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
            # Criar novas receitas mensais (maior concentração no 2º semestre)
            receita_mensal_base = faturamento_por_propriedade / Decimal('12')
            
            for mes in range(1, 13):
                if ano == ano_fim and mes > 10:  # Até outubro de 2025
                    continue
                
                # Ajustar por mês (2º semestre 15% acima, 1º semestre 15% abaixo)
                if mes >= 7:
                    fator_mes = Decimal('1.15')
                else:
                    fator_mes = Decimal('0.85')
                
                receita_mes = receita_mensal_base * fator_mes
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
                    # Atualizar todos os lançamentos do mês proporcionalmente
                    total_existente = sum(l.valor for l in lancamentos_mes)
                    if total_existente > 0:
                        # Ajustar proporcionalmente
                        for lanc in lancamentos_mes:
                            fator_ajuste = receita_mes / total_existente
                            lanc.valor = lanc.valor * fator_ajuste
                            lanc.save()
                    else:
                        # Se total é zero, atualizar o primeiro
                        primeiro = lancamentos_mes.first()
                        primeiro.valor = receita_mes
                        primeiro.descricao = f'Vendas de gado - {mes:02d}/{ano}'
                        primeiro.save()
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
            
            print(f"[OK] {ano}: {propriedade.nome_propriedade} - R$ {faturamento_por_propriedade:,.2f}")
    
    print()
    print("Lançamentos de receita atualizados!")
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
    
    atualizar_lancamentos_receita(propriedades, ano_inicio, ano_fim)
    
    print("=" * 80)
    print("[OK] ATUALIZAÇÃO CONCLUÍDA!")
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

