#!/usr/bin/env python3
"""
Script para transferir todos os templates corrigidos para o servidor
Execute: python transferir_tudo.py
"""
import subprocess
import time

KEY = r"C:\Users\lmonc\Downloads\monpecprojetista.key"
SERVER = "root@191.252.225.106"
BASE_DEST = "/var/www/monpec.com.br/templates/gestao_rural"

arquivos = [
    (r"C:\Monpec_projetista\templates\patrimonio_dashboard.html", f"{BASE_DEST}/patrimonio_dashboard.html"),
    (r"C:\Monpec_projetista\templates\financeiro_dashboard_clean.html", f"{BASE_DEST}/financeiro_dashboard.html"),
    (r"C:\Monpec_projetista\templates\projetos_dashboard_clean.html", f"{BASE_DEST}/projetos_dashboard.html"),
    (r"C:\Monpec_projetista\templates\propriedade_modulos.html", f"{BASE_DEST}/propriedade_modulos.html"),
]

print("="*70)
print("  TRANSFERINDO TEMPLATES CORRIGIDOS PARA O SERVIDOR")
print("="*70)
print()

for i, (origem, destino) in enumerate(arquivos, 1):
    print(f"[{i}/{len(arquivos)}] Transferindo {origem.split('\\')[-1]}...")
    cmd = f'scp -i "{KEY}" "{origem}" {SERVER}:{destino}'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"  ✅ OK")
        else:
            print(f"  ❌ ERRO: {result.stderr}")
    except Exception as e:
        print(f"  ❌ ERRO: {e}")
    time.sleep(1)

print()
print("="*70)
print("  TODOS OS ARQUIVOS TRANSFERIDOS!")
print("="*70)
print()
print("Agora execute no CONSOLE WEB:")
print()
print("pkill -9 python")
print("sleep 2")
print("cd /var/www/monpec.com.br")
print("source venv/bin/activate")
print("python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &")
print()

