# -*- coding: utf-8 -*-
"""
Script para verificar compras de garrotes no Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from collections import defaultdict
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def verificar():
    """Verifica compras de garrotes no Favo de Mel"""
    
    print("=" * 80)
    print("VERIFICAR COMPRAS FAVO DE MEL")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    # Buscar planejamento mais recente
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo}")
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    
    # Buscar compras
    compras = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='COMPRA',
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    print(f"\n[COMPRAS DE GARROTES]")
    print(f"  Total: {compras.count()}")
    
    total_garrotes = 0
    total_valor = 0
    
    for compra in compras:
        print(f"    {compra.data_movimentacao.strftime('%d/%m/%Y')}: {compra.quantidade} garrotes - R$ {compra.valor_total:,.2f}")
        print(f"      Observacao: {compra.observacao}")
        total_garrotes += compra.quantidade
        if compra.valor_total:
            total_valor += compra.valor_total
    
    print(f"\n[RESUMO]")
    print(f"  Total de garrotes comprados: {total_garrotes}")
    print(f"  Valor total investido: R$ {total_valor:,.2f}")
    
    # Agrupar por ano
    compras_por_ano = defaultdict(list)
    for compra in compras:
        ano = compra.data_movimentacao.year
        compras_por_ano[ano].append(compra)
    
    print(f"\n[COMPRAS POR ANO]")
    for ano in sorted(compras_por_ano.keys()):
        compras_ano = compras_por_ano[ano]
        total_ano = sum(c.quantidade for c in compras_ano)
        valor_ano = sum(c.valor_total for c in compras_ano if c.valor_total)
        print(f"  {ano}: {len(compras_ano)} compras, {total_ano} garrotes, R$ {valor_ano:,.2f}")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























