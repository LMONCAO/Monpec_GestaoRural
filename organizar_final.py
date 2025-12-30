import os
import shutil
from pathlib import Path

ROOT = Path(r"C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural")

print("=" * 60)
print("ORGANIZAÇÃO DO PROJETO")
print("=" * 60)
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
    "entrypoint.sh", "organizar_final.py"
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

# Usar os.listdir ao invés de iterdir
root_str = str(ROOT)
print("\n1. Movendo arquivos .md...")
for name in os.listdir(root_str):
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

print("\n2. Movendo scripts...")
for ext in [".sh", ".ps1", ".bat"]:
    for name in os.listdir(root_str):
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

print("\n3. Movendo scripts Python utilitários...")
django_dirs = {"gestao_rural", "sistema_rural", "api", "templates", "static"}
for name in os.listdir(root_str):
    item_path = ROOT / name
    if item_path.is_file() and name.endswith(".py") and name not in keep_in_root:
        parts = str(item_path).split(os.sep)
        is_django = any(d in parts for d in django_dirs)
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

print("\n4. Movendo arquivos .txt de comandos...")
keywords = ["comando", "COMANDO", "deploy", "DEPLOY", "instrucoes", "INSTRUCOES"]
for name in os.listdir(root_str):
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

