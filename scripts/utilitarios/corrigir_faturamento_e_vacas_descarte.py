#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corrigir:
1. Faturamento para R$ 14-16 milhões por ano
2. Vacas de descarte = 20% das matrizes do ano anterior
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho,
    MovimentacaoProjetada
)
from gestao_rural.models_financeiro import (
    LancamentoFinanceiro, CategoriaFinanceira, ReceitaAnual
)

# Faturamento ajustado: R$ 14-16 milhões por ano
FATURAMENTO_ANUAL = {
    2022: Decimal('15000000.00'),  # R$ 15 milhões
    2023: Decimal('14000000.00'),  # R$ 14 milhões (queda de preços)
    2024: Decimal('15000000.00'),  # R$ 15 milhões (recuperação)
    2025: Decimal('16000000.00'),  # R$ 16 milhões (acima do normal)
}


def corrigir_faturamento(propriedades, ano_inicio, ano_fim):
    """Corrige o faturamento para R$ 14-16 milhões por ano"""
    print("=" * 80)
    print("CORRIGINDO FATURAMENTO - R$ 14-16 MILHÕES/ANO")
    print("=" * 80)
    print()
    
    categoria_receita_vendas, _ = CategoriaFinanceira.objects.get_or_create(
        nome='Vendas de Gado',
        tipo=CategoriaFinanceira.TIPO_RECEITA,
        defaults={'descricao': 'Receita com vendas de gado'}
    )
    
    # Deletar receitas antigas (opcional - ou podemos atualizar)
    # Vamos atualizar as ReceitaAnual primeiro
    for ano in range(ano_inicio, ano_fim + 1):
        faturamento_ano = FATURAMENTO_ANUAL.get(ano, FATURAMENTO_ANUAL[2022])
        
        for propriedade in propriedades:
            receita_anual = ReceitaAnual.objects.filter(
                propriedade=propriedade,
                ano=ano
            ).first()
            
            if receita_anual:
                # Atualizar receita bruta
                receita_anual.valor_receita = faturamento_ano
                receita_anual.save()
                print(f"[OK] ReceitaAnual {ano} atualizada: {propriedade.nome_propriedade} - R$ {faturamento_ano:,.2f}")
    
    print()
    print("Faturamento corrigido!")
    print()


