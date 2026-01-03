# -*- coding: utf-8 -*-
"""
Management command para carregar categorias padrão de animais
"""
from django.core.management.base import BaseCommand
from gestao_rural.models import CategoriaAnimal


class Command(BaseCommand):
    help = 'Carrega as categorias padrão de animais no banco de dados'

    def handle(self, *args, **options):
        """Carrega as categorias padrão"""
        
        categorias_padrao = [
            # BEZERROS (0-6 meses)
            {
                'nome': 'Bezerro(a)',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 6,
                'sexo': 'I',
                'descricao': 'Bezerros de 0 a 6 meses de idade'
            },
            
            # BEZERROS MAIORES (6-12 meses)
            {
                'nome': 'Bezerro(a) 6-12 meses',
                'idade_minima_meses': 6,
                'idade_maxima_meses': 12,
                'sexo': 'I',
                'descricao': 'Bezerros de 6 a 12 meses'
            },
            
            # NOVILHOS/NOVILHAS (12-24 meses)
            {
                'nome': 'Novilho(a)',
                'idade_minima_meses': 12,
                'idade_maxima_meses': 24,
                'sexo': 'I',
                'descricao': 'Novilhos de 12 a 24 meses'
            },
            
            # CATEGORIAS POR SEXO - FÊMEAS
            {
                'nome': 'Bezerra',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 6,
                'sexo': 'F',
                'descricao': 'Bezerra de 0 a 6 meses'
            },
            {
                'nome': 'Novilha',
                'idade_minima_meses': 6,
                'idade_maxima_meses': 24,
                'sexo': 'F',
                'descricao': 'Novilha de 6 a 24 meses'
            },
            {
                'nome': 'Novilha Primípara',
                'idade_minima_meses': 24,
                'idade_maxima_meses': 36,
                'sexo': 'F',
                'descricao': 'Novilha primípara (primeira cria)'
            },
            {
                'nome': 'Vaca Primípara',
                'idade_minima_meses': 36,
                'idade_maxima_meses': 48,
                'sexo': 'F',
                'descricao': 'Vaca primípara (já pariu uma vez)'
            },
            {
                'nome': 'Vaca Multípara',
                'idade_minima_meses': 48,
                'idade_maxima_meses': None,
                'sexo': 'F',
                'descricao': 'Vaca multípara (já pariu várias vezes)'
            },
            
            # CATEGORIAS POR SEXO - MACHOS
            {
                'nome': 'Bezerro',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 6,
                'sexo': 'M',
                'descricao': 'Bezerro macho de 0 a 6 meses'
            },
            {
                'nome': 'Novilho',
                'idade_minima_meses': 6,
                'idade_maxima_meses': 24,
                'sexo': 'M',
                'descricao': 'Novilho de 6 a 24 meses'
            },
            {
                'nome': 'Garrotes',
                'idade_minima_meses': 24,
                'idade_maxima_meses': 36,
                'sexo': 'M',
                'descricao': 'Garrotes (touros jovens)'
            },
            {
                'nome': 'Touro',
                'idade_minima_meses': 36,
                'idade_maxima_meses': None,
                'sexo': 'M',
                'descricao': 'Touro reprodutor'
            },
            {
                'nome': 'Boi de Corte',
                'idade_minima_meses': 24,
                'idade_maxima_meses': None,
                'sexo': 'M',
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
                    'descricao': cat_data.get('descricao', ''),
                    'ativo': True
                }
            )
            
            if criada:
                criadas += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Categoria criada: {cat_data["nome"]}'))
            else:
                # Atualizar se já existe
                atualizadas += 1
                self.stdout.write(self.style.WARNING(f'⚠️ Categoria já existe: {cat_data["nome"]}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Resumo: {criadas} categorias criadas, {atualizadas} já existiam'
        ))
