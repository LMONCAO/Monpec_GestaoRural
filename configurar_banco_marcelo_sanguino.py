#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para configurar o banco de dados com Marcelo Sanguino e Fazenda Canta Galo
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import ProdutorRural, Propriedade
from django.contrib.auth.models import User

def configurar_banco():
    """Configura o banco com Marcelo Sanguino e Fazenda Canta Galo"""
    print("=" * 60)
    print("CONFIGURANDO BANCO - MARCELO SANGUINO / FAZENDA CANTA GALO")
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
    
    print(f"[OK] Usuário admin configurado")
    
    # Buscar ou criar produtor Marcelo Sanguino
    produtor, created = ProdutorRural.objects.get_or_create(
        nome__icontains='Marcelo Sanguino',
        defaults={
            'nome': 'Marcelo Sanguino',
            'cpf_cnpj': '00000000000',
            'telefone': '(00) 00000-0000',
            'email': 'marcelo.sanguino@monpec.com.br',
            'usuario_responsavel': usuario,
            'anos_experiencia': 20,
        }
    )
    
    if not created:
        # Atualizar se já existe mas com nome diferente
        produtor.nome = 'Marcelo Sanguino'
        produtor.usuario_responsavel = usuario
        produtor.save()
        print(f"[OK] Produtor atualizado: {produtor.nome} (ID: {produtor.id})")
    else:
        print(f"[OK] Produtor criado: {produtor.nome} (ID: {produtor.id})")
    
    # Buscar ou criar propriedade Fazenda Canta Galo
    propriedade, created = Propriedade.objects.get_or_create(
        nome_propriedade__icontains='Canta Galo',
        defaults={
            'nome_propriedade': 'Fazenda Canta Galo',
            'produtor': produtor,
            'municipio': 'Cidade',
            'uf': 'SP',
            'area_total_ha': 1000.00,
            'tipo_operacao': 'PECUARIA',
            'tipo_ciclo_pecuario': ['CICLO_COMPLETO'],
            'tipo_propriedade': 'PROPRIA',
        }
    )
    
    if not created:
        # Atualizar se já existe mas com nome diferente
        propriedade.nome_propriedade = 'Fazenda Canta Galo'
        propriedade.produtor = produtor
        propriedade.save()
        print(f"[OK] Propriedade atualizada: {propriedade.nome_propriedade} (ID: {propriedade.id})")
    else:
        print(f"[OK] Propriedade criada: {propriedade.nome_propriedade} (ID: {propriedade.id})")
    
    print()
    print("=" * 60)
    print("[OK] BANCO CONFIGURADO COM SUCESSO!")
    print("=" * 60)
    print(f"Produtor: {produtor.nome} (ID: {produtor.id})")
    print(f"Propriedade: {propriedade.nome_propriedade} (ID: {propriedade.id})")
    print()
    print("O sistema está pronto para uso com Marcelo Sanguino!")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    try:
        configurar_banco()
        sys.exit(0)
    except Exception as e:
        print(f"[ERRO] Erro ao configurar banco: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



