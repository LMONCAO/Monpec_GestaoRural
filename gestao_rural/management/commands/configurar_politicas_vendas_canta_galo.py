# -*- coding: utf-8 -*-
"""
Management command para configurar políticas de vendas e transferências
para Fazenda Canta Galo conforme especificado:
- Vender 20% das fêmeas nascidas (bezerras)
- Vender 20% dos machos nascidos (bezerros)
- Transferir todas as vacas descarte para engorda
- Transferir todos os machos 24-36 meses para engorda
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from gestao_rural.models import Propriedade, CategoriaAnimal, PoliticaVendasCategoria, ConfiguracaoVenda


class Command(BaseCommand):
    help = 'Configura políticas de vendas e transferências para Fazenda Canta Galo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fazenda-engorda',
            type=str,
            help='Nome da fazenda de engorda (se não existir, será criada)',
            default='Fazenda Engorda'
        )
        parser.add_argument(
            '--sobrescrever',
            action='store_true',
            help='Sobrescrever políticas existentes',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Configura as políticas de vendas e transferências"""
        
        # 1. Buscar Fazenda Canta Galo
        try:
            propriedade = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
            self.stdout.write(self.style.SUCCESS(f'[OK] Fazenda encontrada: {propriedade.nome_propriedade}'))
        except Propriedade.DoesNotExist:
            self.stdout.write(self.style.ERROR('[ERRO] Fazenda "Canta Galo" nao encontrada!'))
            return
        except Propriedade.MultipleObjectsReturned:
            propriedades = Propriedade.objects.filter(nome_propriedade__icontains='Canta Galo')
            self.stdout.write(self.style.WARNING(f'[AVISO] Multiplas fazendas encontradas. Usando a primeira:'))
            propriedade = propriedades.first()
        
        # 2. Buscar ou criar Fazenda de Engorda
        fazenda_engorda_nome = options['fazenda_engorda']
        try:
            fazenda_engorda = Propriedade.objects.get(nome_propriedade__icontains=fazenda_engorda_nome)
            self.stdout.write(self.style.SUCCESS(f'[OK] Fazenda de engorda encontrada: {fazenda_engorda.nome_propriedade}'))
        except Propriedade.DoesNotExist:
            # Criar fazenda de engorda se não existir
            self.stdout.write(self.style.WARNING(f'[AVISO] Fazenda de engorda nao encontrada. Criando...'))
            # Usar o mesmo produtor da Fazenda Canta Galo
            fazenda_engorda = Propriedade.objects.create(
                nome_propriedade=fazenda_engorda_nome,
                produtor=propriedade.produtor,
                municipio=propriedade.municipio,
                uf=propriedade.uf,
                area_total_ha=Decimal('0.00'),
                tipo_operacao='PECUARIA',
                tipo_ciclo_pecuario=['ENGORDA']
            )
            self.stdout.write(self.style.SUCCESS(f'[OK] Fazenda de engorda criada: {fazenda_engorda.nome_propriedade}'))
        
        # 3. Buscar categorias necessárias
        categorias_map = {}
        categorias_necessarias = {
            'Bezerro(a) 0-12 F': {'percentual': 30, 'tipo': 'VENDA'},
            'Bezerro(o) 0-12 M': {'percentual': 20, 'tipo': 'VENDA'},
            'Vacas Descarte +36 M': {'percentual': 100, 'tipo': 'TRANSFERENCIA'},
            'Boi 24-36 M': {'percentual': 100, 'tipo': 'TRANSFERENCIA'},
        }
        
        for nome_categoria in categorias_necessarias.keys():
            try:
                categoria = CategoriaAnimal.objects.get(nome=nome_categoria, ativo=True)
                categorias_map[nome_categoria] = categoria
            except CategoriaAnimal.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'[AVISO] Categoria "{nome_categoria}" nao encontrada. Pulando...'
                ))
        
        # 4. Limpar políticas existentes se solicitado
        if options['sobrescrever']:
            PoliticaVendasCategoria.objects.filter(propriedade=propriedade).delete()
            ConfiguracaoVenda.objects.filter(propriedade=propriedade).delete()
            self.stdout.write(self.style.WARNING('[INFO] Politicas anteriores excluidas'))
        
        # 5. Criar políticas
        self.stdout.write(self.style.SUCCESS('\n[INFO] Configurando politicas...\n'))
        
        politicas_criadas = 0
        
        # Bezerras: 30% venda
        if 'Bezerro(a) 0-12 F' in categorias_map:
            categoria = categorias_map['Bezerro(a) 0-12 F']
            politica, created = PoliticaVendasCategoria.objects.update_or_create(
                propriedade=propriedade,
                categoria=categoria,
                defaults={
                    'percentual_venda': Decimal('30.00'),
                    'quantidade_venda': 0,  # Será calculado automaticamente
                    'reposicao_tipo': 'NAO_REP',
                    'quantidade_transferir': 0,
                    'quantidade_comprar': 0
                }
            )
            politicas_criadas += 1
            status = '[OK] Criado' if created else '[OK] Atualizado'
            self.stdout.write(
                f'{status} {categoria.nome}: {politica.percentual_venda}% VENDA'
            )
        
        # Bezerros: 20% venda
        if 'Bezerro(o) 0-12 M' in categorias_map:
            categoria = categorias_map['Bezerro(o) 0-12 M']
            politica, created = PoliticaVendasCategoria.objects.update_or_create(
                propriedade=propriedade,
                categoria=categoria,
                defaults={
                    'percentual_venda': Decimal('20.00'),
                    'quantidade_venda': 0,  # Será calculado automaticamente
                    'reposicao_tipo': 'NAO_REP',
                    'quantidade_transferir': 0,
                    'quantidade_comprar': 0
                }
            )
            politicas_criadas += 1
            status = '[OK] Criado' if created else '[OK] Atualizado'
            self.stdout.write(
                f'{status} {categoria.nome}: {politica.percentual_venda}% VENDA'
            )
        
        # Vacas Descarte: 100% transferência para engorda
        if 'Vacas Descarte +36 M' in categorias_map:
            categoria = categorias_map['Vacas Descarte +36 M']
            # Usar ConfiguracaoVenda para transferências de saída
            config, created = ConfiguracaoVenda.objects.update_or_create(
                propriedade=propriedade,
                categoria_venda=categoria,
                defaults={
                    'frequencia_venda': 'MENSAL',
                    'quantidade_venda': 0,  # Será calculado automaticamente (100% do saldo)
                    'tipo_reposicao': 'TRANSFERENCIA',
                    'fazenda_destino': fazenda_engorda,
                    'quantidade_transferencia': 0,  # Será calculado automaticamente
                    'ativo': True
                }
            )
            politicas_criadas += 1
            status = '[OK] Criado' if created else '[OK] Atualizado'
            self.stdout.write(
                f'{status} {categoria.nome}: 100% TRANSFERENCIA -> {fazenda_engorda.nome_propriedade}'
            )
        
        # Bois 24-36 M: 100% transferência para engorda
        if 'Boi 24-36 M' in categorias_map:
            categoria = categorias_map['Boi 24-36 M']
            # Usar ConfiguracaoVenda para transferências de saída
            config, created = ConfiguracaoVenda.objects.update_or_create(
                propriedade=propriedade,
                categoria_venda=categoria,
                defaults={
                    'frequencia_venda': 'MENSAL',
                    'quantidade_venda': 0,  # Será calculado automaticamente (100% do saldo)
                    'tipo_reposicao': 'TRANSFERENCIA',
                    'fazenda_destino': fazenda_engorda,
                    'quantidade_transferencia': 0,  # Será calculado automaticamente
                    'ativo': True
                }
            )
            politicas_criadas += 1
            status = '[OK] Criado' if created else '[OK] Atualizado'
            self.stdout.write(
                f'{status} {categoria.nome}: 100% TRANSFERENCIA -> {fazenda_engorda.nome_propriedade}'
            )
        
        # 6. Resumo
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('RESUMO DAS POLITICAS CONFIGURADAS'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Propriedade: {propriedade.nome_propriedade}')
        self.stdout.write(f'Fazenda de Engorda: {fazenda_engorda.nome_propriedade}')
        self.stdout.write(f'\nPoliticas configuradas:')
        self.stdout.write(f'   - Bezerras (0-12 M): 30% VENDA')
        self.stdout.write(f'   - Bezerros (0-12 M): 20% VENDA')
        self.stdout.write(f'   - Vacas Descarte (+36 M): 100% TRANSFERENCIA -> {fazenda_engorda.nome_propriedade}')
        self.stdout.write(f'   - Bois (24-36 M): 100% TRANSFERENCIA -> {fazenda_engorda.nome_propriedade}')
        self.stdout.write(f'\nTotal de politicas criadas/atualizadas: {politicas_criadas}')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('\n[OK] Politicas configuradas com sucesso!'))
        self.stdout.write(self.style.WARNING(
            '\n[NOTA] As transferencias serao processadas automaticamente durante as projecoes.'
        ))
        self.stdout.write(self.style.WARNING(
            '    Certifique-se de que a fazenda de engorda esta configurada corretamente.'
        ))

