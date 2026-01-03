from django.core.management.base import BaseCommand
from gestao_rural.models import Propriedade, InventarioRebanho, CategoriaAnimal

class Command(BaseCommand):
    help = 'Testa se o inventário está sendo carregado corretamente'

    def handle(self, *args, **options):
        print("🔍 Testando carregamento do inventário...")
        
        # Listar todas as propriedades
        propriedades = Propriedade.objects.all()
        
        for prop in propriedades:
            print(f"\n📋 Propriedade: {prop.nome_propriedade}")
            
            # Buscar inventário
            inventario = InventarioRebanho.objects.filter(propriedade=prop)
            
            if inventario.exists():
                print(f"   ✅ Inventário encontrado: {inventario.count()} itens")
                for item in inventario:
                    print(f"      - {item.categoria.nome}: {item.quantidade} cabeças, R$ {item.valor_por_cabeca}")
            else:
                print(f"   ❌ Nenhum inventário encontrado")
        
        # Testar categorias
        print(f"\n📋 Categorias disponíveis:")
        categorias = CategoriaAnimal.objects.filter(ativo=True)
        for cat in categorias:
            print(f"   - {cat.nome}: {cat.peso_medio_kg or 0} kg")
        
        # Testar busca específica
        print(f"\n🔍 Testando busca por categoria:")
        for cat in categorias:
            inventario_cat = InventarioRebanho.objects.filter(categoria=cat)
            if inventario_cat.exists():
                for item in inventario_cat:
                    print(f"   ✅ {cat.nome}: R$ {item.valor_por_cabeca}")
            else:
                print(f"   ❌ {cat.nome}: Sem inventário")

