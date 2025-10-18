from django.core.management.base import BaseCommand
from gestao_rural.models import CategoriaAnimal

class Command(BaseCommand):
    help = 'Verifica e corrige categorias de animais'

    def handle(self, *args, **options):
        print("🔍 Verificando categorias de animais...")
        
        # Listar todas as categorias
        categorias = CategoriaAnimal.objects.all()
        
        for cat in categorias:
            print(f"\n📋 {cat.nome}:")
            print(f"   Sexo: {cat.get_sexo_display()}")
            print(f"   Raça: {cat.get_raca_display()}")
            print(f"   Idade: {cat.idade_minima_meses}-{cat.idade_maxima_meses} meses")
            print(f"   Peso Médio: {cat.peso_medio_kg or 0} kg")
            print(f"   Ativo: {cat.ativo}")
            
            # Sugerir peso médio baseado no nome da categoria
            if not cat.peso_medio_kg or cat.peso_medio_kg == 0:
                peso_sugerido = self.sugerir_peso(cat.nome)
                if peso_sugerido:
                    print(f"   💡 Peso sugerido: {peso_sugerido} kg")
                    cat.peso_medio_kg = peso_sugerido
                    cat.save()
                    print(f"   ✅ Peso atualizado para {peso_sugerido} kg")
    
    def sugerir_peso(self, nome_categoria):
        """Sugere peso médio baseado no nome da categoria"""
        nome_lower = nome_categoria.lower()
        
        if 'bezerr' in nome_lower and '0-12' in nome_lower:
            return 150.0 if 'fêmea' in nome_lower or 'bezerra' in nome_lower else 180.0
        elif 'novilh' in nome_lower or 'garrot' in nome_lower:
            return 300.0 if 'fêmea' in nome_lower or 'novilh' in nome_lower else 350.0
        elif 'primípar' in nome_lower:
            return 400.0
        elif 'multípar' in nome_lower or 'vaca' in nome_lower:
            return 450.0
        elif 'boi' in nome_lower:
            return 500.0
        elif 'touro' in nome_lower:
            return 600.0
        
        return None

