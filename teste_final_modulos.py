#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client
from gestao_rural.models import Propriedade

def testar_modulos():
    print("TESTANDO TODOS OS MODULOS DA DEMONSTRACAO")
    print("="*60)

    propriedade = Propriedade.objects.filter(nome_propriedade='Fazenda Demonstracao').first()

    if propriedade:
        print(f'Propriedade: {propriedade.nome_propriedade} (ID: {propriedade.id})')
        print()

        client = Client()
        usuario = propriedade.produtor.usuario_responsavel
        client.force_login(usuario)

        modulos = [
            ('pecuaria/dashboard/', 'Pecuária'),
            ('financeiro/', 'Financeiro'),
            ('compras/', 'Compras'),
            ('vendas/', 'Vendas'),
            ('nutricao/', 'Nutrição'),
            ('/projetos-bancarios/propriedade/' + str(propriedade.id) + '/', 'Projetos Bancários'),
        ]

        resultados = []
        for url_suffix, nome in modulos:
            # Projetos bancários usa URL diferente
            if nome == 'Projetos Bancários':
                url = url_suffix
            else:
                url = f'/propriedade/{propriedade.id}/{url_suffix}'

            try:
                response = client.get(url)
                if response.status_code == 200:
                    status = 'OK'
                    emoji = '[OK]'
                else:
                    status = f'ERRO {response.status_code}'
                    emoji = '[ERRO]'
                resultados.append(f'{nome}: {emoji} {status}')
                print(f'{nome}: {emoji} {status}')
            except Exception as e:
                resultados.append(f'{nome}: [ERRO] - {str(e)[:30]}...')
                print(f'{nome}: [ERRO] - {str(e)[:30]}...')

        print()
        print("="*60)
        print("RESUMO FINAL:")
        for resultado in resultados:
            print(f'  {resultado}')

        # Contar sucessos
        sucessos = sum(1 for r in resultados if '[OK]' in r)
        total = len(resultados)

        print()
        if sucessos == total:
            print("SISTEMA DEMONSTRACAO 100% FUNCIONAL!")
            print("Todos os modulos estao funcionando corretamente.")
        else:
            print(f"{sucessos}/{total} modulos funcionando.")
            print("Alguns modulos ainda tem problemas.")

    else:
        print('Propriedade Demonstracao nao encontrada')

if __name__ == '__main__':
    testar_modulos()
