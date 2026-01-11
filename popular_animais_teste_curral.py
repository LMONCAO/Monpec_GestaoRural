#!/usr/bin/env python3
"""
Script para popular banco de dados com animais de teste para o Curral V4.
Gera 50 animais com dados realistas de SISBOV, categorias, idades e sexos variados.
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth import get_user_model

from gestao_rural.models import (
    Propriedade, AnimalIndividual, CategoriaAnimal,
    BrincoAnimal, AnimalPesagem, MovimentacaoIndividual
)

User = get_user_model()

def gerar_sisbov_15_digitos(propriedade_codigo="55003", sequencial_inicial=1000):
    """
    Gera código SISBOV de 15 dígitos no formato brasileiro.

    Formato: UF(2) + Municipio(4) + Propriedade(5) + Animal(4) = 15 dígitos

    Exemplo: 10 5500 37619 7505
             |  |    |    |
             |  |    |    └── Animal (4 dígitos)
             |  |    └─────── Propriedade (5 dígitos)
             |  └──────────── Municipio (4 dígitos)
             └─────────────── UF (2 dígitos)
    """
    # UF São Paulo = 10 (exemplo)
    uf = "10"

    # Municipio fictício
    municipio = "5500"

    # Propriedade (código da propriedade)
    propriedade = propriedade_codigo.zfill(5)  # 5 dígitos

    # Animal sequencial (4 dígitos)
    animal = str(sequencial_inicial).zfill(4)

    return f"{uf}{municipio}{propriedade}{animal}"

def extrair_numero_manejo(sisbov):
    """
    CORREÇÃO: Extrai o número de manejo das posições 9-14 do SISBOV (6 dígitos).
    Exclui o dígito verificador (posição 15).
    Exemplo: 1055005500367242 -> 036724
    """
    if len(sisbov) >= 15:
        return sisbov[9:15]  # Posições 9-14 (6 dígitos)
    return None

def gerar_nome_animal(sexo, numero_brinco):
    """Gera nome fictício para o animal baseado no sexo e número."""
    nomes_macho = [
        "BARÃO", "TOURO", "GARANHÃO", "BRASIL", "CAMPIONE", "DUQUE", "FIDEL", "GARÇOM",
        "HERCULES", "ÍCARO", "JÚPITER", "KÁiser", "LEÃO", "MÁRIO", "NÉSTOR", "ÓSCAR"
    ]

    nomes_femea = [
        "BELA", "CORINA", "DAMA", "ESTRELA", "FADA", "GRAÇA", "HELENA", "ÍRIS",
        "JASMIM", "KIARA", "LUNA", "MÁGICA", "NÉVOA", "ÓPERA", "PÉROLA", "QUITERIA"
    ]

    if sexo == 'MACHO':
        nome_base = random.choice(nomes_macho)
    else:
        nome_base = random.choice(nomes_femea)

    return f"{nome_base} {numero_brinco}"

def calcular_idade(data_nascimento):
    """Calcula idade aproximada em meses."""
    hoje = date.today()
    diferenca = (hoje.year - data_nascimento.year) * 12 + (hoje.month - data_nascimento.month)
    return max(1, diferenca)  # Mínimo 1 mês

def gerar_data_nascimento(categoria, idade_meses=None):
    """Gera data de nascimento baseada na categoria e idade."""
    hoje = date.today()

    # Idades típicas por categoria (em meses)
    idades_por_categoria = {
        'BEZERRO': (1, 6),      # 1-6 meses
        'DESMAMADO': (7, 12),   # 7-12 meses
        'NOVILHO': (13, 24),    # 13-24 meses
        'BOI_GORDO': (25, 48),  # 25-48 meses
        'VACA': (30, 120),      # 30-120 meses
        'TOURO': (36, 144),     # 36-144 meses
    }

    if categoria in idades_por_categoria:
        min_meses, max_meses = idades_por_categoria[categoria]
        if idade_meses:
            meses = idade_meses
        else:
            meses = random.randint(min_meses, max_meses)
    else:
        meses = random.randint(12, 60)  # Padrão

    return hoje - timedelta(days=meses*30)  # Aproximadamente

def obter_ou_criar_categoria(nome_categoria):
    """Obtém ou cria categoria de animal."""
    categoria, created = CategoriaAnimal.objects.get_or_create(
        nome=nome_categoria,
        defaults={
            'descricao': f'Categoria {nome_categoria}',
            'ativo': True
        }
    )
    return categoria

def criar_animal_teste(propriedade, numero_sequencial, hoje):
    """Cria um animal de teste com dados realistas."""

    # Definir sexo e categoria baseada no sequencial
    if numero_sequencial % 5 == 0:  # A cada 5 animais, um macho
        sexo = 'MACHO'
        categorias = ['TOURO', 'NOVILHO', 'BOI_GORDO']
        categoria_nome = random.choice(categorias)
    else:
        sexo = 'FEMEA'
        categorias = ['BEZERRO', 'DESMAMADO', 'NOVILHA', 'VACA']
        categoria_nome = random.choice(categorias)

    # Gerar SISBOV único
    sisbov = gerar_sisbov_15_digitos(sequencial_inicial=numero_sequencial + 1000 + random.randint(10000, 99999))
    numero_manejo = extrair_numero_manejo(sisbov)

    # Gerar códigos adicionais completamente únicos
    import time
    import uuid
    unique_id = str(uuid.uuid4())[:8].upper()  # 8 caracteres únicos
    numero_brinco = f"BR-TEST-{numero_sequencial}-{unique_id}"
    codigo_eletronico = f"982{random.randint(100000000, 999999999)}{numero_sequencial}"

    # Data de nascimento baseada na categoria
    data_nascimento = gerar_data_nascimento(categoria_nome)
    idade_meses = calcular_idade(data_nascimento)

    # Obter categoria
    categoria = obter_ou_criar_categoria(categoria_nome)

    # Nome do animal
    nome_animal = gerar_nome_animal(sexo, numero_manejo)

    # Raça (predominante Nelore no Brasil)
    racas = ['NELORE', 'ANGUS', 'BRANGUS', 'TABAPUA', 'SENEPOL']
    raca = random.choices(racas, weights=[70, 10, 10, 5, 5])[0]

    # Status sanitário e reprodutivo
    status_sanitario = random.choice(['APTO', 'APTO', 'APTO', 'QUARENTENA'])  # Maioria apto

    if sexo == 'MACHO':
        status_reprodutivo = 'INDEFINIDO'
    else:
        status_reprodutivos = ['VAZIA', 'PRENHE', 'LACTACAO', 'SECAGEM']
        status_reprodutivo = random.choice(status_reprodutivos)

    # Tipo de brinco
    tipo_brinco = random.choice(['VISUAL', 'ELETRONICO', 'BOTTON'])

    # Dados BND simulados (80% dos animais terão registro BND)
    tem_registro_bnd = random.random() < 0.8
    status_bnd = 'CONFORME' if tem_registro_bnd else None
    data_cadastro_bnd = data_nascimento + timedelta(days=random.randint(30, 90)) if tem_registro_bnd else None
    numero_registro_bnd = f"BND{random.randint(100000, 999999)}" if tem_registro_bnd else None

    # Criar animal
    animal = AnimalIndividual.objects.create(
        numero_brinco=numero_brinco,
        codigo_sisbov=sisbov,
        numero_manejo=numero_manejo,
        codigo_eletronico=codigo_eletronico,
        tipo_brinco=tipo_brinco,
        propriedade=propriedade,
        categoria=categoria,
        sexo=sexo,
        raca=raca,
        data_nascimento=data_nascimento,
        status='ATIVO',
        status_sanitario=status_sanitario,
        status_reprodutivo=status_reprodutivo,
        status_bnd=status_bnd,
        data_cadastro_bnd=data_cadastro_bnd,
        numero_registro_bnd=numero_registro_bnd,
        tipo_origem='NASCIMENTO'
    )

    # Criar pesagem atual apenas (simplificado para teste)
    # Calcular peso baseado na categoria
    pesos_por_categoria = {
        'BEZERRO': random.randint(80, 150),
        'DESMAMADO': random.randint(150, 250),
        'NOVILHO': random.randint(250, 450),
        'NOVILHA': random.randint(250, 450),
        'BOI_GORDO': random.randint(450, 650),
        'VACA': random.randint(450, 650),
        'TOURO': random.randint(700, 1000),
    }

    peso_atual = pesos_por_categoria.get(categoria_nome, random.randint(400, 600))

    AnimalPesagem.objects.create(
        animal=animal,
        peso_kg=peso_atual,
        data_pesagem=hoje,
        responsavel=None
    )

    return animal


def main():
    """Função principal para executar o script."""
    print("🐄 INICIANDO POPULAÇÃO DE ANIMAIS DE TESTE - CURRAL V4")
    print("=" * 60)

    try:
        # Criar propriedade específica para testes do curral v4
        from gestao_rural.models import ProdutorRural

        # Criar ou obter produtor
        produtor, _ = ProdutorRural.objects.get_or_create(
            nome='Produtor Teste Curral V4',
            defaults={
                'usuario_responsavel': User.objects.filter(is_superuser=True).first() or User.objects.first(),
                'cpf_cnpj': '12345678901',
                'telefone': '11999999999',
            }
        )

        propriedade, created = Propriedade.objects.get_or_create(
            nome_propriedade='Fazenda Teste Curral V4',
            defaults={
                'produtor': produtor,
                'municipio': 'São Paulo',
                'uf': 'SP',
                'area_total_ha': 1000,
            }
        )

        if created:
            print("✅ Propriedade de teste criada!")

        if not propriedade:
            print("❌ ERRO: Nenhuma propriedade encontrada!")
            return

        print(f"📍 Propriedade: {propriedade.nome_propriedade}")
        print(f"🏢 Produtor: {propriedade.produtor}")
        print()

        # Verificar animais existentes
        animais_existentes = AnimalIndividual.objects.filter(propriedade=propriedade).count()
        print(f"📊 Animais existentes: {animais_existentes}")

        # Perguntar se quer continuar
        if animais_existentes > 0:
            resposta = input(f"\n⚠️  Já existem {animais_existentes} animais. Continuar? (s/n): ")
            if resposta.lower() != 's':
                print("❌ Operação cancelada.")
                return

        # Criar 50 animais
        print("\n🚀 CRIANDO 50 ANIMAIS DE TESTE...")
        print("-" * 40)

        hoje = date.today()
        animais_criados = []
        for i in range(50):
            try:
                animal = criar_animal_teste(propriedade, i + 1, hoje)
                animais_criados.append(animal)

                if (i + 1) % 10 == 0:
                    print(f"✅ Criados {i + 1}/50 animais...")

            except Exception as e:
                print(f"❌ Erro ao criar animal {i + 1}: {str(e)}")
                continue

        print(f"\n✅ SUCESSO! Criados {len(animais_criados)} animais de teste.")

        # Estatísticas finais
        print("\n📈 ESTATÍSTICAS DOS ANIMAIS CRIADOS:")
        print("-" * 40)

        # Por sexo
        machos = len([a for a in animais_criados if a.sexo == 'MACHO'])
        femeas = len([a for a in animais_criados if a.sexo == 'FEMEA'])
        print(f"♂️  Machos: {machos}")
        print(f"♀️  Fêmeas: {femeas}")

        # Por categoria
        categorias = {}
        for animal in animais_criados:
            cat = animal.categoria.nome
            categorias[cat] = categorias.get(cat, 0) + 1

        print("\n📂 Por categoria:")
        for categoria, quantidade in sorted(categorias.items()):
            print(f"   {categoria}: {quantidade}")

        # Exemplos de códigos
        print("\n🔢 EXEMPLOS DE CÓDIGOS GERADOS:")
        print("-" * 40)
        for i, animal in enumerate(animais_criados[:5]):
            print(f"Animal {i+1}:")
            print(f"   SISBOV: {animal.codigo_sisbov}")
            print(f"   Manejo: {animal.numero_manejo}")
            print(f"   Brinco: {animal.numero_brinco}")
            print(f"   RFID: {animal.codigo_eletronico}")
            print()

        print("🎯 PRONTO! Agora você pode testar o Curral V4!")
        print("💡 Use qualquer um dos códigos acima para identificar animais.")

    except Exception as e:
        print(f"❌ ERRO GERAL: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()