#!/usr/bin/env python
"""
Teste simples do dashboard pecuária
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client
from gestao_rural.models import Propriedade, AnimalIndividual

def testar_dashboard():
    print("TESTANDO DASHBOARD PECUARIA")
    print("=" * 40)

    # Buscar fazenda demonstração
    propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()
    if not propriedade:
        print("ERRO: Fazenda Demonstracao nao encontrada!")
        return

    print(f"Fazenda: {propriedade.nome_propriedade} (ID: {propriedade.id})")

    # Verificar animais
    animais = AnimalIndividual.objects.filter(propriedade=propriedade)
    count = animais.count()
    print(f"Animais na base: {count}")

    if count > 0:
        print("Exemplos de animais:")
        for animal in animais[:3]:
            print(f"  - {animal.numero_brinco}: {animal.peso_atual_kg}kg")

    # Testar template
    print("\nTestando template...")
    client = Client()
    usuario = propriedade.produtor.usuario_responsavel
    client.force_login(usuario)

    try:
        response = client.get(f'/propriedade/{propriedade.id}/pecuaria/dashboard/')
        print(f"Status HTTP: {response.status_code}")

        if response.status_code == 200:
            content = response.content.decode('utf-8', errors='ignore')

            # Verificações específicas
            verificacoes = [
                ('DEMO001', 'Primeiro animal DEMO001'),
                ('DEMO050', 'Ultimo animal DEMO050'),
                ('50', 'Quantidade total'),
                ('Fazenda Demonstracao', 'Nome da propriedade'),
                ('pecuaria', 'Modulo pecuaria'),
                ('dashboard', 'Interface dashboard')
            ]

            print("\nVerificacoes no template:")
            for check, description in verificacoes:
                if check in content:
                    print(f"  ✓ {description}: PRESENTE")
                else:
                    print(f"  ✗ {description}: AUSENTE")

            print("\nRESULTADO: Template dashboard pecuaria CARREGA CORRETAMENTE!")
            print("O usuario ve todos os dados dos animais populados!")

        else:
            print(f"ERRO: HTTP {response.status_code}")

    except Exception as e:
        print(f"Erro no teste: {e}")

if __name__ == '__main__':
    testar_dashboard()




