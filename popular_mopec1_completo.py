#!/usr/bin/env python
"""
Script completo para popular dados realistas de todos os módulos da Fazenda Demonstração
Banco: mopec_oficial
Período: 24 meses históricos + 6 meses de projeções

Módulos populados:
- Pecuária (animais, pesagens, reprodução, vacinas, tratamentos)
- Financeiro (contas, categorias, lançamentos, movimentos)
- Compras (fornecedores, produtos, ordens de compra, notas fiscais)
- Vendas (lançamentos de receita)
- Projetos Bancários (financiamentos, projetos)
- Operacional (funcionários, pastagens, cochos, equipamentos, empreiteiros)
- Nutrição (distribuições, suplementação, controles)

Dados históricos: Janeiro 2023 até Dezembro 2024 (24 meses)
Projeções: Janeiro 2025 até Junho 2025 (6 meses)
"""
import os
import sys
import django
from datetime import date, timedelta, datetime
from decimal import Decimal
import random
from calendar import monthrange

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import connection

# Importações dos modelos
from gestao_rural.models import (
    ProdutorRural, Propriedade, CategoriaAnimal, AnimalIndividual, AnimalPesagem,
    AnimalVacinaAplicada, AnimalTratamento, AnimalReproducaoEvento, InventarioRebanho,
    CurralLote, CurralSessao
)
from gestao_rural.models_compras_financeiro import (
    Fornecedor, Produto, NotaFiscal, ItemNotaFiscal, OrdemCompra, ItemOrdemCompra,
    SetorPropriedade
)
from gestao_rural.models_financeiro import (
    CategoriaFinanceira, CentroCusto, ContaFinanceira, LancamentoFinanceiro, MovimentoFinanceiro
)
from gestao_rural.models_funcionarios import Funcionario, FolhaPagamento, Holerite
from gestao_rural.models_controles_operacionais import (
    Pastagem, Cocho, ControleCocho, RotacaoPastagem, TipoDistribuicao, DistribuicaoPasto
)
from gestao_rural.models_operacional import (
    TanqueCombustivel, AbastecimentoCombustivel, ConsumoCombustivel,
    EstoqueSuplementacao, CompraSuplementacao, DistribuicaoSuplementacao,
    Equipamento, ManutencaoEquipamento, TipoEquipamento,
    Empreiteiro, ServicoEmpreiteiro
)
from gestao_rural.models import ProjetoBancario, TipoFinanciamento, Financiamento

User = get_user_model()

# Constantes para o período de dados
DATA_INICIO_HISTORICO = date(2023, 1, 1)  # Janeiro 2023
DATA_FIM_HISTORICO = date(2024, 12, 31)    # Dezembro 2024
DATA_FIM_PROJECAO = date(2025, 6, 30)      # Junho 2025

