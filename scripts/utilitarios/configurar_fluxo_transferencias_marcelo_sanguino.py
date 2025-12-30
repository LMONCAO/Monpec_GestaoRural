#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para configurar o fluxo completo de transferências entre as propriedades do Marcelo Sanguino

FLUXO:
1. Fazenda Canta Galo (Matriz) → Invernada Grande: Vacas de descarte (2022-2025)
2. Fazenda Canta Galo (Matriz) → Favo de Mel: Machos 12-24 meses
3. Favo de Mel: Vende 100 cabeças a cada 60 dias (sem saldo negativo)
4. Favo de Mel → Girassol: Animais com categoria modificada
5. Girassol: Animais ficam 90 dias e viram boi gordo
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, date

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, 
    ConfiguracaoVenda, PoliticaVendasCategoria
)

def configurar_fluxo_transferencias():
    """Configura o fluxo completo de transferências"""
    print("=" * 60)
    print("CONFIGURANDO FLUXO DE TRANSFERÊNCIAS - MARCELO SANGUINO")
    print("=" * 60)
    print()
    
    # Buscar propriedades
    produtor = ProdutorRural.objects.filter(nome__icontains='Marcelo Sanguino').first()
    if not produtor:
        print("[ERRO] Produtor Marcelo Sanguino não encontrado!")
        print("Execute primeiro: python configurar_propriedades_marcelo_sanguino.py")
        return False
    
    canta_galo = Propriedade.objects.filter(
        nome_propriedade__icontains='Canta Galo',
        produtor=produtor
    ).first()
    
    invernada_grande = Propriedade.objects.filter(
        nome_propriedade__icontains='Invernada Grande',
        produtor=produtor
    ).first()
    
    favo_mel = Propriedade.objects.filter(
        nome_propriedade__icontains='Favo de Mel',
        produtor=produtor
    ).first()
    
    girassol = Propriedade.objects.filter(
        nome_propriedade__icontains='Girassol',
        produtor=produtor
    ).first()
    
    if not all([canta_galo, invernada_grande, favo_mel, girassol]):
        print("[ERRO] Algumas propriedades não foram encontradas!")
        print("Execute primeiro: python configurar_propriedades_marcelo_sanguino.py")
        return False
    
    print("[OK] Propriedades encontradas:")
    print(f"  - {canta_galo.nome_propriedade} (ID: {canta_galo.id})")
    print(f"  - {invernada_grande.nome_propriedade} (ID: {invernada_grande.id})")
    print(f"  - {favo_mel.nome_propriedade} (ID: {favo_mel.id})")
    print(f"  - {girassol.nome_propriedade} (ID: {girassol.id})")
    print()
    
    # Buscar categorias necessárias
    categorias = {}
    nomes_categorias = [
        'Vaca em Reprodução +36 M',
        'Vaca de Descarte',
        'Garrote 12-24 M',
        'Novilho 12-24 M',
        'Boi 24-36 M',
        'Boi Gordo',
    ]
    
    for nome_cat in nomes_categorias:
        categoria = CategoriaAnimal.objects.filter(nome__icontains=nome_cat.split()[0]).first()
        if categoria:
            categorias[nome_cat] = categoria
            print(f"[OK] Categoria encontrada: {categoria.nome}")
        else:
            print(f"[AVISO] Categoria não encontrada: {nome_cat}")
    
    print()
    
    # ========================================
    # CONFIGURAÇÃO 1: Canta Galo → Invernada Grande
    # Vacas de Descarte (2022-2025)
    # ========================================
    print("[1/4] Configurando: Canta Galo → Invernada Grande (Vacas de Descarte)")
    
    categoria_descarte = categorias.get('Vaca de Descarte')
    if categoria_descarte:
        # Configuração de transferência anual (janeiro de cada ano)
        # IMPORTANTE: fazenda_origem é de onde vem, propriedade é onde recebe
        config, created = ConfiguracaoVenda.objects.get_or_create(
            propriedade=invernada_grande,  # Propriedade que RECEBE
            categoria_venda=categoria_descarte,
            tipo_reposicao='TRANSFERENCIA',
            defaults={
                'frequencia_venda': 'ANUAL',  # Apenas em janeiro
                'quantidade_venda': 0,  # Não vende, apenas recebe
                'fazenda_origem': canta_galo,  # De onde vem
                'quantidade_transferencia': 0,  # Será calculado automaticamente (100% do estoque inicial)
                'ativo': True,
            }
        )
        if created:
            print(f"  [OK] Configuração criada: Recebe vacas de descarte de {canta_galo.nome_propriedade}")
        else:
            print(f"  [OK] Configuração já existe")
    else:
        print(f"  [AVISO] Categoria 'Vaca de Descarte' não encontrada")
    print()
    
    # ========================================
    # CONFIGURAÇÃO 2: Canta Galo → Favo de Mel
    # Machos 12-24 meses (Garrotes/Novilhos)
    # ========================================
    print("[2/4] Configurando: Canta Galo → Favo de Mel (Machos 12-24 meses)")
    
    categoria_machos = categorias.get('Garrote 12-24 M') or categorias.get('Novilho 12-24 M')
    if categoria_machos:
        config, created = ConfiguracaoVenda.objects.get_or_create(
            propriedade=favo_mel,  # Propriedade que RECEBE
            categoria_venda=categoria_machos,
            tipo_reposicao='TRANSFERENCIA',
            defaults={
                'frequencia_venda': 'ANUAL',  # Apenas em janeiro
                'quantidade_venda': 0,
                'fazenda_origem': canta_galo,  # De onde vem
                'quantidade_transferencia': 0,  # Será calculado automaticamente (100% do estoque inicial)
                'ativo': True,
            }
        )
        if created:
            print(f"  [OK] Configuração criada: Recebe machos 12-24 meses de {canta_galo.nome_propriedade}")
        else:
            print(f"  [OK] Configuração já existe")
    else:
        print(f"  [AVISO] Categoria de machos 12-24 meses não encontrada")
    print()
    
    # ========================================
    # CONFIGURAÇÃO 3: Favo de Mel - Vendas
    # 100 cabeças a cada 60 dias (sem saldo negativo)
    # ========================================
    print("[3/4] Configurando: Favo de Mel - Vendas (100 cabeças a cada 60 dias)")
    
    # Buscar categoria que será vendida na Favo de Mel
    # (provavelmente a mesma que recebe, mas após evoluir)
    categoria_venda_favo = categorias.get('Boi 24-36 M') or categoria_machos
    
    if categoria_venda_favo:
        config, created = ConfiguracaoVenda.objects.get_or_create(
            propriedade=favo_mel,
            categoria_venda=categoria_venda_favo,
            tipo_reposicao='VENDA',
            defaults={
                'frequencia_venda': 'BIMESTRAL',  # A cada 60 dias
                'quantidade_venda': 100,
                'ativo': True,
            }
        )
        if created:
            print(f"  [OK] Configuração criada: Vende 100 cabeças a cada 60 dias")
        else:
            config.quantidade_venda = 100
            config.frequencia_venda = 'BIMESTRAL'
            config.save()
            print(f"  [OK] Configuração atualizada: Vende 100 cabeças a cada 60 dias")
    else:
        print(f"  [AVISO] Categoria para venda não encontrada")
    print()
    
    # ========================================
    # CONFIGURAÇÃO 4: Favo de Mel → Girassol
    # Animais com categoria modificada
    # ========================================
    print("[4/4] Configurando: Favo de Mel → Girassol (Animais após evolução)")
    
    categoria_girassol = categorias.get('Boi 24-36 M') or categorias.get('Boi Gordo')
    if categoria_girassol and categoria_venda_favo:
        config, created = ConfiguracaoVenda.objects.get_or_create(
            propriedade=girassol,  # Propriedade que RECEBE
            categoria_venda=categoria_girassol,
            tipo_reposicao='TRANSFERENCIA',
            defaults={
                'frequencia_venda': 'TRIMESTRAL',  # A cada 90 dias aproximadamente
                'quantidade_venda': 0,
                'fazenda_origem': favo_mel,  # De onde vem
                'quantidade_transferencia': 0,  # Será calculado automaticamente
                'ativo': True,
            }
        )
        if created:
            print(f"  [OK] Configuração criada: Recebe animais de {favo_mel.nome_propriedade}")
        else:
            print(f"  [OK] Configuração já existe")
    else:
        print(f"  [AVISO] Categorias não encontradas")
    print()
    
    print("=" * 60)
    print("[OK] CONFIGURAÇÃO DE TRANSFERÊNCIAS CONCLUÍDA!")
    print("=" * 60)
    print()
    print("Resumo das configurações:")
    print("  1. Canta Galo → Invernada Grande: Vacas de descarte (anual)")
    print("  2. Canta Galo → Favo de Mel: Machos 12-24 meses (anual)")
    print("  3. Favo de Mel: Vende 100 cabeças a cada 60 dias")
    print("  4. Favo de Mel → Girassol: Animais após evolução (trimestral)")
    print()
    print("Próximo passo: Configurar inventário inicial na Canta Galo")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        sucesso = configurar_fluxo_transferencias()
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"[ERRO] Erro ao configurar transferências: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

