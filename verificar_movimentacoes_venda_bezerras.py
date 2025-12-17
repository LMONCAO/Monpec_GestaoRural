# -*- coding: utf-8 -*-
"""
Script para verificar movimentações de venda de bezerras fêmeas
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
    """Verifica movimentações de venda de bezerras fêmeas"""
    
    print("=" * 80)
    print("VERIFICAR MOVIMENTACOES DE VENDA DE BEZERRAS FEMEAS")
    print("=" * 80)
    
    # Buscar categoria
    try:
        categoria_bezerra = CategoriaAnimal.objects.get(nome__icontains='Bezerro(a) 0-12 F')
    except CategoriaAnimal.DoesNotExist:
        print("[ERRO] Categoria Bezerro(a) 0-12 F não encontrada")
        return
    
    print(f"\n[INFO] Categoria: {categoria_bezerra.nome}")
    
    # Buscar TODAS as movimentações de venda de bezerras fêmeas
    vendas = MovimentacaoProjetada.objects.filter(
        categoria=categoria_bezerra,
        tipo_movimentacao='VENDA'
    ).select_related('propriedade', 'planejamento').order_by('data_movimentacao')
    
    print(f"\n[MOVIMENTACOES DE VENDA DE BEZERRAS FEMEAS]")
    print(f"  Total: {vendas.count()}")
    
    total_valor = 0
    total_quantidade = 0
    
    for venda in vendas[:20]:  # Mostrar primeiras 20
        valor = venda.valor_total if venda.valor_total else (venda.valor_por_cabeca * venda.quantidade if venda.valor_por_cabeca else 0)
        print(f"    {venda.data_movimentacao.strftime('%d/%m/%Y')}: {venda.quantidade} bezerras - R$ {valor:,.2f}")
        print(f"      Fazenda: {venda.propriedade.nome_propriedade if venda.propriedade else 'N/A'}")
        print(f"      Planejamento: {venda.planejamento.codigo if venda.planejamento else 'N/A'}")
        print(f"      Observacao: {venda.observacao[:50] if venda.observacao else 'N/A'}")
        total_valor += valor if valor else 0
        total_quantidade += venda.quantidade
    
    print(f"\n[RESUMO]")
    print(f"  Total de bezerras vendidas: {total_quantidade}")
    print(f"  Valor total das vendas: R$ {total_valor:,.2f}")
    
    # Calcular quantos garrotes podem ser comprados
    preco_garrote = 2660.00
    garrotes_possiveis = int(total_valor / preco_garrote) if total_valor > 0 else 0
    print(f"  Garrotes que podem ser comprados: {garrotes_possiveis} (R$ {preco_garrote:,.2f} cada)")
    
    # Agrupar por ano
    vendas_por_ano = defaultdict(list)
    for venda in vendas:
        ano = venda.data_movimentacao.year
        vendas_por_ano[ano].append(venda)
    
    print(f"\n[VENDAS POR ANO]")
    for ano in sorted(vendas_por_ano.keys()):
        vendas_ano = vendas_por_ano[ano]
        total_ano = sum(v.quantidade for v in vendas_ano)
        valor_ano = sum(v.valor_total if v.valor_total else (v.valor_por_cabeca * v.quantidade if v.valor_por_cabeca else 0) for v in vendas_ano)
        print(f"  {ano}: {len(vendas_ano)} vendas, {total_ano} bezerras, R$ {valor_ano:,.2f}")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











