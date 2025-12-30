#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar logs de envio de email
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')

import django
django.setup()

from gestao_rural.models_compras_financeiro import ConviteCotacaoFornecedor
from django.utils import timezone
from datetime import timedelta

def verificar_convites_recentes():
    """Verifica convites criados recentemente"""
    
    print("=" * 70)
    print("  VERIFICACAO DE CONVITES DE COTACAO")
    print("=" * 70)
    print()
    
    # Buscar convites das últimas 24 horas
    agora = timezone.now()
    ontem = agora - timedelta(hours=24)
    
    convites = ConviteCotacaoFornecedor.objects.filter(
        criado_em__gte=ontem
    ).order_by('-criado_em')
    
    print(f"Convites criados nas ultimas 24 horas: {convites.count()}")
    print()
    
    for convite in convites[:10]:  # Mostrar os 10 mais recentes
        print(f"ID: {convite.id}")
        print(f"  Requisicao: {convite.requisicao.numero}")
        print(f"  Fornecedor: {convite.fornecedor.nome}")
        print(f"  Email destinatario: {convite.email_destinatario}")
        print(f"  Status: {convite.status}")
        print(f"  Enviado em: {convite.enviado_em if convite.enviado_em else 'Nao enviado'}")
        print(f"  Criado em: {convite.criado_em}")
        print()
    
    # Verificar se há convites sem email enviado
    nao_enviados = convites.filter(enviado_em__isnull=True)
    if nao_enviados.exists():
        print(f"⚠️  {nao_enviados.count()} convite(s) criado(s) mas nao enviado(s)")
        print()
    
    return convites


if __name__ == '__main__':
    try:
        verificar_convites_recentes()
    except Exception as e:
        print(f"\n[ERRO] {e}")
        import traceback
        traceback.print_exc()










































