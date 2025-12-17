# -*- coding: utf-8 -*-
"""
Script para verificar promoções de Vacas Descarte na Canta Galo
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal, PlanejamentoAnual
from datetime import date

canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')

planejamento = PlanejamentoAnual.objects.filter(
    propriedade=canta_galo
).order_by('-data_criacao', '-ano').first()

print("=" * 80)
print("VERIFICAR PROMOCOES VACAS DESCARTE CANTA GALO")
print("=" * 80)

print(f"\n[INFO] Planejamento: {planejamento.codigo}")

# Buscar todas as promoções
promocoes = MovimentacaoProjetada.objects.filter(
    propriedade=canta_galo,
    categoria=categoria_descarte,
    tipo_movimentacao='PROMOCAO_ENTRADA',
    planejamento=planejamento
).order_by('data_movimentacao')

print(f"\n[INFO] Promocoes encontradas: {promocoes.count()}")

for promocao in promocoes:
    print(f"  {promocao.data_movimentacao.strftime('%d/%m/%Y')}: +{promocao.quantidade} - {promocao.observacao}")

# Verificar saldo por ano considerando todas as movimentações
print(f"\n[VERIFICACAO SALDO POR ANO]")
anos = [2022, 2023, 2024, 2025, 2026]

for ano in anos:
    # Buscar inventário
    from gestao_rural.models import InventarioRebanho
    inventario = InventarioRebanho.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        data_inventario__lte=date(ano, 12, 31)
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Se não há inventário para este ano, calcular saldo final do ano anterior
    if not inventario or inventario.data_inventario.year < ano:
        if ano > 2022:
            # Calcular saldo final do ano anterior recursivamente
            # Começar com inventário inicial
            inventario_inicial = InventarioRebanho.objects.filter(
                propriedade=canta_galo,
                categoria=categoria_descarte,
                data_inventario__lte=date(2022, 12, 31)
            ).order_by('-data_inventario').first()
            
            saldo = inventario_inicial.quantidade if inventario_inicial else 0
            
            # Processar todas as movimentações desde 2022 até o ano anterior
            for ano_anterior in range(2022, ano):
                movimentacoes_anterior = MovimentacaoProjetada.objects.filter(
                    propriedade=canta_galo,
                    categoria=categoria_descarte,
                    data_movimentacao__year=ano_anterior,
                    planejamento=planejamento
                ).order_by('data_movimentacao')
                
                for mov in movimentacoes_anterior:
                    if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA']:
                        saldo += mov.quantidade
                    elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
                        saldo -= mov.quantidade
    
    # Adicionar movimentações do ano
    movimentacoes_ano = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        data_movimentacao__year=ano,
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    for mov in movimentacoes_ano:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    print(f"  {ano}: Saldo final = {saldo}")

print(f"\n[OK] Verificacao concluida!")

