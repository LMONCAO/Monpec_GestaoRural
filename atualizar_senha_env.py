#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script temporario para atualizar senha no .env"""
import os

env_file = '.env'
if os.path.exists(env_file):
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir a senha
    content = content.replace('DB_PASSWORD=postgres', 'DB_PASSWORD=L6171r12@@jjms')
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('Senha atualizada no arquivo .env')
else:
    print(f'Arquivo {env_file} nao encontrado')

