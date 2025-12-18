# -*- coding: utf-8 -*-
"""
Script para corrigir vendas faltantes na Girassol
Garante que TODOS os bois sejam vendidos 90 dias após a evolução
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


def calcular_saldo_disponivel(propriedade, categoria, data_venda):
    """Calcula o saldo disponível de uma categoria em uma data específica"""
    from gestao_rural.models import InventarioRebanho
    
    inventario_inicial = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=data_venda
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
        data_movimentacao__lte=data_venda,
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


def criar_venda(propriedade, categoria, quantidade, data_venda, cliente_nome='Frigorifico', 
                valor_por_kg=Decimal('7.00'), peso_medio_kg=Decimal('500.00'), observacao='', planejamento=None):
    """Cria uma venda projetada"""
    peso_total = peso_medio_kg * Decimal(str(quantidade))
    valor_por_animal = valor_por_kg * peso_medio_kg
    valor_total = valor_por_animal * Decimal(str(quantidade))
    
    # Criar movimentação de venda
    movimentacao = MovimentacaoProjetada.objects.create(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao=data_venda,
        tipo_movimentacao='VENDA',
        quantidade=quantidade,
        planejamento=planejamento,
        observacao=observacao
    )
    
    # Criar venda projetada
    from datetime import timedelta
    venda = VendaProjetada.objects.create(
        propriedade=propriedade,
        categoria=categoria,
        movimentacao_projetada=movimentacao,
        data_venda=data_venda,
        quantidade=quantidade,
        cliente_nome=cliente_nome,
        peso_medio_kg=peso_medio_kg,
        peso_total_kg=peso_total,
        valor_por_kg=valor_por_kg,
        valor_por_animal=valor_por_animal,
        valor_total=valor_total,
        data_recebimento=data_venda + timedelta(days=30),
        observacoes=observacao
    )
    
    return movimentacao, venda


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
def corrigir_vendas_faltantes():
    """Corrige vendas faltantes - garante que TODOS os bois sejam vendidos 90 dias após evolução"""
    
    print("=" * 80)
    print("CORRIGIR VENDAS FALTANTES GIRASSOL")
    print("=" * 80)
    print("[REGRA] Todos os bois devem ser vendidos 90 dias após a evolução")
    
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"[INFO] Planejamento: {planejamento.codigo}")
    
    # Buscar todas as evoluções
    evolucoes = MovimentacaoProjetada.objects.filter(
        propriedade=girassol,
        tipo_movimentacao='PROMOCAO_ENTRADA',
        categoria=categoria_boi,
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Total de evolucoes: {evolucoes.count()}")
    
    vendas_criadas = 0
    vendas_corrigidas = 0
    
    for evolucao in evolucoes:
        data_evolucao = evolucao.data_movimentacao
        quantidade_evolucao = evolucao.quantidade
        data_venda_esperada = data_evolucao + timedelta(days=90)
        
        # Buscar vendas existentes próximas à data esperada
        vendas_existentes = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            tipo_movimentacao='VENDA',
            categoria=categoria_boi,
            data_movimentacao__gte=data_venda_esperada - timedelta(days=5),
            data_movimentacao__lte=data_venda_esperada + timedelta(days=5),
            planejamento=planejamento
        )
        
        total_vendido = sum(v.quantidade for v in vendas_existentes)
        
        if total_vendido < quantidade_evolucao:
            falta = quantidade_evolucao - total_vendido
            
            print(f"\n[PROBLEMA] Evolucao {data_evolucao.strftime('%d/%m/%Y')}: {quantidade_evolucao} bois")
            print(f"  Vendido: {total_vendido}, Falta: {falta}")
            
            # Verificar saldo disponível na data da venda
            saldo_disponivel = calcular_saldo_disponivel(girassol, categoria_boi, data_venda_esperada)
            
            # Vender o que tiver disponível (pode ser menos se já foi vendido antes)
            quantidade_a_vender = min(falta, saldo_disponivel)
            
            if quantidade_a_vender > 0:
                # Verificar se já existe venda nesta data exata
                venda_exata = MovimentacaoProjetada.objects.filter(
                    propriedade=girassol,
                    tipo_movimentacao='VENDA',
                    categoria=categoria_boi,
                    data_movimentacao=data_venda_esperada,
                    planejamento=planejamento
                ).first()
                
                if venda_exata:
                    # Atualizar quantidade da venda existente
                    venda_exata.quantidade += quantidade_a_vender
                    venda_exata.save()
                    
                    # Atualizar VendaProjetada
                    venda_proj = VendaProjetada.objects.filter(movimentacao_projetada=venda_exata).first()
                    if venda_proj:
                        venda_proj.quantidade = venda_exata.quantidade
                        venda_proj.valor_total = venda_proj.valor_por_animal * Decimal(str(venda_exata.quantidade))
                        venda_proj.peso_total_kg = venda_proj.peso_medio_kg * Decimal(str(venda_exata.quantidade))
                        venda_proj.save()
                    
                    print(f"  [OK] Venda atualizada: +{quantidade_a_vender} bois")
                    vendas_corrigidas += 1
                else:
                    # Criar nova venda
                    observacao = f'Venda completa do lote - {quantidade_a_vender} bois apos 90 dias da evolucao (evolucao em {data_evolucao.strftime("%d/%m/%Y")})'
                    criar_venda(
                        propriedade=girassol,
                        categoria=categoria_boi,
                        quantidade=quantidade_a_vender,
                        data_venda=data_venda_esperada,
                        observacao=observacao,
                        planejamento=planejamento
                    )
                    print(f"  [OK] Venda criada: {quantidade_a_vender} bois em {data_venda_esperada.strftime('%d/%m/%Y')}")
                    vendas_criadas += 1
            else:
                print(f"  [AVISO] Sem saldo disponivel para vender (saldo: {saldo_disponivel})")
    
    print(f"\n[OK] Concluido!")
    print(f"   Vendas criadas: {vendas_criadas}")
    print(f"   Vendas corrigidas: {vendas_corrigidas}")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_vendas_faltantes()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















