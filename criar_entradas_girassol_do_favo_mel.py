# -*- coding: utf-8 -*-
"""
Script para criar entradas na Girassol baseadas nas saídas do Favo de Mel
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual
)


@transaction.atomic
def criar_entradas():
    """Cria entradas na Girassol baseadas nas saídas do Favo de Mel"""
    
    print("=" * 80)
    print("CRIAR ENTRADAS GIRASSOL DO FAVO DE MEL")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamentos
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        propriedade=girassol
    ).order_by('-data_criacao', '-ano').first()
    
    print(f"\n[INFO] Planejamento Favo de Mel: {planejamento_favo.codigo}")
    print(f"[INFO] Planejamento Girassol: {planejamento_girassol.codigo}")
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    
    # Buscar saídas do Favo de Mel
    saidas_favo = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_favo
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Saídas do Favo de Mel encontradas: {saidas_favo.count()}")
    
    # Criar entradas na Girassol
    entradas_criadas = 0
    for saida in saidas_favo:
        # Verificar se já existe entrada
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            categoria=categoria_garrote,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            data_movimentacao=saida.data_movimentacao,
            quantidade=saida.quantidade,
            planejamento=planejamento_girassol
        ).first()
        
        if entrada_existente:
            print(f"  [INFO] Entrada já existe para {saida.data_movimentacao.strftime('%d/%m/%Y')}")
        else:
            # Criar entrada
            MovimentacaoProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria_garrote,
                data_movimentacao=saida.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=saida.quantidade,
                planejamento=planejamento_girassol,
                observacao=f'Transferencia de Favo de Mel - {saida.quantidade} garrotes - CONFIGURACAO PADRAO: 480 a cada 90 dias'
            )
            print(f"  [OK] Entrada criada: {saida.quantidade} garrotes em {saida.data_movimentacao.strftime('%d/%m/%Y')}")
            entradas_criadas += 1
    
    print(f"\n[RESUMO] Entradas criadas: {entradas_criadas}")
    print("\n[OK] Concluido!")


if __name__ == '__main__':
    try:
        criar_entradas()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()




















