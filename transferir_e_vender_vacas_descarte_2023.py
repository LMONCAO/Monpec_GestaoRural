# -*- coding: utf-8 -*-
"""
Script para:
1. Transferir todas as 975 vacas descarte da Canta Galo para Invernada Grande em 2023
2. Vender todas essas vacas na Invernada Grande
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
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, VendaProjetada, InventarioRebanho
)


def calcular_saldo_disponivel(propriedade, categoria, data_referencia):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
    # Buscar inventário inicial (mais recente, independente da data)
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria
    ).order_by('-data_inventario').first()
    
    saldo = 0
    
    # Se há inventário inicial, considerar como saldo inicial
    if inventario_inicial:
        saldo = inventario_inicial.quantidade
    
    # Aplicar todas as movimentações até a data de referência
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia
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
def transferir_e_vender_vacas_descarte_2023():
    """Transfere e vende todas as vacas descarte em 2023"""
    
    print("=" * 80)
    print("TRANSFERIR E VENDER VACAS DESCARTE 2023")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada_grande
    ).order_by('-data_criacao', '-ano').first()
    
    # ========== 1. VERIFICAR SALDO DISPONÍVEL NA CANTA GALO ==========
    print("\n[PASSO 1] Verificando saldo disponivel na Canta Galo em 2023...")
    
    # Verificar saldo antes de qualquer transferência em 2023
    data_verificacao = date(2023, 1, 1)
    saldo_disponivel = calcular_saldo_disponivel(canta_galo, categoria_descarte, data_verificacao)
    
    print(f"   [INFO] Saldo disponivel em 01/01/2023: {saldo_disponivel}")
    
    # Verificar se há promoções de vacas em reprodução para descarte em 2023
    categoria_reproducao = CategoriaAnimal.objects.get(nome__icontains='Vacas em Reprodução')
    promocoes_2023 = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='PROMOCAO_ENTRADA',
        categoria=categoria_descarte,
        data_movimentacao__year=2023
    ).order_by('data_movimentacao')
    
    total_promovido = sum(p.quantidade for p in promocoes_2023)
    print(f"   [INFO] Total promovido para descarte em 2023: {total_promovido}")
    
    # Saldo total disponível = saldo inicial + promoções
    saldo_total_disponivel = saldo_disponivel + total_promovido
    print(f"   [INFO] Saldo total disponivel (inicial + promocoes): {saldo_total_disponivel}")
    
    # ========== 2. DELETAR TRANSFERÊNCIAS EXISTENTES DE 2023 ==========
    print("\n[PASSO 2] Deletando transferencias existentes de 2023...")
    
    # Deletar saídas da Canta Galo
    saidas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte,
        data_movimentacao__year=2023
    )
    
    # Deletar entradas na Invernada Grande
    entradas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte,
        data_movimentacao__year=2023
    )
    
    total_deletado = saidas_existentes.count() + entradas_existentes.count()
    entradas_existentes.delete()
    saidas_existentes.delete()
    
    print(f"   [OK] {total_deletado} transferencias deletadas")
    
    # ========== 3. CRIAR TRANSFERÊNCIA DE 975 VACAS ==========
    print("\n[PASSO 3] Criando transferencia de 975 vacas descarte...")
    
    # Data da transferência: após a última promoção ou início de 2023
    if promocoes_2023.exists():
        ultima_promocao = promocoes_2023.last()
        data_transferencia = ultima_promocao.data_movimentacao + timedelta(days=1)
    else:
        data_transferencia = date(2023, 1, 15)
    
    quantidade_transferir = 975
    
    # Verificar se há saldo suficiente
    saldo_na_data = calcular_saldo_disponivel(canta_galo, categoria_descarte, data_transferencia)
    if saldo_na_data < quantidade_transferir:
        print(f"   [AVISO] Saldo insuficiente ({saldo_na_data}) para transferir {quantidade_transferir}")
        quantidade_transferir = saldo_na_data
    
    if quantidade_transferir > 0:
        # Criar transferência de saída da Canta Galo
        MovimentacaoProjetada.objects.create(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            data_movimentacao=data_transferencia,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            quantidade=quantidade_transferir,
            planejamento=planejamento_canta,
            observacao=f'Transferencia para Invernada Grande - {quantidade_transferir} vacas descarte (ano 2023)'
        )
        
        # Criar transferência de entrada na Invernada Grande
        MovimentacaoProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            data_movimentacao=data_transferencia,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            quantidade=quantidade_transferir,
            planejamento=planejamento_invernada,
            observacao=f'Transferencia de Canta Galo - {quantidade_transferir} vacas descarte (ano 2023)'
        )
        
        print(f"   [OK] Transferencia criada: {quantidade_transferir} em {data_transferencia.strftime('%d/%m/%Y')}")
    else:
        print(f"   [ERRO] Nao foi possivel criar transferencia (saldo insuficiente)")
        return
    
    # ========== 4. DELETAR VENDAS EXISTENTES NA INVERNADA GRANDE DE 2023 ==========
    print("\n[PASSO 4] Deletando vendas existentes na Invernada Grande de 2023...")
    
    vendas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='VENDA',
        categoria=categoria_descarte,
        data_movimentacao__year=2023
    )
    
    vendas_projetadas_existentes = VendaProjetada.objects.filter(
        movimentacao_projetada__in=vendas_existentes
    )
    vendas_projetadas_existentes.delete()
    vendas_existentes.delete()
    
    print(f"   [OK] {vendas_existentes.count()} vendas deletadas")
    
    # ========== 5. CRIAR VENDAS MENSAIS NA INVERNADA GRANDE (APENAS 2023) ==========
    print("\n[PASSO 5] Criando vendas mensais na Invernada Grande (apenas 2023)...")
    
    # Primeira venda: 1 mês após a transferência
    data_primeira_venda = date(data_transferencia.year, data_transferencia.month + 1, 1)
    if data_primeira_venda.month > 12:
        data_primeira_venda = date(data_primeira_venda.year + 1, 1, 1)
    
    quantidade_restante = quantidade_transferir
    data_venda = data_primeira_venda
    lote = 1
    vendas_criadas = 0
    
    # Criar vendas apenas até dezembro de 2023
    while quantidade_restante > 0 and data_venda.year == 2023:
        quantidade_venda = min(80, quantidade_restante)
        
        peso_medio_kg = Decimal('450.00')
        valor_por_kg = Decimal('6.50')
        valor_por_animal = valor_por_kg * peso_medio_kg
        valor_total = valor_por_animal * Decimal(str(quantidade_venda))
        
        movimentacao = MovimentacaoProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            data_movimentacao=data_venda,
            tipo_movimentacao='VENDA',
            quantidade=quantidade_venda,
            valor_por_cabeca=valor_por_animal,
            valor_total=valor_total,
            planejamento=planejamento_invernada,
            observacao=f'Venda mensal lote {lote} - {quantidade_venda} vacas descarte para JBS (ano 2023)'
        )
        
        VendaProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            movimentacao_projetada=movimentacao,
            data_venda=data_venda,
            quantidade=quantidade_venda,
            cliente_nome='JBS',
            peso_medio_kg=peso_medio_kg,
            peso_total_kg=peso_medio_kg * Decimal(str(quantidade_venda)),
            valor_por_kg=valor_por_kg,
            valor_por_animal=valor_por_animal,
            valor_total=valor_total,
            data_recebimento=data_venda + timedelta(days=30),
            observacoes=f'Venda mensal lote {lote} - {quantidade_venda} vacas descarte para JBS'
        )
        
        print(f"   [OK] Venda criada: {quantidade_venda} em {data_venda.strftime('%d/%m/%Y')}")
        vendas_criadas += 1
        quantidade_restante -= quantidade_venda
        lote += 1
        
        # Próxima venda: 1 mês depois (apenas se ainda estiver em 2023)
        if data_venda.month == 12:
            break
        else:
            data_venda = date(data_venda.year, data_venda.month + 1, 1)
    
    # Se ainda houver quantidade restante, criar venda final em dezembro/2023
    if quantidade_restante > 0:
        data_venda_final = date(2023, 12, 20)
        
        peso_medio_kg = Decimal('450.00')
        valor_por_kg = Decimal('6.50')
        valor_por_animal = valor_por_kg * peso_medio_kg
        valor_total = valor_por_animal * Decimal(str(quantidade_restante))
        
        movimentacao = MovimentacaoProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            data_movimentacao=data_venda_final,
            tipo_movimentacao='VENDA',
            quantidade=quantidade_restante,
            valor_por_cabeca=valor_por_animal,
            valor_total=valor_total,
            planejamento=planejamento_invernada,
            observacao=f'Venda final para zerar saldo 2023 - {quantidade_restante} vacas descarte'
        )
        
        VendaProjetada.objects.create(
            propriedade=invernada_grande,
            categoria=categoria_descarte,
            movimentacao_projetada=movimentacao,
            data_venda=data_venda_final,
            quantidade=quantidade_restante,
            cliente_nome='JBS',
            peso_medio_kg=peso_medio_kg,
            peso_total_kg=peso_medio_kg * Decimal(str(quantidade_restante)),
            valor_por_kg=valor_por_kg,
            valor_por_animal=valor_por_animal,
            valor_total=valor_total,
            data_recebimento=data_venda_final + timedelta(days=30),
            observacoes=f'Venda final para zerar saldo 2023'
        )
        
        print(f"   [OK] Venda final criada: {quantidade_restante} em {data_venda_final.strftime('%d/%m/%Y')}")
        vendas_criadas += 1
    
    # ========== 6. VERIFICAR SALDO FINAL ==========
    print("\n[PASSO 6] Verificando saldos finais...")
    
    saldo_final_canta = calcular_saldo_disponivel(canta_galo, categoria_descarte, date(2023, 12, 31))
    saldo_final_invernada = calcular_saldo_disponivel(invernada_grande, categoria_descarte, date(2023, 12, 31))
    
    print(f"   [INFO] Saldo final Canta Galo: {saldo_final_canta}")
    print(f"   [INFO] Saldo final Invernada Grande: {saldo_final_invernada}")
    
    if saldo_final_invernada == 0:
        print(f"   [OK] Saldo da Invernada Grande zerado!")
    else:
        print(f"   [AVISO] Ainda ha {saldo_final_invernada} vacas na Invernada Grande")
    
    print(f"\n[OK] Concluido!")
    print(f"   Transferencia: {quantidade_transferir} vacas")
    print(f"   Vendas criadas: {vendas_criadas}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        transferir_e_vender_vacas_descarte_2023()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

