#!/usr/bin/env python
"""
Script para popular equipamentos da Fazenda Demonstração
"""
import os
import sys
import django
from decimal import Decimal
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade
from gestao_rural.models_operacional import Equipamento, TipoEquipamento

def main():
    print("="*60)
    print("POPULANDO EQUIPAMENTOS - FAZENDA DEMONSTRACAO")
    print("="*60)

    # Buscar propriedade
    propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
    if not propriedade:
        print("ERRO: Propriedade Fazenda Demonstracao nao encontrada!")
        return

    print(f"Propriedade: {propriedade.nome_propriedade}")

    # Criar tipos de equipamentos
    tipos_equip = {}
    tipos_nomes = ['Trator', 'Pulverizador', 'Caminhao', 'Maquina de Feno']
    for tipo_nome in tipos_nomes:
        tipo, created = TipoEquipamento.objects.get_or_create(nome=tipo_nome)
        tipos_equip[tipo_nome] = tipo

    print("Tipos de equipamentos verificados/criados")

    # Criar equipamentos
    equipamentos_data = [
        {
            'nome': 'Trator Valtra BM125',
            'tipo': 'Trator',
            'marca': 'Valtra',
            'ano': 2020,
            'valor': Decimal('350000.00')
        },
        {
            'nome': 'Pulverizador Jacto Phoenix 4000',
            'tipo': 'Pulverizador',
            'marca': 'Jacto',
            'ano': 2019,
            'valor': Decimal('45000.00')
        },
        {
            'nome': 'Caminhao Mercedes-Benz Atron 1724',
            'tipo': 'Caminhao',
            'marca': 'Mercedes-Benz',
            'ano': 2018,
            'valor': Decimal('180000.00')
        },
        {
            'nome': 'Enfardadeira New Holland 269',
            'tipo': 'Maquina de Feno',
            'marca': 'New Holland',
            'ano': 2021,
            'valor': Decimal('85000.00')
        },
    ]

    equipamentos_criados = 0
    for equip_data in equipamentos_data:
        tipo_equip = tipos_equip.get(equip_data['tipo'])
        if tipo_equip:
            equipamento, created = Equipamento.objects.get_or_create(
                propriedade=propriedade,
                nome=equip_data['nome'],
                defaults={
                    'tipo': tipo_equip,
                    'marca': equip_data['marca'],
                    'ano': equip_data['ano'],
                    'ativo': True,
                    'valor_aquisicao': equip_data['valor'],
                    'data_aquisicao': date.today().replace(year=equip_data['ano']),
                    'observacoes': f'Equipamento {equip_data["tipo"]} da marca {equip_data["marca"]}'
                }
            )
            if created:
                equipamentos_criados += 1
                print(f"  - {equipamento.nome} ({equipamento.marca} {equipamento.ano})")

    print(f"\nEquipamentos criados: {equipamentos_criados}")
    print("="*60)
    print("EQUIPAMENTOS POPULADOS COM SUCESSO!")
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




