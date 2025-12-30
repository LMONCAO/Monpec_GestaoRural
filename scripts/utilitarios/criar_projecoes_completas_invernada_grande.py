# -*- coding: utf-8 -*-
"""
Script para criar projeções completas para Invernada Grande (2022-2024)
e corrigir saldo negativo vendendo as vacas restantes
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date
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
def criar_projecoes_completas():
    """Cria projeções completas para Invernada Grande"""
    
    print("=" * 80)
    print("CRIAR PROJECOES COMPLETAS INVERNADA GRANDE 2022-2024")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    invernada = Propriedade.objects.get(nome_propriedade__icontains='Invernada Grande')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    
    planejamento_invernada = PlanejamentoAnual.objects.filter(
        propriedade=invernada
    ).order_by('-data_criacao', '-ano').first()
    
    if not planejamento_invernada:
        print("[ERRO] Nenhum planejamento encontrado")
        return
    
    print(f"[INFO] Planejamento: {planejamento_invernada.codigo}")
    
    # Buscar transferências de saída da Canta Galo
    saidas_canta = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        categoria=categoria_descarte
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de saida da Canta Galo: {saidas_canta.count()}")
    
    for saida in saidas_canta:
        ano = saida.data_movimentacao.year
        quantidade = saida.quantidade
        
        print(f"\n[ANO {ano}] Transferencia de {quantidade} vacas em {saida.data_movimentacao.strftime('%d/%m/%Y')}")
        
        # Verificar se já existe entrada correspondente
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=invernada,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=categoria_descarte,
            data_movimentacao=saida.data_movimentacao,
            quantidade=quantidade
        ).first()
        
        if not entrada_existente:
            # Criar entrada
            MovimentacaoProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                data_movimentacao=saida.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=quantidade,
                planejamento=planejamento_invernada,
                observacao=f'Transferencia de Canta Galo - {quantidade} vacas descarte (ano {ano})'
            )
            print(f"  [OK] Entrada criada: {quantidade} vacas")
        else:
            print(f"  [INFO] Entrada ja existe")
        
        # Criar vendas mensais de 80 cabeças
        data_inicio_vendas = date(ano, saida.data_movimentacao.month + 1, 15)
        quantidade_restante = quantidade
        lote = 1
        
        # Verificar vendas existentes para este ano
        vendas_existentes = MovimentacaoProjetada.objects.filter(
            propriedade=invernada,
            tipo_movimentacao='VENDA',
            categoria=categoria_descarte,
            data_movimentacao__year=ano
        )
        
        total_vendido = sum(v.quantidade for v in vendas_existentes)
        quantidade_restante = quantidade - total_vendido
        
        if quantidade_restante <= 0:
            print(f"  [INFO] Todas as vacas ja foram vendidas ({total_vendido})")
            continue
        
        print(f"  [INFO] Criando vendas para {quantidade_restante} vacas restantes")
        
        data_venda = data_inicio_vendas
        while quantidade_restante > 0 and lote <= 20:
            quantidade_venda = min(80, quantidade_restante)
            
            # Verificar se já existe venda nesta data
            venda_existente = MovimentacaoProjetada.objects.filter(
                propriedade=invernada,
                tipo_movimentacao='VENDA',
                categoria=categoria_descarte,
                data_movimentacao=data_venda
            ).first()
            
            if not venda_existente:
                # Criar movimentação de venda
                movimentacao = MovimentacaoProjetada.objects.create(
                    propriedade=invernada,
                    categoria=categoria_descarte,
                    data_movimentacao=data_venda,
                    tipo_movimentacao='VENDA',
                    quantidade=quantidade_venda,
                    planejamento=planejamento_invernada,
                    observacao=f'Venda mensal JBS - {quantidade_venda} vacas descarte (lote {lote}, ano {ano})'
                )
                
                # Criar venda projetada
                valor_por_kg = Decimal('7.00')
                peso_medio_kg = Decimal('440.00')
                valor_por_animal = valor_por_kg * peso_medio_kg
                valor_total = valor_por_animal * Decimal(str(quantidade_venda))
                
                VendaProjetada.objects.create(
                    propriedade=invernada,
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
                    data_recebimento=data_venda,
                    observacoes=f'Venda mensal JBS - {quantidade_venda} vacas descarte (lote {lote}, ano {ano})'
                )
                
                print(f"    [OK] Venda criada: {quantidade_venda} em {data_venda.strftime('%d/%m/%Y')}")
            
            quantidade_restante -= quantidade_venda
            
            # Próxima venda: próximo mês
            if data_venda.month == 12:
                data_venda = date(data_venda.year + 1, 1, 15)
            else:
                data_venda = date(data_venda.year, data_venda.month + 1, 15)
            
            lote += 1
    
    # Corrigir saldo negativo de 2025 vendendo as 2 vacas restantes
    print(f"\n[CORRIGIR SALDO NEGATIVO 2025]")
    
    # Calcular saldo atual
    from gestao_rural.models import InventarioRebanho
    
    inventario = InventarioRebanho.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    movimentacoes_2025 = MovimentacaoProjetada.objects.filter(
        propriedade=invernada,
        categoria=categoria_descarte,
        data_movimentacao__year=2025
    ).order_by('data_movimentacao')
    
    for mov in movimentacoes_2025:
        if mov.tipo_movimentacao in ['TRANSFERENCIA_ENTRADA', 'PROMOCAO_ENTRADA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA', 'PROMOCAO_SAIDA']:
            saldo -= mov.quantidade
    
    if saldo < 0:
        quantidade_vender = abs(saldo)
        print(f"  [INFO] Saldo negativo: {saldo}, vendendo {quantidade_vender} vacas")
        
        data_venda = date(2025, 12, 30)
        
        venda_existente = MovimentacaoProjetada.objects.filter(
            propriedade=invernada,
            tipo_movimentacao='VENDA',
            categoria=categoria_descarte,
            data_movimentacao=data_venda,
            quantidade=quantidade_vender
        ).first()
        
        if not venda_existente:
            movimentacao = MovimentacaoProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                data_movimentacao=data_venda,
                tipo_movimentacao='VENDA',
                quantidade=quantidade_vender,
                planejamento=planejamento_invernada,
                observacao=f'Venda para zerar saldo negativo - {quantidade_vender} vacas descarte (ano 2025)'
            )
            
            valor_por_kg = Decimal('7.00')
            peso_medio_kg = Decimal('440.00')
            valor_por_animal = valor_por_kg * peso_medio_kg
            valor_total = valor_por_animal * Decimal(str(quantidade_vender))
            
            VendaProjetada.objects.create(
                propriedade=invernada,
                categoria=categoria_descarte,
                movimentacao_projetada=movimentacao,
                data_venda=data_venda,
                quantidade=quantidade_vender,
                cliente_nome='JBS',
                peso_medio_kg=peso_medio_kg,
                peso_total_kg=peso_medio_kg * Decimal(str(quantidade_vender)),
                valor_por_kg=valor_por_kg,
                valor_por_animal=valor_por_animal,
                valor_total=valor_total,
                data_recebimento=data_venda,
                observacoes=f'Venda para zerar saldo negativo - {quantidade_vender} vacas descarte (ano 2025)'
            )
            
            print(f"  [OK] Venda criada: {quantidade_vender} vacas em {data_venda.strftime('%d/%m/%Y')}")
        else:
            print(f"  [INFO] Venda ja existe")
    else:
        print(f"  [INFO] Saldo: {saldo}")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        criar_projecoes_completas()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























