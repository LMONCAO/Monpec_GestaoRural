#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar se o banco de dados está correto (Marcelo Sanguino / Fazenda Canta Galo)
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import ProdutorRural, Propriedade

def verificar_banco():
    """Verifica se o banco de dados contém Marcelo Sanguino e Fazenda Canta Galo"""
    print("=" * 60)
    print("VERIFICACAO DO BANCO DE DADOS")
    print("=" * 60)
    print()
    
    # Verificar se há produtores no banco
    total_produtores = ProdutorRural.objects.count()
    print(f"[INFO] Total de produtores no banco: {total_produtores}")
    
    if total_produtores == 0:
        print("[ERRO] Nenhum produtor encontrado no banco!")
        print("[ERRO] O banco de dados esta vazio ou incorreto!")
        return False
    
    # Buscar produtor (tentar variações do nome)
    produtor = None
    variacoes = ['Sanguino', 'sanguino', 'SANGUINO', 'Marcelo Sanguino', 'Marcelo']
    
    for variacao in variacoes:
        produtor = ProdutorRural.objects.filter(nome__icontains=variacao).first()
        if produtor:
            break
    
    if produtor:
        print(f"[OK] Produtor encontrado: {produtor.nome} (ID: {produtor.id})")
    else:
        print("[ERRO] Produtor 'Marcelo Sanguino' NAO ENCONTRADO!")
        print("       Lista de produtores no banco:")
        for p in ProdutorRural.objects.all()[:10]:
            print(f"         - {p.nome} (ID: {p.id})")
        return False
    
    # Verificar se há propriedades no banco
    total_propriedades = Propriedade.objects.count()
    print(f"[INFO] Total de propriedades no banco: {total_propriedades}")
    
    if total_propriedades == 0:
        print("[ERRO] Nenhuma propriedade encontrada no banco!")
        return False
    
    # Buscar propriedade (tentar variações do nome)
    propriedade = None
    variacoes_prop = ['Canta Galo', 'Canta', 'CANTA', 'canta galo', 'CantaGalo']
    
    for variacao in variacoes_prop:
        propriedade = Propriedade.objects.filter(nome_propriedade__icontains=variacao).first()
        if propriedade:
            break
    
    if propriedade:
        print(f"[OK] Fazenda encontrada: {propriedade.nome_propriedade} (ID: {propriedade.id})")
        
        # Verificar se a propriedade pertence ao produtor correto
        if propriedade.produtor.id != produtor.id:
            print(f"[AVISO] A propriedade pertence a outro produtor: {propriedade.produtor.nome}")
            print("[AVISO] Mas continuando mesmo assim...")
    else:
        print("[ERRO] Fazenda 'Canta Galo' NAO ENCONTRADA!")
        print("       Lista de propriedades no banco:")
        for prop in Propriedade.objects.all()[:10]:
            print(f"         - {prop.nome_propriedade} (ID: {prop.id}) - Produtor: {prop.produtor.nome}")
        return False
    
    print()
    print("=" * 60)
    print("[OK] BANCO DE DADOS CORRETO!")
    print(f"[OK] Produtor: {produtor.nome}")
    print(f"[OK] Fazenda: {propriedade.nome_propriedade}")
    print(f"[OK] Propriedade ID: {propriedade.id}")
    print("=" * 60)
    return True

if __name__ == '__main__':
    sucesso = verificar_banco()
    sys.exit(0 if sucesso else 1)

