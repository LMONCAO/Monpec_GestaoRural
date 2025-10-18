from django.core.management.base import BaseCommand
from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho,
    ParametrosProjecaoRebanho, MovimentacaoProjetada, RegraPromocaoCategoria
)
from gestao_rural.views import gerar_projecao
from django.contrib.auth.models import User
from datetime import date


class Command(BaseCommand):
    help = 'Testa a lógica de promoção de categorias'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Testando lógica de promoção...\n')
        
        # Criar usuário de teste se não existir
        user, created = User.objects.get_or_create(
            username='teste_promocao',
            defaults={'email': 'teste@teste.com'}
        )
        
        # Criar produtor de teste
        produtor, created = ProdutorRural.objects.get_or_create(
            nome='Produtor Teste',
            defaults={
                'cpf_cnpj': '12345678901',
                'usuario_responsavel': user,
                'telefone': '11999999999'
            }
        )
        
        # Criar propriedade de teste
        propriedade, created = Propriedade.objects.get_or_create(
            nome_propriedade='Fazenda Teste',
            defaults={
                'produtor': produtor,
                'municipio': 'Teste',
                'uf': 'SP',
                'area_total_ha': 100.0,
                'tipo_operacao': 'PECUARIA',
                'tipo_ciclo_pecuario': 'CICLO_COMPLETO'
            }
        )
        
        # Limpar dados anteriores
        InventarioRebanho.objects.filter(propriedade=propriedade).delete()
        MovimentacaoProjetada.objects.filter(propriedade=propriedade).delete()
        ParametrosProjecaoRebanho.objects.filter(propriedade=propriedade).delete()
        
        # Criar parâmetros de teste
        parametros = ParametrosProjecaoRebanho.objects.create(
            propriedade=propriedade,
            taxa_natalidade_anual=85.0,
            taxa_mortalidade_bezerros_anual=5.0,
            taxa_mortalidade_adultos_anual=2.0,
            percentual_venda_machos_anual=0.0,
            percentual_venda_femeas_anual=0.0,
            periodicidade='ANUAL'
        )
        
        # Criar inventário inicial
        bezerras = CategoriaAnimal.objects.get(nome='Bezerras (0-12m)')
        bezerros = CategoriaAnimal.objects.get(nome='Bezerros (0-12m)')
        
        InventarioRebanho.objects.create(
            propriedade=propriedade,
            categoria=bezerras,
            quantidade=50,
            data_inventario=date.today()
        )
        
        InventarioRebanho.objects.create(
            propriedade=propriedade,
            categoria=bezerros,
            quantidade=30,
            data_inventario=date.today()
        )
        
        self.stdout.write('📊 Inventário inicial criado:')
        self.stdout.write(f'  - Bezerras (0-12m): 50')
        self.stdout.write(f'  - Bezerros (0-12m): 30')
        
        # Gerar projeção para 3 anos
        self.stdout.write('\n🔄 Gerando projeção para 3 anos...')
        gerar_projecao(propriedade, 3)
        
        # Verificar movimentações geradas
        movimentacoes = MovimentacaoProjetada.objects.filter(propriedade=propriedade).order_by('data_movimentacao')
        
        self.stdout.write('\n📋 Movimentações geradas:')
        for mov in movimentacoes:
            self.stdout.write(f'  {mov.data_movimentacao} - {mov.tipo_movimentacao} - {mov.categoria.nome}: {mov.quantidade}')
        
        # Verificar se as promoções estão corretas
        self.stdout.write('\n🔍 Verificando promoções:')
        
        # Verificar promoção de Bezerras → Novilhas
        promocoes_bezerras = movimentacoes.filter(
            categoria=bezerras,
            tipo_movimentacao='TRANSFERENCIA_SAIDA'
        )
        if promocoes_bezerras.exists():
            total_bezerras_promovidas = sum(p.quantidade for p in promocoes_bezerras)
            self.stdout.write(f'  ✅ Bezerras promovidas: {total_bezerras_promovidas}')
        else:
            self.stdout.write('  ❌ Nenhuma promoção de Bezerras encontrada')
        
        # Verificar promoção de Bezerros → Garrotes
        promocoes_bezerros = movimentacoes.filter(
            categoria=bezerros,
            tipo_movimentacao='TRANSFERENCIA_SAIDA'
        )
        if promocoes_bezerros.exists():
            total_bezerros_promovidos = sum(p.quantidade for p in promocoes_bezerros)
            self.stdout.write(f'  ✅ Bezerros promovidos: {total_bezerros_promovidos}')
        else:
            self.stdout.write('  ❌ Nenhuma promoção de Bezerros encontrada')
        
        # Verificar se não há mistura de sexos
        self.stdout.write('\n🚫 Verificando separação por sexo:')
        
        # Verificar se Bezerras foram promovidas corretamente para Novilhas
        novilhas = CategoriaAnimal.objects.get(nome='Novilhas (12-24m)')
        garrotes = CategoriaAnimal.objects.get(nome='Garrotes (12-24m)')
        
        # Verificar promoção de Bezerras para Novilhas
        bezerras_para_novilhas = movimentacoes.filter(
            categoria=novilhas,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA'
        )
        
        if bezerras_para_novilhas.exists():
            total_bezerras_para_novilhas = sum(p.quantidade for p in bezerras_para_novilhas)
            self.stdout.write(f'  ✅ Bezerras promovidas para Novilhas: {total_bezerras_para_novilhas}')
        else:
            self.stdout.write('  ❌ Nenhuma Bezerra foi promovida para Novilhas')
        
        # Verificar promoção de Bezerros para Garrotes
        bezerros_para_garrotes = movimentacoes.filter(
            categoria=garrotes,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA'
        )
        
        if bezerros_para_garrotes.exists():
            total_bezerros_para_garrotes = sum(p.quantidade for p in bezerros_para_garrotes)
            self.stdout.write(f'  ✅ Bezerros promovidos para Garrotes: {total_bezerros_para_garrotes}')
        else:
            self.stdout.write('  ❌ Nenhum Bezerro foi promovido para Garrotes')
        
        # Verificar se não há mistura (Bezerras não foram para Garrotes)
        bezerras_para_garrotes_erro = movimentacoes.filter(
            categoria=garrotes,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            observacao__icontains='Bezerras'
        )
        
        if bezerras_para_garrotes_erro.exists():
            self.stdout.write('  ❌ ERRO: Bezerras foram promovidas para Garrotes!')
        else:
            self.stdout.write('  ✅ Bezerras não foram promovidas para categorias de machos')
        
        # Verificar se não há mistura (Bezerros não foram para Novilhas)
        bezerros_para_novilhas_erro = movimentacoes.filter(
            categoria=novilhas,
            tipo_movimentacao='TRANSFERENCIA_ENTRADA',
            observacao__icontains='Bezerros'
        )
        
        if bezerros_para_novilhas_erro.exists():
            self.stdout.write('  ❌ ERRO: Bezerros foram promovidos para Novilhas!')
        else:
            self.stdout.write('  ✅ Bezerros não foram promovidos para categorias de fêmeas')
        
        self.stdout.write('\n✅ Teste concluído!')
        
        # Limpar dados de teste
        self.stdout.write('\n🧹 Limpando dados de teste...')
        propriedade.delete()
        produtor.delete()
        user.delete()
