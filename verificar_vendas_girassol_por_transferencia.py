# -*- coding: utf-8 -*-
"""
Script para verificar se as vendas da Girassol correspondem às transferências recebidas
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import timedelta
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def verificar():
    """Verifica se as vendas correspondem às transferências"""
    
    print("=" * 80)
    print("VERIFICAR VENDAS GIRASSOL POR TRANSFERENCIA")
    print("=" * 80)
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamento
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"\n[INFO] Planejamento: {planejamento.codigo if planejamento else 'Nenhum'}")
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    # Buscar transferências de entrada
    entradas = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    print(f"\n[TRANSFERENCIAS DE ENTRADA]")
    print(f"  Total: {entradas.count()}")
    
    # Para cada entrada, verificar se há venda correspondente (90 dias depois)
    print(f"\n[VERIFICACAO: ENTRADA -> VENDA (90 DIAS)]")
    
    total_entradas = 0
    total_vendido = 0
    
    for entrada in entradas:
        data_entrada = entrada.data_movimentacao
        quantidade_entrada = entrada.quantidade
        data_venda_esperada = data_entrada + timedelta(days=90)
        
        # Buscar vendas próximas à data esperada (tolerância de 5 dias)
        vendas = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            categoria=categoria_boi,
            tipo_movimentacao='VENDA',
            planejamento=planejamento,
            data_movimentacao__gte=data_venda_esperada - timedelta(days=5),
            data_movimentacao__lte=data_venda_esperada + timedelta(days=5)
        )
        
        total_vendido_entrada = sum(v.quantidade for v in vendas)
        
        status = "OK" if total_vendido_entrada == quantidade_entrada else "ERRO"
        
        print(f"\n  Entrada: {data_entrada.strftime('%d/%m/%Y')} - {quantidade_entrada} garrotes")
        print(f"    Venda esperada: {data_venda_esperada.strftime('%d/%m/%Y')} - {quantidade_entrada} bois")
        print(f"    Vendas encontradas: {vendas.count()}")
        print(f"    Total vendido: {total_vendido_entrada} bois")
        print(f"    Status: {status}")
        
        if vendas.count() > 0:
            for venda in vendas:
                print(f"      {venda.data_movimentacao.strftime('%d/%m/%Y')}: {venda.quantidade} bois")
        
        total_entradas += quantidade_entrada
        total_vendido += total_vendido_entrada
    
    print(f"\n[RESUMO]")
    print(f"  Total recebido: {total_entradas} garrotes")
    print(f"  Total vendido: {total_vendido} bois")
    print(f"  Diferença: {total_entradas - total_vendido}")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











