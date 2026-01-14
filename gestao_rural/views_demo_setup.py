# -*- coding: utf-8 -*-
"""
View para configurar automaticamente o ambiente de demonstração
Cria produtor, propriedade e dados realistas automaticamente
"""

from django.shortcuts import render, redirect
from django.urls import reverse
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
    Cria produtor, propriedade Fazenda Demonstração e dados realistas.
    """
    logger.info(f'DEMO_SETUP CHAMADO - user: {request.user.username}')
    
    # Verificar se é usuário de demonstração
    # IMPORTANTE: Superusuários e staff nunca são demo
    is_demo_user = False
    
    if request.user.is_superuser or request.user.is_staff:
        is_demo_user = False
    # Verificar se é usuário demo padrão
    elif request.user.username in ['demo', 'demo_monpec']:
        is_demo_user = True
        logger.info(f'Usuário demo padrão detectado: {request.user.username}')
    else:
        # Verificar se é usuário de demonstração (do popup ou criado via formulário)
        try:
            UsuarioAtivo.objects.get(usuario=request.user)
            is_demo_user = True
            logger.info(f'Usuário demo (UsuarioAtivo) detectado: {request.user.username}')
        except:
            # Verificar se é usuário criado via formulário de demonstração
            # Usuários demo têm registro na tabela UsuarioAtivo com o email
            try:
                UsuarioAtivo.objects.get(email=request.user.email)
                is_demo_user = True
                logger.info(f'Usuário demo (formulário) detectado via email: {request.user.username} ({request.user.email})')
            except:
                logger.info(f'Usuário {request.user.username} não é demo (sem UsuarioAtivo)')
                pass
    
    if not is_demo_user:
        logger.warning(f'Usuário não demo tentou acessar demo_setup: {request.user.username}')
        messages.error(request, 'Esta página é apenas para usuários de demonstração.')
        return redirect('dashboard')
    
    # PARA USUÁRIOS DEMO: Sempre usar a propriedade compartilhada "Fazenda Demonstracao"
    # Primeiro verificar se a propriedade demo compartilhada já existe
    logger.info(f'[DEMO_SETUP] Verificando propriedade demo compartilhada para usuário: {request.user.username}')
    logger.info(f'[DEMO_SETUP] Usuário identificado como demo: {is_demo_user}')

    propriedade = Propriedade.objects.filter(
        nome_propriedade='Fazenda Demonstracao'
    ).first()

    logger.info(f'[DEMO_SETUP] Propriedade "Fazenda Demonstracao" encontrada: {propriedade is not None}')

    if propriedade:
        # Propriedade demo compartilhada já existe, redirecionar diretamente
        logger.info(f'[DEMO_SETUP] Usando propriedade demo compartilhada {propriedade.id} ({propriedade.nome_propriedade})')
        logger.info(f'[DEMO_SETUP] Propriedade pertence ao produtor: {propriedade.produtor.nome if propriedade.produtor else "SEM PRODUTOR"}')
        messages.success(request, 'Demonstração configurada! Redirecionando...')
        # Forçar redirecionamento para versão demo
        propriedade_url = reverse('propriedade_modulos', kwargs={'propriedade_id': propriedade.id})
        demo_url = f"{propriedade_url}?demo=true"
        logger.info(f'[DEMO_SETUP] Redirecionando para versão demo: {demo_url}')
        return redirect(demo_url)

    # Se chegou aqui, precisa criar tudo automaticamente
    logger.info(f'[DEMO_SETUP] Propriedade compartilhada não encontrada, chamando _criar_dados_demo_completos...')
    # Primeiro verificar se deve mostrar a página de configuração ou criar os dados
    if not request.GET.get('create', False):
        # Mostrar a página de configuração primeiro
        logger.info(f'Mostrando página de configuração da demonstração para {request.user.username}')
        return render(request, 'gestao_rural/demo_setup.html')

    # Criar os dados automaticamente usando a função compartilhada
    logger.info(f'Iniciando criação automática de dados para demonstração...')
    try:
        propriedade = _criar_dados_demo_completos(request.user)

        # Verificar se a propriedade foi criada corretamente
        if not propriedade:
            logger.error('Erro: Propriedade não foi criada após chamar _criar_dados_demo_completos')
            messages.error(request, 'Erro ao criar propriedade. Por favor, tente novamente.')
            return redirect('dashboard')

        # Redirecionar diretamente para a propriedade demo
        logger.info(f'REDIRECIONANDO PARA PROPRIEDADE DEMO {propriedade.id} - {propriedade.nome_propriedade}')
        messages.success(request, 'Demonstração configurada com sucesso!')
        # Forçar redirecionamento para versão demo
        propriedade_url = reverse('propriedade_modulos', kwargs={'propriedade_id': propriedade.id})
        demo_url = f"{propriedade_url}?demo=true"
        logger.info(f'[DEMO_SETUP] Redirecionando para versão demo: {demo_url}')
        return redirect(demo_url)
            
    except Exception as e:
        logger.error(f'Erro ao configurar demonstração: {e}', exc_info=True)
        messages.error(request, f'Erro ao configurar demonstração: {str(e)}')
        # Tentar redirecionar para o dashboard em caso de erro
        return redirect('dashboard')
    
    # Se chegou aqui sem criar propriedade, redirecionar para o dashboard
    logger.warning(f'Demo setup concluído sem criar propriedade. Redirecionando para dashboard.')
    return redirect('dashboard')


def _criar_dados_demo_completos(user, nome_completo, email, telefone):
    """
    Cria produtor, propriedade e dados de demonstração para um usuário.
    Retorna a propriedade criada.
    Esta função é chamada automaticamente quando um usuário se cadastra via formulário de demonstração.
    """
    from .models import ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho
    from decimal import Decimal
    from datetime import date
    from django.db import transaction
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f'[_criar_dados_demo] Iniciando para usuário: {user.username}')
    
    try:
        logger.info(f'[_criar_dados_demo] Iniciando transação para criar dados demo para: {user.username}')

        with transaction.atomic():
            # 1. Verificar se já existe propriedade demo compartilhada
            propriedade = Propriedade.objects.filter(
                nome_propriedade='Fazenda Demonstracao'
            ).first()

            logger.info(f'[_criar_dados_demo] Verificação inicial - Propriedade "Fazenda Demonstracao" existe: {propriedade is not None}')

            if propriedade:
                logger.info(f'[_criar_dados_demo] Propriedade demo compartilhada já existe: {propriedade.id}')
                logger.info(f'[_criar_dados_demo] Propriedade pertence ao produtor: {propriedade.produtor.nome if propriedade.produtor else "SEM PRODUTOR"}')
                return propriedade

            # 2. Criar produtor demo compartilhado
            cpf_demo = 'DEMO-COMPARTILHADO'
            produtor, created = ProdutorRural.objects.get_or_create(
                cpf_cnpj=cpf_demo,
                defaults={
                    'nome': 'Fazenda Demonstracao Ltda',
                    'email': 'demo@monpec.com.br',
                    'telefone': '(67) 99999-9999',
                    'endereco': 'Rodovia BR-060, Km 45',
                    'anos_experiencia': 15
                }
            )
            logger.info(f'[_criar_dados_demo] Produtor compartilhado: {produtor.nome} (ID: {produtor.id})')

            # 3. Criar propriedade Fazenda Demonstração compartilhada
            logger.info(f'[_criar_dados_demo] Criando propriedade "Fazenda Demonstracao" para produtor: {produtor.nome}')

            propriedade, created = Propriedade.objects.get_or_create(
                nome_propriedade='Fazenda Demonstracao',
                defaults={
                    'produtor': produtor,
                    'municipio': 'Campo Grande',
                    'uf': 'MS',
                    'area_total_ha': Decimal('1500.00'),
                    'latitude': Decimal('-20.4697'),
                    'longitude': Decimal('-54.6201'),
                    'tipo_operacao': 'PECUARIA',
                    'tipo_ciclo_pecuario': ['CICLO_COMPLETO'],
                    'tipo_propriedade': 'PROPRIA',
                    'valor_hectare_proprio': Decimal('12000.00'),
                }
            )

            logger.info(f'[_criar_dados_demo] Propriedade criada: {propriedade.nome_propriedade} (ID: {propriedade.id}, Criada: {created})')
            logger.info(f'[_criar_dados_demo] Propriedade: {propriedade.nome_propriedade} (ID: {propriedade.id})')
            
            # 3. Criar categorias de animais (se não existirem)
            # IMPORTANTE: Tentar carregar categorias padrão primeiro via fixture
            try:
                from django.core.management import call_command
                call_command('loaddata', 'categorias_animais.json', verbosity=0, ignore=True)
                logger.info('[_criar_dados_demo] Categorias padrão carregadas via fixture')
            except Exception as e:
                logger.warning(f'[_criar_dados_demo] Não foi possível carregar fixture de categorias: {e}')
            
            categorias_data = [
                {'nome': 'Vaca em Lactacao', 'sexo': 'F', 'idade_minima_meses': 36, 'peso_medio_kg': Decimal('450.00')},
                {'nome': 'Vaca Seca', 'sexo': 'F', 'idade_minima_meses': 36, 'peso_medio_kg': Decimal('480.00')},
                {'nome': 'Novilha', 'sexo': 'F', 'idade_minima_meses': 18, 'peso_medio_kg': Decimal('320.00')},
                {'nome': 'Bezerra', 'sexo': 'F', 'idade_minima_meses': 0, 'peso_medio_kg': Decimal('150.00')},
                {'nome': 'Touro Reprodutor', 'sexo': 'M', 'idade_minima_meses': 24, 'peso_medio_kg': Decimal('650.00')},
                {'nome': 'Bezerro', 'sexo': 'M', 'idade_minima_meses': 0, 'peso_medio_kg': Decimal('160.00')},
            ]
            
            categorias = {}
            for cat_data in categorias_data:
                categoria, _ = CategoriaAnimal.objects.get_or_create(
                    nome=cat_data['nome'],
                    defaults={
                        'sexo': cat_data['sexo'],
                        'idade_minima_meses': cat_data['idade_minima_meses'],
                        'peso_medio_kg': cat_data['peso_medio_kg'],
                    }
                )
                categorias[cat_data['nome']] = categoria
                logger.info(f'[_criar_dados_demo] Categoria garantida: {cat_data["nome"]} (ID: {categoria.id})')

            # 4. Criar inventário de rebanho
            inventario_data = [
                {'categoria': 'Vaca em Lactacao', 'quantidade': 10},
                {'categoria': 'Vaca Seca', 'quantidade': 8},
                {'categoria': 'Novilha', 'quantidade': 12},
                {'categoria': 'Bezerra', 'quantidade': 8},
                {'categoria': 'Touro Reprodutor', 'quantidade': 3},
                {'categoria': 'Bezerro', 'quantidade': 6},
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
            
            logger.info(f'[_criar_dados_demo] Inventário criado com {sum(d["quantidade"] for d in inventario_data)} animais')

            # 5. Popular automaticamente dados completos da Fazenda Demonstração
            try:
                logger.info('[_criar_dados_demo] Populando dados completos da Fazenda Demonstracao...')

                # Chamar scripts de populacao automatica (mesmo padrão da Monpec1)
                import subprocess
                import os
                import sys

                scripts_dir = os.path.dirname(__file__)
                scripts_dir = os.path.dirname(scripts_dir)  # Voltar para raiz do projeto

                # Executar scripts de populacao na mesma ordem da Monpec1
                scripts = [
                    'python popular_funcionarios.py',
                    'python popular_pastagens.py',
                    'python popular_equipamentos.py',
                    'python popular_fornecedores.py'
                ]

                for script in scripts:
                    try:
                        result = subprocess.run(
                            script,
                            shell=True,
                            cwd=scripts_dir,
                            capture_output=True,
                            text=True,
                            timeout=60
                        )
                        if result.returncode == 0:
                            logger.info(f'[_criar_dados_demo] Script executado com sucesso: {script}')
                        else:
                            logger.warning(f'[_criar_dados_demo] Script falhou: {script} - {result.stderr}')
                    except Exception as e:
                        logger.warning(f'[_criar_dados_demo] Erro ao executar {script}: {e}')

                # Configurações adicionais iguais à Monpec1
                try:
                    logger.info('[_criar_dados_demo] Aplicando configurações especiais da demo...')

                    # Importar modelos necessários
                    from gestao_rural.models_patrimonio import TipoBem, BemPatrimonial
                    from decimal import Decimal
                    import random
                    from datetime import date, timedelta

                    # 1. Criar bens patrimoniais (igual à Monpec1)
                    logger.info('[_criar_dados_demo] Criando tipos de bem...')
                    tipos = [
                        {'nome': 'Máquinas e Equipamentos', 'categoria': 'MAQUINA', 'taxa_depreciacao': Decimal('10.00')},
                        {'nome': 'Veículos', 'categoria': 'VEICULO', 'taxa_depreciacao': Decimal('20.00')},
                        {'nome': 'Instalações e Construções', 'categoria': 'INSTALACAO', 'taxa_depreciacao': Decimal('5.00')},
                    ]

                    tipos_bem = {}
                    for tipo_data in tipos:
                        tipo, created = TipoBem.objects.get_or_create(
                            nome=tipo_data['nome'],
                            defaults={
                                'categoria': tipo_data['categoria'],
                                'taxa_depreciacao': tipo_data['taxa_depreciacao']
                            }
                        )
                        tipos_bem[tipo_data['nome']] = tipo
                        logger.info(f'[_criar_dados_demo] TipoBem {tipo_data["nome"]}: {"criado" if created else "já existia"}')

                    logger.info('[_criar_dados_demo] Criando bens patrimoniais...')
                    bens = [
                        {'nome': 'Trator John Deere', 'tipo': 'Máquinas e Equipamentos', 'valor': Decimal('350000.00')},
                        {'nome': 'Caminhão Ford', 'tipo': 'Veículos', 'valor': Decimal('180000.00')},
                        {'nome': 'Curral de Manejo', 'tipo': 'Instalações e Construções', 'valor': Decimal('150000.00')},
                    ]

                    for bem_data in bens:
                        bem, created = BemPatrimonial.objects.get_or_create(
                            propriedade=propriedade,
                            descricao=bem_data['nome'],
                            defaults={
                                'tipo_bem': tipos_bem[bem_data['tipo']],
                                'valor_aquisicao': bem_data['valor'],
                                'data_aquisicao': date.today() - timedelta(days=random.randint(365, 1825)),
                            }
                        )
                        logger.info(f'[_criar_dados_demo] Bem {bem_data["nome"]}: {"criado" if created else "já existia"}')

                    # 2. Bens patrimoniais criados com sucesso (essa é a configuração principal da demo)

                    logger.info('[_criar_dados_demo] Configurações especiais aplicadas com sucesso')

                except Exception as e:
                    logger.warning(f'[_criar_dados_demo] Erro ao aplicar configurações especiais: {e}')

                logger.info('[_criar_dados_demo] Dados da Fazenda Demonstracao populados automaticamente')

            except Exception as e:
                logger.warning(f'[_criar_dados_demo] Erro ao popular dados automaticos (nao critico): {e}')

            return propriedade
            
    except Exception as e:
        logger.error(f'[_criar_dados_demo] Erro ao criar dados: {e}', exc_info=True)
        raise

