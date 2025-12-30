#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script final para organizar arquivos do projeto
Execute este arquivo diretamente no diretório raiz
"""
import os
import shutil
from pathlib import Path

# Detectar diretório raiz automaticamente
ROOT = Path(__file__).parent.absolute()

print("=" * 70)
print("ORGANIZAÇÃO DO PROJETO - MOVENDO ARQUIVOS")
print("=" * 70)
print(f"Diretório: {ROOT}")

# Criar pastas
folders = {
    "docs": ROOT / "docs",
    "scripts/deploy": ROOT / "scripts" / "deploy",
    "scripts/admin": ROOT / "scripts" / "admin",
    "scripts/correcoes": ROOT / "scripts" / "correcoes",
    "scripts/utilitarios": ROOT / "scripts" / "utilitarios",
    "scripts/configuracao": ROOT / "scripts" / "configuracao",
    "scripts/backup": ROOT / "scripts" / "backup",
    "deploy": ROOT / "deploy",
    "temp": ROOT / "temp",
}

for folder in folders.values():
    folder.mkdir(parents=True, exist_ok=True)

keep_in_root = {
    "manage.py", "requirements.txt", "Dockerfile", "Dockerfile.prod",
    ".gitignore", "app.yaml", "build-config.yaml", "cloudbuild-config.yaml",
    "entrypoint.sh", "ORGANIZAR_AGORA_FINAL.py"
}

stats = {"md": 0, "sh": 0, "ps1": 0, "bat": 0, "py": 0, "txt": 0}

def categorize(name):
    n = name.lower()
    if any(k in n for k in ["deploy", "atualizar", "aplicar_migracoes", "cloud", "gcp", "google"]):
        return folders["scripts/deploy"]
    elif any(k in n for k in ["admin", "criar_admin", "superuser"]):
        return folders["scripts/admin"]
    elif any(k in n for k in ["corrigir", "correcao", "fix", "solucao"]):
        return folders["scripts/correcoes"]
    elif any(k in n for k in ["configurar", "config", "setup"]):
        return folders["scripts/configuracao"]
    elif any(k in n for k in ["backup", "exportar", "importar"]):
        return folders["scripts/backup"]
    return folders["scripts/deploy"]

# Usar múltiplas estratégias para encontrar arquivos
print("\n🔍 Buscando arquivos...")

# Estratégia 1: glob
md_glob = list(ROOT.glob("*.md"))
sh_glob = list(ROOT.glob("*.sh"))
ps1_glob = list(ROOT.glob("*.ps1"))
bat_glob = list(ROOT.glob("*.bat"))
py_glob = list(ROOT.glob("*.py"))
txt_glob = list(ROOT.glob("*.txt"))

# Estratégia 2: os.listdir
try:
    items = os.listdir(str(ROOT))
    md_listdir = [ROOT / f for f in items if f.endswith('.md') and (ROOT / f).is_file()]
    sh_listdir = [ROOT / f for f in items if f.endswith('.sh') and (ROOT / f).is_file()]
    ps1_listdir = [ROOT / f for f in items if f.endswith('.ps1') and (ROOT / f).is_file()]
    bat_listdir = [ROOT / f for f in items if f.endswith('.bat') and (ROOT / f).is_file()]
    py_listdir = [ROOT / f for f in items if f.endswith('.py') and (ROOT / f).is_file()]
    txt_listdir = [ROOT / f for f in items if f.endswith('.txt') and (ROOT / f).is_file()]
except:
    md_listdir = sh_listdir = ps1_listdir = bat_listdir = py_listdir = txt_listdir = []

# Combinar resultados
md_files = list(set(md_glob + md_listdir))
sh_files = list(set(sh_glob + sh_listdir))
ps1_files = list(set(ps1_glob + ps1_listdir))
bat_files = list(set(bat_glob + bat_listdir))
py_files = list(set(py_glob + py_listdir))
txt_files = list(set(txt_glob + txt_listdir))

print(f"  Encontrados: {len(md_files)} .md, {len(sh_files)} .sh, {len(ps1_files)} .ps1, {len(bat_files)} .bat, {len(py_files)} .py, {len(txt_files)} .txt")

# 1. Mover .md
print("\n1️⃣  Movendo arquivos .md para docs/...")
for f in md_files:
    if f.name not in keep_in_root:
        try:
            dest = folders["docs"] / f.name
            counter = 1
            while dest.exists():
                dest = folders["docs"] / f"{f.stem}_{counter}{f.suffix}"
                counter += 1
            shutil.move(str(f), str(dest))
            print(f"  ✓ {f.name}")
            stats["md"] += 1
        except Exception as e:
            print(f"  ✗ {f.name}: {e}")

# 2. Mover scripts
print("\n2️⃣  Movendo scripts para scripts/...")
for ext, files in [(".sh", sh_files), (".ps1", ps1_files), (".bat", bat_files)]:
    for f in files:
        if f.name not in keep_in_root:
            try:
                dest_dir = categorize(f.name)
                dest = dest_dir / f.name
                counter = 1
                while dest.exists():
                    dest = dest_dir / f"{f.stem}_{counter}{f.suffix}"
                    counter += 1
                shutil.move(str(f), str(dest))
                print(f"  ✓ {f.name} -> {dest_dir.relative_to(ROOT)}")
                stats[ext[1:]] += 1
            except Exception as e:
                print(f"  ✗ {f.name}: {e}")

# 3. Mover Python
print("\n3️⃣  Movendo scripts Python para scripts/utilitarios/...")
django_dirs = {"gestao_rural", "sistema_rural", "api", "templates", "static"}
for f in py_files:
    if f.name not in keep_in_root:
        parts = f.parts
        is_django = any(d in parts for d in django_dirs)
        if not is_django:
            try:
                dest = folders["scripts/utilitarios"] / f.name
                counter = 1
                while dest.exists():
                    dest = folders["scripts/utilitarios"] / f"{f.stem}_{counter}{f.suffix}"
                    counter += 1
                shutil.move(str(f), str(dest))
                print(f"  ✓ {f.name}")
                stats["py"] += 1
            except Exception as e:
                print(f"  ✗ {f.name}: {e}")

# 4. Mover .txt
print("\n4️⃣  Movendo arquivos .txt para deploy/...")
keywords = ["comando", "COMANDO", "deploy", "DEPLOY", "instrucoes", "INSTRUCOES"]
for f in txt_files:
    if any(k in f.name for k in keywords):
        try:
            dest = folders["deploy"] / f.name
            counter = 1
            while dest.exists():
                dest = folders["deploy"] / f"{f.stem}_{counter}{f.suffix}"
                counter += 1
            shutil.move(str(f), str(dest))
            print(f"  ✓ {f.name}")
            stats["txt"] += 1
        except Exception as e:
            print(f"  ✗ {f.name}: {e}")

# Resumo
print("\n" + "=" * 70)
print("📊 RESUMO")
print("=" * 70)
total = 0
for key, count in stats.items():
    if count > 0:
        print(f"  {key.upper()}: {count} arquivo(s)")
        total += count
print(f"\n  ✅ TOTAL: {total} arquivo(s) movidos com sucesso!")
print("=" * 70)
print("\n🎉 Organização concluída!")

