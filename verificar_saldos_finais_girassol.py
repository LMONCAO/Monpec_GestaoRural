# -*- coding: utf-8 -*-
"""
Script para verificar saldos finais da Girassol por ano
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, MovimentacaoProjetada, CategoriaAnimal, PlanejamentoAnual, InventarioRebanho
from datetime import date

girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
planejamento = PlanejamentoAnual.objects.filter(propriedade=girassol).order_by('-data_criacao', '-ano').first()

print("=" * 80)
print("VERIFICAR SALDOS FINAIS GIRASSOL")
print("=" * 80)

saldos_desejados = {
    2022: 300,
    2023: 250,
    2024: 400,
    2025: 320
}

anos = [2022, 2023, 2024, 2025, 2026]

for ano in anos:
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=girassol,
        categoria=categoria_boi,
        data_inventario__lte=date(ano, 12, 31)
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Se não há inventário para este ano, usar saldo final do ano anterior
    if not inventario or inventario.data_inventario.year < ano:
        if ano > 2022:
            # Calcular saldo final do ano anterior
            inventario_anterior = InventarioRebanho.objects.filter(
                propriedade=girassol,
                categoria=categoria_boi,
                data_inventario__lte=date(ano - 1, 12, 31)
            ).order_by('-data_inventario').first()
            
            saldo = inventario_anterior.quantidade if inventario_anterior else 0
            
            # Adicionar movimentações do ano anterior
            movimentacoes_anterior = MovimentacaoProjetada.objects.filter(
                propriedade=girassol,
                categoria=categoria_boi,
                data_movimentacao__year=ano - 1,
                planejamento=planejamento
            ).order_by('data_movimentacao')
            
            for mov in movimentacoes_anterior:
                if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA']:
                    saldo += mov.quantidade
                elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
                    saldo -= mov.quantidade
    
    # Movimentações do ano
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        categoria=categoria_boi,
        data_movimentacao__year=ano,
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    desejado = saldos_desejados.get(ano, None)
    status = "OK" if (desejado is None or saldo == desejado) else "AJUSTAR"
    
    print(f"\n{ano}: Saldo final = {saldo}", end="")
    if desejado is not None:
        print(f" (desejado: {desejado}) [{status}]")
    else:
        print()

print(f"\n[OK] Verificacao concluida!")

