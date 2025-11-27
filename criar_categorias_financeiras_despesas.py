# -*- coding: utf-8 -*-
"""
Script para criar categorias financeiras padrão para despesas na pecuária
"""
import os
import sys
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

# Reconfigurar stdout para UTF-8
sys.stdout.reconfigure(encoding='utf-8')

from gestao_rural.models import Propriedade
from gestao_rural.models_financeiro import CategoriaFinanceira

# Categorias financeiras padrão para despesas na pecuária
CATEGORIAS_DESPESAS = [
    {
        'nome': 'Ração e Suplementos',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Despesas com ração, suplementos minerais, vitaminas e concentrados',
        'cor': '#FF6B6B',
    },
    {
        'nome': 'Medicamentos e Veterinário',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Medicamentos, vacinas, vermífugos e serviços veterinários',
        'cor': '#4ECDC4',
    },
    {
        'nome': 'Combustíveis',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Diesel, gasolina e outros combustíveis para máquinas e veículos',
        'cor': '#FFE66D',
    },
    {
        'nome': 'Mão de Obra',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Salários, encargos sociais e benefícios dos funcionários',
        'cor': '#95E1D3',
    },
    {
        'nome': 'Manutenção e Reparos',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Manutenção de equipamentos, máquinas, instalações e reparos',
        'cor': '#F38181',
    },
    {
        'nome': 'Pastagens e Forragens',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Sementes, fertilizantes, calcário e insumos para pastagens',
        'cor': '#AAE3E2',
    },
    {
        'nome': 'Compra de Animais',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Aquisição de animais para reposição ou aumento do rebanho',
        'cor': '#FFB6C1',
    },
    {
        'nome': 'Energia e Utilidades',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Energia elétrica, água, telefone e internet',
        'cor': '#FFD93D',
    },
    {
        'nome': 'Impostos e Taxas',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Impostos, taxas governamentais e contribuições',
        'cor': '#6BCB77',
    },
    {
        'nome': 'Seguros',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Seguros de equipamentos, veículos, animais e propriedade',
        'cor': '#4D96FF',
    },
    {
        'nome': 'Transporte e Frete',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Frete de animais, insumos e transporte em geral',
        'cor': '#9B59B6',
    },
    {
        'nome': 'Serviços Terceirizados',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Serviços de manejo, inseminação, castração, consultorias',
        'cor': '#E67E22',
    },
    {
        'nome': 'Material de Consumo',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Materiais diversos: cercas, arames, bebedouros, cochos',
        'cor': '#1ABC9C',
    },
    {
        'nome': 'Financiamentos',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Parcelas de financiamentos e empréstimos',
        'cor': '#E74C3C',
    },
    {
        'nome': 'Outras Despesas',
        'tipo': CategoriaFinanceira.TIPO_DESPESA,
        'descricao': 'Outras despesas não categorizadas',
        'cor': '#95A5A6',
    },
]

def criar_categorias_financeiras_despesas():
    """Cria categorias financeiras padrão para despesas"""
    # Buscar propriedade (Marcelo Sanguino / Fazenda Canta Galo)
    propriedade = Propriedade.objects.filter(
        nome_propriedade__icontains='Canta Galo'
    ).first()
    
    if not propriedade:
        print("❌ ERRO: Propriedade 'Fazenda Canta Galo' não encontrada!")
        print("   Verifique se está usando o banco de dados correto.")
        return
    
    print("=" * 60)
    print("CRIAÇÃO DE CATEGORIAS FINANCEIRAS - DESPESAS")
    print("=" * 60)
    print(f"Propriedade: {propriedade.nome_propriedade}")
    print()
    
    cadastradas = 0
    ja_existiam = 0
    
    for cat_data in CATEGORIAS_DESPESAS:
        try:
            # Verificar se já existe
            categoria_existente = CategoriaFinanceira.objects.filter(
                propriedade=propriedade,
                nome=cat_data['nome'],
                tipo=cat_data['tipo']
            ).first()
            
            if categoria_existente:
                print(f"⏭️  Já existe: {cat_data['nome']}")
                ja_existiam += 1
            else:
                # Criar nova categoria
                categoria = CategoriaFinanceira.objects.create(
                    propriedade=propriedade,
                    nome=cat_data['nome'],
                    tipo=cat_data['tipo'],
                    descricao=cat_data['descricao'],
                    cor=cat_data.get('cor', ''),
                    ativa=True,
                )
                print(f"✅ Criada: {cat_data['nome']}")
                cadastradas += 1
        except Exception as e:
            print(f"❌ Erro ao criar {cat_data['nome']}: {e}")
    
    print()
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"✅ Criadas: {cadastradas}")
    print(f"⏭️  Já existiam: {ja_existiam}")
    print(f"📊 Total de categorias: {len(CATEGORIAS_DESPESAS)}")
    print()

if __name__ == '__main__':
    criar_categorias_financeiras_despesas()

