# -*- coding: utf-8 -*-
"""
Script para verificar a projeção da Invernada Grande
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from django.db import transaction

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, InventarioRebanho
)


def calcular_saldo(propriedade, categoria, data_referencia, planejamento):
    """Calcula saldo em uma data específica"""
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Aplicar movimentações
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    return max(0, saldo)


def verificar_projecao():
    """Verifica a projeção da Invernada Grande"""
    
    print("=" * 80)
    print("VERIFICAR PROJECAO INVERNADA GRANDE")
    print("=" * 80)
    
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento:
        print("[ERRO] Planejamento nao encontrado")
        return
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo}")
    
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte
    ).first()
    
    if inventario:
        print(f"\n[INVENTARIO] {inventario.data_inventario.strftime('%d/%m/%Y')}: {inventario.quantidade} vacas")
    else:
        print("\n[INVENTARIO] Nenhum inventario encontrado")
    
    # Transferências de entrada
    entradas = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    print(f"\n[ENTRADAS] Total: {entradas.count()}")
    for entrada in entradas:
        print(f"  {entrada.data_movimentacao.strftime('%d/%m/%Y')}: +{entrada.quantidade} vacas")
    
    # Vendas
    vendas = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        tipo_movimentacao='VENDA',
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    print(f"\n[VENDAS] Total: {vendas.count()}")
    total_vendido = 0
    for venda in vendas:
        total_vendido += venda.quantidade
        print(f"  {venda.data_movimentacao.strftime('%d/%m/%Y')}: -{venda.quantidade} vacas")
    print(f"  Total vendido: {total_vendido} vacas")
    
    # Saldos por ano
    print(f"\n[SALDOS POR ANO]")
    for ano in [2022, 2023, 2024]:
        saldo_fim_ano = calcular_saldo(invernada, categoria_descarte, date(ano, 12, 31), planejamento)
        saldo_inicio_ano = calcular_saldo(invernada, categoria_descarte, date(ano, 1, 1), planejamento)
        print(f"  {ano}: Inicio={saldo_inicio_ano}, Fim={saldo_fim_ano}")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar_projecao()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










