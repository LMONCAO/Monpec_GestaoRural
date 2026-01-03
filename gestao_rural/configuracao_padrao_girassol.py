# -*- coding: utf-8 -*-
"""
Módulo para aplicar configuração padrão da Girassol automaticamente
Este módulo é chamado automaticamente após gerar uma nova projeção
CONFIGURAÇÃO PADRÃO: Vender 480 cabeças a cada 90 dias após entrada
"""
import logging
from django.db import transaction
from datetime import date, timedelta
from decimal import Decimal
from .models import (
    Propriedade, MovimentacaoProjetada, CategoriaAnimal, 
    PlanejamentoAnual, VendaProjetada
)

logger = logging.getLogger(__name__)


def calcular_saldo_disponivel(propriedade, categoria, data_referencia, planejamento):
    """Calcula saldo disponível considerando inventário e movimentações"""
    from .models import InventarioRebanho
    
    # Inventário inicial
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').first()
    
    saldo = inventario.quantidade if inventario else 0
    
    # Aplicar movimentações até a data
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria,
        data_movimentacao__lte=data_referencia,
        planejamento=planejamento
    ).order_by('data_movimentacao', 'id')
    
    for mov in movimentacoes:
        if mov.tipo_movimentacao in ['PROMOCAO_ENTRADA', 'TRANSFERENCIA_ENTRADA', 'NASCIMENTO', 'COMPRA']:
            saldo += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'PROMOCAO_SAIDA', 'TRANSFERENCIA_SAIDA']:
            saldo -= mov.quantidade
    
    return max(0, saldo)


