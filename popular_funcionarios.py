#!/usr/bin/env python
"""
Script para popular funcionários da Fazenda Demonstração
"""
import os
import sys
import django
from datetime import date
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade
from gestao_rural.models_funcionarios import Funcionario

def main():
    print("="*60)
    print("POPULANDO FUNCIONARIOS - FAZENDA DEMONSTRACAO")
    print("="*60)

    # Buscar propriedade
    propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
    if not propriedade:
        print("ERRO: Propriedade Fazenda Demonstracao nao encontrada!")
        return

    print(f"Propriedade: {propriedade.nome_propriedade}")

    # Criar funcionários
    funcionarios_data = [
        {
            'nome': 'Joao Silva',
            'cpf': '123.456.789-00',
            'cargo': 'Gerente de Fazenda',
            'salario': Decimal('8500.00')
        },
        {
            'nome': 'Maria Santos',
            'cpf': '234.567.890-11',
            'cargo': 'Veterinaria',
            'salario': Decimal('6800.00')
        },
        {
            'nome': 'Pedro Oliveira',
            'cpf': '345.678.901-22',
            'cargo': 'Capataz',
            'salario': Decimal('4800.00')
        },
        {
            'nome': 'Carlos Souza',
            'cpf': '456.789.012-33',
            'cargo': 'Vaqueiro',
            'salario': Decimal('2700.00')
        },
        {
            'nome': 'Antonio Costa',
            'cpf': '567.890.123-44',
            'cargo': 'Vaqueiro',
            'salario': Decimal('2700.00')
        },
        {
            'nome': 'Roberto Alves',
            'cpf': '678.901.234-55',
            'cargo': 'Mecanico',
            'salario': Decimal('3800.00')
        },
    ]

    funcionarios_criados = 0
    for func_data in funcionarios_data:
        funcionario, created = Funcionario.objects.get_or_create(
            cpf=func_data['cpf'],
            defaults={
                'propriedade': propriedade,
                'nome': func_data['nome'],
                'cargo': func_data['cargo'],
                'salario_base': func_data['salario'],
                'tipo_contrato': 'CLT',
                'data_admissao': date.today().replace(year=date.today().year - random.randint(1, 5)),
                'situacao': 'ATIVO',
                'sexo': random.choice(['M', 'F']),
                'telefone': f'(67) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                'cidade': 'Campo Grande',
                'estado': 'MS',
                'jornada_trabalho': 44
            }
        )
        if created:
            funcionarios_criados += 1
            print(f"  - {funcionario.nome} ({funcionario.cargo})")

    print(f"\nFuncionarios criados: {funcionarios_criados}")
    print("="*60)
    print("FUNCIONARIOS POPULADOS COM SUCESSO!")
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
