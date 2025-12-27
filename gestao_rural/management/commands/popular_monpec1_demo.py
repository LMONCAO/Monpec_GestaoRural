# -*- coding: utf-8 -*-
"""
Comando para popular a propriedade Monpec1 com dados realistas de pecuária
para demonstração do sistema
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Importar todos os modelos
from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho,
    ParametrosProjecaoRebanho, MovimentacaoProjetada, CustoFixo, CustoVariavel,
    Financiamento, IndicadorFinanceiro, AnimalIndividual,
    MovimentacaoIndividual, BrincoAnimal, FluxoCaixa, ProjetoBancario,
    PlanejamentoAnual, CenarioPlanejamento
)

# Importar modelos de outros módulos
try:
    from gestao_rural.models_reproducao import (
        Touro, EstacaoMonta, IATF, MontaNatural, Nascimento
    )
except ImportError:
    Touro = EstacaoMonta = IATF = MontaNatural = Nascimento = None

try:
    from gestao_rural.models_operacional import (
        TanqueCombustivel, AbastecimentoCombustivel, ConsumoCombustivel,
        EstoqueSuplementacao, CompraSuplementacao, DistribuicaoSuplementacao,
        Empreiteiro, ServicoEmpreiteiro, Equipamento, ManutencaoEquipamento
    )
except ImportError:
    TanqueCombustivel = AbastecimentoCombustivel = ConsumoCombustivel = None
    EstoqueSuplementacao = CompraSuplementacao = DistribuicaoSuplementacao = None
    Empreiteiro = ServicoEmpreiteiro = Equipamento = ManutencaoEquipamento = None

try:
    from gestao_rural.models_funcionarios import (
        Funcionario, FolhaPagamento, Holerite
    )
except ImportError:
    Funcionario = FolhaPagamento = Holerite = None

try:
    from gestao_rural.models_compras_financeiro import (
        Fornecedor, OrdemCompra, NotaFiscal, ContaPagar, ContaReceber
    )
except ImportError:
    Fornecedor = OrdemCompra = NotaFiscal = ContaPagar = ContaReceber = None

try:
    from gestao_rural.models_controles_operacionais import (
        Pastagem, RotacaoPastagem, MonitoramentoPastagem
    )
except ImportError:
    Pastagem = RotacaoPastagem = MonitoramentoPastagem = None

try:
    from gestao_rural.models_patrimonio import (
        TipoBem, BemPatrimonial
    )
except ImportError:
    TipoBem = BemPatrimonial = None

try:
    from gestao_rural.models_financeiro import (
        LancamentoFinanceiro, CategoriaFinanceira
    )
except ImportError:
    LancamentoFinanceiro = CategoriaFinanceira = None


class Command(BaseCommand):
    help = 'Popula a propriedade Monpec1 com dados realistas de pecuária para demonstração'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forçar recriação mesmo se já existirem dados',
        )
        parser.add_argument(
            '--propriedade-id',
            type=int,
            help='ID da propriedade a popular (se não informado, busca propriedade Monpec do usuário demo)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando popularização da Monpec1...'))
        
        propriedade_id = options.get('propriedade_id')
        
        if propriedade_id:
            # Se foi passado propriedade_id, usar essa propriedade
            try:
                propriedade = Propriedade.objects.get(pk=propriedade_id)
                self.stdout.write(self.style.SUCCESS(f'✅ Usando propriedade: {propriedade.nome_propriedade} (ID: {propriedade.id})'))
            except Propriedade.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Propriedade {propriedade_id} não encontrada!'))
                return
        else:
            # Buscar ou criar propriedade Monpec1 (comportamento padrão)
            # Primeiro, buscar ou criar produtor demo
            demo_user = User.objects.filter(username__in=['demo', 'demo_monpec']).first()
            if not demo_user:
                # Criar usuário demo se não existir
                demo_user = User.objects.create_user(
                    username='demo_monpec',
                    email='demo@monpec.com.br',
                    password='demo123',
                    first_name='Demo',
                    last_name='Monpec'
                )
            
            produtor = ProdutorRural.objects.filter(usuario_responsavel=demo_user).first()
            if not produtor:
                produtor = ProdutorRural.objects.create(
                    nome='Fazenda Monpec Demo',
                    cpf_cnpj='00.000.000/0001-00',
                    usuario_responsavel=demo_user,
                    email='demo@monpec.com.br',
                    telefone='(67) 99999-9999',
                    endereco='Campo Grande, MS'
                )
            
            # Buscar propriedade Monpec1 para este produtor específico
            propriedade = Propriedade.objects.filter(
                produtor=produtor,
                nome_propriedade__iregex=r'^Monpec\d+$'
            ).order_by('nome_propriedade').first()
        
            if not propriedade:
                self.stdout.write(self.style.ERROR('❌ Propriedade Monpec não encontrada para este produtor!'))
                self.stdout.write(self.style.WARNING('💡 Criando propriedade Monpec1...'))
                
                propriedade = Propriedade.objects.create(
                    produtor=produtor,
                    nome_propriedade='Monpec1',
                    municipio='Campo Grande',
                    uf='MS',
                    area_total_ha=Decimal('5000.00'),
                    tipo_operacao='PECUARIA',
                    tipo_ciclo_pecuario=['CICLO_COMPLETO'],
                    tipo_propriedade='PROPRIA',
                    valor_hectare_proprio=Decimal('12000.00'),
                )
        
        self.stdout.write(self.style.SUCCESS(f'✅ Propriedade encontrada: {propriedade.nome_propriedade} (ID: {propriedade.id})'))
        
        # Verificar se já existem dados
        if not options['force']:
            if InventarioRebanho.objects.filter(propriedade=propriedade).exists():
                self.stdout.write(self.style.WARNING('⚠️  Já existem dados na Monpec1. Use --force para recriar.'))
                return
        
        # Limpar dados existentes se force
        if options['force']:
            self.stdout.write(self.style.WARNING('🗑️  Limpando dados existentes...'))
            InventarioRebanho.objects.filter(propriedade=propriedade).delete()
            if AnimalIndividual:
                AnimalIndividual.objects.filter(propriedade=propriedade).delete()
            if MovimentacaoIndividual:
                MovimentacaoIndividual.objects.filter(propriedade=propriedade).delete()
        
        # 1. Criar categorias de animais
        self.stdout.write(self.style.SUCCESS('📋 Criando categorias de animais...'))
        categorias_data = [
            {'nome': 'Vacas em Lactação', 'sexo': 'F', 'idade_minima_meses': 24, 'peso_medio_kg': Decimal('450.00')},
            {'nome': 'Vacas Secas', 'sexo': 'F', 'idade_minima_meses': 24, 'peso_medio_kg': Decimal('450.00')},
            {'nome': 'Novilhas', 'sexo': 'F', 'idade_minima_meses': 12, 'peso_medio_kg': Decimal('280.00')},
            {'nome': 'Bezerras', 'sexo': 'F', 'idade_minima_meses': 0, 'peso_medio_kg': Decimal('35.00')},
            {'nome': 'Touros', 'sexo': 'M', 'idade_minima_meses': 24, 'peso_medio_kg': Decimal('650.00')},
            {'nome': 'Bezerros', 'sexo': 'M', 'idade_minima_meses': 0, 'peso_medio_kg': Decimal('38.00')},
            {'nome': 'Bois', 'sexo': 'M', 'idade_minima_meses': 12, 'peso_medio_kg': Decimal('400.00')},
        ]
        
        categorias = {}
        for cat_data in categorias_data:
            # CategoriaAnimal não tem campo propriedade, apenas nome (que é unique)
            categoria, created = CategoriaAnimal.objects.get_or_create(
                nome=cat_data['nome'],
                defaults={
                    'sexo': cat_data['sexo'],  # 'F' para Fêmea, 'M' para Macho
                    'idade_minima_meses': cat_data['idade_minima_meses'],
                    'peso_medio_kg': cat_data['peso_medio_kg'],
                }
            )
            categorias[cat_data['nome']] = categoria
            if created:
                self.stdout.write(f'  ✓ {categoria.nome}')
        
        # 2. Criar inventário de rebanho
        self.stdout.write(self.style.SUCCESS('🐄 Criando inventário de rebanho...'))
        inventario_data = [
            {'categoria': 'Vacas em Lactação', 'quantidade': 850},
            {'categoria': 'Vacas Secas', 'quantidade': 150},
            {'categoria': 'Novilhas', 'quantidade': 320},
            {'categoria': 'Bezerras', 'quantidade': 280},
            {'categoria': 'Touros', 'quantidade': 25},
            {'categoria': 'Bezerros', 'quantidade': 310},
            {'categoria': 'Bois', 'quantidade': 450},
        ]
        
        for inv_data in inventario_data:
            InventarioRebanho.objects.create(
                propriedade=propriedade,
                categoria=categorias[inv_data['categoria']],
                quantidade=inv_data['quantidade'],
                data_inventario=date.today(),
            )
            self.stdout.write(f'  ✓ {inv_data["categoria"]}: {inv_data["quantidade"]} cabeças')
        
        # 3. Criar animais individuais (amostra)
        if AnimalIndividual:
            self.stdout.write(self.style.SUCCESS('🆔 Criando animais individuais (amostra)...'))
            vacas_lactacao = categorias['Vacas em Lactação']
            for i in range(1, 51):  # 50 animais de exemplo
                brinco = f'MONPEC1-{str(i).zfill(4)}'
                AnimalIndividual.objects.create(
                    propriedade=propriedade,
                    categoria=vacas_lactacao,
                    brinco=brinco,
                    nome=f'Vaca {i}',
                    data_nascimento=date.today() - timedelta(days=random.randint(730, 2555)),  # 2-7 anos
                    sexo='FEMEA',
                    peso_atual=Decimal(str(random.randint(400, 500))),
                    status='ATIVO',
                )
            self.stdout.write(f'  ✓ 50 animais individuais criados')
        
        # 4. Criar touros
        if Touro:
            self.stdout.write(self.style.SUCCESS('🐂 Criando touros...'))
            for i in range(1, 6):
                Touro.objects.create(
                    propriedade=propriedade,
                    nome=f'Touro {i}',
                    raca='NELORE',
                    data_nascimento=date.today() - timedelta(days=random.randint(1095, 2555)),
                    peso=Decimal(str(random.randint(600, 700))),
                    status='ATIVO',
                )
            self.stdout.write(f'  ✓ 5 touros criados')
        
        # 5. Criar estações de monta
        if EstacaoMonta:
            self.stdout.write(self.style.SUCCESS('📅 Criando estações de monta...'))
            estacao = EstacaoMonta.objects.create(
                propriedade=propriedade,
                nome='Estação de Monta 2025',
                data_inicio=date(2025, 1, 15),
                data_fim=date(2025, 4, 15),
                tipo='IATF',
            )
            self.stdout.write(f'  ✓ Estação de monta criada')
        
        # 6. Criar IATFs
        if IATF:
            self.stdout.write(self.style.SUCCESS('💉 Criando procedimentos IATF...'))
            for i in range(1, 21):
                IATF.objects.create(
                    propriedade=propriedade,
                    animal=AnimalIndividual.objects.filter(propriedade=propriedade, sexo='FEMEA').first() if AnimalIndividual else None,
                    data_procedimento=date.today() - timedelta(days=random.randint(1, 90)),
                    veterinario=f'Dr. Veterinário {i % 3 + 1}',
                    protocolo='PROTOCOLO_5_DIAS',
                    status='CONCLUIDO',
                )
            self.stdout.write(f'  ✓ 20 procedimentos IATF criados')
        
        # 7. Criar nascimentos
        if Nascimento:
            self.stdout.write(self.style.SUCCESS('👶 Criando nascimentos...'))
            for i in range(1, 31):
                Nascimento.objects.create(
                    propriedade=propriedade,
                    mae=AnimalIndividual.objects.filter(propriedade=propriedade, sexo='FEMEA').first() if AnimalIndividual else None,
                    data_nascimento=date.today() - timedelta(days=random.randint(1, 180)),
                    sexo=random.choice(['MACHO', 'FEMEA']),
                    peso_nascimento=Decimal(str(random.randint(30, 45))),
                    tipo_parto=random.choice(['NORMAL', 'CESAREA']),
                )
            self.stdout.write(f'  ✓ 30 nascimentos criados')
        
        # 8. Criar tanques de combustível
        if TanqueCombustivel:
            self.stdout.write(self.style.SUCCESS('⛽ Criando tanques de combustível...'))
            tanque = TanqueCombustivel.objects.create(
                propriedade=propriedade,
                nome='Tanque Principal',
                capacidade_litros=Decimal('10000.00'),
                estoque_atual=Decimal('7500.00'),
                estoque_minimo=Decimal('2000.00'),
                localizacao='Sede da Fazenda',
            )
            self.stdout.write(f'  ✓ Tanque de combustível criado')
            
            # Criar abastecimentos
            if AbastecimentoCombustivel:
                for i in range(1, 13):  # 12 meses
                    AbastecimentoCombustivel.objects.create(
                        propriedade=propriedade,
                        tanque=tanque,
                        tipo='COMPRA',
                        data=date(2025, i, 15) if i <= date.today().month else date(2024, i, 15),
                        fornecedor='Posto Combustível Central',
                        quantidade_litros=Decimal('5000.00'),
                        preco_unitario=Decimal('5.80'),
                        valor_total=Decimal('29000.00'),
                    )
                self.stdout.write(f'  ✓ 12 abastecimentos criados')
        
        # 9. Criar estoque de suplementação
        if EstoqueSuplementacao:
            self.stdout.write(self.style.SUCCESS('🌾 Criando estoque de suplementação...'))
            suplementos = [
                {'nome': 'Sal Mineral', 'unidade': 'KG', 'quantidade': Decimal('5000.00')},
                {'nome': 'Ração Concentrada', 'unidade': 'KG', 'quantidade': Decimal('10000.00')},
                {'nome': 'Silagem de Milho', 'unidade': 'TONELADA', 'quantidade': Decimal('200.00')},
            ]
            
            for sup in suplementos:
                EstoqueSuplementacao.objects.create(
                    propriedade=propriedade,
                    nome=sup['nome'],
                    unidade_medida=sup['unidade'],
                    quantidade_atual=sup['quantidade'],
                    estoque_minimo=sup['quantidade'] * Decimal('0.3'),
                )
            self.stdout.write(f'  ✓ 3 tipos de suplementação criados')
        
        # 10. Criar parâmetros de projeção (necessário para gerar projeções)
        self.stdout.write(self.style.SUCCESS('⚙️  Criando parâmetros de projeção...'))
        parametros_projecao, created = ParametrosProjecaoRebanho.objects.get_or_create(
            propriedade=propriedade,
            defaults={
                'taxa_natalidade_anual': Decimal('85.00'),
                'taxa_mortalidade_bezerros_anual': Decimal('5.00'),
                'taxa_mortalidade_adultos_anual': Decimal('2.00'),
                'percentual_venda_machos_anual': Decimal('90.00'),
                'percentual_venda_femeas_anual': Decimal('10.00'),
                'periodicidade': 'MENSAL',
            }
        )
        if created:
            self.stdout.write(f'  ✓ Parâmetros de projeção criados')
        else:
            self.stdout.write(f'  ✓ Parâmetros de projeção já existiam')
        
        # 11. Criar funcionários
        if Funcionario:
            self.stdout.write(self.style.SUCCESS('👷 Criando funcionários...'))
            funcionarios_data = [
                {'nome': 'João Silva', 'cargo': 'Gerente de Fazenda', 'salario': Decimal('8000.00')},
                {'nome': 'Maria Santos', 'cargo': 'Veterinária', 'salario': Decimal('12000.00')},
                {'nome': 'Pedro Oliveira', 'cargo': 'Capataz', 'salario': Decimal('5000.00')},
                {'nome': 'Ana Costa', 'cargo': 'Ordenhadeira', 'salario': Decimal('2500.00')},
                {'nome': 'Carlos Souza', 'cargo': 'Peão', 'salario': Decimal('2000.00')},
            ]
            
            for func_data in funcionarios_data:
                Funcionario.objects.create(
                    propriedade=propriedade,
                    nome=func_data['nome'],
                    cargo=func_data['cargo'],
                    salario_base=func_data['salario'],
                    data_admissao=date.today() - timedelta(days=random.randint(365, 1825)),
                    status='ATIVO',
                )
            self.stdout.write(f'  ✓ {len(funcionarios_data)} funcionários criados')
        
        # 11. Criar fornecedores
        if Fornecedor:
            self.stdout.write(self.style.SUCCESS('🏪 Criando fornecedores...'))
            fornecedores_data = [
                {'nome': 'Agropecuária Central', 'tipo': 'REVENDA'},
                {'nome': 'Cooperativa Rural MS', 'tipo': 'COOPERATIVA'},
                {'nome': 'Frigorífico Sul', 'tipo': 'FRIGORIFICO'},
                {'nome': 'Farmácia Veterinária', 'tipo': 'FARMACIA'},
            ]
            
            for forn_data in fornecedores_data:
                Fornecedor.objects.create(
                    propriedade=propriedade,
                    nome=forn_data['nome'],
                    tipo=forn_data['tipo'],
                    cnpj=f'{random.randint(10000000, 99999999)}/0001-{random.randint(10, 99)}',
                    telefone=f'(67) {random.randint(3000, 9999)}-{random.randint(1000, 9999)}',
                )
            self.stdout.write(f'  ✓ {len(fornecedores_data)} fornecedores criados')
        
        # 12. Criar contas a pagar
        if ContaPagar:
            self.stdout.write(self.style.SUCCESS('💰 Criando contas a pagar...'))
            for i in range(1, 25):
                ContaPagar.objects.create(
                    propriedade=propriedade,
                    fornecedor=Fornecedor.objects.filter(propriedade=propriedade).first() if Fornecedor else None,
                    descricao=f'Conta {i}',
                    valor=Decimal(str(random.randint(500, 5000))),
                    data_vencimento=date.today() + timedelta(days=random.randint(1, 60)),
                    status='PENDENTE' if random.random() > 0.3 else 'PAGO',
                )
            self.stdout.write(f'  ✓ 24 contas a pagar criadas')
        
        # 13. Criar contas a receber
        if ContaReceber:
            self.stdout.write(self.style.SUCCESS('💵 Criando contas a receber...'))
            for i in range(1, 15):
                ContaReceber.objects.create(
                    propriedade=propriedade,
                    cliente='Cliente ' + str(i),
                    descricao=f'Venda de Gado {i}',
                    valor=Decimal(str(random.randint(5000, 50000))),
                    data_vencimento=date.today() + timedelta(days=random.randint(1, 90)),
                    status='PENDENTE' if random.random() > 0.4 else 'RECEBIDO',
                )
            self.stdout.write(f'  ✓ 14 contas a receber criadas')
        
        # 14. Criar pastagens
        if Pastagem:
            self.stdout.write(self.style.SUCCESS('🌱 Criando pastagens...'))
            pastagens_data = [
                {'nome': 'Pastagem 1 - Brachiaria', 'area_ha': Decimal('500.00'), 'tipo': 'BRAQUIARIA'},
                {'nome': 'Pastagem 2 - Panicum', 'area_ha': Decimal('400.00'), 'tipo': 'PANICUM'},
                {'nome': 'Pastagem 3 - Tifton', 'area_ha': Decimal('300.00'), 'tipo': 'TIFTON'},
            ]
            
            for past_data in pastagens_data:
                Pastagem.objects.create(
                    propriedade=propriedade,
                    nome=past_data['nome'],
                    area_hectares=past_data['area_ha'],
                    tipo_pastagem=past_data['tipo'],
                    data_plantio=date.today() - timedelta(days=random.randint(365, 1095)),
                )
            self.stdout.write(f'  ✓ {len(pastagens_data)} pastagens criadas')
        
        # 15. Criar bens patrimoniais
        if TipoBem and BemPatrimonial:
            self.stdout.write(self.style.SUCCESS('🏗️ Criando bens patrimoniais...'))
            tipos = [
                {'nome': 'Máquinas e Equipamentos', 'depreciacao_anual': Decimal('10.00')},
                {'nome': 'Veículos', 'depreciacao_anual': Decimal('20.00')},
                {'nome': 'Benfeitorias', 'depreciacao_anual': Decimal('5.00')},
            ]
            
            tipos_bem = {}
            for tipo_data in tipos:
                tipo, _ = TipoBem.objects.get_or_create(
                    nome=tipo_data['nome'],
                    defaults={'taxa_depreciacao_anual': tipo_data['depreciacao_anual']}
                )
                tipos_bem[tipo_data['nome']] = tipo
            
            bens = [
                {'nome': 'Trator John Deere', 'tipo': 'Máquinas e Equipamentos', 'valor': Decimal('350000.00')},
                {'nome': 'Caminhão Ford', 'tipo': 'Veículos', 'valor': Decimal('180000.00')},
                {'nome': 'Curral de Manejo', 'tipo': 'Benfeitorias', 'valor': Decimal('150000.00')},
            ]
            
            for bem_data in bens:
                BemPatrimonial.objects.create(
                    propriedade=propriedade,
                    tipo=tipos_bem[bem_data['tipo']],
                    nome=bem_data['nome'],
                    valor_aquisicao=bem_data['valor'],
                    data_aquisicao=date.today() - timedelta(days=random.randint(365, 1825)),
                )
            self.stdout.write(f'  ✓ {len(bens)} bens patrimoniais criados')
        
        # 16. Criar fluxo de caixa
        if FluxoCaixa:
            self.stdout.write(self.style.SUCCESS('💸 Criando fluxo de caixa...'))
            hoje = date.today()
            for i in range(1, 13):  # 12 meses
                mes = hoje.month - (12 - i) if i <= hoje.month else hoje.month + (i - hoje.month)
                ano = hoje.year if i <= hoje.month else hoje.year - 1
                
                FluxoCaixa.objects.create(
                    propriedade=propriedade,
                    data=date(ano, mes, 15),
                    tipo='RECEITA',
                    descricao=f'Venda de Gado - Mês {i}',
                    valor=Decimal(str(random.randint(50000, 150000))),
                )
                
                FluxoCaixa.objects.create(
                    propriedade=propriedade,
                    data=date(ano, mes, 20),
                    tipo='DESPESA',
                    descricao=f'Despesas Operacionais - Mês {i}',
                    valor=Decimal(str(random.randint(30000, 80000))),
                )
            self.stdout.write(f'  ✓ 24 lançamentos de fluxo de caixa criados')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Popularização da Monpec1 concluída com sucesso!'))
        self.stdout.write(self.style.SUCCESS(f'📊 Propriedade: {propriedade.nome_propriedade} (ID: {propriedade.id})'))
        self.stdout.write(self.style.SUCCESS('🎉 A propriedade está pronta para demonstração!'))


