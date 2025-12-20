# -*- coding: utf-8 -*-
"""
Script para verificar e corrigir vendas na Fazenda Girassol.
Garante que as vendas acontecem apenas após as evoluções.
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from decimal import Decimal
from datetime import date
from django.db import transaction, connection
from collections import defaultdict

from gestao_rural.models import (
    Propriedade, CategoriaAnimal, MovimentacaoProjetada, 
    VendaProjetada
)


def calcular_saldo_antes_venda(propriedade, categoria, data_venda):
    """Calcula o saldo disponível antes de uma venda"""
    from gestao_rural.models import InventarioRebanho
    
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario__lte=data_venda
    ).order_by('-data_inventario').first()
    
    saldo = 0
    data_inventario = None
    
    if inventario_inicial:
        data_inventario = inventario_inicial.data_inventario
        inventarios = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario=data_inventario,
            categoria=categoria
        )
        saldo = sum(inv.quantidade for inv in inventarios)
    
    filtro_data = {}
    if data_inventario:
        filtro_data = {'data_movimentacao__gt': data_inventario}
    
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_venda,
        **filtro_data
    )
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['NASCIMENTO', 'COMPRA', 'TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
            saldo -= mov.quantidade
            if saldo < 0:
                saldo = 0
    
    return saldo


@transaction.atomic
def verificar_e_corrigir_vendas_girassol():
    """Verifica e corrige vendas na Fazenda Girassol"""
    
    try:
        girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
        print(f"[OK] Propriedade encontrada: {girassol.nome_propriedade}")
    except:
        print("[ERRO] Propriedade 'Girassol' nao encontrada")
        return
    
    try:
        categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
        print(f"[OK] Categoria encontrada: {categoria_boi.nome}")
    except:
        print("[ERRO] Categoria 'Boi 24-36 M' nao encontrada")
        return
    
    # Buscar todas as vendas de Boi 24-36 M
    vendas = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='VENDA',
        categoria=categoria_boi,
        data_movimentacao__year__in=[2022, 2023]
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Vendas encontradas: {vendas.count()}")
    
    vendas_corrigidas = 0
    
    for venda in vendas:
        data_venda = venda.data_movimentacao
        quantidade_venda = venda.quantidade
        
        # Calcular saldo disponível ANTES desta venda
        saldo_disponivel = calcular_saldo_antes_venda(girassol, categoria_boi, data_venda)
        
        print(f"\n   Venda: {data_venda.strftime('%d/%m/%Y')} - {quantidade_venda} cabecas")
        print(f"   Saldo disponivel antes da venda: {saldo_disponivel}")
        
        if saldo_disponivel < quantidade_venda:
            print(f"   [AVISO] Saldo insuficiente! Ajustando quantidade de {quantidade_venda} para {saldo_disponivel}")
            
            # Ajustar quantidade da venda
            venda.quantidade = saldo_disponivel
            if venda.valor_por_cabeca:
                venda.valor_total = venda.valor_por_cabeca * Decimal(str(saldo_disponivel))
            venda.observacao = f"{venda.observacao or ''} [CORRIGIDO: quantidade ajustada de {quantidade_venda} para {saldo_disponivel}]"
            venda.save()
            
            # Ajustar venda projetada associada
            venda_projetada = VendaProjetada.objects.filter(movimentacao_projetada=venda).first()
            if venda_projetada:
                venda_projetada.quantidade = saldo_disponivel
                if venda_projetada.valor_por_animal:
                    venda_projetada.valor_total = venda_projetada.valor_por_animal * Decimal(str(saldo_disponivel))
                    if venda_projetada.peso_medio_kg:
                        venda_projetada.peso_total_kg = venda_projetada.peso_medio_kg * Decimal(str(saldo_disponivel))
                venda_projetada.save()
            
            vendas_corrigidas += 1
        else:
            print(f"   [OK] Saldo suficiente")
    
    print(f"\n[OK] Concluido!")
    print(f"   Vendas corrigidas: {vendas_corrigidas}")


if __name__ == '__main__':
    print("=" * 60)
    print("VERIFICACAO E CORRECAO DE VENDAS - GIRASSOL")
    print("=" * 60)
    print("\nEste script ira:")
    print("1. Verificar vendas de Boi 24-36 M na Fazenda Girassol")
    print("2. Ajustar quantidades se o saldo for insuficiente")
    print("\n" + "=" * 60 + "\n")
    
    try:
        verificar_e_corrigir_vendas_girassol()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























