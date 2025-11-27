# -*- coding: utf-8 -*-
"""
Management command para criar inventário de 4800 matrizes para Fazenda Canta Galo
com o restante do rebanho proporcional (70% de nascimento)
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import date
from gestao_rural.models import Propriedade, CategoriaAnimal, InventarioRebanho


class Command(BaseCommand):
    help = 'Cria inventário de 4800 matrizes para Fazenda Canta Galo com rebanho proporcional (70% nascimento)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--data-inventario',
            type=str,
            help='Data do inventário no formato YYYY-MM-DD (padrão: hoje)',
        )
        parser.add_argument(
            '--sobrescrever',
            action='store_true',
            help='Sobrescrever inventário existente na mesma data',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Cria o inventário com 4800 matrizes e rebanho proporcional"""
        
        # 1. Buscar Fazenda Canta Galo
        try:
            propriedade = Propriedade.objects.get(nome_propriedade__icontains='Canta Galo')
            self.stdout.write(self.style.SUCCESS(f'✅ Fazenda encontrada: {propriedade.nome_propriedade}'))
        except Propriedade.DoesNotExist:
            self.stdout.write(self.style.ERROR('❌ Fazenda "Canta Galo" não encontrada!'))
            self.stdout.write('Propriedades disponíveis:')
            for prop in Propriedade.objects.all()[:10]:
                self.stdout.write(f'  - {prop.nome_propriedade} (ID: {prop.id})')
            return
        except Propriedade.MultipleObjectsReturned:
            propriedades = Propriedade.objects.filter(nome_propriedade__icontains='Canta Galo')
            self.stdout.write(self.style.WARNING(f'⚠️  Múltiplas fazendas encontradas. Usando a primeira:'))
            for prop in propriedades:
                self.stdout.write(f'  - {prop.nome_propriedade} (ID: {prop.id})')
            propriedade = propriedades.first()
        
        # 2. Definir data do inventário
        if options['data_inventario']:
            try:
                from datetime import datetime
                data_inventario = datetime.strptime(options['data_inventario'], '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(self.style.ERROR('❌ Data inválida! Use o formato YYYY-MM-DD'))
                return
        else:
            data_inventario = date.today()
        
        self.stdout.write(f'📅 Data do inventário: {data_inventario.strftime("%d/%m/%Y")}')
        
        # 3. Verificar se já existe inventário nesta data
        if not options['sobrescrever']:
            inventario_existente = InventarioRebanho.objects.filter(
                propriedade=propriedade,
                data_inventario=data_inventario
            ).exists()
            
            if inventario_existente:
                self.stdout.write(self.style.WARNING(
                    f'⚠️  Já existe inventário para esta data. Use --sobrescrever para substituir.'
                ))
                return
        
        # 4. Buscar categorias
        categorias_map = {}
        categorias_necessarias = [
            'Vacas em Reprodução +36 M',
            'Vacas Descarte +36 M',
            'Primíparas 24-36 M',
            'Novilha 12-24 M',
            'Bezerro(a) 0-12 M',
            'Bezerro(o) 0-12 M',
            'Garrote 12-24 M',
            'Boi 24-36 M',
            'Touro +36 M',
        ]
        
        for nome_categoria in categorias_necessarias:
            try:
                categoria = CategoriaAnimal.objects.get(nome=nome_categoria, ativo=True)
                categorias_map[nome_categoria] = categoria
            except CategoriaAnimal.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f'⚠️  Categoria "{nome_categoria}" não encontrada. Pulando...'
                ))
        
        if 'Vacas em Reprodução +36 M' not in categorias_map:
            self.stdout.write(self.style.ERROR('❌ Categoria "Vacas em Reprodução +36 M" não encontrada!'))
            return
        
        # 5. Calcular rebanho proporcional baseado em 4800 matrizes e 70% de nascimento
        matrizes = 4800
        taxa_nascimento = 0.70
        
        # Nascimentos anuais (70% das matrizes)
        nascimentos_anuais = int(matrizes * taxa_nascimento)  # 3360
        
        # Distribuição de sexo: 50% machos, 50% fêmeas
        bezerros_nascidos = int(nascimentos_anuais * 0.50)  # 1680
        bezerras_nascidas = int(nascimentos_anuais * 0.50)  # 1680
        
        # Taxa de mortalidade e descarte (aproximada)
        taxa_mortalidade_bezerros = 0.08  # 8%
        taxa_mortalidade_jovens = 0.05    # 5%
        taxa_descarte_vacas = 0.10         # 10% das matrizes
        
        # Cálculo do rebanho proporcional
        # Bezerros (0-12M): nascimentos do último ano menos mortalidade
        bezerros_0_12 = int(bezerros_nascidos * (1 - taxa_mortalidade_bezerros))  # ~1546
        
        # Bezerras (0-12M): nascimentos do último ano menos mortalidade
        bezerras_0_12 = int(bezerras_nascidas * (1 - taxa_mortalidade_bezerros))  # ~1546
        
        # Garrotes (12-24M): bezerros do ano anterior que sobreviveram
        garrotes_12_24 = int(bezerros_0_12 * (1 - taxa_mortalidade_jovens))  # ~1469
        
        # Novilhas (12-24M): bezerras do ano anterior que sobreviveram
        novilhas_12_24 = int(bezerras_0_12 * (1 - taxa_mortalidade_jovens))  # ~1469
        
        # Bois (24-36M): garrotes do ano anterior (considerando vendas)
        boi_24_36 = int(garrotes_12_24 * 0.85)  # ~1249 (15% vendidos)
        
        # Primíparas (24-36M): novilhas que entraram em reprodução
        primiparas_24_36 = int(novilhas_12_24 * 0.80)  # ~1175 (80% entram em reprodução)
        
        # Touros: 1% das matrizes (proporção típica)
        touros = max(1, int(matrizes * 0.01))  # 48
        
        # Vacas Descarte: 10% das matrizes
        vacas_descarte = int(matrizes * taxa_descarte_vacas)  # 480
        
        # Vacas em Reprodução: 4800 (valor base)
        vacas_reproducao = matrizes  # 4800
        
        # 6. Valores por cabeça (estimativas realistas em R$)
        valores_por_cabeca = {
            'Bezerro(a) 0-12 M': Decimal('1200.00'),
            'Bezerro(o) 0-12 M': Decimal('1100.00'),
            'Novilha 12-24 M': Decimal('1800.00'),
            'Garrote 12-24 M': Decimal('2000.00'),
            'Primíparas 24-36 M': Decimal('2800.00'),
            'Boi 24-36 M': Decimal('3500.00'),
            'Vacas Descarte +36 M': Decimal('2500.00'),
            'Vacas em Reprodução +36 M': Decimal('3200.00'),
            'Touro +36 M': Decimal('8000.00'),
        }
        
        # 7. Criar/atualizar inventário
        self.stdout.write(self.style.SUCCESS('\n📊 Criando inventário...\n'))
        
        if options['sobrescrever']:
            # Excluir inventário existente na mesma data
            InventarioRebanho.objects.filter(
                propriedade=propriedade,
                data_inventario=data_inventario
            ).delete()
            self.stdout.write(self.style.WARNING('🗑️  Inventário anterior excluído'))
        
        inventario_criado = {
            'Vacas em Reprodução +36 M': vacas_reproducao,
            'Vacas Descarte +36 M': vacas_descarte,
            'Primíparas 24-36 M': primiparas_24_36,
            'Novilha 12-24 M': novilhas_12_24,
            'Bezerro(a) 0-12 M': bezerras_0_12,
            'Bezerro(o) 0-12 M': bezerros_0_12,
            'Garrote 12-24 M': garrotes_12_24,
            'Boi 24-36 M': boi_24_36,
            'Touro +36 M': touros,
        }
        
        total_animais = 0
        total_valor = Decimal('0.00')
        itens_criados = 0
        
        for nome_categoria, quantidade in inventario_criado.items():
            if nome_categoria not in categorias_map:
                continue
            
            categoria = categorias_map[nome_categoria]
            valor_por_cabeca = valores_por_cabeca.get(nome_categoria, Decimal('0.00'))
            
            inventario, created = InventarioRebanho.objects.update_or_create(
                propriedade=propriedade,
                categoria=categoria,
                data_inventario=data_inventario,
                defaults={
                    'quantidade': quantidade,
                    'valor_por_cabeca': valor_por_cabeca
                }
            )
            
            valor_total = inventario.valor_total
            total_animais += quantidade
            total_valor += valor_total
            itens_criados += 1
            
            status = '✅ Criado' if created else '🔄 Atualizado'
            self.stdout.write(
                f'{status} {nome_categoria}: '
                f'{quantidade:,} cabeças × R$ {valor_por_cabeca:,.2f} = '
                f'R$ {valor_total:,.2f}'
            )
        
        # 8. Resumo
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('📊 RESUMO DO INVENTÁRIO'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'🏠 Propriedade: {propriedade.nome_propriedade}')
        self.stdout.write(f'📅 Data: {data_inventario.strftime("%d/%m/%Y")}')
        self.stdout.write(f'🐄 Matrizes (Vacas em Reprodução): {vacas_reproducao:,}')
        self.stdout.write(f'🐂 Total de Animais: {total_animais:,}')
        self.stdout.write(f'💰 Valor Total do Rebanho: R$ {total_valor:,.2f}')
        self.stdout.write(f'📋 Itens criados/atualizados: {itens_criados}')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('\n✅ Inventário criado com sucesso!'))



