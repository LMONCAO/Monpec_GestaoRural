from django.core.management.base import BaseCommand
from gestao_rural.models import CategoriaAnimal

class Command(BaseCommand):
    help = 'Popula as categorias de animais com pesos médios padrão'

    def handle(self, *args, **options):
        # Pesos médios padrão por categoria
        pesos_padrao = {
            'Bezerras (0-12m)': 150.0,
            'Bezerros (0-12m)': 180.0,
            'Novilhas (12-24m)': 300.0,
            'Garrotes (12-24m)': 350.0,
            'Primíparas (24-36m)': 400.0,
            'Bois Magros (24-36m)': 450.0,
            'Multíparas (>36m)': 450.0,
            'Vacas de Descarte': 400.0,
            'Bois (24-36m)': 500.0,
            'Touros': 600.0,
        }
        
        categorias_atualizadas = 0
        
        for nome_categoria, peso in pesos_padrao.items():
            try:
                categoria = CategoriaAnimal.objects.get(nome=nome_categoria)
                if not categoria.peso_medio_kg or categoria.peso_medio_kg == 0:
                    categoria.peso_medio_kg = peso
                    categoria.save()
                    categorias_atualizadas += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {nome_categoria}: {peso} kg')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ {nome_categoria}: já tem peso {categoria.peso_medio_kg} kg')
                    )
            except CategoriaAnimal.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Categoria não encontrada: {nome_categoria}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎯 Total de categorias atualizadas: {categorias_atualizadas}')
        )

