# -*- coding: utf-8 -*-
"""
Script para verificar vendas de bezerras fêmeas
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
    PlanejamentoAnual, VendaProjetada
)


def verificar():
    """Verifica vendas de bezerras fêmeas"""
    
    print("=" * 80)
    print("VERIFICAR VENDAS DE BEZERRAS FEMEAS")
    print("=" * 80)
    
    # Buscar categoria
    try:
        categoria_bezerra = CategoriaAnimal.objects.get(nome__icontains='Bezerro(a) 0-12 F')
    except CategoriaAnimal.DoesNotExist:
        print("[ERRO] Categoria Bezerro(a) 0-12 F não encontrada")
        return
    
    print(f"\n[INFO] Categoria: {categoria_bezerra.nome}")
    
    # Buscar TODAS as vendas de bezerras fêmeas
    vendas = VendaProjetada.objects.filter(
        categoria=categoria_bezerra
    ).select_related('movimentacao_projetada', 'movimentacao_projetada__propriedade', 'movimentacao_projetada__planejamento')
    
    print(f"\n[VENDAS DE BEZERRAS FEMEAS]")
    print(f"  Total: {vendas.count()}")
    
    total_valor = 0
    total_quantidade = 0
    
    for venda in vendas[:20]:  # Mostrar primeiras 20
        mov = venda.movimentacao_projetada
        if mov:
            valor = venda.valor_total if venda.valor_total else (venda.valor_por_kg * venda.peso_medio_kg * venda.quantidade if venda.valor_por_kg and venda.peso_medio_kg else 0)
            print(f"    {venda.data_venda.strftime('%d/%m/%Y')}: {venda.quantidade} bezerras - R$ {valor:,.2f}")
            print(f"      Fazenda: {mov.propriedade.nome_propriedade if mov.propriedade else 'N/A'}")
            print(f"      Planejamento: {mov.planejamento.codigo if mov.planejamento else 'N/A'}")
            total_valor += valor if valor else 0
            total_quantidade += venda.quantidade
    
    print(f"\n[RESUMO]")
    print(f"  Total de bezerras vendidas: {total_quantidade}")
    print(f"  Valor total das vendas: R$ {total_valor:,.2f}")
    
    # Calcular quantos garrotes podem ser comprados
    preco_garrote = 2660.00
    garrotes_possiveis = int(total_valor / preco_garrote) if total_valor > 0 else 0
    print(f"  Garrotes que podem ser comprados: {garrotes_possiveis} (R$ {preco_garrote:,.2f} cada)")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











