import json
from pathlib import Path

data = json.loads(Path('funcoes_gestao_rural.json').read_text(encoding='utf-8'))

lines = ['# Relatório de Funções por Módulo', '']

for rel in sorted(data):
    display = rel.replace('\\', '/')
    lines.append(f"## {display}")
    for entry in data[rel]:
        if entry['type'] == 'function':
            args = ', '.join(entry.get('args') or [])
            doc = (entry.get('doc') or '').strip()
            doc_text = doc if doc else 'Sem descrição registrada.'
            signature = f"{entry['name']}({args})" if args else f"{entry['name']}()"
            lines.append(f"- Função `{signature}`: {doc_text}")
        elif entry['type'] == 'class':
            lines.append(f"- Classe `{entry['name']}`:")
            for method in entry.get('methods', []):
                args = ', '.join(method.get('args') or [])
                doc = (method.get('doc') or '').strip()
                doc_text = doc if doc else 'Sem descrição registrada.'
                signature = f"{method['name']}({args})" if args else f"{method['name']}()"
                lines.append(f"  - Método `{signature}`: {doc_text}")
    lines.append('')

Path('RELATORIO_FUNCOES_MODULOS.md').write_text('\n'.join(lines), encoding='utf-8')
print('Relatório gerado em RELATORIO_FUNCOES_MODULOS.md')
