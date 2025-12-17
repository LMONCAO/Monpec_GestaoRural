# -*- coding: utf-8 -*-
"""
Script para criar grupos de despesas variáveis comuns na pecuária
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
from gestao_rural.models_financeiro import GrupoDespesa

# Grupos de despesas variáveis comuns na pecuária
GRUPOS_DESPESAS_VARIAVEIS = [
    {
        'nome': 'Ração e Suplementos',
        'tipo': GrupoDespesa.TIPO_VARIAVEL,
        'descricao': 'Ração, suplementos minerais, vitaminas e concentrados',
        'ordem': 1,
    },
    {
        'nome': 'Medicamentos e Veterinário',
        'tipo': GrupoDespesa.TIPO_VARIAVEL,
        'descricao': 'Medicamentos, vacinas, vermífugos e serviços veterinários',
        'ordem': 2,
    },
    {
        'nome': 'Combustíveis',
        'tipo': GrupoDespesa.TIPO_VARIAVEL,
        'descricao': 'Diesel, gasolina e outros combustíveis para máquinas e veículos',
        'ordem': 3,
    },
    {
        'nome': 'Compra de Animais',
        'tipo': GrupoDespesa.TIPO_VARIAVEL,
        'descricao': 'Aquisição de animais para reposição ou aumento do rebanho',
        'ordem': 4,
    },
    {
        'nome': 'Pastagens e Forragens',
        'tipo': GrupoDespesa.TIPO_VARIAVEL,
        'descricao': 'Sementes, fertilizantes, calcário e insumos para pastagens',
        'ordem': 5,
    },
    {
        'nome': 'Serviços Terceirizados',
        'tipo': GrupoDespesa.TIPO_VARIAVEL,
        'descricao': 'Serviços de manejo, inseminação, castração, etc',
        'ordem': 6,
    },
    {
        'nome': 'Material de Consumo',
        'tipo': GrupoDespesa.TIPO_VARIAVEL,
        'descricao': 'Materiais diversos: cercas, arames, bebedouros, cochos, etc',
        'ordem': 7,
    },
    {
        'nome': 'Transporte de Animais',
        'tipo': GrupoDespesa.TIPO_VARIAVEL,
        'descricao': 'Frete e transporte de animais',
        'ordem': 8,
    },
    {
        'nome': 'Comissões e Taxas de Venda',
        'tipo': GrupoDespesa.TIPO_VARIAVEL,
        'descricao': 'Comissões de leilões, taxas de venda e intermediários',
        'ordem': 9,
    },
    {
        'nome': 'Outras Despesas Variáveis',
        'tipo': GrupoDespesa.TIPO_VARIAVEL,
        'descricao': 'Outras despesas variáveis não categorizadas',
        'ordem': 99,
    },
]

def criar_grupos_despesas_variaveis():
    """Cria grupos de despesas variáveis para pecuária"""
    # Buscar propriedade (Marcelo Sanguino / Fazenda Canta Galo)
    propriedade = Propriedade.objects.filter(
        nome_propriedade__icontains='Canta Galo'
    ).first()
    
    if not propriedade:
        print("❌ ERRO: Propriedade 'Fazenda Canta Galo' não encontrada!")
        print("   Verifique se está usando o banco de dados correto.")
        return
    
    print("=" * 60)
    print("CRIAÇÃO DE GRUPOS DE DESPESAS VARIÁVEIS - PECUÁRIA")
    print("=" * 60)
    print(f"Propriedade: {propriedade.nome_propriedade}")
    print()
    
    cadastrados = 0
    ja_existiam = 0
    
    for grupo_data in GRUPOS_DESPESAS_VARIAVEIS:
        try:
            # Verificar se já existe
            grupo_existente = GrupoDespesa.objects.filter(
                propriedade=propriedade,
                nome=grupo_data['nome'],
                tipo=grupo_data['tipo']
            ).first()
            
            if grupo_existente:
                print(f"⏭️  Já existe: {grupo_data['nome']}")
                ja_existiam += 1
            else:
                # Criar novo grupo
                grupo = GrupoDespesa.objects.create(
                    propriedade=propriedade,
                    nome=grupo_data['nome'],
                    tipo=grupo_data['tipo'],
                    descricao=grupo_data['descricao'],
                    ordem=grupo_data['ordem'],
                    ativo=True,
                )
                print(f"✅ Criado: {grupo_data['nome']}")
                cadastrados += 1
        except Exception as e:
            print(f"❌ Erro ao criar {grupo_data['nome']}: {e}")
    
    print()
    print("=" * 60)
    print("RESUMO")
    print("=" * 60)
    print(f"✅ Criados: {cadastrados}")
    print(f"⏭️  Já existiam: {ja_existiam}")
    print(f"📊 Total de grupos: {len(GRUPOS_DESPESAS_VARIAVEIS)}")
    print()

if __name__ == '__main__':
    criar_grupos_despesas_variaveis()













