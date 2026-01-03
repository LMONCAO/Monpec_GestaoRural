# -*- coding: utf-8 -*-
"""
Comando para atualizar preços dos planos de assinatura
"""

from django.core.management.base import BaseCommand
from gestao_rural.models import PlanoAssinatura
from decimal import Decimal


class Command(BaseCommand):
    help = 'Atualiza o preço mensal de referência de todos os planos ativos para R$ 99,90'

    def add_arguments(self, parser):
        parser.add_argument(
            '--preco',
            type=float,
            default=99.90,
            help='Preço a ser definido (padrão: 99.90)',
        )

    def handle(self, *args, **options):
        preco = Decimal(str(options['preco']))
        
        self.stdout.write(f"Atualizando planos para R$ {preco}...")
        
        planos = PlanoAssinatura.objects.filter(ativo=True)
        
        if not planos.exists():
            self.stdout.write(self.style.WARNING('Nenhum plano ativo encontrado.'))
            return
        
        atualizados = 0
        for plano in planos:
            plano.preco_mensal_referencia = preco
            plano.save()
            atualizados += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Plano "{plano.nome}" atualizado para R$ {preco}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ {atualizados} plano(s) atualizado(s) com sucesso!'
            )
        )

