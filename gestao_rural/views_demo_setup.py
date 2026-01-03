# -*- coding: utf-8 -*-
"""
View para configurar automaticamente o ambiente de demonstração
Cria produtor, propriedade e dados realistas automaticamente
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
import random
import logging

from .models import ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho
from .models_auditoria import UsuarioAtivo

logger = logging.getLogger(__name__)


@login_required
def demo_setup(request):
    """
    Configura automaticamente o ambiente de demonstração para usuários demo.
    Cria produtor, propriedade Monpec1 e dados realistas.
    """
    logger.info(f'DEMO_SETUP CHAMADO - user: {request.user.username}')
    
    # Verificar se é usuário de demonstração
    is_demo_user = False
    
    # Verificar se é usuário demo padrão
    if request.user.username in ['demo', 'demo_monpec']:
        is_demo_user = True
        logger.info(f'Usuário demo padrão detectado: {request.user.username}')
    else:
        # Verificar se é usuário de demonstração (do popup)
        try:
            UsuarioAtivo.objects.get(usuario=request.user)
            is_demo_user = True
            logger.info(f'Usuário demo (popup) detectado: {request.user.username}')
        except:
            logger.info(f'Usuário {request.user.username} não é demo')
            pass
    
    if not is_demo_user:
        logger.warning(f'Usuário não demo tentou acessar demo_setup: {request.user.username}')
        messages.error(request, 'Esta página é apenas para usuários de demonstração.')
        return redirect('dashboard')
    
    # Verificar se já tem produtor e propriedade
    produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
    propriedade = None
    
    if produtor:
        propriedade = Propriedade.objects.filter(
            produtor=produtor,
            nome_propriedade__iregex=r'^Monpec\d+$'
        ).order_by('nome_propriedade').first()
        
        if propriedade:
            # Já está configurado, redirecionar para a propriedade
            logger.info(f'Demonstração já configurada. Redirecionando para propriedade {propriedade.id}')
            messages.success(request, 'Demonstração já configurada! Redirecionando...')
            return redirect('propriedade_modulos', propriedade_id=propriedade.id)
    
    # Se chegou aqui, precisa criar tudo automaticamente
    logger.info(f'Iniciando criação automática de dados para demonstração...')
    try:
        with transaction.atomic():
            # 1. Criar ou obter produtor
            if not produtor:
                # Obter dados do UsuarioAtivo se disponível
                nome_completo = request.user.get_full_name() or request.user.username
                email = request.user.email or f'{request.user.username}@demo.com'
                telefone = ''
                
                try:
                    usuario_ativo = UsuarioAtivo.objects.get(usuario=request.user)
                    nome_completo = usuario_ativo.nome_completo
                    email = usuario_ativo.email
                    telefone = usuario_ativo.telefone or ''
                except:
                    pass
                
                # Criar produtor com identificador único "demonstração" no CPF/CNPJ
                # Usar CPF único por usuário para evitar conflito de unique constraint
                cpf_demo = f'DEMO-{request.user.id:06d}'  # Formato: DEMO-000001, DEMO-000002, etc.
                
                produtor, created = ProdutorRural.objects.get_or_create(
                    usuario_responsavel=request.user,
                    defaults={
                        'nome': nome_completo or 'Produtor Demo',
                        'cpf_cnpj': cpf_demo,
                        'email': email,
                        'telefone': telefone,
                        'endereco': 'Campo Grande, MS',
                        'anos_experiencia': 10
                    }
                )
                if created:
                    logger.info(f'Produtor criado: {produtor.nome} (CPF: {cpf_demo})')
                else:
                    logger.info(f'Produtor já existia: {produtor.nome} (CPF: {produtor.cpf_cnpj})')
            
            # 2. Criar propriedade Monpec1 (ou Monpec2, Monpec3, etc. se já existir para este produtor)
            if not propriedade:
                # Verificar se já existe propriedade com nome "Monpec" para este produtor
                propriedades_existentes = Propriedade.objects.filter(
                    produtor=produtor,
                    nome_propriedade__iregex=r'^Monpec\d+$'
                ).order_by('nome_propriedade')
                
                # Determinar o próximo número disponível para este produtor
                if propriedades_existentes.exists():
                    # Encontrar o maior número usado
                    import re
                    numeros_usados = []
                    for prop in propriedades_existentes:
                        match = re.search(r'Monpec(\d+)', prop.nome_propriedade, re.IGNORECASE)
                        if match:
                            numeros_usados.append(int(match.group(1)))
                    
                    if numeros_usados:
                        proximo_numero = max(numeros_usados) + 1
                    else:
                        proximo_numero = 2
                    
                    nome_propriedade = f'Monpec{proximo_numero}'
                    logger.info(f'Propriedade Monpec1 já existe para este produtor. Usando {nome_propriedade}')
                else:
                    nome_propriedade = 'Monpec1'
                
                propriedade, created = Propriedade.objects.get_or_create(
                    produtor=produtor,
                    nome_propriedade=nome_propriedade,
                    defaults={
                        'municipio': 'Campo Grande',
                        'uf': 'MS',
                        'area_total_ha': Decimal('5000.00'),
                        'tipo_operacao': 'PECUARIA',
                        'tipo_ciclo_pecuario': ['CICLO_COMPLETO'],
                        'tipo_propriedade': 'PROPRIA',
                        'valor_hectare_proprio': Decimal('12000.00'),
                    }
                )
                if created:
                    logger.info(f'Propriedade criada: {propriedade.nome_propriedade} (ID: {propriedade.id})')
                else:
                    logger.info(f'Propriedade já existia: {propriedade.nome_propriedade} (ID: {propriedade.id})')
            
            # 3. Criar categorias de animais
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
            
            # 4. Criar inventário de rebanho
            inventario_data = [
                {'categoria': 'Vacas em Lactação', 'quantidade': 850},
                {'categoria': 'Vacas Secas', 'quantidade': 150},
                {'categoria': 'Novilhas', 'quantidade': 320},
                {'categoria': 'Bezerras', 'quantidade': 280},
                {'categoria': 'Touros', 'quantidade': 25},
                {'categoria': 'Bezerros', 'quantidade': 310},
                {'categoria': 'Bois', 'quantidade': 450},
            ]
            
            # Limpar inventário existente
            InventarioRebanho.objects.filter(propriedade=propriedade).delete()
            
            for inv_data in inventario_data:
                InventarioRebanho.objects.create(
                    propriedade=propriedade,
                    categoria=categorias[inv_data['categoria']],
                    quantidade=inv_data['quantidade'],
                    data_inventario=date.today(),
                )
            
            logger.info(f'Inventário criado com {sum(d["quantidade"] for d in inventario_data)} animais')
            
            # 5. Criar dados operacionais
            try:
                from .models_operacional import (
                    TanqueCombustivel, AbastecimentoCombustivel,
                    EstoqueSuplementacao, CompraSuplementacao, DistribuicaoSuplementacao,
                    Equipamento, ManutencaoEquipamento
                )
                
                # Tanque de combustível
                tanque, _ = TanqueCombustivel.objects.get_or_create(
                    propriedade=propriedade,
                    nome='Tanque Principal',
                    defaults={
                        'capacidade_litros': Decimal('10000.00'),
                        'estoque_atual': Decimal('7500.00'),
                        'estoque_minimo': Decimal('2000.00'),
                        'localizacao': 'Sede da Fazenda',
                    }
                )
                
                # Abastecimentos (últimos 3 meses)
                for i in range(1, 4):
                    AbastecimentoCombustivel.objects.get_or_create(
                        propriedade=propriedade,
                        tanque=tanque,
                        data=date.today() - timedelta(days=i*30),
                        defaults={
                            'tipo': 'COMPRA',
                            'fornecedor': 'Posto Combustível Central',
                            'quantidade_litros': Decimal('5000.00'),
                            'preco_unitario': Decimal('5.80'),
                            'valor_total': Decimal('29000.00'),
                        }
                    )
                
                # Estoque de suplementação
                suplementos = [
                    {'nome': 'Sal Mineral', 'unidade': 'KG', 'quantidade': Decimal('5000.00')},
                    {'nome': 'Ração Concentrada', 'unidade': 'KG', 'quantidade': Decimal('10000.00')},
                    {'nome': 'Silagem de Milho', 'unidade': 'TONELADA', 'quantidade': Decimal('200.00')},
                ]
                
                for sup in suplementos:
                    EstoqueSuplementacao.objects.get_or_create(
                        propriedade=propriedade,
                        nome=sup['nome'],
                        defaults={
                            'unidade_medida': sup['unidade'],
                            'quantidade_atual': sup['quantidade'],
                            'estoque_minimo': sup['quantidade'] * Decimal('0.3'),
                        }
                    )
                
                # Equipamentos
                equipamentos_data = [
                    {'nome': 'Trator John Deere', 'tipo': 'TRATOR', 'marca': 'John Deere', 'modelo': '5075E'},
                    {'nome': 'Pulverizador', 'tipo': 'PULVERIZADOR', 'marca': 'Jacto', 'modelo': 'AM-12'},
                    {'nome': 'Plantadeira', 'tipo': 'PLANTADEIRA', 'marca': 'Máquinas Agrícolas', 'modelo': 'PL-8'},
                ]
                
                for eq_data in equipamentos_data:
                    Equipamento.objects.get_or_create(
                        propriedade=propriedade,
                        nome=eq_data['nome'],
                        defaults={
                            'tipo': eq_data['tipo'],
                            'marca': eq_data['marca'],
                            'modelo': eq_data['modelo'],
                            'ano_fabricacao': 2020,
                            'valor_aquisicao': Decimal('150000.00'),
                        }
                    )
                
                logger.info('Dados operacionais criados')
            except Exception as e:
                logger.warning(f'Erro ao criar dados operacionais: {e}')
            
            # 6. Criar dados de reprodução
            try:
                from .models_reproducao import Touro, EstacaoMonta, IATF, Nascimento
                from .models import AnimalIndividual
                
                # Touros
                for i in range(1, 6):
                    Touro.objects.get_or_create(
                        propriedade=propriedade,
                        nome=f'Touro {i}',
                        defaults={
                            'raca': 'NELORE',
                            'data_nascimento': date.today() - timedelta(days=random.randint(1095, 2555)),
                            'peso': Decimal(str(random.randint(600, 700))),
                            'status': 'ATIVO',
                        }
                    )
                
                # Estação de monta
                estacao, _ = EstacaoMonta.objects.get_or_create(
                    propriedade=propriedade,
                    nome='Estação de Monta 2025',
                    defaults={
                        'data_inicio': date(2025, 1, 15),
                        'data_fim': date(2025, 4, 15),
                        'tipo': 'IATF',
                    }
                )
                
                # IATFs (20 procedimentos)
                vacas = AnimalIndividual.objects.filter(propriedade=propriedade, sexo='FEMEA')[:20]
                for i, vaca in enumerate(vacas, 1):
                    IATF.objects.get_or_create(
                        propriedade=propriedade,
                        animal=vaca,
                        data_procedimento=date.today() - timedelta(days=random.randint(1, 90)),
                        defaults={
                            'veterinario': f'Dr. Veterinário {i % 3 + 1}',
                            'protocolo': 'PROTOCOLO_5_DIAS',
                            'status': 'CONCLUIDO',
                        }
                    )
                
                # Nascimentos (30 nascimentos)
                for i in range(1, 31):
                    mae = AnimalIndividual.objects.filter(propriedade=propriedade, sexo='FEMEA').first()
                    if mae:
                        Nascimento.objects.get_or_create(
                            propriedade=propriedade,
                            mae=mae,
                            data_nascimento=date.today() - timedelta(days=random.randint(1, 180)),
                            defaults={
                                'sexo': random.choice(['MACHO', 'FEMEA']),
                                'peso_nascimento': Decimal(str(random.randint(30, 45))),
                                'tipo_parto': random.choice(['NORMAL', 'CESAREA']),
                            }
                        )
                
                logger.info('Dados de reprodução criados')
            except Exception as e:
                logger.warning(f'Erro ao criar dados de reprodução: {e}')
            
            # 7. Criar funcionários
            try:
                from .models_funcionarios import Funcionario, FolhaPagamento
                
                funcionarios_data = [
                    {'nome': 'João Silva', 'cargo': 'Gerente de Fazenda', 'salario': Decimal('8000.00')},
                    {'nome': 'Maria Santos', 'cargo': 'Veterinária', 'salario': Decimal('12000.00')},
                    {'nome': 'Pedro Oliveira', 'cargo': 'Capataz', 'salario': Decimal('5000.00')},
                    {'nome': 'Ana Costa', 'cargo': 'Ordenhadeira', 'salario': Decimal('2500.00')},
                    {'nome': 'Carlos Souza', 'cargo': 'Peão', 'salario': Decimal('2000.00')},
                ]
                
                for func_data in funcionarios_data:
                    funcionario, _ = Funcionario.objects.get_or_create(
                        propriedade=propriedade,
                        nome=func_data['nome'],
                        defaults={
                            'cargo': func_data['cargo'],
                            'salario_base': func_data['salario'],
                            'data_admissao': date.today() - timedelta(days=random.randint(365, 1825)),
                            'status': 'ATIVO',
                        }
                    )
                    
                    # Criar folha de pagamento do mês atual
                    FolhaPagamento.objects.get_or_create(
                        propriedade=propriedade,
                        funcionario=funcionario,
                        mes=date.today().month,
                        ano=date.today().year,
                        defaults={
                            'salario_bruto': funcionario.salario_base,
                            'status': 'PAGO',
                        }
                    )
                
                logger.info('Funcionários criados')
            except Exception as e:
                logger.warning(f'Erro ao criar funcionários: {e}')
            
            # 8. Criar fornecedores e contas
            try:
                from .models_compras_financeiro import Fornecedor, ContaPagar, ContaReceber
                
                fornecedores_data = [
                    {'nome': 'Agropecuária Central', 'tipo': 'REVENDA'},
                    {'nome': 'Cooperativa Rural MS', 'tipo': 'COOPERATIVA'},
                    {'nome': 'Frigorífico Sul', 'tipo': 'FRIGORIFICO'},
                    {'nome': 'Farmácia Veterinária', 'tipo': 'FARMACIA'},
                ]
                
                fornecedores = []
                for forn_data in fornecedores_data:
                    fornecedor, _ = Fornecedor.objects.get_or_create(
                        propriedade=propriedade,
                        nome=forn_data['nome'],
                        defaults={
                            'tipo': forn_data['tipo'],
                            'cnpj': f'{random.randint(10000000, 99999999)}/0001-{random.randint(10, 99)}',
                            'telefone': f'(67) {random.randint(3000, 9999)}-{random.randint(1000, 9999)}',
                        }
                    )
                    fornecedores.append(fornecedor)
                
                # Contas a pagar (24 contas)
                for i in range(1, 25):
                    ContaPagar.objects.get_or_create(
                        propriedade=propriedade,
                        fornecedor=random.choice(fornecedores) if fornecedores else None,
                        descricao=f'Conta {i}',
                        data_vencimento=date.today() + timedelta(days=random.randint(1, 60)),
                        defaults={
                            'valor': Decimal(str(random.randint(500, 5000))),
                            'status': 'PENDENTE' if random.random() > 0.3 else 'PAGO',
                        }
                    )
                
                # Contas a receber (14 contas)
                for i in range(1, 15):
                    ContaReceber.objects.get_or_create(
                        propriedade=propriedade,
                        cliente=f'Cliente {i}',
                        descricao=f'Venda de Gado {i}',
                        data_vencimento=date.today() + timedelta(days=random.randint(1, 90)),
                        defaults={
                            'valor': Decimal(str(random.randint(5000, 50000))),
                            'status': 'PENDENTE' if random.random() > 0.4 else 'RECEBIDO',
                        }
                    )
                
                logger.info('Fornecedores e contas criados')
            except Exception as e:
                logger.warning(f'Erro ao criar fornecedores e contas: {e}')
            
            # 9. Criar pastagens
            try:
                from .models_controles_operacionais import Pastagem, RotacaoPastagem
                
                pastagens_data = [
                    {'nome': 'Pastagem 1 - Brachiaria', 'area_ha': Decimal('500.00'), 'tipo': 'BRAQUIARIA'},
                    {'nome': 'Pastagem 2 - Panicum', 'area_ha': Decimal('400.00'), 'tipo': 'PANICUM'},
                    {'nome': 'Pastagem 3 - Tifton', 'area_ha': Decimal('300.00'), 'tipo': 'TIFTON'},
                ]
                
                for past_data in pastagens_data:
                    pastagem, _ = Pastagem.objects.get_or_create(
                        propriedade=propriedade,
                        nome=past_data['nome'],
                        defaults={
                            'area_hectares': past_data['area_ha'],
                            'tipo_pastagem': past_data['tipo'],
                            'data_plantio': date.today() - timedelta(days=random.randint(365, 1095)),
                        }
                    )
                
                logger.info('Pastagens criadas')
            except Exception as e:
                logger.warning(f'Erro ao criar pastagens: {e}')
            
            # 10. Criar bens patrimoniais
            try:
                from .models_patrimonio import TipoBem, BemPatrimonial
                
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
                    BemPatrimonial.objects.get_or_create(
                        propriedade=propriedade,
                        tipo=tipos_bem[bem_data['tipo']],
                        nome=bem_data['nome'],
                        defaults={
                            'valor_aquisicao': bem_data['valor'],
                            'data_aquisicao': date.today() - timedelta(days=random.randint(365, 1825)),
                        }
                    )
                
                logger.info('Bens patrimoniais criados')
            except Exception as e:
                logger.warning(f'Erro ao criar bens patrimoniais: {e}')
            
            # 11. Criar fluxo de caixa
            try:
                from .models import FluxoCaixa
                
                hoje = date.today()
                for i in range(1, 13):  # 12 meses
                    mes = hoje.month - (12 - i) if i <= hoje.month else hoje.month + (i - hoje.month)
                    ano = hoje.year if i <= hoje.month else hoje.year - 1
                    
                    FluxoCaixa.objects.get_or_create(
                        propriedade=propriedade,
                        data=date(ano, mes, 15),
                        descricao=f'Venda de Gado - Mês {i}',
                        defaults={
                            'tipo': 'RECEITA',
                            'valor': Decimal(str(random.randint(50000, 150000))),
                        }
                    )
                    
                    FluxoCaixa.objects.get_or_create(
                        propriedade=propriedade,
                        data=date(ano, mes, 20),
                        descricao=f'Despesas Operacionais - Mês {i}',
                        defaults={
                            'tipo': 'DESPESA',
                            'valor': Decimal(str(random.randint(30000, 80000))),
                        }
                    )
                
                logger.info('Fluxo de caixa criado')
            except Exception as e:
                logger.warning(f'Erro ao criar fluxo de caixa: {e}')
            
            # 12. Criar animais individuais (amostra)
            try:
                from .models import AnimalIndividual, BrincoAnimal
                
                vacas_lactacao = categorias.get('Vacas em Lactação')
                if vacas_lactacao:
                    for i in range(1, 51):  # 50 animais de exemplo
                        brinco_num = f'MONPEC1-{str(i).zfill(4)}'
                        brinco, _ = BrincoAnimal.objects.get_or_create(
                            numero=brinco_num,
                            defaults={'tipo': 'ELETRONICO'}
                        )
                        
                        AnimalIndividual.objects.get_or_create(
                            propriedade=propriedade,
                            categoria=vacas_lactacao,
                            brinco=brinco_num,
                            defaults={
                                'nome': f'Vaca {i}',
                                'data_nascimento': date.today() - timedelta(days=random.randint(730, 2555)),
                                'sexo': 'FEMEA',
                                'peso_atual': Decimal(str(random.randint(400, 500))),
                                'status': 'ATIVO',
                            }
                        )
                    
                    logger.info('50 animais individuais criados')
            except Exception as e:
                logger.warning(f'Erro ao criar animais individuais: {e}')
            
            # 13. Criar dados financeiros adicionais
            try:
                from .models_financeiro import LancamentoFinanceiro, CategoriaFinanceira, ContaFinanceira
                
                # Criar categorias financeiras
                categorias_fin = [
                    {'nome': 'Receitas de Vendas', 'tipo': 'RECEITA'},
                    {'nome': 'Despesas Operacionais', 'tipo': 'DESPESA'},
                    {'nome': 'Despesas com Pessoal', 'tipo': 'DESPESA'},
                    {'nome': 'Despesas com Combustível', 'tipo': 'DESPESA'},
                ]
                
                cats_fin = {}
                for cat_fin_data in categorias_fin:
                    cat_fin, _ = CategoriaFinanceira.objects.get_or_create(
                        propriedade=propriedade,
                        nome=cat_fin_data['nome'],
                        defaults={'tipo': cat_fin_data['tipo']}
                    )
                    cats_fin[cat_fin_data['nome']] = cat_fin
                
                # Criar conta financeira
                conta, _ = ContaFinanceira.objects.get_or_create(
                    propriedade=propriedade,
                    nome='Conta Corrente Principal',
                    defaults={
                        'tipo': 'CONTA_CORRENTE',
                        'banco': 'Banco do Brasil',
                        'agencia': '1234',
                        'conta': '56789-0',
                        'saldo_inicial': Decimal('50000.00'),
                    }
                )
                
                # Criar lançamentos financeiros (últimos 6 meses)
                for i in range(1, 7):
                    mes = date.today().month - (6 - i) if i <= date.today().month else date.today().month + (i - date.today().month)
                    ano = date.today().year if i <= date.today().month else date.today().year - 1
                    
                    # Receita
                    LancamentoFinanceiro.objects.get_or_create(
                        propriedade=propriedade,
                        conta=conta,
                        categoria=cats_fin.get('Receitas de Vendas'),
                        data=date(ano, mes, 10),
                        descricao=f'Venda de Gado - {mes}/{ano}',
                        defaults={
                            'tipo': 'RECEITA',
                            'valor': Decimal(str(random.randint(80000, 150000))),
                            'status': 'CONCLUIDO',
                        }
                    )
                    
                    # Despesa operacional
                    LancamentoFinanceiro.objects.get_or_create(
                        propriedade=propriedade,
                        conta=conta,
                        categoria=cats_fin.get('Despesas Operacionais'),
                        data=date(ano, mes, 15),
                        descricao=f'Despesas Operacionais - {mes}/{ano}',
                        defaults={
                            'tipo': 'DESPESA',
                            'valor': Decimal(str(random.randint(40000, 70000))),
                            'status': 'CONCLUIDO',
                        }
                    )
                
                logger.info('Dados financeiros criados')
            except Exception as e:
                logger.warning(f'Erro ao criar dados financeiros: {e}')
            
            # 14. Criar projeto bancário (exemplo)
            try:
                from .models import ProjetoBancario
                
                ProjetoBancario.objects.get_or_create(
                    propriedade=propriedade,
                    nome='Projeto de Expansão 2025',
                    defaults={
                        'banco': 'Banco do Brasil',
                        'valor_financiamento': Decimal('2000000.00'),
                        'taxa_juros_anual': Decimal('12.5'),
                        'prazo_meses': 120,
                        'data_inicio': date.today(),
                        'status': 'APROVADO',
                    }
                )
                
                logger.info('Projeto bancário criado')
            except Exception as e:
                logger.warning(f'Erro ao criar projeto bancário: {e}')
            
            # 15. Criar custos fixos e variáveis
            try:
                from .models import CustoFixo, CustoVariavel
                
                # Custos fixos
                custos_fixos = [
                    {'descricao': 'Aluguel de Pastagem', 'valor_mensal': Decimal('15000.00')},
                    {'descricao': 'Salários Fixos', 'valor_mensal': Decimal('25000.00')},
                    {'descricao': 'Manutenção de Equipamentos', 'valor_mensal': Decimal('5000.00')},
                ]
                
                for cf_data in custos_fixos:
                    CustoFixo.objects.get_or_create(
                        propriedade=propriedade,
                        descricao=cf_data['descricao'],
                        defaults={'valor_mensal': cf_data['valor_mensal']}
                    )
                
                # Custos variáveis
                custos_variaveis = [
                    {'descricao': 'Ração por Animal', 'valor_unitario': Decimal('150.00')},
                    {'descricao': 'Medicamentos', 'valor_unitario': Decimal('50.00')},
                    {'descricao': 'Combustível', 'valor_unitario': Decimal('5.80')},
                ]
                
                for cv_data in custos_variaveis:
                    CustoVariavel.objects.get_or_create(
                        propriedade=propriedade,
                        descricao=cv_data['descricao'],
                        defaults={'valor_unitario': cv_data['valor_unitario']}
                    )
                
                logger.info('Custos fixos e variáveis criados')
            except Exception as e:
                logger.warning(f'Erro ao criar custos: {e}')
            
            # Garantir que propriedade foi criada corretamente
            if not propriedade:
                logger.error('Erro: Propriedade não foi criada após todo o processo')
                messages.error(request, 'Erro ao criar propriedade. Por favor, tente novamente.')
                return redirect('dashboard')
            
            # Popular com dados completos usando o comando popular_monpec1_demo
            # Isso garante que todos os usuários demo tenham os mesmos dados completos do demo_monpec
            # IMPORTANTE: Executar FORA do transaction.atomic para garantir que o commit aconteça
            logger.info(f'Executando popular_monpec1_demo para popular dados completos (mesmo template do demo_monpec)...')
        
        # Executar o comando FORA do transaction.atomic para evitar problemas de transação aninhada
        try:
            from django.core.management import call_command
            import sys
            import io
            
            # Configurar encoding UTF-8 para stdout/stderr para evitar erros com emojis no Windows
            if sys.platform == 'win32':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
            
            # Usar force=True para garantir que os dados sejam populados mesmo se já existirem alguns dados parciais
            call_command('popular_monpec1_demo', propriedade_id=propriedade.id, force=True, verbosity=2)
            logger.info(f'Dados completos populados com sucesso!')
            messages.success(request, 'Demonstração configurada com sucesso! Todos os módulos foram populados com dados realistas. Você será redirecionado...')
        except Exception as e:
            logger.error(f'ERRO ao executar popular_monpec1_demo: {e}', exc_info=True)
            # Ainda mostrar mensagem de sucesso pois os dados básicos foram criados
            # Remover emojis da mensagem de erro para evitar problemas de encoding
            error_msg = str(e).encode('ascii', errors='ignore').decode('ascii')
            messages.warning(request, f'Demonstração configurada, mas houve um problema ao popular todos os dados: {error_msg}. Tente acessar novamente.')
        
        # Redirecionar para a propriedade
        logger.info(f'REDIRECIONANDO PARA PROPRIEDADE {propriedade.id} - {propriedade.nome_propriedade}')
        return redirect('propriedade_modulos', propriedade_id=propriedade.id)
            
    except Exception as e:
        logger.error(f'Erro ao configurar demonstração: {e}', exc_info=True)
        messages.error(request, f'Erro ao configurar demonstração: {str(e)}')
        # Tentar redirecionar para o dashboard em caso de erro
        return redirect('dashboard')
    
    # Se chegou aqui sem criar propriedade, redirecionar para o dashboard
    logger.warning(f'Demo setup concluído sem criar propriedade. Redirecionando para dashboard.')
    return redirect('dashboard')

