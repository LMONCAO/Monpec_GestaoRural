# -*- coding: utf-8 -*-
"""
Script para corrigir transferências do Favo de Mel para Girassol.
Regras:
1. Transferir 350 cabeças a cada 3 meses
2. Não deixar saldo negativo
3. Quando acabar o saldo, esperar novas entradas antes de transferir
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.db import transaction, connection
from calendar import monthrange
import time

from gestao_rural.models import (
    Propriedade, PlanejamentoAnual, MovimentacaoProjetada, 
    CategoriaAnimal, InventarioRebanho
)


def adicionar_meses(data, meses):
    """Adiciona meses a uma data"""
    ano = data.year
    mes = data.month + meses
    dia = data.day
    
    while mes > 12:
        mes -= 12
        ano += 1
    
    ultimo_dia_mes = monthrange(ano, mes)[1]
    if dia > ultimo_dia_mes:
        dia = ultimo_dia_mes
    
    return date(ano, mes, dia)


def calcular_saldo_disponivel(propriedade, categoria, data_referencia):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
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


@transaction.atomic
def corrigir_transferencias_favo_mel_para_girassol():
    """Corrige transferências do Favo de Mel para Girassol respeitando saldo"""
    
    print("=" * 60)
    print("CORRIGIR TRANSFERENCIAS FAVO DE MEL -> GIRASSOL")
    print("=" * 60)
    
    # Buscar propriedades
    try:
        favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
        girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
        print(f"\n[OK] Propriedades encontradas")
    except:
        print("[ERRO] Propriedades nao encontradas")
        return
    
    # Buscar categoria
    try:
        categoria = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
        print(f"[OK] Categoria: {categoria.nome}")
    except:
        print("[ERRO] Categoria nao encontrada")
        return
    
    # Buscar planejamentos
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_favo or not planejamento_girassol:
        print("[ERRO] Planejamentos nao encontrados")
        return
    
    print(f"[OK] Planejamento Favo de Mel: {planejamento_favo.codigo}")
    print(f"[OK] Planejamento Girassol: {planejamento_girassol.codigo}")
    
    # Buscar transferências de entrada no Favo de Mel
    transferencias_entrada = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de ENTRADA no Favo de Mel: {transferencias_entrada.count()}")
    for t in transferencias_entrada:
        print(f"   + {t.data_movimentacao.strftime('%d/%m/%Y')}: {t.quantidade}")
    
    # Buscar transferências de saída existentes
    transferencias_saida_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de SAIDA existentes: {transferencias_saida_existentes.count()}")
    
    # Excluir transferências de saída existentes para recriar corretamente
    if transferencias_saida_existentes.exists():
        print(f"[INFO] Excluindo {transferencias_saida_existentes.count()} transferencias de saida existentes...")
        transferencias_saida_existentes.delete()
    
    # Criar transferências de saída respeitando saldo
    # CONFIGURAÇÃO PADRÃO: 480 cabeças a cada 90 dias (3 meses), começando em abril/2022
    # Mas só transferir se houver saldo disponível
    
    data_primeira_transferencia = date(2022, 4, 1)
    quantidade_por_transferencia = 480  # CONFIGURAÇÃO PADRÃO: Alterado de 350 para 480
    intervalo_meses = 3  # 90 dias = 3 meses
    
    data_transferencia = data_primeira_transferencia
    ano_fim = 2026
    transferencias_criadas = 0
    
    # Agrupar entradas por data para facilitar cálculo
    entradas_por_data = {}
    for entrada in transferencias_entrada:
        ano = entrada.data_movimentacao.year
        if ano not in entradas_por_data:
            entradas_por_data[ano] = []
        entradas_por_data[ano].append(entrada)
    
    while data_transferencia.year <= ano_fim:
        # Calcular saldo disponível na data da transferência
        saldo_disponivel = calcular_saldo_disponivel(favo_mel, categoria, data_transferencia)
        
        if saldo_disponivel <= 0:
            print(f"   [AVISO] Sem saldo disponivel em {data_transferencia.strftime('%d/%m/%Y')} (saldo: {saldo_disponivel})")
            # Pular para próxima data
            data_transferencia = adicionar_meses(data_transferencia, intervalo_meses)
            continue
        
        # Quantidade a transferir: mínimo entre quantidade desejada e saldo disponível
        quantidade_transferir = min(quantidade_por_transferencia, saldo_disponivel)
        
        # Verificar se já existe transferência de entrada no Girassol para esta data
        entrada_girassol = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria,
            data_movimentacao=data_transferencia
        ).first()
        
        # Criar transferência de saída do Favo de Mel
        MovimentacaoProjetada.objects.create(
            propriedade=favo_mel,
            categoria=categoria,
            data_movimentacao=data_transferencia,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            quantidade=quantidade_transferir,
            planejamento=planejamento_favo,
            observacao=f'Transferencia para Girassol - {quantidade_transferir} garrotes (saldo disponivel: {saldo_disponivel})'
        )
        
        # Criar transferência de entrada no Girassol (sempre criar/atualizar)
        if not entrada_girassol:
            MovimentacaoProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria,
                data_movimentacao=data_transferencia,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=quantidade_transferir,
                planejamento=planejamento_girassol,
                observacao=f'Transferencia de Favo de Mel - {quantidade_transferir} garrotes'
            )
            print(f"   [OK] Transferencia ENTRADA criada no Girassol: {quantidade_transferir}")
        else:
            # Atualizar quantidade e planejamento se necessário
            if entrada_girassol.quantidade != quantidade_transferir or entrada_girassol.planejamento != planejamento_girassol:
                entrada_girassol.quantidade = quantidade_transferir
                entrada_girassol.planejamento = planejamento_girassol
                entrada_girassol.save()
                print(f"   [OK] Transferencia ENTRADA atualizada no Girassol: {quantidade_transferir}")
        
        print(f"   [OK] Transferencia criada: {quantidade_transferir} em {data_transferencia.strftime('%d/%m/%Y')} (saldo disponivel: {saldo_disponivel})")
        transferencias_criadas += 1
        
        # Próxima transferência: 3 meses depois
        data_transferencia = adicionar_meses(data_transferencia, intervalo_meses)
    
    print(f"\n[OK] Concluido!")
    print(f"   Transferencias criadas: {transferencias_criadas}")


if __name__ == '__main__':
    print("\nEste script ira:")
    print("1. Verificar transferencias de entrada no Favo de Mel")
    print("2. Criar transferencias de saida para Girassol (350 a cada 3 meses)")
    print("3. Respeitar saldo disponivel (nao deixar negativo)")
    print("4. Esperar novas entradas quando o saldo acabar")
    print("\n" + "=" * 60 + "\n")
    
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_transferencias_favo_mel_para_girassol()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

