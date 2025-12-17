# -*- coding: utf-8 -*-
"""
Script para corrigir os problemas finais identificados
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
def corrigir_problemas_finais():
    """Corrige os problemas finais"""
    
    print("=" * 80)
    print("CORRIGIR PROBLEMAS FINAIS")
    print("=" * 80)
    
    # Buscar propriedades
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    invernada_grande = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar categorias
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote 12-24')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    # Buscar planejamentos
    planejamento_canta = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    # ========== PROBLEMA 1: Transferências Canta -> Favo ==========
    print("\n[PROBLEMA 1] Corrigindo transferencias Canta Galo -> Favo de Mel...")
    
    # Buscar entradas no Favo de Mel
    entradas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_garrote
    ).order_by('data_movimentacao')
    
    # Buscar TODAS as saídas da Canta Galo (sem filtro de observação)
    saidas_canta = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_garrote
    )
    
    print(f"   Entradas no Favo de Mel: {entradas_favo.count()}")
    print(f"   Saidas da Canta Galo: {saidas_canta.count()}")
    
    # Agrupar entradas por data
    entradas_por_data = {}
    for entrada in entradas_favo:
        data_key = entrada.data_movimentacao
        if data_key not in entradas_por_data:
            entradas_por_data[data_key] = []
        entradas_por_data[data_key].append(entrada)
    
    # Criar saídas correspondentes
    saidas_criadas = 0
    for data_key, lista_entradas in entradas_por_data.items():
        quantidade_total = sum(e.quantidade for e in lista_entradas)
        
        # Verificar se já existe saída para esta data
        saida_existente = saidas_canta.filter(
            data_movimentacao=data_key
        ).first()
        
        if not saida_existente:
            MovimentacaoProjetada.objects.create(
                propriedade=canta_galo,
                categoria=categoria_garrote,
                data_movimentacao=data_key,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                quantidade=quantidade_total,
                planejamento=planejamento_canta,
                observacao=f'Transferencia para Favo de Mel - {quantidade_total} garrotes'
            )
            saidas_criadas += 1
            print(f"   [OK] Saida criada: {quantidade_total} em {data_key.strftime('%d/%m/%Y')}")
    
    print(f"   [OK] {saidas_criadas} saidas criadas")
    
    # ========== PROBLEMA 2: Vendas faltantes na Invernada Grande ==========
    print("\n[PROBLEMA 2] Corrigindo vendas na Invernada Grande...")
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada_grande
    ).order_by('-data_criacao', '-ano').first()
    
    # Buscar entradas de vacas descarte
    entradas_invernada = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=categoria_descarte
    ).order_by('data_movimentacao')
    
    # Buscar vendas existentes
    vendas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=invernada_grande,
        tipo_movimentacao='VENDA',
        categoria=categoria_descarte
    )
    
    print(f"   Entradas: {entradas_invernada.count()}")
    print(f"   Vendas existentes: {vendas_existentes.count()}")
    
    # Para cada entrada, criar vendas mensais de 80 cabeças
    vendas_criadas = 0
    for entrada in entradas_invernada:
        data_entrada = entrada.data_movimentacao
        quantidade_total = entrada.quantidade
        
        # Primeira venda: 1 mês após a entrada
        data_primeira_venda = date(data_entrada.year, data_entrada.month + 1, 1)
        if data_primeira_venda.month > 12:
            data_primeira_venda = date(data_primeira_venda.year + 1, 1, 1)
        
        # Criar vendas de 80 cabeças até acabar
        quantidade_restante = quantidade_total
        data_venda = data_primeira_venda
        lote = 1
        
        while quantidade_restante > 0 and lote <= 10:
            quantidade_venda = min(80, quantidade_restante)
            
            # Verificar se já existe venda
            venda_existente = vendas_existentes.filter(
                data_movimentacao=data_venda,
                quantidade=quantidade_venda
            ).first()
            
            if not venda_existente:
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
                    observacao=f'Venda mensal lote {lote} - {quantidade_venda} vacas descarte para JBS (entrada em {data_entrada.strftime("%d/%m/%Y")})'
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
                
                vendas_criadas += 1
                print(f"   [OK] Venda criada: {quantidade_venda} em {data_venda.strftime('%d/%m/%Y')}")
            
            quantidade_restante -= quantidade_venda
            lote += 1
            
            # Próxima venda: 1 mês depois
            if data_venda.month == 12:
                data_venda = date(data_venda.year + 1, 1, 1)
            else:
                data_venda = date(data_venda.year, data_venda.month + 1, 1)
    
    print(f"   [OK] {vendas_criadas} vendas criadas")
    
    # ========== PROBLEMA 3: Vendas faltantes na Girassol ==========
    print("\n[PROBLEMA 3] Corrigindo vendas faltantes na Girassol...")
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    # Buscar evoluções sem venda correspondente
    evolucoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='PROMOCAO_ENTRADA',
        categoria=categoria_boi
    ).order_by('data_movimentacao')
    
    vendas_girassol = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='VENDA',
        categoria=categoria_boi
    )
    
    vendas_criadas_girassol = 0
    
    for evolucao in evolucoes:
        data_evolucao = evolucao.data_movimentacao
        quantidade = evolucao.quantidade
        
        # Venda 90 dias após a evolução
        data_venda = data_evolucao + timedelta(days=90)
        
        # Verificar se já existe venda
        venda_existente = vendas_girassol.filter(
            data_movimentacao=data_venda,
            quantidade=quantidade
        ).first()
        
        if not venda_existente:
            peso_medio_kg = Decimal('500.00')
            valor_por_kg = Decimal('7.00')
            valor_por_animal = valor_por_kg * peso_medio_kg
            valor_total = valor_por_animal * Decimal(str(quantidade))
            
            movimentacao = MovimentacaoProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria_boi,
                data_movimentacao=data_venda,
                tipo_movimentacao='VENDA',
                quantidade=quantidade,
                valor_por_cabeca=valor_por_animal,
                valor_total=valor_total,
                planejamento=planejamento_girassol,
                observacao=f'Venda completa do lote - {quantidade} bois apos 90 dias da evolucao (evolucao em {data_evolucao.strftime("%d/%m/%Y")})'
            )
            
            VendaProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria_boi,
                movimentacao_projetada=movimentacao,
                data_venda=data_venda,
                quantidade=quantidade,
                cliente_nome='Frigorifico',
                peso_medio_kg=peso_medio_kg,
                peso_total_kg=peso_medio_kg * Decimal(str(quantidade)),
                valor_por_kg=valor_por_kg,
                valor_por_animal=valor_por_animal,
                valor_total=valor_total,
                data_recebimento=data_venda + timedelta(days=30),
                observacoes=f'Venda completa do lote - {quantidade} bois apos 90 dias da evolucao'
            )
            
            vendas_criadas_girassol += 1
            print(f"   [OK] Venda criada: {quantidade} em {data_venda.strftime('%d/%m/%Y')}")
    
    print(f"   [OK] {vendas_criadas_girassol} vendas criadas")
    
    print(f"\n[OK] Todas as correcoes concluidas!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_problemas_finais()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











