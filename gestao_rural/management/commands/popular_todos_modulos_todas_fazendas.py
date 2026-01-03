# -*- coding: utf-8 -*-
"""
Comando para popular dados em TODOS os módulos e TODAS as fazendas
Simula o ano completo de 2025 desde janeiro com fazendas de grande porte
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction, models
from datetime import date, datetime, timedelta
from decimal import Decimal
import random
import time
from calendar import monthrange

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


class Command(BaseCommand):
    help = 'Popula dados em TODOS os módulos para TODAS as fazendas - Simulação completa de 2025'

    def add_arguments(self, parser):
        parser.add_argument(
            '--propriedade-id',
            type=int,
            help='ID de uma propriedade específica (opcional)',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Pular dados que já existem',
        )
        parser.add_argument(
            '--ano',
            type=int,
            default=2025,
            help='Ano para simulação (padrão: 2025)',
        )
        parser.add_argument(
            '--grande-porte',
            action='store_true',
            default=True,
            help='Criar fazendas de grande porte com muitos dados (padrão: True)',
        )

    def handle(self, *args, **options):
        propriedade_id = options.get('propriedade_id')
        skip_existing = options.get('skip_existing', False)
        ano_simulacao = options.get('ano', 2025)
        grande_porte = options.get('grande_porte', True)

        self.stdout.write(self.style.SUCCESS(f"🚀 Iniciando simulação completa do ano {ano_simulacao}..."))
        self.stdout.write(f"📅 Período: Janeiro {ano_simulacao} até Dezembro {ano_simulacao}")
        if grande_porte:
            self.stdout.write("🏭 Modo: FAZENDAS DE GRANDE PORTE (muitos dados)")

        # Obter propriedades (fora da transação)
        if propriedade_id:
            propriedades = Propriedade.objects.filter(id=propriedade_id)
            if not propriedades.exists():
                self.stdout.write(self.style.ERROR(f"❌ Propriedade {propriedade_id} não encontrada!"))
                return
        else:
            propriedades = Propriedade.objects.all()

        if not propriedades.exists():
            self.stdout.write(self.style.WARNING("⚠️ Nenhuma propriedade encontrada! Criando uma propriedade de exemplo..."))
            propriedades = [self._criar_propriedade_exemplo()]

        total_propriedades = propriedades.count()
        self.stdout.write(f"📊 Processando {total_propriedades} propriedade(s)...")

        # Garantir categorias padrão (fora da transação)
        self._garantir_categorias_padrao()

        # Processar cada propriedade em sua própria transação
        propriedades_processadas = 0
        propriedades_com_erro = 0

        for idx, propriedade in enumerate(propriedades, 1):
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"🏠 Propriedade {idx}/{total_propriedades}: {propriedade.nome_propriedade}")
            self.stdout.write(f"{'='*60}")

            try:
                # Processar cada propriedade em sua própria transação
                with transaction.atomic():
                    # Módulo 1: Pecuária (Inventário inicial em janeiro)
                    self._popular_pecuaria(propriedade, skip_existing, ano_simulacao, grande_porte)

                    # Módulo 2: Rastreabilidade (PNIB) - Muitos animais
                    self._popular_rastreabilidade(propriedade, skip_existing, ano_simulacao, grande_porte)

                    # Módulo 3: Reprodução - Eventos ao longo do ano
                    self._popular_reproducao(propriedade, skip_existing, ano_simulacao, grande_porte)

                    # Módulo 4: Operacional - Lançamentos mensais
                    self._popular_operacional(propriedade, skip_existing, ano_simulacao, grande_porte)

                    # Módulo 5: Funcionários - Folha mensal
                    self._popular_funcionarios(propriedade, skip_existing, ano_simulacao, grande_porte)

                    # Módulo 6: Compras e Fornecedores - Compras mensais
                    self._popular_compras(propriedade, skip_existing, ano_simulacao, grande_porte)

                    # Módulo 7: Pastagens
                    self._popular_pastagens(propriedade, skip_existing, ano_simulacao, grande_porte)

                # Módulo 8: Financeiro - Lançamentos mensais
                self._popular_financeiro(propriedade, skip_existing, ano_simulacao, grande_porte)

                # Módulo 9: Projetos Bancários
                self._popular_projetos_bancarios(propriedade, skip_existing, ano_simulacao, grande_porte)

                # Módulo 10: Bens e Patrimônio
                self._popular_bens_patrimonio(propriedade, skip_existing, ano_simulacao, grande_porte)

                # Módulo 11: Movimentações mensais ao longo do ano
                self._popular_movimentacoes_anuais(propriedade, skip_existing, ano_simulacao, grande_porte)

                self.stdout.write(self.style.SUCCESS(f"✅ Propriedade {propriedade.nome_propriedade} concluída!"))
                propriedades_processadas += 1

            except Exception as e:
                propriedades_com_erro += 1
                self.stdout.write(self.style.ERROR(f"❌ Erro ao processar {propriedade.nome_propriedade}: {str(e)}"))
                # Não imprimir traceback completo para não poluir a saída
                # import traceback
                # self.stdout.write(traceback.format_exc())
                self.stdout.write(f"   ⚠️ Continuando com próxima propriedade...")

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Processamento concluído!"))
        self.stdout.write(f"   ✅ Propriedades processadas: {propriedades_processadas}")
        if propriedades_com_erro > 0:
            self.stdout.write(self.style.WARNING(f"   ⚠️ Propriedades com erro: {propriedades_com_erro}"))

    def _criar_propriedade_exemplo(self):
        """Cria uma propriedade de exemplo se não existir nenhuma"""
        user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@monpec.com.br',
                'first_name': 'Administrador',
                'last_name': 'Sistema',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if not user.check_password('admin123'):
            user.set_password('admin123')
            user.save()

        produtor, _ = ProdutorRural.objects.get_or_create(
            cpf_cnpj='00000000000',
            defaults={
                'nome': 'Produtor Exemplo',
                'usuario_responsavel': user,
                'telefone': '(00) 00000-0000',
                'email': 'produtor@exemplo.com',
                'endereco': 'Endereço de exemplo',
                'anos_experiencia': 10
            }
        )

        propriedade, _ = Propriedade.objects.get_or_create(
            nome_propriedade='Fazenda Exemplo',
            produtor=produtor,
            defaults={
                'municipio': 'Campo Grande',
                'uf': 'MS',
                'area_total_ha': Decimal('1000.00'),
                'tipo_operacao': 'PECUARIA',
                'tipo_ciclo_pecuario': ['CICLO_COMPLETO'],
                'tipo_propriedade': 'PROPRIA',
                'valor_hectare_proprio': Decimal('10000.00')
            }
        )

        return propriedade

    def _garantir_categorias_padrao(self):
        """Garante que as categorias padrão existam"""
        self.stdout.write("📋 Verificando categorias padrão...")

        categorias_data = [
            {'nome': 'Bezerro(a)', 'sexo': 'I', 'idade_minima_meses': 0, 'idade_maxima_meses': 12, 'peso_medio_kg': Decimal('50.00')},
            {'nome': 'Novilho(a)', 'sexo': 'I', 'idade_minima_meses': 12, 'idade_maxima_meses': 24, 'peso_medio_kg': Decimal('250.00')},
            {'nome': 'Bezerra', 'sexo': 'F', 'idade_minima_meses': 0, 'idade_maxima_meses': 6, 'peso_medio_kg': Decimal('50.00')},
            {'nome': 'Novilha', 'sexo': 'F', 'idade_minima_meses': 6, 'idade_maxima_meses': 24, 'peso_medio_kg': Decimal('250.00')},
            {'nome': 'Novilha Primípara', 'sexo': 'F', 'idade_minima_meses': 24, 'idade_maxima_meses': 36, 'peso_medio_kg': Decimal('350.00')},
            {'nome': 'Vaca Primípara', 'sexo': 'F', 'idade_minima_meses': 36, 'idade_maxima_meses': 48, 'peso_medio_kg': Decimal('450.00')},
            {'nome': 'Vaca Multípara', 'sexo': 'F', 'idade_minima_meses': 48, 'idade_maxima_meses': 999, 'peso_medio_kg': Decimal('500.00')},
            {'nome': 'Bezerro', 'sexo': 'M', 'idade_minima_meses': 0, 'idade_maxima_meses': 6, 'peso_medio_kg': Decimal('55.00')},
            {'nome': 'Novilho', 'sexo': 'M', 'idade_minima_meses': 6, 'idade_maxima_meses': 24, 'peso_medio_kg': Decimal('280.00')},
            {'nome': 'Boi de Corte', 'sexo': 'M', 'idade_minima_meses': 24, 'idade_maxima_meses': 999, 'peso_medio_kg': Decimal('400.00')},
            {'nome': 'Touro', 'sexo': 'M', 'idade_minima_meses': 36, 'idade_maxima_meses': 999, 'peso_medio_kg': Decimal('800.00')},
        ]

        for cat_data in categorias_data:
            categoria, created = CategoriaAnimal.objects.get_or_create(
                nome=cat_data['nome'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f"  ✅ Categoria {categoria.nome} criada")

    def _popular_pecuaria(self, propriedade, skip_existing, ano, grande_porte):
        """Popular módulo de Pecuária - Inventário inicial em janeiro (MÁXIMO 1500 ANIMAIS)"""
        self.stdout.write("  🐄 Módulo Pecuária (Inventário Janeiro)...")

        # Data inicial: 1º de janeiro do ano
        data_inicial = date(ano, 1, 1)

        # Inventário de Rebanho - Janeiro (inventário inicial)
        # MÁXIMO 1500 ANIMAIS POR FAZENDA
        MAX_ANIMAIS = 1500
        
        categorias = CategoriaAnimal.objects.filter(ativo=True)
        total_animais = 0
        
        # Distribuição realista para máximo 1500 animais
        # Estrutura típica: 40% vacas, 20% novilhas, 15% bezerros, 15% bois, 5% touros, 5% outros
        distribuicao_alvo = {
            'Vaca': 0.40,      # ~600 animais
            'Novilha': 0.20,   # ~300 animais
            'Bezerro': 0.15,   # ~225 animais
            'Bezerra': 0.10,   # ~150 animais
            'Boi': 0.10,       # ~150 animais
            'Touro': 0.02,     # ~30 animais
            'Novilho': 0.03,   # ~45 animais
        }

        for categoria in categorias:
            if skip_existing and InventarioRebanho.objects.filter(
                propriedade=propriedade,
                categoria=categoria,
                data_inventario=data_inicial
            ).exists():
                continue

            # Determinar quantidade baseada no tipo de categoria (realista)
            nome_cat = categoria.nome
            percentual = 0.0
            
            for key, pct in distribuicao_alvo.items():
                if key in nome_cat:
                    percentual = pct
                    break
            
            if percentual == 0:
                percentual = 0.01  # Outros: 1%
            
            # Calcular quantidade baseada no percentual
            quantidade_alvo = int(MAX_ANIMAIS * percentual)
            # Adicionar variação de ±20%
            quantidade = random.randint(int(quantidade_alvo * 0.8), int(quantidade_alvo * 1.2))
            
            # Garantir que não ultrapasse o máximo
            if total_animais + quantidade > MAX_ANIMAIS:
                quantidade = max(0, MAX_ANIMAIS - total_animais)
            
            if quantidade == 0:
                continue
            
            # Valores realistas por categoria
            if 'Bezerro' in nome_cat or 'Bezerra' in nome_cat:
                valor_por_cabeca = Decimal(str(random.uniform(600, 900))).quantize(Decimal('0.01'))
            elif 'Novilho' in nome_cat or 'Novilha' in nome_cat:
                valor_por_cabeca = Decimal(str(random.uniform(1000, 1800))).quantize(Decimal('0.01'))
            elif 'Vaca' in nome_cat:
                valor_por_cabeca = Decimal(str(random.uniform(2500, 4000))).quantize(Decimal('0.01'))
            elif 'Touro' in nome_cat:
                valor_por_cabeca = Decimal(str(random.uniform(6000, 10000))).quantize(Decimal('0.01'))
            elif 'Boi' in nome_cat:
                valor_por_cabeca = Decimal(str(random.uniform(1800, 2800))).quantize(Decimal('0.01'))
            else:
                valor_por_cabeca = Decimal(str(random.uniform(1000, 2000))).quantize(Decimal('0.01'))

            InventarioRebanho.objects.update_or_create(
                propriedade=propriedade,
                categoria=categoria,
                data_inventario=data_inicial,
                defaults={
                    'quantidade': quantidade,
                    'valor_por_cabeca': valor_por_cabeca
                }
            )
            total_animais += quantidade
            
            if total_animais >= MAX_ANIMAIS:
                break

        self.stdout.write(f"    ✅ Inventário inicial: {total_animais} animais (máximo {MAX_ANIMAIS}) em {data_inicial.strftime('%d/%m/%Y')}")

        # Parâmetros de Projeção
        ParametrosProjecaoRebanho.objects.update_or_create(
            propriedade=propriedade,
            defaults={
                'taxa_natalidade_anual': Decimal('85.00'),
                'taxa_mortalidade_bezerros_anual': Decimal('5.00'),
                'taxa_mortalidade_adultos_anual': Decimal('2.00'),
                'percentual_venda_machos_anual': Decimal('90.00'),
                'percentual_venda_femeas_anual': Decimal('10.00'),
                'periodicidade': 'MENSAL'
            }
        )

        self.stdout.write("    ✅ Inventário e parâmetros criados")

    def _popular_rastreabilidade(self, propriedade, skip_existing, ano, grande_porte):
        """Popular módulo de Rastreabilidade (PNIB) - Muitos animais"""
        self.stdout.write("  🏷️ Módulo Rastreabilidade (PNIB)...")

        if not AnimalIndividual:
            self.stdout.write("    ⚠️ Modelo AnimalIndividual não disponível")
            return

        # Criar muitos animais individuais para fazenda grande
        categorias = CategoriaAnimal.objects.filter(ativo=True)
        animais_criados = 0
        data_inicial = date(ano, 1, 1)

        for categoria in categorias:
            inventario = InventarioRebanho.objects.filter(
                propriedade=propriedade,
                categoria=categoria,
                data_inventario=data_inicial
            ).first()

            if not inventario or inventario.quantidade == 0:
                continue

            # Criar animais individuais baseado no inventário (realista: 30-50% do inventário rastreado)
            # Não criar mais que o inventário
            percentual_rastreado = random.uniform(0.30, 0.50)  # 30-50% rastreados
            quantidade_animais = min(int(inventario.quantidade * percentual_rastreado), inventario.quantidade)

            for i in range(quantidade_animais):
                # Gerar número de brinco único usando timestamp e contador
                timestamp = int(time.time() * 1000000) % 100000000  # Últimos 8 dígitos do timestamp em microssegundos
                numero_brinco = f"BR{propriedade.id:02d}{categoria.id:02d}{timestamp:08d}{i+1:04d}"
                
                # Verificar se já existe e tentar novamente se necessário
                tentativas = 0
                while AnimalIndividual.objects.filter(numero_brinco=numero_brinco).exists() and tentativas < 10:
                    timestamp = int(time.time() * 1000000) % 100000000
                    numero_brinco = f"BR{propriedade.id:02d}{categoria.id:02d}{timestamp:08d}{i+1:04d}"
                    tentativas += 1
                    time.sleep(0.001)  # Pequeno delay para garantir timestamp diferente
                
                if skip_existing and AnimalIndividual.objects.filter(
                    propriedade=propriedade,
                    numero_brinco=numero_brinco
                ).exists():
                    continue

                # Calcular data de nascimento baseada na idade da categoria
                idade_meses = random.randint(
                    categoria.idade_minima_meses or 0,
                    min(categoria.idade_maxima_meses or 120, 120)
                )
                data_nascimento = data_inicial - timedelta(days=idade_meses * 30)

                try:
                    animal = AnimalIndividual.objects.create(
                        propriedade=propriedade,
                        categoria=categoria,
                        numero_brinco=numero_brinco,
                        sexo=categoria.sexo if categoria.sexo != 'I' else random.choice(['M', 'F']),
                        data_nascimento=data_nascimento,
                        raca='NELORE',
                        peso_atual_kg=Decimal(str(random.uniform(100, 500))).quantize(Decimal('0.01')),
                        status='ATIVO'
                    )
                except Exception as e:
                    # Se ainda houver erro de duplicata, pular este animal
                    self.stdout.write(f"    ⚠️ Erro ao criar animal com brinco {numero_brinco}: {str(e)}")
                    continue

                # Criar brinco
                if BrincoAnimal:
                    BrincoAnimal.objects.get_or_create(
                        numero_brinco=animal.numero_brinco,
                        defaults={
                            'tipo_brinco': 'VISUAL',
                            'animal': animal,
                            'propriedade': propriedade,
                            'status': 'EM_USO',
                            'data_utilizacao': data_nascimento + timedelta(days=30),
                            'data_aquisicao': data_nascimento
                        }
                    )

                animais_criados += 1

        self.stdout.write(f"    ✅ {animais_criados} animais individuais criados")

    def _popular_reproducao(self, propriedade, skip_existing, ano, grande_porte):
        """Popular módulo de Reprodução - Eventos ao longo do ano"""
        self.stdout.write("  👶 Módulo Reprodução...")

        if not Touro:
            self.stdout.write("    ⚠️ Modelos de reprodução não disponíveis")
            return

        data_inicial = date(ano, 1, 1)

        # Criar touros (mais para fazenda grande)
        num_touros = 15 if grande_porte else 3
        animais_machos = AnimalIndividual.objects.filter(
            propriedade=propriedade,
            sexo='M',
            categoria__nome__icontains='Touro'
        )[:num_touros]

        if not animais_machos.exists() or animais_machos.count() < num_touros:
            # Criar touros se não existirem
            categoria_touro = CategoriaAnimal.objects.filter(nome__icontains='Touro').first()
            if categoria_touro:
                for i in range(num_touros):
                    if AnimalIndividual.objects.filter(
                        propriedade=propriedade,
                        numero_brinco=f"{propriedade.id:04d}TOU{i+1:03d}"
                    ).exists():
                        continue
                    animal = AnimalIndividual.objects.create(
                        propriedade=propriedade,
                        categoria=categoria_touro,
                        numero_brinco=f"{propriedade.id:04d}TOU{i+1:03d}",
                        sexo='M',
                        data_nascimento=data_inicial - timedelta(days=random.randint(1000, 2000)),
                        raca='NELORE',
                        peso_atual_kg=Decimal('800.00'),
                        status='ATIVO'
                    )
                animais_machos = AnimalIndividual.objects.filter(
                    propriedade=propriedade,
                    sexo='M',
                    categoria__nome__icontains='Touro'
                )[:num_touros]

        for animal in animais_machos:
            Touro.objects.get_or_create(
                propriedade=propriedade,
                animal_individual=animal,
                defaults={
                    'status': 'APTO',
                    'propriedade_touro': 'PROPRIO',
                    'raca': 'Nelore',
                    'numero_brinco': animal.numero_brinco if hasattr(animal, 'numero_brinco') else f'T{animal.id:06d}'
                }
            )

        # Criar Estação de Monta (janeiro a abril)
        EstacaoMonta.objects.get_or_create(
            propriedade=propriedade,
            nome='Estação de Monta Principal',
            defaults={
                'data_inicio': date(ano, 1, 1),
                'data_fim': date(ano, 4, 30),
                'tipo': 'IATF',
                'numero_vacas_objetivo': 200 if grande_porte else 50,
                'taxa_prenhez_objetivo': Decimal('85.00')
            }
        )

        # Criar IATFs ao longo do ano (janeiro a abril)
        if IATF:
            vacas = AnimalIndividual.objects.filter(
                propriedade=propriedade,
                sexo='F',
                categoria__nome__icontains='Vaca'
            )[:50 if grande_porte else 10]

            estacao_monta = EstacaoMonta.objects.filter(propriedade=propriedade).first()
            for mes in range(1, 5):  # Janeiro a abril
                for idx, vaca in enumerate(vacas[:10]):  # 10 IATFs por mês
                    data_iatf = date(ano, mes, random.randint(1, 28))
                    protocolo = f'IATF-{mes:02d}-{idx+1:03d}'
                    IATF.objects.get_or_create(
                        propriedade=propriedade,
                        animal_individual=vaca,
                        protocolo=protocolo,
                        defaults={
                            'estacao_monta': estacao_monta,
                            'data_programada': data_iatf,
                            'data_realizacao': data_iatf,
                            'status': 'REALIZADA',
                            'observacoes': f'IATF {mes}/{ano}'
                        }
                    )

        self.stdout.write(f"    ✅ {animais_machos.count()} touros e estações de monta criados")

    def _popular_operacional(self, propriedade, skip_existing, ano, grande_porte):
        """Popular módulo Operacional - Muitos lançamentos"""
        self.stdout.write("  ⚙️ Módulo Operacional...")

        if not TanqueCombustivel:
            self.stdout.write("    ⚠️ Modelos operacionais não disponíveis")
            return

        # Tanques de Combustível (múltiplos para fazenda grande)
        num_tanques = 2 if grande_porte else 1
        tanques = []
        for i in range(num_tanques):
            tanque, _ = TanqueCombustivel.objects.get_or_create(
                propriedade=propriedade,
                nome=f'Tanque {i+1}',
                defaults={
                    'capacidade_litros': Decimal(str(random.uniform(1000, 2000))).quantize(Decimal('0.01')) if grande_porte else Decimal('500.00'),
                    'estoque_atual': Decimal(str(random.uniform(100, 300))).quantize(Decimal('0.01')) if grande_porte else Decimal('100.00'),
                    'estoque_minimo': Decimal('100.00') if grande_porte else Decimal('50.00'),
                    'localizacao': f'Local {i+1}'
                }
            )
            tanques.append(tanque)

        # Abastecimentos mensais (mínimo 232 total, mas com quantidades realistas)
        # Reduzir quantidade de abastecimentos para evitar estoque muito alto
        abastecimentos_criados = 0
        if AbastecimentoCombustivel:
            # Gerar 10-15 abastecimentos por mês (total: 120-180 no ano)
            for mes in range(1, 13):
                num_abastecimentos = random.randint(10, 15) if grande_porte else random.randint(8, 12)
                for i in range(num_abastecimentos):
                    data_abastecimento = date(ano, mes, random.randint(1, 25))
                    tanque = random.choice(tanques)
                    # Quantidades realistas: 200-500 litros por abastecimento
                    quantidade = Decimal(str(random.uniform(200, 500))).quantize(Decimal('0.01')) if grande_porte else Decimal(str(random.uniform(100, 300))).quantize(Decimal('0.01'))
                    preco = Decimal(str(random.uniform(5.20, 5.80))).quantize(Decimal('0.01'))
                    
                    # Verificar se o abastecimento não ultrapassa a capacidade
                    # O modelo já atualiza o estoque automaticamente, então precisamos verificar antes
                    tanque.refresh_from_db()
                    estoque_apos_abastecimento = tanque.estoque_atual + quantidade
                    if estoque_apos_abastecimento <= tanque.capacidade_litros:
                        AbastecimentoCombustivel.objects.update_or_create(
                            propriedade=propriedade,
                            tanque=tanque,
                            data=data_abastecimento,
                            defaults={
                                'tipo': 'COMPRA',
                                'quantidade_litros': quantidade,
                                'preco_unitario': preco,
                                'valor_total': quantidade * preco,
                                'fornecedor': f'Posto {random.randint(1, 5)}',
                                'numero_nota_fiscal': f'NF{mes:02d}{i+1:04d}'
                            }
                        )
                        abastecimentos_criados += 1
                    else:
                        # Ajustar quantidade para não ultrapassar capacidade
                        quantidade_ajustada = max(Decimal('0'), tanque.capacidade_litros - tanque.estoque_atual)
                        if quantidade_ajustada > 0:
                            AbastecimentoCombustivel.objects.update_or_create(
                                propriedade=propriedade,
                                tanque=tanque,
                                data=data_abastecimento,
                                defaults={
                                    'tipo': 'COMPRA',
                                    'quantidade_litros': quantidade_ajustada,
                                    'preco_unitario': preco,
                                    'valor_total': quantidade_ajustada * preco,
                                    'fornecedor': f'Posto {random.randint(1, 5)}',
                                    'numero_nota_fiscal': f'NF{mes:02d}{i+1:04d}'
                                }
                            )
                            abastecimentos_criados += 1

        # Consumos mensais (mínimo 232 total, mas com quantidades realistas)
        # Criar mais consumos que abastecimentos para manter estoque controlado
        consumos_criados = 0
        if ConsumoCombustivel:
            # Gerar 20-30 consumos por mês (total: 240-360 no ano, garantindo 232+)
            for mes in range(1, 13):
                num_consumos = random.randint(20, 30) if grande_porte else random.randint(15, 25)
                for i in range(num_consumos):
                    data_consumo = date(ano, mes, random.randint(1, 28))
                    tanque = random.choice(tanques)
                    # Consumos realistas: 30-100 litros por consumo
                    quantidade = Decimal(str(random.uniform(30, 100))).quantize(Decimal('0.01'))
                    valor_unitario = Decimal(str(random.uniform(5.20, 5.80))).quantize(Decimal('0.01'))
                    
                    # O modelo ConsumoCombustivel já atualiza o estoque automaticamente
                    ConsumoCombustivel.objects.update_or_create(
                        propriedade=propriedade,
                        tanque=tanque,
                        data=data_consumo,
                        defaults={
                            'quantidade_litros': quantidade,
                            'valor_unitario': valor_unitario,
                            'valor_total': quantidade * valor_unitario,
                            'finalidade': random.choice(['Plantio', 'Colheita', 'Transporte', 'Manutenção', 'Outros'])
                        }
                    )
                    consumos_criados += 1

        # Estoque de Suplementação (múltiplos tipos)
        estoques_criados = 0
        if EstoqueSuplementacao:
            tipos_suplemento = ['Sal Mineral', 'Ração Concentrada', 'Ureia', 'Farelo de Soja', 'Milho', 'Suplemento Proteico']
            for tipo in tipos_suplemento:
                estoque, _ = EstoqueSuplementacao.objects.get_or_create(
                    propriedade=propriedade,
                    tipo_suplemento=tipo,
                    defaults={
                        'quantidade_atual': Decimal(str(random.uniform(500, 5000))).quantize(Decimal('0.01')) if grande_porte else Decimal(str(random.uniform(100, 1000))).quantize(Decimal('0.01')),
                        'unidade_medida': 'KG',
                        'quantidade_minima': Decimal('200.00') if grande_porte else Decimal('50.00'),
                        'valor_unitario_medio': Decimal(str(random.uniform(2.00, 8.00))).quantize(Decimal('0.01'))
                    }
                )
                estoques_criados += 1

        # Compras de Suplementação mensais (mínimo 232 total)
        compras_suplementacao_criadas = 0
        if CompraSuplementacao and EstoqueSuplementacao:
            estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade)
            # Gerar pelo menos 20 compras por mês para garantir 240+ total
            for mes in range(1, 13):
                num_compras = random.randint(20, 30) if grande_porte else random.randint(15, 25)
                for i in range(num_compras):
                    if estoques.exists():
                        estoque = random.choice(list(estoques))
                        data_compra = date(ano, mes, random.randint(1, 25))
                        quantidade = Decimal(str(random.uniform(500, 2000))).quantize(Decimal('0.01')) if grande_porte else Decimal(str(random.uniform(100, 500))).quantize(Decimal('0.01'))
                        preco_unitario = Decimal(str(random.uniform(2.00, 8.00))).quantize(Decimal('0.01'))
                        
                        CompraSuplementacao.objects.update_or_create(
                            estoque=estoque,
                            data=data_compra,
                            defaults={
                                'quantidade': quantidade,
                                'preco_unitario': preco_unitario,
                                'valor_total': quantidade * preco_unitario,
                                'fornecedor': f'Fornecedor {random.randint(1, 10)}',
                                'numero_nota_fiscal': f'NF-SUP{mes:02d}{i+1:04d}'
                            }
                        )
                        compras_suplementacao_criadas += 1

        # Equipamentos (muitos para fazenda grande)
        equipamentos_criados = 0
        if Equipamento:
            from gestao_rural.models_operacional import TipoEquipamento
            
            # Criar tipos de equipamento se não existirem
            tipos_equipamento = ['TRATOR', 'PULVERIZADOR', 'CAMINHAO', 'COLHEDORA', 'PLANTADEIRA', 'GRADE', 'ARADO', 'ENXADA_ROTATIVA']
            tipos_criados = {}
            for tipo_nome in tipos_equipamento:
                tipo_obj, _ = TipoEquipamento.objects.get_or_create(
                    nome=tipo_nome,
                    defaults={'descricao': f'Tipo de equipamento {tipo_nome}'}
                )
                tipos_criados[tipo_nome] = tipo_obj
            
            if grande_porte:
                equipamentos_data = [
                    {'nome': 'Trator John Deere 6110J', 'tipo': 'TRATOR', 'valor_aquisicao': Decimal('350000.00')},
                    {'nome': 'Trator Massey Ferguson 6713', 'tipo': 'TRATOR', 'valor_aquisicao': Decimal('280000.00')},
                    {'nome': 'Pulverizador Jacto', 'tipo': 'PULVERIZADOR', 'valor_aquisicao': Decimal('45000.00')},
                    {'nome': 'Caminhão Mercedes-Benz', 'tipo': 'CAMINHAO', 'valor_aquisicao': Decimal('180000.00')},
                    {'nome': 'Colheitadeira', 'tipo': 'COLHEDORA', 'valor_aquisicao': Decimal('800000.00')},
                    {'nome': 'Plantadeira', 'tipo': 'PLANTADEIRA', 'valor_aquisicao': Decimal('120000.00')},
                    {'nome': 'Grade Aradora', 'tipo': 'GRADE', 'valor_aquisicao': Decimal('35000.00')},
                ]
            else:
                equipamentos_data = [
                    {'nome': 'Trator John Deere', 'tipo': 'TRATOR', 'valor_aquisicao': Decimal('150000.00')},
                    {'nome': 'Pulverizador', 'tipo': 'PULVERIZADOR', 'valor_aquisicao': Decimal('25000.00')},
                    {'nome': 'Caminhão', 'tipo': 'CAMINHAO', 'valor_aquisicao': Decimal('80000.00')},
                ]

            for eq_data in equipamentos_data:
                tipo_obj = tipos_criados.get(eq_data['tipo'])
                if not tipo_obj:
                    continue
                    
                equipamento, _ = Equipamento.objects.get_or_create(
                    propriedade=propriedade,
                    nome=eq_data['nome'],
                    defaults={
                        'tipo': tipo_obj,
                        'valor_aquisicao': eq_data['valor_aquisicao'],
                        'data_aquisicao': date(ano, 1, 1) - timedelta(days=random.randint(100, 1000)),
                        'ativo': True
                    }
                )
                equipamentos_criados += 1

                # Manutenções para cada equipamento (REALISTA: 1-2 por ANO por equipamento)
                if ManutencaoEquipamento:
                    hoje = date.today()
                    # Apenas 1-2 manutenções por ANO por equipamento (não por mês!)
                    num_manutencoes_ano = random.randint(1, 2)
                    
                    for i in range(num_manutencoes_ano):
                        # Distribuir ao longo do ano
                        mes = random.randint(1, 12)
                        data_agendamento = date(ano, mes, random.randint(1, 28))
                        
                        # Se a data é no passado, 98% devem estar concluídas
                        # Se a data é no futuro próximo (próximos 60 dias), podem estar agendadas
                        if data_agendamento < hoje:
                            # Manutenções passadas: 98% concluídas
                            status_manutencao = 'CONCLUIDA' if random.random() < 0.98 else 'AGENDADA'
                            data_realizacao = data_agendamento + timedelta(days=random.randint(0, 7)) if status_manutencao == 'CONCLUIDA' else None
                        elif data_agendamento <= hoje + timedelta(days=60):
                            # Manutenções próximas: 20% agendadas, 80% concluídas
                            status_manutencao = 'AGENDADA' if random.random() < 0.2 else 'CONCLUIDA'
                            data_realizacao = data_agendamento if status_manutencao == 'CONCLUIDA' else None
                        else:
                            # Manutenções futuras: não criar
                            continue
                        
                        ManutencaoEquipamento.objects.update_or_create(
                            propriedade=propriedade,
                            equipamento=equipamento,
                            data_agendamento=data_agendamento,
                            descricao=f'Manutenção {mes}/{ano} - {equipamento.nome}',
                            defaults={
                                'tipo': random.choice(['PREVENTIVA', 'CORRETIVA', 'REVISAO']),
                                'valor_pecas': Decimal(str(random.uniform(300, 2500))).quantize(Decimal('0.01')),
                                'valor_mao_obra': Decimal(str(random.uniform(500, 4000))).quantize(Decimal('0.01')),
                                'data_realizacao': data_realizacao,
                                'status': status_manutencao
                            }
                        )

        # Empreiteiros
        empreiteiros_criados = 0
        if Empreiteiro:
            empreiteiros_data = [
                {'nome': 'Empreiteiro João Silva', 'especialidade': 'Construção'},
                {'nome': 'Empreiteiro Maria Santos', 'especialidade': 'Pasto'},
                {'nome': 'Empreiteiro Pedro Costa', 'especialidade': 'Manutenção'},
            ]

            for emp_data in empreiteiros_data:
                empreiteiro, _ = Empreiteiro.objects.get_or_create(
                    propriedade=propriedade,
                    nome=emp_data['nome'],
                    defaults={
                        'especialidade': emp_data['especialidade'],
                        'telefone': f'(00) {random.randint(3000, 9999)}-{random.randint(1000, 9999)}',
                        'ativo': True
                    }
                )
                empreiteiros_criados += 1

                # Serviços de empreiteiros mensais (mínimo 232 total)
                if ServicoEmpreiteiro:
                    # Gerar pelo menos 2 serviços por mês por empreiteiro
                    for mes in range(1, 13):
                        num_servicos = random.randint(2, 4) if grande_porte else random.randint(1, 3)
                        for i in range(num_servicos):
                            data_inicio = date(ano, mes, random.randint(1, 20))
                            data_fim = data_inicio + timedelta(days=random.randint(1, 10))
                            valor_orcamento = Decimal(str(random.uniform(1000, 10000))).quantize(Decimal('0.01')) if grande_porte else Decimal(str(random.uniform(500, 3000))).quantize(Decimal('0.01'))
                            status_servico = random.choice(['ORCAMENTO', 'APROVADO', 'EM_ANDAMENTO', 'CONCLUIDO'])
                            
                            ServicoEmpreiteiro.objects.update_or_create(
                                propriedade=propriedade,
                                empreiteiro=empreiteiro,
                                descricao=f'Serviço {emp_data["especialidade"]} - {mes}/{ano} - Item {i+1}',
                                data_inicio=data_inicio,
                                defaults={
                                    'data_fim': data_fim if status_servico in ['CONCLUIDO', 'EM_ANDAMENTO'] else None,
                                    'valor_orcamento': valor_orcamento,
                                    'valor_final': valor_orcamento if status_servico == 'CONCLUIDO' else None,
                                    'status': status_servico
                                }
                            )

        total_operacional = abastecimentos_criados + consumos_criados + compras_suplementacao_criadas
        self.stdout.write(f"    ✅ {len(tanques)} tanques, {abastecimentos_criados} abastecimentos, {consumos_criados} consumos")
        self.stdout.write(f"    ✅ {estoques_criados} estoques, {compras_suplementacao_criadas} compras suplementação")
        self.stdout.write(f"    ✅ {equipamentos_criados} equipamentos, {empreiteiros_criados} empreiteiros")
        self.stdout.write(f"    ✅ Total operacional: {total_operacional} lançamentos")

    def _popular_funcionarios(self, propriedade, skip_existing, ano, grande_porte):
        """Popular módulo de Funcionários - Folha mensal"""
        self.stdout.write("  👥 Módulo Funcionários...")

        if not Funcionario:
            self.stdout.write("    ⚠️ Modelos de funcionários não disponíveis")
            return

        # Mais funcionários para fazenda grande
        if grande_porte:
            funcionarios_data = [
                {'nome': 'João Silva', 'cpf': f'{propriedade.id:03d}11111111', 'cargo': 'Gerente', 'salario': Decimal('5000.00')},
                {'nome': 'Maria Santos', 'cpf': f'{propriedade.id:03d}22222222', 'cargo': 'Vaqueiro', 'salario': Decimal('3000.00')},
                {'nome': 'Pedro Oliveira', 'cpf': f'{propriedade.id:03d}33333333', 'cargo': 'Vaqueiro', 'salario': Decimal('3000.00')},
                {'nome': 'Carlos Souza', 'cpf': f'{propriedade.id:03d}44444444', 'cargo': 'Auxiliar', 'salario': Decimal('2000.00')},
                {'nome': 'Ana Costa', 'cpf': f'{propriedade.id:03d}55555555', 'cargo': 'Auxiliar', 'salario': Decimal('2000.00')},
                {'nome': 'Roberto Lima', 'cpf': f'{propriedade.id:03d}66666666', 'cargo': 'Motorista', 'salario': Decimal('2500.00')},
            ]
        else:
            funcionarios_data = [
                {'nome': 'João Silva', 'cpf': f'{propriedade.id:03d}11111111', 'cargo': 'Gerente', 'salario': Decimal('3500.00')},
                {'nome': 'Maria Santos', 'cpf': f'{propriedade.id:03d}22222222', 'cargo': 'Vaqueiro', 'salario': Decimal('2500.00')},
                {'nome': 'Pedro Oliveira', 'cpf': f'{propriedade.id:03d}33333333', 'cargo': 'Auxiliar', 'salario': Decimal('1800.00')},
            ]

        for func_data in funcionarios_data:
            funcionario, _ = Funcionario.objects.get_or_create(
                propriedade=propriedade,
                cpf=func_data['cpf'],
                defaults={
                    'nome': func_data['nome'],
                    'cargo': func_data['cargo'],
                    'salario_base': func_data['salario'],
                    'tipo_contrato': 'CLT',
                    'situacao': 'ATIVO',
                    'data_admissao': date(ano, 1, 1) - timedelta(days=random.randint(100, 1000))
                }
            )

            # Criar folha de pagamento mensal
            if FolhaPagamento:
                for mes in range(1, 13):
                    data_vencimento = date(ano, mes, 5)
                    competencia = f"{mes:02d}/{ano}"
                    FolhaPagamento.objects.update_or_create(
                        propriedade=propriedade,
                        competencia=competencia,
                        defaults={
                            'data_vencimento': data_vencimento,
                            'status': 'PAGA',
                            'total_proventos': Decimal('0.00'),
                            'total_descontos': Decimal('0.00'),
                            'total_liquido': Decimal('0.00')
                        }
                    )

        self.stdout.write(f"    ✅ {len(funcionarios_data)} funcionários e 12 folhas de pagamento criados")

    def _popular_compras(self, propriedade, skip_existing, ano, grande_porte):
        """Popular módulo de Compras - Muitos dados"""
        self.stdout.write("  🛒 Módulo Compras...")

        if not Fornecedor:
            self.stdout.write("    ⚠️ Modelos de compras não disponíveis")
            return

        # Criar muitos fornecedores
        fornecedores_data = [
            {'nome': 'Agropecuária Central Ltda', 'tipo': 'RACAO', 'cpf_cnpj': f'{propriedade.id:02d}000000000001'},
            {'nome': 'Farmácia Veterinária São Bento', 'tipo': 'MEDICAMENTO', 'cpf_cnpj': f'{propriedade.id:02d}000000000002'},
            {'nome': 'Posto Combustível Rural', 'tipo': 'COMBUSTIVEL', 'cpf_cnpj': f'{propriedade.id:02d}000000000003'},
            {'nome': 'Máquinas e Equipamentos Agro', 'tipo': 'EQUIPAMENTO', 'cpf_cnpj': f'{propriedade.id:02d}000000000004'},
            {'nome': 'Serviços Rurais Especializados', 'tipo': 'SERVICO', 'cpf_cnpj': f'{propriedade.id:02d}000000000005'},
            {'nome': 'Distribuidora de Insumos', 'tipo': 'RACAO', 'cpf_cnpj': f'{propriedade.id:02d}000000000006'},
        ]

        fornecedores_criados = []
        for forn_data in fornecedores_data:
            fornecedor, _ = Fornecedor.objects.get_or_create(
                cpf_cnpj=forn_data['cpf_cnpj'],
                defaults={
                    'propriedade': propriedade,
                    'nome': forn_data['nome'],
                    'tipo': forn_data['tipo'],
                    'telefone': f'(00) {random.randint(3000, 9999)}-{random.randint(1000, 9999)}',
                    'email': f'fornecedor{forn_data["tipo"].lower()}@exemplo.com',
                    'cidade': 'Campo Grande',
                    'estado': 'MS',
                    'ativo': True
                }
            )
            fornecedores_criados.append(fornecedor)

        # Criar MUITAS ordens de compra mensais (mínimo 232 total)
        ordens_criadas = 0
        if OrdemCompra:
            # Gerar pelo menos 20 ordens por mês para garantir 240+ total
            for mes in range(1, 13):
                num_ordens = random.randint(20, 30) if grande_porte else random.randint(15, 25)
                for i in range(num_ordens):
                    data_emissao = date(ano, mes, random.randint(1, 25))
                    fornecedor = random.choice(fornecedores_criados)
                    valor_total = Decimal(str(random.uniform(5000, 50000))).quantize(Decimal('0.01')) if grande_porte else Decimal(str(random.uniform(1000, 10000))).quantize(Decimal('0.01'))
                    
                    numero_ordem = f"OC-{ano}-{mes:02d}-{i+1:04d}"
                    
                    ordem, _ = OrdemCompra.objects.get_or_create(
                        numero_ordem=numero_ordem,
                        defaults={
                            'propriedade': propriedade,
                            'fornecedor': fornecedor,
                            'data_emissao': data_emissao,
                            'data_entrega_prevista': data_emissao + timedelta(days=random.randint(7, 30)),
                            'valor_total': valor_total,
                            'status': random.choice(['APROVADA', 'ENVIADA', 'RECEBIDA']),
                            'observacoes': f'Ordem de compra {mes}/{ano} - Item {i+1}'
                        }
                    )
                    ordens_criadas += 1

        # Criar MUITAS notas fiscais mensais (mínimo 232 total)
        notas_criadas = 0
        if NotaFiscal:
            # Gerar pelo menos 20 notas por mês para garantir 240+ total
            for mes in range(1, 13):
                num_notas = random.randint(20, 30) if grande_porte else random.randint(15, 25)
                for i in range(num_notas):
                    data_emissao = date(ano, mes, random.randint(1, 28))
                    fornecedor = random.choice(fornecedores_criados)
                    valor_produtos = Decimal(str(random.uniform(3000, 40000))).quantize(Decimal('0.01')) if grande_porte else Decimal(str(random.uniform(500, 5000))).quantize(Decimal('0.01'))
                    valor_frete = Decimal(str(random.uniform(100, 1000))).quantize(Decimal('0.01'))
                    valor_total = valor_produtos + valor_frete
                    
                    numero_nf = f"{mes:02d}{random.randint(100000, 999999)}"
                    chave_acesso = f"{ano}{mes:02d}{propriedade.id:02d}{random.randint(100000000000000000000000000000000000, 999999999999999999999999999999999999):036d}"
                    
                    nota, _ = NotaFiscal.objects.get_or_create(
                        chave_acesso=chave_acesso,
                        defaults={
                            'propriedade': propriedade,
                            'fornecedor': fornecedor,
                            'tipo': 'ENTRADA',
                            'numero': numero_nf,
                            'serie': '1',
                            'data_emissao': data_emissao,
                            'data_entrada': data_emissao + timedelta(days=random.randint(1, 5)),
                            'valor_produtos': valor_produtos,
                            'valor_frete': valor_frete,
                            'valor_total': valor_total,
                            'status': 'AUTORIZADA'
                        }
                    )
                    notas_criadas += 1

        total_compras = ordens_criadas + notas_criadas
        self.stdout.write(f"    ✅ {len(fornecedores_criados)} fornecedores, {ordens_criadas} ordens de compra e {notas_criadas} notas fiscais ({total_compras} lançamentos totais)")

    def _popular_pastagens(self, propriedade, skip_existing, ano, grande_porte):
        """Popular módulo de Pastagens"""
        self.stdout.write("  🌿 Módulo Pastagens...")

        if not Pastagem:
            self.stdout.write("    ⚠️ Modelos de pastagens não disponíveis")
            return

        # Criar pastagens
        pastagens_data = [
            {'nome': 'Pastagem 1 - Brachiaria', 'area_ha': Decimal('200.00'), 'tipo': 'BRAQUIARIA'},
            {'nome': 'Pastagem 2 - Panicum', 'area_ha': Decimal('150.00'), 'tipo': 'PANICUM'},
            {'nome': 'Pastagem 3 - Capim Mombaça', 'area_ha': Decimal('180.00'), 'tipo': 'MOMBACA'},
        ]

        for past_data in pastagens_data:
            Pastagem.objects.get_or_create(
                propriedade=propriedade,
                nome=past_data['nome'],
                defaults={
                    'area_ha': past_data['area_ha'],
                    'tipo_pastagem': past_data['tipo'],
                    'status': 'ATIVA'
                }
            )

        self.stdout.write("    ✅ Pastagens criadas")

    def _popular_financeiro(self, propriedade, skip_existing, ano, grande_porte):
        """Popular módulo Financeiro - Muitos lançamentos"""
        self.stdout.write("  💰 Módulo Financeiro...")

        # Custos Fixos (mais para fazenda grande)
        if grande_porte:
            custos_fixos_data = [
                {'nome_custo': 'Mão de Obra', 'valor_mensal': Decimal('15000.00'), 'tipo_custo': 'PESSOAL'},
                {'nome_custo': 'Energia Elétrica', 'valor_mensal': Decimal('1500.00'), 'tipo_custo': 'INFRAESTRUTURA'},
                {'nome_custo': 'Combustível', 'valor_mensal': Decimal('5000.00'), 'tipo_custo': 'OPERACIONAL'},
                {'nome_custo': 'Manutenção de Equipamentos', 'valor_mensal': Decimal('3000.00'), 'tipo_custo': 'OPERACIONAL'},
                {'nome_custo': 'Telefone e Internet', 'valor_mensal': Decimal('500.00'), 'tipo_custo': 'ADMINISTRATIVO'},
                {'nome_custo': 'Seguros', 'valor_mensal': Decimal('2000.00'), 'tipo_custo': 'FINANCEIRO'},
            ]
        else:
            custos_fixos_data = [
                {'nome_custo': 'Mão de Obra', 'valor_mensal': Decimal('8000.00'), 'tipo_custo': 'PESSOAL'},
                {'nome_custo': 'Energia Elétrica', 'valor_mensal': Decimal('800.00'), 'tipo_custo': 'INFRAESTRUTURA'},
                {'nome_custo': 'Combustível', 'valor_mensal': Decimal('2000.00'), 'tipo_custo': 'OPERACIONAL'},
                {'nome_custo': 'Manutenção', 'valor_mensal': Decimal('1500.00'), 'tipo_custo': 'OPERACIONAL'},
            ]

        for custo_data in custos_fixos_data:
            CustoFixo.objects.update_or_create(
                propriedade=propriedade,
                nome_custo=custo_data['nome_custo'],
                defaults=custo_data
            )

        # Custos Variáveis
        custos_variaveis_data = [
            {'nome_custo': 'Ração', 'tipo_custo': 'ALIMENTACAO', 'valor_por_cabeca': Decimal('45.00')},
            {'nome_custo': 'Medicamentos', 'tipo_custo': 'SANEAMENTO', 'valor_por_cabeca': Decimal('15.00')},
            {'nome_custo': 'Vacinas', 'tipo_custo': 'SANEAMENTO', 'valor_por_cabeca': Decimal('8.00')},
            {'nome_custo': 'Sal Mineral', 'tipo_custo': 'ALIMENTACAO', 'valor_por_cabeca': Decimal('5.00')},
        ]

        for custo_data in custos_variaveis_data:
            CustoVariavel.objects.update_or_create(
                propriedade=propriedade,
                nome_custo=custo_data['nome_custo'],
                defaults=custo_data
            )

        # Criar tipos de financiamento se não existirem
        from gestao_rural.models import TipoFinanciamento
        tipo_rural, _ = TipoFinanciamento.objects.get_or_create(
            nome='Financiamento Rural',
            defaults={'descricao': 'Financiamento para atividades rurais'}
        )
        tipo_investimento, _ = TipoFinanciamento.objects.get_or_create(
            nome='Empréstimo Investimento',
            defaults={'descricao': 'Empréstimo para investimentos'}
        )

        # Financiamentos (múltiplos)
        financiamentos_data = [
            {
                'nome': 'Financiamento Rural - Banco do Brasil',
                'tipo': tipo_rural,
                'valor_principal': Decimal('200000.00') if grande_porte else Decimal('150000.00'),
                'taxa_juros_anual': Decimal('8.5'),
                'numero_parcelas': 60,
                'data_contratacao': date(ano, 1, 15),
                'data_primeiro_vencimento': date(ano, 2, 15),
                'data_ultimo_vencimento': date(ano + 5, 1, 15),
                'valor_parcela': Decimal('3500.00') if grande_porte else Decimal('2500.00'),
            },
            {
                'nome': 'Empréstimo Investimento - Caixa',
                'tipo': tipo_investimento,
                'valor_principal': Decimal('100000.00') if grande_porte else Decimal('50000.00'),
                'taxa_juros_anual': Decimal('12.0'),
                'numero_parcelas': 36,
                'data_contratacao': date(ano, 3, 10),
                'data_primeiro_vencimento': date(ano, 4, 10),
                'data_ultimo_vencimento': date(ano + 3, 3, 10),
                'valor_parcela': Decimal('3200.00') if grande_porte else Decimal('1600.00'),
            },
        ]

        for fin_data in financiamentos_data:
            Financiamento.objects.update_or_create(
                propriedade=propriedade,
                nome=fin_data['nome'],
                defaults=fin_data
            )

        # Calcular valor do rebanho para balancear receitas e despesas
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade, data_inventario=date(ano, 1, 1))
        valor_rebanho = sum(inv.quantidade * inv.valor_por_cabeca for inv in inventario)
        
        # Receita anual estimada: 15% do valor do rebanho (realista para pecuária)
        receita_anual_estimada = valor_rebanho * Decimal('0.15')
        receita_mensal_estimada = receita_anual_estimada / Decimal('12')
        
        # Despesa anual estimada: 10-12% do valor do rebanho (balanceada)
        despesa_anual_estimada = valor_rebanho * Decimal(str(random.uniform(0.10, 0.12)))
        despesa_mensal_estimada = despesa_anual_estimada / Decimal('12')
        
        # Contas a Pagar mensais (COERENTE com despesa mensal estimada)
        contas_pagar_criadas = 0
        total_despesas_criadas = Decimal('0.00')
        try:
            from gestao_rural.models_compras_financeiro import ContaPagar
            fornecedores = Fornecedor.objects.filter(propriedade=propriedade)
            
            if fornecedores.exists():
                # Distribuir despesas mensais de forma realista (8-15 contas por mês)
                for mes in range(1, 13):
                    num_contas = random.randint(8, 15) if grande_porte else random.randint(5, 10)
                    despesa_mes_restante = despesa_mensal_estimada
                    
                    for i in range(num_contas):
                        data_vencimento = date(ano, mes, random.randint(1, 28))
                        fornecedor = random.choice(list(fornecedores))
                        
                        # Calcular valor proporcional (última conta pega o restante)
                        if i == num_contas - 1:
                            valor = despesa_mes_restante
                        else:
                            # Distribuir proporcionalmente
                            percentual = Decimal(str(random.uniform(0.05, 0.25)))  # 5-25% da despesa mensal
                            valor = despesa_mensal_estimada * percentual
                            despesa_mes_restante -= valor
                        
                        valor = max(Decimal('100.00'), valor.quantize(Decimal('0.01')))  # Mínimo R$ 100
                        
                        # Para contas vencidas, 70% devem estar pagas
                        hoje = date.today()
                        if data_vencimento < hoje:
                            status = 'PAGA' if random.random() < 0.7 else 'PENDENTE'
                            data_pagamento = data_vencimento + timedelta(days=random.randint(0, 30)) if status == 'PAGA' else None
                        else:
                            status = 'PENDENTE'
                            data_pagamento = None
                        
                        ContaPagar.objects.update_or_create(
                            propriedade=propriedade,
                            fornecedor=fornecedor,
                            descricao=f'Conta {i+1} - {data_vencimento.strftime("%B %Y")}',
                            data_vencimento=data_vencimento,
                            defaults={
                                'valor': valor,
                                'categoria': random.choice(['Combustível', 'Ração', 'Medicamentos', 'Manutenção', 'Outros']),
                                'status': status,
                                'data_pagamento': data_pagamento,
                                'forma_pagamento': random.choice(['Boleto', 'Transferência', 'Dinheiro', 'Cheque'])
                            }
                        )
                        contas_pagar_criadas += 1
                        total_despesas_criadas += valor
        except ImportError:
            ContaPagar = None

        # Contas a Receber mensais (COERENTE com receita mensal estimada)
        contas_receber_criadas = 0
        total_receitas_criadas = Decimal('0.00')
        try:
            from gestao_rural.models_compras_financeiro import ContaReceber
            
            # Distribuir receitas mensais de forma realista (3-8 vendas por mês)
            for mes in range(1, 13):
                num_contas = random.randint(3, 8) if grande_porte else random.randint(2, 5)
                receita_mes_restante = receita_mensal_estimada
                
                for i in range(num_contas):
                    data_vencimento = date(ano, mes, random.randint(1, 28))
                    
                    # Calcular valor proporcional (última conta pega o restante)
                    if i == num_contas - 1:
                        valor = receita_mes_restante
                    else:
                        # Distribuir proporcionalmente
                        percentual = Decimal(str(random.uniform(0.15, 0.40)))  # 15-40% da receita mensal
                        valor = receita_mensal_estimada * percentual
                        receita_mes_restante -= valor
                    
                    valor = max(Decimal('500.00'), valor.quantize(Decimal('0.01')))  # Mínimo R$ 500
                    
                    # Para contas vencidas, 80% devem estar recebidas
                    hoje = date.today()
                    if data_vencimento < hoje:
                        status = 'RECEBIDA' if random.random() < 0.8 else 'PENDENTE'
                        data_recebimento = data_vencimento + timedelta(days=random.randint(0, 15)) if status == 'RECEBIDA' else None
                    else:
                        status = 'PENDENTE'
                        data_recebimento = None
                    
                    ContaReceber.objects.update_or_create(
                        propriedade=propriedade,
                        descricao=f'Venda de Animais {i+1} - {data_vencimento.strftime("%B %Y")}',
                        data_vencimento=data_vencimento,
                        defaults={
                            'valor': valor,
                            'categoria': 'Venda de Animais',
                            'cliente': f'Cliente {random.randint(1, 50)}',
                            'status': status,
                            'data_recebimento': data_recebimento,
                            'forma_recebimento': random.choice(['Transferência', 'Dinheiro', 'Cheque'])
                        }
                    )
                    contas_receber_criadas += 1
                    total_receitas_criadas += valor
        except ImportError:
            ContaReceber = None

        total_financeiro = contas_pagar_criadas + contas_receber_criadas
        self.stdout.write(f"    ✅ Custos fixos, variáveis, {len(financiamentos_data)} financiamentos criados")
        if contas_pagar_criadas > 0:
            self.stdout.write(f"    ✅ {contas_pagar_criadas} contas a pagar criadas (Total: R$ {total_despesas_criadas:,.2f})")
        if contas_receber_criadas > 0:
            self.stdout.write(f"    ✅ {contas_receber_criadas} contas a receber criadas (Total: R$ {total_receitas_criadas:,.2f})")
        self.stdout.write(f"    ✅ Receitas/Despesas balanceadas: Receita ~15% do rebanho, Despesa ~10-12% do rebanho")

    def _popular_projetos_bancarios(self, propriedade, skip_existing, ano, grande_porte):
        """Popular módulo de Projetos Bancários"""
        self.stdout.write("  🏦 Módulo Projetos Bancários...")

        from gestao_rural.models import ProjetoBancario
        try:
            from gestao_rural.models import DocumentoProjeto
        except ImportError:
            DocumentoProjeto = None

        # Criar MUITOS projetos bancários (mínimo 232 total)
        projetos_data = []
        tipos_projeto = ['CUSTEIO', 'INVESTIMENTO', 'COMERCIALIZACAO', 'REFINANCIAMENTO']
        bancos = ['Banco do Brasil', 'Caixa Econômica Federal', 'Banco do Nordeste', 'Banco da Amazônia', 'Bradesco', 'Itaú']
        
        # Gerar pelo menos 20 projetos por mês para garantir 240+ total
        for mes in range(1, 13):
            num_projetos = random.randint(20, 30) if grande_porte else random.randint(15, 25)
            for i in range(num_projetos):
                projetos_data.append({
                    'nome_projeto': f'Projeto {tipos_projeto[random.randint(0, len(tipos_projeto)-1)]} {mes:02d}/{ano} - {i+1:03d}',
                    'tipo_projeto': tipos_projeto[random.randint(0, len(tipos_projeto)-1)],
                    'banco_solicitado': bancos[random.randint(0, len(bancos)-1)],
                    'valor_solicitado': Decimal(str(random.uniform(100000, 1000000))).quantize(Decimal('0.01')) if grande_porte else Decimal(str(random.uniform(50000, 500000))).quantize(Decimal('0.01')),
                    'prazo_pagamento': random.randint(12, 120),
                    'taxa_juros': Decimal(str(random.uniform(6.0, 12.0))).quantize(Decimal('0.01')),
                    'data_solicitacao': date(ano, mes, random.randint(1, 25)),
                    'status': random.choice(['RASCUNHO', 'EM_ANALISE', 'APROVADO', 'CONTRATADO']),
                })

        projetos_criados = []
        for proj_data in projetos_data:
            projeto, _ = ProjetoBancario.objects.update_or_create(
                propriedade=propriedade,
                nome_projeto=proj_data['nome_projeto'],
                defaults={
                    **proj_data,
                    'valor_aprovado': proj_data['valor_solicitado'] * Decimal('0.9') if proj_data['status'] == 'APROVADO' else None,
                    'data_aprovacao': proj_data['data_solicitacao'] + timedelta(days=30) if proj_data['status'] == 'APROVADO' else None,
                    'observacoes': f'Projeto {proj_data["tipo_projeto"]} para {ano}'
                }
            )
            projetos_criados.append(projeto)

            # Criar documentos para cada projeto
            if DocumentoProjeto:
                tipos_docs = ['PROJETO_TECNICO', 'LAUDO_AVALIACAO', 'CONTRATO']
                for tipo_doc in tipos_docs:
                    DocumentoProjeto.objects.update_or_create(
                        projeto=projeto,
                        tipo_documento=tipo_doc,
                        nome_documento=f'{projeto.nome_projeto} - {tipo_doc}',
                        defaults={
                            'observacoes': f'Documento {tipo_doc} do projeto {projeto.nome_projeto}'
                        }
                    )

        self.stdout.write(f"    ✅ {len(projetos_criados)} projetos bancários criados (mínimo 232)")

    def _popular_bens_patrimonio(self, propriedade, skip_existing, ano, grande_porte):
        """Popular módulo de Bens e Patrimônio"""
        self.stdout.write("  🏛️ Módulo Bens e Patrimônio...")

        if not TipoBem or not BemPatrimonial:
            self.stdout.write("    ⚠️ Modelos de patrimônio não disponíveis")
            return

        # Criar tipos de bens se não existirem (usando categorias do TipoBem)
        tipos_bem_data = [
            {'nome': 'Trator', 'categoria': 'MAQUINA', 'vida_util_anos': 10, 'taxa_depreciacao': Decimal('10.00')},
            {'nome': 'Colheitadeira', 'categoria': 'MAQUINA', 'vida_util_anos': 10, 'taxa_depreciacao': Decimal('10.00')},
            {'nome': 'Plantadeira', 'categoria': 'MAQUINA', 'vida_util_anos': 10, 'taxa_depreciacao': Decimal('10.00')},
            {'nome': 'Pulverizador', 'categoria': 'MAQUINA', 'vida_util_anos': 10, 'taxa_depreciacao': Decimal('10.00')},
            {'nome': 'Caminhão', 'categoria': 'VEICULO', 'vida_util_anos': 5, 'taxa_depreciacao': Decimal('20.00')},
            {'nome': 'Caminhonete', 'categoria': 'VEICULO', 'vida_util_anos': 5, 'taxa_depreciacao': Decimal('20.00')},
            {'nome': 'Galpão', 'categoria': 'INSTALACAO', 'vida_util_anos': 25, 'taxa_depreciacao': Decimal('4.00')},
            {'nome': 'Casa Sede', 'categoria': 'TERRA', 'vida_util_anos': 25, 'taxa_depreciacao': Decimal('4.00')},
            {'nome': 'Silo', 'categoria': 'INSTALACAO', 'vida_util_anos': 15, 'taxa_depreciacao': Decimal('6.67')},
            {'nome': 'Curral', 'categoria': 'INSTALACAO', 'vida_util_anos': 15, 'taxa_depreciacao': Decimal('6.67')},
            {'nome': 'Cerca Elétrica', 'categoria': 'TERRA', 'vida_util_anos': 10, 'taxa_depreciacao': Decimal('10.00')},
            {'nome': 'Sistema de Irrigação', 'categoria': 'TERRA', 'vida_util_anos': 10, 'taxa_depreciacao': Decimal('10.00')},
        ]

        tipos_criados = []
        for tipo_data in tipos_bem_data:
            tipo, _ = TipoBem.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults={
                    'categoria': tipo_data['categoria'],
                    'vida_util_anos': tipo_data['vida_util_anos'],
                    'taxa_depreciacao': tipo_data['taxa_depreciacao']
                }
            )
            tipos_criados.append(tipo)

        # Criar MUITOS bens patrimoniais (mínimo 232 total)
        bens_data = []
        tipos_maquinas = ['Trator', 'Colheitadeira', 'Plantadeira', 'Pulverizador', 'Grade', 'Arado', 'Semeadora', 'Enxada Rotativa']
        tipos_veiculos = ['Caminhão', 'Caminhonete', 'Trator de Esteira', 'Moto', 'Carreta']
        tipos_construcoes = ['Galpão', 'Casa Sede', 'Silo', 'Curral', 'Escritório', 'Alojamento']
        tipos_benfeitorias = ['Cerca Elétrica', 'Sistema de Irrigação', 'Poço Artesiano', 'Estrada Interna', 'Ponte']
        
        # Gerar pelo menos 20 bens por mês para garantir 240+ total
        for mes in range(1, 13):
            num_bens = random.randint(20, 30) if grande_porte else random.randint(15, 25)
            for i in range(num_bens):
                tipo_categoria = random.choice(['MAQUINA', 'VEICULO', 'INSTALACAO', 'TERRA', 'OUTRO'])
                
                if tipo_categoria == 'MAQUINA':
                    descricao = f'{tipos_maquinas[random.randint(0, len(tipos_maquinas)-1)]} {i+1}'
                    valor = Decimal(str(random.uniform(30000, 800000))).quantize(Decimal('0.01'))
                elif tipo_categoria == 'VEICULO':
                    descricao = f'{tipos_veiculos[random.randint(0, len(tipos_veiculos)-1)]} {i+1}'
                    valor = Decimal(str(random.uniform(50000, 300000))).quantize(Decimal('0.01'))
                elif tipo_categoria == 'INSTALACAO':
                    descricao = f'{tipos_construcoes[random.randint(0, len(tipos_construcoes)-1)]} {i+1}'
                    valor = Decimal(str(random.uniform(50000, 500000))).quantize(Decimal('0.01'))
                else:  # TERRA ou OUTRO
                    descricao = f'{tipos_benfeitorias[random.randint(0, len(tipos_benfeitorias)-1)]} {i+1}'
                    valor = Decimal(str(random.uniform(20000, 200000))).quantize(Decimal('0.01'))
                
                # Selecionar um tipo de bem correspondente à categoria
                tipos_filtrados = [t for t in tipos_criados if t.categoria == tipo_categoria]
                tipo_bem = random.choice(tipos_filtrados) if tipos_filtrados else tipos_criados[0]
                
                bens_data.append({
                    'descricao': f'{descricao} - {mes:02d}/{ano}',
                    'tipo_bem': tipo_bem,
                    'valor': valor
                })

        bens_criados = 0
        estados = ['NOVO', 'OTIMO', 'BOM', 'REGULAR', 'RUIM']
        for bem_data in bens_data:
            # Data de aquisição variando entre 1 ano atrás e 10 anos atrás
            data_aquisicao = date(ano, 1, 1) - timedelta(days=random.randint(365, 3650))
            
            bem, _ = BemPatrimonial.objects.update_or_create(
                propriedade=propriedade,
                tipo_bem=bem_data['tipo_bem'],
                descricao=bem_data['descricao'],
                defaults={
                    'valor_aquisicao': bem_data['valor'],
                    'valor_residual': bem_data['valor'] * Decimal('0.1'),
                    'data_aquisicao': data_aquisicao,
                    'quantidade': random.randint(1, 3),
                    'estado_conservacao': random.choice(estados),
                    'ativo': True
                }
            )
            bens_criados += 1

        self.stdout.write(f"    ✅ {len(tipos_criados)} tipos de bens, {bens_criados} bens patrimoniais criados (mínimo 232)")

    def _popular_movimentacoes_anuais(self, propriedade, skip_existing, ano, grande_porte):
        """Criar movimentações mensais ao longo do ano 2025"""
        self.stdout.write("  📅 Criando movimentações mensais de 2025...")

        from gestao_rural.models import PlanejamentoAnual, CenarioPlanejamento

        # Criar PlanejamentoAnual para o ano
        planejamento, _ = PlanejamentoAnual.objects.get_or_create(
            propriedade=propriedade,
            ano=ano,
            defaults={
                'descricao': f'Planejamento anual {ano} - Simulação completa',
                'status': 'APROVADO'
            }
        )

        # Criar CenarioPlanejamento (Baseline)
        cenario, _ = CenarioPlanejamento.objects.get_or_create(
            planejamento=planejamento,
            nome='Baseline',
            defaults={
                'descricao': 'Cenário base de planejamento',
                'is_baseline': True
            }
        )

        categorias = CategoriaAnimal.objects.filter(ativo=True)
        movimentacoes_criadas = 0
        nascimentos_criados = 0

        # Criar movimentações para cada mês do ano
        for mes in range(1, 13):
            data_mes = date(ano, mes, 15)  # Dia 15 de cada mês
            
            # VENDAS - Mais frequentes em meses específicos (março, junho, setembro, dezembro)
            if mes in [3, 6, 9, 12]:
                categorias_venda = categorias.filter(sexo='M')  # Vender machos
                for categoria in categorias_venda[:3]:
                    quantidade = random.randint(20, 100) if grande_porte else random.randint(5, 20)
                    valor_por_cabeca = Decimal(str(random.uniform(1500, 2500))).quantize(Decimal('0.01'))
                    
                    # Criar múltiplas vendas por mês para garantir mais lançamentos
                    num_vendas = random.randint(2, 5) if grande_porte else 1
                    for venda_idx in range(num_vendas):
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            planejamento=planejamento,
                            cenario=cenario,
                            data_movimentacao=data_mes,
                            tipo_movimentacao='VENDA',
                            categoria=categoria,
                            quantidade=quantidade,
                            valor_por_cabeca=valor_por_cabeca,
                            valor_total=quantidade * valor_por_cabeca,
                            observacao=f'Venda mensal {venda_idx+1} - {data_mes.strftime("%B %Y")}'
                        )
                    movimentacoes_criadas += 1

            # NASCIMENTOS - Mais frequentes após estações de monta (setembro a dezembro)
            if mes in [9, 10, 11, 12]:
                categoria_bezerro = categorias.filter(nome__icontains='Bezerro').first()
                categoria_bezerra = categorias.filter(nome__icontains='Bezerra').first()
                
                for categoria in [categoria_bezerro, categoria_bezerra]:
                    if not categoria:
                        continue
                    quantidade = random.randint(30, 150) if grande_porte else random.randint(5, 30)
                    
                    # Criar múltiplos nascimentos por mês
                    num_nascimentos = random.randint(2, 4) if grande_porte else 1
                    for nasc_idx in range(num_nascimentos):
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            planejamento=planejamento,
                            cenario=cenario,
                            data_movimentacao=data_mes,
                            tipo_movimentacao='NASCIMENTO',
                            categoria=categoria,
                            quantidade=quantidade,
                            valor_por_cabeca=Decimal('0.00'),
                            valor_total=Decimal('0.00'),
                            observacao=f'Nascimentos {nasc_idx+1} - {data_mes.strftime("%B %Y")}'
                        )
                    nascimentos_criados += 1

            # COMPRAS - Esporádicas (fevereiro, maio, agosto)
            if mes in [2, 5, 8]:
                categoria_compra = categorias.filter(sexo='F').first()  # Comprar fêmeas
                if categoria_compra:
                    quantidade = random.randint(10, 50) if grande_porte else random.randint(3, 10)
                    valor_por_cabeca = Decimal(str(random.uniform(2000, 3500))).quantize(Decimal('0.01'))
                    
                    # Criar múltiplas compras por mês
                    num_compras = random.randint(2, 3) if grande_porte else 1
                    for compra_idx in range(num_compras):
                        MovimentacaoProjetada.objects.create(
                            propriedade=propriedade,
                            planejamento=planejamento,
                            cenario=cenario,
                            data_movimentacao=data_mes,
                            tipo_movimentacao='COMPRA',
                            categoria=categoria_compra,
                            quantidade=quantidade,
                            valor_por_cabeca=valor_por_cabeca,
                            valor_total=quantidade * valor_por_cabeca,
                            observacao=f'Compra de matrizes {compra_idx+1} - {data_mes.strftime("%B %Y")}'
                        )
                    movimentacoes_criadas += 1

            # Criar lançamentos financeiros mensais
            if FluxoCaixa:
                # Calcular valores baseados nas movimentações do mês
                receita_vendas = MovimentacaoProjetada.objects.filter(
                    propriedade=propriedade,
                    data_movimentacao__year=ano,
                    data_movimentacao__month=mes,
                    tipo_movimentacao='VENDA'
                ).aggregate(total=models.Sum('valor_total'))['total'] or Decimal('0.00')

                custo_fixo = CustoFixo.objects.filter(propriedade=propriedade).aggregate(
                    total=models.Sum('valor_mensal')
                )['total'] or Decimal('0.00')

                # Calcular custo variável baseado no inventário
                total_animais = InventarioRebanho.objects.filter(
                    propriedade=propriedade,
                    data_inventario__lte=data_mes
                ).aggregate(total=models.Sum('quantidade'))['total'] or 0

                custo_variavel = CustoVariavel.objects.filter(propriedade=propriedade).aggregate(
                    total=models.Sum('valor_por_cabeca')
                )['total'] or Decimal('0.00')
                custo_variavel_total = custo_variavel * Decimal(str(total_animais))

                lucro_bruto = receita_vendas - custo_fixo - custo_variavel_total
                margem = (lucro_bruto / receita_vendas * 100) if receita_vendas > 0 else Decimal('0.00')

                FluxoCaixa.objects.update_or_create(
                    propriedade=propriedade,
                    data_referencia=data_mes,
                    defaults={
                        'receita_total': receita_vendas,
                        'custo_fixo_total': custo_fixo,
                        'custo_variavel_total': custo_variavel_total,
                        'lucro_bruto': lucro_bruto,
                        'margem_lucro': margem
                    }
                )

        # Contar movimentações criadas
        total_movimentacoes = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            planejamento=planejamento,
            cenario=cenario
        ).count()
        
        self.stdout.write(f"    ✅ {total_movimentacoes} movimentações projetadas criadas (vinculadas ao planejamento)")
        self.stdout.write(f"    ✅ Planejamento {ano} e cenário Baseline criados")
        self.stdout.write(f"    ✅ 12 lançamentos de fluxo de caixa mensais criados")
        
        # Criar lançamentos financeiros baseados nas contas a pagar e receber
        self._popular_lancamentos_financeiros(propriedade, ano, grande_porte)

    def _popular_lancamentos_financeiros(self, propriedade, ano, grande_porte):
        """Criar lançamentos financeiros baseados nas contas a pagar e receber"""
        self.stdout.write("  💳 Criando lançamentos financeiros...")
        
        try:
            from gestao_rural.models_financeiro import (
                LancamentoFinanceiro, CategoriaFinanceira, ContaFinanceira, CentroCusto
            )
            from gestao_rural.models_compras_financeiro import ContaPagar, ContaReceber
        except ImportError:
            self.stdout.write("    ⚠️ Modelos financeiros não disponíveis")
            return
        
        # Criar conta financeira padrão se não existir
        conta_padrao, _ = ContaFinanceira.objects.get_or_create(
            propriedade=propriedade,
            nome='Conta Principal',
            defaults={
                'tipo': ContaFinanceira.TIPO_CORRENTE,
                'banco': 'Banco do Brasil',
                'saldo_inicial': Decimal('0.00'),
                'data_saldo_inicial': date(ano, 1, 1)
            }
        )
        
        # Criar centros de custo se não existirem
        centros_custo_data = [
            {'codigo': 'PEC', 'nome': 'Pecuária', 'tipo': CentroCusto.TIPO_OPERACIONAL},
            {'codigo': 'AGR', 'nome': 'Agricultura', 'tipo': CentroCusto.TIPO_OPERACIONAL},
            {'codigo': 'INF', 'nome': 'Infraestrutura', 'tipo': CentroCusto.TIPO_OPERACIONAL},
            {'codigo': 'ADM', 'nome': 'Administração', 'tipo': CentroCusto.TIPO_ADMINISTRATIVO},
            {'codigo': 'INV', 'nome': 'Investimentos', 'tipo': CentroCusto.TIPO_INVESTIMENTO},
        ]
        
        centros_custo = []
        for cc_data in centros_custo_data:
            # Preparar defaults com todos os campos possíveis
            defaults = {
                'tipo': cc_data['tipo'],
                'descricao': f'Centro de custo {cc_data["nome"]}',
                'ativo': True,
                'codigo': cc_data['codigo']  # Sempre incluir codigo (campo obrigatório no banco)
            }
            
            # Tentar criar usando get_or_create com codigo (campo obrigatório)
            try:
                centro, _ = CentroCusto.objects.get_or_create(
                    propriedade=propriedade,
                    codigo=cc_data['codigo'],
                    defaults=defaults
                )
            except Exception as e:
                # Se falhar, tentar criar diretamente
                try:
                    centro = CentroCusto.objects.create(
                        propriedade=propriedade,
                        codigo=cc_data['codigo'],
                        nome=cc_data['nome'],
                        tipo=cc_data['tipo'],
                        descricao=f'Centro de custo {cc_data["nome"]}',
                        ativo=True
                    )
                except Exception:
                    # Se ainda falhar, tentar sem codigo (fallback)
                    defaults.pop('codigo', None)
                    centro, _ = CentroCusto.objects.get_or_create(
                        propriedade=propriedade,
                        nome=cc_data['nome'],
                        defaults=defaults
                    )
            centros_custo.append(centro)
        
        # Criar categorias financeiras se não existirem
        categorias_receita = []
        categorias_despesa = []
        
        # Categorias de receita
        cat_receitas = [
            {'nome': 'Venda de Animais', 'tipo': CategoriaFinanceira.TIPO_RECEITA},
            {'nome': 'Venda de Produção', 'tipo': CategoriaFinanceira.TIPO_RECEITA},
            {'nome': 'Outras Receitas', 'tipo': CategoriaFinanceira.TIPO_RECEITA},
        ]
        
        for cat_data in cat_receitas:
            categoria, _ = CategoriaFinanceira.objects.get_or_create(
                propriedade=propriedade,
                nome=cat_data['nome'],
                defaults={
                    'tipo': cat_data['tipo'],
                    'descricao': f'Categoria de {cat_data["nome"]}'
                }
            )
            categorias_receita.append(categoria)
        
        # Categorias de despesa
        cat_despesas = [
            {'nome': 'Combustível', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Ração', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Medicamentos', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Manutenção', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Salários', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
            {'nome': 'Outras Despesas', 'tipo': CategoriaFinanceira.TIPO_DESPESA},
        ]
        
        for cat_data in cat_despesas:
            categoria, _ = CategoriaFinanceira.objects.get_or_create(
                propriedade=propriedade,
                nome=cat_data['nome'],
                defaults={
                    'tipo': cat_data['tipo'],
                    'descricao': f'Categoria de {cat_data["nome"]}'
                }
            )
            categorias_despesa.append(categoria)
        
        lancamentos_criados = 0
        
        # Criar lançamentos a partir de Contas a Receber
        if ContaReceber:
            contas_receber = ContaReceber.objects.filter(
                propriedade=propriedade,
                data_vencimento__year=ano
            )
            
            hoje = date.today()
            for conta in contas_receber:
                categoria = categorias_receita[0] if categorias_receita else None
                if not categoria:
                    continue
                
                # Selecionar centro de custo aleatório (maioria em Pecuária)
                centro_custo = random.choices(
                    centros_custo,
                    weights=[40, 20, 15, 15, 10]  # 40% Pecuária, 20% Agricultura, etc.
                )[0] if centros_custo else None
                
                # Se a conta está vencida, marcar como recebida e quitada
                # Se está no futuro, pode estar pendente
                if conta.data_vencimento < hoje:
                    # Contas vencidas: 85% recebidas e quitadas
                    status_conta = 'RECEBIDA' if random.random() < 0.85 else 'PENDENTE'
                    data_recebimento = conta.data_vencimento + timedelta(days=random.randint(0, 15)) if status_conta == 'RECEBIDA' else None
                else:
                    # Contas futuras: 30% já recebidas (adiantadas)
                    status_conta = 'RECEBIDA' if random.random() < 0.3 else 'PENDENTE'
                    data_recebimento = conta.data_vencimento - timedelta(days=random.randint(0, 30)) if status_conta == 'RECEBIDA' else None
                
                # Usar data de recebimento como competência se recebida, senão usar data de vencimento
                data_competencia = data_recebimento if data_recebimento else conta.data_vencimento
                
                LancamentoFinanceiro.objects.update_or_create(
                    propriedade=propriedade,
                    descricao=conta.descricao,
                    data_competencia=data_competencia,
                    data_vencimento=conta.data_vencimento,
                    defaults={
                        'categoria': categoria,
                        'tipo': CategoriaFinanceira.TIPO_RECEITA,
                        'valor': conta.valor,
                        'conta_destino': conta_padrao,
                        'centro_custo': centro_custo,
                        'data_quitacao': data_recebimento,
                        'status': 'QUITADO' if status_conta == 'RECEBIDA' else 'PENDENTE',
                        'forma_pagamento': getattr(conta, 'forma_recebimento', 'PIX') or 'PIX',
                        'documento_referencia': f'CR-{conta.id}',
                        'observacoes': f'Conta a receber: {conta.descricao}'
                    }
                )
                lancamentos_criados += 1
        
        # Criar lançamentos a partir de Contas a Pagar
        if ContaPagar:
            contas_pagar = ContaPagar.objects.filter(
                propriedade=propriedade,
                data_vencimento__year=ano
            )
            
            for conta in contas_pagar:
                # Mapear categoria da conta para categoria financeira
                categoria_nome = conta.categoria or 'Outras Despesas'
                categoria = next(
                    (c for c in categorias_despesa if c.nome == categoria_nome),
                    categorias_despesa[-1] if categorias_despesa else None
                )
                if not categoria:
                    continue
                
                # Mapear categoria da conta para centro de custo
                if 'Combustível' in categoria_nome or 'Manutenção' in categoria_nome:
                    centro_custo = next((cc for cc in centros_custo if cc.nome == 'Infraestrutura'), centros_custo[0] if centros_custo else None)
                elif 'Ração' in categoria_nome or 'Medicamentos' in categoria_nome:
                    centro_custo = next((cc for cc in centros_custo if cc.nome == 'Pecuária'), centros_custo[0] if centros_custo else None)
                elif 'Salários' in categoria_nome:
                    centro_custo = next((cc for cc in centros_custo if cc.nome == 'Administração'), centros_custo[0] if centros_custo else None)
                else:
                    # Selecionar centro de custo aleatório
                    centro_custo = random.choices(
                        centros_custo,
                        weights=[40, 20, 15, 15, 10]  # 40% Pecuária, 20% Agricultura, etc.
                    )[0] if centros_custo else None
                
                # Se a conta está paga, criar lançamento quitado
                if conta.status == 'PAGA' and conta.data_pagamento:
                    LancamentoFinanceiro.objects.update_or_create(
                        propriedade=propriedade,
                        descricao=conta.descricao,
                        data_competencia=conta.data_pagamento,  # Usar data de pagamento como competência
                        data_vencimento=conta.data_vencimento,
                        defaults={
                            'categoria': categoria,
                            'tipo': CategoriaFinanceira.TIPO_DESPESA,
                            'valor': conta.valor,
                            'conta_origem': conta_padrao,
                            'centro_custo': centro_custo,
                            'data_quitacao': conta.data_pagamento,
                            'status': 'QUITADO',
                            'forma_pagamento': getattr(conta, 'forma_pagamento', 'PIX') or 'PIX',
                            'documento_referencia': f'CP-{conta.id}',
                            'observacoes': f'Conta a pagar: {conta.descricao}'
                        }
                    )
                    lancamentos_criados += 1
                elif conta.status == 'PENDENTE' or conta.status == 'VENCIDA':
                    # Criar também lançamentos pendentes para controle
                    LancamentoFinanceiro.objects.update_or_create(
                        propriedade=propriedade,
                        descricao=conta.descricao,
                        data_competencia=conta.data_vencimento,
                        data_vencimento=conta.data_vencimento,
                        defaults={
                            'categoria': categoria,
                            'tipo': CategoriaFinanceira.TIPO_DESPESA,
                            'valor': conta.valor,
                            'conta_origem': conta_padrao,
                            'centro_custo': centro_custo,
                            'data_quitacao': None,
                            'status': 'PENDENTE',
                            'forma_pagamento': getattr(conta, 'forma_pagamento', 'PIX') or 'PIX',
                            'documento_referencia': f'CP-{conta.id}',
                            'observacoes': f'Conta a pagar: {conta.descricao}'
                        }
                    )
                    lancamentos_criados += 1
        
        # Criar lançamentos a partir de Movimentações Projetadas (Vendas)
        movimentacoes_vendas = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            data_movimentacao__year=ano,
            tipo_movimentacao='VENDA',
            valor_total__gt=0
        )
        
        categoria_venda = categorias_receita[0] if categorias_receita else None
        # Centro de custo para vendas: principalmente Pecuária
        centro_custo_vendas = next((cc for cc in centros_custo if cc.nome == 'Pecuária'), centros_custo[0] if centros_custo else None)
        hoje = date.today()
        if categoria_venda:
            for mov in movimentacoes_vendas:
                # Vendas no passado: 90% quitadas, vendas futuras: 20% quitadas (adiantadas)
                if mov.data_movimentacao < hoje:
                    status_venda = 'QUITADO' if random.random() < 0.90 else 'PENDENTE'
                    data_quitacao = mov.data_movimentacao + timedelta(days=random.randint(0, 10)) if status_venda == 'QUITADO' else None
                else:
                    status_venda = 'QUITADO' if random.random() < 0.20 else 'PENDENTE'
                    data_quitacao = mov.data_movimentacao - timedelta(days=random.randint(0, 30)) if status_venda == 'QUITADO' else None
                
                # Usar data de quitação como competência se quitada
                data_competencia = data_quitacao if data_quitacao else mov.data_movimentacao
                
                LancamentoFinanceiro.objects.update_or_create(
                    propriedade=propriedade,
                    descricao=f'Venda de {mov.categoria.nome}',
                    data_competencia=data_competencia,
                    data_vencimento=mov.data_movimentacao,
                    defaults={
                        'categoria': categoria_venda,
                        'tipo': CategoriaFinanceira.TIPO_RECEITA,
                        'valor': mov.valor_total or Decimal('0.00'),
                        'conta_destino': conta_padrao,
                        'centro_custo': centro_custo_vendas,
                        'data_quitacao': data_quitacao,
                        'status': status_venda,
                        'forma_pagamento': 'PIX',
                        'documento_referencia': f'VENDA-{mov.id}',
                        'observacoes': mov.observacao or f'Venda de {mov.quantidade} {mov.categoria.nome}'
                    }
                )
                lancamentos_criados += 1
        
        # Garantir receitas no mês atual (para aparecer no dashboard)
        hoje = date.today()
        mes_atual = hoje.month
        ano_atual = hoje.year
        
        if ano == ano_atual and mes_atual <= 12:
            # Criar receitas adicionais para o mês atual para garantir que apareçam no dashboard
            categoria_receita_atual = categorias_receita[0] if categorias_receita else None
            centro_custo_pecuaria = next((cc for cc in centros_custo if cc.nome == 'Pecuária'), centros_custo[0] if centros_custo else None)
            
            if categoria_receita_atual:
                # Calcular receita mensal estimada
                inventario = InventarioRebanho.objects.filter(propriedade=propriedade, data_inventario=date(ano, 1, 1))
                valor_rebanho = sum(inv.quantidade * inv.valor_por_cabeca for inv in inventario)
                receita_mensal_estimada = (valor_rebanho * Decimal('0.15')) / Decimal('12')
                
                # Criar 3-5 receitas quitadas no mês atual
                num_receitas_mes_atual = random.randint(3, 5)
                receita_restante = receita_mensal_estimada
                
                for i in range(num_receitas_mes_atual):
                    if i == num_receitas_mes_atual - 1:
                        valor = receita_restante
                    else:
                        percentual = Decimal(str(random.uniform(0.20, 0.35)))
                        valor = receita_mensal_estimada * percentual
                        receita_restante -= valor
                    
                    valor = max(Decimal('1000.00'), valor.quantize(Decimal('0.01')))
                    data_receita = date(ano_atual, mes_atual, random.randint(1, hoje.day if hoje.month == mes_atual else 28))
                    
                    LancamentoFinanceiro.objects.update_or_create(
                        propriedade=propriedade,
                        descricao=f'Venda de Animais - Mês Atual {i+1}',
                        data_competencia=data_receita,
                        data_vencimento=data_receita,
                        defaults={
                            'categoria': categoria_receita_atual,
                            'tipo': CategoriaFinanceira.TIPO_RECEITA,
                            'valor': valor,
                            'conta_destino': conta_padrao,
                            'centro_custo': centro_custo_pecuaria,
                            'data_quitacao': data_receita,
                            'status': 'QUITADO',
                            'forma_pagamento': 'PIX',
                            'documento_referencia': f'VENDA-MES-ATUAL-{i+1}',
                            'observacoes': f'Venda de animais - mês atual ({mes_atual}/{ano_atual})'
                        }
                    )
                    lancamentos_criados += 1
        
        self.stdout.write(f"    ✅ {len(centros_custo)} centros de custo criados")
        self.stdout.write(f"    ✅ {lancamentos_criados} lançamentos financeiros criados (com centro de custo)")

