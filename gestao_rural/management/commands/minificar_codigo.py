"""
Comando para minificar e ofuscar código JavaScript/CSS
Uso: python manage.py minificar_codigo
"""
from django.core.management.base import BaseCommand
from pathlib import Path
import re


class Command(BaseCommand):
    help = 'Minifica e ofusca código JavaScript/CSS para proteção'

    def handle(self, *args, **options):
        self.stdout.write('Minificando código...')
        
        # Minificar JavaScript
        js_files = [
            'static/js/protecao_codigo.js',
        ]
        
        for js_file in js_files:
            file_path = Path(js_file)
            if file_path.exists():
                self._minificar_js(file_path)
                self.stdout.write(self.style.SUCCESS(f'Minificado: {js_file}'))
        
        self.stdout.write(self.style.SUCCESS('Minificação concluída!'))

    def _minificar_js(self, file_path: Path):
        """Minifica arquivo JavaScript"""
        content = file_path.read_text(encoding='utf-8')
        
        # Remover comentários
        content = re.sub(r'//.*', '', content)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Remover espaços extras
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\s*{\s*', '{', content)
        content = re.sub(r'\s*}\s*', '}', content)
        content = re.sub(r'\s*;\s*', ';', content)
        content = re.sub(r'\s*,\s*', ',', content)
        content = re.sub(r'\s*=\s*', '=', content)
        
        # Salvar versão minificada
        minified_path = file_path.parent / f"{file_path.stem}.min{file_path.suffix}"
        minified_path.write_text(content, encoding='utf-8')







