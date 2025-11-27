# -*- coding: utf-8 -*-
"""
Serviço para gerar vendas projetadas a partir das movimentações projetadas
"""

import logging
from decimal import Decimal
from datetime import timedelta
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from ..models import (
    Propriedade,
    PlanejamentoAnual,
    CenarioPlanejamento,
    MovimentacaoProjetada,
    CategoriaAnimal,
    VendaProjetada,
    InventarioRebanho
)
# Importar Cliente apenas quando necessário para evitar conflitos

logger = logging.getLogger(__name__)


def gerar_vendas_do_cenario(propriedade, cenario, cliente_padrao=None):
    """
    Gera vendas projetadas a partir das movimentações projetadas do tipo VENDA do cenário
    
    Args:
        propriedade: Propriedade
        cenario: CenarioPlanejamento
        cliente_padrao: Cliente (opcional) - cliente padrão para vendas sem cliente definido
    
    Returns:
        List[VendaProjetada]: Lista de vendas criadas
    """
    vendas_criadas = []
    
    if not cenario:
        return vendas_criadas
    
    planejamento = cenario.planejamento
    ano_planejamento = planejamento.ano if planejamento else None
    
    # IDs de movimentações que já têm vendas geradas para este cenário
    ids_com_venda_este_cenario = list(VendaProjetada.objects.filter(
        cenario=cenario,
        movimentacao_projetada__isnull=False
    ).values_list('movimentacao_projetada_id', flat=True))
    
    # Buscar movimentações de VENDA vinculadas ao planejamento
    # IMPORTANTE: A referência principal é o PLANEJAMENTO, não a propriedade isolada
    # As movimentações devem estar vinculadas ao planejamento quando a projeção é gerada
    movimentacoes_venda = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        tipo_movimentacao='VENDA',
        quantidade__gt=0
    )
    
    # PRIORIDADE 1: Buscar TODAS as movimentações vinculadas ao planejamento
    # IMPORTANTE: Uma projeção pode ter vários anos (ex: 2022-2026), então buscamos
    # TODAS as movimentações do planejamento, independente do ano
    if planejamento:
        # Primeiro, buscar movimentações diretamente vinculadas ao planejamento
        movimentacoes_venda_planejamento = movimentacoes_venda.filter(planejamento=planejamento)
        total_vinculadas = movimentacoes_venda_planejamento.count()
        
        logger.info(f"Buscando movimentações VENDA do planejamento {planejamento.codigo}")
        logger.info(f"Total de movimentações VENDA vinculadas ao planejamento: {total_vinculadas}")
        
        # Se não encontrou movimentações vinculadas, tentar vincular movimentações sem planejamento do mesmo período
        if total_vinculadas == 0:
            logger.warning(f"Nenhuma movimentação VENDA encontrada vinculada ao planejamento {planejamento.codigo}")
            logger.info("Tentando buscar movimentações sem planejamento do mesmo período...")
            
            # Buscar movimentações sem planejamento que possam pertencer a este planejamento
            # Baseado no ano do planejamento e anos próximos (projeção multi-ano)
            anos_busca = [planejamento.ano + i for i in range(-2, 6)]  # Buscar 2 anos antes até 5 anos depois
            movimentacoes_sem_planejamento = MovimentacaoProjetada.objects.filter(
                propriedade=propriedade,
                tipo_movimentacao='VENDA',
                quantidade__gt=0,
                planejamento__isnull=True,
                data_movimentacao__year__in=anos_busca
            )
            total_sem_planejamento = movimentacoes_sem_planejamento.count()
            
            if total_sem_planejamento > 0:
                logger.info(f"Encontradas {total_sem_planejamento} movimentações VENDA sem planejamento no período {anos_busca}")
                # Vincular essas movimentações ao planejamento
                movimentacoes_sem_planejamento.update(planejamento=planejamento)
                logger.info(f"Movimentações vinculadas ao planejamento {planejamento.codigo}")
                # Buscar novamente após vincular
                movimentacoes_venda = MovimentacaoProjetada.objects.filter(
                    propriedade=propriedade,
                    tipo_movimentacao='VENDA',
                    quantidade__gt=0,
                    planejamento=planejamento
                )
            else:
                logger.warning(f"Nenhuma movimentação VENDA encontrada no período {anos_busca}")
                movimentacoes_venda = MovimentacaoProjetada.objects.none()
        else:
            movimentacoes_venda = movimentacoes_venda_planejamento
            # Log de informações sobre o range de anos encontrado
            anos_encontrados = movimentacoes_venda.values_list('data_movimentacao__year', flat=True).distinct()
            logger.info(f"Anos encontrados nas movimentações: {sorted(anos_encontrados)}")
    else:
        # Se não há planejamento, não podemos gerar vendas (projeção deve estar vinculada)
        logger.warning("Não há planejamento vinculado ao cenário. Não é possível gerar vendas.")
        return vendas_criadas
    
    # Excluir movimentações que já têm venda gerada para este cenário
    if ids_com_venda_este_cenario:
        movimentacoes_venda = movimentacoes_venda.exclude(id__in=ids_com_venda_este_cenario)
    
    # IMPORTANTE: Não filtrar por cenário nas movimentações
    # As movimentações são geradas para o planejamento e podem ser compartilhadas entre cenários
    # Apenas evitamos criar vendas duplicadas para o mesmo cenário
    
    logger.info(f"Total de movimentações VENDA encontradas do planejamento: {movimentacoes_venda.count()}")
    logger.info(f"IDs de movimentações já com vendas para este cenário: {ids_com_venda_este_cenario}")
    
    # Não aplicar filtro de cenário - usar todas as movimentações do planejamento
    # O filtro já foi aplicado pelo planejamento acima
    
    movimentacoes_venda = movimentacoes_venda.order_by('data_movimentacao')
    
    if not movimentacoes_venda.exists():
        # Log para debug - nenhuma movimentação encontrada
        total_vendas_propriedade = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade, 
            tipo_movimentacao='VENDA', 
            quantidade__gt=0
        ).count()
        total_vendas_planejamento = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            planejamento=planejamento,
            tipo_movimentacao='VENDA',
            quantidade__gt=0
        ).count() if planejamento else 0
        logger.warning(
            f'Nenhuma movimentação de VENDA encontrada para: propriedade={propriedade.id}, '
            f'planejamento={planejamento.codigo if planejamento else None}, cenario={cenario.nome if cenario else None}, '
            f'ano={ano_planejamento}. '
            f'Total VENDA na propriedade: {total_vendas_propriedade}, '
            f'Total VENDA no planejamento: {total_vendas_planejamento}'
        )
        return vendas_criadas
    
    # Buscar cliente padrão se não foi fornecido
    if not cliente_padrao:
        try:
            from ..models_cadastros import Cliente
            # Verificar se a tabela existe antes de fazer a query
            from django.db import connection
            table_name = Cliente._meta.db_table
            if table_name in connection.introspection.table_names():
                cliente_padrao = Cliente.objects.filter(
                    propriedade=propriedade,
                    ativo=True,
                    tipo_cliente='FRIGORIFICO'
                ).first()
                if not cliente_padrao:
                    cliente_padrao = Cliente.objects.filter(
                        propriedade=propriedade,
                        ativo=True
                    ).first()
        except Exception as e:
            # Se houver erro (tabela não existe), usar None
            logger.warning(f"Erro ao buscar cliente padrão: {e}")
            cliente_padrao = None
    
    # Buscar prazo de pagamento padrão (do cliente ou 30 dias)
    prazo_pagamento = 30
    if cliente_padrao:
        try:
            if hasattr(cliente_padrao, 'prazo_pagamento_dias') and cliente_padrao.prazo_pagamento_dias:
                prazo_pagamento = cliente_padrao.prazo_pagamento_dias
            
            # Buscar frigorífico vinculado ao cliente para obter prazo
            if hasattr(cliente_padrao, 'frigorifico_vinculado') and cliente_padrao.frigorifico_vinculado:
                frigorifico = cliente_padrao.frigorifico_vinculado
                if hasattr(frigorifico, 'prazo_pagamento_dias') and frigorifico.prazo_pagamento_dias:
                    prazo_pagamento = frigorifico.prazo_pagamento_dias
        except Exception as e:
            logger.warning(f"Erro ao buscar prazo de pagamento: {e}")
            prazo_pagamento = 30
    
    with transaction.atomic():
        # Limpar vendas anteriores do cenário (opcional - pode comentar para manter histórico)
        # VendaProjetada.objects.filter(cenario=cenario).delete()
        
        total_processadas = 0
        for movimentacao in movimentacoes_venda:
            total_processadas += 1
            logger.info(f"Processando movimentação {total_processadas}/{movimentacoes_venda.count()}: {movimentacao.id} - {movimentacao.categoria.nome} - {movimentacao.quantidade} cabeças - {movimentacao.data_movimentacao}")
            
            # Verificar se já existe venda para esta movimentação E este cenário
            venda_existente = VendaProjetada.objects.filter(
                movimentacao_projetada=movimentacao,
                cenario=cenario
            ).first()
            
            if venda_existente:
                logger.info(f"Venda já existe para movimentação {movimentacao.id} e cenário {cenario.nome}")
                # Se a venda existe mas está com valor zerado, atualizar
                if not venda_existente.valor_total or venda_existente.valor_total == 0:
                    # Recalcular valores
                    valor_por_cabeca = movimentacao.valor_por_cabeca
                    if not valor_por_cabeca or valor_por_cabeca == 0:
                        # Buscar do inventário ou CEPEA
                        inventario_item = InventarioRebanho.objects.filter(
                            propriedade=propriedade,
                            categoria=movimentacao.categoria
                        ).first()
                        
                        if inventario_item and inventario_item.valor_por_cabeca:
                            valor_por_cabeca = inventario_item.valor_por_cabeca
                        else:
                            try:
                                from ..views import obter_valor_padrao_por_categoria
                                ano_mov = movimentacao.data_movimentacao.year if movimentacao.data_movimentacao else None
                                valor_por_cabeca = obter_valor_padrao_por_categoria(
                                    movimentacao.categoria, 
                                    propriedade, 
                                    ano_mov
                                )
                            except Exception:
                                valor_por_cabeca = Decimal('2000.00')
                    
                    # Atualizar venda existente
                    venda_existente.valor_por_animal = valor_por_cabeca
                    venda_existente.valor_total = valor_por_cabeca * venda_existente.quantidade
                    if venda_existente.peso_total_kg and venda_existente.peso_total_kg > 0:
                        venda_existente.valor_por_kg = valor_por_cabeca / (venda_existente.peso_total_kg / venda_existente.quantidade)
                    venda_existente.save()
                    logger.info(f"Venda existente {venda_existente.id} atualizada com valores corretos")
                
                vendas_criadas.append(venda_existente)
                continue
            
            # Calcular valores
            # Buscar valor da movimentação, se não tiver, buscar do inventário ou CEPEA
            valor_por_cabeca = movimentacao.valor_por_cabeca
            
            if not valor_por_cabeca or valor_por_cabeca == 0:
                # Tentar buscar do inventário
                inventario_item = InventarioRebanho.objects.filter(
                    propriedade=propriedade,
                    categoria=movimentacao.categoria
                ).first()
                
                if inventario_item and inventario_item.valor_por_cabeca:
                    valor_por_cabeca = inventario_item.valor_por_cabeca
                    logger.info(f"Valor obtido do inventário para {movimentacao.categoria.nome}: R$ {valor_por_cabeca}")
                else:
                    # Tentar buscar do CEPEA ou usar valor padrão
                    try:
                        from ..views import obter_valor_padrao_por_categoria
                        ano_mov = movimentacao.data_movimentacao.year if movimentacao.data_movimentacao else None
                        valor_por_cabeca = obter_valor_padrao_por_categoria(
                            movimentacao.categoria, 
                            propriedade, 
                            ano_mov
                        )
                        logger.info(f"Valor obtido do CEPEA/padrão para {movimentacao.categoria.nome} ({ano_mov}): R$ {valor_por_cabeca}")
                    except Exception as e:
                        logger.warning(f"Erro ao buscar valor padrão para {movimentacao.categoria.nome}: {e}")
                        valor_por_cabeca = Decimal('2000.00')  # Valor padrão genérico
                        logger.info(f"Usando valor genérico R$ {valor_por_cabeca}")
            
            quantidade = movimentacao.quantidade
            
            # Calcular peso médio baseado na categoria (valores aproximados)
            peso_medio_kg = calcular_peso_medio_categoria(movimentacao.categoria)
            peso_total_kg = None
            valor_por_kg = None
            
            if peso_medio_kg:
                peso_total_kg = peso_medio_kg * quantidade
                if peso_total_kg > 0:
                    valor_por_kg = valor_por_cabeca / peso_medio_kg if peso_medio_kg > 0 else None
            
            # Calcular valor total
            valor_total = valor_por_cabeca * quantidade if valor_por_cabeca else Decimal('0.00')
            
            # Obter nome do cliente (pode ser None se não houver cliente padrão)
            cliente_nome = None
            if cliente_padrao:
                cliente_nome = cliente_padrao.nome
            else:
                cliente_nome = "Cliente não definido"
            
            # Criar venda projetada
            venda = VendaProjetada.objects.create(
                propriedade=propriedade,
                planejamento=movimentacao.planejamento,
                cenario=cenario,
                movimentacao_projetada=movimentacao,
                data_venda=movimentacao.data_movimentacao,
                categoria=movimentacao.categoria,
                quantidade=quantidade,
                cliente_nome=cliente_nome,
                peso_total_kg=peso_total_kg,
                peso_medio_kg=peso_medio_kg,
                valor_por_kg=valor_por_kg,
                valor_por_animal=valor_por_cabeca,
                valor_total=valor_total,
                prazo_pagamento_dias=prazo_pagamento,
                observacoes=f"Venda gerada automaticamente da projeção"
            )
            
            # Calcular data de recebimento
            if not venda.data_recebimento:
                venda.data_recebimento = venda.data_venda + timedelta(days=prazo_pagamento)
                venda.save()
            
            vendas_criadas.append(venda)
            logger.info(f"✅ Venda criada: ID={venda.id}, {venda.quantidade} {venda.categoria.nome}, Valor Total=R$ {venda.valor_total}")
    
    logger.info(f"✅✅ Total de {len(vendas_criadas)} vendas criadas para o cenário {cenario.nome}")
    return vendas_criadas


