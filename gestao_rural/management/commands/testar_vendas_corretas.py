from django.core.management.base import BaseCommand
from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho,
    ParametrosProjecaoRebanho, MovimentacaoProjetada
)
from gestao_rural.views import gerar_projecao
from django.contrib.auth.models import User
from datetime import date


class Command(BaseCommand):
    help = 'Testa se as vendas estão sendo aplicadas corretamente apenas quando há saldo disponível'

    def handle(self, *args, **options):
        self.stdout.write('🧪 Testando lógica de vendas...\n')
        
        # Criar usuário de teste se não existir
        user, created = User.objects.get_or_create(
            username='teste_vendas',
            defaults={'email': 'teste@teste.com'}
        )
        
        # Criar produtor de teste
        produtor, created = ProdutorRural.objects.get_or_create(
            nome='Produtor Teste Vendas',
            defaults={
                'cpf_cnpj': '98765432101',
                'usuario_responsavel': user,
                'telefone': '11999999999'
            }
        )
        
        # Criar propriedade de teste
        propriedade, created = Propriedade.objects.get_or_create(
            nome_propriedade='Fazenda Teste Vendas',
            defaults={
                'produtor': produtor,
                'municipio': 'Teste',
                'uf': 'SP',
                'area_total_ha': 100.0,
                'tipo_operacao': 'PECUARIA',
                'tipo_ciclo_pecuario': ['CICLO_COMPLETO']
            }
        )
        
        # Limpar dados anteriores
        InventarioRebanho.objects.filter(propriedade=propriedade).delete()
        MovimentacaoProjetada.objects.filter(propriedade=propriedade).delete()
        ParametrosProjecaoRebanho.objects.filter(propriedade=propriedade).delete()
        
        # Criar parâmetros de teste com vendas altas para testar
        parametros = ParametrosProjecaoRebanho.objects.create(
            propriedade=propriedade,
            taxa_natalidade_anual=85.0,
            taxa_mortalidade_bezerros_anual=5.0,
            taxa_mortalidade_adultos_anual=2.0,
            percentual_venda_machos_anual=50.0,  # 50% de vendas para testar
            percentual_venda_femeas_anual=30.0,  # 30% de vendas para testar
            periodicidade='ANUAL'
        )
        
        # Criar inventário inicial APENAS com Bezerras e Bezerros (sem Novilhas)
        bezerras = CategoriaAnimal.objects.get(nome='Bezerras (0-12m)')
        bezerros = CategoriaAnimal.objects.get(nome='Bezerros (0-12m)')
        novilhas = CategoriaAnimal.objects.get(nome='Novilhas (12-24m)')
        
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
        
        # NÃO criar inventário para Novilhas (saldo = 0)
        
        self.stdout.write('📊 Inventário inicial criado:')
        self.stdout.write(f'  - Bezerras (0-12m): 50')
        self.stdout.write(f'  - Bezerros (0-12m): 30')
        self.stdout.write(f'  - Novilhas (12-24m): 0 (SEM SALDO)')
        
        # Gerar projeção para 2 anos
        self.stdout.write('\n🔄 Gerando projeção para 2 anos...')
        gerar_projecao(propriedade, 2)
        
        # Verificar movimentações geradas
        movimentacoes = MovimentacaoProjetada.objects.filter(propriedade=propriedade).order_by('data_movimentacao')
        
        self.stdout.write('\n📋 Movimentações geradas:')
        for mov in movimentacoes:
            self.stdout.write(f'  {mov.data_movimentacao} - {mov.tipo_movimentacao} - {mov.categoria.nome}: {mov.quantidade}')
        
        # Verificar se há vendas de Novilhas (que não deveria ter)
        vendas_novilhas = movimentacoes.filter(
            categoria=novilhas,
            tipo_movimentacao='VENDA'
        )
        
        self.stdout.write('\n🔍 Verificando vendas de Novilhas:')
        if vendas_novilhas.exists():
            self.stdout.write('  ❌ ERRO: Vendas de Novilhas encontradas mesmo sem saldo inicial!')
            for venda in vendas_novilhas:
                self.stdout.write(f'    - {venda.data_movimentacao}: {venda.quantidade} Novilhas vendidas')
        else:
            self.stdout.write('  ✅ CORRETO: Nenhuma venda de Novilhas (sem saldo inicial)')
        
        # Verificar vendas de categorias com saldo
        vendas_bezerras = movimentacoes.filter(
            categoria=bezerras,
            tipo_movimentacao='VENDA'
        )
        
        vendas_bezerros = movimentacoes.filter(
            categoria=bezerros,
            tipo_movimentacao='VENDA'
        )
        
        self.stdout.write('\n🔍 Verificando vendas de categorias com saldo:')
        if vendas_bezerras.exists():
            total_vendas_bezerras = sum(v.quantidade for v in vendas_bezerras)
            self.stdout.write(f'  ✅ Vendas de Bezerras: {total_vendas_bezerras} (com saldo inicial de 50)')
        else:
            self.stdout.write('  ℹ️ Nenhuma venda de Bezerras')
        
        if vendas_bezerros.exists():
            total_vendas_bezerros = sum(v.quantidade for v in vendas_bezerros)
            self.stdout.write(f'  ✅ Vendas de Bezerros: {total_vendas_bezerros} (com saldo inicial de 30)')
        else:
            self.stdout.write('  ℹ️ Nenhuma venda de Bezerros')
        
        self.stdout.write('\n✅ Teste concluído!')
        
        # Limpar dados de teste
        self.stdout.write('\n🧹 Limpando dados de teste...')
        propriedade.delete()
        produtor.delete()
        user.delete()

