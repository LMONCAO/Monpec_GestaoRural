"""
Comando para popular o sistema com dados realistas do setor pecuário.

Baseado em dados de mercado 2024-2025:
- Preço arroba: R$ 280-320
- Margem de lucro: 15-25%
- Custo por cabeça: R$ 1.800-2.500
- Peso médio abate: 450-500 kg (15-16 arrobas)
- Taxa natalidade: 70-85%
- Taxa mortalidade: 2-4%
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import random
from django.contrib.auth import get_user_model

from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho,
    PlanejamentoAnual, AnimalIndividual, MovimentacaoProjetada,
)
from gestao_rural.models_financeiro import ContaFinanceira, MovimentoFinanceiro
from gestao_rural.models_operacional import CompraSuplementacao
from gestao_rural.models_patrimonio import BemPatrimonial
from gestao_rural.models_funcionarios import Funcionario, FolhaPagamento
from gestao_rural.models_controles_operacionais import Pastagem, Cocho

User = get_user_model()


class Command(BaseCommand):
    help = 'Popula o sistema com dados realistas do setor pecuário em todos os módulos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--produtor-id',
            type=int,
            help='ID do produtor (se não informado, usa o primeiro)',
        )
        parser.add_argument(
            '--propriedade-id',
            type=int,
            help='ID da propriedade (se não informado, usa a primeira)',
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Limpa dados existentes antes de popular',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('POPULANDO SISTEMA COM DADOS REALISTAS'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # Dados de mercado realistas (2024-2025)
        self.PRECO_ARROBA = Decimal('300.00')  # R$ 300/arroba
        self.PESO_MEDIO_ABATE = Decimal('480.00')  # 480 kg = 16 arrobas
        self.VALOR_MEDIO_CABECA = self.PRECO_ARROBA * (self.PESO_MEDIO_ABATE / Decimal('30'))
        self.CUSTO_POR_CABECA = Decimal('2200.00')  # R$ 2.200/cabeça/ano
        self.MARGEM_LUCRO = Decimal('0.20')  # 20% de margem
        
        # Obter ou criar produtor
        produtor = self.get_produtor(options.get('produtor_id'))
        propriedade = self.get_propriedade(produtor, options.get('propriedade_id'))
        
        if options.get('limpar'):
            self.limpar_dados(propriedade)
        
        # Popular dados em sequência lógica
        self.stdout.write('\n[1/10] Criando categorias de animais...')
        categorias, valores_por_categoria, categorias_data = self.criar_categorias(propriedade)
        
        self.stdout.write('[2/10] Criando inventário inicial...')
        inventario = self.criar_inventario_inicial(propriedade, categorias, valores_por_categoria, categorias_data)
        
        self.stdout.write('[3/10] Criando movimentações de rebanho...')
        self.criar_movimentacoes(propriedade, categorias, inventario, valores_por_categoria)
        
        self.stdout.write('[4/10] Criando planejamento anual...')
        planejamento = self.criar_planejamento(propriedade, categorias)
        
        self.stdout.write('[5/10] Criando dados financeiros...')
        self.criar_dados_financeiros(propriedade, planejamento)
        
        self.stdout.write('[6/10] Criando compras e suplementação...')
        self.criar_compras(propriedade)
        
        self.stdout.write('[7/10] Criando vendas...')
        self.criar_vendas(propriedade, categorias, valores_por_categoria)
        
        self.stdout.write('[8/10] Criando bens patrimoniais...')
        self.criar_bens_patrimoniais(propriedade)
        
        self.stdout.write('[9/10] Criando funcionários e folha de pagamento...')
        self.criar_funcionarios(propriedade)
        
        self.stdout.write('[10/10] Criando pastagens e cochos...')
        self.criar_pastagens_cochos(propriedade)
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ DADOS POPULADOS COM SUCESSO!'))
        self.stdout.write('=' * 60)
        self.stdout.write(f'\nPropriedade: {propriedade.nome_propriedade}')
        self.stdout.write(f'Total de animais: {sum(i.quantidade for i in inventario)} cabeças')
        self.stdout.write(f'Valor total do rebanho: R$ {sum(i.valor_total for i in inventario):,.2f}')

    def get_produtor(self, produtor_id):
        if produtor_id:
            return ProdutorRural.objects.get(id=produtor_id)
        produtor = ProdutorRural.objects.first()
        if not produtor:
            self.stdout.write(self.style.ERROR('Nenhum produtor encontrado!'))
            raise Exception('Crie um produtor primeiro')
        return produtor

    def get_propriedade(self, produtor, propriedade_id):
        if propriedade_id:
            return Propriedade.objects.get(id=propriedade_id, produtor=produtor)
        propriedade = Propriedade.objects.filter(produtor=produtor).first()
        if not propriedade:
            self.stdout.write(self.style.ERROR('Nenhuma propriedade encontrada!'))
            raise Exception('Crie uma propriedade primeiro')
        return propriedade

    def limpar_dados(self, propriedade):
        self.stdout.write(self.style.WARNING('Limpando dados existentes...'))
        # Não limpar tudo, apenas dados específicos se necessário
        pass

    def criar_categorias(self, propriedade):
        """Cria categorias realistas de animais"""
        categorias_data = [
            {'nome': 'Bezerros (0-12 meses)', 'tipo': 'MACHO', 'peso_medio': 150, 'valor_por_cabeca': 800},
            {'nome': 'Bezerras (0-12 meses)', 'tipo': 'FEMEA', 'peso_medio': 140, 'valor_por_cabeca': 750},
            {'nome': 'Garrote (12-24 meses)', 'tipo': 'MACHO', 'peso_medio': 320, 'valor_por_cabeca': 1800},
            {'nome': 'Novilhas (12-24 meses)', 'tipo': 'FEMEA', 'peso_medio': 300, 'valor_por_cabeca': 2000},
            {'nome': 'Bois (24-36 meses)', 'tipo': 'MACHO', 'peso_medio': 450, 'valor_por_cabeca': 4800},
            {'nome': 'Vacas Primíparas', 'tipo': 'FEMEA', 'peso_medio': 420, 'valor_por_cabeca': 4500},
            {'nome': 'Vacas Multíparas', 'tipo': 'FEMEA', 'peso_medio': 480, 'valor_por_cabeca': 5000},
            {'nome': 'Touros', 'tipo': 'MACHO', 'peso_medio': 650, 'valor_por_cabeca': 8000},
        ]
        
        categorias = []
        valores_por_categoria = {}  # Dicionário para mapear categoria -> valor_por_cabeca
        
        for cat_data in categorias_data:
            categoria, created = CategoriaAnimal.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={
                    'sexo': 'M' if cat_data['tipo'] == 'MACHO' else 'F',
                    'peso_medio_kg': Decimal(str(cat_data['peso_medio'])),
                }
            )
            categorias.append(categoria)
            valores_por_categoria[categoria.id] = Decimal(str(cat_data['valor_por_cabeca']))
        
        return categorias, valores_por_categoria, categorias_data

    def criar_inventario_inicial(self, propriedade, categorias, valores_por_categoria, categorias_data):
        """Cria inventário inicial realista"""
        data_inventario = timezone.now().date() - timedelta(days=30)
        
        # Distribuição realista de animais
        distribuicao = {
            'Bezerros (0-12 meses)': 45,
            'Bezerras (0-12 meses)': 42,
            'Garrote (12-24 meses)': 38,
            'Novilhas (12-24 meses)': 35,
            'Bois (24-36 meses)': 28,
            'Vacas Primíparas': 25,
            'Vacas Multíparas': 120,
            'Touros': 8,
        }
        
        inventario = []
        for categoria in categorias:
            quantidade = distribuicao.get(categoria.nome, 0)
            if quantidade > 0:
                valor_por_cabeca = valores_por_categoria.get(categoria.id, Decimal('0'))
                item = InventarioRebanho.objects.create(
                    propriedade=propriedade,
                    categoria=categoria,
                    data_inventario=data_inventario,
                    quantidade=quantidade,
                    valor_por_cabeca=valor_por_cabeca,
                )
                inventario.append(item)
        
        return inventario

    def criar_movimentacoes(self, propriedade, categorias, inventario, valores_por_categoria):
        """Cria movimentações realistas nos últimos 12 meses"""
        hoje = timezone.now().date()
        
        # Criar movimentações mensais
        for mes in range(12, 0, -1):
            data = hoje - timedelta(days=30 * mes)
            
            # Nascimentos (taxa de natalidade 75%)
            vacas_reprodutoras = sum(
                i.quantidade for i in inventario 
                if 'Vaca' in i.categoria.nome
            )
            nascimentos = int(vacas_reprodutoras * 0.75 / 12)
            
            if nascimentos > 0:
                # 50% machos, 50% fêmeas
                bezerros_cat = next((c for c in categorias if 'Bezerros' in c.nome), None)
                bezerras_cat = next((c for c in categorias if 'Bezerras' in c.nome), None)
                
                if bezerros_cat:
                    valor_por_cabeca = valores_por_categoria.get(bezerros_cat.id, Decimal('0'))
                    quantidade = nascimentos // 2
                    MovimentacaoProjetada.objects.create(
                        propriedade=propriedade,
                        categoria=bezerros_cat,
                        tipo_movimentacao='NASCIMENTO',
                        data_movimentacao=data,
                        quantidade=quantidade,
                        valor_por_cabeca=valor_por_cabeca,
                        valor_total=quantidade * valor_por_cabeca,
                    )
                
                if bezerras_cat:
                    valor_por_cabeca = valores_por_categoria.get(bezerras_cat.id, Decimal('0'))
                    quantidade = nascimentos - (nascimentos // 2)
                    MovimentacaoProjetada.objects.create(
                        propriedade=propriedade,
                        categoria=bezerras_cat,
                        tipo_movimentacao='NASCIMENTO',
                        data_movimentacao=data,
                        quantidade=quantidade,
                        valor_por_cabeca=valor_por_cabeca,
                        valor_total=quantidade * valor_por_cabeca,
                    )
            
            # Mortes (taxa de mortalidade 3%)
            total_animais = sum(i.quantidade for i in inventario)
            mortes = max(1, int(total_animais * 0.03 / 12))
            
            if mortes > 0:
                categoria_morte = random.choice(categorias)
                valor_por_cabeca = valores_por_categoria.get(categoria_morte.id, Decimal('0'))
                MovimentacaoProjetada.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_morte,
                    tipo_movimentacao='MORTE',
                    data_movimentacao=data,
                    quantidade=mortes,
                    valor_por_cabeca=valor_por_cabeca,
                    valor_total=mortes * valor_por_cabeca,
                )

    def criar_planejamento(self, propriedade, categorias):
        """Cria planejamento anual com projeções realistas"""
        ano = timezone.now().year
        
        planejamento, created = PlanejamentoAnual.objects.get_or_create(
            propriedade=propriedade,
            ano=ano,
            defaults={
                'taxa_natalidade': Decimal('75.00'),
                'taxa_mortalidade': Decimal('3.00'),
                'percentual_venda_machos_anual': Decimal('80.00'),
                'percentual_venda_femeas_anual': Decimal('15.00'),
            }
        )
        
        return planejamento

    def criar_dados_financeiros(self, propriedade, planejamento):
        """Cria dados financeiros realistas"""
        hoje = timezone.now().date()
        
        # Criar conta financeira principal
        conta, _ = ContaFinanceira.objects.get_or_create(
            propriedade=propriedade,
            nome='Conta Principal',
            defaults={
                'tipo': 'CORRENTE',
                'saldo_inicial': Decimal('50000.00'),
            }
        )
        
        # Receitas mensais (vendas de animais)
        for mes in range(12, 0, -1):
            data = hoje - timedelta(days=30 * mes)
            
            # Vendas mensais (15-20 cabeças/mês)
            quantidade_vendas = random.randint(15, 20)
            valor_venda = quantidade_vendas * self.VALOR_MEDIO_CABECA
            
            MovimentoFinanceiro.objects.create(
                propriedade=propriedade,
                conta=conta,
                tipo='RECEITA',
                categoria='Vendas de Animais',
                data=data,
                valor=valor_venda,
                descricao=f'Venda de {quantidade_vendas} cabeças',
            )
        
        # Despesas mensais
        despesas_mensais = {
            'Alimentação': Decimal('15000.00'),
            'Sanidade': Decimal('5000.00'),
            'Mão de Obra': Decimal('12000.00'),
            'Energia e Combustível': Decimal('3000.00'),
            'Manutenção': Decimal('4000.00'),
            'Impostos e Taxas': Decimal('2000.00'),
        }
        
        for mes in range(12, 0, -1):
            data = hoje - timedelta(days=30 * mes)
            
            for categoria, valor in despesas_mensais.items():
                # Variação de ±10%
                valor_var = valor * Decimal(str(random.uniform(0.9, 1.1)))
                
                MovimentoFinanceiro.objects.create(
                    propriedade=propriedade,
                    conta=conta,
                    tipo='DESPESA',
                    categoria=categoria,
                    data=data,
                    valor=valor_var,
                    descricao=f'{categoria} - {data.strftime("%m/%Y")}',
                )

    def criar_compras(self, propriedade):
        """Cria compras de suplementação realistas"""
        hoje = timezone.now().date()
        
        tipos_suplementacao = [
            {'nome': 'Sal Mineral', 'unidade': 'KG', 'preco_unitario': Decimal('3.50')},
            {'nome': 'Ração Concentrada', 'unidade': 'KG', 'preco_unitario': Decimal('2.80')},
            {'nome': 'Silagem', 'unidade': 'TON', 'preco_unitario': Decimal('180.00')},
            {'nome': 'Feno', 'unidade': 'FARDO', 'preco_unitario': Decimal('25.00')},
        ]
        
        for mes in range(6, 0, -1):
            data = hoje - timedelta(days=30 * mes)
            
            for suplemento in tipos_suplementacao:
                quantidade = random.randint(100, 500) if suplemento['unidade'] == 'KG' else random.randint(10, 50)
                
                CompraSuplementacao.objects.create(
                    propriedade=propriedade,
                    tipo_suplementacao=suplemento['nome'],
                    data=data,
                    quantidade=quantidade,
                    unidade=suplemento['unidade'],
                    valor_unitario=suplemento['preco_unitario'],
                    valor_total=quantidade * suplemento['preco_unitario'],
                )

    def criar_vendas(self, propriedade, categorias, valores_por_categoria):
        """Cria vendas realistas através de movimentações"""
        hoje = timezone.now().date()
        
        # Vendas mensais através de MovimentacaoRebanho
        for mes in range(12, 0, -1):
            data = hoje - timedelta(days=30 * mes)
            
            # Vender principalmente bois e garrotes
            categoria_venda = next((c for c in categorias if 'Bois' in c.nome or 'Garrote' in c.nome), None)
            
            if categoria_venda:
                quantidade = random.randint(10, 20)
                valor_por_cabeca = valores_por_categoria.get(categoria_venda.id, self.VALOR_MEDIO_CABECA)
                
                MovimentacaoProjetada.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_venda,
                    tipo_movimentacao='VENDA',
                    data_movimentacao=data,
                    quantidade=quantidade,
                    valor_por_cabeca=valor_por_cabeca,
                    valor_total=quantidade * valor_por_cabeca,
                )

    def criar_bens_patrimoniais(self, propriedade):
        """Cria bens patrimoniais realistas"""
        bens = [
            {'nome': 'Trator John Deere 6110J', 'valor': Decimal('350000.00'), 'depreciacao': Decimal('10.00')},
            {'nome': 'Pulverizador', 'valor': Decimal('45000.00'), 'depreciacao': Decimal('15.00')},
            {'nome': 'Caminhão Ford F-3500', 'valor': Decimal('180000.00'), 'depreciacao': Decimal('12.00')},
            {'nome': 'Balança Eletrônica', 'valor': Decimal('25000.00'), 'depreciacao': Decimal('10.00')},
            {'nome': 'Bebedouros Automáticos', 'valor': Decimal('15000.00'), 'depreciacao': Decimal('8.00')},
        ]
        
        for bem_data in bens:
            BemPatrimonial.objects.create(
                propriedade=propriedade,
                nome=bem_data['nome'],
                data_aquisicao=timezone.now().date() - timedelta(days=random.randint(30, 1095)),
                valor_aquisicao=bem_data['valor'],
                taxa_depreciacao_anual=bem_data['depreciacao'],
            )

    def criar_funcionarios(self, propriedade):
        """Cria funcionários e folha de pagamento"""
        cargos = [
            {'nome': 'Gerente de Fazenda', 'salario': Decimal('8000.00')},
            {'nome': 'Vaqueiro', 'salario': Decimal('3500.00')},
            {'nome': 'Tratorista', 'salario': Decimal('4500.00')},
            {'nome': 'Auxiliar de Campo', 'salario': Decimal('2500.00')},
        ]
        
        funcionarios = []
        for cargo_data in cargos:
            funcionario = Funcionario.objects.create(
                propriedade=propriedade,
                nome=f'Funcionário {cargo_data["nome"]}',
                cargo=cargo_data['nome'],
                data_admissao=timezone.now().date() - timedelta(days=random.randint(180, 1095)),
                salario_base=cargo_data['salario'],
            )
            funcionarios.append(funcionario)
        
        # Criar folha de pagamento dos últimos 6 meses
        hoje = timezone.now().date()
        for mes in range(6, 0, -1):
            data = hoje - timedelta(days=30 * mes)
            
            for funcionario in funcionarios:
                FolhaPagamento.objects.create(
                    propriedade=propriedade,
                    funcionario=funcionario,
                    mes_referencia=data.month,
                    ano_referencia=data.year,
                    salario_bruto=funcionario.salario_base,
                    total_descontos=funcionario.salario_base * Decimal('0.15'),
                    salario_liquido=funcionario.salario_base * Decimal('0.85'),
                )

    def criar_pastagens_cochos(self, propriedade):
        """Cria pastagens e cochos"""
        # Criar pastagens
        pastagens = [
            {'nome': 'Pastagem 1 - Capim Braquiária', 'area_hectares': Decimal('50.00')},
            {'nome': 'Pastagem 2 - Capim Panicum', 'area_hectares': Decimal('45.00')},
            {'nome': 'Pastagem 3 - Capim Tifton', 'area_hectares': Decimal('40.00')},
        ]
        
        pastagens_criadas = []
        for pasto_data in pastagens:
            pastagem = Pastagem.objects.create(
                propriedade=propriedade,
                nome=pasto_data['nome'],
                area_hectares=pasto_data['area_hectares'],
            )
            pastagens_criadas.append(pastagem)
        
        # Criar cochos
        tipos_cochos = ['SAL', 'RACAO', 'AGUA', 'MISTO']
        
        for pastagem in pastagens_criadas:
            for i, tipo in enumerate(tipos_cochos):
                Cocho.objects.create(
                    propriedade=propriedade,
                    pastagem=pastagem,
                    nome=f'Cocho {tipo} - {pastagem.nome}',
                    tipo_cocho=tipo,
                    capacidade=Decimal('500.00') if tipo == 'AGUA' else Decimal('1000.00'),
                    unidade_capacidade='L' if tipo == 'AGUA' else 'KG',
                    status='ATIVO',
                )

