# -*- coding: utf-8 -*-
"""
Script para corrigir os problemas identificados na verificação
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


def aguardar_banco_livre(max_tentativas=30, intervalo=3):
    """Aguarda o banco de dados ficar livre"""
    for tentativa in range(max_tentativas):
        try:
            with connection.cursor() as cursor:
                cursor.execute("BEGIN IMMEDIATE")
                cursor.execute("ROLLBACK")
            return True
        except Exception:
            if tentativa < max_tentativas - 1:
                time.sleep(intervalo)
            else:
                return False
    return False


@transaction.atomic
def corrigir_problemas():
    """Corrige os problemas identificados"""
    
    print("=" * 80)
    print("CORRIGIR PROBLEMAS IDENTIFICADOS")
    print("=" * 80)
    
    # Buscar propriedades
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    
    # Buscar categorias
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    # Buscar planejamentos
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada_grande
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    # ========== PROBLEMA 1: Transferências de Vacas Descarte ==========
    print("\n[PROBLEMA 1] Corrigindo transferencias de Vacas Descarte...")
    
    saidas_descarte = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte
    ).order_by('data_movimentacao')
    
    entradas_descarte = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte
    )
    
    print(f"   Saidas encontradas: {saidas_descarte.count()}")
    print(f"   Entradas existentes: {entradas_descarte.count()}")
    
    # Criar entradas correspondentes
    entradas_criadas = 0
    for saida in saidas_descarte:
        entrada_existente = entradas_descarte.filter(
            data_movimentacao=saida.data_movimentacao,
            quantidade=saida.quantidade
        ).first()
        
        if not entrada_existente:
            MovimentacaoProjetada.objects.create(
                propriedade=invernada_grande,
                categoria=categoria_descarte,
                data_movimentacao=saida.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=saida.quantidade,
                planejamento=planejamento_invernada,
                observacao=f'Transferencia de Canta Galo - {saida.quantidade} vacas descarte'
            )
            entradas_criadas += 1
            print(f"   [OK] Entrada criada: {saida.quantidade} em {saida.data_movimentacao.strftime('%d/%m/%Y')}")
    
    print(f"   [OK] {entradas_criadas} entradas criadas")
    
    # ========== PROBLEMA 2: Transferências de Garrotes Canta -> Favo ==========
    print("\n[PROBLEMA 2] Corrigindo transferencias de Garrotes Canta -> Favo...")
    
    # Buscar entradas no Favo de Mel
    entradas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    # Buscar saídas da Canta Galo
    saidas_canta = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote
    )
    
    print(f"   Entradas no Favo de Mel: {entradas_favo.count()}")
    print(f"   Saidas da Canta Galo: {saidas_canta.count()}")
    
    # Criar saídas correspondentes
    saidas_criadas = 0
    for entrada in entradas_favo:
        saida_existente = saidas_canta.filter(
            data_movimentacao=entrada.data_movimentacao,
            quantidade=entrada.quantidade
        ).first()
        
        if not saida_existente:
            MovimentacaoProjetada.objects.create(
                propriedade=canta_galo,
                categoria=categoria_garrote,
                data_movimentacao=entrada.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                quantidade=entrada.quantidade,
                planejamento=planejamento_canta,
                observacao=f'Transferencia para Favo de Mel - {entrada.quantidade} garrotes'
            )
            saidas_criadas += 1
            print(f"   [OK] Saida criada: {entrada.quantidade} em {entrada.data_movimentacao.strftime('%d/%m/%Y')}")
    
    print(f"   [OK] {saidas_criadas} saidas criadas")
    
    # ========== PROBLEMA 3: Vendas faltantes na Girassol ==========
    print("\n[PROBLEMA 3] Verificando vendas faltantes na Girassol...")
    
    from gestao_rural.models import Propriedade as Prop
    girassol = Prop.objects.get(nome_propriedade__icontains='Girassol')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    evolucoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='PROMOCAO_ENTRADA',
        categoria=categoria_boi
    ).order_by('data_movimentacao')
    
    vendas = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='VENDA',
        categoria=categoria_boi
    )
    
    total_evolucoes = sum(e.quantidade for e in evolucoes)
    total_vendas = sum(v.quantidade for v in vendas)
    
    print(f"   Total evolucoes: {total_evolucoes}")
    print(f"   Total vendas: {total_vendas}")
    print(f"   Diferenca: {total_evolucoes - total_vendas}")
    
    if total_evolucoes > total_vendas:
        print(f"   [AVISO] Faltam {total_evolucoes - total_vendas} vendas")
        print(f"   Execute o script criar_vendas_90_dias_apos_evolucao_girassol.py para criar as vendas faltantes")
    
    print(f"\n[OK] Correcoes concluidas!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_problemas()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















