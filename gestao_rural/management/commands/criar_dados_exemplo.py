# -*- coding: utf-8 -*-
"""
Comando Django para criar dados de exemplo
python manage.py criar_dados_exemplo
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date, timedelta
import random

from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, AnimalIndividual
)


class Command(BaseCommand):
    help = 'Cria dados de exemplo para testes do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--usuario',
            type=str,
            default='admin',
            help='Nome do usuário para associar os dados'
        )

    def handle(self, *args, **options):
        usuario_nome = options['usuario']
        
        # Criar ou obter usuário
        usuario, created = User.objects.get_or_create(
            username=usuario_nome,
            defaults={
                'email': f'{usuario_nome}@exemplo.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            usuario.set_password('admin123')
            usuario.save()
            self.stdout.write(self.style.SUCCESS(f'Usuário {usuario_nome} criado com sucesso!'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Usando usuário existente: {usuario_nome}'))

        # Criar Produtor
        produtor, created = ProdutorRural.objects.get_or_create(
            cpf_cnpj='12345678901',
            defaults={
                'nome': 'João Silva',
                'usuario_responsavel': usuario,
                'telefone': '(67) 99999-9999',
                'email': 'joao@exemplo.com'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Produtor criado!'))

        # Criar Propriedade
        propriedade, created = Propriedade.objects.get_or_create(
            nome_propriedade='Fazenda Exemplo',
            produtor=produtor,
            defaults={
                'municipio': 'Campo Grande',
                'uf': 'MS',
                'area_total': Decimal('1000.00'),
                'tipo': 'PROPRIA',
                'valor_hectare': Decimal('5000.00')
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Propriedade criada!'))

        # Criar Categorias
        categorias_nomes = [
            'Bezerros (0-12m)', 'Bezerras (0-12m)',
            'Garrotes (12-24m)', 'Novilhas (12-24m)',
            'Bois Magros (24-36m)', 'Primíparas (24-36m)',
            'Multíparas (>36m)', 'Touros', 'Vacas de Descarte'
        ]
        
        categorias = {}
        for nome in categorias_nomes:
            cat, created = CategoriaAnimal.objects.get_or_create(nome=nome)
            categorias[nome] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'Categoria {nome} criada!'))

        # Criar Animais Individuais
        self.stdout.write('Criando animais individuais...')
        animais_criados = 0
        
        # Bezerros e Bezerras
        for i in range(1, 11):
            sexo = 'M' if i % 2 == 0 else 'F'
            categoria_nome = 'Bezerros (0-12m)' if sexo == 'M' else 'Bezerras (0-12m)'
            data_nasc = date.today() - timedelta(days=random.randint(30, 300))
            
            AnimalIndividual.objects.get_or_create(
                numero_brinco=f'BZ{str(i).zfill(4)}',
                propriedade=propriedade,
                defaults={
                    'categoria': categorias[categoria_nome],
                    'sexo': sexo,
                    'data_nascimento': data_nasc,
                    'status': 'ATIVO',
                    'valor_aquisicao': Decimal('1500.00')
                }
            )
            animais_criados += 1

        # Garrotes e Novilhas
        for i in range(1, 16):
            sexo = 'M' if i % 2 == 0 else 'F'
            categoria_nome = 'Garrotes (12-24m)' if sexo == 'M' else 'Novilhas (12-24m)'
            data_nasc = date.today() - timedelta(days=random.randint(400, 700))
            
            AnimalIndividual.objects.get_or_create(
                numero_brinco=f'GV{str(i).zfill(4)}',
                propriedade=propriedade,
                defaults={
                    'categoria': categorias[categoria_nome],
                    'sexo': sexo,
                    'data_nascimento': data_nasc,
                    'status': 'ATIVO',
                    'valor_aquisicao': Decimal('2500.00')
                }
            )
            animais_criados += 1

        # Multíparas
        for i in range(1, 21):
            data_nasc = date.today() - timedelta(days=random.randint(1000, 2000))
            
            AnimalIndividual.objects.get_or_create(
                numero_brinco=f'MP{str(i).zfill(4)}',
                propriedade=propriedade,
                defaults={
                    'categoria': categorias['Multíparas (>36m)'],
                    'sexo': 'F',
                    'data_nascimento': data_nasc,
                    'status': 'ATIVO',
                    'valor_aquisicao': Decimal('3500.00')
                }
            )
            animais_criados += 1

        self.stdout.write(self.style.SUCCESS(f'{animais_criados} animais criados!'))

        # Criar dados de IATF se o módulo existir
        try:
            from gestao_rural.models_iatf_completo import (
                ProtocoloIATF, TouroSemen, LoteSemen, LoteIATF, IATFIndividual
            )
            
            # Criar Protocolo
            protocolo, created = ProtocoloIATF.objects.get_or_create(
                nome='Ovsynch Padrão',
                defaults={
                    'tipo': 'OVSYNCH',
                    'dia_gnrh': 0,
                    'dia_pgf2a': 7,
                    'dia_gnrh_final': 9,
                    'dia_iatf': 10,
                    'taxa_prenhez_esperada': Decimal('50.00'),
                    'custo_protocolo': Decimal('150.00')
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Protocolo IATF criado!'))

            # Criar Touro Sêmen
            touro, created = TouroSemen.objects.get_or_create(
                numero_touro='T001',
                defaults={
                    'nome_touro': 'Touro Exemplo',
                    'raca': 'Nelore',
                    'tipo_semen': 'CONVENCIONAL',
                    'preco_dose': Decimal('80.00')
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Touro Sêmen criado!'))

            # Criar Lote Sêmen
            lote_semen, created = LoteSemen.objects.get_or_create(
                numero_lote='LOTE001',
                propriedade=propriedade,
                defaults={
                    'touro': touro,
                    'numero_doses': 50,
                    'data_aquisicao': date.today() - timedelta(days=30),
                    'preco_unitario': Decimal('80.00'),
                    'status': 'ESTOQUE'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Lote de Sêmen criado!'))

            # Criar Lote IATF
            lote_iatf, created = LoteIATF.objects.get_or_create(
                nome_lote='Lote IATF Exemplo',
                propriedade=propriedade,
                defaults={
                    'protocolo': protocolo,
                    'data_inicio': date.today() - timedelta(days=20),
                    'touro_semen': touro,
                    'lote_semen': lote_semen,
                    'status': 'EM_ANDAMENTO',
                    'custo_medicamentos': Decimal('1500.00'),
                    'custo_mao_obra': Decimal('500.00')
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS('Lote IATF criado!'))

            # Criar IATFs Individuais
            animais_femeas = AnimalIndividual.objects.filter(
                propriedade=propriedade,
                sexo='F',
                status='ATIVO'
            )[:5]
            
            for animal in animais_femeas:
                IATFIndividual.objects.get_or_create(
                    animal_individual=animal,
                    lote_iatf=lote_iatf,
                    defaults={
                        'propriedade': propriedade,
                        'protocolo': protocolo,
                        'data_inicio_protocolo': lote_iatf.data_inicio,
                        'touro_semen': touro,
                        'lote_semen': lote_semen,
                        'status': 'DIA_7_PGF2A',
                        'custo_protocolo': Decimal('30.00'),
                        'custo_semen': Decimal('80.00'),
                        'custo_inseminacao': Decimal('10.00')
                    }
                )
            
            self.stdout.write(self.style.SUCCESS(f'{animais_femeas.count()} IATFs individuais criadas!'))

        except ImportError:
            self.stdout.write(self.style.WARNING('Módulo IATF completo não encontrado. Pulando criação de dados IATF.'))

        self.stdout.write(self.style.SUCCESS('\n✅ Dados de exemplo criados com sucesso!'))
        self.stdout.write(self.style.SUCCESS(f'   Usuário: {usuario_nome} / Senha: admin123'))
        self.stdout.write(self.style.SUCCESS(f'   Propriedade: {propriedade.nome_propriedade}'))


