"""
Script para listar todas as propriedades e proprietários cadastrados no sistema
Execute: python manage.py shell
>>> exec(open('listar_propriedades_proprietarios.py').read())
Ou execute diretamente: python listar_propriedades_proprietarios.py
"""

import os
import sys
import django

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade, ProdutorRural
from django.db.models import Count

print("=" * 80)
print("LISTA DE PROPRIETÁRIOS E PROPRIEDADES CADASTRADAS NO SISTEMA")
print("=" * 80)
print()

# Buscar todos os proprietários
proprietarios = ProdutorRural.objects.all().order_by('nome')

print(f"TOTAL DE PROPRIETÁRIOS: {proprietarios.count()}")
print("-" * 80)
print()

if proprietarios.exists():
    for idx, proprietario in enumerate(proprietarios, 1):
        print(f"{idx}. PROPRIETÁRIO: {proprietario.nome}")
        print(f"   CPF/CNPJ: {proprietario.cpf_cnpj}")
        if proprietario.documento_identidade:
            print(f"   RG: {proprietario.documento_identidade}")
        if proprietario.data_nascimento:
            print(f"   Data de Nascimento: {proprietario.data_nascimento.strftime('%d/%m/%Y')}")
            if proprietario.idade:
                print(f"   Idade: {proprietario.idade} anos")
        if proprietario.anos_experiencia:
            print(f"   Anos de Experiência: {proprietario.anos_experiencia}")
        if proprietario.telefone:
            print(f"   Telefone: {proprietario.telefone}")
        if proprietario.email:
            print(f"   E-mail: {proprietario.email}")
        if proprietario.endereco:
            print(f"   Endereço: {proprietario.endereco}")
        print(f"   Usuário Responsável: {proprietario.usuario_responsavel.username} ({proprietario.usuario_responsavel.email})")
        print(f"   Data de Cadastro: {proprietario.data_cadastro.strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Buscar propriedades deste proprietário
        propriedades = Propriedade.objects.filter(produtor=proprietario).order_by('nome_propriedade')
        print(f"   PROPRIEDADES ({propriedades.count()}):")
        
        if propriedades.exists():
            for prop_idx, prop in enumerate(propriedades, 1):
                print(f"      {prop_idx}. {prop.nome_propriedade}")
                print(f"         Localização: {prop.municipio} - {prop.uf}")
                print(f"         Área Total: {prop.area_total_ha} ha")
                print(f"         Tipo de Operação: {prop.get_tipo_operacao_display()}")
                print(f"         Tipo de Propriedade: {prop.get_tipo_propriedade_display()}")
                if prop.car:
                    print(f"         CAR: {prop.car}")
                if prop.incra:
                    print(f"         INCRA: {prop.incra}")
                if prop.nirf:
                    print(f"         NIRF: {prop.nirf}")
                if prop.tipo_propriedade == 'PROPRIA' and prop.valor_hectare_proprio:
                    print(f"         Valor por Hectare: R$ {prop.valor_hectare_proprio:,.2f}")
                elif prop.tipo_propriedade == 'ARRENDAMENTO' and prop.valor_mensal_hectare_arrendamento:
                    print(f"         Valor Mensal por Hectare (Arrendamento): R$ {prop.valor_mensal_hectare_arrendamento:,.2f}")
                print(f"         Data de Cadastro: {prop.data_cadastro.strftime('%d/%m/%Y %H:%M:%S')}")
                print()
        else:
            print("      Nenhuma propriedade cadastrada para este proprietário.")
        
        print("-" * 80)
        print()
else:
    print("Nenhum proprietário cadastrado no sistema.")
    print()

# Resumo por propriedades
print("=" * 80)
print("RESUMO GERAL")
print("=" * 80)
print(f"Total de Proprietários: {ProdutorRural.objects.count()}")
print(f"Total de Propriedades: {Propriedade.objects.count()}")

# Estatísticas por tipo de propriedade
propriedades_proprias = Propriedade.objects.filter(tipo_propriedade='PROPRIA').count()
propriedades_arrendamento = Propriedade.objects.filter(tipo_propriedade='ARRENDAMENTO').count()
print(f"  - Propriedades Próprias: {propriedades_proprias}")
print(f"  - Propriedades Arrendadas: {propriedades_arrendamento}")

# Estatísticas por UF
print("\nPropriedades por Estado (UF):")
propriedades_por_uf = Propriedade.objects.values('uf').annotate(total=Count('id')).order_by('-total')
for item in propriedades_por_uf:
    print(f"  - {item['uf']}: {item['total']} propriedade(s)")

# Proprietários com mais propriedades
print("\nProprietários com mais propriedades:")
proprietarios_com_mais_propriedades = ProdutorRural.objects.annotate(
    num_propriedades=Count('propriedade')
).order_by('-num_propriedades')[:5]

for prop in proprietarios_com_mais_propriedades:
    print(f"  - {prop.nome}: {prop.num_propriedades} propriedade(s)")

print()
print("=" * 80)