def corrigir_vacas_descarte(propriedades, ano_inicio, ano_fim):
    """Corrige vacas de descarte = 20% das matrizes do ano anterior"""
    print("=" * 80)
    print("CORRIGINDO VACAS DE DESCARTE - 20% DAS MATRIZES DO ANO ANTERIOR")
    print("=" * 80)
    print()
    
    # Buscar categorias
    categoria_vaca_reproducao = CategoriaAnimal.objects.filter(
        nome__icontains='Vaca'
    ).filter(
        nome__icontains='Reprodução'
    ).exclude(
        nome__icontains='Descarte'
    ).first()
    
    categoria_vaca_descarte = CategoriaAnimal.objects.filter(
        nome__icontains='Vaca'
    ).filter(
        nome__icontains='Descarte'
    ).first()
    
    if not categoria_vaca_reproducao:
        print("[ERRO] Categoria 'Vacas em Reprodução' não encontrada!")
        return
    
    if not categoria_vaca_descarte:
        print("[AVISO] Categoria 'Vacas Descarte' não encontrada. Criando...")
        categoria_vaca_descarte = CategoriaAnimal.objects.create(
            nome='Vacas Descarte +36 M',
            descricao='Vacas descartadas (20% das matrizes do ano anterior)',
            idade_minima_meses=36,
            idade_maxima_meses=120,
        )
    
    # Para cada propriedade e ano
    for propriedade in propriedades:
        if 'Canta Galo' not in propriedade.nome_propriedade:
            continue
        
        for ano in range(ano_inicio, ano_fim + 1):
            # Buscar inventário de matrizes do ano anterior
            ano_anterior = ano - 1
            if ano_anterior < ano_inicio:
                # Para o primeiro ano, usar o próprio ano como base
                ano_anterior = ano
            
            inventario_matrizes = InventarioRebanho.objects.filter(
                propriedade=propriedade,
                categoria=categoria_vaca_reproducao,
                data_inventario__year=ano_anterior
            ).first()
            
            if not inventario_matrizes:
                print(f"[AVISO] Não encontrado inventário de matrizes para {ano_anterior}")
                continue
            
            # Calcular 20% das matrizes do ano anterior
            matrizes_ano_anterior = inventario_matrizes.quantidade
            vacas_descarte_quantidade = int(matrizes_ano_anterior * Decimal('0.20'))
            
            # Remover inventário de vacas descarte se existir (não devem estar no inventário)
            InventarioRebanho.objects.filter(
                propriedade=propriedade,
                categoria=categoria_vaca_descarte,
                data_inventario__year=ano
            ).delete()
            
            # Criar movimentação de descarte (transferência para Invernada Grande)
            if vacas_descarte_quantidade > 0:
                # Buscar propriedade destino (Invernada Grande)
                invernada_grande = propriedades.filter(
                    nome_propriedade__icontains='Invernada Grande'
                ).first()
                
                if invernada_grande:
                    # Criar transferência de descarte
                    data_descarte = date(ano, 7, 1)  # Julho (época de descarte)
                    
                    # Saída da Canta Galo
                    MovimentacaoProjetada.objects.filter(
                        propriedade=propriedade,
                        categoria=categoria_vaca_descarte,
                        data_movimentacao__year=ano,
                        tipo_movimentacao='TRANSFERENCIA_SAIDA'
                    ).delete()  # Remover antigas
                    
                    MovimentacaoProjetada.objects.create(
                        propriedade=propriedade,
                        categoria=categoria_vaca_reproducao,  # Saem como matrizes
                        data_movimentacao=data_descarte,
                        tipo_movimentacao='TRANSFERENCIA_SAIDA',
                        quantidade=vacas_descarte_quantidade,
                        observacao=f'Descarte de 20% das matrizes ({vacas_descarte_quantidade} cabeças) - Transferência para Invernada Grande'
                    )
                    
                    # Entrada na Invernada Grande (como vacas descarte)
                    MovimentacaoProjetada.objects.filter(
                        propriedade=invernada_grande,
                        categoria=categoria_vaca_descarte,
                        data_movimentacao__year=ano,
                        tipo_movimentacao='TRANSFERENCIA_ENTRADA'
                    ).delete()  # Remover antigas
                    
                    MovimentacaoProjetada.objects.create(
                        propriedade=invernada_grande,
                        categoria=categoria_vaca_descarte,
                        data_movimentacao=data_descarte,
                        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                        quantidade=vacas_descarte_quantidade,
                        observacao=f'Recebimento de vacas descartadas da Canta Galo ({vacas_descarte_quantidade} cabeças - 20% das matrizes)'
                    )
                    
                    print(f"[OK] {ano}: {vacas_descarte_quantidade} vacas descartadas (20% de {matrizes_ano_anterior} matrizes de {ano_anterior})")
                else:
                    print(f"[AVISO] Propriedade 'Invernada Grande' não encontrada para {ano}")
    
    print()
    print("Vacas de descarte corrigidas!")
    print()


def main():
    """Função principal"""
    print("=" * 80)
    print("CORREÇÃO DE FATURAMENTO E VACAS DE DESCARTE")
    print("=" * 80)
    print()
    
    # Buscar propriedades
    produtor = ProdutorRural.objects.filter(nome__icontains='Marcelo Sanguino').first()
    if not produtor:
        print("[ERRO] Produtor Marcelo Sanguino não encontrado!")
        return
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    print(f"[OK] Propriedades encontradas: {propriedades.count()}")
    print()
    
    ano_inicio = 2022
    ano_fim = 2025
    
    # 1. Corrigir faturamento
    corrigir_faturamento(propriedades, ano_inicio, ano_fim)
    
    # 2. Corrigir vacas de descarte
    corrigir_vacas_descarte(propriedades, ano_inicio, ano_fim)
    
    print("=" * 80)
    print("[OK] CORREÇÕES CONCLUÍDAS!")
    print("=" * 80)
    print()
    print("Resumo das correções:")
    print("  - Faturamento ajustado para R$ 14-16 milhões/ano")
    print("  - Vacas de descarte = 20% das matrizes do ano anterior")
    print("  - Descarte transferido para Invernada Grande em julho")
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

