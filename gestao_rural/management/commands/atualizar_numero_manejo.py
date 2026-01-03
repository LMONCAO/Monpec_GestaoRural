"""Comando Django para atualizar o número de manejo dos animais existentes."""

from django.core.management.base import BaseCommand
from gestao_rural.models import AnimalIndividual
import re


def extrair_numero_manejo(codigo_sisbov):
    """Extrai o número de manejo do código SISBOV."""
    if not codigo_sisbov:
        return ''
    codigo_limpo = re.sub(r'\D', '', str(codigo_sisbov))
    if len(codigo_limpo) == 15:
        # Código SISBOV completo: extrair posições 8-13 (6 dígitos)
        return codigo_limpo[8:14]
    elif len(codigo_limpo) >= 8:
        # Lógica anterior para códigos menores
        return codigo_limpo[:-1][-7:]
    return ''


class Command(BaseCommand):
    help = 'Atualiza o número de manejo de todos os animais baseado no código SISBOV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem salvar no banco de dados (apenas mostra o que seria feito)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        animais = AnimalIndividual.objects.filter(
            codigo_sisbov__isnull=False
        ).exclude(codigo_sisbov='')
        
        total = animais.count()
        atualizados = 0
        sem_manejo = 0
        
        self.stdout.write(self.style.SUCCESS(f'Processando {total} animais...'))
        
        for animal in animais:
            numero_manejo = extrair_numero_manejo(animal.codigo_sisbov)
            
            if numero_manejo:
                if animal.numero_manejo != numero_manejo:
                    if not dry_run:
                        animal.numero_manejo = numero_manejo
                        animal.save(update_fields=['numero_manejo'])
                    self.stdout.write(
                        f'  {animal.numero_brinco}: {animal.codigo_sisbov} -> Manejo: {numero_manejo}'
                    )
                    atualizados += 1
            else:
                sem_manejo += 1
                self.stdout.write(
                    self.style.WARNING(
                        f'  {animal.numero_brinco}: Não foi possível extrair número de manejo de {animal.codigo_sisbov}'
                    )
                )
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f'\nDRY RUN: {atualizados} animais seriam atualizados, {sem_manejo} sem manejo calculável'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'\n✓ {atualizados} animais atualizados, {sem_manejo} sem manejo calculável'
            ))



