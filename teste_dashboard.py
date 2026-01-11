#!/usr/bin/env python
import requests

try:
    response = requests.get('http://localhost:8000/propriedade/5/pecuaria/planejamento/')
    if 'Total de animais' in response.text:
        print('Cards preenchidos - Total de animais encontrado')
    else:
        print('Cards nao preenchidos - Total de animais nao encontrado')

    if '1300' in response.text:
        print('Valor 1300 encontrado')
    else:
        print('Valor 1300 nao encontrado')

except Exception as e:
    print(f'Erro ao testar: {e}')