def calcular_peso_medio_categoria(categoria):
    """
    Calcula peso médio aproximado por categoria de animal (em kg)
    Valores são aproximações padrão da indústria
    """
    nome_categoria = categoria.nome.upper()
    
    # Pesos médios aproximados por categoria
    pesos_medios = {
        'BEZERRO': Decimal('120.00'),  # ~120 kg
        'BEZERRA': Decimal('110.00'),  # ~110 kg
        'NOVILHO': Decimal('280.00'),  # ~280 kg
        'NOVILHA': Decimal('250.00'),  # ~250 kg
        'GARROTE': Decimal('350.00'),  # ~350 kg
        'BOI': Decimal('450.00'),      # ~450 kg
        'PRIMIPARA': Decimal('380.00'), # ~380 kg
        'VACA': Decimal('450.00'),     # ~450 kg
        'TOURO': Decimal('650.00'),    # ~650 kg
    }
    
    # Buscar correspondência parcial
    for key, peso in pesos_medios.items():
        if key in nome_categoria:
            return peso
    
    # Peso padrão caso não encontre
    return Decimal('350.00')


def gerar_vendas_todos_cenarios(propriedade, planejamento=None):
    """
    Gera vendas para todos os cenários de um planejamento
    
    Args:
        propriedade: Propriedade
        planejamento: PlanejamentoAnual (opcional)
    
    Returns:
        dict: Dicionário com cenário como chave e lista de vendas como valor
    """
    if not planejamento:
        planejamento = PlanejamentoAnual.objects.filter(
            propriedade=propriedade
        ).order_by('-ano').first()
    
    if not planejamento:
        return {}
    
    vendas_por_cenario = {}
    cenarios = planejamento.cenarios.all()
    
    logger.info(f"Gerando vendas para {cenarios.count()} cenários do planejamento {planejamento.codigo}")
    
    for cenario in cenarios:
        logger.info(f"Iniciando geração de vendas para o cenário: {cenario.nome}")
        try:
            vendas = gerar_vendas_do_cenario(propriedade, cenario)
            vendas_por_cenario[cenario] = vendas
            logger.info(f"✅ Cenário {cenario.nome}: {len(vendas)} vendas geradas")
        except Exception as e:
            logger.error(f"❌ Erro ao gerar vendas para o cenário {cenario.nome}: {str(e)}", exc_info=True)
            vendas_por_cenario[cenario] = []
    
    total_vendas = sum(len(vendas) for vendas in vendas_por_cenario.values())
    logger.info(f"✅✅ Total geral: {total_vendas} vendas geradas para {len(cenarios)} cenários")
    
    return vendas_por_cenario