@transaction.atomic
def aplicar_configuracao_padrao_girassol(propriedade, planejamento):
    """
    Aplica configuração padrão da Girassol automaticamente após gerar projeção
    
    NOVA CONFIGURAÇÃO PADRÃO (2025):
    - Recebe garrotes do Favo de Mel (transferências e compras)
    - Ficam 90 dias na Girassol
    - Após 90 dias, vende de 100 em 100 até acabar o estoque
    - Sempre respeita saldo disponível (não pode ficar negativo)
    """
    logger.info(f"Iniciando aplicação de configuração padrão para {propriedade.nome_propriedade}")
    
    # Buscar categoria
    try:
        categoria_garrote = CategoriaAnimal.objects.get(nome__icontains='Garrote')
        categoria_boi = CategoriaAnimal.objects.get(nome__icontains='Boi 24-36')
    except CategoriaAnimal.DoesNotExist as e:
        logger.warning(f"Categoria não encontrada: {e}")
        return
    
    # ========== 1. BUSCAR TRANSFERÊNCIAS DE ENTRADA ==========
    logger.info("Buscando transferências de entrada...")
    
    entradas = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria_garrote,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        planejamento=planejamento
    ).order_by('data_movimentacao')
    
    logger.info(f"Transferências de entrada encontradas: {entradas.count()}")
    
    # ========== 2. DELETAR VENDAS EXISTENTES PARA RECRIAR ==========
    logger.info("Deletando vendas existentes para recriar...")
    
    # Buscar movimentações de venda existentes
    vendas_existentes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        categoria=categoria_boi,
        tipo_movimentacao='VENDA',
        planejamento=planejamento
    )
    
    total_vendas = vendas_existentes.count()
    
    # Deletar VendaProjetada associadas
    for mov in vendas_existentes:
        VendaProjetada.objects.filter(movimentacao_projetada=mov).delete()
    
    # Deletar movimentações de venda
    vendas_existentes.delete()
    
    logger.info(f"Deletadas: {total_vendas} vendas")
    
    # ========== 3. CRIAR EVOLUÇÕES E VENDAS ==========
    logger.info("Criando evoluções e vendas: após 90 dias, vender TUDO que recebeu na transferência...")
    
    intervalo_dias = 90  # 90 dias após entrada
    evolucoes_criadas = 0
    vendas_criadas = 0
    
    for entrada in entradas:
        data_entrada = entrada.data_movimentacao
        quantidade_entrada = entrada.quantidade
        
        logger.debug(f"Processando entrada: {quantidade_entrada} em {data_entrada.strftime('%d/%m/%Y')}")
        
        # NOVA CONFIGURAÇÃO: Após 90 dias, vender TUDO que recebeu nesta transferência
        # Data da venda: 90 dias após entrada
        data_venda = data_entrada + timedelta(days=intervalo_dias)
        
        # Criar evolução de TODO o lote na data da venda
        # (assumindo que após 90 dias, todos evoluem para venda)
        data_evolucao = date(data_entrada.year + 1, data_entrada.month, data_entrada.day)
        
        # Se a venda for antes da evolução natural, criar evolução antecipada
        if data_venda < data_evolucao:
            # Criar evolução de TODO o lote recebido
            MovimentacaoProjetada.objects.create(
                propriedade=propriedade,
                categoria=categoria_garrote,
                data_movimentacao=data_venda,
                tipo_movimentacao='PROMOCAO_SAIDA',
                quantidade=quantidade_entrada,
                planejamento=planejamento,
                observacao=f'Evolução: Garrote 12-24 → Boi 24-36 (lote completo de {quantidade_entrada} para venda após 90 dias) - NOVA REGRA 2025: vende tudo que recebeu'
            )
            
            MovimentacaoProjetada.objects.create(
                propriedade=propriedade,
                categoria=categoria_boi,
                data_movimentacao=data_venda,
                tipo_movimentacao='PROMOCAO_ENTRADA',
                quantidade=quantidade_entrada,
                planejamento=planejamento,
                observacao=f'Evolução: Garrote 12-24 → Boi 24-36 (lote completo de {quantidade_entrada} para venda após 90 dias) - NOVA REGRA 2025: vende tudo que recebeu'
            )
            
            evolucoes_criadas += 1
            logger.debug(f"Evolução criada: {quantidade_entrada} em {data_venda.strftime('%d/%m/%Y')}")
        
        # Verificar saldo disponível de bois gordos na data da venda
        saldo_disponivel = calcular_saldo_disponivel(
            propriedade, categoria_boi, data_venda, planejamento
        )
        
        # Vender TUDO que recebeu nesta transferência (mas não mais do que o saldo disponível)
        quantidade_vender = min(quantidade_entrada, saldo_disponivel)
        
        if quantidade_vender > 0:
            # Criar movimentação de venda
            movimentacao_venda = MovimentacaoProjetada.objects.create(
                propriedade=propriedade,
                categoria=categoria_boi,
                data_movimentacao=data_venda,
                tipo_movimentacao='VENDA',
                quantidade=quantidade_vender,
                planejamento=planejamento,
                observacao=f'Venda de gado gordo após 90 dias de engorda - Vendeu TUDO que recebeu na transferência de {data_entrada.strftime("%d/%m/%Y")} ({quantidade_entrada} garrotes) - NOVA REGRA 2025'
            )
            
            # Obter valores por ano para boi gordo
            ano_venda = data_venda.year
            
            def obter_valor_boi_gordo_por_ano(ano):
                """Retorna o valor total do boi gordo conforme o ano"""
                valores = {
                    2022: Decimal('5700.00'),
                    2023: Decimal('4950.00'),
                    2024: Decimal('5890.00'),
                    2025: Decimal('6032.00'),
                }
                return valores.get(ano, Decimal('5700.00'))  # Padrão se ano não encontrado
            
            valor_total_boi = obter_valor_boi_gordo_por_ano(ano_venda)
            # Calcular valor por kg (assumindo peso médio de 500kg)
            peso_medio = Decimal('500.00')
            valor_por_kg = valor_total_boi / peso_medio
            
            # Criar VendaProjetada
            VendaProjetada.objects.create(
                propriedade=propriedade,
                movimentacao_projetada=movimentacao_venda,
                data_venda=data_venda,
                categoria=categoria_boi,
                quantidade=quantidade_vender,
                cliente_nome='Frigorífico',
                valor_por_kg=valor_por_kg,
                peso_medio_kg=peso_medio,
                valor_total=valor_total_boi * Decimal(str(quantidade_vender))
            )
            
            vendas_criadas += 1
            logger.debug(f"Venda criada: {quantidade_vender} em {data_venda.strftime('%d/%m/%Y')} (recebeu {quantidade_entrada} em {data_entrada.strftime('%d/%m/%Y')}, saldo disponivel: {saldo_disponivel})")
        else:
            logger.debug(f"Sem saldo disponível para venda em {data_venda.strftime('%d/%m/%Y')} (saldo: {saldo_disponivel}, quantidade recebida: {quantidade_entrada})")
    
    logger.info(f"Evoluções criadas: {evolucoes_criadas}")
    logger.info(f"Vendas criadas: {vendas_criadas}")
    logger.info(f"Configuração padrão aplicada com sucesso para {propriedade.nome_propriedade}")

