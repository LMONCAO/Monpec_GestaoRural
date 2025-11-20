# -*- coding: utf-8 -*-
"""
Management command para criar as categorias padrão do sistema
As categorias são criadas automaticamente se não existirem
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from gestao_rural.models import CategoriaAnimal


class Command(BaseCommand):
    help = 'Cria as categorias padrão de animais do sistema (9 categorias)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força atualização mesmo se categoria já existir',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Cria as categorias padrão do sistema"""
        
        categorias_padrao = [
            # FÊMEAS (5 categorias)
            {
                'nome': 'Bezerro(a) 0-12 M',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 12,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Fêmeas de 0 a 12 Meses'
            },
            {
                'nome': 'Novilha 12-24 M',
                'idade_minima_meses': 12,
                'idade_maxima_meses': 24,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Fêmeas de 12 a 24 Meses'
            },
            {
                'nome': 'Primíparas 24-36 M',
                'idade_minima_meses': 24,
                'idade_maxima_meses': 36,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Fêmeas Primíparas de 24 a 36 Meses'
            },
            {
                'nome': 'Vacas Descarte +36 M',
                'idade_minima_meses': 36,
                'idade_maxima_meses': None,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Vacas de Descarte acima de 36 Meses'
            },
            {
                'nome': 'Vacas em Reprodução +36 M',
                'idade_minima_meses': 36,
                'idade_maxima_meses': None,
                'sexo': 'F',
                'raca': 'NELORE',
                'descricao': 'Vacas em Reprodução acima de 36 Meses'
            },
            
            # MACHOS (4 categorias)
            {
                'nome': 'Bezerro(o) 0-12 M',
                'idade_minima_meses': 0,
                'idade_maxima_meses': 12,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Machos de 0 a 12 Meses'
            },
            {
                'nome': 'Garrote 12-24 M',
                'idade_minima_meses': 12,
                'idade_maxima_meses': 24,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Garrotes de 12 a 24 Meses'
            },
            {
                'nome': 'Boi 24-36 M',
                'idade_minima_meses': 24,
                'idade_maxima_meses': 36,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Bois de 24 a 36 Meses'
            },
            {
                'nome': 'Touro +36 M',
                'idade_minima_meses': 36,
                'idade_maxima_meses': None,
                'sexo': 'M',
                'raca': 'NELORE',
                'descricao': 'Touros acima de 36 Meses'
            },
        ]
        
        criadas = 0
        atualizadas = 0
        ja_existiam = 0
        
        self.stdout.write(self.style.SUCCESS('\n📋 Criando categorias padrão do sistema...\n'))
        
        for cat_data in categorias_padrao:
            categoria, criada = CategoriaAnimal.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={
                    'idade_minima_meses': cat_data.get('idade_minima_meses'),
                    'idade_maxima_meses': cat_data.get('idade_maxima_meses'),
                    'sexo': cat_data.get('sexo', 'I'),
                    'raca': cat_data.get('raca', 'NELORE'),
                    'descricao': cat_data.get('descricao', ''),
                    'ativo': True
                }
            )
            
            if criada:
                criadas += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Categoria criada: {cat_data["nome"]}'))
            else:
                if options['force']:
                    # Atualizar categoria existente
                    categoria.idade_minima_meses = cat_data.get('idade_minima_meses')
                    categoria.idade_maxima_meses = cat_data.get('idade_maxima_meses')
                    categoria.sexo = cat_data.get('sexo', 'I')
                    categoria.raca = cat_data.get('raca', 'NELORE')
                    categoria.descricao = cat_data.get('descricao', '')
                    categoria.ativo = True
                    categoria.save()
                    atualizadas += 1
                    self.stdout.write(self.style.WARNING(f'🔄 Categoria atualizada: {cat_data["nome"]}'))
                else:
                    ja_existiam += 1
                    self.stdout.write(self.style.SUCCESS(f'ℹ️  Categoria já existe: {cat_data["nome"]}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Resumo: {criadas} criadas, {atualizadas} atualizadas, {ja_existiam} já existiam\n'
        ))
        
        self.stdout.write(self.style.SUCCESS('✅ Categorias padrão configuradas com sucesso!'))

















