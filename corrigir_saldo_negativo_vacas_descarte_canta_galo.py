# -*- coding: utf-8 -*-
"""
Script para corrigir saldo negativo de Vacas Descarte na Canta Galo
Garantindo que as promoções ocorram antes das transferências
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from datetime import date, timedelta
from django.db import transaction, connection
import time

from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, InventarioRebanho
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
def corrigir_saldo_negativo():
    """Corrige saldo negativo de Vacas Descarte"""
    
    print("=" * 80)
    print("CORRIGIR SALDO NEGATIVO VACAS DESCARTE CANTA GALO")
    print("=" * 80)
    
    canta_galo = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
    categoria_descarte = CategoriaAnimal.objects.get(nome__icontains='Vacas Descarte')
    categoria_reproducao = CategoriaAnimal.objects.get(nome__icontains='Vacas em Reprodução')
    
    planejamento = PlanejamentoAnual.objects.filter(
        propriedade=canta_galo
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"[INFO] Planejamento: {planejamento.codigo}")
    
    # Verificar transferências de saída
    transferencias_saida = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        categoria=categoria_descarte,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Transferencias de saida encontradas: {transferencias_saida.count()}")
    
    for transferencia in transferencias_saida:
        ano = transferencia.data_movimentacao.year
        quantidade = transferencia.quantidade
        
        print(f"\n[TRANSFERENCIA] {transferencia.data_movimentacao.strftime('%d/%m/%Y')}: {quantidade} vacas descarte")
        
        # Calcular saldo disponível antes da transferência
        # Começar com inventário inicial
        inventario = InventarioRebanho.objects.filter(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            data_inventario__lte=transferencia.data_movimentacao
        ).order_by('-data_inventario').first()
        
        saldo = inventario.quantidade if inventario else 0
        
        # Adicionar todas as movimentações até a data da transferência (incluindo anos anteriores)
        movimentacoes_anteriores = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            data_movimentacao__lt=transferencia.data_movimentacao,
            planejamento=planejamento
        ).order_by('data_movimentacao')
        
        for mov in movimentacoes_anteriores:
            if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA']:
                saldo += mov.quantidade
            elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
                saldo -= mov.quantidade
        
        # Adicionar promoções do mesmo ano até a data da transferência
        promocoes_antes = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            tipo_movimentacao='PROMOCAO_ENTRADA',
            data_movimentacao__lte=transferencia.data_movimentacao,
            data_movimentacao__year=ano,
            planejamento=planejamento
        )
        
        total_promocoes = sum(p.quantidade for p in promocoes_antes)
        saldo += total_promocoes
        
        # Subtrair outras saídas do mesmo ano antes desta transferência
        outras_saidas = MovimentacaoProjetada.objects.filter(
            propriedade=canta_galo,
            categoria=categoria_descarte,
            tipo_movimentacao__in=['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA'],
            data_movimentacao__lt=transferencia.data_movimentacao,
            data_movimentacao__year=ano,
            planejamento=planejamento
        )
        
        total_outras_saidas = sum(s.quantidade for s in outras_saidas)
        saldo -= total_outras_saidas
        
        print(f"  Saldo disponivel: {saldo} (inicial: {inventario.quantidade if inventario else 0}, promocoes: {total_promocoes}, outras saidas: {total_outras_saidas})")
        
        if saldo < quantidade:
            # Precisa criar promoção antes da transferência
            quantidade_faltante = quantidade - saldo
            
            print(f"  [PROBLEMA] Saldo insuficiente. Faltam {quantidade_faltante} vacas descarte")
            
            # Verificar se já existe promoção na mesma data ou antes
            promocao_existente = MovimentacaoProjetada.objects.filter(
                propriedade=canta_galo,
                categoria=categoria_descarte,
                tipo_movimentacao='PROMOCAO_ENTRADA',
                data_movimentacao=transferencia.data_movimentacao,
                planejamento=planejamento
            ).first()
            
            if promocao_existente:
                # Aumentar quantidade da promoção existente
                promocao_existente.quantidade += quantidade_faltante
                promocao_existente.save()
                print(f"  [OK] Promocao existente atualizada: {promocao_existente.quantidade} vacas")
            else:
                # Criar nova promoção 1 dia antes da transferência
                data_promocao = transferencia.data_movimentacao - timedelta(days=1)
                
                # Verificar promoção de saída correspondente
                promocao_saida = MovimentacaoProjetada.objects.filter(
                    propriedade=canta_galo,
                    categoria=categoria_reproducao,
                    tipo_movimentacao='PROMOCAO_SAIDA',
                    data_movimentacao=data_promocao,
                    planejamento=planejamento
                ).first()
                
                if not promocao_saida:
                    # Criar promoção de saída
                    MovimentacaoProjetada.objects.create(
                        propriedade=canta_galo,
                        categoria=categoria_reproducao,
                        data_movimentacao=data_promocao,
                        tipo_movimentacao='PROMOCAO_SAIDA',
                        quantidade=quantidade_faltante,
                        planejamento=planejamento,
                        observacao=f'Promocao para descarte antes de transferencia {transferencia.data_movimentacao.strftime("%d/%m/%Y")}'
                    )
                    print(f"  [OK] Promocao de saida criada: {quantidade_faltante} vacas em {data_promocao.strftime('%d/%m/%Y')}")
                
                # Criar promoção de entrada
                MovimentacaoProjetada.objects.create(
                    propriedade=canta_galo,
                    categoria=categoria_descarte,
                    data_movimentacao=data_promocao,
                    tipo_movimentacao='PROMOCAO_ENTRADA',
                    quantidade=quantidade_faltante,
                    planejamento=planejamento,
                    observacao=f'Promocao para descarte antes de transferencia {transferencia.data_movimentacao.strftime("%d/%m/%Y")}'
                )
                print(f"  [OK] Promocao de entrada criada: {quantidade_faltante} vacas em {data_promocao.strftime('%d/%m/%Y')}")
    
    print(f"\n[OK] Concluido!")


if __name__ == '__main__':
    if not aguardar_banco_livre():
        sys.exit(1)
    
    try:
        corrigir_saldo_negativo()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()

