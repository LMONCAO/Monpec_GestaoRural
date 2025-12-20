# -*- coding: utf-8 -*-
"""
Script de correção coordenada completa para todas as fazendas
Resolve todos os problemas de forma sincronizada e matemática
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
from collections import defaultdict

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


@transaction.atomic
def corrigir_todas_fazendas():
    """Corrige todos os problemas de forma coordenada"""
    
    print("=" * 80)
    print("CORRECAO COORDENADA COMPLETA - TODAS AS FAZENDAS")
    print("=" * 80)
    
    fazendas = Propriedade.objects.all().order_by('nome_propriedade')
    
    # Mapear fazendas por nome para facilitar busca
    fazendas_dict = {f.nome_propriedade: f for f in fazendas}
    
    # 1. CORRIGIR TRANSFERENCIAS DESBALANCEADAS
    print("\n" + "=" * 80)
    print("1. CORRIGIR TRANSFERENCIAS DESBALANCEADAS")
    print("=" * 80)
    
    transferencias_criadas = 0
    
    for fazenda in fazendas:
        planejamento = PlanejamentoAnual.objects.filter(
            propriedade=fazenda
        ).order_by('-data_criacao', '-ano').first()
        
        if not planejamento:
            continue
        
        # Buscar todas as transferências de saída
        saidas = MovimentacaoProjetada.objects.filter(
            propriedade=fazenda,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            planejamento=planejamento
        ).order_by('data_movimentacao')
        
        for saida in saidas:
            # Tentar identificar fazenda de destino pela observação
            observacao = saida.observacao or ''
            
            # Buscar se já existe entrada correspondente
            entradas_existentes = MovimentacaoProjetada.objects.filter(
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                categoria=saida.categoria,
                data_movimentacao=saida.data_movimentacao,
                quantidade=saida.quantidade,
                planejamento=planejamento
            )
            
            # Verificar se alguma entrada corresponde a esta saída
            entrada_correspondente = None
            for entrada in entradas_existentes:
                # Verificar se a observação menciona a fazenda de origem
                if fazenda.nome_propriedade.lower() in (entrada.observacao or '').lower():
                    entrada_correspondente = entrada
                    break
            
            if entrada_correspondente:
                continue
            
            # Tentar identificar destino pela observação da saída
            destino_nome = None
            if 'favo de mel' in observacao.lower() or 'favo' in observacao.lower():
                destino_nome = 'Fazenda Favo de Mel'
            elif 'girassol' in observacao.lower():
                destino_nome = 'Fazenda Girassol'
            elif 'invernada' in observacao.lower():
                destino_nome = 'FAZENDA INVERNADA GRANDE'
            elif 'canta galo' in observacao.lower():
                destino_nome = 'FAZENDA CANTA GALO'
            
            if destino_nome and destino_nome in fazendas_dict:
                destino = fazendas_dict[destino_nome]
                
                # Buscar planejamento da fazenda de destino
                planejamento_destino = PlanejamentoAnual.objects.filter(
                    propriedade=destino
                ).order_by('-data_criacao', '-ano').first()
                
                if planejamento_destino:
                    # Verificar se já existe entrada
                    entrada_existente = MovimentacaoProjetada.objects.filter(
                        propriedade=destino,
                        categoria=saida.categoria,
                        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                        data_movimentacao=saida.data_movimentacao,
                        quantidade=saida.quantidade,
                        planejamento=planejamento_destino
                    ).first()
                    
                    if not entrada_existente:
                        MovimentacaoProjetada.objects.create(
                            propriedade=destino,
                            categoria=saida.categoria,
                            data_movimentacao=saida.data_movimentacao,
                            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                            quantidade=saida.quantidade,
                            planejamento=planejamento_destino,
                            observacao=f'Transferencia de {fazenda.nome_propriedade} - {saida.quantidade} {saida.categoria.nome}'
                        )
                        transferencias_criadas += 1
                        print(f"  [OK] Entrada criada: {destino.nome_propriedade} - {saida.data_movimentacao.strftime('%d/%m/%Y')} - {saida.quantidade} {saida.categoria.nome}")
    
    print(f"\n[INFO] Transferencias criadas: {transferencias_criadas}")
    
    # 2. CORRIGIR SAIDAS SEM SALDO (criar promoções antes)
    print("\n" + "=" * 80)
    print("2. CORRIGIR SAIDAS SEM SALDO")
    print("=" * 80)
    
    promocoes_criadas = 0
    
    for fazenda in fazendas:
        planejamento = PlanejamentoAnual.objects.filter(
            propriedade=fazenda
        ).order_by('-data_criacao', '-ano').first()
        
        if not planejamento:
            continue
        
        # Buscar todas as saídas
        saidas = MovimentacaoProjetada.objects.filter(
            propriedade=fazenda,
            tipo_movimentacao__in=['VENDA', 'TRANSFERENCIA_SAIDA', 'MORTE'],
            planejamento=planejamento
        ).order_by('data_movimentacao')
        
        for saida in saidas:
            # Calcular saldo disponível antes desta saída
            inventario = InventarioRebanho.objects.filter(
                propriedade=fazenda,
                categoria=saida.categoria,
                data_inventario__lte=saida.data_movimentacao
            ).order_by('-data_inventario').first()
            
            saldo = inventario.quantidade if inventario else 0
            
            # Adicionar todas as movimentações anteriores
            movimentacoes_anteriores = MovimentacaoProjetada.objects.filter(
                propriedade=fazenda,
                categoria=saida.categoria,
                data_movimentacao__lt=saida.data_movimentacao,
                planejamento=planejamento
            ).order_by('data_movimentacao')
            
            for mov in movimentacoes_anteriores:
                if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
                    saldo += mov.quantidade
                elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
                    saldo -= mov.quantidade
            
            # Adicionar promoções do mesmo ano antes desta saída
            promocoes_antes = MovimentacaoProjetada.objects.filter(
                propriedade=fazenda,
                categoria=saida.categoria,
                tipo_movimentacao='PROMOCAO_ENTRADA',
                data_movimentacao__lte=saida.data_movimentacao,
                data_movimentacao__year=saida.data_movimentacao.year,
                planejamento=planejamento
            )
            
            total_promocoes = sum(p.quantidade for p in promocoes_antes)
            saldo += total_promocoes
            
            # Subtrair outras saídas do mesmo ano antes desta
            outras_saidas = MovimentacaoProjetada.objects.filter(
                propriedade=fazenda,
                categoria=saida.categoria,
                tipo_movimentacao__in=['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA'],
                data_movimentacao__lt=saida.data_movimentacao,
                data_movimentacao__year=saida.data_movimentacao.year,
                planejamento=planejamento
            )
            
            total_outras_saidas = sum(s.quantidade for s in outras_saidas)
            saldo -= total_outras_saidas
            
            if saldo < saida.quantidade:
                quantidade_faltante = saida.quantidade - saldo
                
                # Verificar categoria de origem para promoção
                # Se for "Vacas Descarte", precisa vir de "Vacas em Reprodução"
                categoria_origem = None
                if 'Vacas Descarte' in saida.categoria.nome:
                    categoria_origem = CategoriaAnimal.objects.filter(
                        nome__icontains='Vacas em Reprodução'
                    ).first()
                elif 'Garrote' in saida.categoria.nome:
                    categoria_origem = CategoriaAnimal.objects.filter(
                        nome__icontains='Bezerro'
                    ).first()
                
                if categoria_origem:
                    # Criar promoção 1 dia antes da saída
                    data_promocao = saida.data_movimentacao - timedelta(days=1)
                    
                    # Verificar se já existe promoção nesta data
                    promocao_existente = MovimentacaoProjetada.objects.filter(
                        propriedade=fazenda,
                        categoria=saida.categoria,
                        tipo_movimentacao='PROMOCAO_ENTRADA',
                        data_movimentacao=data_promocao,
                        planejamento=planejamento
                    ).first()
                    
                    if promocao_existente:
                        promocao_existente.quantidade += quantidade_faltante
                        promocao_existente.save()
                        print(f"  [OK] Promocao atualizada: {fazenda.nome_propriedade} - {data_promocao.strftime('%d/%m/%Y')} - +{quantidade_faltante} {saida.categoria.nome}")
                    else:
                        # Criar promoção de saída
                        MovimentacaoProjetada.objects.create(
                            propriedade=fazenda,
                            categoria=categoria_origem,
                            data_movimentacao=data_promocao,
                            tipo_movimentacao='PROMOCAO_SAIDA',
                            quantidade=quantidade_faltante,
                            planejamento=planejamento,
                            observacao=f'Promocao para {saida.categoria.nome} antes de {saida.tipo_movimentacao}'
                        )
                        
                        # Criar promoção de entrada
                        MovimentacaoProjetada.objects.create(
                            propriedade=fazenda,
                            categoria=saida.categoria,
                            data_movimentacao=data_promocao,
                            tipo_movimentacao='PROMOCAO_ENTRADA',
                            quantidade=quantidade_faltante,
                            planejamento=planejamento,
                            observacao=f'Promocao para {saida.categoria.nome} antes de {saida.tipo_movimentacao}'
                        )
                        promocoes_criadas += 1
                        print(f"  [OK] Promocao criada: {fazenda.nome_propriedade} - {data_promocao.strftime('%d/%m/%Y')} - +{quantidade_faltante} {saida.categoria.nome}")
    
    print(f"\n[INFO] Promocoes criadas: {promocoes_criadas}")
    
    print(f"\n[OK] Correcao concluida!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_todas_fazendas()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























