# -*- coding: utf-8 -*-
"""
Management command para carregar TODAS as categorias padrão de animais
"""
from django.core.management.base import BaseCommand
from gestao_rural.models import CategoriaAnimal
from decimal import Decimal


class Command(BaseCommand):
    help = 'Carrega TODAS as categorias padrão de animais no banco de dados'

    def handle(self, *args, **options):
        """Carrega as categorias padrão"""
        
        categorias_padrao = [
            # CATEGORIAS INDEFINIDAS (GERAIS)
            {
                'nome': 'Bezerro(a)',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 12,
                'sexo': 'I',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('50.00'),
                'descricao': 'Bezerros de 0 a 12 meses de idade'
            },
            {
                'nome': 'Novilho(a)',
                'idade_minima_meses': 12,
                'idade_maxima_meses': 24,
                'sexo': 'I',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('250.00'),
                'descricao': 'Novilhos de 12 a 24 meses'
            },
            {
                'nome': 'Garrotes',
                'idade_minima_meses': 24,
                'idade_maxima_meses': 36,
                'sexo': 'I',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('350.00'),
                'descricao': 'Garrotes de 24 a 36 meses'
            },
            
            # CATEGORIAS FÊMEAS
            {
                'nome': 'Bezerra',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 6,
                'sexo': 'F',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('50.00'),
                'descricao': 'Bezerra de 0 a 6 meses'
            },
            {
                'nome': 'Novilha',
                'idade_minima_meses': 6,
                'idade_maxima_meses': 24,
                'sexo': 'F',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('250.00'),
                'descricao': 'Novilha de 6 a 24 meses'
            },
            {
                'nome': 'Novilha Primípara',
                'idade_minima_meses': 24,
                'idade_maxima_meses': 36,
                'sexo': 'F',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('350.00'),
                'descricao': 'Novilha primípara (primeira cria)'
            },
            {
                'nome': 'Vaca Primípara',
                'idade_minima_meses': 36,
                'idade_maxima_meses': 48,
                'sexo': 'F',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('450.00'),
                'descricao': 'Vaca primípara (já pariu uma vez)'
            },
            {
                'nome': 'Vaca Multípara',
                'idade_minima_meses': 48,
                'idade_maxima_meses': None,
                'sexo': 'F',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('500.00'),
                'descricao': 'Vaca multípara (já pariu várias vezes)'
            },
            
            # CATEGORIAS MACHOS
            {
                'nome': 'Bezerro',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 6,
                'sexo': 'M',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('55.00'),
                'descricao': 'Bezerro macho de 0 a 6 meses'
            },
            {
                'nome': 'Novilho',
                'idade_minima_meses': 6,
                'idade_maxima_meses': 24,
                'sexo': 'M',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('280.00'),
                'descricao': 'Novilho de 6 a 24 meses'
            },
            {
                'nome': 'Touro',
                'idade_minima_meses': 36,
                'idade_maxima_meses': None,
                'sexo': 'M',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('800.00'),
                'descricao': 'Touro reprodutor'
            },
            {
                'nome': 'Boi de Corte',
                'idade_minima_meses': 24,
                'idade_maxima_meses': None,
                'sexo': 'M',
                'raca': 'NELORE',
                'peso_medio_kg': Decimal('400.00'),
                'descricao': 'Boi para engorda e corte'
            },
        ]
        
        criadas = 0
        atualizadas = 0
        
        for cat_data in categorias_padrao:
            categoria, criada = CategoriaAnimal.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={
                    'idade_minima_meses': cat_data.get('idade_minima_meses'),
                    'idade_maxima_meses': cat_data.get('idade_maxima_meses'),
                    'sexo': cat_data.get('sexo', 'I'),
                    'raca': cat_data.get('raca', 'NELORE'),
                    'peso_medio_kg': cat_data.get('peso_medio_kg', Decimal('0.00')),
                    'descricao': cat_data.get('descricao', ''),
                    'ativo': True
                }
            )
            
            if criada:
                criadas += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Categoria criada: {cat_data["nome"]}'))
            else:
                # Atualizar se já existe
                categoria.sexo = cat_data.get('sexo', 'I')
                categoria.idade_minima_meses = cat_data.get('idade_minima_meses')
                categoria.idade_maxima_meses = cat_data.get('idade_maxima_meses')
                categoria.raca = cat_data.get('raca', 'NELORE')
                categoria.peso_medio_kg = cat_data.get('peso_medio_kg', Decimal('0.00'))
                categoria.descricao = cat_data.get('descricao', '')
                categoria.ativo = True
                categoria.save()
                atualizadas += 1
                self.stdout.write(self.style.WARNING(f'⚠️ Categoria atualizada: {cat_data["nome"]}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Resumo: {criadas} categorias criadas, {atualizadas} atualizadas'
        ))

