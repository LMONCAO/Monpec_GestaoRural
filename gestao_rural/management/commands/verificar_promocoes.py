from django.core.management.base import BaseCommand
from gestao_rural.models import RegraPromocaoCategoria, CategoriaAnimal


class Command(BaseCommand):
    help = 'Verifica as regras de promoção de categorias'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Verificando regras de promoção...\n')
        
        # Listar todas as categorias
        self.stdout.write('📋 Categorias disponíveis:')
        categorias = CategoriaAnimal.objects.all().order_by('nome')
        for categoria in categorias:
            self.stdout.write(f'  - {categoria.nome} (ID: {categoria.id})')
        
        self.stdout.write('\n📊 Regras de promoção ativas:')
        regras = RegraPromocaoCategoria.objects.filter(ativo=True).order_by('categoria_origem__nome')
        
        if not regras.exists():
            self.stdout.write('  ❌ Nenhuma regra encontrada!')
            return
        
        for regra in regras:
            self.stdout.write(f'  ✅ {regra.categoria_origem.nome} → {regra.categoria_destino.nome} (Idade: {regra.idade_minima_meses}-{regra.idade_maxima_meses}m)')
        
        # Verificar se há regras duplicadas
        self.stdout.write('\n🔍 Verificando duplicatas...')
        origens = regras.values_list('categoria_origem', flat=True)
        duplicatas = []
        for origem in origens:
            count = regras.filter(categoria_origem_id=origem).count()
            if count > 1:
                duplicatas.append(origem)
        
        if duplicatas:
            self.stdout.write('  ❌ Duplicatas encontradas:')
            for origem_id in duplicatas:
                origem = CategoriaAnimal.objects.get(id=origem_id)
                self.stdout.write(f'    - {origem.nome} tem múltiplas regras de promoção')
        else:
            self.stdout.write('  ✅ Nenhuma duplicata encontrada')
        
        # Verificar fluxo de promoção
        self.stdout.write('\n🔄 Verificando fluxo de promoção:')
        
        # Fêmeas
        self.stdout.write('  👩 Fêmeas:')
        try:
            bezerras = CategoriaAnimal.objects.get(nome='Bezerras (0-12m)')
            novilhas = CategoriaAnimal.objects.get(nome='Novilhas (12-24m)')
            primiparas = CategoriaAnimal.objects.get(nome='Primíparas (24-36m)')
            multiparas = CategoriaAnimal.objects.get(nome='Multíparas (>36m)')
            
            # Verificar se existe regra Bezerras → Novilhas
            if RegraPromocaoCategoria.objects.filter(categoria_origem=bezerras, categoria_destino=novilhas, ativo=True).exists():
                self.stdout.write('    ✅ Bezerras → Novilhas')
            else:
                self.stdout.write('    ❌ Bezerras → Novilhas (FALTANDO)')
            
            # Verificar se existe regra Novilhas → Primíparas
            if RegraPromocaoCategoria.objects.filter(categoria_origem=novilhas, categoria_destino=primiparas, ativo=True).exists():
                self.stdout.write('    ✅ Novilhas → Primíparas')
            else:
                self.stdout.write('    ❌ Novilhas → Primíparas (FALTANDO)')
            
            # Verificar se existe regra Primíparas → Multíparas
            if RegraPromocaoCategoria.objects.filter(categoria_origem=primiparas, categoria_destino=multiparas, ativo=True).exists():
                self.stdout.write('    ✅ Primíparas → Multíparas')
            else:
                self.stdout.write('    ❌ Primíparas → Multíparas (FALTANDO)')
                
        except CategoriaAnimal.DoesNotExist as e:
            self.stdout.write(f'    ❌ Categoria não encontrada: {e}')
        
        # Machos
        self.stdout.write('  👨 Machos:')
        try:
            bezerros = CategoriaAnimal.objects.get(nome='Bezerros (0-12m)')
            garrotes = CategoriaAnimal.objects.get(nome='Garrotes (12-24m)')
            bois_magros = CategoriaAnimal.objects.get(nome='Bois Magros (24-36m)')
            
            # Verificar se existe regra Bezerros → Garrotes
            if RegraPromocaoCategoria.objects.filter(categoria_origem=bezerros, categoria_destino=garrotes, ativo=True).exists():
                self.stdout.write('    ✅ Bezerros → Garrotes')
            else:
                self.stdout.write('    ❌ Bezerros → Garrotes (FALTANDO)')
            
            # Verificar se existe regra Garrotes → Bois Magros
            if RegraPromocaoCategoria.objects.filter(categoria_origem=garrotes, categoria_destino=bois_magros, ativo=True).exists():
                self.stdout.write('    ✅ Garrotes → Bois Magros')
            else:
                self.stdout.write('    ❌ Garrotes → Bois Magros (FALTANDO)')
                
        except CategoriaAnimal.DoesNotExist as e:
            self.stdout.write(f'    ❌ Categoria não encontrada: {e}')
        
        self.stdout.write('\n✅ Verificação concluída!')

