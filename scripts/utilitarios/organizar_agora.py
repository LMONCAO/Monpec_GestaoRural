#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script para organizar arquivos - Execute este arquivo"""
import os
import shutil
from pathlib import Path

# Encontrar diretório raiz
script_dir = Path(__file__).parent.absolute()
ROOT = script_dir

print("=" * 60)
print("ORGANIZAÇÃO DO PROJETO")
print("=" * 60)
print(f"Diretório: {ROOT}")

# Verificar se é o diretório correto
if not (ROOT / "manage.py").exists() and not (ROOT / "sistema_rural").exists():
    print("AVISO: Não encontrado manage.py ou sistema_rural. Continuando...")

# Criar estrutura
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

keep_in_root = {
    "manage.py", "requirements.txt", "Dockerfile", "Dockerfile.prod",
    ".gitignore", "app.yaml", "build-config.yaml", "cloudbuild-config.yaml",
    "entrypoint.sh", "EXECUTAR_ORGANIZACAO.ps1", "_organizar_agora.py",
    "organizar_projeto_completo.py", "organizar_projeto.ps1", "organizar_agora.py"
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

print("\n1. Movendo arquivos .md...")
for f in ROOT.glob("*.md"):
    if f.name not in keep_in_root:
        dest = folders["docs"] / f.name
        counter = 1
        while dest.exists():
            dest = folders["docs"] / f"{f.stem}_{counter}{f.suffix}"
            counter += 1
        shutil.move(str(f), str(dest))
        print(f"  ✓ {f.name} -> docs/")
        stats["md"] += 1

print("\n2. Movendo scripts...")
for ext in [".sh", ".ps1", ".bat"]:
    for f in ROOT.glob(f"*{ext}"):
        if f.name not in keep_in_root:
            dest_dir = categorize(f.name)
            dest = dest_dir / f.name
            counter = 1
            while dest.exists():
                dest = dest_dir / f"{f.stem}_{counter}{f.suffix}"
                counter += 1
            shutil.move(str(f), str(dest))
            print(f"  ✓ {f.name} -> {dest_dir.relative_to(ROOT)}/")
            stats[ext[1:]] += 1

print("\n3. Movendo scripts Python utilitários...")
django_dirs = {"gestao_rural", "sistema_rural", "api", "templates", "static"}
for f in ROOT.glob("*.py"):
    if f.name not in keep_in_root:
        parts = f.parts
        rel_to_root = f.relative_to(ROOT)
        is_django = any(part in django_dirs for part in parts if part != ROOT.name)
        
        if not is_django and str(rel_to_root.parent) == ".":
            dest = folders["scripts/utilitarios"] / f.name
            counter = 1
            while dest.exists():
                dest = folders["scripts/utilitarios"] / f"{f.stem}_{counter}{f.suffix}"
                counter += 1
            shutil.move(str(f), str(dest))
            print(f"  ✓ {f.name} -> scripts/utilitarios/")
            stats["py"] += 1

print("\n4. Movendo arquivos .txt de comandos...")
keywords = ["comando", "COMANDO", "deploy", "DEPLOY", "instrucoes", "INSTRUCOES"]
for f in ROOT.glob("*.txt"):
    if any(k in f.name for k in keywords):
        dest = folders["deploy"] / f.name
        counter = 1
        while dest.exists():
            dest = folders["deploy"] / f"{f.stem}_{counter}{f.suffix}"
            counter += 1
        shutil.move(str(f), str(dest))
        print(f"  ✓ {f.name} -> deploy/")
        stats["txt"] += 1

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
print("Consulte docs/ORGANIZACAO_PROJETO.md para mais informações.")

