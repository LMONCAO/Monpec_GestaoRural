# -*- coding: utf-8 -*-
"""
Script para verificar saldos negativos em todas as fazendas e categorias
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from collections import defaultdict
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    InventarioRebanho
)


def calcular_saldo_final(propriedade, categoria, data_referencia):
    """Calcula o saldo final de uma categoria em uma data específica"""
    # Buscar inventário inicial
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = 0
    data_inventario = None
    
    if inventario_inicial:
        data_inventario = inventario_inicial.data_inventario
        saldo = inventario_inicial.quantidade
    
    filtro_data = {}
    if data_inventario:
        filtro_data = {'data_movimentacao__gt': data_inventario}
    
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia,
        **filtro_data
    ).order_by('data_movimentacao')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
            saldo -= mov.quantidade
    
    return saldo


print("=" * 80)
print("VERIFICAR SALDOS NEGATIVOS - TODAS AS FAZENDAS")
print("=" * 80)

# Buscar todas as propriedades
propriedades = Propriedade.objects.all().order_by('nome_propriedade')

# Buscar todas as categorias
categorias = CategoriaAnimal.objects.filter(ativo=True).order_by('nome')

# Anos para verificar
anos = [2022, 2023, 2024, 2025, 2026]

problemas_encontrados = []

for propriedade in propriedades:
    print(f"\n{'='*80}")
    print(f"FAZENDA: {propriedade.nome_propriedade}")
    print(f"{'='*80}")
    
    problemas_fazenda = []
    
    for categoria in categorias:
        for ano in anos:
            data_fim_ano = date(ano, 12, 31)
            saldo_final = calcular_saldo_final(propriedade, categoria, data_fim_ano)
            
            if saldo_final < 0:
                problemas_fazenda.append({
                    'categoria': categoria.nome,
                    'ano': ano,
                    'saldo': saldo_final
                })
                print(f"  [PROBLEMA] {categoria.nome} em {ano}: Saldo = {saldo_final}")
                
                # Verificar movimentações detalhadas
                movimentacoes = MovimentacaoProjetada.objects.filter(
                    propriedade=propriedade,
                    categoria=categoria,
                    data_movimentacao__year=ano
                ).order_by('data_movimentacao')
                
                print(f"    Movimentacoes em {ano}:")
                saldo_parcial = 0
                
                # Buscar inventário inicial
                inventario = InventarioRebanho.objects.filter(
                    propriedade=propriedade,
                    categoria=categoria,
                    data_inventario__lte=data_fim_ano
                ).order_by('-data_inventario').first()
                
                if inventario:
                    saldo_parcial = inventario.quantidade
                    print(f"      Inventario inicial: {saldo_parcial}")
                
                for mov in movimentacoes:
                    if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
                        saldo_parcial += mov.quantidade
                        sinal = '+'
                    elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
                        saldo_parcial -= mov.quantidade
                        sinal = '-'
                    else:
                        sinal = '?'
                    
                    obs_safe = mov.observacao.encode('ascii', 'ignore').decode('ascii') if mov.observacao else ''
                    print(f"      {sinal} {mov.data_movimentacao.strftime('%d/%m/%Y')}: {mov.quantidade} - {mov.tipo_movimentacao} (saldo: {saldo_parcial}) - {obs_safe[:40]}")
    
    if problemas_fazenda:
        problemas_encontrados.append({
            'propriedade': propriedade.nome_propriedade,
            'problemas': problemas_fazenda
        })
    else:
        print(f"  [OK] Nenhum saldo negativo encontrado")

# Resumo final
print(f"\n{'='*80}")
print("RESUMO FINAL")
print(f"{'='*80}")

if problemas_encontrados:
    print(f"\n[PROBLEMAS ENCONTRADOS: {len(problemas_encontrados)} fazendas]")
    for item in problemas_encontrados:
        print(f"\n  {item['propriedade']}:")
        for prob in item['problemas']:
            print(f"    - {prob['categoria']} em {prob['ano']}: Saldo = {prob['saldo']}")
else:
    print("\n[OK] Nenhum saldo negativo encontrado em nenhuma fazenda!")

print(f"\n[OK] Verificacao concluida!")










