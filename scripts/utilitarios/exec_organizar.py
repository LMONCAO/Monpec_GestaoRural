#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
from pathlib import Path

ROOT = Path(r"C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural")

print("=" * 60)
print("ORGANIZAÇÃO DO PROJETO")
print("=" * 60)
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
    "entrypoint.sh", "EXECUTAR_ORGANIZACAO.ps1", "_organizar_agora.py",
    "organizar_projeto_completo.py", "organizar_projeto.ps1", "organizar_agora.py",
    "exec_organizar.py"
}

stats = {"md": 0, "sh": 0, "ps1": 0, "bat": 0, "py": 0, "txt": 0}

def categorize(name):
    n = name.lower()
    if any(k in n for k in ["deploy", "atualizar", "aplicar_migracoes", "cloud", "gcp"]):
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

# Mover arquivos
print("\n1. Movendo arquivos .md...")
for item in ROOT.iterdir():
    if item.is_file() and item.suffix == ".md" and item.name not in keep_in_root:
        dest = folders["docs"] / item.name
        counter = 1
        while dest.exists():
            dest = folders["docs"] / f"{item.stem}_{counter}{item.suffix}"
            counter += 1
        try:
            shutil.move(str(item), str(dest))
            print(f"  ✓ {item.name} -> docs/")
            stats["md"] += 1
        except Exception as e:
            print(f"  ✗ Erro ao mover {item.name}: {e}")

print("\n2. Movendo scripts...")
for ext in [".sh", ".ps1", ".bat"]:
    for item in ROOT.iterdir():
        if item.is_file() and item.suffix == ext and item.name not in keep_in_root:
            dest_dir = categorize(item.name)
            dest = dest_dir / item.name
            counter = 1
            while dest.exists():
                dest = dest_dir / f"{item.stem}_{counter}{item.suffix}"
                counter += 1
            try:
                shutil.move(str(item), str(dest))
                print(f"  ✓ {item.name} -> {dest_dir.relative_to(ROOT)}/")
                stats[ext[1:]] += 1
            except Exception as e:
                print(f"  ✗ Erro ao mover {item.name}: {e}")

print("\n3. Movendo scripts Python utilitários...")
django_dirs = {"gestao_rural", "sistema_rural", "api", "templates", "static"}
for item in ROOT.iterdir():
    if item.is_file() and item.suffix == ".py" and item.name not in keep_in_root:
        parts = item.parts
        is_django = any(d in parts for d in django_dirs)
        if not is_django:
            dest = folders["scripts/utilitarios"] / item.name
            counter = 1
            while dest.exists():
                dest = folders["scripts/utilitarios"] / f"{item.stem}_{counter}{item.suffix}"
                counter += 1
            try:
                shutil.move(str(item), str(dest))
                print(f"  ✓ {item.name} -> scripts/utilitarios/")
                stats["py"] += 1
            except Exception as e:
                print(f"  ✗ Erro ao mover {item.name}: {e}")

print("\n4. Movendo arquivos .txt de comandos...")
keywords = ["comando", "COMANDO", "deploy", "DEPLOY", "instrucoes", "INSTRUCOES"]
for item in ROOT.iterdir():
    if item.is_file() and item.suffix == ".txt":
        if any(k in item.name for k in keywords):
            dest = folders["deploy"] / item.name
            counter = 1
            while dest.exists():
                dest = folders["deploy"] / f"{item.stem}_{counter}{item.suffix}"
                counter += 1
            try:
                shutil.move(str(item), str(dest))
                print(f"  ✓ {item.name} -> deploy/")
                stats["txt"] += 1
            except Exception as e:
                print(f"  ✗ Erro ao mover {item.name}: {e}")

print("\n" + "=" * 60)
print("RESUMO")
print("=" * 60)
total = 0
for key, count in stats.items():
    if count > 0:
        print(f"  {key.upper()}: {count} arquivo(s)")
        total += count
print(f"  TOTAL: {total} arquivo(s) movidos")
print("=" * 60)
print("\n✅ Organização concluída!")

