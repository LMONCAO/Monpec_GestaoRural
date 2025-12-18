# -*- coding: utf-8 -*-
"""
Script para corrigir saldos negativos de vacas descarte na Canta Galo
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
def corrigir_saldos_negativos():
    """Corrige saldos negativos de vacas descarte"""
    
    print("=" * 80)
    print("CORRIGIR SALDOS NEGATIVOS - VACAS DESCARTE")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    # Buscar todas as transferências de saída de vacas descarte
    saidas = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de saida encontradas: {saidas.count()}")
    
    # Verificar cada transferência e deletar as que causam saldo negativo
    transferencias_deletadas = 0
    
    for saida in saidas:
        # Calcular saldo disponível ANTES da transferência
        saldo_antes = calcular_saldo_disponivel(canta_galo, categoria_descarte, saida.data_movimentacao)
        
        # Se o saldo disponível é menor que a quantidade a transferir, deletar a transferência
        if saldo_antes < saida.quantidade:
            print(f"  [PROBLEMA] {saida.data_movimentacao.strftime('%d/%m/%Y')}: Transferindo {saida.quantidade} mas saldo disponivel = {saldo_antes}")
            
            # Buscar entrada correspondente na Invernada Grande
            invernada_grande = Propriedade.objects.filter(nome_propriedade__icontains='Invernada Grande').first()
            if invernada_grande:
                entrada_correspondente = MovimentacaoProjetada.objects.filter(
                    propriedade=invernada_grande,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    categoria=categoria_descarte,
                    data_movimentacao=saida.data_movimentacao,
                    quantidade=saida.quantidade
                ).first()
                
                if entrada_correspondente:
                    # Deletar vendas relacionadas na Invernada Grande
                    from gestao_rural.models import VendaProjetada
                    vendas_relacionadas = MovimentacaoProjetada.objects.filter(
                        propriedade=invernada_grande,
                        tipo_movimentacao='VENDA',
                        categoria=categoria_descarte,
                        data_movimentacao__gte=saida.data_movimentacao,
                        data_movimentacao__year=saida.data_movimentacao.year
                    )
                    
                    vendas_projetadas = VendaProjetada.objects.filter(
                        movimentacao_projetada__in=vendas_relacionadas
                    )
                    vendas_projetadas.delete()
                    vendas_relacionadas.delete()
                    
                    entrada_correspondente.delete()
                    print(f"    [OK] Entrada correspondente deletada")
            
            saida.delete()
            print(f"    [OK] Transferencia de saida deletada")
            transferencias_deletadas += 1
        else:
            print(f"  [OK] {saida.data_movimentacao.strftime('%d/%m/%Y')}: Transferindo {saida.quantidade} (saldo disponivel: {saldo_antes})")
    
    # Verificar saldos finais após correção
    print(f"\n[VERIFICACAO DE SALDOS APOS CORRECAO]")
    anos = [2022, 2023, 2024, 2025, 2026]
    
    for ano in anos:
        saldo_final = calcular_saldo_disponivel(canta_galo, categoria_descarte, date(ano, 12, 31))
        if saldo_final < 0:
            print(f"  [AVISO] {ano}: Saldo ainda negativo = {saldo_final}")
        else:
            print(f"  [OK] {ano}: Saldo = {saldo_final}")
    
    print(f"\n[OK] Concluido!")
    print(f"   Transferencias deletadas: {transferencias_deletadas}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_saldos_negativos()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















