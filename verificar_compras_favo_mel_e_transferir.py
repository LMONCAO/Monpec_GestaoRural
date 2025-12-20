# -*- coding: utf-8 -*-
"""
Script para verificar compras no Favo de Mel e criar transferências para Girassol
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
def verificar_e_transferir():
    """Verifica compras e cria transferências"""
    
    print("=" * 80)
    print("VERIFICAR COMPRAS FAVO DE MEL E TRANSFERIR PARA GIRASSOL")
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
    
    # Buscar compras no Favo de Mel
    compras = MovimentacaoProjetada.objects.filter(
        propriedade=favo_mel,
        categoria=categoria_garrote,
        tipo_movimentacao='COMPRA',
        planejamento=planejamento_favo
    ).order_by('data_movimentacao')
    
    print(f"\n[COMPRAS NO FAVO DE MEL]")
    print(f"  Total: {compras.count()}")
    
    if compras.count() == 0:
        print("  [AVISO] Nenhuma compra encontrada. Aplicando configuração padrão do Favo de Mel...")
        try:
            from gestao_rural.configuracao_padrao_favo_mel import aplicar_configuracao_padrao_favo_mel
            aplicar_configuracao_padrao_favo_mel(favo_mel, planejamento_favo)
            print("  [OK] Configuração padrão aplicada!")
            
            # Buscar compras novamente
            compras = MovimentacaoProjetada.objects.filter(
                propriedade=favo_mel,
                categoria=categoria_garrote,
                tipo_movimentacao='COMPRA',
                planejamento=planejamento_favo
            ).order_by('data_movimentacao')
            print(f"  Compras após configuração: {compras.count()}")
        except Exception as e:
            print(f"  [ERRO] {str(e)}")
            return
    
    # Criar transferências para Girassol
    transferencias_criadas = 0
    
    for compra in compras:
        # Verificar se já existe transferência de saída
        saida_existente = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            categoria=categoria_garrote,
            tipo_movimentacao='TRANSFERENCIA_SAIDA',
            data_movimentacao=compra.data_movimentacao,
            quantidade=compra.quantidade,
            planejamento=planejamento_favo
        ).first()
        
        if not saida_existente:
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
            planejamento=planejamento_girassol
        ).first()
        
        if not entrada_existente:
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
    
    # Aplicar configuração padrão da Girassol
    if transferencias_criadas > 0:
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
        verificar_e_transferir()
    except Exception as e:
        print(f"\n[ERRO] {str(e)}")
        import traceback
        traceback.print_exc()
























