# -*- coding: utf-8 -*-
"""
Script para garantir que as correções sejam mantidas após gerar uma nova projeção
Este script deve ser executado APÓS gerar uma nova projeção
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
    PlanejamentoAnual, InventarioRebanho
)

print("=" * 80)
print("GARANTIR CORRECOES APOS NOVA PROJECAO")
print("=" * 80)
print("\n[AVISO] Este script deve ser executado APOS gerar uma nova projecao")
print("[AVISO] Ele vai verificar e recriar correcoes necessarias")
print("\n[INFO] Executando automaticamente...")


def calcular_saldo_disponivel(propriedade, categoria, data_referencia):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
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
            if saldo < 0:
                saldo = 0
    
    return saldo


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
def garantir_correcoes():
    """Garante que as correções sejam mantidas"""
    
    print("\n[1] Verificando transferencias Canta Galo -> Invernada Grande (Vacas Descarte)")
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    # Verificar transferência de 2022
    saida_2022 = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte,
        data_movimentacao__year=2022
    ).first()
    
    if not saida_2022:
        saldo_disponivel = calcular_saldo_disponivel(canta_galo, categoria_descarte, date(2022, 1, 15))
        if saldo_disponivel >= 512:
            MovimentacaoProjetada.objects.create(
                propriedade=canta_galo,
                categoria=categoria_descarte,
                data_movimentacao=date(2022, 1, 15),
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                quantidade=512,
                planejamento=planejamento_canta,
                observacao='Transferencia para Invernada Grande - 512 vacas descarte (ano 2022)'
            )
            print("  [OK] Transferencia SAIDA 2022 criada")
            
            MovimentacaoProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                data_movimentacao=date(2022, 1, 15),
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=512,
                planejamento=planejamento_invernada,
                observacao='Transferencia de Canta Galo - 512 vacas descarte (ano 2022)'
            )
            print("  [OK] Transferencia ENTRADA 2022 criada")
    
    print("\n[2] Verificando transferencias Canta Galo -> Favo de Mel (Garrotes)")
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    # Verificar se há saídas sem entradas correspondentes
    saidas_canta = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote
    )
    
    for saida in saidas_canta:
        entrada_correspondente = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_garrote,
            data_movimentacao=saida.data_movimentacao,
            quantidade=saida.quantidade
        ).first()
        
        if not entrada_correspondente:
            MovimentacaoProjetada.objects.create(
                propriedade=favo_mel,
                categoria=categoria_garrote,
                data_movimentacao=saida.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=saida.quantidade,
                planejamento=planejamento_favo,
                observacao=f'Transferencia de Canta Galo - {saida.quantidade} garrotes'
            )
            print(f"  [OK] Entrada criada: {saida.quantidade} em {saida.data_movimentacao.strftime('%d/%m/%Y')}")
    
    print("\n[3] Verificando transferencias Favo de Mel -> Girassol (Garrotes)")
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    # Verificar se há saídas sem entradas correspondentes
    saidas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote
    )
    
    for saida in saidas_favo:
        entrada_correspondente = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_garrote,
            data_movimentacao=saida.data_movimentacao,
            quantidade=saida.quantidade
        ).first()
        
        if not entrada_correspondente:
            MovimentacaoProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria_garrote,
                data_movimentacao=saida.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=saida.quantidade,
                planejamento=planejamento_girassol,
                observacao=f'Entrada de {saida.quantidade} garrotes de {favo_mel.nome_propriedade}'
            )
            print(f"  [OK] Entrada criada: {saida.quantidade} em {saida.data_movimentacao.strftime('%d/%m/%Y')}")
    
    print("\n[OK] Correcoes garantidas!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        print("[ERRO] Banco de dados bloqueado")
        sys.exit(1)
    
    try:
        garantir_correcoes()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

