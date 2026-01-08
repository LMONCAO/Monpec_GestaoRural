#!/usr/bin/env python
import os
import shutil

# Diretório de origem (com acentos)
source_dir = r'C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural'

# Diretório de destino (sem acentos)
dest_dir = r'C:\monpec_project'

# Arquivos e pastas essenciais para copiar
essential_items = [
    'manage.py',
    'sistema_rural',
    'requirements.txt',
]

print(f"Copiando de: {source_dir}")
print(f"Para: {dest_dir}")

for item in essential_items:
    source_path = os.path.join(source_dir, item)
    dest_path = os.path.join(dest_dir, item)

    if os.path.exists(source_path):
        print(f"Copiando: {item}")
        if os.path.isdir(source_path):
            shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source_path, dest_path)
    else:
        print(f"Não encontrado: {item}")

print("Cópia concluída!")