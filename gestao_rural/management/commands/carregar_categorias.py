# -*- coding: utf-8 -*-
"""
Comando Django para carregar categorias pré-cadastradas
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Carrega categorias de animais pré-cadastradas no sistema'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('📦 Carregando categorias de animais...'))
        
        try:
            # Carregar fixture
            call_command('loaddata', 'categorias_animais.json')
            
            self.stdout.write(self.style.SUCCESS('✅ Categorias carregadas com sucesso!'))
            self.stdout.write('')
            self.stdout.write('Categorias disponíveis:')
            self.stdout.write('  1. Bezerros (0-12m) ♂')
            self.stdout.write('  2. Bezerras (0-12m) ♀')
            self.stdout.write('  3. Garrotes (12-24m) ♂')
            self.stdout.write('  4. Novilhas (12-24m) ♀')
            self.stdout.write('  5. Bois Magros (24-36m) ♂')
            self.stdout.write('  6. Primíparas (24-36m) ♀')
            self.stdout.write('  7. Multíparas (>36m) ♀')
            self.stdout.write('  8. Touros ♂')
            self.stdout.write('  9. Vacas de Descarte ♀')
            self.stdout.write('  10. Bois Gordos (>36m) ♂')
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('🎉 Sistema pronto para uso!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao carregar categorias: {e}'))
            self.stdout.write(self.style.WARNING('Verifique se o arquivo categorias_animais.json existe em gestao_rural/fixtures/'))

