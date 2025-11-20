#!/usr/bin/env python
"""
Script para verificar onde está o brinco 105500376195137 no sistema
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import AnimalIndividual, BrincoAnimal, Propriedade
from django.db.models import Q
import re

def normalizar_codigo(codigo):
    """Remove caracteres não numéricos"""
    if not codigo:
        return ''
    return re.sub(r'\D', '', str(codigo))

codigo_buscado = "105500376195137"
codigo_normalizado = normalizar_codigo(codigo_buscado)

print("=" * 80)
print(f"VERIFICANDO BRINCO: {codigo_buscado}")
print(f"Código normalizado: {codigo_normalizado}")
print("=" * 80)

# Buscar em todas as propriedades
print("\n1. BUSCANDO COMO ANIMAL INDIVIDUAL:")
print("-" * 80)

animais = AnimalIndividual.objects.filter(
    Q(codigo_sisbov__icontains=codigo_normalizado) |
    Q(numero_brinco__icontains=codigo_normalizado) |
    Q(codigo_eletronico__icontains=codigo_normalizado)
).select_related('propriedade', 'categoria')

if animais.exists():
    print(f"[OK] Encontrados {animais.count()} animal(is):")
    for animal in animais:
        print(f"\n   ID: {animal.id}")
        print(f"   Propriedade: {animal.propriedade.nome_propriedade} (ID: {animal.propriedade.id})")
        print(f"   Código SISBOV: {animal.codigo_sisbov}")
        print(f"   Número Brinco: {animal.numero_brinco}")
        print(f"   Código Eletrônico: {animal.codigo_eletronico}")
        print(f"   Categoria: {animal.categoria.nome if animal.categoria else 'N/A'}")
        print(f"   Status: {animal.get_status_display() if hasattr(animal, 'get_status_display') else 'N/A'}")
        
        # Verificar normalização
        sisbov_norm = normalizar_codigo(animal.codigo_sisbov)
        brinco_norm = normalizar_codigo(animal.numero_brinco)
        eletronico_norm = normalizar_codigo(animal.codigo_eletronico)
        
        print(f"   Normalizados: SISBOV={sisbov_norm}, Brinco={brinco_norm}, Eletrônico={eletronico_norm}")
        print(f"   Match: {'[SIM]' if (sisbov_norm == codigo_normalizado or brinco_norm == codigo_normalizado or eletronico_norm == codigo_normalizado) else '[NAO]'}")
else:
    print("[ERRO] Nenhum animal encontrado com esse codigo")

# Buscar no estoque de brincos
print("\n2. BUSCANDO NO ESTOQUE DE BRINCOS:")
print("-" * 80)

brincos = BrincoAnimal.objects.filter(
    Q(numero_brinco__icontains=codigo_normalizado) |
    Q(codigo_rfid__icontains=codigo_normalizado)
).select_related('propriedade')

if brincos.exists():
    print(f"[OK] Encontrados {brincos.count()} brinco(s) no estoque:")
    for brinco in brincos:
        print(f"\n   ID: {brinco.id}")
        print(f"   Propriedade: {brinco.propriedade.nome_propriedade} (ID: {brinco.propriedade.id})")
        print(f"   Número Brinco: {brinco.numero_brinco}")
        print(f"   Código RFID: {brinco.codigo_rfid}")
        print(f"   Tipo: {brinco.get_tipo_brinco_display() if hasattr(brinco, 'get_tipo_brinco_display') else 'N/A'}")
        print(f"   Status: {brinco.get_status_display() if hasattr(brinco, 'get_status_display') else 'N/A'}")
        
        # Verificar normalização
        brinco_norm = normalizar_codigo(brinco.numero_brinco)
        rfid_norm = normalizar_codigo(brinco.codigo_rfid)
        
        print(f"   Normalizados: Brinco={brinco_norm}, RFID={rfid_norm}")
        print(f"   Match: {'[SIM]' if (brinco_norm == codigo_normalizado or rfid_norm == codigo_normalizado) else '[NAO]'}")
else:
    print("[ERRO] Nenhum brinco encontrado no estoque com esse codigo")

# Buscar por substring (últimos dígitos)
print("\n3. BUSCANDO POR ÚLTIMOS 7 DÍGITOS (número de manejo):")
print("-" * 80)

if len(codigo_normalizado) >= 7:
    ultimos_7 = codigo_normalizado[-7:]
    print(f"Últimos 7 dígitos: {ultimos_7}")
    
    animais_parcial = AnimalIndividual.objects.filter(
        Q(codigo_sisbov__endswith=ultimos_7) |
        Q(numero_brinco__endswith=ultimos_7)
    ).select_related('propriedade')
    
    if animais_parcial.exists():
        print(f"[OK] Encontrados {animais_parcial.count()} animal(is) com ultimos 7 digitos:")
        for animal in animais_parcial[:5]:  # Limitar a 5 para não sobrecarregar
            sisbov_norm = normalizar_codigo(animal.codigo_sisbov)
            brinco_norm = normalizar_codigo(animal.numero_brinco)
            print(f"   Animal {animal.id}: SISBOV={sisbov_norm}, Brinco={brinco_norm}")
    
    brincos_parcial = BrincoAnimal.objects.filter(
        Q(numero_brinco__endswith=ultimos_7) |
        Q(codigo_rfid__endswith=ultimos_7)
    ).select_related('propriedade')
    
    if brincos_parcial.exists():
        print(f"[OK] Encontrados {brincos_parcial.count()} brinco(s) no estoque com ultimos 7 digitos:")
        for brinco in brincos_parcial[:5]:  # Limitar a 5
            brinco_norm = normalizar_codigo(brinco.numero_brinco)
            rfid_norm = normalizar_codigo(brinco.codigo_rfid)
            print(f"   Brinco {brinco.id}: Brinco={brinco_norm}, RFID={rfid_norm}")

# Listar todas as propriedades para referência
print("\n4. PROPRIEDADES NO SISTEMA:")
print("-" * 80)
propriedades = Propriedade.objects.all().order_by('id')
print(f"Total de propriedades: {propriedades.count()}")
for prop in propriedades:
    total_animais = AnimalIndividual.objects.filter(propriedade=prop).count()
    total_brincos = BrincoAnimal.objects.filter(propriedade=prop).count()
    print(f"   ID {prop.id}: {prop.nome_propriedade} - {total_animais} animais, {total_brincos} brincos")

print("\n" + "=" * 80)
print("VERIFICAÇÃO CONCLUÍDA")
print("=" * 80)

