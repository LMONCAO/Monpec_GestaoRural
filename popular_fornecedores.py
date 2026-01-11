#!/usr/bin/env python
"""
Script para popular fornecedores da Fazenda Demonstração
"""
import os
import sys
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade
from gestao_rural.models_compras_financeiro import Fornecedor

def main():
    print("="*60)
    print("POPULANDO FORNECEDORES - FAZENDA DEMONSTRACAO")
    print("="*60)

    # Buscar propriedade
    propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
    if not propriedade:
        print("ERRO: Propriedade Fazenda Demonstracao nao encontrada!")
        return

    print(f"Propriedade: {propriedade.nome_propriedade}")

    # Criar fornecedores
    fornecedores_data = [
        {
            'nome': 'Nutripec Racao e Suplementos Ltda',
            'nome_fantasia': 'Nutripec',
            'cpf_cnpj': '10.234.567/0001-11',
            'tipo': 'RACAO',
            'telefone': '(67) 3321-1234',
            'email': 'vendas@nutripec.com.br',
            'cidade': 'Campo Grande',
            'estado': 'MS'
        },
        {
            'nome': 'Vet Agro Medicamentos Veterinarios',
            'nome_fantasia': 'Vet Agro',
            'cpf_cnpj': '11.345.678/0001-22',
            'tipo': 'MEDICAMENTO',
            'telefone': '(67) 3322-2345',
            'email': 'contato@vetagro.com.br',
            'cidade': 'Campo Grande',
            'estado': 'MS'
        },
        {
            'nome': 'Agro Maquinas e Equipamentos S/A',
            'nome_fantasia': 'Agro Maquinas',
            'cpf_cnpj': '12.456.789/0001-33',
            'tipo': 'EQUIPAMENTO',
            'telefone': '(67) 3323-3456',
            'email': 'vendas@agromaquinas.com.br',
            'cidade': 'Dourados',
            'estado': 'MS'
        },
        {
            'nome': 'Posto Combustiveis Rural',
            'nome_fantasia': 'Posto Rural',
            'cpf_cnpj': '13.567.890/0001-44',
            'tipo': 'COMBUSTIVEL',
            'telefone': '(67) 3324-4567',
            'email': 'posto@rural.com.br',
            'cidade': 'Campo Grande',
            'estado': 'MS'
        },
    ]

    fornecedores_criados = 0
    for fornecedor_data in fornecedores_data:
        fornecedor, created = Fornecedor.objects.get_or_create(
            cpf_cnpj=fornecedor_data['cpf_cnpj'],
            defaults={
                'propriedade': propriedade,
                'nome': fornecedor_data['nome'],
                'nome_fantasia': fornecedor_data['nome_fantasia'],
                'tipo': fornecedor_data['tipo'],
                'telefone': fornecedor_data['telefone'],
                'email': fornecedor_data['email'],
                'endereco': f'Rua {fornecedor_data["tipo"].lower()}, 123',
                'cidade': fornecedor_data['cidade'],
                'estado': fornecedor_data['estado'],
                'cep': '79000-000',
                'ativo': True,
                'observacoes': f'Fornecedor de {fornecedor_data["tipo"].lower()}'
            }
        )
        if created:
            fornecedores_criados += 1
            print(f"  - {fornecedor.nome_fantasia} ({fornecedor.tipo})")

    print(f"\nFornecedores criados: {fornecedores_criados}")
    print("="*60)
    print("FORNECEDORES POPULADOS COM SUCESSO!")
    print("="*60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)




