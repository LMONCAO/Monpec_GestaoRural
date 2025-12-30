#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para atualizar preços dos planos no banco de dados
"""
import os
import sys
import django

# Adicionar o diretório do projeto ao path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

try:
    django.setup()
except Exception as e:
    print(f"Erro ao configurar Django: {e}")
    sys.exit(1)

from gestao_rural.models import PlanoAssinatura
from decimal import Decimal

def atualizar_precos():
    """Atualiza todos os planos ativos para R$ 99,90"""
    preco = Decimal('99.90')
    print(f"\n{'='*60}")
    print(f"Atualizando preços dos planos para R$ {preco}")
    print(f"{'='*60}\n")
    
    planos = PlanoAssinatura.objects.filter(ativo=True)
    
    if not planos.exists():
        print('[AVISO] Nenhum plano ativo encontrado no banco de dados.')
        return
    
    print(f"Encontrados {planos.count()} plano(s) ativo(s):\n")
    
    atualizados = 0
    for plano in planos:
        preco_antigo = plano.preco_mensal_referencia
        plano.preco_mensal_referencia = preco
        plano.save()
        atualizados += 1
        
        preco_antigo_str = f"R$ {preco_antigo}" if preco_antigo else "nao definido"
        print(f"  [OK] Plano: {plano.nome}")
        print(f"    Preco anterior: {preco_antigo_str}")
        print(f"    Novo preco: R$ {preco}")
        print()
    
    print(f"{'='*60}")
    print(f"[SUCESSO] {atualizados} plano(s) atualizado(s) com sucesso!")
    print(f"{'='*60}\n")
    
    # Verificar se há planos inativos também
    planos_inativos = PlanoAssinatura.objects.filter(ativo=False)
    if planos_inativos.exists():
        print(f"[INFO] Nota: Existem {planos_inativos.count()} plano(s) inativo(s) que nao foram alterados.\n")

if __name__ == '__main__':
    try:
        atualizar_precos()
    except Exception as e:
        print(f"\n[ERRO] Erro ao atualizar precos: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

