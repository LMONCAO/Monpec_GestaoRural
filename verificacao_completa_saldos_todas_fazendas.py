# -*- coding: utf-8 -*-
"""
Script para verificação completa de saldos e transferências em todas as fazendas
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
print("VERIFICACAO COMPLETA DE SALDOS - TODAS AS FAZENDAS")
print("=" * 80)

propriedades = Propriedade.objects.all().order_by('nome_propriedade')
categorias = CategoriaAnimal.objects.filter(ativo=True).order_by('nome')
anos = [2022, 2023, 2024, 2025, 2026]

problemas = []
aviso = []

for propriedade in propriedades:
    print(f"\n{'='*80}")
    print(f"FAZENDA: {propriedade.nome_propriedade}")
    print(f"{'='*80}")
    
    for categoria in categorias:
        saldos_por_ano = {}
        
        for ano in anos:
            saldo_final = calcular_saldo_final(propriedade, categoria, date(ano, 12, 31))
            saldos_por_ano[ano] = saldo_final
            
            if saldo_final < 0:
                problemas.append({
                    'propriedade': propriedade.nome_propriedade,
                    'categoria': categoria.nome,
                    'ano': ano,
                    'saldo': saldo_final
                })
        
        # Verificar se há movimentações mas saldo sempre zero
        movimentacoes = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            categoria=categoria,
            data_movimentacao__year__in=anos
        )
        
        if movimentacoes.exists() and all(s == 0 for s in saldos_por_ano.values()):
            # Verificar transferências
            saidas = MovimentacaoProjetada.objects.filter(
                propriedade=propriedade,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                categoria=categoria,
                data_movimentacao__year__in=anos
            )
            
            entradas = MovimentacaoProjetada.objects.filter(
                propriedade=propriedade,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                categoria=categoria,
                data_movimentacao__year__in=anos
            )
            
            total_saidas = sum(s.quantidade for s in saidas)
            total_entradas = sum(e.quantidade for e in entradas)
            
            if total_saidas != total_entradas:
                aviso.append({
                    'propriedade': propriedade.nome_propriedade,
                    'categoria': categoria.nome,
                    'saidas': total_saidas,
                    'entradas': total_entradas
                })
        
        # Mostrar apenas categorias com problemas ou movimentações significativas
        if any(s < 0 for s in saldos_por_ano.values()) or movimentacoes.count() > 5:
            print(f"\n  {categoria.nome}:")
            for ano in anos:
                saldo = saldos_por_ano[ano]
                if saldo < 0:
                    print(f"    {ano}: Saldo = {saldo} [PROBLEMA]")
                elif saldo > 0:
                    print(f"    {ano}: Saldo = {saldo}")

# Resumo
print(f"\n{'='*80}")
print("RESUMO FINAL")
print(f"{'='*80}")

if problemas:
    print(f"\n[PROBLEMAS ENCONTRADOS: {len(problemas)}]")
    for prob in problemas:
        print(f"  - {prob['propriedade']}: {prob['categoria']} em {prob['ano']} = {prob['saldo']}")
else:
    print(f"\n[OK] Nenhum saldo negativo encontrado!")

if aviso:
    print(f"\n[AVISOS: {len(aviso)}]")
    for av in aviso:
        print(f"  - {av['propriedade']}: {av['categoria']} - Saidas: {av['saidas']}, Entradas: {av['entradas']}")

print(f"\n[OK] Verificacao concluida!")











