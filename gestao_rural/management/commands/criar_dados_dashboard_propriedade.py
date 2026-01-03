# -*- coding: utf-8 -*-
"""
Comando Django para criar dados para o dashboard da propriedade
python manage.py criar_dados_dashboard_propriedade --propriedade-id 19
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random

from gestao_rural.models import (
    Propriedade, InventarioRebanho, CategoriaAnimal
)


class Command(BaseCommand):
    help = 'Cria dados financeiros e operacionais para preencher o dashboard de uma propriedade'

    def add_arguments(self, parser):
        parser.add_argument(
            '--propriedade-id',
            type=int,
            default=19,
            help='ID da propriedade (padrão: 19 - Monpec1)'
        )
        parser.add_argument(
            '--data-inicio',
            type=str,
            default='2025-01-01',
            help='Data de início do período (formato: YYYY-MM-DD)'
        )

    def handle(self, *args, **options):
        propriedade_id = options['propriedade_id']
        data_inicio_str = options['data_inicio']
        
        try:
            data_inicio = date.fromisoformat(data_inicio_str)
        except ValueError:
            self.stdout.write(self.style.ERROR(f'Data inválida: {data_inicio_str}. Use formato YYYY-MM-DD'))
            return
        
        data_fim = timezone.localdate()
        
        # Buscar propriedade
        try:
            propriedade = Propriedade.objects.get(id=propriedade_id)
            self.stdout.write(self.style.SUCCESS(f'Propriedade encontrada: {propriedade.nome_propriedade}'))
        except Propriedade.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Propriedade com ID {propriedade_id} nao encontrada!'))
            return
        
        # Importar modelos financeiros
        try:
            from gestao_rural.models_financeiro import (
                LancamentoFinanceiro, CategoriaFinanceira, ContaFinanceira, CentroCusto
            )
        except ImportError:
            self.stdout.write(self.style.ERROR('Erro ao importar modelos financeiros'))
            return
        
        # Importar modelos operacionais
        try:
            from gestao_rural.models_operacional import (
                TanqueCombustivel, ConsumoCombustivel,
                EstoqueSuplementacao, DistribuicaoSuplementacao
            )
            from gestao_rural.models_controles_operacionais import Cocho
            from gestao_rural.models_funcionarios import Funcionario
            from gestao_rural.models_reproducao import Nascimento
        except ImportError as e:
            self.stdout.write(self.style.WARNING(f'Alguns modulos nao disponiveis: {e}'))
            ConsumoCombustivel = None
            DistribuicaoSuplementacao = None
            Nascimento = None
            Funcionario = None
        
        self.stdout.write(self.style.SUCCESS(f'\nCriando dados para o periodo: {data_inicio} ate {data_fim}'))
        
        # 1. Garantir categorias e contas financeiras
        self.stdout.write('\nConfigurando categorias financeiras...')
        categoria_receita, _ = CategoriaFinanceira.objects.get_or_create(
            nome='Venda de Gado',
            defaults={
                'tipo': CategoriaFinanceira.TIPO_RECEITA,
                'descricao': 'Receitas com venda de gado'
            }
        )
        
        categoria_despesa_combustivel, _ = CategoriaFinanceira.objects.get_or_create(
            nome='Combustível',
            defaults={
                'tipo': CategoriaFinanceira.TIPO_DESPESA,
                'descricao': 'Despesas com combustível'
            }
        )
        
        categoria_despesa_suplemento, _ = CategoriaFinanceira.objects.get_or_create(
            nome='Suplementação',
            defaults={
                'tipo': CategoriaFinanceira.TIPO_DESPESA,
                'descricao': 'Despesas com suplementação'
            }
        )
        
        categoria_despesa_folha, _ = CategoriaFinanceira.objects.get_or_create(
            nome='Folha de Pagamento',
            defaults={
                'tipo': CategoriaFinanceira.TIPO_DESPESA,
                'descricao': 'Despesas com folha de pagamento'
            }
        )
        
        categoria_despesa_veterinario, _ = CategoriaFinanceira.objects.get_or_create(
            nome='Medicamentos e Veterinário',
            defaults={
                'tipo': CategoriaFinanceira.TIPO_DESPESA,
                'descricao': 'Despesas com medicamentos, vacinas e produtos veterinários'
            }
        )
        
        # Conta financeira - buscar existente ou criar
        conta_principal = ContaFinanceira.objects.filter(
            propriedade=propriedade
        ).first()
        
        if not conta_principal:
            # Tentar criar com os campos que existem
            try:
                conta_principal = ContaFinanceira.objects.create(
                    propriedade=propriedade,
                    nome='Caixa Principal',
                    tipo=ContaFinanceira.TIPO_CAIXA,
                    banco='Caixa',
                    saldo_inicial=Decimal('100000.00'),
                    ativa=True
                )
            except Exception as e:
                # Se falhar, tentar sem banco ou com instituicao se o campo existir
                try:
                    # Verificar se o campo instituicao existe
                    # Tentar com instituicao usando raw SQL se necessário
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO gestao_rural_contafinanceira 
                            (propriedade_id, nome, tipo, instituicao, saldo_inicial, ativa, criado_em, atualizado_em)
                            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                        """, (
                            propriedade.id,
                            'Caixa Principal',
                            ContaFinanceira.TIPO_CAIXA,
                            'Caixa',
                            Decimal('100000.00'),
                            1
                        ))
                        conta_id = cursor.lastrowid
                        conta_principal = ContaFinanceira.objects.get(id=conta_id)
                except Exception as e2:
                    self.stdout.write(self.style.WARNING(f'Erro ao criar conta financeira: {e2}'))
                    # Usar qualquer conta existente ou pular se não houver
                    conta_principal = None
        
        # Centro de custo - buscar existente ou criar
        centro_custo = CentroCusto.objects.filter(
            propriedade=propriedade
        ).first()
        
        if not centro_custo:
            try:
                # Tentar criar com codigo se o campo existir
                create_kwargs = {
                    'propriedade': propriedade,
                    'nome': 'Bovinos',
                    'descricao': 'Centro de custo para bovinos',
                    'ativo': True
                }
                # Tentar criar normalmente, se falhar, usar raw SQL para adicionar codigo
                try:
                    if hasattr(CentroCusto, 'codigo'):
                        create_kwargs['codigo'] = 'BOV'
                    centro_custo = CentroCusto.objects.create(**create_kwargs)
                except Exception as e2:
                    # Se falhar, usar raw SQL
                    from django.db import connection
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO gestao_rural_centrocusto 
                            (propriedade_id, nome, tipo, codigo, descricao, ativo, criado_em, atualizado_em)
                            VALUES (?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                        """, (
                            propriedade.id,
                            'Bovinos',
                            CentroCusto.TIPO_OPERACIONAL,
                            'BOV',
                            'Centro de custo para bovinos',
                            1
                        ))
                        centro_id = cursor.lastrowid
                        centro_custo = CentroCusto.objects.get(id=centro_id)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Erro ao criar centro de custo: {e}'))
                centro_custo = None
        
        # 2. Atualizar inventário com valores se necessário
        self.stdout.write('\nVerificando e atualizando inventario...')
        inventarios = InventarioRebanho.objects.filter(propriedade=propriedade)
        total_atualizado = 0
        
        for inventario in inventarios:
            if not inventario.valor_por_cabeca or inventario.valor_por_cabeca == 0:
                # Definir valor médio por cabeça baseado na categoria
                if 'bezerro' in inventario.categoria.nome.lower() or 'bezerra' in inventario.categoria.nome.lower():
                    valor_medio = Decimal('800.00')
                elif 'novilho' in inventario.categoria.nome.lower() or 'novilha' in inventario.categoria.nome.lower():
                    valor_medio = Decimal('1200.00')
                elif 'vaca' in inventario.categoria.nome.lower():
                    valor_medio = Decimal('1500.00')
                elif 'touro' in inventario.categoria.nome.lower():
                    valor_medio = Decimal('3000.00')
                else:
                    valor_medio = Decimal('1000.00')
                
                inventario.valor_por_cabeca = valor_medio
                inventario.save()
                total_atualizado += 1
        
        if total_atualizado > 0:
            self.stdout.write(self.style.SUCCESS(f'Atualizados {total_atualizado} itens do inventario com valores'))
        
        # 3. Criar lançamentos financeiros (receitas e despesas)
        self.stdout.write('\nCriando lancamentos financeiros...')
        
        # Calcular quantos meses no período
        meses_no_periodo = (data_fim.year - data_inicio.year) * 12 + (data_fim.month - data_inicio.month) + 1
        
        receitas_criadas = 0
        despesas_criadas = 0
        
        # Criar receitas (vendas de gado) - 2-4 por mês
        current_date = data_inicio
        while current_date <= data_fim:
            # Criar 2-4 receitas por mês
            num_receitas = random.randint(2, 4)
            for _ in range(num_receitas):
                # Distribuir ao longo do mês
                dia = random.randint(1, 28)
                try:
                    data_comp = current_date.replace(day=dia)
                except ValueError:
                    data_comp = current_date.replace(day=28)
                
                if data_comp > data_fim:
                    break
                
                valor_receita = Decimal(str(random.uniform(50000, 150000))).quantize(Decimal('0.01'))
                
                LancamentoFinanceiro.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_receita,
                    centro_custo=centro_custo,
                    conta_destino=conta_principal,
                    tipo=CategoriaFinanceira.TIPO_RECEITA,
                    descricao=f'Venda de gado - {data_comp.strftime("%m/%Y")}',
                    valor=valor_receita,
                    data_competencia=data_comp,
                    data_vencimento=data_comp,
                    data_quitacao=data_comp if random.random() > 0.2 else None,
                    forma_pagamento=LancamentoFinanceiro.FORMA_PIX,
                    status=LancamentoFinanceiro.STATUS_QUITADO if random.random() > 0.2 else LancamentoFinanceiro.STATUS_PENDENTE
                )
                receitas_criadas += 1
            
            # Avançar para o próximo mês
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        self.stdout.write(self.style.SUCCESS(f'Criadas {receitas_criadas} receitas'))
        
        # Criar despesas mensais recorrentes
        current_date = data_inicio
        while current_date <= data_fim:
            # Combustível - 2-3 por mês
            for _ in range(random.randint(2, 3)):
                dia = random.randint(1, 28)
                try:
                    data_comp = current_date.replace(day=dia)
                except ValueError:
                    data_comp = current_date.replace(day=28)
                
                if data_comp > data_fim:
                    break
                
                # Combustível: ~R$ 150.000-250.000/ano para propriedade média
                # 2-3 compras/mês = R$ 4.000-8.000 por compra
                valor = Decimal(str(random.uniform(4000, 8000))).quantize(Decimal('0.01'))
                
                LancamentoFinanceiro.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_despesa_combustivel,
                    centro_custo=centro_custo,
                    conta_origem=conta_principal,
                    tipo=CategoriaFinanceira.TIPO_DESPESA,
                    descricao=f'Combustível - {data_comp.strftime("%m/%Y")}',
                    valor=valor,
                    data_competencia=data_comp,
                    data_vencimento=data_comp,
                    data_quitacao=data_comp if random.random() > 0.3 else None,
                    forma_pagamento=LancamentoFinanceiro.FORMA_PIX,
                    status=LancamentoFinanceiro.STATUS_QUITADO if random.random() > 0.3 else LancamentoFinanceiro.STATUS_PENDENTE
                )
                despesas_criadas += 1
            
            # Veterinário (Medicamentos e Vacinas) - 2-4 por mês
            for _ in range(random.randint(2, 4)):
                dia = random.randint(1, 28)
                try:
                    data_comp = current_date.replace(day=dia)
                except ValueError:
                    data_comp = current_date.replace(day=28)
                
                if data_comp > data_fim:
                    break
                
                # Veterinário: ~R$ 100-150/animal/ano = R$ 238.500-357.750/ano para 2385 animais
                # Dividindo por 12 meses e 2-4 compras/mês = R$ 5.000-15.000 por compra
                valor = Decimal(str(random.uniform(5000, 15000))).quantize(Decimal('0.01'))
                
                LancamentoFinanceiro.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_despesa_veterinario,
                    centro_custo=centro_custo,
                    conta_origem=conta_principal,
                    tipo=CategoriaFinanceira.TIPO_DESPESA,
                    descricao=f'Produtos Veterinários - {data_comp.strftime("%m/%Y")}',
                    valor=valor,
                    data_competencia=data_comp,
                    data_vencimento=data_comp,
                    data_quitacao=data_comp if random.random() > 0.3 else None,
                    forma_pagamento=LancamentoFinanceiro.FORMA_PIX,
                    status=LancamentoFinanceiro.STATUS_QUITADO if random.random() > 0.3 else LancamentoFinanceiro.STATUS_PENDENTE
                )
                despesas_criadas += 1
            
            # Suplementação - 4-6 por mês
            for _ in range(random.randint(4, 6)):
                dia = random.randint(1, 28)
                try:
                    data_comp = current_date.replace(day=dia)
                except ValueError:
                    data_comp = current_date.replace(day=28)
                
                if data_comp > data_fim:
                    break
                
                # Suplementação: ~R$ 200-300/animal/ano = R$ 477.000-715.500/ano
                # 4-6 compras/mês = R$ 6.000-12.000 por compra
                valor = Decimal(str(random.uniform(6000, 12000))).quantize(Decimal('0.01'))
                
                LancamentoFinanceiro.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_despesa_suplemento,
                    centro_custo=centro_custo,
                    conta_origem=conta_principal,
                    tipo=CategoriaFinanceira.TIPO_DESPESA,
                    descricao=f'Suplementação - {data_comp.strftime("%m/%Y")}',
                    valor=valor,
                    data_competencia=data_comp,
                    data_vencimento=data_comp,
                    data_quitacao=data_comp if random.random() > 0.3 else None,
                    forma_pagamento=LancamentoFinanceiro.FORMA_PIX,
                    status=LancamentoFinanceiro.STATUS_QUITADO if random.random() > 0.3 else LancamentoFinanceiro.STATUS_PENDENTE
                )
                despesas_criadas += 1
            
            # Folha de pagamento - 1 por mês
            dia = random.randint(1, 10)
            try:
                data_comp = current_date.replace(day=dia)
            except ValueError:
                data_comp = current_date.replace(day=5)
            
            if data_comp <= data_fim:
                # Folha: 5-8 funcionários × R$ 2.000-3.500 = R$ 10.000-28.000/mês
                # Usar valor médio para o mês
                valor = Decimal(str(random.uniform(10000, 20000))).quantize(Decimal('0.01'))
                
                LancamentoFinanceiro.objects.create(
                    propriedade=propriedade,
                    categoria=categoria_despesa_folha,
                    centro_custo=centro_custo,
                    conta_origem=conta_principal,
                    tipo=CategoriaFinanceira.TIPO_DESPESA,
                    descricao=f'Folha de Pagamento - {data_comp.strftime("%m/%Y")}',
                    valor=valor,
                    data_competencia=data_comp,
                    data_vencimento=data_comp,
                    data_quitacao=data_comp,
                    forma_pagamento=LancamentoFinanceiro.FORMA_TRANSFERENCIA,
                    status=LancamentoFinanceiro.STATUS_QUITADO
                )
                despesas_criadas += 1
            
            # Avançar para o próximo mês
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        self.stdout.write(self.style.SUCCESS(f'Criadas {despesas_criadas} despesas'))
        
        # 4. Criar dados de consumo de combustível se módulo disponível
        if ConsumoCombustivel:
            self.stdout.write('\nCriando dados de consumo de combustivel...')
            tanques = TanqueCombustivel.objects.filter(propriedade=propriedade)
            
            if tanques.exists():
                tanque = tanques.first()
                consumos_criados = 0
                
                current_date = data_inicio
                while current_date <= data_fim:
                    # 2-3 consumos por mês
                    for _ in range(random.randint(2, 3)):
                        dia = random.randint(1, 28)
                        try:
                            data_consumo = current_date.replace(day=dia)
                        except ValueError:
                            data_consumo = current_date.replace(day=28)
                        
                        if data_consumo > data_fim:
                            break
                        
                        # Combustível: consumo realista para propriedade pecuária
                        # ~R$ 150.000-250.000/ano = R$ 12.500-20.800/mês
                        # 2-3 abastecimentos/mês = R$ 4.000-10.000 por abastecimento
                        litros = Decimal(str(random.uniform(700, 1500))).quantize(Decimal('0.01'))
                        preco_litro = Decimal('5.50')
                        valor_total = (litros * preco_litro).quantize(Decimal('0.01'))
                        
                        # Criar com campos que existem no modelo
                        ConsumoCombustivel.objects.create(
                            propriedade=propriedade,
                            tanque=tanque,
                            quantidade_litros=litros,
                            valor_unitario=preco_litro,
                            valor_total=valor_total,
                            data=data_consumo,
                            tipo_equipamento=random.choice(['Trator', 'Caminhão', 'Máquina']),
                            identificacao=f'{random.randint(1, 10)}'
                        )
                        consumos_criados += 1
                    
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                
                self.stdout.write(self.style.SUCCESS(f'Criados {consumos_criados} consumos de combustivel'))
            else:
                self.stdout.write(self.style.WARNING('Nenhum tanque de combustivel encontrado'))
        
        # 5. Criar distribuições de suplementação se módulo disponível
        if DistribuicaoSuplementacao:
            self.stdout.write('\nCriando dados de distribuicao de suplementacao...')
            estoques = EstoqueSuplementacao.objects.filter(propriedade=propriedade)
            
            if estoques.exists():
                estoque = estoques.first()
                distribuicoes_criadas = 0
                
                current_date = data_inicio
                while current_date <= data_fim:
                    # 4-6 distribuições por mês
                    for _ in range(random.randint(4, 6)):
                        dia = random.randint(1, 28)
                        try:
                            data_dist = current_date.replace(day=dia)
                        except ValueError:
                            data_dist = current_date.replace(day=28)
                        
                        if data_dist > data_fim:
                            break
                        
                        quantidade = Decimal(str(random.uniform(100, 500))).quantize(Decimal('0.01'))
                        preco_unitario = Decimal(str(random.uniform(2.50, 5.00))).quantize(Decimal('0.01'))
                        valor_total = (quantidade * preco_unitario).quantize(Decimal('0.01'))
                        
                        DistribuicaoSuplementacao.objects.create(
                            estoque=estoque,
                            quantidade=quantidade,
                            valor_unitario=preco_unitario,
                            valor_total=valor_total,
                            data=data_dist,
                            observacoes=f'Distribuição de suplementação - {data_dist.strftime("%d/%m/%Y")}',
                            numero_animais=random.randint(50, 200)
                        )
                        distribuicoes_criadas += 1
                    
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                
                self.stdout.write(self.style.SUCCESS(f'Criadas {distribuicoes_criadas} distribuicoes de suplementacao'))
            else:
                self.stdout.write(self.style.WARNING('Nenhum estoque de suplementacao encontrado - criando estoque...'))
                # Criar estoque se não existir
                try:
                    estoque = EstoqueSuplementacao.objects.create(
                        propriedade=propriedade,
                        tipo_suplemento='Sal Mineral',
                        quantidade_atual=Decimal('5000'),
                        quantidade_minima=Decimal('500'),
                        valor_unitario_medio=Decimal('3.50'),
                        valor_total_estoque=Decimal('17500')
                    )
                    
                    # Agora criar distribuições
                    distribuicoes_criadas = 0
                    current_date = data_inicio
                    while current_date <= data_fim:
                        for _ in range(random.randint(4, 6)):
                            dia = random.randint(1, 28)
                            try:
                                data_dist = current_date.replace(day=dia)
                            except ValueError:
                                data_dist = current_date.replace(day=28)
                            
                            if data_dist > data_fim:
                                break
                            
                            quantidade = Decimal(str(random.uniform(100, 500))).quantize(Decimal('0.01'))
                            preco_unitario = Decimal(str(random.uniform(2.50, 5.00))).quantize(Decimal('0.01'))
                            valor_total = (quantidade * preco_unitario).quantize(Decimal('0.01'))
                            
                            DistribuicaoSuplementacao.objects.create(
                                estoque=estoque,
                                quantidade=quantidade,
                                valor_unitario=preco_unitario,
                                valor_total=valor_total,
                                data=data_dist,
                                observacoes=f'Distribuição de suplementação - {data_dist.strftime("%d/%m/%Y")}',
                                numero_animais=random.randint(50, 200)
                            )
                            distribuicoes_criadas += 1
                        
                        if current_date.month == 12:
                            current_date = current_date.replace(year=current_date.year + 1, month=1)
                        else:
                            current_date = current_date.replace(month=current_date.month + 1)
                    
                    self.stdout.write(self.style.SUCCESS(f'Criado estoque e {distribuicoes_criadas} distribuicoes'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Erro ao criar estoque: {e}'))
        
        # 6. Criar nascimentos se módulo disponível
        if Nascimento:
            self.stdout.write('\nCriando dados de nascimentos...')
            nascimentos_criados = 0
            
            current_date = data_inicio
            while current_date <= data_fim:
                # 10-30 nascimentos por mês
                num_nascimentos = random.randint(10, 30)
                for _ in range(num_nascimentos):
                    dia = random.randint(1, 28)
                    try:
                        data_nasc = current_date.replace(day=dia)
                    except ValueError:
                        data_nasc = current_date.replace(day=28)
                    
                    if data_nasc > data_fim:
                        break
                    
                    # Buscar animais fêmeas para usar como mãe (se disponível)
                    try:
                        from gestao_rural.models import AnimalIndividual
                        maes = AnimalIndividual.objects.filter(
                            propriedade=propriedade,
                            categoria__sexo='F'
                        )
                        if maes.exists():
                            mae = random.choice(list(maes))
                        else:
                            mae = None
                    except:
                        mae = None
                    
                    sexo = random.choice(['M', 'F'])
                    
                    # Criar nascimento com campos corretos
                    try:
                        Nascimento.objects.create(
                            propriedade=propriedade,
                            mae=mae if mae else None,
                            sexo=sexo,
                            data_nascimento=data_nasc,
                            observacoes=f'Nascimento registrado em {data_nasc.strftime("%d/%m/%Y")}'
                        )
                    except Exception as nasc_error:
                        # Se falhar, tentar criar sem alguns campos opcionais
                        try:
                            Nascimento.objects.create(
                                propriedade=propriedade,
                                sexo=sexo,
                                data_nascimento=data_nasc
                            )
                        except Exception:
                            # Se ainda falhar, pular este nascimento
                            continue
                    nascimentos_criados += 1
                
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            
            self.stdout.write(self.style.SUCCESS(f'Criados {nascimentos_criados} nascimentos'))
        
        # 6.5. Criar manutenções de equipamentos
        self.stdout.write('\nCriando manutencoes de equipamentos...')
        try:
            from gestao_rural.models_operacional import Equipamento, ManutencaoEquipamento
            
            # Criar equipamentos se não existirem
            equipamentos_criados = 0
            tipos_equipamentos = ['Trator', 'Caminhão', 'Pulverizador', 'Arado']
            for tipo in tipos_equipamentos:
                if not Equipamento.objects.filter(propriedade=propriedade, nome=tipo).exists():
                    try:
                        try:
                            from gestao_rural.models_operacional import TipoEquipamento
                            tipo_eq, _ = TipoEquipamento.objects.get_or_create(
                                nome='Outros',
                                defaults={'descricao': 'Equipamentos diversos', 'ativo': True}
                            )
                            Equipamento.objects.create(
                                propriedade=propriedade,
                                nome=tipo,
                                tipo=tipo_eq,
                                ativo=True
                            )
                        except:
                            # Tentar sem tipo se falhar
                            Equipamento.objects.create(
                                propriedade=propriedade,
                                nome=tipo,
                                ativo=True
                            )
                        equipamentos_criados += 1
                    except:
                        pass
            
            if equipamentos_criados > 0:
                self.stdout.write(self.style.SUCCESS(f'Criados {equipamentos_criados} equipamentos'))
            
            # Criar manutenções
            equipamentos = Equipamento.objects.filter(propriedade=propriedade, ativo=True)[:5]
            manutencoes_criadas = 0
            
            if equipamentos.exists():
                current_date = data_inicio
                while current_date <= data_fim:
                    # 1-3 manutenções por mês
                    for _ in range(random.randint(1, 3)):
                        dia = random.randint(1, 28)
                        try:
                            data_manut = current_date.replace(day=dia)
                        except ValueError:
                            data_manut = current_date.replace(day=28)
                        
                        if data_manut > data_fim:
                            break
                        
                        equipamento = random.choice(list(equipamentos))
                        # Manutenção: valores realistas para tratores e equipamentos
                        valor_pecas = Decimal(str(random.uniform(1000, 8000))).quantize(Decimal('0.01'))
                        valor_mao_obra = Decimal(str(random.uniform(500, 3000))).quantize(Decimal('0.01'))
                        valor_total = valor_pecas + valor_mao_obra
                        
                        try:
                            ManutencaoEquipamento.objects.create(
                                propriedade=propriedade,
                                equipamento=equipamento,
                                tipo=random.choice(['PREVENTIVA', 'CORRETIVA', 'REVISAO']),
                                descricao=f'Manutenção {random.choice(["preventiva", "corretiva", "revisão"])} - {data_manut.strftime("%m/%Y")}',
                                data_agendamento=data_manut,
                                data_realizacao=data_manut if random.random() > 0.3 else None,
                                valor_pecas=valor_pecas,
                                valor_mao_obra=valor_mao_obra,
                                valor_total=valor_total,
                                status=random.choice(['AGENDADA', 'EM_ANDAMENTO', 'CONCLUIDA'])
                            )
                            manutencoes_criadas += 1
                        except:
                            continue
                    
                    if current_date.month == 12:
                        current_date = current_date.replace(year=current_date.year + 1, month=1)
                    else:
                        current_date = current_date.replace(month=current_date.month + 1)
                
                self.stdout.write(self.style.SUCCESS(f'Criadas {manutencoes_criadas} manutencoes'))
            else:
                self.stdout.write(self.style.WARNING('Nenhum equipamento encontrado para criar manutencoes'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao criar manutencoes: {e}'))
        
        # 7. Criar dados para Pecuária (Animais Rastreados, Touros, IATFs)
        self.stdout.write('\nCriando dados de pecuaria...')
        animais_criados = 0
        touros_criados = 0
        iatfs_criados = 0
        try:
            from gestao_rural.models import AnimalIndividual, CategoriaAnimal
            from gestao_rural.models_reproducao import Touro, IATF
            
            # Animais rastreados - CategoriaAnimal tem propriedade sim
            categorias_femeas = CategoriaAnimal.objects.filter(propriedade=propriedade, sexo='F')[:5]
            categorias_machos = CategoriaAnimal.objects.filter(propriedade=propriedade, sexo='M')[:5]
            
            if categorias_femeas.exists() or categorias_machos.exists():
                for i in range(random.randint(50, 200)):
                    categoria = random.choice(list(categorias_femeas) + list(categorias_machos))
                    codigo_sisbov = f'BR{random.randint(1000000000000, 9999999999999)}'
                    
                    try:
                        AnimalIndividual.objects.create(
                            propriedade=propriedade,
                            categoria=categoria,
                            codigo_sisbov=codigo_sisbov,
                            numero_brinco=f'{random.randint(1000, 9999)}',
                            status='ATIVO',
                            status_sanitario='APTO'
                        )
                        animais_criados += 1
                    except:
                        continue
                
                self.stdout.write(self.style.SUCCESS(f'Criados {animais_criados} animais rastreados'))
            
            # Touros aptos
            for i in range(random.randint(5, 15)):
                try:
                    numero_brinco = f'TOURO{random.randint(1, 999)}'
                    if not Touro.objects.filter(numero_brinco=numero_brinco).exists():
                        Touro.objects.create(
                            propriedade=propriedade,
                            numero_brinco=numero_brinco,
                            nome=f'Touro {numero_brinco}',
                            raca=random.choice(['Nelore', 'Angus', 'Brahman', 'Hereford']),
                            status='APTO',
                            propriedade_touro='PROPRIO'
                        )
                        touros_criados += 1
                except:
                    continue
            
            self.stdout.write(self.style.SUCCESS(f'Criados {touros_criados} touros aptos'))
            
            # IATFs pendentes
            animais_femeas = AnimalIndividual.objects.filter(propriedade=propriedade, categoria__sexo='F', status='ATIVO')[:20]
            if animais_femeas.exists():
                for animal in animais_femeas[:random.randint(5, 15)]:
                    data_prog = date.today() + timedelta(days=random.randint(1, 30))
                    try:
                        IATF.objects.create(
                            propriedade=propriedade,
                            animal_individual=animal,
                            data_programada=data_prog,
                            protocolo='Ovsynch',
                            status='PROGRAMADA',
                            resultado='PENDENTE'
                        )
                        iatfs_criados += 1
                    except:
                        continue
            
            self.stdout.write(self.style.SUCCESS(f'Criadas {iatfs_criados} IATFs pendentes'))
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao criar dados de pecuaria: {e}'))
        
        # 8. Criar dados para Nutrição (Estoque com valores, Cochos)
        self.stdout.write('\nCriando dados de nutricao...')
        estoques_atualizados = 0
        cochos_criados = 0
        try:
            from gestao_rural.models_operacional import EstoqueSuplementacao
            from gestao_rural.models_controles_operacionais import Cocho
            
            # Criar/atualizar estoques com valores
            tipos_suplementos = ['Sal Mineral', 'Ração', 'Suplemento Proteico', 'Vitaminas']
            for tipo in tipos_suplementos:
                estoque, created = EstoqueSuplementacao.objects.get_or_create(
                    propriedade=propriedade,
                    tipo_suplemento=tipo,
                    defaults={
                        'quantidade_atual': Decimal(str(random.uniform(1000, 5000))),
                        'quantidade_minima': Decimal('500'),
                        'valor_unitario_medio': Decimal(str(random.uniform(2.50, 8.00))),
                        'valor_total_estoque': Decimal('0')
                    }
                )
                if created or estoque.valor_total_estoque == 0:
                    estoque.valor_total_estoque = estoque.quantidade_atual * estoque.valor_unitario_medio
                    estoque.save()
                    estoques_atualizados += 1
            
            self.stdout.write(self.style.SUCCESS(f'Atualizados {estoques_atualizados} estoques de suplementacao'))
            
            # Criar cochos ativos
            for i in range(random.randint(10, 25)):
                try:
                    Cocho.objects.create(
                        propriedade=propriedade,
                        nome=f'Cocho {i+1}',
                        tipo_cocho=random.choice(['SAL', 'RACAO', 'AGUA', 'MISTO']),
                        capacidade=Decimal(str(random.uniform(50, 200))),
                        status='ATIVO'
                    )
                    cochos_criados += 1
                except:
                    continue
            
            self.stdout.write(self.style.SUCCESS(f'Criados {cochos_criados} cochos ativos'))
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao criar dados de nutricao: {e}'))
        
        # 9. Criar dados para Compras (Requisições e Ordens pendentes)
        self.stdout.write('\nCriando dados de compras...')
        requisicoes_criadas = 0
        ordens_criadas = 0
        try:
            from gestao_rural.models_compras_financeiro import RequisicaoCompra, OrdemCompra, Fornecedor
            
            # Criar fornecedor se não existir
            fornecedor, _ = Fornecedor.objects.get_or_create(
                propriedade=propriedade,
                nome='Fornecedor Exemplo Ltda',
                defaults={
                    'cnpj': '12345678000190',
                    'ativo': True
                }
            )
            
            # Requisições pendentes
            for i in range(random.randint(2, 8)):
                try:
                    RequisicaoCompra.objects.create(
                        propriedade=propriedade,
                        titulo=f'Requisição {i+1}',
                        status='PENDENTE'
                    )
                    requisicoes_criadas += 1
                except:
                    continue
            
            self.stdout.write(self.style.SUCCESS(f'Criadas {requisicoes_criadas} requisicoes pendentes'))
            
            # Ordens pendentes
            for i in range(random.randint(1, 5)):
                try:
                    numero = f'OC-{date.today().year}-{random.randint(1000, 9999)}'
                    if not OrdemCompra.objects.filter(numero_ordem=numero).exists():
                        OrdemCompra.objects.create(
                            propriedade=propriedade,
                            fornecedor=fornecedor,
                            numero_ordem=numero,
                            data_emissao=date.today() - timedelta(days=random.randint(1, 30)),
                            data_entrega_prevista=date.today() + timedelta(days=random.randint(5, 15)),
                            status=random.choice(['APROVADA', 'ENVIADA']),
                            valor_total=Decimal(str(random.uniform(5000, 50000)))
                        )
                        ordens_criadas += 1
                except:
                    continue
            
            self.stdout.write(self.style.SUCCESS(f'Criadas {ordens_criadas} ordens pendentes'))
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao criar dados de compras: {e}'))
        
        # 10. Criar dados para Bens e Patrimônio
        self.stdout.write('\nCriando dados de bens e patrimonio...')
        bens_criados = 0
        try:
            from gestao_rural.models_patrimonio import BemPatrimonial, TipoBem
            
            # Criar tipos de bens se não existirem
            tipos_nomes = ['Trator', 'Caminhão', 'Implemento', 'Máquina', 'Benfeitoria']
            tipos_criados = []
            for nome_tipo in tipos_nomes:
                tipo, _ = TipoBem.objects.get_or_create(
                    nome=nome_tipo,
                    defaults={
                        'categoria': 'EQUIPAMENTO' if nome_tipo != 'Benfeitoria' else 'IMOVEL',
                        'taxa_depreciacao': Decimal('10.00')
                    }
                )
                tipos_criados.append(tipo)
            
            # Criar bens patrimoniais
            for i, tipo_bem in enumerate(tipos_criados):
                try:
                    BemPatrimonial.objects.create(
                        propriedade=propriedade,
                        tipo_bem=tipo_bem,
                        descricao=f'{tipo_bem.nome} {i+1}',
                        data_aquisicao=date.today() - timedelta(days=random.randint(365, 3650)),
                        valor_aquisicao=Decimal(str(random.uniform(50000, 500000))),
                        valor_residual=Decimal('10000'),
                        quantidade=random.randint(1, 3),
                        estado_conservacao=random.choice(['NOVO', 'OTIMO', 'BOM', 'REGULAR']),
                        ativo=True
                    )
                    bens_criados += 1
                except:
                    continue
            
            self.stdout.write(self.style.SUCCESS(f'Criados {bens_criados} bens patrimoniais'))
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao criar dados de patrimonio: {e}'))
        
        # Resumo
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('DADOS CRIADOS COM SUCESSO!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(f'Propriedade: {propriedade.nome_propriedade} (ID: {propriedade.id})')
        self.stdout.write(f'Periodo: {data_inicio} ate {data_fim}')
        self.stdout.write(f'Receitas criadas: {receitas_criadas}')
        self.stdout.write(f'Despesas criadas: {despesas_criadas}')
        self.stdout.write(self.style.SUCCESS('\nRecarregue o dashboard para ver os dados!'))

