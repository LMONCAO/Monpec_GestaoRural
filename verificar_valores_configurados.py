# -*- coding: utf-8 -*-
"""
Script para verificar se os valores foram configurados corretamente
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, VendaProjetada, CategoriaAnimal
)


def verificar():
    """Verifica valores configurados"""
    
    print("=" * 80)
    print("VERIFICAR VALORES CONFIGURADOS")
    print("=" * 80)
    
    # Buscar categorias
    categoria_bezerra = CategoriaAnimal.objects.get(nome__icontains='Bezerro(a) 0-12 F')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    # Valores esperados
    valores_bezerras = {
        2022: 1900.00,
        2023: 1600.00,
        2024: 1875.00,
        2025: 2100.00,
    }
    
    valores_garrotes = {
        2022: 2300.00,
        2023: 2000.00,
        2024: 2280.00,
        2025: 2350.00,
    }
    
    valores_boi_gordo = {
        2022: 5700.00,
        2023: 4950.00,
        2024: 5890.00,
        2025: 6032.00,
    }
    
    # ========== 1. VENDAS DE BEZERRAS ==========
    print("\n[1. VENDAS DE BEZERRAS]")
    vendas_bezerras = MovimentacaoProjetada.objects.filter(
        categoria=categoria_bezerra,
        tipo_movimentacao='VENDA'
    ).order_by('data_movimentacao')
    
    for venda in vendas_bezerras[:10]:  # Primeiras 10
        ano = venda.data_movimentacao.year
        valor_esperado = valores_bezerras.get(ano, 0)
        valor_atual = float(venda.valor_por_cabeca) if venda.valor_por_cabeca else 0
        
        status = "OK" if abs(valor_atual - valor_esperado) < 0.01 else "ERRO"
        print(f"  {venda.data_movimentacao.strftime('%d/%m/%Y')} ({ano}): R$ {valor_atual:,.2f} (esperado: R$ {valor_esperado:,.2f}) [{status}]")
    
    # ========== 2. COMPRAS DE GARROTES ==========
    print("\n[2. COMPRAS DE GARROTES]")
    compras_garrotes = MovimentacaoProjetada.objects.filter(
        categoria=categoria_garrote,
        tipo_movimentacao='COMPRA'
    ).order_by('data_movimentacao')
    
    for compra in compras_garrotes[:10]:  # Primeiras 10
        ano = compra.data_movimentacao.year
        valor_esperado = valores_garrotes.get(ano, 0)
        valor_atual = float(compra.valor_por_cabeca) if compra.valor_por_cabeca else 0
        
        status = "OK" if abs(valor_atual - valor_esperado) < 0.01 else "ERRO"
        print(f"  {compra.data_movimentacao.strftime('%d/%m/%Y')} ({ano}): R$ {valor_atual:,.2f} (esperado: R$ {valor_esperado:,.2f}) [{status}]")
    
    # ========== 3. VENDAS DE BOI GORDO ==========
    print("\n[3. VENDAS DE BOI GORDO]")
    vendas_boi = MovimentacaoProjetada.objects.filter(
        categoria=categoria_boi,
        tipo_movimentacao='VENDA'
    ).order_by('data_movimentacao')
    
    print(f"  Total de vendas encontradas: {vendas_boi.count()}")
    
    for venda in vendas_boi[:10]:  # Primeiras 10
        ano = venda.data_movimentacao.year
        valor_esperado = valores_boi_gordo.get(ano, 0)
        valor_atual = float(venda.valor_por_cabeca) if venda.valor_por_cabeca else 0
        
        # Verificar VendaProjetada também
        venda_projetada = VendaProjetada.objects.filter(
            movimentacao_projetada=venda
        ).first()
        
        if venda_projetada:
            valor_total_vp = float(venda_projetada.valor_total) if venda_projetada.valor_total else 0
            valor_por_kg_vp = float(venda_projetada.valor_por_kg) if venda_projetada.valor_por_kg else 0
            print(f"  {venda.data_movimentacao.strftime('%d/%m/%Y')} ({ano}):")
            print(f"    Movimentacao: R$ {valor_atual:,.2f} (esperado: R$ {valor_esperado:,.2f})")
            print(f"    VendaProjetada: R$ {valor_total_vp:,.2f} total, R$ {valor_por_kg_vp:,.2f}/kg")
        else:
            status = "OK" if abs(valor_atual - valor_esperado) < 0.01 else "ERRO"
            print(f"  {venda.data_movimentacao.strftime('%d/%m/%Y')} ({ano}): R$ {valor_atual:,.2f} (esperado: R$ {valor_esperado:,.2f}) [{status}]")
    
    print("\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    try:
        verificar()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()










