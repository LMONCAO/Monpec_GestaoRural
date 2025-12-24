#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para configurar as 4 propriedades do Marcelo Sanguino
e configurar o fluxo de transferências entre elas
"""
import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import ProdutorRural, Propriedade
from django.contrib.auth.models import User

def criar_propriedades():
    """Cria as 4 propriedades do Marcelo Sanguino"""
    print("=" * 60)
    print("CONFIGURANDO PROPRIEDADES - MARCELO SANGUINO")
    print("=" * 60)
    print()
    
    # Buscar ou criar usuário admin
    usuario, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@monpec.com.br',
            'first_name': 'Admin',
            'last_name': 'Sistema',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if not usuario.check_password('admin'):
        usuario.set_password('admin')
        usuario.save()
    
    # Buscar produtor Marcelo Sanguino
    produtor = ProdutorRural.objects.filter(nome__icontains='Marcelo Sanguino').first()
    if not produtor:
        produtor = ProdutorRural.objects.create(
            nome='Marcelo Sanguino',
            cpf_cnpj='00000000000',
            telefone='(00) 00000-0000',
            email='marcelo.sanguino@monpec.com.br',
            usuario_responsavel=usuario,
            anos_experiencia=20,
        )
        print(f"[OK] Produtor criado: {produtor.nome} (ID: {produtor.id})")
    else:
        print(f"[OK] Produtor encontrado: {produtor.nome} (ID: {produtor.id})")
    print()
    
    # Lista de propriedades
    propriedades_config = [
        {
            'nome': 'Fazenda Canta Galo',
            'municipio': 'Cidade',
            'uf': 'SP',
            'area_total_ha': 1000.00,
            'tipo_operacao': 'PECUARIA',
            'tipo_ciclo_pecuario': ['CICLO_COMPLETO'],
            'tipo_propriedade': 'PROPRIA',
            'descricao': 'Propriedade matriz - transfere gado para outras fazendas',
        },
        {
            'nome': 'Invernada Grande',
            'municipio': 'Cidade',
            'uf': 'SP',
            'area_total_ha': 800.00,
            'tipo_operacao': 'PECUARIA',
            'tipo_ciclo_pecuario': ['ENGORDA'],
            'tipo_propriedade': 'PROPRIA',
            'descricao': 'Recebe vacas de descarte da Canta Galo',
        },
        {
            'nome': 'Favo de Mel',
            'municipio': 'Cidade',
            'uf': 'SP',
            'area_total_ha': 600.00,
            'tipo_operacao': 'PECUARIA',
            'tipo_ciclo_pecuario': ['RECRIA'],
            'tipo_propriedade': 'PROPRIA',
            'descricao': 'Recebe machos 12-24 meses, vende 100 cabeças a cada 60 dias',
        },
        {
            'nome': 'Girassol',
            'municipio': 'Cidade',
            'uf': 'SP',
            'area_total_ha': 500.00,
            'tipo_operacao': 'PECUARIA',
            'tipo_ciclo_pecuario': ['ENGORDA'],
            'tipo_propriedade': 'PROPRIA',
            'descricao': 'Recebe animais da Favo de Mel, ficam 90 dias e viram boi gordo',
        },
    ]
    
    propriedades_criadas = []
    
    for prop_config in propriedades_config:
        propriedade, created = Propriedade.objects.get_or_create(
            nome_propriedade=prop_config['nome'],
            produtor=produtor,
            defaults={
                'municipio': prop_config['municipio'],
                'uf': prop_config['uf'],
                'area_total_ha': Decimal(str(prop_config['area_total_ha'])),
                'tipo_operacao': prop_config['tipo_operacao'],
                'tipo_ciclo_pecuario': prop_config['tipo_ciclo_pecuario'],
                'tipo_propriedade': prop_config['tipo_propriedade'],
            }
        )
        
        if created:
            print(f"[OK] Propriedade criada: {propriedade.nome_propriedade} (ID: {propriedade.id})")
        else:
            print(f"[OK] Propriedade já existe: {propriedade.nome_propriedade} (ID: {propriedade.id})")
        
        propriedades_criadas.append(propriedade)
    
    print()
    print("=" * 60)
    print("[OK] PROPRIEDADES CONFIGURADAS!")
    print("=" * 60)
    print()
    print("Propriedades criadas:")
    for prop in propriedades_criadas:
        print(f"  - {prop.nome_propriedade} (ID: {prop.id})")
    print()
    print("Próximo passo: Configurar transferências automáticas")
    print("=" * 60)
    
    return propriedades_criadas

if __name__ == '__main__':
    try:
        propriedades = criar_propriedades()
        sys.exit(0)
    except Exception as e:
        print(f"[ERRO] Erro ao configurar propriedades: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

