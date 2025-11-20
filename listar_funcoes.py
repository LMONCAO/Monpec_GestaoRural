import os
import ast
import json
from pathlib import Path

BASE_DIR = Path('gestao_rural')
report = {}

for path in BASE_DIR.rglob('*.py'):
    rel = path.relative_to(BASE_DIR).as_posix()
    try:
        source = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        source = path.read_text(encoding='latin-1')
    try:
        tree = ast.parse(source, filename=rel)
    except Exception as exc:
        report.setdefault(rel, []).append({
            "type": "error",
            "message": str(exc)
        })
        continue

    items = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            doc = ast.get_docstring(node) or ''
            items.append({
                "type": "function",
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],
                "doc": doc.strip().splitlines()[0] if doc.strip() else ''
            })
        elif isinstance(node, ast.ClassDef):
            methods = []
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    doc = ast.get_docstring(child) or ''
                    methods.append({
                        "name": child.name,
                        "args": [arg.arg for arg in child.args.args],
                        "doc": doc.strip().splitlines()[0] if doc.strip() else ''
                    })
            if methods:
                items.append({
                    "type": "class",
                    "name": node.name,
                    "methods": methods
                })
    if items:
        report[rel] = items

Path('funcoes_gestao_rural.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding='utf-8'
)
print(f"Total de módulos documentados: {len(report)}")
