# -*- coding: utf-8 -*-
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import CategoriaAnimal, MovimentacaoProjetada, InventarioRebanho

print("=" * 60)
print("VERIFICACAO FINAL - CATEGORIA BEZERRO")
print("=" * 60)

# Verificar se a categoria ainda existe
cat_inexistente = CategoriaAnimal.objects.filter(nome='Bezerro(a) 0-12 M').first()
if cat_inexistente:
    print(f"\n[ERRO] Categoria 'Bezerro(a) 0-12 M' ainda existe!")
    print(f"   ID: {cat_inexistente.id}, Sexo: {cat_inexistente.sexo}")
else:
    print(f"\n[OK] Categoria 'Bezerro(a) 0-12 M' nao existe mais")

# Verificar movimentações usando essa categoria
movs = MovimentacaoProjetada.objects.filter(categoria__nome='Bezerro(a) 0-12 M')
print(f"\n[INFO] Movimentacoes usando 'Bezerro(a) 0-12 M': {movs.count()}")
if movs.exists():
    print("   [ERRO] Ainda ha movimentacoes usando esta categoria!")
    for m in movs[:5]:
        print(f"      - ID {m.id}: {m.data_movimentacao.strftime('%d/%m/%Y')} - {m.quantidade}")

# Verificar inventários
invs = InventarioRebanho.objects.filter(categoria__nome='Bezerro(a) 0-12 M')
print(f"\n[INFO] Inventarios usando 'Bezerro(a) 0-12 M': {invs.count()}")

# Listar categorias corretas
print(f"\n[INFO] Categorias corretas de bezerros:")
categorias_corretas = CategoriaAnimal.objects.filter(nome__icontains='Bezerro').order_by('nome')
for c in categorias_corretas:
    print(f"   - {c.nome} (ID: {c.id}, Sexo: {c.sexo})")

print(f"\n[OK] Verificacao concluida!")
























