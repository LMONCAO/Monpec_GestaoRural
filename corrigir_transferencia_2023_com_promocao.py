# -*- coding: utf-8 -*-
"""
Script para corrigir transferência de 2023 considerando promoções de vacas em reprodução
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date, timedelta
from decimal import Decimal
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, VendaProjetada
)


def calcular_saldo_disponivel(propriedade, categoria, data_referencia):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
    from gestao_rural.models import InventarioRebanho
    
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
def corrigir_transferencia_2023():
    """Corrige transferência de 2023 considerando promoções"""
    
    print("=" * 80)
    print("CORRIGIR TRANSFERENCIA 2023 COM PROMOCOES")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    
    categoria_reproducao = CategoriaAnimal.objects.get(nome__icontains='Vacas em Reprodução')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada_grande
    ).order_by('-data_criacao', '-ano').first()
    
    # Buscar vendas de vacas em reprodução em 2023
    vendas_reproducao = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='VENDA',
        categoria=categoria_reproducao,
        data_movimentacao__year=2023
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Vendas de vacas em reproducao em 2023: {vendas_reproducao.count()}")
    
    total_promovido = 0
    
    for venda in vendas_reproducao:
        data_venda = venda.data_movimentacao
        quantidade = venda.quantidade
        
        # Data da promoção: 1 dia antes da venda (ou na mesma data)
        data_promocao = data_venda - timedelta(days=1)
        if data_promocao < data_venda:
            data_promocao = data_venda
        
        # Verificar se já existe promoção
        promocao_existente = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            tipo_movimentacao='PROMOCAO_ENTRADA',
            categoria=categoria_descarte,
            data_movimentacao=data_promocao,
            quantidade=quantidade
        ).first()
        
        if not promocao_existente:
            # Criar promoção de saída (reprodução)
            MovimentacaoProjetada.objects.create(
                propriedade=canta_galo,
                categoria=categoria_reproducao,
                data_movimentacao=data_promocao,
                tipo_movimentacao='PROMOCAO_SAIDA',
                quantidade=quantidade,
                planejamento=planejamento_canta,
                observacao=f'Promocao para descarte antes da venda em {data_venda.strftime("%d/%m/%Y")}'
            )
            
            # Criar promoção de entrada (descarte)
            MovimentacaoProjetada.objects.create(
                propriedade=canta_galo,
                categoria=categoria_descarte,
                data_movimentacao=data_promocao,
                tipo_movimentacao='PROMOCAO_ENTRADA',
                quantidade=quantidade,
                planejamento=planejamento_canta,
                observacao=f'Promocao para descarte antes da venda em {data_venda.strftime("%d/%m/%Y")}'
            )
            
            print(f"   [OK] Promocao criada: {quantidade} vacas em {data_promocao.strftime('%d/%m/%Y')}")
            total_promovido += quantidade
        
        # Alterar venda para ser de descarte
        if venda.categoria != categoria_descarte:
            venda.categoria = categoria_descarte
            venda.save()
            
            venda_projetada = VendaProjetada.objects.filter(
                movimentacao_projetada=venda
            ).first()
            if venda_projetada:
                venda_projetada.categoria = categoria_descarte
                venda_projetada.save()
    
    print(f"\n[INFO] Total promovido para descarte: {total_promovido}")
    
    # Agora criar transferência para Invernada Grande se houver saldo
    if total_promovido > 0:
        # Data da transferência: após a primeira promoção
        primeira_promocao = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            tipo_movimentacao='PROMOCAO_ENTRADA',
            categoria=categoria_descarte,
            data_movimentacao__year=2023
        ).order_by('data_movimentacao').first()
        
        if primeira_promocao:
            data_transferencia = primeira_promocao.data_movimentacao + timedelta(days=1)
            
            # Verificar saldo disponível
            saldo_disponivel = calcular_saldo_disponivel(canta_galo, categoria_descarte, data_transferencia)
            
            if saldo_disponivel > 0:
                quantidade_transferir = min(512, saldo_disponivel)
                
                # Verificar se já existe transferência
                transferencia_existente = MovimentacaoProjetada.objects.filter(
                    propriedade=canta_galo,
                    tipo_movimentacao='TRANSFERENCIA_SAIDA',
                    categoria=categoria_descarte,
                    data_movimentacao__year=2023
                ).first()
                
                if not transferencia_existente:
                    # Criar transferência de saída
                    MovimentacaoProjetada.objects.create(
                        propriedade=canta_galo,
                        categoria=categoria_descarte,
                        data_movimentacao=data_transferencia,
                        tipo_movimentacao='TRANSFERENCIA_SAIDA',
                        quantidade=quantidade_transferir,
                        planejamento=planejamento_canta,
                        observacao=f'Transferencia para Invernada Grande - {quantidade_transferir} vacas descarte (ano 2023)'
                    )
                    
                    # Criar transferência de entrada
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
                    
                    # Criar vendas mensais na Invernada Grande
                    print(f"\n[INFO] Criando vendas mensais na Invernada Grande para 2023...")
                    
                    data_primeira_venda = date(data_transferencia.year, data_transferencia.month + 1, 1)
                    if data_primeira_venda.month > 12:
                        data_primeira_venda = date(data_primeira_venda.year + 1, 1, 1)
                    
                    quantidade_restante = quantidade_transferir
                    data_venda = data_primeira_venda
                    lote = 1
                    
                    while quantidade_restante > 0 and lote <= 10 and data_venda.year == 2023:
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
                        quantidade_restante -= quantidade_venda
                        lote += 1
                        
                        # Próxima venda: 1 mês depois
                        if data_venda.month == 12:
                            break
                        else:
                            data_venda = date(data_venda.year, data_venda.month + 1, 1)
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_transferencia_2023()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















