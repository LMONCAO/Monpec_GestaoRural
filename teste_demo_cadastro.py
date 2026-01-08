#!/usr/bin/env python
"""
Script para verificar se a Fazenda Demonstração está configurada
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import Propriedade
from gestao_rural.models import AnimalIndividual
from gestao_rural.models_funcionarios import Funcionario
from gestao_rural.models_controles_operacionais import Pastagem, Cocho
from gestao_rural.models_operacional import Equipamento
from gestao_rural.models_compras_financeiro import Fornecedor

def testar_propriedade_demo():
    print("="*60)
    print("VERIFICANDO FAZENDA DEMONSTRACAO")
    print("="*60)

    # Verificar se existe a propriedade
    propriedades = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao')
    if propriedades.exists():
        prop = propriedades.first()
        print(f"Propriedade encontrada: {prop.nome_propriedade}")
        print(f"Produtor: {prop.produtor.nome}")
        print(f"Municipio: {prop.municipio}/{prop.uf}")
        print(f"Area: {prop.area_total_ha} ha")

        # Verificar dados populados
        animais = AnimalIndividual.objects.filter(propriedade=prop).count()
        funcionarios = Funcionario.objects.filter(propriedade=prop).count()
        pastagens = Pastagem.objects.filter(propriedade=prop).count()
        cochos = Cocho.objects.filter(propriedade=prop).count()
        equipamentos = Equipamento.objects.filter(propriedade=prop).count()
        fornecedores = Fornecedor.objects.filter(propriedade=prop).count()

        print("\nDados populados:")
        print(f"  - Animais: {animais}")
        print(f"  - Funcionarios: {funcionarios}")
        print(f"  - Pastagens: {pastagens}")
        print(f"  - Cochos: {cochos}")
        print(f"  - Equipamentos: {equipamentos}")
        print(f"  - Fornecedores: {fornecedores}")

        total_itens = animais + funcionarios + pastagens + cochos + equipamentos + fornecedores
        print(f"\nTOTAL DE ITENS: {total_itens}")

        if total_itens > 10:
            print("\nFAZENDA DEMONSTRACAO TOTALMENTE CONFIGURADA!")
            print("Sistema pronto para demonstracoes!")
        else:
            print("\nAlguns dados podem nao ter sido populados completamente")
            print("Execute os scripts individuais se necessario")

    else:
        print("PROPRIEDADE 'Fazenda Demonstracao' NAO ENCONTRADA!")
        print("Execute primeiro: python popular_fazenda_demonstracao.py")

if __name__ == '__main__':
    testar_propriedade_demo()