# -*- coding: utf-8 -*-
"""
Script para criar grupos de despesas fixas comuns na pecuária
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

# Grupos de despesas fixas comuns na pecuária
GRUPOS_DESPESAS_FIXAS = [
    {
        'nome': 'Mão de Obra',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Salários, encargos sociais e benefícios dos funcionários',
        'ordem': 1,
    },
    {
        'nome': 'Aluguel/Arrendamento',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Aluguel de pastos, arrendamento de terras e instalações',
        'ordem': 2,
    },
    {
        'nome': 'Energia Elétrica',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Conta de energia elétrica das instalações',
        'ordem': 3,
    },
    {
        'nome': 'Água e Saneamento',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Conta de água, esgoto e saneamento',
        'ordem': 4,
    },
    {
        'nome': 'Telefone e Internet',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Telefonia fixa, móvel e serviços de internet',
        'ordem': 5,
    },
    {
        'nome': 'Manutenção de Instalações',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Manutenção preventiva e corretiva de currais, cercas, cochos, etc',
        'ordem': 6,
    },
    {
        'nome': 'Manutenção de Equipamentos',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Manutenção de tratores, máquinas e equipamentos',
        'ordem': 7,
    },
    {
        'nome': 'Seguros',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Seguros de equipamentos, instalações e animais',
        'ordem': 8,
    },
    {
        'nome': 'Impostos e Taxas',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'IPTU, ITR, taxas de licenciamento e outros impostos fixos',
        'ordem': 9,
    },
    {
        'nome': 'Assessoria e Consultoria',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Serviços de contabilidade, consultoria veterinária, agronômica',
        'ordem': 10,
    },
    {
        'nome': 'Depreciação',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Depreciação de equipamentos, veículos e benfeitorias',
        'ordem': 11,
    },
    {
        'nome': 'Financiamentos e Empréstimos',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Parcelas de financiamentos e empréstimos',
        'ordem': 12,
    },
    {
        'nome': 'Outras Despesas Fixas',
        'tipo': GrupoDespesa.TIPO_FIXA,
        'descricao': 'Outras despesas fixas não categorizadas',
        'ordem': 99,
    },
]

def criar_grupos_despesas_fixas():
    """Cria grupos de despesas fixas para pecuária"""
    # Buscar propriedade (Marcelo Sanguino / Fazenda Canta Galo)
    propriedade = Propriedade.objects.filter(
        nome_propriedade__icontains='Canta Galo'
    ).first()
    
    if not propriedade:
        print("❌ ERRO: Propriedade 'Fazenda Canta Galo' não encontrada!")
        print("   Verifique se está usando o banco de dados correto.")
        return
    
    print("=" * 60)
    print("CRIAÇÃO DE GRUPOS DE DESPESAS FIXAS - PECUÁRIA")
    print("=" * 60)
    print(f"Propriedade: {propriedade.nome_propriedade}")
    print()
    
    cadastrados = 0
    ja_existiam = 0
    
    for grupo_data in GRUPOS_DESPESAS_FIXAS:
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
    print(f"📊 Total de grupos: {len(GRUPOS_DESPESAS_FIXAS)}")
    print()

if __name__ == '__main__':
    criar_grupos_despesas_fixas()














