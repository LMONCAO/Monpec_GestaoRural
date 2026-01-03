from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, timedelta
from decimal import Decimal
import random
from gestao_rural.models import *

class Command(BaseCommand):
    help = 'Popula o sistema com dados de teste'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Iniciando criação de dados de teste...")
        
        # 1. Criar usuário se não existir
        user, created = User.objects.get_or_create(
            username='teste',
            defaults={
                'email': 'teste@exemplo.com',
                'first_name': 'Usuário',
                'last_name': 'Teste',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('123456')
            user.save()
            self.stdout.write(self.style.SUCCESS("✅ Usuário de teste criado"))
        else:
            self.stdout.write("✅ Usuário de teste já existe")
        
        # 2. Criar Produtor Rural
        produtor, created = ProdutorRural.objects.get_or_create(
            cpf_cnpj='12345678901',
            defaults={
                'nome': 'João Silva',
                'usuario_responsavel': user,
                'telefone': '(11) 99999-9999',
                'email': 'joao@fazenda.com',
                'endereco': 'Fazenda São José, Zona Rural',
                'anos_experiencia': 15
            }
        )
        self.stdout.write("✅ Produtor Rural criado")
        
        # 3. Criar Propriedade
        propriedade, created = Propriedade.objects.get_or_create(
            nome_propriedade='Fazenda São José',
            defaults={
                'produtor': produtor,
                'municipio': 'Ribeirão Preto',
                'uf': 'SP',
                'area_total_ha': Decimal('500.00'),
                'tipo_operacao': 'MISTA',
                'tipo_ciclo_pecuario': ['CICLO_COMPLETO'],
                'tipo_propriedade': 'PROPRIA',
                'valor_hectare_proprio': Decimal('15000.00')
            }
        )
        self.stdout.write("✅ Propriedade criada")
        
        # 4. Criar Categorias de Animais
        categorias_data = [
            {'nome': 'Vacas Adultas', 'sexo': 'F', 'idade_minima': 24, 'idade_maxima': 120},
            {'nome': 'Touros', 'sexo': 'M', 'idade_minima': 24, 'idade_maxima': 120},
            {'nome': 'Bezerras', 'sexo': 'F', 'idade_minima': 0, 'idade_maxima': 12},
            {'nome': 'Bezerros', 'sexo': 'M', 'idade_minima': 0, 'idade_maxima': 12},
            {'nome': 'Novilhas', 'sexo': 'F', 'idade_minima': 12, 'idade_maxima': 24},
            {'nome': 'Novilhos', 'sexo': 'M', 'idade_minima': 12, 'idade_maxima': 24},
        ]
        
        for cat_data in categorias_data:
            categoria, created = CategoriaAnimal.objects.get_or_create(
                nome=cat_data['nome'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f"✅ Categoria {categoria.nome} criada")
        
        # 5. Criar Inventário de Rebanho
        self.stdout.write("📊 Criando inventário de rebanho...")
        for categoria in CategoriaAnimal.objects.all():
            inventario, created = InventarioRebanho.objects.get_or_create(
                propriedade=propriedade,
                categoria=categoria,
                data_inventario=date.today(),
                defaults={
                    'quantidade': random.randint(10, 100),
                    'valor_por_cabeca': Decimal(str(random.uniform(800, 3000))).quantize(Decimal('0.01'))
                }
            )
            if created:
                inventario.valor_total = inventario.quantidade * inventario.valor_por_cabeca
                inventario.save()
        
        self.stdout.write("✅ Inventário de rebanho criado")
        
        # 6. Criar Parâmetros de Projeção
        self.stdout.write("📈 Criando parâmetros de projeção...")
        parametros, created = ParametrosProjecao.objects.get_or_create(
            propriedade=propriedade,
            defaults={
                'taxa_natalidade': Decimal('0.85'),
                'taxa_mortalidade_adultos': Decimal('0.03'),
                'taxa_mortalidade_bezerros': Decimal('0.08'),
                'taxa_descarte': Decimal('0.15'),
                'idade_primeira_cria': 36,
                'intervalo_partos': 14,
                'peso_medio_venda': Decimal('450.00'),
                'preco_medio_venda': Decimal('180.00'),
                'custo_manutencao_por_cabeca': Decimal('120.00')
            }
        )
        self.stdout.write("✅ Parâmetros de projeção criados")
        
        # 7. Criar Custos Fixos
        self.stdout.write("💰 Criando custos fixos...")
        custos_fixos_data = [
            {'nome_custo': 'Mão de Obra', 'valor_mensal': Decimal('5000.00'), 'tipo_custo': 'MAO_OBRA'},
            {'nome_custo': 'Aluguel de Pasto', 'valor_mensal': Decimal('2000.00'), 'tipo_custo': 'PASTAGEM'},
            {'nome_custo': 'Energia Elétrica', 'valor_mensal': Decimal('800.00'), 'tipo_custo': 'ENERGIA'},
            {'nome_custo': 'Combustível', 'valor_mensal': Decimal('1200.00'), 'tipo_custo': 'COMBUSTIVEL'},
            {'nome_custo': 'Manutenção', 'valor_mensal': Decimal('1500.00'), 'tipo_custo': 'MANUTENCAO'},
        ]
        
        for custo_data in custos_fixos_data:
            custo, created = CustoFixo.objects.get_or_create(
                propriedade=propriedade,
                nome_custo=custo_data['nome_custo'],
                defaults=custo_data
            )
            if created:
                self.stdout.write(f"✅ Custo fixo {custo.nome_custo} criado")
        
        # 8. Criar Custos Variáveis
        self.stdout.write("📊 Criando custos variáveis...")
        custos_variaveis_data = [
            {'nome_custo': 'Ração', 'tipo_custo': 'ALIMENTACAO', 'valor_por_cabeca': Decimal('45.00')},
            {'nome_custo': 'Medicamentos', 'tipo_custo': 'SANEAMENTO', 'valor_por_cabeca': Decimal('15.00')},
            {'nome_custo': 'Sementes', 'tipo_custo': 'PASTAGEM', 'valor_por_cabeca': Decimal('8.00')},
            {'nome_custo': 'Inseminação', 'tipo_custo': 'REPRODUCAO', 'valor_por_cabeca': Decimal('25.00')},
        ]
        
        for custo_data in custos_variaveis_data:
            custo, created = CustoVariavel.objects.get_or_create(
                propriedade=propriedade,
                nome_custo=custo_data['nome_custo'],
                defaults=custo_data
            )
            if created:
                self.stdout.write(f"✅ Custo variável {custo.nome_custo} criado")
        
        # 9. Criar Financiamentos
        self.stdout.write("🏦 Criando financiamentos...")
        financiamentos_data = [
            {
                'nome_financiamento': 'Financiamento Rural - Banco do Brasil',
                'valor_principal': Decimal('150000.00'),
                'taxa_juros_anual': Decimal('8.5'),
                'prazo_meses': 60,
                'data_inicio': date.today() - timedelta(days=30),
                'tipo_financiamento': 'RURAL'
            },
            {
                'nome_financiamento': 'Empréstimo Pessoal - Caixa',
                'valor_principal': Decimal('50000.00'),
                'taxa_juros_anual': Decimal('12.0'),
                'prazo_meses': 24,
                'data_inicio': date.today() - timedelta(days=15),
                'tipo_financiamento': 'PESSOAL'
            }
        ]
        
        for fin_data in financiamentos_data:
            financiamento, created = Financiamento.objects.get_or_create(
                propriedade=propriedade,
                nome_financiamento=fin_data['nome_financiamento'],
                defaults=fin_data
            )
            if created:
                self.stdout.write(f"✅ Financiamento {financiamento.nome_financiamento} criado")
        
        # 10. Criar Indicadores Financeiros
        self.stdout.write("📊 Criando indicadores financeiros...")
        indicadores_data = [
            {'nome': 'Receita Bruta Anual', 'valor': Decimal('450000.00'), 'tipo': 'RECEITA', 'ano': 2024},
            {'nome': 'Custos Operacionais', 'valor': Decimal('280000.00'), 'tipo': 'CUSTO', 'ano': 2024},
            {'nome': 'Lucro Líquido', 'valor': Decimal('170000.00'), 'tipo': 'LUCRO', 'ano': 2024},
            {'nome': 'Margem de Lucro', 'valor': Decimal('37.78'), 'tipo': 'PERCENTUAL', 'ano': 2024},
            {'nome': 'ROI', 'valor': Decimal('15.5'), 'tipo': 'PERCENTUAL', 'ano': 2024},
        ]
        
        for ind_data in indicadores_data:
            indicador, created = IndicadorFinanceiro.objects.get_or_create(
                propriedade=propriedade,
                nome=ind_data['nome'],
                ano=ind_data['ano'],
                defaults=ind_data
            )
            if created:
                self.stdout.write(f"✅ Indicador {indicador.nome} criado")
        
        # 11. Criar Movimentações Projetadas
        self.stdout.write("📅 Criando movimentações projetadas...")
        movimentacoes_data = [
            {
                'data_movimentacao': date.today() + timedelta(days=30),
                'tipo_movimentacao': 'VENDA',
                'categoria': CategoriaAnimal.objects.filter(sexo='M').first(),
                'quantidade': 15,
                'valor_por_cabeca': Decimal('1800.00')
            },
            {
                'data_movimentacao': date.today() + timedelta(days=60),
                'tipo_movimentacao': 'NASCIMENTO',
                'categoria': CategoriaAnimal.objects.filter(sexo='F').first(),
                'quantidade': 25,
                'valor_por_cabeca': Decimal('0.00')
            },
            {
                'data_movimentacao': date.today() + timedelta(days=90),
                'tipo_movimentacao': 'COMPRA',
                'categoria': CategoriaAnimal.objects.filter(sexo='F').first(),
                'quantidade': 10,
                'valor_por_cabeca': Decimal('2500.00')
            }
        ]
        
        for mov_data in movimentacoes_data:
            if mov_data['categoria']:
                movimentacao, created = MovimentacaoProjetada.objects.get_or_create(
                    propriedade=propriedade,
                    data_movimentacao=mov_data['data_movimentacao'],
                    tipo_movimentacao=mov_data['tipo_movimentacao'],
                    categoria=mov_data['categoria'],
                    defaults={
                        'quantidade': mov_data['quantidade'],
                        'valor_por_cabeca': mov_data['valor_por_cabeca'],
                        'valor_total': mov_data['quantidade'] * mov_data['valor_por_cabeca']
                    }
                )
                if created:
                    self.stdout.write(f"✅ Movimentação {movimentacao.get_tipo_movimentacao_display()} criada")
        
        self.stdout.write(self.style.SUCCESS("\n🎉 Dados de teste criados com sucesso!"))
        self.stdout.write(f"📊 Propriedade: {propriedade.nome_propriedade}")
        self.stdout.write(f"👤 Produtor: {produtor.nome}")
        self.stdout.write(f"🔗 Acesse: http://localhost:8000/propriedade/{propriedade.id}/pecuaria/")
        
        return propriedade












