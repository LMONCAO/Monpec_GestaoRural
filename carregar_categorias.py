from gestao_rural.models import CategoriaAnimal

categorias = [
    {'nome': 'Bezerros (0-12m)', 'descricao': 'Bezerros machos', 'sexo': 'M', 'idade_minima_meses': 0, 'idade_maxima_meses': 12},
    {'nome': 'Bezerras (0-12m)', 'descricao': 'Bezerras fêmeas', 'sexo': 'F', 'idade_minima_meses': 0, 'idade_maxima_meses': 12},
    {'nome': 'Garrotes (12-24m)', 'descricao': 'Garrotes machos', 'sexo': 'M', 'idade_minima_meses': 12, 'idade_maxima_meses': 24},
    {'nome': 'Novilhas (12-24m)', 'descricao': 'Novilhas fêmeas', 'sexo': 'F', 'idade_minima_meses': 12, 'idade_maxima_meses': 24},
    {'nome': 'Bois Magros (24-36m)', 'descricao': 'Bois magros', 'sexo': 'M', 'idade_minima_meses': 24, 'idade_maxima_meses': 36},
    {'nome': 'Novilhas Prontas (24-36m)', 'descricao': 'Novilhas prontas', 'sexo': 'F', 'idade_minima_meses': 24, 'idade_maxima_meses': 36},
    {'nome': 'Bois Gordos (36m+)', 'descricao': 'Bois gordos', 'sexo': 'M', 'idade_minima_meses': 36, 'idade_maxima_meses': 999},
    {'nome': 'Vacas Matrizes', 'descricao': 'Vacas matrizes', 'sexo': 'F', 'idade_minima_meses': 36, 'idade_maxima_meses': 999},
    {'nome': 'Touros Reprodutores', 'descricao': 'Touros', 'sexo': 'M', 'idade_minima_meses': 24, 'idade_maxima_meses': 999},
]

total = 0
for cat in categorias:
    obj, created = CategoriaAnimal.objects.get_or_create(nome=cat['nome'], defaults=cat)
    if created:
        total += 1
        print('Criada:', cat['nome'])
    else:
        print('Ja existe:', cat['nome'])

print('Total de categorias:', CategoriaAnimal.objects.count())

