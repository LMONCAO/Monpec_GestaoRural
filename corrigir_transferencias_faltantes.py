# -*- coding: utf-8 -*-
"""
Script para corrigir transferencias faltantes de Canta Galo para Favo de Mel
Cria as transferencias de ENTRADA que estao faltando
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    Propriedade, CategoriaAnimal, MovimentacaoProjetada
)
from django.db.models import Q
from datetime import date
from decimal import Decimal

def corrigir_transferencias():
    """Corrige transferencias faltantes criando as entradas correspondentes"""
    
    print("=" * 80)
    print("CORRECAO DE TRANSFERENCIAS FALTANTES - CANTA GALO -> FAVO DE MEL")
    print("=" * 80)
    print()
    
    # Buscar propriedades
    canta_galo = Propriedade.objects.filter(
        nome_propriedade__icontains='Canta Galo'
    ).first()
    
    favo_mel = Propriedade.objects.filter(
        nome_propriedade__icontains='Favo de Mel'
    ).first()
    
    if not canta_galo:
        print("ERRO: Fazenda Canta Galo nao encontrada!")
        return
    
    if not favo_mel:
        print("ERRO: Fazenda Favo de Mel nao encontrada!")
        return
    
    print(f"OK - Fazenda Canta Galo: {canta_galo.nome_propriedade} (ID: {canta_galo.id})")
    print(f"OK - Fazenda Favo de Mel: {favo_mel.nome_propriedade} (ID: {favo_mel.id})")
    print()
    
    # Buscar todas as transferencias de SAIDA de Canta Galo (2024+)
    # Vamos verificar todas e criar entradas em Favo de Mel se for o caso
    transferencias_saida = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        data_movimentacao__year__gte=2024
    ).select_related('categoria').order_by('data_movimentacao')
    
    print(f"Transferencias de SAIDA encontradas: {transferencias_saida.count()}")
    print()
    
    transferencias_criadas = 0
    
    for transf_saida in transferencias_saida:
        # Verificar se a categoria deve ir para Favo de Mel
        # Machos 12-24 (Garrote) e vacas de descarte devem ir para Favo de Mel a partir de 2024
        categoria_nome_lower = transf_saida.categoria.nome.lower()
        deve_ir_para_favo_mel = False
        
        if 'garrote' in categoria_nome_lower or 'macho 12-24' in categoria_nome_lower or 'macho 12 a 24' in categoria_nome_lower:
            deve_ir_para_favo_mel = True
        elif 'descarte' in categoria_nome_lower and transf_saida.data_movimentacao.year >= 2024:
            deve_ir_para_favo_mel = True
        
        if not deve_ir_para_favo_mel:
            continue
        
        # Verificar se ja existe transferencia de entrada correspondente
        transf_entrada_existe = MovimentacaoProjetada.objects.filter(
            propriedade=favo_mel,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            categoria=transf_saida.categoria,
            data_movimentacao=transf_saida.data_movimentacao,
            quantidade=transf_saida.quantidade
        ).exists()
        
        if transf_entrada_existe:
            print(f"OK - Transferencia de ENTRADA ja existe para: {transf_saida.data_movimentacao.strftime('%d/%m/%Y')} - {transf_saida.quantidade} {transf_saida.categoria.nome}")
        else:
            # Criar transferencia de entrada
            observacao = f'Transferencia automatica de {canta_galo.nome_propriedade} - {transf_saida.categoria.nome}'
            if transf_saida.observacao:
                # Extrair informacoes da observacao original
                if 'estoque inicial' in transf_saida.observacao.lower():
                    ano = transf_saida.data_movimentacao.year
                    observacao = f'Transferencia automatica do estoque inicial do ano {ano} - {transf_saida.categoria.nome} de {canta_galo.nome_propriedade}'
            
            MovimentacaoProjetada.objects.create(
                propriedade=favo_mel,
                categoria=transf_saida.categoria,
                data_movimentacao=transf_saida.data_movimentacao,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                quantidade=transf_saida.quantidade,
                observacao=observacao,
                planejamento=transf_saida.planejamento,
                cenario=transf_saida.cenario
            )
            
            print(f"CRIADO - Transferencia de ENTRADA: {transf_saida.data_movimentacao.strftime('%d/%m/%Y')} - {transf_saida.quantidade} {transf_saida.categoria.nome}")
            transferencias_criadas += 1
    
    print()
    print("=" * 80)
    print(f"CORRECAO CONCLUIDA: {transferencias_criadas} transferencias de ENTRADA criadas")
    print("=" * 80)
    
    # Verificar tambem transferencias de vacas de descarte
    print()
    print("Verificando transferencias de vacas de descarte...")
    
    # Buscar transferencias de descarte
    transferencias_descarte = MovimentacaoProjetada.objects.filter(
        propriedade=canta_galo,
        tipo_movimentacao='TRANSFERENCIA_SAIDA',
        data_movimentacao__year__gte=2024,
        categoria__nome__icontains='Descarte'
    ).select_related('categoria').order_by('data_movimentacao')
    
    for transf_descarte in transferencias_descarte:
        # Verificar se menciona Favo de Mel na observacao ou se e de 2024+
        ano = transf_descarte.data_movimentacao.year
        if ano >= 2024:
            # Verificar se ja existe entrada correspondente
            transf_entrada_existe = MovimentacaoProjetada.objects.filter(
                propriedade=favo_mel,
                tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                categoria=transf_descarte.categoria,
                data_movimentacao=transf_descarte.data_movimentacao,
                quantidade=transf_descarte.quantidade
            ).exists()
            
            if not transf_entrada_existe:
                # Criar transferencia de entrada para Favo de Mel
                observacao = f'Transferencia de vacas de descarte para recria - {transf_descarte.categoria.nome} de {canta_galo.nome_propriedade}'
                
                MovimentacaoProjetada.objects.create(
                    propriedade=favo_mel,
                    categoria=transf_descarte.categoria,
                    data_movimentacao=transf_descarte.data_movimentacao,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    quantidade=transf_descarte.quantidade,
                    observacao=observacao,
                    planejamento=transf_descarte.planejamento,
                    cenario=transf_descarte.cenario
                )
                
                print(f"CRIADO - Transferencia de ENTRADA (descarte): {transf_descarte.data_movimentacao.strftime('%d/%m/%Y')} - {transf_descarte.quantidade} {transf_descarte.categoria.nome}")
                transferencias_criadas += 1

if __name__ == '__main__':
    corrigir_transferencias()

