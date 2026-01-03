# -*- coding: utf-8 -*-
"""
Management command para remover categorias duplicadas ou incorretas
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from gestao_rural.models import CategoriaAnimal, InventarioRebanho, MovimentacaoProjetada


class Command(BaseCommand):
    help = 'Remove categorias duplicadas ou incorretas do sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra o que seria removido sem realmente remover',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Remove categorias duplicadas ou incorretas"""
        
        dry_run = options['dry_run']
        
        # Categorias a remover (nomes incorretos ou duplicados)
        categorias_para_remover = [
            'Garrote 12-4 M',  # Erro de digitação - deveria ser 12-24 (mantém Garrote 12-24 M)
        ]
        
        # Categoria correta para migrar dados
        categoria_correta_map = {
            'Garrote 12-4 M': 'Garrote 12-24 M',
        }
        
        removidas = 0
        mantidas = 0
        
        self.stdout.write(self.style.SUCCESS('\n🔍 Verificando categorias duplicadas/incorretas...\n'))
        
        for nome_incorreto in categorias_para_remover:
            try:
                categoria = CategoriaAnimal.objects.get(nome=nome_incorreto)
                
                # Verificar se está sendo usada
                inventarios_count = InventarioRebanho.objects.filter(categoria=categoria).count()
                movimentacoes_count = MovimentacaoProjetada.objects.filter(categoria=categoria).count()
                
                if inventarios_count > 0 or movimentacoes_count > 0:
                    # Se estiver em uso, tentar migrar para categoria correta
                    nome_correto = categoria_correta_map.get(nome_incorreto)
                    if nome_correto:
                        try:
                            categoria_correta = CategoriaAnimal.objects.get(nome=nome_correto)
                            
                            if dry_run:
                                self.stdout.write(self.style.WARNING(
                                    f'🔍 [DRY RUN] Categoria "{nome_incorreto}" seria migrada para "{nome_correto}" '
                                    f'({inventarios_count} inventários, {movimentacoes_count} movimentações)'
                                ))
                            else:
                                # Migrar dados
                                InventarioRebanho.objects.filter(categoria=categoria).update(categoria=categoria_correta)
                                MovimentacaoProjetada.objects.filter(categoria=categoria).update(categoria=categoria_correta)
                                
                                # Remover categoria incorreta
                                categoria.delete()
                                self.stdout.write(self.style.SUCCESS(
                                    f'✅ Categoria "{nome_incorreto}" migrada para "{nome_correto}" e removida'
                                ))
                            removidas += 1
                        except CategoriaAnimal.DoesNotExist:
                            self.stdout.write(self.style.ERROR(
                                f'❌ Categoria correta "{nome_correto}" não encontrada. '
                                f'Não é possível migrar "{nome_incorreto}".'
                            ))
                            mantidas += 1
                    else:
                        self.stdout.write(self.style.WARNING(
                            f'⚠️  Categoria "{nome_incorreto}" está sendo usada '
                            f'({inventarios_count} inventários, {movimentacoes_count} movimentações). '
                            f'Não pode ser removida automaticamente.'
                        ))
                        mantidas += 1
                else:
                    if dry_run:
                        self.stdout.write(self.style.WARNING(
                            f'🔍 [DRY RUN] Categoria "{nome_incorreto}" seria removida (não está em uso)'
                        ))
                    else:
                        categoria.delete()
                        self.stdout.write(self.style.SUCCESS(
                            f'✅ Categoria removida: "{nome_incorreto}"'
                        ))
                    removidas += 1
                    
            except CategoriaAnimal.DoesNotExist:
                self.stdout.write(self.style.SUCCESS(
                    f'ℹ️  Categoria "{nome_incorreto}" não existe'
                ))
        
        # Verificar duplicatas reais (mesmo nome)
        self.stdout.write(self.style.SUCCESS('\n🔍 Verificando duplicatas por nome...\n'))
        
        from collections import Counter
        todas_categorias = CategoriaAnimal.objects.all()
        nomes = [c.nome for c in todas_categorias]
        contador = Counter(nomes)
        duplicados = {nome: count for nome, count in contador.items() if count > 1}
        
        if duplicados:
            for nome, count in duplicados.items():
                categorias_duplicadas = CategoriaAnimal.objects.filter(nome=nome).order_by('id')
                self.stdout.write(self.style.WARNING(
                    f'⚠️  Encontradas {count} categorias com nome "{nome}":'
                ))
                
                # Manter a primeira e remover as outras
                primeira = categorias_duplicadas.first()
                outras = categorias_duplicadas.exclude(id=primeira.id)
                
                for categoria in outras:
                    inventarios_count = InventarioRebanho.objects.filter(categoria=categoria).count()
                    movimentacoes_count = MovimentacaoProjetada.objects.filter(categoria=categoria).count()
                    
                    if inventarios_count > 0 or movimentacoes_count > 0:
                        self.stdout.write(self.style.WARNING(
                            f'   ⚠️  Categoria ID {categoria.id} está em uso, mantendo'
                        ))
                    else:
                        if dry_run:
                            self.stdout.write(self.style.WARNING(
                                f'   🔍 [DRY RUN] Categoria ID {categoria.id} seria removida'
                            ))
                        else:
                            categoria.delete()
                            self.stdout.write(self.style.SUCCESS(
                                f'   ✅ Categoria ID {categoria.id} removida'
                            ))
                        removidas += 1
        else:
            self.stdout.write(self.style.SUCCESS('✅ Nenhuma duplicata por nome encontrada'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n📊 Resumo: {removidas} removidas, {mantidas} mantidas (em uso)\n'
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                '⚠️  Modo DRY RUN - nenhuma categoria foi realmente removida'
            ))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Limpeza concluída!'))

