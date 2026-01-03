#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
from pathlib import Path

# Usar o diretório do script como raiz
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
    print(f"✓ {folder.relative_to(ROOT)}")

# Arquivos que devem permanecer na raiz
keep_in_root = {
    "manage.py", "requirements.txt", "Dockerfile", "Dockerfile.prod",
    ".gitignore", "app.yaml", "build-config.yaml", "cloudbuild-config.yaml",
    "entrypoint.sh", "mover_arquivos_agora.py"
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

# Usar os.listdir que funciona melhor
root_str = str(ROOT)
all_items = os.listdir(root_str)

print(f"\n📁 Total de itens encontrados na raiz: {len(all_items)}")

# 1. Mover arquivos .md
print("\n1️⃣  Movendo arquivos .md para docs/...")
for name in all_items:
    item_path = ROOT / name
    if item_path.is_file() and name.endswith(".md") and name not in keep_in_root:
        dest = folders["docs"] / name
        counter = 1
        while dest.exists():
            dest = folders["docs"] / f"{item_path.stem}_{counter}{item_path.suffix}"
            counter += 1
        try:
            shutil.move(str(item_path), str(dest))
            print(f"  ✓ {name} -> docs/")
            stats["md"] += 1
        except Exception as e:
            print(f"  ✗ Erro ao mover {name}: {e}")

# 2. Mover scripts .sh, .ps1, .bat
print("\n2️⃣  Movendo scripts (.sh, .ps1, .bat) para scripts/...")
for ext in [".sh", ".ps1", ".bat"]:
    for name in all_items:
        item_path = ROOT / name
        if item_path.is_file() and name.endswith(ext) and name not in keep_in_root:
            dest_dir = categorize(name)
            dest = dest_dir / name
            counter = 1
            while dest.exists():
                dest = dest_dir / f"{item_path.stem}_{counter}{item_path.suffix}"
                counter += 1
            try:
                shutil.move(str(item_path), str(dest))
                print(f"  ✓ {name} -> {dest_dir.relative_to(ROOT)}/")
                stats[ext[1:]] += 1
            except Exception as e:
                print(f"  ✗ Erro ao mover {name}: {e}")

# 3. Mover scripts Python utilitários
print("\n3️⃣  Movendo scripts Python utilitários para scripts/utilitarios/...")
django_dirs = {"gestao_rural", "sistema_rural", "api", "templates", "static"}
for name in all_items:
    item_path = ROOT / name
    if item_path.is_file() and name.endswith(".py") and name not in keep_in_root:
        # Verificar se não está em subdiretório Django
        path_str = str(item_path)
        is_django = any(f"/{d}/" in path_str or f"\\{d}\\" in path_str for d in django_dirs)
        if not is_django:
            dest = folders["scripts/utilitarios"] / name
            counter = 1
            while dest.exists():
                dest = folders["scripts/utilitarios"] / f"{item_path.stem}_{counter}{item_path.suffix}"
                counter += 1
            try:
                shutil.move(str(item_path), str(dest))
                print(f"  ✓ {name} -> scripts/utilitarios/")
                stats["py"] += 1
            except Exception as e:
                print(f"  ✗ Erro ao mover {name}: {e}")

# 4. Mover arquivos .txt de comandos
print("\n4️⃣  Movendo arquivos .txt de comandos para deploy/...")
keywords = ["comando", "COMANDO", "deploy", "DEPLOY", "instrucoes", "INSTRUCOES"]
for name in all_items:
    item_path = ROOT / name
    if item_path.is_file() and name.endswith(".txt"):
        if any(k in name for k in keywords):
            dest = folders["deploy"] / name
            counter = 1
            while dest.exists():
                dest = folders["deploy"] / f"{item_path.stem}_{counter}{item_path.suffix}"
                counter += 1
            try:
                shutil.move(str(item_path), str(dest))
                print(f"  ✓ {name} -> deploy/")
                stats["txt"] += 1
            except Exception as e:
                print(f"  ✗ Erro ao mover {name}: {e}")

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
print("📖 Consulte docs/ORGANIZACAO_PROJETO.md para mais informações.")

