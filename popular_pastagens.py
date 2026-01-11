#!/usr/bin/env python
"""
Script para popular pastagens e cochos da Fazenda Demonstração
"""
import os
import sys
import django
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade
from gestao_rural.models_controles_operacionais import Pastagem, Cocho

def main():
    print("="*60)
    print("POPULANDO PASTAGENS E COCHOS - FAZENDA DEMONSTRACAO")
    print("="*60)

    # Buscar propriedade
    propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
    if not propriedade:
        print("ERRO: Propriedade Fazenda Demonstracao nao encontrada!")
        return

    print(f"Propriedade: {propriedade.nome_propriedade}")

    # Criar pastagens
    pastagens_data = [
        {'nome': 'Pastagem Norte', 'tipo': 'BRACHIARIA', 'area': Decimal('200.00')},
        {'nome': 'Pastagem Sul', 'tipo': 'PANICUM', 'area': Decimal('180.00')},
        {'nome': 'Pastagem Leste', 'tipo': 'CYNODON', 'area': Decimal('150.00')},
        {'nome': 'Pastagem Oeste', 'tipo': 'UROCHLOA', 'area': Decimal('170.00')},
        {'nome': 'Pastagem Central', 'tipo': 'BRACHIARIA', 'area': Decimal('160.00')},
    ]

    pastagens_criadas = 0
    pastagens = []

    for past_data in pastagens_data:
        pastagem, created = Pastagem.objects.get_or_create(
            propriedade=propriedade,
            nome=past_data['nome'],
            defaults={
                'tipo_pastagem': past_data['tipo'],
                'area_ha': past_data['area'],
                'capacidade_suporte': past_data['area'] * Decimal('2.5'),
                'status': random.choice(['EM_USO', 'EM_USO', 'EM_USO', 'DESCANSO']),
            }
        )
        if created:
            pastagens_criadas += 1
            pastagens.append(pastagem)
            print(f"  - {pastagem.nome} ({pastagem.area_ha} ha)")

    print(f"\nPastagens criadas: {pastagens_criadas}")

    # Criar cochos
    cochos_criados = 0
    tipos_cocho = ['SAL', 'RACAO', 'AGUA']

    for pastagem in pastagens:
        num_cochos = random.randint(2, 3)
        for i in range(num_cochos):
            tipo = random.choice(tipos_cocho)
            capacidade = Decimal(str(random.randint(200, 600))) if tipo != 'AGUA' else Decimal(str(random.randint(1000, 3000)))

            try:
                cocho, created = Cocho.objects.get_or_create(
                    propriedade=propriedade,
                    pastagem=pastagem,
                    nome=f'{pastagem.nome} - Cocho {i+1} ({tipo})',
                    defaults={
                        'tipo_cocho': tipo,
                        'capacidade': capacidade,
                        'unidade_capacidade': 'KG' if tipo != 'AGUA' else 'L',
                        'status': 'ATIVO'
                    }
                )
                if created:
                    cochos_criados += 1
                    print(f"  - {cocho.nome}")
            except Exception as e:
                print(f"Erro ao criar cocho {pastagem.nome}: {e}")

    print(f"\nCochos criados: {cochos_criados}")
    print("="*60)
    print("PASTAGENS E COCHOS POPULADOS COM SUCESSO!")
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




