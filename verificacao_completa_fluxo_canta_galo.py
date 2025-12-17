# -*- coding: utf-8 -*-
"""
Script completo para verificar todo o fluxo partindo da Fazenda Canta Galo
Verifica:
1. Transferências de saída da Canta Galo
2. Transferências de entrada nas propriedades de destino
3. Evoluções
4. Vendas
5. Saldos negativos
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
    InventarioRebanho, PlanejamentoAnual
)


def calcular_saldo_por_data(propriedade, categoria, data_referencia):
    """Calcula o saldo de uma categoria em uma data específica"""
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario__lte=data_referencia
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


def verificar_fluxo_completo():
    """Verifica todo o fluxo partindo da Canta Galo"""
    
    print("=" * 80)
    print("VERIFICACAO COMPLETA DO FLUXO - FAZENDA CANTA GALO")
    print("=" * 80)
    
    # Buscar propriedades
    try:
        canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
        invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
        favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
        girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    except:
        print("[ERRO] Propriedades nao encontradas")
        return
    
    # Buscar categorias
    try:
        categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
        categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
        categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    except:
        print("[ERRO] Categorias nao encontradas")
        return
    
    problemas = []
    avisos = []
    
    # ========== 1. VERIFICAR TRANSFERÊNCIAS DE VACAS DESCARTE ==========
    print("\n" + "=" * 80)
    print("1. TRANSFERENCIAS DE VACAS DESCARTE (Canta Galo -> Invernada Grande)")
    print("=" * 80)
    
    saidas_descarte = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de SAIDA da Canta Galo: {saidas_descarte.count()}")
    total_saida_descarte = 0
    for s in saidas_descarte:
        total_saida_descarte += s.quantidade
        print(f"   - {s.data_movimentacao.strftime('%d/%m/%Y')}: {s.quantidade} (obs: {s.observacao[:50] if s.observacao else 'Sem obs'})")
    
    entradas_descarte = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de ENTRADA na Invernada Grande: {entradas_descarte.count()}")
    total_entrada_descarte = 0
    for e in entradas_descarte:
        total_entrada_descarte += e.quantidade
        print(f"   + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade}")
    
    if total_saida_descarte != total_entrada_descarte:
        problemas.append(f"Vacas Descarte: Saida ({total_saida_descarte}) != Entrada ({total_entrada_descarte})")
    else:
        print(f"\n[OK] Transferencias de vacas descarte estao balanceadas: {total_saida_descarte}")
    
    # Verificar vendas na Invernada Grande
    vendas_invernada = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='VENDA',
        categoria=categoria_descarte
    ).order_by('data_movimentacao')
    
    total_vendas_invernada = sum(v.quantidade for v in vendas_invernada)
    print(f"\n[INFO] Vendas na Invernada Grande: {vendas_invernada.count()} vendas, total: {total_vendas_invernada}")
    
    if total_vendas_invernada != total_entrada_descarte:
        avisos.append(f"Invernada Grande: Vendas ({total_vendas_invernada}) != Entradas ({total_entrada_descarte})")
    
    # ========== 2. VERIFICAR TRANSFERÊNCIAS DE GARROTES ==========
    print("\n" + "=" * 80)
    print("2. TRANSFERENCIAS DE GARROTES (Canta Galo -> Favo de Mel)")
    print("=" * 80)
    
    # Buscar entradas no Favo de Mel primeiro
    entradas_garrote_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    # Buscar todas as saídas de garrotes da Canta Galo
    todas_saidas_garrote_canta = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    # Filtrar apenas as que correspondem às entradas no Favo de Mel
    saidas_garrote_canta = []
    for entrada in entradas_garrote_favo:
        saida_correspondente = todas_saidas_garrote_canta.filter(
            data_movimentacao=entrada.data_movimentacao,
            quantidade=entrada.quantidade
        ).first()
        if saida_correspondente:
            saidas_garrote_canta.append(saida_correspondente)
    
    print(f"\n[INFO] Transferencias de SAIDA da Canta Galo para Favo de Mel: {len(saidas_garrote_canta)}")
    total_saida_garrote_canta = 0
    for s in saidas_garrote_canta:
        total_saida_garrote_canta += s.quantidade
        print(f"   - {s.data_movimentacao.strftime('%d/%m/%Y')}: {s.quantidade}")
    
    print(f"\n[INFO] Transferencias de ENTRADA no Favo de Mel: {entradas_garrote_favo.count()}")
    total_entrada_garrote_favo = 0
    for e in entradas_garrote_favo:
        total_entrada_garrote_favo += e.quantidade
        print(f"   + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade}")
    
    if total_saida_garrote_canta != total_entrada_garrote_favo:
        problemas.append(f"Garrotes Canta->Favo: Saida ({total_saida_garrote_canta}) != Entrada ({total_entrada_garrote_favo})")
    else:
        print(f"\n[OK] Transferencias de garrotes Canta->Favo estao balanceadas: {total_saida_garrote_canta}")
    
    # ========== 3. VERIFICAR TRANSFERÊNCIAS FAVO DE MEL -> GIRASSOL ==========
    print("\n" + "=" * 80)
    print("3. TRANSFERENCIAS DE GARROTES (Favo de Mel -> Girassol)")
    print("=" * 80)
    
    saidas_garrote_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de SAIDA do Favo de Mel: {saidas_garrote_favo.count()}")
    total_saida_garrote_favo = 0
    for s in saidas_garrote_favo:
        total_saida_garrote_favo += s.quantidade
        print(f"   - {s.data_movimentacao.strftime('%d/%m/%Y')}: {s.quantidade}")
    
    entradas_garrote_girassol = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de ENTRADA no Girassol: {entradas_garrote_girassol.count()}")
    total_entrada_garrote_girassol = 0
    for e in entradas_garrote_girassol:
        total_entrada_garrote_girassol += e.quantidade
        print(f"   + {e.data_movimentacao.strftime('%d/%m/%Y')}: {e.quantidade}")
    
    if total_saida_garrote_favo != total_entrada_garrote_girassol:
        problemas.append(f"Garrotes Favo->Girassol: Saida ({total_saida_garrote_favo}) != Entrada ({total_entrada_garrote_girassol})")
    else:
        print(f"\n[OK] Transferencias de garrotes Favo->Girassol estao balanceadas: {total_saida_garrote_favo}")
    
    # Verificar saldo no Favo de Mel
    saldo_final_favo = calcular_saldo_por_data(favo_mel, categoria_garrote, date(2026, 12, 31))
    if saldo_final_favo < 0:
        problemas.append(f"Favo de Mel: Saldo negativo de garrotes: {saldo_final_favo}")
    else:
        print(f"\n[OK] Saldo final no Favo de Mel: {saldo_final_favo} (nao negativo)")
    
    # ========== 4. VERIFICAR EVOLUÇÕES NA GIRASSOL ==========
    print("\n" + "=" * 80)
    print("4. EVOLUCOES NA GIRASSOL (Garrote -> Boi)")
    print("=" * 80)
    
    evolucoes_saida = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='PROMOCAO_SAIDA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    evolucoes_entrada = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='PROMOCAO_ENTRADA',
        categoria=categoria_boi
    ).order_by('data_movimentacao')
    
    total_evolucoes_saida = sum(e.quantidade for e in evolucoes_saida)
    total_evolucoes_entrada = sum(e.quantidade for e in evolucoes_entrada)
    
    print(f"\n[INFO] Evolucoes SAIDA (Garrote): {evolucoes_saida.count()}, total: {total_evolucoes_saida}")
    print(f"[INFO] Evolucoes ENTRADA (Boi): {evolucoes_entrada.count()}, total: {total_evolucoes_entrada}")
    
    if total_evolucoes_saida != total_evolucoes_entrada:
        problemas.append(f"Girassol: Evolucoes SAIDA ({total_evolucoes_saida}) != ENTRADA ({total_evolucoes_entrada})")
    else:
        print(f"\n[OK] Evolucoes estao balanceadas: {total_evolucoes_saida}")
    
    # Verificar se todas as transferências têm evolução
    transferencias_sem_evolucao = []
    for entrada in entradas_garrote_girassol:
        data_evolucao_esperada = date(entrada.data_movimentacao.year + 1, entrada.data_movimentacao.month, 1)
        evolucao_existente = evolucoes_saida.filter(
            data_movimentacao__year=data_evolucao_esperada.year,
            data_movimentacao__month=data_evolucao_esperada.month,
            quantidade=entrada.quantidade
        ).first()
        
        if not evolucao_existente:
            transferencias_sem_evolucao.append(f"Transferencia de {entrada.data_movimentacao.strftime('%d/%m/%Y')}: {entrada.quantidade} garrotes sem evolucao")
    
    if transferencias_sem_evolucao:
        problemas.extend(transferencias_sem_evolucao)
    else:
        print(f"\n[OK] Todas as transferencias tem evolucao correspondente")
    
    # ========== 5. VERIFICAR VENDAS NA GIRASSOL ==========
    print("\n" + "=" * 80)
    print("5. VENDAS NA GIRASSOL (Bois)")
    print("=" * 80)
    
    vendas_girassol = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='VENDA',
        categoria=categoria_boi
    ).order_by('data_movimentacao')
    
    total_vendas_girassol = sum(v.quantidade for v in vendas_girassol)
    print(f"\n[INFO] Vendas na Girassol: {vendas_girassol.count()} vendas, total: {total_vendas_girassol}")
    
    if total_vendas_girassol < total_evolucoes_entrada:
        avisos.append(f"Girassol: Vendas ({total_vendas_girassol}) < Evolucoes ({total_evolucoes_entrada}) - Pode haver estoque acumulado")
    
    # Verificar saldos negativos
    print(f"\n[INFO] Verificando saldos negativos...")
    
    # Verificar saldo final na Girassol
    saldo_final_girassol_garrote = calcular_saldo_por_data(girassol, categoria_garrote, date(2026, 12, 31))
    saldo_final_girassol_boi = calcular_saldo_por_data(girassol, categoria_boi, date(2026, 12, 31))
    
    if saldo_final_girassol_garrote < 0:
        problemas.append(f"Girassol: Saldo negativo de garrotes: {saldo_final_girassol_garrote}")
    else:
        print(f"[OK] Saldo final de garrotes na Girassol: {saldo_final_girassol_garrote}")
    
    if saldo_final_girassol_boi < 0:
        problemas.append(f"Girassol: Saldo negativo de bois: {saldo_final_girassol_boi}")
    else:
        print(f"[OK] Saldo final de bois na Girassol: {saldo_final_girassol_boi}")
    
    # ========== RESUMO FINAL ==========
    print("\n" + "=" * 80)
    print("RESUMO FINAL")
    print("=" * 80)
    
    print(f"\n[RESUMO DE QUANTIDADES]")
    print(f"   Vacas Descarte:")
    print(f"      Canta Galo -> Invernada Grande: {total_saida_descarte}")
    print(f"      Vendas na Invernada Grande: {total_vendas_invernada}")
    print(f"   Garrotes:")
    print(f"      Canta Galo -> Favo de Mel: {total_saida_garrote_canta}")
    print(f"      Favo de Mel -> Girassol: {total_saida_garrote_favo}")
    print(f"      Evolucoes na Girassol: {total_evolucoes_entrada}")
    print(f"      Vendas na Girassol: {total_vendas_girassol}")
    
    if problemas:
        print(f"\n[PROBLEMAS ENCONTRADOS: {len(problemas)}]")
        for i, problema in enumerate(problemas, 1):
            print(f"   {i}. {problema}")
    else:
        print(f"\n[OK] Nenhum problema encontrado!")
    
    if avisos:
        print(f"\n[AVISOS: {len(avisos)}]")
        for i, aviso in enumerate(avisos, 1):
            print(f"   {i}. {aviso}")
    
    print(f"\n[OK] Verificacao concluida!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        verificar_fluxo_completo()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

