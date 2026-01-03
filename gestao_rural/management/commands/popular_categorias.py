from django.core.management.base import BaseCommand
from gestao_rural.models import CategoriaAnimal, RegraPromocaoCategoria


class Command(BaseCommand):
    help = 'Popula as categorias de animais e regras de promoção para gado de corte'

    def handle(self, *args, **options):
        self.stdout.write('Criando categorias de animais...')
        
        # Criar categorias de fêmeas
        categorias_femeas = [
            ('Bezerras (0-12m)', 'Fêmeas de 0 a 12 meses'),
            ('Novilhas (12-24m)', 'Fêmeas de 12 a 24 meses - Prontas para primeiro entoure'),
            ('Primíparas (24-36m)', 'Fêmeas de 24 a 36 meses - Vacas de primeira cria'),
            ('Multíparas (>36m)', 'Fêmeas acima de 36 meses - Vacas experientes'),
            ('Vacas de Descarte', 'Fêmeas selecionadas para descarte'),
        ]
        
        # Criar categorias de machos
        categorias_machos = [
            ('Bezerros (0-12m)', 'Machos de 0 a 12 meses'),
            ('Garrotes (12-24m)', 'Machos de 12 a 24 meses'),
            ('Bois Magros (24-36m)', 'Machos de 24 a 36 meses - Prontos para venda'),
            ('Touros', 'Machos reprodutores'),
        ]
        
        # Criar todas as categorias
        todas_categorias = categorias_femeas + categorias_machos
        
        for nome, descricao in todas_categorias:
            # Determinar sexo e raça baseado no nome
            if 'Fêmea' in nome or 'Bezerra' in nome or 'Novilha' in nome or 'Primípara' in nome or 'Multípara' in nome or 'Vaca' in nome:
                sexo = 'F'
            elif 'Macho' in nome or 'Bezerro' in nome or 'Garrotes' in nome or 'Bois' in nome or 'Touro' in nome:
                sexo = 'M'
            else:
                sexo = 'I'
            
            categoria, created = CategoriaAnimal.objects.get_or_create(
                nome=nome,
                defaults={
                    'descricao': descricao, 
                    'ativo': True,
                    'sexo': sexo,
                    'raca': 'NELORE'  # Raça padrão
                }
            )
            if created:
                self.stdout.write(f'✓ Criada categoria: {nome}')
            else:
                self.stdout.write(f'- Categoria já existe: {nome}')
        
        self.stdout.write('\nCriando regras de promoção...')
        
        # Regras de promoção para fêmeas
        regras_promocao = [
            # (categoria_origem, categoria_destino, idade_min, idade_max)
            ('Bezerras (0-12m)', 'Novilhas (12-24m)', 12, 12),
            ('Novilhas (12-24m)', 'Primíparas (24-36m)', 24, 24),
            ('Primíparas (24-36m)', 'Multíparas (>36m)', 36, 36),
        ]
        
        # Regras de promoção para machos
        regras_promocao.extend([
            ('Bezerros (0-12m)', 'Garrotes (12-24m)', 12, 12),
            ('Garrotes (12-24m)', 'Bois Magros (24-36m)', 24, 24),
        ])
        
        for origem, destino, idade_min, idade_max in regras_promocao:
            try:
                categoria_origem = CategoriaAnimal.objects.get(nome=origem)
                categoria_destino = CategoriaAnimal.objects.get(nome=destino)
                
                regra, created = RegraPromocaoCategoria.objects.get_or_create(
                    categoria_origem=categoria_origem,
                    categoria_destino=categoria_destino,
                    defaults={
                        'idade_minima_meses': idade_min,
                        'idade_maxima_meses': idade_max,
                        'ativo': True
                    }
                )
                
                if created:
                    self.stdout.write(f'✓ Criada regra: {origem} → {destino}')
                else:
                    self.stdout.write(f'- Regra já existe: {origem} → {destino}')
                    
            except CategoriaAnimal.DoesNotExist:
                self.stdout.write(f'✗ Erro: Categoria não encontrada para regra {origem} → {destino}')
        
        self.stdout.write('\n✓ Categorias e regras de promoção criadas com sucesso!')
