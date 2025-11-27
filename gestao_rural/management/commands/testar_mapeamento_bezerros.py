# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from gestao_rural.apis_integracao.api_cepea import CEPEAService
from gestao_rural.models import PrecoCEPEA


class Command(BaseCommand):
    help = 'Testa o mapeamento de categorias de bezerros para CEPEA'

    def handle(self, *args, **options):
        service = CEPEAService()
        categorias_teste = ['Bezerro(o) 0-12 M', 'Bezerro(a) 0-12 M', 'Bezerro(a) 0-12 F']

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write('Teste de mapeamento de categorias:')
        self.stdout.write('=' * 70)

        for cat in categorias_teste:
            tipo_cepea = service.mapear_categoria_para_cepea(cat)
            preco = PrecoCEPEA.objects.filter(uf='SP', ano=2024, tipo_categoria=tipo_cepea).first()
            if preco:
                self.stdout.write(
                    f'{cat:30} -> {tipo_cepea:10} -> R$ {preco.preco_medio:>12,.2f}'
                )
            else:
                self.stdout.write(
                    f'{cat:30} → {tipo_cepea:10} → PREÇO NÃO ENCONTRADO'
                )

        self.stdout.write('=' * 70)
        
        bezerro = PrecoCEPEA.objects.filter(uf='SP', ano=2024, tipo_categoria='BEZERRO').first()
        bezerra = PrecoCEPEA.objects.filter(uf='SP', ano=2024, tipo_categoria='BEZERRA').first()

        if bezerro and bezerra:
            diferenca_pct = ((bezerro.preco_medio / bezerra.preco_medio - 1) * 100)
            self.stdout.write(f'\nDiferença:')
            self.stdout.write(f'  Bezerro (macho): R$ {bezerro.preco_medio:,.2f}')
            self.stdout.write(f'  Bezerra (fêmea): R$ {bezerra.preco_medio:,.2f}')
            self.stdout.write(f'  Bezerro é {diferenca_pct:.1f}% mais caro que Bezerra')
            self.stdout.write('')

