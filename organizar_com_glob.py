#!/usr/bin/env python
# -*- coding: utf-8 -*-
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.absolute()

print("=" * 70)
print("ORGANIZAÇÃO DO PROJETO - MOVENDO ARQUIVOS")
print("=" * 70)
print(f"Diretório: {ROOT}")

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
    "entrypoint.sh", "organizar_com_glob.py"
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

# Usar glob que funciona melhor
print("\n1️⃣  Movendo arquivos .md para docs/...")
for f in ROOT.glob("*.md"):
    if f.name not in keep_in_root and f.parent == ROOT:
        dest = folders["docs"] / f.name
        counter = 1
        while dest.exists():
            dest = folders["docs"] / f"{f.stem}_{counter}{f.suffix}"
            counter += 1
        try:
            shutil.move(str(f), str(dest))
            print(f"  ✓ {f.name}")
            stats["md"] += 1
        except Exception as e:
            print(f"  ✗ {f.name}: {e}")

print("\n2️⃣  Movendo scripts (.sh, .ps1, .bat) para scripts/...")
for ext in [".sh", ".ps1", ".bat"]:
    for f in ROOT.glob(f"*{ext}"):
        if f.name not in keep_in_root and f.parent == ROOT:
            dest_dir = categorize(f.name)
            dest = dest_dir / f.name
            counter = 1
            while dest.exists():
                dest = dest_dir / f"{f.stem}_{counter}{f.suffix}"
                counter += 1
            try:
                shutil.move(str(f), str(dest))
                print(f"  ✓ {f.name} -> {dest_dir.relative_to(ROOT)}")
                stats[ext[1:]] += 1
            except Exception as e:
                print(f"  ✗ {f.name}: {e}")

print("\n3️⃣  Movendo scripts Python utilitários para scripts/utilitarios/...")
django_dirs = {"gestao_rural", "sistema_rural", "api", "templates", "static"}
for f in ROOT.glob("*.py"):
    if f.name not in keep_in_root and f.parent == ROOT:
        # Verificar se não está em subdiretório Django
        parts = f.parts
        is_django = any(d in parts for d in django_dirs)
        if not is_django:
            dest = folders["scripts/utilitarios"] / f.name
            counter = 1
            while dest.exists():
                dest = folders["scripts/utilitarios"] / f"{f.stem}_{counter}{f.suffix}"
                counter += 1
            try:
                shutil.move(str(f), str(dest))
                print(f"  ✓ {f.name}")
                stats["py"] += 1
            except Exception as e:
                print(f"  ✗ {f.name}: {e}")

print("\n4️⃣  Movendo arquivos .txt de comandos para deploy/...")
keywords = ["comando", "COMANDO", "deploy", "DEPLOY", "instrucoes", "INSTRUCOES"]
for f in ROOT.glob("*.txt"):
    if f.parent == ROOT and any(k in f.name for k in keywords):
        dest = folders["deploy"] / f.name
        counter = 1
        while dest.exists():
            dest = folders["deploy"] / f"{f.stem}_{counter}{f.suffix}"
            counter += 1
        try:
            shutil.move(str(f), str(dest))
            print(f"  ✓ {f.name}")
            stats["txt"] += 1
        except Exception as e:
            print(f"  ✗ {f.name}: {e}")

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

