#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para cadastrar múltiplos clientes de uma vez
"""
import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade
from gestao_rural.models_cadastros import Cliente

# Lista de clientes fornecida
clientes_nomes = [
    "CLAUDIO BERGMANN",
    "RONALDO SERGIO MARTINS GUIMARAES/BRUNA DE BAR",
    "LUIZ GUSTAVO AGUILLAR STEIM",
    "RODRIGO ARNAS CAVASSA",
    "AGROPECUARIA RIO ESTREITO LTDA",
    "ENRICO CESAR VOLPON",
    "MARIO MAURICIO VASQUEZ BELTRAO",
    "RENATO FELIPE PINHEIRO MARTINS",
    "RUY CANDIDO DA SILVA",
    "LISONETE ROSA POCAI",
    "MARIO MAURICIO VASQUEZ BELTRAO",  # Duplicado - será ignorado
    "RUY CANDIDO DA SILVA",  # Duplicado - será ignorado
    "JBS SA",
    "Beta Carnes",
    "ROBERTO PEDRO TONIAL E OUTROS",
    "CEZAR DELEVATI CARLOTO",
    "ANIEL LUZO LIMA DOS SANTOS"
]

def cadastrar_clientes():
    print("=" * 60)
    print("CADASTRANDO CLIENTES")
    print("=" * 60)
    print()
    
    # Buscar propriedade Fazenda Canta Galo
    propriedade = Propriedade.objects.filter(nome_propriedade__icontains='Canta Galo').first()
    
    if not propriedade:
        print("[ERRO] Propriedade 'Fazenda Canta Galo' nao encontrada!")
        print("   Verifique se a propriedade existe no banco de dados.")
        return
    
    print(f"[OK] Propriedade encontrada: {propriedade.nome_propriedade} (ID: {propriedade.id})")
    print()
    
    clientes_cadastrados = 0
    clientes_ja_existentes = 0
    clientes_erro = 0
    
    # Remover duplicados mantendo ordem
    clientes_unicos = []
    for cliente in clientes_nomes:
        if cliente.strip() and cliente.strip() not in clientes_unicos:
            clientes_unicos.append(cliente.strip())
    
    print(f"Total de clientes unicos: {len(clientes_unicos)}")
    print()
    
    for i, nome_cliente in enumerate(clientes_unicos, 1):
        nome_limpo = nome_cliente.strip()
        
        if not nome_limpo:
            continue
        
        try:
            # Gerar CPF/CNPJ temporario unico (usando indice)
            cpf_cnpj_base = f"00000000000{i:03d}"
            
            # Verificar se ja existe cliente com este nome
            cliente_existente = Cliente.objects.filter(
                propriedade=propriedade,
                nome__iexact=nome_limpo
            ).first()
            
            if cliente_existente:
                print(f"[{i}/{len(clientes_unicos)}] [AVISO] Ja existe: {nome_limpo}")
                clientes_ja_existentes += 1
                continue
            
            # Verificar se CPF/CNPJ ja existe e gerar um novo se necessario
            cpf_cnpj = cpf_cnpj_base
            contador = 0
            while Cliente.objects.filter(cpf_cnpj=cpf_cnpj).exists():
                contador += 1
                cpf_cnpj = f"00000000000{i:03d}{contador:02d}"
            
            # Determinar tipo de pessoa (se tem LTDA, SA, EIRELI, etc. e juridica)
            tipo_pessoa = 'JURIDICA' if any(termo in nome_limpo.upper() for termo in ['LTDA', 'SA', 'EIRELI', 'ME', 'EPP']) else 'FISICA'
            
            # Determinar tipo de cliente (se tem SA, LTDA, pode ser frigorifico)
            tipo_cliente = 'FRIGORIFICO' if any(termo in nome_limpo.upper() for termo in ['FRIGORIFICO', 'JBS', 'BETA CARNES']) else 'OUTROS'
            
            # Criar cliente
            cliente = Cliente.objects.create(
                propriedade=propriedade,
                nome=nome_limpo,
                tipo_pessoa=tipo_pessoa,
                cpf_cnpj=cpf_cnpj,
                tipo_cliente=tipo_cliente,
                ativo=True
            )
            
            print(f"[{i}/{len(clientes_unicos)}] [OK] Cadastrado: {nome_limpo}")
            clientes_cadastrados += 1
            
        except Exception as e:
            print(f"[{i}/{len(clientes_unicos)}] [ERRO] ao cadastrar {nome_limpo}: {str(e)}")
            clientes_erro += 1
    
    print()
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"[OK] Clientes cadastrados: {clientes_cadastrados}")
    print(f"[AVISO] Clientes ja existentes: {clientes_ja_existentes}")
    print(f"[ERRO] Erros: {clientes_erro}")
    print(f"Total processado: {len(clientes_unicos)}")
    print()

if __name__ == '__main__':
    cadastrar_clientes()