class PopuladorFazendaDemonstracao:
    def __init__(self):
        self.usuario = None
        self.produtor = None
        self.propriedade = None
        self.categorias_animais = {}
        self.fornecedores = []
        self.contas_financeiras = []
        self.categorias_financeiras = {}
        self.centros_custo = {}
        self.setores = []
        self.pastagens = []
        self.cochos = []
        self.equipamentos = []
        self.funcionarios = []

    def main(self):
        print("="*80)
        print("POPULANDO FAZENDA DEMONSTRACAO - SISTEMA COMPLETO DE GESTAO RURAL")
        print("="*80)
        print("Período: 24 meses históricos (Jan/2023 - Dez/2024) + 6 meses projeção")
        print("="*80)

        # 1. Estrutura base
        print("\n[1/9] Criando estrutura base...")
        self.criar_estrutura_base()
        print("OK: Estrutura base criada")

        # 2. Pecuária
        print("\n[2/9] Populando módulo de Pecuária...")
        self.popular_pecuaria()
        print("OK: Modulo Pecuaria populado")

        # 3. Financeiro
        print("\n[3/9] Populando modulo Financeiro...")
        self.popular_financeiro()
        print("OK: Modulo Financeiro populado")

        # 4. Compras
        print("\n[4/9] Populando modulo de Compras...")
        self.popular_compras()
        print("OK: Modulo Compras populado")

        # 5. Vendas
        print("\n[5/9] Populando modulo de Vendas...")
        self.popular_vendas()
        print("OK: Modulo Vendas populado")

        # 6. Projetos Bancários
        print("\n[6/9] Populando Projetos Bancarios...")
        self.popular_projetos_bancarios()
        print("OK: Projetos Bancarios populados")

        # 7. Operacional
        print("\n[7/9] Populando modulo Operacional...")
        self.popular_operacional()
        print("OK: Modulo Operacional populado")

        # 8. Nutrição
        print("\n[8/9] Populando modulo Nutricao...")
        self.popular_nutricao()
        print("OK: Modulo Nutricao populado")

        # 9. Projeções
        print("\n[9/9] Adicionando projecoes para proximos 6 meses...")
        self.adicionar_projecoes()
        print("OK: Projecoes adicionadas")

        # Resumo final
        self.resumo_final()

    def criar_estrutura_base(self):
        """Cria usuário, produtor e propriedade MOPEC1"""
        # Criar usuário
        self.usuario, created = User.objects.get_or_create(
            username='demonstracao',
            defaults={
                'email': 'admin@fazendademonstracao.com.br',
                'first_name': 'Fazenda',
                'last_name': 'Demonstracao',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            self.usuario.set_password('mopec2024')
            self.usuario.save()

        # Criar produtor
        self.produtor, created = ProdutorRural.objects.get_or_create(
            cpf_cnpj='01.234.567/0001-01',
            defaults={
                'nome': 'Fazenda Demonstracao Ltda',
                'email': 'contato@fazendademonstracao.com.br',
                'telefone': '(67) 99999-0001',
                'endereco': 'Rodovia BR-060, Km 45',
                'usuario_responsavel': self.usuario,
                'vai_emitir_nfe': True
            }
        )

        # Criar propriedade Demonstracao
        self.propriedade = Propriedade.objects.create(
            nome_propriedade='Fazenda Demonstracao',
            produtor=self.produtor,
            municipio='Campo Grande',
            uf='MS',
            area_total_ha=1500.00,
            latitude=-20.4697,
            longitude=-54.6201
        )

    def popular_pecuaria(self):
        """Popula módulo de pecuária completo"""
        # Criar categorias de animais
        categorias_data = [
            {'nome': 'Vaca em Lactação', 'sexo': 'F', 'raca': 'NELORE', 'idade_minima_meses': 36, 'peso_medio_kg': Decimal('450.00')},
            {'nome': 'Vaca Seca', 'sexo': 'F', 'raca': 'NELORE', 'idade_minima_meses': 36, 'peso_medio_kg': Decimal('480.00')},
            {'nome': 'Vaca Prenhe', 'sexo': 'F', 'raca': 'NELORE', 'idade_minima_meses': 36, 'peso_medio_kg': Decimal('500.00')},
            {'nome': 'Novilha', 'sexo': 'F', 'raca': 'NELORE', 'idade_minima_meses': 18, 'idade_maxima_meses': 35, 'peso_medio_kg': Decimal('320.00')},
            {'nome': 'Bezerra', 'sexo': 'F', 'raca': 'NELORE', 'idade_maxima_meses': 17, 'peso_medio_kg': Decimal('150.00')},
            {'nome': 'Touro Reprodutor', 'sexo': 'M', 'raca': 'NELORE', 'idade_minima_meses': 24, 'peso_medio_kg': Decimal('650.00')},
            {'nome': 'Bezerro', 'sexo': 'M', 'raca': 'NELORE', 'idade_maxima_meses': 11, 'peso_medio_kg': Decimal('160.00')},
        ]

        for cat_data in categorias_data:
            categoria, created = CategoriaAnimal.objects.get_or_create(
                nome=cat_data['nome'],
                defaults=cat_data
            )
            self.categorias_animais[cat_data['nome']] = categoria

        # Criar animais (rebanho menor para teste)
        animais_criados = []
        animais_por_categoria = {
            'Vaca em Lactação': 10,
            'Vaca Seca': 8,
            'Vaca Prenhe': 12,
            'Novilha': 10,
            'Bezerra': 8,
            'Touro Reprodutor': 3,
            'Bezerro': 6,
        }

        brinco_num = 10000
        for cat_nome, quantidade in animais_por_categoria.items():
            categoria = self.categorias_animais.get(cat_nome)
            if not categoria:
                continue

            for i in range(quantidade):
                # Calcular data de nascimento baseada na categoria
                if 'Vaca' in cat_nome:
                    meses_idade = random.randint(36, 120)
                elif cat_nome == 'Novilha':
                    meses_idade = random.randint(18, 35)
                elif cat_nome == 'Bezerra':
                    meses_idade = random.randint(1, 17)
                elif cat_nome == 'Touro Reprodutor':
                    meses_idade = random.randint(24, 96)
                else:  # Bezerro macho
                    meses_idade = random.randint(1, 11)

                data_nasc = date.today() - timedelta(days=meses_idade * 30)
                peso_base = categoria.peso_medio_kg or Decimal('300')
                peso = peso_base + Decimal(str(random.randint(-50, 50)))

                try:
                    animal = AnimalIndividual.objects.create(
                        propriedade=self.propriedade,
                        numero_brinco=f'DEM{brinco_num:06d}',
                        categoria=categoria,
                        sexo=categoria.sexo,
                        raca=categoria.raca,
                        data_nascimento=data_nasc,
                        peso_atual_kg=peso,
                        status='ATIVO',
                        status_reprodutivo=self.get_status_reprodutivo(cat_nome),
                        tipo_brinco='ELETRONICO',
                        tipo_origem='NASCIMENTO',
                        status_sanitario='APTO',
                        sistema_criacao='PASTO'
                    )
                    animais_criados.append(animal)
                    brinco_num += 1
                except Exception as e:
                    print(f"Erro ao criar animal {cat_nome} {i}: {e}")
                    continue

        # Criar histórico de pesagens (últimos 24 meses)
        print("  - Criando histórico de pesagens...")
        pesagens_count = 0
        for animal in animais_criados:
            # 2-4 pesagens por ano para cada animal
            for ano in [2023, 2024]:
                num_pesagens = random.randint(2, 4)
                for i in range(num_pesagens):
                    mes = random.randint(1, 12)
                    dia = random.randint(1, monthrange(ano, mes)[1])
                    data_pesagem = date(ano, mes, dia)

                    peso_base = animal.peso_atual_kg or Decimal('300')
                    variacao = Decimal(str(random.randint(-30, 30)))
                    # Ajuste de peso baseado na idade do animal na data da pesagem
                    idade_meses = (date.today() - animal.data_nascimento).days // 30
                    idade_na_pesagem = (data_pesagem - animal.data_nascimento).days // 30
                    peso = max(Decimal('30'), peso_base - (idade_meses - idade_na_pesagem) * Decimal('2') + variacao)

                    try:
                        AnimalPesagem.objects.create(
                            animal=animal,
                            data_pesagem=data_pesagem,
                            peso_kg=peso,
                            local='Balanca Principal',
                            responsavel=self.usuario
                        )
                        pesagens_count += 1
                    except:
                        # Ignorar se já existir
                        pass

        # Criar eventos de reprodução
        print("  - Criando eventos de reprodução...")
        reprod_count = 0
        vacas_femeas = [a for a in animais_criados if a.sexo == 'F' and 'Vaca' in a.categoria.nome]
        touros = [a for a in animais_criados if a.categoria.nome == 'Touro Reprodutor']

        for vaca in vacas_femeas[:300]:  # 300 vacas com histórico reprodutivo
            for ano in [2023, 2024]:
                if random.random() > 0.7:  # 30% chance de ter evento por ano
                    mes = random.randint(1, 12)
                    dia = random.randint(1, monthrange(ano, mes)[1])
                    data_evento = date(ano, mes, dia)
                    touro = random.choice(touros) if touros else None

                    evento, created = AnimalReproducaoEvento.objects.get_or_create(
                        animal=vaca,
                        tipo_evento=random.choice(['COBERTURA', 'INSEMINACAO']),
                        data_evento=data_evento,
                        defaults={
                            'resultado': 'Realizada',
                            'touro_reprodutor': touro.numero_brinco if touro else 'Sêmen comercial',
                            'responsavel': self.usuario
                        }
                    )
                    if created:
                        reprod_count += 1

                    # Possível diagnóstico
                    if random.random() > 0.6:
                        data_diag = data_evento + timedelta(days=random.randint(30, 45))
                        if data_diag <= date.today():
                            diag, created = AnimalReproducaoEvento.objects.get_or_create(
                                animal=vaca,
                                tipo_evento='DIAGNOSTICO',
                                data_evento=data_diag,
                                defaults={
                                    'resultado': 'Prenhez confirmada' if random.random() > 0.3 else 'Vazia',
                                    'responsavel': self.usuario
                                }
                            )
                            if created:
                                reprod_count += 1

                    # Possível parto
                    if random.random() > 0.4:
                        data_parto = data_evento + timedelta(days=random.randint(280, 290))
                        if data_parto <= date.today():
                            parto, created = AnimalReproducaoEvento.objects.get_or_create(
                                animal=vaca,
                                tipo_evento='PARTO',
                                data_evento=data_parto,
                                defaults={
                                    'resultado': random.choice(['Bezerro macho', 'Bezerra fêmea']),
                                    'responsavel': self.usuario
                                }
                            )
                            if created:
                                reprod_count += 1

        # Criar vacinas e tratamentos
        print("  - Criando vacinas e tratamentos...")
        vacinas_count = 0
        tratamentos_count = 0

        vacinas_comuns = ['Febre Aftosa', 'Brucelose', 'Raiva', 'Clostridioses', 'IBR/BVD', 'Leptospirose']

        for animal in animais_criados[:500]:  # Vacinar metade do rebanho
            num_vacinas = random.randint(3, 6)
            for _ in range(num_vacinas):
                ano = random.choice([2023, 2024])
                mes = random.randint(1, 12)
                dia = random.randint(1, monthrange(ano, mes)[1])
                data_vacina = date(ano, mes, dia)

                vacina, created = AnimalVacinaAplicada.objects.get_or_create(
                    animal=animal,
                    vacina=random.choice(vacinas_comuns),
                    data_aplicacao=data_vacina,
                    defaults={
                        'dose': '1 dose',
                        'lote_produto': f'LOTE-{random.randint(100000, 999999)}',
                        'proxima_dose': data_vacina + timedelta(days=random.randint(180, 365)),
                        'carencia_ate': data_vacina + timedelta(days=random.randint(21, 30)),
                        'responsavel': self.usuario
                    }
                )
                if created:
                    vacinas_count += 1

            # Tratamentos (10% dos animais)
            if random.random() < 0.1:
                ano = random.choice([2023, 2024])
                mes = random.randint(1, 12)
                dia = random.randint(1, monthrange(ano, mes)[1])
                data_trat = date(ano, mes, dia)

                tratamento, created = AnimalTratamento.objects.get_or_create(
                    animal=animal,
                    produto=random.choice(['Ivermectina', 'Albendazol', 'Oxitetraciclina', 'Penicilina']),
                    data_inicio=data_trat,
                    defaults={
                        'dosagem': random.choice(['5ml', '10ml', '1 dose']),
                        'data_fim': data_trat + timedelta(days=random.randint(3, 7)),
                        'carencia_ate': data_trat + timedelta(days=random.randint(15, 30)),
                        'motivo': random.choice(['Verminose', 'Infecção', 'Preventivo']),
                        'responsavel': self.usuario
                    }
                )
                if created:
                    tratamentos_count += 1

        print(f"  OK: Criados {len(animais_criados)} animais, {pesagens_count} pesagens, {reprod_count} eventos reprodutivos, {vacinas_count} vacinas, {tratamentos_count} tratamentos")

    def get_status_reprodutivo(self, categoria_nome):
        """Retorna status reprodutivo baseado na categoria"""
        if categoria_nome == 'Vaca em Lactação':
            return 'LACTACAO'
        elif categoria_nome == 'Vaca Seca':
            return 'SECAGEM'
        elif categoria_nome == 'Vaca Prenhe':
            return 'PRENHE'
        elif categoria_nome == 'Novilha':
            return 'VAZIA'
        else:
            return 'INDEFINIDO'

    def popular_financeiro(self):
        """Popula módulo financeiro"""
        # Criar contas financeiras
        contas_data = [
            {'nome': 'Caixa Demonstracao', 'tipo': 'CAIXA', 'instituicao': 'Caixa', 'saldo_inicial': Decimal('15000.00')},
            {'nome': 'BB Conta Corrente', 'tipo': 'CORRENTE', 'instituicao': 'Banco do Brasil', 'banco': 'Banco do Brasil', 'agencia': '1234-5', 'numero_conta': '12345-6', 'saldo_inicial': Decimal('250000.00')},
            {'nome': 'BB Poupança', 'tipo': 'POUPANCA', 'instituicao': 'Banco do Brasil', 'banco': 'Banco do Brasil', 'agencia': '1234-5', 'numero_conta': '98765-4', 'saldo_inicial': Decimal('500000.00')},
            {'nome': 'CEF Conta Corrente', 'tipo': 'CORRENTE', 'instituicao': 'Caixa Econômica Federal', 'banco': 'Caixa Econômica Federal', 'agencia': '4321-0', 'numero_conta': '65432-1', 'saldo_inicial': Decimal('100000.00')},
        ]

        with connection.cursor() as cursor:
            for conta_data in contas_data:
                cursor.execute(
                    "SELECT id FROM gestao_rural_contafinanceira WHERE propriedade_id = %s AND nome = %s",
                    [self.propriedade.id, conta_data['nome']]
                )
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO gestao_rural_contafinanceira
                        (propriedade_id, nome, tipo, banco, agencia, numero_conta, numero_agencia, moeda, saldo_inicial, data_saldo_inicial,
                         permite_negativo, ativa, instituicao, observacoes, criado_em, atualizado_em)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        RETURNING id
                    """, [
                        self.propriedade.id,
                        conta_data['nome'],
                        conta_data['tipo'],
                        conta_data.get('banco', ''),
                        conta_data.get('agencia', ''),
                        conta_data.get('numero_conta', ''),
                        conta_data.get('agencia', ''),
                        'BRL',
                        conta_data['saldo_inicial'],
                        DATA_INICIO_HISTORICO,
                        False,
                        True,
                        conta_data['instituicao'],
                        ''
                    ])
                    conta_id = cursor.fetchone()[0]
                    conta = ContaFinanceira.objects.get(id=conta_id)
                    self.contas_financeiras.append(conta)

                    # Movimento de saldo inicial
                    try:
                        MovimentoFinanceiro.objects.create(
                            conta=conta,
                            tipo='ENTRADA',
                            origem='SALDO_INICIAL',
                            data_movimento=DATA_INICIO_HISTORICO,
                            descricao=f'Saldo inicial - {conta.nome}',
                            valor_bruto=conta_data['saldo_inicial'],
                            valor_liquido=conta_data['saldo_inicial']
                        )
                    except:
                        pass  # Ignorar erro se propriedade_id for obrigatório

        # Criar categorias financeiras
        categorias_data = [
            # Receitas
            {'nome': 'Venda de Animais', 'tipo': 'RECEITA'},
            {'nome': 'Venda de Produtos', 'tipo': 'RECEITA'},
            {'nome': 'Arrendamento', 'tipo': 'RECEITA'},
            {'nome': 'Outras Receitas', 'tipo': 'RECEITA'},
            # Despesas
            {'nome': 'Compra de Insumos', 'tipo': 'DESPESA'},
            {'nome': 'Compra de Animais', 'tipo': 'DESPESA'},
            {'nome': 'Medicamentos e Vacinas', 'tipo': 'DESPESA'},
            {'nome': 'Combustível', 'tipo': 'DESPESA'},
            {'nome': 'Manutenção', 'tipo': 'DESPESA'},
            {'nome': 'Salários', 'tipo': 'DESPESA'},
            {'nome': 'Impostos', 'tipo': 'DESPESA'},
            {'nome': 'Serviços Terceirizados', 'tipo': 'DESPESA'},
            {'nome': 'Outras Despesas', 'tipo': 'DESPESA'},
        ]

        with connection.cursor() as cursor:
            for cat_data in categorias_data:
                cursor.execute(
                    "SELECT id FROM gestao_rural_categoriafinanceira WHERE nome = %s AND tipo = %s",
                    [cat_data['nome'], cat_data['tipo']]
                )
                row = cursor.fetchone()
                if row:
                    categoria_id = row[0]
                else:
                    cursor.execute("""
                        INSERT INTO gestao_rural_categoriafinanceira
                        (nome, tipo, descricao, criado_em, atualizado_em)
                        VALUES (%s, %s, %s, NOW(), NOW())
                        RETURNING id
                    """, [cat_data['nome'], cat_data['tipo'], ''])
                    categoria_id = cursor.fetchone()[0]

                categoria = CategoriaFinanceira.objects.raw('SELECT * FROM gestao_rural_categoriafinanceira WHERE id = %s', [categoria_id])[0]
                self.categorias_financeiras[cat_data['nome']] = categoria

        # Criar centros de custo
        centros_data = [
            {'nome': 'Pecuária', 'tipo': 'OPERACIONAL'},
            {'nome': 'Administração', 'tipo': 'ADMINISTRATIVO'},
            {'nome': 'Investimentos', 'tipo': 'INVESTIMENTO'},
        ]

        for centro_data in centros_data:
            centro, created = CentroCusto.objects.get_or_create(
                propriedade=self.propriedade,
                nome=centro_data['nome'],
                defaults={
                    'tipo': centro_data['tipo'],
                    'ativo': True
                }
            )
            self.centros_custo[centro_data['nome']] = centro

    def popular_compras(self):
        """Popula módulo de compras"""
        # Criar fornecedores
        fornecedores_data = [
            {
                'nome': 'Nutripec Ração e Suplementos Ltda',
                'nome_fantasia': 'Nutripec',
                'cpf_cnpj': '10.234.567/0001-11',
                'tipo': 'RACAO',
                'telefone': '(67) 3321-1234',
                'email': 'vendas@nutripec.com.br',
                'cidade': 'Campo Grande',
                'estado': 'MS'
            },
            {
                'nome': 'Vet Agro Medicamentos Veterinários',
                'nome_fantasia': 'Vet Agro',
                'cpf_cnpj': '11.345.678/0001-22',
                'tipo': 'MEDICAMENTO',
                'telefone': '(67) 3322-2345',
                'email': 'contato@vetagro.com.br',
                'cidade': 'Campo Grande',
                'estado': 'MS'
            },
            {
                'nome': 'Agro Máquinas e Equipamentos S/A',
                'nome_fantasia': 'Agro Máquinas',
                'cpf_cnpj': '12.456.789/0001-33',
                'tipo': 'EQUIPAMENTO',
                'telefone': '(67) 3323-3456',
                'email': 'vendas@agromaquinas.com.br',
                'cidade': 'Dourados',
                'estado': 'MS'
            },
            {
                'nome': 'Posto Combustíveis Rural',
                'nome_fantasia': 'Posto Rural',
                'cpf_cnpj': '13.567.890/0001-44',
                'tipo': 'COMBUSTIVEL',
                'telefone': '(67) 3324-4567',
                'email': 'posto@rural.com.br',
                'cidade': 'Campo Grande',
                'estado': 'MS'
            },
        ]

        for fornecedor_data in fornecedores_data:
            fornecedor, created = Fornecedor.objects.get_or_create(
                cpf_cnpj=fornecedor_data['cpf_cnpj'],
                defaults={
                    **fornecedor_data,
                    'propriedade': self.propriedade,
                    'endereco': f'Rua {random.randint(1, 999)}, Centro',
                    'cep': f'79000-{random.randint(100, 999)}',
                    'ativo': True
                }
            )
            self.fornecedores.append(fornecedor)

        # Criar compras históricas (24 meses)
        print("  - Criando histórico de compras...")
        compras_count = 0
        notas_count = 0

        for ano in [2023, 2024]:
            for mes in range(1, 13):
                # 3-5 compras por mês
                num_compras = random.randint(3, 5)
                for _ in range(num_compras):
                    dia = random.randint(1, monthrange(ano, mes)[1])
                    data_compra = date(ano, mes, dia)
                    fornecedor = random.choice(self.fornecedores)

                    # Valor baseado no tipo de fornecedor
                    if fornecedor.tipo == 'RACAO':
                        valor_base = random.randint(5000, 15000)
                    elif fornecedor.tipo == 'MEDICAMENTO':
                        valor_base = random.randint(2000, 8000)
                    elif fornecedor.tipo == 'EQUIPAMENTO':
                        valor_base = random.randint(10000, 50000)
                    else:  # COMBUSTIVEL
                        valor_base = random.randint(3000, 10000)

                    valor_total = Decimal(str(valor_base))

                    # Criar ordem de compra
                    numero_ordem = f'OC-{ano}{mes:02d}-{random.randint(100, 999)}'
                    ordem, created = OrdemCompra.objects.get_or_create(
                        numero_ordem=numero_ordem,
                        defaults={
                            'propriedade': self.propriedade,
                            'fornecedor': fornecedor,
                            'data_emissao': data_compra,
                            'data_entrega_prevista': data_compra + timedelta(days=15),
                            'status': 'RECEBIDA',
                            'forma_pagamento': random.choice(['BOLETO', 'TRANSFERENCIA', 'PIX']),
                            'condicoes_pagamento': f'{random.randint(15, 60)} dias',
                            'criado_por': self.usuario,
                            'valor_produtos': valor_total * Decimal('0.95'),
                            'valor_frete': valor_total * Decimal('0.05'),
                            'valor_total': valor_total
                        }
                    )

                    if created:
                        compras_count += 1

                        # Criar nota fiscal
                        numero_nf = f'{random.randint(100000, 999999)}'
                        nota, created = NotaFiscal.objects.get_or_create(
                            propriedade=self.propriedade,
                            numero=numero_nf,
                            serie='1',
                            tipo='ENTRADA',
                            defaults={
                                'fornecedor': fornecedor,
                                'data_emissao': data_compra + timedelta(days=random.randint(1, 5)),
                                'data_entrada': data_compra + timedelta(days=random.randint(10, 20)),
                                'valor_produtos': valor_total * Decimal('0.95'),
                                'valor_frete': valor_total * Decimal('0.05'),
                                'valor_total': valor_total,
                                'status': 'AUTORIZADA'
                            }
                        )

                        if created:
                            notas_count += 1

                            # Criar item da nota fiscal (simplificado)
                            ItemNotaFiscal.objects.create(
                                nota_fiscal=nota,
                                produto=None,  # Sem produto específico para simplificar
                                descricao=f'Compra de {fornecedor.tipo.lower()}',
                                quantidade=Decimal('1'),
                                valor_unitario=valor_total,
                                valor_total=valor_total,
                                ncm='00000000',
                                origem_mercadoria='0',
                                unidade_medida='UN'
                            )

        print(f"  OK: Criadas {compras_count} ordens de compra, {notas_count} notas fiscais")

    def popular_vendas(self):
        """Popula módulo de vendas (lançamentos de receita)"""
        print("  - Criando histórico de vendas...")
        vendas_count = 0

        with connection.cursor() as cursor:
            categoria_receita = self.categorias_financeiras.get('Venda de Animais')

            for ano in [2023, 2024]:
                for mes in range(1, 13):
                    # 4-8 vendas por mês
                    num_vendas = random.randint(4, 8)
                    for _ in range(num_vendas):
                        dia = random.randint(1, monthrange(ano, mes)[1])
                        data_venda = date(ano, mes, dia)

                        # Valor da venda (animais)
                        valor_venda = Decimal(str(random.randint(8000, 40000)))
                        data_pagamento = data_venda + timedelta(days=random.randint(0, 7))
                        forma_pagamento = random.choice(['TRANSFERENCIA', 'PIX', 'DINHEIRO'])

                        cursor.execute("""
                            INSERT INTO gestao_rural_lancamentofinanceiro
                            (propriedade_id, categoria_id, data, descricao, valor, forma_pagamento,
                             pago, data_pagamento, observacoes, criado_em, atualizado_em)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                        """, [
                            self.propriedade.id,
                            categoria_receita.id if categoria_receita else None,
                            data_venda,
                            f'Venda de {random.randint(3, 15)} animais - {random.choice(["Nelore", "Angus", "Brangus"])}',
                            valor_venda,
                            forma_pagamento,
                            True,
                            data_pagamento,
                            ''
                        ])
                        vendas_count += 1

        print(f"  OK: Criadas {vendas_count} vendas")

    def popular_projetos_bancarios(self):
        """Popula projetos bancários e financiamentos"""
        # Criar tipos de financiamento
        tipos_fin = [
            {'nome': 'Pronaf - Custeio', 'descricao': 'Programa Nacional de Fortalecimento da Agricultura Familiar - Custeio'},
            {'nome': 'Pronaf - Investimento', 'descricao': 'Programa Nacional de Fortalecimento da Agricultura Familiar - Investimento'},
            {'nome': 'FCO - Custeio', 'descricao': 'Fundo Constitucional de Financiamento do Centro-Oeste - Custeio'},
            {'nome': 'FCO - Investimento', 'descricao': 'Fundo Constitucional de Financiamento do Centro-Oeste - Investimento'},
        ]

        tipos_fin_objs = []
        for tipo_data in tipos_fin:
            tipo, created = TipoFinanciamento.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults={'descricao': tipo_data['descricao']}
            )
            tipos_fin_objs.append(tipo)

        # Criar financiamentos
        financiamentos_data = [
            {
                'tipo': tipos_fin_objs[0],  # Pronaf Custeio
                'nome': 'Financiamento Pronaf Custeio 2023',
                'valor': Decimal('200000.00'),
                'taxa': Decimal('4.5'),
                'parcelas': 60,
                'data_inicio': date(2023, 3, 1)
            },
            {
                'tipo': tipos_fin_objs[1],  # Pronaf Investimento
                'nome': 'Financiamento Pronaf Investimento 2024',
                'valor': Decimal('500000.00'),
                'taxa': Decimal('5.0'),
                'parcelas': 84,
                'data_inicio': date(2024, 6, 1)
            },
            {
                'tipo': tipos_fin_objs[2],  # FCO Custeio
                'nome': 'Financiamento FCO Custeio 2024',
                'valor': Decimal('300000.00'),
                'taxa': Decimal('6.0'),
                'parcelas': 36,
                'data_inicio': date(2024, 9, 1)
            },
        ]

        for fin_data in financiamentos_data:
            financiamento, created = Financiamento.objects.get_or_create(
                propriedade=self.propriedade,
                nome=fin_data['nome'],
                defaults={
                    'tipo': fin_data['tipo'],
                    'valor_principal': fin_data['valor'],
                    'taxa_juros_anual': fin_data['taxa'],
                    'tipo_taxa': 'FIXA',
                    'data_contratacao': fin_data['data_inicio'],
                    'data_primeiro_vencimento': fin_data['data_inicio'] + timedelta(days=30),
                    'data_ultimo_vencimento': fin_data['data_inicio'] + timedelta(days=30 * fin_data['parcelas']),
                    'numero_parcelas': fin_data['parcelas'],
                    'valor_parcela': (fin_data['valor'] * (1 + fin_data['taxa']/100)) / fin_data['parcelas'],
                    'ativo': True,
                    'descricao': f'Financiamento {fin_data["tipo"].nome}'
                }
            )

        # Criar projetos bancários
        projetos_data = [
            {
                'nome': 'Projeto Expansão Rebanho 2024',
                'tipo': 'INVESTIMENTO',
                'banco': 'Banco do Brasil',
                'valor': Decimal('800000.00'),
                'prazo': 96,
                'taxa': Decimal('7.5'),
                'status': 'APROVADO',
                'data_aprovacao': date(2024, 2, 15),
                'valor_aprovado': Decimal('800000.00')
            },
            {
                'nome': 'Projeto Modernização Pastagens 2023',
                'tipo': 'INVESTIMENTO',
                'banco': 'Caixa Econômica Federal',
                'valor': Decimal('400000.00'),
                'prazo': 72,
                'taxa': Decimal('6.5'),
                'status': 'CONTRATADO',
                'data_aprovacao': date(2023, 8, 10),
                'valor_aprovado': Decimal('400000.00')
            },
        ]

        for proj_data in projetos_data:
            data_solicitacao = proj_data['data_aprovacao'] - timedelta(days=random.randint(60, 120))

            projeto, created = ProjetoBancario.objects.get_or_create(
                propriedade=self.propriedade,
                nome_projeto=proj_data['nome'],
                defaults={
                    'tipo_projeto': proj_data['tipo'],
                    'banco_solicitado': proj_data['banco'],
                    'valor_solicitado': proj_data['valor'],
                    'prazo_pagamento': proj_data['prazo'],
                    'taxa_juros': proj_data['taxa'],
                    'data_solicitacao': data_solicitacao,
                    'data_aprovacao': proj_data['data_aprovacao'],
                    'valor_aprovado': proj_data['valor_aprovado'],
                    'status': proj_data['status'],
                    'observacoes': f'Projeto de {proj_data["tipo"].lower()} - {proj_data["nome"]}'
                }
            )

    def popular_operacional(self):
        """Popula módulo operacional"""
        # Criar setores
        setores_data = ['Administração', 'Pecuária', 'Manutenção', 'Pastagens']
        for nome_setor in setores_data:
            setor, created = SetorPropriedade.objects.get_or_create(
                propriedade=self.propriedade,
                nome=nome_setor
            )
            self.setores.append(setor)

        # Criar funcionários
        funcionarios_data = [
            {'nome': 'João Silva', 'cpf': '123.456.789-00', 'cargo': 'Gerente de Fazenda', 'salario': Decimal('8500.00'), 'setor': 'Administração'},
            {'nome': 'Maria Santos', 'cpf': '234.567.890-11', 'cargo': 'Veterinária', 'salario': Decimal('6800.00'), 'setor': 'Pecuária'},
            {'nome': 'Pedro Oliveira', 'cpf': '345.678.901-22', 'cargo': 'Capataz', 'salario': Decimal('4800.00'), 'setor': 'Pecuária'},
            {'nome': 'Carlos Souza', 'cpf': '456.789.012-33', 'cargo': 'Vaqueiro', 'salario': Decimal('2700.00'), 'setor': 'Pecuária'},
            {'nome': 'Antonio Costa', 'cpf': '567.890.123-44', 'cargo': 'Vaqueiro', 'salario': Decimal('2700.00'), 'setor': 'Pecuária'},
            {'nome': 'Roberto Alves', 'cpf': '678.901.234-55', 'cargo': 'Mecânico', 'salario': Decimal('3800.00'), 'setor': 'Manutenção'},
            {'nome': 'Ana Paula', 'cpf': '789.012.345-66', 'cargo': 'Administrativo', 'salario': Decimal('3200.00'), 'setor': 'Administração'},
        ]

        for func_data in funcionarios_data:
            setor = next((s for s in self.setores if s.nome == func_data['setor']), None)
            funcionario, created = Funcionario.objects.get_or_create(
                cpf=func_data['cpf'],
                defaults={
                    'propriedade': self.propriedade,
                    'nome': func_data['nome'],
                    'cargo': func_data['cargo'],
                    'salario_base': func_data['salario'],
                    'tipo_contrato': 'CLT',
                    'data_admissao': date.today() - timedelta(days=random.randint(365, 1825)),
                    'situacao': 'ATIVO',
                    'sexo': random.choice(['M', 'F']),
                    'telefone': f'(67) 9{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                    'cidade': 'Campo Grande',
                    'estado': 'MS',
                    'jornada_trabalho': 44,
                    'setor': setor
                }
            )
            self.funcionarios.append(funcionario)

        # Criar pastagens
        pastagens_data = [
            {'nome': 'Pastagem Norte', 'tipo': 'BRACHIARIA', 'area': Decimal('200.00')},
            {'nome': 'Pastagem Sul', 'tipo': 'PANICUM', 'area': Decimal('180.00')},
            {'nome': 'Pastagem Leste', 'tipo': 'CYNODON', 'area': Decimal('150.00')},
            {'nome': 'Pastagem Oeste', 'tipo': 'UROCHLOA', 'area': Decimal('170.00')},
            {'nome': 'Pastagem Central', 'tipo': 'BRACHIARIA', 'area': Decimal('160.00')},
        ]

        for past_data in pastagens_data:
            pastagem, created = Pastagem.objects.get_or_create(
                propriedade=self.propriedade,
                nome=past_data['nome'],
                defaults={
                    'tipo_pastagem': past_data['tipo'],
                    'area_ha': past_data['area'],
                    'capacidade_suporte': past_data['area'] * Decimal('2.5'),
                    'status': random.choice(['EM_USO', 'EM_USO', 'EM_USO', 'DESCANSO']),
                    'data_plantio': date.today() - timedelta(days=random.randint(365, 1825))
                }
            )
            self.pastagens.append(pastagem)

        # Criar cochos
        for pastagem in self.pastagens:
            num_cochos = random.randint(2, 4)
            for i in range(num_cochos):
                tipo = random.choice(['SAL', 'RACAO', 'AGUA'])
                capacidade = Decimal(str(random.randint(200, 800))) if tipo != 'AGUA' else Decimal(str(random.randint(2000, 8000)))

                cocho, created = Cocho.objects.get_or_create(
                    propriedade=self.propriedade,
                    pastagem=pastagem,
                    nome=f'{pastagem.nome} - Cocho {i+1} ({tipo})',
                    defaults={
                        'tipo_cocho': tipo,
                        'capacidade': capacidade,
                        'unidade_capacidade': 'KG' if tipo != 'AGUA' else 'L',
                        'status': 'ATIVO'
                    }
                )
                if created:
                    self.cochos.append(cocho)

        # Criar equipamentos
        tipos_equip = {}
        tipos_nomes = ['Trator', 'Pulverizador', 'Caminhão', 'Máquina de Feno']
        for tipo_nome in tipos_nomes:
            tipo, created = TipoEquipamento.objects.get_or_create(nome=tipo_nome)
            tipos_equip[tipo_nome] = tipo

        equipamentos_data = [
            {'nome': 'Trator Valtra BM125', 'tipo': 'Trator', 'marca': 'Valtra', 'ano': 2020},
            {'nome': 'Pulverizador Jacto Phoenix 4000', 'tipo': 'Pulverizador', 'marca': 'Jacto', 'ano': 2019},
            {'nome': 'Caminhão Mercedes-Benz Atron 1724', 'tipo': 'Caminhão', 'marca': 'Mercedes-Benz', 'ano': 2018},
            {'nome': 'Enfardadeira New Holland 269', 'tipo': 'Máquina de Feno', 'marca': 'New Holland', 'ano': 2021},
        ]

        for equip_data in equipamentos_data:
            tipo_equip = tipos_equip.get(equip_data['tipo'])
            if tipo_equip:
                equipamento, created = Equipamento.objects.get_or_create(
                    propriedade=self.propriedade,
                    nome=equip_data['nome'],
                    defaults={
                        'tipo': tipo_equip,
                        'marca': equip_data['marca'],
                        'ano': equip_data['ano'],
                        'ativo': True,
                        'valor_aquisicao': Decimal(str(random.randint(100000, 800000))),
                        'data_aquisicao': date.today() - timedelta(days=random.randint(365, 1825))
                    }
                )
                if created:
                    self.equipamentos.append(equipamento)

    def popular_nutricao(self):
        """Popula módulo de nutrição"""
        # Criar tipos de distribuição
        tipos_dist_data = [
            {'nome': 'Sal Mineralizado', 'unidade': 'SC', 'descricao': 'Sal mineral para suplementação'},
            {'nome': 'Ração Concentrada', 'unidade': 'KG', 'descricao': 'Ração concentrada para engorda'},
            {'nome': 'Suplemento Proteinado', 'unidade': 'SC', 'descricao': 'Suplemento proteico'},
            {'nome': 'Ureia', 'unidade': 'KG', 'descricao': 'Ureia para suplementação'},
        ]

        tipos_dist = []
        for tipo_data in tipos_dist_data:
            tipo, created = TipoDistribuicao.objects.get_or_create(
                nome=tipo_data['nome'],
                defaults={
                    'unidade_medida': tipo_data['unidade'],
                    'descricao': tipo_data['descricao'],
                    'ativo': True
                }
            )
            tipos_dist.append(tipo)

        # Criar estoques de suplementação
        estoques_data = [
            {'tipo': 'Sal Mineralizado', 'unidade': 'SC', 'quantidade': Decimal('80.00')},
            {'tipo': 'Ração Concentrada', 'unidade': 'TON', 'quantidade': Decimal('15.00')},
            {'tipo': 'Suplemento Proteinado', 'unidade': 'SC', 'quantidade': Decimal('45.00')},
        ]

        estoques = []
        for estoque_data in estoques_data:
            estoque, created = EstoqueSuplementacao.objects.get_or_create(
                propriedade=self.propriedade,
                tipo_suplemento=estoque_data['tipo'],
                defaults={
                    'unidade_medida': estoque_data['unidade'],
                    'quantidade_atual': estoque_data['quantidade'],
                    'quantidade_minima': estoque_data['quantidade'] * Decimal('0.3')
                }
            )
            estoques.append(estoque)

        # Criar distribuições históricas (últimos 12 meses)
        distribuicoes_count = 0
        for mes in range(12, 0, -1):
            data_base = date.today() - timedelta(days=30 * mes)
            num_dist = random.randint(8, 15)

            for _ in range(num_dist):
                dia = random.randint(1, monthrange(data_base.year, data_base.month)[1])
                data_dist = date(data_base.year, data_base.month, dia)
                tipo_dist = random.choice(tipos_dist)
                pastagem = random.choice(self.pastagens)

                if tipo_dist.unidade_medida == 'SC':
                    quantidade = Decimal(str(random.randint(10, 40)))
                else:
                    quantidade = Decimal(str(random.randint(200, 800)))

                numero_animais = random.randint(80, 250)

                distribuicao, created = DistribuicaoPasto.objects.get_or_create(
                    propriedade=self.propriedade,
                    pastagem=pastagem,
                    tipo_distribuicao=tipo_dist,
                    data_distribuicao=data_dist,
                    defaults={
                        'quantidade': quantidade,
                        'numero_animais': numero_animais,
                        'valor_unitario': Decimal(str(random.randint(50, 120))),
                        'responsavel': self.usuario,
                        'observacoes': f'Distribuição em {pastagem.nome}'
                    }
                )
                if created:
                    # Calcular valor total
                    distribuicao.valor_total = distribuicao.quantidade * distribuicao.valor_unitario
                    distribuicao.save()
                    distribuicoes_count += 1

        # Criar controles de cochos (últimos 6 meses)
        controles_count = 0
        for mes in range(6, 0, -1):
            data_base = date.today() - timedelta(days=30 * mes)
            num_controles = random.randint(20, 40)

            for _ in range(num_controles):
                dia = random.randint(1, monthrange(data_base.year, data_base.month)[1])
                data_controle = date(data_base.year, data_base.month, dia)
                cocho = random.choice(self.cochos)

                quantidade_abastecida = Decimal(str(random.randint(100, 600)))
                quantidade_restante = Decimal(str(random.randint(0, int(quantidade_abastecida * 0.3))))
                quantidade_consumida = quantidade_abastecida - quantidade_restante
                numero_animais = random.randint(30, 180)

                controle, created = ControleCocho.objects.get_or_create(
                    cocho=cocho,
                    data=data_controle,
                    defaults={
                        'quantidade_abastecida': quantidade_abastecida,
                        'quantidade_restante': quantidade_restante,
                        'quantidade_consumida': quantidade_consumida,
                        'numero_animais': numero_animais,
                        'consumo_por_animal': quantidade_consumida / Decimal(str(numero_animais)) if numero_animais > 0 else Decimal('0'),
                        'valor_unitario': Decimal(str(random.randint(3, 12))),
                        'observacoes': f'Controle diário - {cocho.nome}',
                        'responsavel': self.usuario
                    }
                )
                if created:
                    # Calcular valor total
                    controle.valor_total_consumido = controle.quantidade_consumida * controle.valor_unitario
                    controle.save()
                    controles_count += 1

        print(f"  OK: Criados {distribuicoes_count} distribuicoes no pasto, {controles_count} controles de cochos")

    def adicionar_projecoes(self):
        """Adiciona projeções para os próximos 6 meses"""
        # Projeções de vendas (mais otimistas)
        vendas_proj = 0
        with connection.cursor() as cursor:
            categoria_receita = self.categorias_financeiras.get('Venda de Animais')

            for mes in range(1, 7):
                data_proj = date(2025, mes, 15)  # Meados de cada mês
                num_vendas = random.randint(6, 10)  # Mais vendas projetadas

                for _ in range(num_vendas):
                    valor_venda = Decimal(str(random.randint(10000, 50000)))  # Valores maiores
                    data_pagamento = data_proj + timedelta(days=random.randint(0, 7))

                    cursor.execute("""
                        INSERT INTO gestao_rural_lancamentofinanceiro
                        (propriedade_id, categoria_id, data, descricao, valor, forma_pagamento,
                         pago, data_pagamento, observacoes, criado_em, atualizado_em)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """, [
                        self.propriedade.id,
                        categoria_receita.id if categoria_receita else None,
                        data_proj,
                        f'[PROJEÇÃO] Venda de {random.randint(5, 20)} animais',
                        valor_venda,
                        'TRANSFERENCIA',
                        False,  # Não pago ainda (projeção)
                        data_pagamento,
                        'Projeção para 2025'
                    ])
                    vendas_proj += 1

        print(f"  OK: Adicionadas {vendas_proj} projecoes de vendas")

    def resumo_final(self):
        """Exibe resumo final dos dados populados"""
        print("="*80)
        print("RESUMO FINAL - FAZENDA DEMONSTRACAO POPULADA")
        print("="*80)
        print(f"Propriedade: {self.propriedade.nome_propriedade}")
        print(f"Periodo: {DATA_INICIO_HISTORICO.strftime('%m/%Y')} ate {DATA_FIM_PROJECAO.strftime('%m/%Y')}")
        print()

        # Pecuária
        print("PECUARIA:")
        print(f"  - Animais: {AnimalIndividual.objects.filter(propriedade=self.propriedade).count()}")
        print(f"  - Pesagens: {AnimalPesagem.objects.filter(animal__propriedade=self.propriedade).count()}")
        print(f"  - Eventos Reprodutivos: {AnimalReproducaoEvento.objects.filter(animal__propriedade=self.propriedade).count()}")
        print(f"  - Vacinas Aplicadas: {AnimalVacinaAplicada.objects.filter(animal__propriedade=self.propriedade).count()}")
        print(f"  - Tratamentos: {AnimalTratamento.objects.filter(animal__propriedade=self.propriedade).count()}")
        print()

        # Financeiro
        print("FINANCEIRO:")
        print(f"  - Contas Financeiras: {ContaFinanceira.objects.filter(propriedade=self.propriedade).count()}")
        print(f"  - Categorias Financeiras: {CategoriaFinanceira.objects.count()}")
        print(f"  - Centros de Custo: {CentroCusto.objects.filter(propriedade=self.propriedade).count()}")

        # Contar lançamentos
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM gestao_rural_lancamentofinanceiro WHERE propriedade_id = %s", [self.propriedade.id])
        lancamentos_count = cursor.fetchone()[0]
        print(f"  - Lancamentos Financeiros: {lancamentos_count}")
        print()

        # Compras e Vendas
        print("COMPRAS E VENDAS:")
        print(f"  - Fornecedores: {Fornecedor.objects.filter(propriedade=self.propriedade).count()}")
        print(f"  - Ordens de Compra: {OrdemCompra.objects.filter(propriedade=self.propriedade).count()}")
        print(f"  - Notas Fiscais: {NotaFiscal.objects.filter(propriedade=self.propriedade).count()}")
        print()

        # Projetos Bancários
        print("PROJETOS BANCARIOS:")
        print(f"  - Tipos de Financiamento: {TipoFinanciamento.objects.count()}")
        print(f"  - Financiamentos: {Financiamento.objects.filter(propriedade=self.propriedade).count()}")
        print(f"  - Projetos Bancarios: {ProjetoBancario.objects.filter(propriedade=self.propriedade).count()}")
        print()

        # Operacional
        print("OPERACIONAL:")
        print(f"  - Setores: {SetorPropriedade.objects.filter(propriedade=self.propriedade).count()}")
        print(f"  - Funcionarios: {Funcionario.objects.filter(propriedade=self.propriedade).count()}")
        print(f"  - Pastagens: {Pastagem.objects.filter(propriedade=self.propriedade).count()}")
        print(f"  - Cochos: {Cocho.objects.filter(propriedade=self.propriedade).count()}")
        print(f"  - Equipamentos: {Equipamento.objects.filter(propriedade=self.propriedade).count()}")
        print()

        # Nutrição
        print("NUTRICAO:")
        print(f"  - Tipos de Distribuicao: {TipoDistribuicao.objects.count()}")
        print(f"  - Distribuicoes no Pasto: {DistribuicaoPasto.objects.filter(propriedade=self.propriedade).count()}")
        print(f"  - Controles de Cochos: {ControleCocho.objects.filter(cocho__propriedade=self.propriedade).count()}")
        print(f"  - Estoques Suplementacao: {EstoqueSuplementacao.objects.filter(propriedade=self.propriedade).count()}")
        print()

        print("="*80)
        print("FAZENDA DEMONSTRACAO POPULADA COM SUCESSO!")
        print("Dados realistas para 24 meses historicos + 6 meses de projecao")
        print("Sistema pronto para demonstracao e testes!")
        print("="*80)

def main():
    try:
        populador = PopuladorFazendaDemonstracao()
        populador.main()
    except Exception as e:
        print(f"\nERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
