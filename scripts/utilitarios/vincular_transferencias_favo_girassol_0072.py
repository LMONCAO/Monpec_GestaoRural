# -*- coding: utf-8 -*-
"""
Script para vincular transferências do Favo de Mel para Girassol ao planejamento PROJ-2025-0072
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.db import transaction
from gestao_rural.models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, PlanejamentoAnual
)


@transaction.atomic
def vincular_transferencias():
    """Vincula transferências do Favo de Mel para Girassol ao planejamento PROJ-2025-0072"""
    
    print("=" * 80)
    print("VINCULAR TRANSFERENCIAS FAVO DE MEL -> GIRASSOL PROJ-2025-0072")
    print("=" * 80)
    
    favo_mel = Propriedade.objects.get(nome_propriedade__icontains='Favo de Mel')
    girassol = Propriedade.objects.get(nome_propriedade__icontains='Girassol')
    
    # Buscar planejamentos
    planejamento_favo = PlanejamentoAnual.objects.filter(
        propriedade=favo_mel
    ).order_by('-data_criacao', '-ano').first()
    
    planejamento_girassol = PlanejamentoAnual.objects.filter(
        codigo='PROJ-2025-0072'
    ).first()
    
    if not planejamento_girassol:
        print("\n[ERRO] Planejamento PROJ-2025-0072 não encontrado!")
        return
    
    print(f"\n[INFO] Planejamento Favo de Mel: {planejamento_favo.codigo if planejamento_favo else 'Nenhum'}")
    print(f"[INFO] Planejamento Girassol: {planejamento_girassol.codigo}")
    
    # Buscar categoria
    categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
    
    # Buscar TODAS as transferências de saída do Favo de Mel para Girassol
    saidas_favo_mel = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        planejamento=planejamento_favo,
        observacao__icontains='Girassol'
    ).order_by('data_movimentacao')
    
    print(f"\n[TRANSFERENCIAS DE SAIDA DO FAVO DE MEL]")
    print(f"  Total: {saidas_favo_mel.count()}")
    
    transferencias_vinculadas = 0
    entradas_criadas = 0
    
    for saida in saidas_favo_mel:
        # Verificar se já existe entrada correspondente na Girassol no planejamento PROJ-2025-0072
        entrada_existente = MovimentacaoProjetada.objects.filter(
            propriedade=girassol,
            categoria=categoria_garrote,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            data_movimentacao=saida.data_movimentacao,
            quantidade=saida.quantidade,
            planejamento=planejamento_girassol
        ).first()
        
        if not entrada_existente:
            # Criar entrada na Girassol
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
        else:
            print(f"  [INFO] Entrada já existe: {saida.quantidade} garrotes em {saida.data_movimentacao.strftime('%d/%m/%Y')}")
    
    print(f"\n[RESUMO]")
    print(f"  Transferências processadas: {saidas_favo_mel.count()}")
    print(f"  Entradas criadas: {entradas_criadas}")
    
    # Aplicar configuração padrão da Girassol para criar evoluções e vendas
    if entradas_criadas > 0:
        print("\n[Aplicando configuração padrão da Girassol...]")
        try:
            from gestao_rural.configuracao_padrao_girassol import aplicar_configuracao_padrao_girassol
            aplicar_configuracao_padrao_girassol(girassol, planejamento_girassol)
            print("[OK] Configuração padrão aplicada!")
        except Exception as e:
            print(f"[ERRO] {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n[OK] Concluido!")


if __name__ == '__main__':
    try:
        vincular_transferencias()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























