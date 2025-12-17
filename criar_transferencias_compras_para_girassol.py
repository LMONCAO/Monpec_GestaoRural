# -*- coding: utf-8 -*-
"""
Script para criar transferências das compras para Girassol
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
def criar_transferencias():
    """Cria transferências das compras para Girassol"""
    
    print("=" * 80)
    print("CRIAR TRANSFERENCIAS DAS COMPRAS PARA GIRASSOL")
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
    
    # Buscar compras
    compras = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='COMPRA',
        planejamento=planejamento_favo
    ).order_by('data_movimentacao')
    
    print(f"\n[INFO] Compras encontradas: {compras.count()}")
    
    transferencias_criadas = 0
    
    for compra in compras:
        # Verificar se já existe transferência de saída para esta compra
        saida_existente = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            categoria=categoria_garrote,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            data_movimentacao=compra.data_movimentacao,
            quantidade=compra.quantidade,
            planejamento=planejamento_favo,
            observacao__icontains='comprados'
        ).first()
        
        if saida_existente:
            print(f"  [INFO] Transferência de saída já existe para {compra.data_movimentacao.strftime('%d/%m/%Y')}")
        else:
            # Criar transferência de saída
            MovimentacaoProjetada.objects.create(
                propriedade=favo_mel,
                categoria=categoria_garrote,
                data_movimentacao=compra.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_SAIDA',
                quantidade=compra.quantidade,
                planejamento=planejamento_favo,
                observacao=f'Transferencia para Girassol - {compra.quantidade} garrotes comprados - NOVA REGRA 2025: compra transferida imediatamente'
            )
            print(f"  [OK] Transferência de saída criada: {compra.quantidade} garrotes em {compra.data_movimentacao.strftime('%d/%m/%Y')}")
        
        # Verificar se já existe transferência de entrada na Girassol
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            categoria=categoria_garrote,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            data_movimentacao=compra.data_movimentacao,
            quantidade=compra.quantidade,
            planejamento=planejamento_girassol,
            observacao__icontains='comprados'
        ).first()
        
        if entrada_existente:
            print(f"  [INFO] Transferência de entrada já existe para {compra.data_movimentacao.strftime('%d/%m/%Y')}")
        else:
            # Criar transferência de entrada
            MovimentacaoProjetada.objects.create(
                propriedade=girassol,
                categoria=categoria_garrote,
                data_movimentacao=compra.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=compra.quantidade,
                planejamento=planejamento_girassol,
                observacao=f'Transferencia de Favo de Mel - {compra.quantidade} garrotes comprados - NOVA REGRA 2025: ficam 90 dias e vendem de 100 em 100'
            )
            print(f"  [OK] Transferência de entrada criada: {compra.quantidade} garrotes em {compra.data_movimentacao.strftime('%d/%m/%Y')}")
            transferencias_criadas += 1
    
    print(f"\n[RESUMO] Transferências criadas: {transferencias_criadas}")
    print("\n[OK] Concluido!")


if __name__ == '__main__':
    try:
        criar_transferencias()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()











