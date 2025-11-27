# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from gestao_rural.models import Propriedade, CategoriaAnimal, PoliticaVendasCategoria


class Command(BaseCommand):
    help = 'Cria política de venda de 20% para bezerras'

    @transaction.atomic
    def handle(self, *args, **options):
        # Buscar primeira propriedade
        propriedade = Propriedade.objects.first()
        if not propriedade:
            self.stdout.write(self.style.ERROR('Nenhuma propriedade encontrada!'))
            return
        
        self.stdout.write(f'Propriedade: {propriedade.nome_propriedade}')
        
        # Buscar categoria de bezerras
        try:
            bezerras = CategoriaAnimal.objects.get(nome='Bezerro(a) 0-12 M')
            self.stdout.write(f'Categoria encontrada: {bezerras.nome}')
            
            # Criar ou atualizar política
            politica, created = PoliticaVendasCategoria.objects.update_or_create(
                propriedade=propriedade,
                categoria=bezerras,
                defaults={
                    'percentual_venda': Decimal('20.00'),
                    'quantidade_venda': 0,
                    'reposicao_tipo': 'NAO_REP',
                    'quantidade_transferir': 0,
                    'quantidade_comprar': 0
                }
            )
            
            status = "Criada" if created else "Atualizada"
            self.stdout.write(self.style.SUCCESS(f'Politica {status}: {politica.categoria.nome} - {politica.percentual_venda}%'))
            
        except CategoriaAnimal.DoesNotExist:
            self.stdout.write(self.style.ERROR('Categoria Bezerro(a) 0-12 M nao encontrada!'))
            return
        
        # Listar todas as políticas
        self.stdout.write('\nPolíticas de venda configuradas:')
        politicas = PoliticaVendasCategoria.objects.filter(propriedade=propriedade).order_by('categoria__nome')
        for p in politicas:
            self.stdout.write(f'  - {p.categoria.nome}: {p.percentual_venda}%')


