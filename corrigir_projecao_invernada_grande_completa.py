# -*- coding: utf-8 -*-
"""
Script para corrigir completamente a projeção da Invernada Grande:
1. Criar entradas (TRANSFERENCIA_ENTRADA) das 512 vacas descarte da Canta Galo
2. Criar vendas mensais de 80 cabeças
3. Zerar todo o saldo no fim de 2023
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date, timedelta
from django.db import transaction, connection
from decimal import Decimal
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, InventarioRebanho, VendaProjetada
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


def calcular_saldo_disponivel(propriedade, categoria, data_referencia, planejamento):
    """Calcula saldo disponível considerando inventário e movimentações"""
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Aplicar movimentações até a data
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    return max(0, saldo)


@transaction.atomic
def corrigir_projecao_invernada_grande():
    """Corrige completamente a projeção da Invernada Grande"""
    
    print("=" * 80)
    print("CORRIGIR PROJECAO INVERNADA GRANDE - COMPLETA")
    print("=" * 80)
    
    # Buscar propriedades
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    # Buscar categoria
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    # Buscar planejamentos
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    # Usar o planejamento mais recente da Invernada Grande
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_canta or not planejamento_invernada:
        print("[ERRO] Planejamentos nao encontrados")
        return
    
    print(f"[INFO] Planejamento Canta Galo: {planejamento_canta.codigo}")
    print(f"[INFO] Planejamento Invernada: {planejamento_invernada.codigo}")
    print(f"[INFO] IMPORTANTE: Todas as movimentacoes serao vinculadas ao planejamento atual: {planejamento_invernada.codigo}")
    
    # ========== 1. BUSCAR TRANSFERÊNCIAS DE SAÍDA DA CANTA GALO ==========
    print("\n[PASSO 1] Buscando transferências de saída da Canta Galo...")
    
    saidas_canta = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_canta,
        data_movimentacao__year__in=[2022, 2023]
    ).order_by('data_movimentacao')
    
    print(f"[INFO] Transferencias encontradas: {saidas_canta.count()}")
    
    if not saidas_canta.exists():
        print("[AVISO] Nenhuma transferencia de saida encontrada na Canta Galo")
        return
    
    # ========== 2. CRIAR ENTRADAS NA INVERNADA GRANDE ==========
    print("\n[PASSO 2] Criando entradas na Invernada Grande...")
    
    entradas_criadas = 0
    for saida in saidas_canta:
        ano = saida.data_movimentacao.year
        quantidade = saida.quantidade
        data_transferencia = saida.data_movimentacao
        
        print(f"\n[ANO {ano}] Transferencia de {quantidade} vacas em {data_transferencia.strftime('%d/%m/%Y')}")
        
        # Verificar se já existe entrada
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=invernada,
            categoria=categoria_descarte,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            data_movimentacao=data_transferencia,
            quantidade=quantidade,
            planejamento=planejamento_invernada
        ).first()
        
        if entrada_existente:
            print(f"  [INFO] Entrada ja existe")
        else:
            # Criar entrada
            MovimentacaoProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                data_movimentacao=data_transferencia,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=quantidade,
                planejamento=planejamento_invernada,
                observacao=f'Transferencia de Canta Galo - {quantidade} vacas descarte (ano {ano})'
            )
            print(f"  [OK] Entrada criada: {quantidade} vacas")
            entradas_criadas += 1
    
    print(f"\n[RESUMO] Entradas criadas: {entradas_criadas}")
    
    # ========== 3. DELETAR VENDAS EXISTENTES PARA RECRIAR ==========
    print("\n[PASSO 3] Deletando vendas existentes para recriar...")
    
    vendas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        tipo_movimentacao='VENDA',
        data_movimentacao__year__in=[2022, 2023],
        planejamento=planejamento_invernada
    )
    
    total_vendas_deletadas = vendas_existentes.count()
    vendas_existentes.delete()
    print(f"[OK] {total_vendas_deletadas} vendas deletadas")
    
    # ========== 4. CRIAR VENDAS MENSAIS ==========
    print("\n[PASSO 4] Criando vendas mensais de 80 cabeças...")
    
    vendas_criadas = 0
    
    for saida in saidas_canta:
        ano = saida.data_movimentacao.year
        quantidade_total = saida.quantidade
        data_transferencia = saida.data_movimentacao
        
        print(f"\n[ANO {ano}] Processando vendas para {quantidade_total} vacas...")
        
        # Primeira venda: 1 mês após a transferência
        data_venda = date(data_transferencia.year, data_transferencia.month + 1, 15)
        if data_venda.month > 12:
            data_venda = date(data_venda.year + 1, 1, 15)
        
        quantidade_restante = quantidade_total
        lote = 1
        
        # Criar vendas mensais de 80 cabeças até zerar ou até dezembro de 2023
        while quantidade_restante > 0 and data_venda.year <= 2023:
            quantidade_venda = min(80, quantidade_restante)
            
            # Verificar saldo disponível antes de criar venda
            saldo_disponivel = calcular_saldo_disponivel(
                invernada, categoria_descarte, data_venda, planejamento_invernada
            )
            
            if saldo_disponivel <= 0:
                print(f"  [AVISO] Sem saldo disponivel em {data_venda.strftime('%d/%m/%Y')} (saldo: {saldo_disponivel})")
                break
            
            # Ajustar quantidade se necessário
            quantidade_venda = min(quantidade_venda, saldo_disponivel)
            
            # Valores
            peso_medio_kg = Decimal('450.00')
            valor_por_kg = Decimal('6.50')
            valor_por_animal = valor_por_kg * peso_medio_kg
            valor_total = valor_por_animal * Decimal(str(quantidade_venda))
            
            # Criar movimentação de venda
            movimentacao = MovimentacaoProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                data_movimentacao=data_venda,
                tipo_movimentacao='VENDA',
                quantidade=quantidade_venda,
                valor_por_cabeca=valor_por_animal,
                valor_total=valor_total,
                planejamento=planejamento_invernada,
                observacao=f'Venda mensal lote {lote} - {quantidade_venda} vacas descarte para JBS (ano {ano})'
            )
            
            # Criar VendaProjetada
            peso_total = peso_medio_kg * Decimal(str(quantidade_venda))
            VendaProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                movimentacao_projetada=movimentacao,
                planejamento=planejamento_invernada,
                data_venda=data_venda,
                quantidade=quantidade_venda,
                cliente_nome='JBS',
                peso_medio_kg=peso_medio_kg,
                peso_total_kg=peso_total,
                valor_por_kg=valor_por_kg,
                valor_por_animal=valor_por_animal,
                valor_total=valor_total,
                data_recebimento=data_venda + timedelta(days=30),
                observacoes=f'Venda mensal lote {lote} - {quantidade_venda} vacas descarte para JBS (ano {ano})'
            )
            
            print(f"  [OK] Venda criada: {quantidade_venda} vacas em {data_venda.strftime('%d/%m/%Y')} (saldo antes: {saldo_disponivel}, restante: {quantidade_restante - quantidade_venda})")
            
            quantidade_restante -= quantidade_venda
            lote += 1
            
            # Próximo mês
            if data_venda.month == 12:
                data_venda = date(data_venda.year + 1, 1, 15)
            else:
                data_venda = date(data_venda.year, data_venda.month + 1, 15)
            
            vendas_criadas += 1
    
    print(f"\n[RESUMO] Vendas criadas: {vendas_criadas}")
    
    # ========== 5. ZERAR SALDO NO FIM DE 2023 ==========
    print("\n[PASSO 5] Zerando saldo no fim de 2023...")
    
    data_fim_2023 = date(2023, 12, 31)
    saldo_final_2023 = calcular_saldo_disponivel(
        invernada, categoria_descarte, data_fim_2023, planejamento_invernada
    )
    
    print(f"[INFO] Saldo final em 31/12/2023: {saldo_final_2023} vacas")
    
    if saldo_final_2023 > 0:
        # Criar venda final para zerar
        data_venda_final = date(2023, 12, 30)
        
        peso_medio_kg = Decimal('450.00')
        valor_por_kg = Decimal('6.50')
        valor_por_animal = valor_por_kg * peso_medio_kg
        valor_total = valor_por_animal * Decimal(str(saldo_final_2023))
        
        movimentacao = MovimentacaoProjetada.objects.create(
            propriedade=invernada,
            categoria=categoria_descarte,
            data_movimentacao=data_venda_final,
            tipo_movimentacao='VENDA',
            quantidade=saldo_final_2023,
            valor_por_cabeca=valor_por_animal,
            valor_total=valor_total,
            planejamento=planejamento_invernada,
            observacao=f'Venda final para zerar saldo - {saldo_final_2023} vacas descarte (fim de 2023)'
        )
        
        peso_total = peso_medio_kg * Decimal(str(saldo_final_2023))
        VendaProjetada.objects.create(
            propriedade=invernada,
            categoria=categoria_descarte,
            movimentacao_projetada=movimentacao,
            planejamento=planejamento_invernada,
            data_venda=data_venda_final,
            quantidade=saldo_final_2023,
            cliente_nome='JBS',
            peso_medio_kg=peso_medio_kg,
            peso_total_kg=peso_total,
            valor_por_kg=valor_por_kg,
            valor_por_animal=valor_por_animal,
            valor_total=valor_total,
            data_recebimento=data_venda_final + timedelta(days=30),
            observacoes=f'Venda final para zerar saldo - {saldo_final_2023} vacas descarte (fim de 2023)'
        )
        
        print(f"  [OK] Venda final criada: {saldo_final_2023} vacas em {data_venda_final.strftime('%d/%m/%Y')}")
        
        # Verificar saldo após venda final
        saldo_apos_venda = calcular_saldo_disponivel(
            invernada, categoria_descarte, date(2024, 1, 1), planejamento_invernada
        )
        print(f"  [VERIFICACAO] Saldo em 01/01/2024: {saldo_apos_venda} vacas")
    else:
        print(f"  [OK] Saldo ja esta zerado")
    
    print("\n" + "=" * 80)
    print("[SUCESSO] Projecao da Invernada Grande corrigida!")
    print("=" * 80)


if __name__ == '__main__':
    if not aguardar_banco_livre():
        print("[ERRO] Nao foi possivel acessar o banco de dados")
        sys.exit(1)
    
    try:
        corrigir_projecao_invernada_grande()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

