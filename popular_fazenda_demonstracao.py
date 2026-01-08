#!/usr/bin/env python
"""
Script para popular Fazenda Demonstração com dados básicos realistas
Banco: monpec_oficial
Dados históricos: Janeiro 2023 até Dezembro 2024 (24 meses)
Projeções: Janeiro 2025 até Junho 2025 (6 meses)
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth import get_user_model
from gestao_rural.models import ProdutorRural, Propriedade, CategoriaAnimal, AnimalIndividual

User = get_user_model()

def main():
    print("="*70)
    print("POPULANDO FAZENDA DEMONSTRACAO - DADOS BASICOS")
    print("="*70)

    # Criar usuário
    usuario, created = User.objects.get_or_create(
        username='demonstracao',
        defaults={
            'email': 'admin@fazendademonstracao.com.br',
            'first_name': 'Fazenda',
            'last_name': 'Demonstracao',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        usuario.set_password('demo2024')
        usuario.save()
        print("Usuario 'demonstracao' criado")

    # Criar produtor
    produtor, created = ProdutorRural.objects.get_or_create(
        cpf_cnpj='01.234.567/0001-01',
        defaults={
            'nome': 'Fazenda Demonstracao Ltda',
            'email': 'contato@fazendademonstracao.com.br',
            'telefone': '(67) 99999-0001',
            'endereco': 'Rodovia BR-060, Km 45',
            'usuario_responsavel': usuario,
            'vai_emitir_nfe': True
        }
    )
    if created:
        print("Produtor criado")

    # Criar propriedade
    propriedade = Propriedade.objects.create(
        nome_propriedade='Fazenda Demonstracao',
        produtor=produtor,
        municipio='Campo Grande',
        uf='MS',
        area_total_ha=1500.00,
        latitude=-20.4697,
        longitude=-54.6201
    )
    print("Propriedade criada")

    # Criar categorias de animais
    categorias = [
        {'nome': 'Vaca em Lactacao', 'sexo': 'F', 'raca': 'NELORE', 'idade_minima_meses': 36, 'peso_medio_kg': Decimal('450.00')},
        {'nome': 'Vaca Seca', 'sexo': 'F', 'raca': 'NELORE', 'idade_minima_meses': 36, 'peso_medio_kg': Decimal('480.00')},
        {'nome': 'Novilha', 'sexo': 'F', 'raca': 'NELORE', 'idade_minima_meses': 18, 'peso_medio_kg': Decimal('320.00')},
        {'nome': 'Bezerra', 'sexo': 'F', 'raca': 'NELORE', 'peso_medio_kg': Decimal('150.00')},
        {'nome': 'Touro Reprodutor', 'sexo': 'M', 'raca': 'NELORE', 'idade_minima_meses': 24, 'peso_medio_kg': Decimal('650.00')},
        {'nome': 'Bezerro', 'sexo': 'M', 'raca': 'NELORE', 'peso_medio_kg': Decimal('160.00')},
    ]

    categorias_objs = {}
    for cat_data in categorias:
        categoria, created = CategoriaAnimal.objects.get_or_create(
            nome=cat_data['nome'],
            defaults=cat_data
        )
        categorias_objs[cat_data['nome']] = categoria

    print("Categorias de animais criadas")

    # Criar animais básicos
    animais_criados = 0
    animais_por_categoria = {
        'Vaca em Lactacao': 15,
        'Vaca Seca': 10,
        'Novilha': 12,
        'Bezerra': 8,
        'Touro Reprodutor': 3,
        'Bezerro': 6,
    }

    for cat_nome, quantidade in animais_por_categoria.items():
        categoria = categorias_objs.get(cat_nome)
        if not categoria:
            continue

        for i in range(quantidade):
            data_nasc = date.today() - timedelta(days=random.randint(365, 1825))
            peso = categoria.peso_medio_kg or Decimal('300')

            # Gerar número de brinco único
            while True:
                numero_brinco = f'DEM{random.randint(100000, 999999)}'
                if not AnimalIndividual.objects.filter(numero_brinco=numero_brinco).exists():
                    break

            try:
                AnimalIndividual.objects.create(
                    propriedade=propriedade,
                    numero_brinco=numero_brinco,
                    categoria=categoria,
                    sexo=categoria.sexo,
                    raca=categoria.raca,
                    data_nascimento=data_nasc,
                    peso_atual_kg=peso,
                    status='ATIVO',
                    status_reprodutivo='VAZIA' if categoria.sexo == 'F' else 'INDEFINIDO',
                    tipo_brinco='ELETRONICO',
                    tipo_origem='NASCIMENTO',
                    status_sanitario='APTO',
                    sistema_criacao='PASTO'
                )
                animais_criados += 1
            except Exception as e:
                print(f"Erro animal {cat_nome}: {e}")
                continue

    print(f"Animais criados: {animais_criados}")

    # Resumo
    print("="*70)
    print("RESUMO - FAZENDA DEMONSTRACAO")
    print("="*70)
    print(f"Propriedade: {propriedade.nome_propriedade}")
    print(f"Animais: {AnimalIndividual.objects.filter(propriedade=propriedade).count()}")
    print(f"Categorias: {CategoriaAnimal.objects.count()}")
    print("="*70)
    print("FAZENDA DEMONSTRACAO PRONTA!")
    print("="*70)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
