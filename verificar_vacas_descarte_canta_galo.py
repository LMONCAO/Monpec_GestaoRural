# -*- coding: utf-8 -*-
"""
Script para verificar saldo de vacas descarte na Canta Galo
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date, timedelta
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, PlanejamentoAnual,
    InventarioRebanho
)


def calcular_saldo_disponivel(propriedade, categoria, data_referencia, planejamento):
    """Calcula saldo disponível ANTES da data de referência"""
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lt=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Aplicar movimentações ANTES da data (não incluir movimentações na própria data)
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lt=data_referencia,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    return max(0, saldo)  # Não permitir saldo negativo


def verificar():
    """Verifica saldo de vacas descarte na Canta Galo"""
    
    print("=" * 80)
    print("VERIFICAR VACAS DESCARTE CANTA GALO")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    
    # Buscar planejamento
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo if planejamento else 'Nenhum'}")
    
    # Buscar categoria
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    # Buscar TODAS as movimentações de vacas descarte
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    print(f"\n[MOVIMENTACOES DE VACAS DESCARTE]")
    print(f"  Total: {movimentacoes.count()}")
    
    # Verificar transferências de saída
    transferencias_saida = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    print(f"\n[TRANSFERENCIAS DE SAIDA]")
    print(f"  Total: {transferencias_saida.count()}")
    
    for saida in transferencias_saida:
        # Calcular saldo disponível ANTES desta transferência
        data_verificacao = saida.data_movimentacao - timedelta(days=1)
        saldo_disponivel = calcular_saldo_disponivel(
            canta_galo, categoria_descarte, data_verificacao, planejamento
        )
        
        # Calcular saldo após a transferência
        saldo_apos = saldo_disponivel - saida.quantidade
        
        status = "OK" if saldo_disponivel >= saida.quantidade else "ERRO"
        
        print(f"  {saida.data_movimentacao.strftime('%d/%m/%Y')}: {saida.quantidade} vacas")
        print(f"    Saldo antes: {saldo_disponivel}")
        print(f"    Saldo após: {saldo_apos}")
        print(f"    Status: {status}")
        
        if saldo_apos < 0:
            print(f"    [ERRO CRITICO] Saldo negativo após transferência!")
    
    # Verificar saldo final por ano
    print(f"\n[SALDO FINAL POR ANO]")
    for ano in [2022, 2023, 2024, 2025]:
        data_fim_ano = date(ano, 12, 31)
        saldo_fim_ano = calcular_saldo_disponivel(
            canta_galo, categoria_descarte, data_fim_ano, planejamento
        )
        
        # Aplicar movimentações do próprio dia 31/12
        movs_31_12 = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            data_movimentacao=data_fim_ano,
            planejamento=planejamento
        )
        
        for mov in movs_31_12:
            if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
                saldo_fim_ano += mov.quantidade
            elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
                saldo_fim_ano -= mov.quantidade
        
        status_ano = "OK" if saldo_fim_ano >= 0 else "ERRO"
        print(f"  {ano}: {saldo_fim_ano} vacas [{status_ano}]")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
