# -*- coding: utf-8 -*-
"""
IA Avançada de Planejamento com Aprendizado e Pesquisa
Sistema que aprende com dados do setor pecuário e pesquisa informações na internet
"""

import logging
import json
from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from django.db.models import Q, Sum, Avg, Count, Max, Min
from django.utils import timezone
from django.conf import settings

from gestao_rural.models import (
    Propriedade,
    PlanejamentoAnual,
    CategoriaAnimal,
    InventarioRebanho,
    MovimentacaoProjetada,
    MovimentacaoIndividual,
    MetaComercialPlanejada,
    MetaFinanceiraPlanejada,
    CenarioPlanejamento,
)
from .ml_price_prediction import MLPricePredictionService
from .ml_natalidade_mortalidade import MLNatalidadeMortalidadeService
from .big_data_analytics import BigDataAnalyticsService
from ..apis_integracao.api_imea import IMEAService
from ..apis_integracao.api_scot_consultoria import ScotConsultoriaService

# Importar módulos de Machine Learning
from .ml_models import (
    PrevisaoPrecosML,
    AnaliseCorrelacaoAnomalias,
    PrevisaoNatalidadeMortalidadeML,
)

logger = logging.getLogger(__name__)


class IAPlanejamentoAvancada:
    """
    IA Avançada que:
    - Aprende com dados históricos do sistema
    - Pesquisa informações de mercado na internet
    - Fornece recomendações inteligentes baseadas em dados reais
    - Analisa tendências e padrões
    """
    
    def __init__(self, propriedade: Propriedade):
        self.propriedade = propriedade
        self.ano_atual = timezone.now().year
        self.dados_aprendizado = {}
        self.insights_mercado = {}

        # Inicializar serviços avançados
        self.ml_price_service = MLPricePredictionService()
        self.ml_natalidade_service = MLNatalidadeMortalidadeService()
        self.big_data_service = BigDataAnalyticsService()
        self.imea_service = IMEAService()
        self.scot_service = ScotConsultoriaService()

        # Inicializar módulos de Machine Learning
        try:
            self.ml_previsao_precos = PrevisaoPrecosML(propriedade)
            self.ml_analise_correlacao = AnaliseCorrelacaoAnomalias(propriedade)
            self.ml_previsao_reprodutiva = PrevisaoNatalidadeMortalidadeML(propriedade)
            self.ml_disponivel = True
        except Exception as e:
            logger.warning(f'Erro ao inicializar módulos ML: {e}')
            self.ml_disponivel = False
        
    def analisar_planejamento_com_ia(
        self, 
        planejamento: Optional[PlanejamentoAnual] = None,
        incluir_pesquisa_web: bool = True
    ) -> Dict[str, Any]:
        """
        Análise completa do planejamento com IA
        """
        try:
            # 1. Aprender com dados históricos
            dados_historicos = self._aprender_com_dados_historicos()
            
            # 2. Analisar inventário atual
            analise_inventario = self._analisar_inventario_atual()
            
            # 3. Analisar planejamento existente (se houver)
            analise_planejamento = {}
            if planejamento:
                analise_planejamento = self._analisar_planejamento_existente(planejamento)
            
            # 4. Pesquisar informações de mercado (se habilitado)
            dados_mercado = {}
            if incluir_pesquisa_web:
                dados_mercado = self._pesquisar_informacoes_mercado()

            # 5. Análises com Machine Learning (se disponível)
            analises_ml = {}
            if self.ml_disponivel:
                try:
                    analises_ml = self._executar_analises_ml(
                        dados_historicos,
                        analise_inventario
                    )
                except Exception as e:
                    logger.warning(f'Erro nas análises ML: {e}')
                    analises_ml = {'erro_ml': str(e)}

            # 6. Gerar recomendações inteligentes
            recomendacoes = self._gerar_recomendacoes_inteligentes(
                dados_historicos,
                analise_inventario,
                analise_planejamento,
                dados_mercado,
                analises_ml
            )

            # 7. Calcular projeções otimizadas
            projecoes = self._calcular_projecoes_otimizadas(
                dados_historicos,
                analise_inventario,
                analises_ml
            )
            
            return {
                'sucesso': True,
                'dados_historicos': dados_historicos,
                'analise_inventario': analise_inventario,
                'analise_planejamento': analise_planejamento,
                'dados_mercado': dados_mercado,
                'analises_ml': analises_ml,
                'recomendacoes': recomendacoes,
                'projecoes': projecoes,
                'insights': self._gerar_insights_gerais(
                    dados_historicos,
                    analise_inventario,
                    dados_mercado,
                    analises_ml
                ),
                'timestamp': timezone.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f'Erro na análise de IA: {e}', exc_info=True)
            return {
                'sucesso': False,
                'erro': str(e),
                'recomendacoes': ['Erro na análise. Tente novamente.'],
            }
    
    def _aprender_com_dados_historicos(self) -> Dict[str, Any]:
        """
        Aprende padrões e tendências dos dados históricos do sistema
        """
        # Buscar movimentações dos últimos 3 anos
        ano_inicio = self.ano_atual - 3
        movimentacoes = MovimentacaoIndividual.objects.filter(
            Q(propriedade_origem=self.propriedade) | 
            Q(propriedade_destino=self.propriedade) |
            Q(animal__propriedade=self.propriedade)
        ).filter(
            data_movimentacao__year__gte=ano_inicio
        ).select_related('categoria_anterior', 'categoria_nova', 'animal__categoria')
        
        # Análise de vendas
        vendas = movimentacoes.filter(tipo_movimentacao='VENDA')
        total_vendas = vendas.count()
        valor_total_vendas = vendas.aggregate(total=Sum('valor'))['total'] or Decimal('0')
        quantidade_total_vendas = sum(
            getattr(v, 'quantidade_animais', 1) for v in vendas
        )
        
        # Preço médio por categoria
        precos_por_categoria = {}
        for categoria in CategoriaAnimal.objects.filter(ativo=True):
            vendas_cat = vendas.filter(
                Q(categoria_anterior=categoria) | 
                Q(categoria_nova=categoria) |
                Q(animal__categoria=categoria)
            )
            if vendas_cat.exists():
                valor_cat = vendas_cat.aggregate(total=Sum('valor'))['total'] or Decimal('0')
                qtd_cat = sum(getattr(v, 'quantidade_animais', 1) for v in vendas_cat)
                if qtd_cat > 0:
                    precos_por_categoria[categoria.nome] = {
                        'preco_medio': float(valor_cat / Decimal(qtd_cat)),
                        'quantidade_vendida': qtd_cat,
                        'valor_total': float(valor_cat),
                    }
        
        # Análise de compras
        compras = movimentacoes.filter(tipo_movimentacao='COMPRA')
        total_compras = compras.count()
        valor_total_compras = compras.aggregate(total=Sum('valor'))['total'] or Decimal('0')
        
        # Análise de nascimentos
        nascimentos = movimentacoes.filter(tipo_movimentacao='NASCIMENTO')
        total_nascimentos = nascimentos.count()
        
        # Análise de mortes
        mortes = movimentacoes.filter(tipo_movimentacao='MORTE')
        total_mortes = mortes.count()
        
        # Sazonalidade (por mês)
        sazonalidade = defaultdict(lambda: {'vendas': 0, 'compras': 0, 'nascimentos': 0})
        for mov in movimentacoes:
            mes = mov.data_movimentacao.month
            if mov.tipo_movimentacao == 'VENDA':
                sazonalidade[mes]['vendas'] += getattr(mov, 'quantidade_animais', 1)
            elif mov.tipo_movimentacao == 'COMPRA':
                sazonalidade[mes]['compras'] += getattr(mov, 'quantidade_animais', 1)
            elif mov.tipo_movimentacao == 'NASCIMENTO':
                sazonalidade[mes]['nascimentos'] += getattr(mov, 'quantidade_animais', 1)
        
        # Tendências de preço (últimos 12 meses)
        ultimos_12_meses = timezone.now() - timedelta(days=365)
        vendas_recentes = vendas.filter(data_movimentacao__gte=ultimos_12_meses)
        preco_medio_recente = Decimal('0')
        if vendas_recentes.exists() and quantidade_total_vendas > 0:
            preco_medio_recente = valor_total_vendas / Decimal(quantidade_total_vendas)
        
        return {
            'periodo_analise': f'{ano_inicio} - {self.ano_atual}',
            'vendas': {
                'total': total_vendas,
                'quantidade_total': quantidade_total_vendas,
                'valor_total': float(valor_total_vendas),
                'preco_medio': float(preco_medio_recente) if preco_medio_recente else 0,
                'precos_por_categoria': precos_por_categoria,
            },
            'compras': {
                'total': total_compras,
                'valor_total': float(valor_total_compras),
            },
            'nascimentos': {
                'total': total_nascimentos,
            },
            'mortes': {
                'total': total_mortes,
            },
            'sazonalidade': dict(sazonalidade),
            'taxa_natalidade_historica': self._calcular_taxa_natalidade_historica(),
            'taxa_mortalidade_historica': self._calcular_taxa_mortalidade_historica(),
        }
    
    def _analisar_inventario_atual(self) -> Dict[str, Any]:
        """
        Analisa o inventário atual da propriedade
        """
        inventario = InventarioRebanho.objects.filter(
            propriedade=self.propriedade
        ).select_related('categoria').order_by('-data_inventario')
        
        if not inventario.exists():
            return {
                'existe': False,
                'mensagem': 'Nenhum inventário cadastrado',
            }
        
        inventario_recente = inventario.first()
        data_inventario = inventario_recente.data_inventario
        
        # Buscar todos os itens do inventário mais recente
        itens = InventarioRebanho.objects.filter(
            propriedade=self.propriedade,
            data_inventario=data_inventario
        ).select_related('categoria')
        
        total_animais = sum(item.quantidade for item in itens)
        valor_total = sum(item.valor_total or Decimal('0') for item in itens)
        
        # Análise por categoria
        categorias_analise = {}
        for item in itens:
            categoria = item.categoria.nome
            categorias_analise[categoria] = {
                'quantidade': item.quantidade,
                'valor_total': float(item.valor_total or Decimal('0')),
                'valor_por_cabeca': float(item.valor_por_cabeca or Decimal('0')),
            }
        
        # Identificar matrizes
        matrizes = sum(
            item.quantidade for item in itens
            if any(kw in item.categoria.nome.lower() for kw in ['vaca', 'matriz'])
        )
        
        return {
            'existe': True,
            'data': data_inventario,
            'total_animais': total_animais,
            'valor_total': float(valor_total),
            'matrizes': matrizes,
            'categorias': categorias_analise,
            'idade_inventario_dias': (timezone.now().date() - data_inventario).days,
        }
    
    def _analisar_planejamento_existente(self, planejamento: PlanejamentoAnual) -> Dict[str, Any]:
        """
        Analisa um planejamento existente
        """
        metas_comerciais = MetaComercialPlanejada.objects.filter(planejamento=planejamento)
        metas_financeiras = MetaFinanceiraPlanejada.objects.filter(planejamento=planejamento)
        cenarios = CenarioPlanejamento.objects.filter(planejamento=planejamento)
        
        receita_planejada = sum(
            (meta.quantidade_animais or 0) * (meta.preco_medio_esperado or Decimal('0'))
            for meta in metas_comerciais
        )
        
        custos_planejados = sum(
            meta.valor_anual_previsto or Decimal('0')
            for meta in metas_financeiras
            if meta.tipo_custo != 'INVESTIMENTO'
        )
        
        investimentos_planejados = sum(
            meta.valor_anual_previsto or Decimal('0')
            for meta in metas_financeiras
            if meta.tipo_custo == 'INVESTIMENTO'
        )
        
        return {
            'ano': planejamento.ano,
            'status': planejamento.status,
            'descricao': planejamento.descricao,
            'metas_comerciais_count': metas_comerciais.count(),
            'metas_financeiras_count': metas_financeiras.count(),
            'cenarios_count': cenarios.count(),
            'receita_planejada': float(receita_planejada),
            'custos_planejados': float(custos_planejados),
            'investimentos_planejados': float(investimentos_planejados),
            'resultado_planejado': float(receita_planejada - custos_planejados - investimentos_planejados),
        }
    
    def _pesquisar_informacoes_mercado(self) -> Dict[str, Any]:
        """
        Pesquisa informações de mercado na internet
        Simula pesquisa de preços e tendências do setor pecuário
        """
        # Em produção, isso poderia usar APIs reais como:
        # - CEPEA (Centro de Estudos Avançados em Economia Aplicada)
        # - IMEA (Instituto Mato-grossense de Economia Agropecuária)
        # - Web scraping de sites de leilões
        # - APIs de cotações
        
        # Por enquanto, retorna dados simulados baseados em benchmarks do setor
        estado = self.propriedade.estado or 'MT'
        
        # Preços médios de mercado por região (valores de referência)
        precos_mercado = {
            'MT': {  # Mato Grosso
                'Boi Gordo': {'preco_arroba': 280.00, 'tendencia': 'estavel'},
                'Novilho': {'preco_arroba': 300.00, 'tendencia': 'alta'},
                'Bezerro': {'preco_cabeca': 1800.00, 'tendencia': 'alta'},
            },
            'MS': {  # Mato Grosso do Sul
                'Boi Gordo': {'preco_arroba': 285.00, 'tendencia': 'estavel'},
                'Novilho': {'preco_arroba': 305.00, 'tendencia': 'alta'},
                'Bezerro': {'preco_cabeca': 1850.00, 'tendencia': 'alta'},
            },
            'GO': {  # Goiás
                'Boi Gordo': {'preco_arroba': 275.00, 'tendencia': 'estavel'},
                'Novilho': {'preco_arroba': 295.00, 'tendencia': 'alta'},
                'Bezerro': {'preco_cabeca': 1750.00, 'tendencia': 'alta'},
            },
        }
        
        # Obter preços da região
        precos_regiao = precos_mercado.get(estado, precos_mercado['MT'])
        
        # Sazonalidade de preços (meses melhores para venda)
        meses_melhor_venda = [7, 8, 9, 10]  # Julho a Outubro (seca)
        meses_pior_venda = [11, 12, 1, 2]  # Novembro a Fevereiro (chuva)
        
        # Tendências do mercado
        mes_atual = timezone.now().month
        estacao = 'seca' if mes_atual in [5, 6, 7, 8, 9, 10] else 'chuva'
        
        return {
            'regiao': estado,
            'precos_mercado': precos_regiao,
            'meses_melhor_venda': meses_melhor_venda,
            'meses_pior_venda': meses_pior_venda,
            'estacao_atual': estacao,
            'recomendacao_epoca': 'vender' if mes_atual in meses_melhor_venda else 'aguardar',
            'fonte': 'Benchmarks do setor pecuário',
            'atualizacao': timezone.now().isoformat(),
        }
    
    def _gerar_recomendacoes_inteligentes(
        self,
        dados_historicos: Dict[str, Any],
        analise_inventario: Dict[str, Any],
        analise_planejamento: Dict[str, Any],
        dados_mercado: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Gera recomendações inteligentes baseadas em todos os dados analisados
        """
        recomendacoes = []
        
        # 1. Recomendações baseadas em inventário
        if analise_inventario.get('existe'):
            idade_inventario = analise_inventario.get('idade_inventario_dias', 0)
            if idade_inventario > 90:
                recomendacoes.append({
                    'tipo': 'inventario',
                    'prioridade': 'alta',
                    'titulo': 'Atualizar Inventário',
                    'mensagem': f'Seu inventário tem {idade_inventario} dias. Recomendamos atualizar para ter dados mais precisos.',
                    'acao': 'Atualizar inventário',
                })
        
        # 2. Recomendações baseadas em histórico de vendas
        if dados_historicos.get('vendas', {}).get('total', 0) > 0:
            preco_medio_historico = dados_historicos['vendas'].get('preco_medio', 0)
            precos_mercado_atual = dados_mercado.get('precos_mercado', {})
            
            # Comparar com preços de mercado
            if precos_mercado_atual:
                for categoria_mercado, dados_preco in precos_mercado_atual.items():
                    preco_mercado = dados_preco.get('preco_arroba', 0)
                    if preco_mercado > preco_medio_historico * 1.1:  # 10% acima
                        recomendacoes.append({
                            'tipo': 'preco',
                            'prioridade': 'media',
                            'titulo': f'Oportunidade de Venda - {categoria_mercado}',
                            'mensagem': f'Preços de mercado estão {((preco_mercado/preco_medio_historico - 1) * 100):.1f}% acima da sua média histórica. Boa época para vender!',
                            'acao': 'Avaliar vendas',
                        })
        
        # 3. Recomendações baseadas em sazonalidade
        mes_atual = timezone.now().month
        meses_melhor_venda = dados_mercado.get('meses_melhor_venda', [])
        if mes_atual in meses_melhor_venda:
            recomendacoes.append({
                'tipo': 'sazonalidade',
                'prioridade': 'alta',
                'titulo': 'Época Favorável para Vendas',
                'mensagem': 'Estamos na melhor época do ano para vendas. Considere planejar vendas para os próximos meses.',
                'acao': 'Planejar vendas',
            })
        
        # 4. Recomendações baseadas em taxa de natalidade
        taxa_natalidade = dados_historicos.get('taxa_natalidade_historica', 0)
        if taxa_natalidade < 0.70:  # Abaixo de 70%
            recomendacoes.append({
                'tipo': 'reproducao',
                'prioridade': 'alta',
                'titulo': 'Melhorar Taxa de Natalidade',
                'mensagem': f'Sua taxa de natalidade histórica é {taxa_natalidade*100:.1f}%. Considere melhorar manejo reprodutivo, nutrição das matrizes ou IATF.',
                'acao': 'Revisar reprodução',
            })
        
        # 5. Recomendações baseadas em taxa de mortalidade
        taxa_mortalidade = dados_historicos.get('taxa_mortalidade_historica', 0)
        if taxa_mortalidade > 0.05:  # Acima de 5%
            recomendacoes.append({
                'tipo': 'sanidade',
                'prioridade': 'alta',
                'titulo': 'Reduzir Taxa de Mortalidade',
                'mensagem': f'Sua taxa de mortalidade histórica é {taxa_mortalidade*100:.1f}%. Considere melhorar programa sanitário e manejo.',
                'acao': 'Revisar sanidade',
            })
        
        # 6. Recomendações baseadas em planejamento existente
        if analise_planejamento:
            resultado_planejado = analise_planejamento.get('resultado_planejado', 0)
            if resultado_planejado < 0:
                recomendacoes.append({
                    'tipo': 'financeiro',
                    'prioridade': 'alta',
                    'titulo': 'Planejamento com Resultado Negativo',
                    'mensagem': f'Seu planejamento prevê resultado negativo de R$ {abs(resultado_planejado):,.2f}. Revise custos e receitas.',
                    'acao': 'Revisar planejamento',
                })
        
        return recomendacoes
    
    def _calcular_projecoes_otimizadas(
        self,
        dados_historicos: Dict[str, Any],
        analise_inventario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula projeções otimizadas baseadas em dados históricos
        """
        if not analise_inventario.get('existe'):
            return {'mensagem': 'Necessário inventário para projeções'}
        
        total_animais = analise_inventario.get('total_animais', 0)
        matrizes = analise_inventario.get('matrizes', 0)
        
        # Projeção de nascimentos (baseado em taxa histórica)
        taxa_natalidade = dados_historicos.get('taxa_natalidade_historica', 0.75)
        nascimentos_projetados = int(matrizes * taxa_natalidade) if matrizes > 0 else 0
        
        # Projeção de vendas (baseado em histórico)
        vendas_historicas_ano = dados_historicos.get('vendas', {}).get('quantidade_total', 0) / 3  # Média dos últimos 3 anos
        vendas_projetadas = int(vendas_historicas_ano)
        
        # Projeção de receita (baseado em preço médio histórico)
        preco_medio = dados_historicos.get('vendas', {}).get('preco_medio', 0)
        receita_projetada = vendas_projetadas * preco_medio
        
        return {
            'nascimentos_projetados': nascimentos_projetados,
            'vendas_projetadas': vendas_projetadas,
            'receita_projetada': float(receita_projetada),
            'preco_medio_projetado': float(preco_medio),
            'taxa_natalidade_usada': taxa_natalidade,
        }
    
    def _gerar_insights_gerais(
        self,
        dados_historicos: Dict[str, Any],
        analise_inventario: Dict[str, Any],
        dados_mercado: Dict[str, Any]
    ) -> List[str]:
        """
        Gera insights gerais sobre a propriedade
        """
        insights = []
        
        # Insight sobre crescimento
        if analise_inventario.get('existe'):
            total_animais = analise_inventario.get('total_animais', 0)
            if total_animais > 0:
                insights.append(f"📊 Rebanho atual: {total_animais} animais")
        
        # Insight sobre histórico de vendas
        vendas_total = dados_historicos.get('vendas', {}).get('total', 0)
        if vendas_total > 0:
            insights.append(f"💰 Histórico: {vendas_total} vendas registradas nos últimos 3 anos")
        
        # Insight sobre mercado
        if dados_mercado.get('recomendacao_epoca') == 'vender':
            insights.append("📈 Mercado favorável: Boa época para vendas")
        
        return insights
    
    def _calcular_taxa_natalidade_historica(self) -> float:
        """
        Calcula taxa de natalidade histórica
        """
        # Buscar matrizes no inventário mais recente
        inventario = InventarioRebanho.objects.filter(
            propriedade=self.propriedade
        ).select_related('categoria').order_by('-data_inventario').first()
        
        if not inventario:
            return 0.75  # Default
        
        # Buscar itens do inventário mais recente
        itens = InventarioRebanho.objects.filter(
            propriedade=self.propriedade,
            data_inventario=inventario.data_inventario
        )
        
        matrizes = sum(
            item.quantidade for item in itens
            if any(kw in item.categoria.nome.lower() for kw in ['vaca', 'matriz'])
        )
        
        if matrizes == 0:
            return 0.75  # Default
        
        # Buscar nascimentos dos últimos 12 meses
        data_limite = timezone.now() - timedelta(days=365)
        nascimentos = MovimentacaoIndividual.objects.filter(
            Q(propriedade_origem=self.propriedade) |
            Q(propriedade_destino=self.propriedade) |
            Q(animal__propriedade=self.propriedade)
        ).filter(
            tipo_movimentacao='NASCIMENTO',
            data_movimentacao__gte=data_limite
        )
        
        total_nascimentos = sum(
            getattr(n, 'quantidade_animais', 1) for n in nascimentos
        )
        
        taxa = total_nascimentos / matrizes if matrizes > 0 else 0.75
        return min(taxa, 1.0)  # Máximo 100%
    
    def _calcular_taxa_mortalidade_historica(self) -> float:
        """
        Calcula taxa de mortalidade histórica
        """
        # Buscar total de animais no inventário mais recente
        inventario = InventarioRebanho.objects.filter(
            propriedade=self.propriedade
        ).order_by('-data_inventario').first()
        
        if not inventario:
            return 0.03  # Default 3%
        
        itens = InventarioRebanho.objects.filter(
            propriedade=self.propriedade,
            data_inventario=inventario.data_inventario
        )
        
        total_animais = sum(item.quantidade for item in itens)
        
        if total_animais == 0:
            return 0.03  # Default
        
        # Buscar mortes dos últimos 12 meses
        data_limite = timezone.now() - timedelta(days=365)
        mortes = MovimentacaoIndividual.objects.filter(
            Q(propriedade_origem=self.propriedade) |
            Q(animal__propriedade=self.propriedade)
        ).filter(
            tipo_movimentacao='MORTE',
            data_movimentacao__gte=data_limite
        )
        
        total_mortes = sum(
            getattr(m, 'quantidade_animais', 1) for m in mortes
        )
        
        taxa = total_mortes / total_animais if total_animais > 0 else 0.03
        return min(taxa, 0.10)  # Máximo 10%

    def _executar_analises_ml(
        self,
        dados_historicos: Dict[str, Any],
        analise_inventario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executa todas as análises de Machine Learning
        """
        analises_ml = {}

        try:
            # 1. Previsão de preços com ML
            previsao_precos = self.ml_previsao_precos.prever_preco_futuro(
                uf=self.propriedade.uf or 'MT',  # Default MT se não definido
                tipo_categoria='BOI',  # Categoria principal
                meses_a_frente=6
            )
            analises_ml['previsao_precos_ml'] = previsao_precos

        except Exception as e:
            logger.warning(f'Erro na previsão de preços ML: {e}')
            analises_ml['previsao_precos_ml'] = {'erro': str(e)}

        try:
            # 2. Análise de correlações
            correlacoes = self.ml_analise_correlacao.analisar_correlacoes_producao()
            analises_ml['correlacoes'] = correlacoes

        except Exception as e:
            logger.warning(f'Erro na análise de correlações: {e}')
            analises_ml['correlacoes'] = {'erro': str(e)}

        try:
            # 3. Detecção de anomalias
            anomalias = self.ml_analise_correlacao.detectar_anomalias('producao')
            analises_ml['anomalias_producao'] = anomalias

        except Exception as e:
            logger.warning(f'Erro na detecção de anomalias: {e}')
            analises_ml['anomalias_producao'] = {'erro': str(e)}

        try:
            # 4. Previsão de natalidade
            previsao_natalidade = self.ml_previsao_reprodutiva.prever_natalidade_futura(6)
            analises_ml['previsao_natalidade'] = previsao_natalidade

        except Exception as e:
            logger.warning(f'Erro na previsão de natalidade: {e}')
            analises_ml['previsao_natalidade'] = {'erro': str(e)}

        try:
            # 5. Previsão de mortalidade
            previsao_mortalidade = self.ml_previsao_reprodutiva.prever_mortalidade_futura(6)
            analises_ml['previsao_mortalidade'] = previsao_mortalidade

        except Exception as e:
            logger.warning(f'Erro na previsão de mortalidade: {e}')
            analises_ml['previsao_mortalidade'] = {'erro': str(e)}

        return analises_ml

    def _gerar_recomendacoes_inteligentes(
        self,
        dados_historicos: Dict[str, Any],
        analise_inventario: Dict[str, Any],
        analise_planejamento: Dict[str, Any],
        dados_mercado: Dict[str, Any],
        analises_ml: Dict[str, Any] = None
    ) -> List[str]:
        """
        Gera recomendações inteligentes incluindo análises ML
        """
        recomendacoes = []

        # Recomendações base (existentes)
        recomendacoes.extend(self._gerar_recomendacoes_base(
            dados_historicos, analise_inventario, analise_planejamento, dados_mercado
        ))

        # Recomendações baseadas em ML (se disponíveis)
        if analises_ml and self.ml_disponivel:
            recomendacoes.extend(self._gerar_recomendacoes_ml(analises_ml))

        return recomendacoes

    def _gerar_recomendacoes_ml(self, analises_ml: Dict[str, Any]) -> List[str]:
        """
        Gera recomendações baseadas nas análises de Machine Learning
        """
        recomendacoes = []

        # Recomendações baseadas em previsões de preços
        if 'previsao_precos_ml' in analises_ml and 'previsoes' in analises_ml['previsao_precos_ml']:
            previsoes = analises_ml['previsao_precos_ml']['previsoes']
            if previsoes:
                ultima_previsao = previsoes[-1]
                preco_atual = float(dados_historicos.get('precos_medios', {}).get('BOI', 0))

                if ultima_previsao.get('preco_previsto', 0) > preco_atual * 1.1:
                    recomendacoes.append(
                        "ML indica tendência de alta de preços. Considere adiar vendas para maximizar receita."
                    )
                elif ultima_previsao.get('preco_previsto', 0) < preco_atual * 0.9:
                    recomendacoes.append(
                        "ML projeta queda de preços. Avalie antecipar vendas para evitar perdas."
                    )

        # Recomendações baseadas em anomalias
        if 'anomalias_producao' in analises_ml and 'anomalias_detectadas' in analises_ml['anomalias_producao']:
            anomalias = analises_ml['anomalias_producao']['anomalias_detectadas']
            if len(anomalias) > 2:
                recomendacoes.append(
                    f"ML detectou {len(anomalias)} anomalias na produção. Revise processos de manejo."
                )

        # Recomendações baseadas em natalidade
        if 'previsao_natalidade' in analises_ml and 'previsoes' in analises_ml['previsao_natalidade']:
            natalidade = analises_ml['previsao_natalidade']['previsoes']
            if natalidade:
                taxa_media = sum(p.get('taxa_natalidade_prevista', 0) for p in natalidade) / len(natalidade)
                if taxa_media < 0.7:
                    recomendacoes.append(
                        f"ML projeta taxa de natalidade baixa ({taxa_media:.1%}). Considere investir em reprodução."
                    )

        # Recomendações baseadas em mortalidade
        if 'previsao_mortalidade' in analises_ml and 'previsoes' in analises_ml['previsao_mortalidade']:
            mortalidade = analises_ml['previsao_mortalidade']['previsoes']
            if mortalidade:
                taxa_media = sum(p.get('taxa_mortalidade_prevista', 0) for p in mortalidade) / len(mortalidade)
                if taxa_media > 0.05:
                    recomendacoes.append(
                        f"ML indica risco alto de mortalidade ({taxa_media:.1%}). Priorize saúde animal."
                    )

        # Recomendações baseadas em correlações
        if 'correlacoes' in analises_ml and 'correlacoes_fortes' in analises_ml['correlacoes']:
            correlacoes = analises_ml['correlacoes']['correlacoes_fortes']
            for correlacao in correlacoes[:2]:  # Top 2 correlações
                var1 = correlacao.get('variavel_1', '')
                var2 = correlacao.get('variavel_2', '')
                coef = correlacao.get('correlacao', 0)

                if 'precipitacao' in var1.lower() and coef > 0.5:
                    recomendacoes.append(
                        "Correlação forte entre precipitação e produtividade. Monitore condições climáticas."
                    )

        return recomendacoes

    def _calcular_projecoes_otimizadas(
        self,
        dados_historicos: Dict[str, Any],
        analise_inventario: Dict[str, Any],
        analises_ml: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Calcula projeções otimizadas incluindo ML
        """
        projecoes_base = self._calcular_projecoes_base(dados_historicos, analise_inventario)

        # Enriquecer com ML se disponível
        if analises_ml and self.ml_disponivel:
            projecoes_ml = self._integrar_projecoes_ml(projecoes_base, analises_ml)
            projecoes_base.update(projecoes_ml)

        return projecoes_base

    def _integrar_projecoes_ml(
        self,
        projecoes_base: Dict[str, Any],
        analises_ml: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integra projeções de ML nas projeções base
        """
        projecoes_ml = {}

        # Natalidade ML
        if 'previsao_natalidade' in analises_ml and 'previsoes' in analises_ml['previsao_natalidade']:
            natalidade_ml = analises_ml['previsao_natalidade']['previsoes']
            projecoes_ml['natalidade_ml'] = natalidade_ml

        # Mortalidade ML
        if 'previsao_mortalidade' in analises_ml and 'previsoes' in analises_ml['previsao_mortalidade']:
            mortalidade_ml = analises_ml['previsao_mortalidade']['previsoes']
            projecoes_ml['mortalidade_ml'] = mortalidade_ml

        # Preços ML
        if 'previsao_precos_ml' in analises_ml and 'previsoes' in analises_ml['previsao_precos_ml']:
            precos_ml = analises_ml['previsao_precos_ml']['previsoes']
            projecoes_ml['precos_ml'] = precos_ml

        return projecoes_ml

    def _gerar_insights_gerais(
        self,
        dados_historicos: Dict[str, Any],
        analise_inventario: Dict[str, Any],
        dados_mercado: Dict[str, Any],
        analises_ml: Dict[str, Any] = None
    ) -> List[str]:
        """
        Gera insights gerais incluindo ML
        """
        insights = []

        # Insights base
        insights.extend(self._gerar_insights_base(
            dados_historicos, analise_inventario, dados_mercado
        ))

        # Insights de ML
        if analises_ml and self.ml_disponivel:
            insights.extend(self._gerar_insights_ml(analises_ml))

        return insights

    def _gerar_insights_ml(self, analises_ml: Dict[str, Any]) -> List[str]:
        """
        Gera insights baseados em análises de ML
        """
        insights = []

        if 'correlacoes' in analises_ml and 'insights_principais' in analises_ml['correlacoes']:
            insights_ml = analises_ml['correlacoes']['insights_principais']
            insights.extend(insights_ml[:3])  # Top 3 insights

        if 'anomalias_producao' in analises_ml and 'insights' in analises_ml['anomalias_producao']:
            insights_anomalias = analises_ml['anomalias_producao']['insights']
            insights.extend(insights_anomalias[:2])  # Top 2 insights

        # Insight sobre disponibilidade de ML
        if self.ml_disponivel:
            insights.append("Machine Learning integrado: previsões mais precisas disponíveis")
        else:
            insights.append("Machine Learning não disponível: usando métodos tradicionais")

        return insights

    # ========================================
    # MÉTODOS AVANÇADOS COM ML E APIs EXTERNAS
    # ========================================

    def _gerar_previsoes_ml(self) -> Dict[str, Any]:
        """
        Gera previsões usando Machine Learning avançado
        """
        previsoes = {
            'precos': {},
            'natalidade': {},
            'mortalidade': {},
            'disponivel': False
        }

        try:
            # 1. Previsões de preços para diferentes categorias
            categorias_preco = ['BOI', 'BEZERRO', 'BEZERRA', 'GARROTE', 'NOVILHA']

            for categoria in categorias_preco:
                try:
                    # Mapear categoria para formato da API
                    categoria_mapeada = categoria.lower()
                    if categoria == 'BOI':
                        categoria_mapeada = 'boi_gordo'
                    elif categoria == 'BEZERRO':
                        categoria_mapeada = 'bezerro'
                    elif categoria == 'BEZERRA':
                        categoria_mapeada = 'bezerra'
                    elif categoria == 'GARROTE':
                        categoria_mapeada = 'novilho'
                    elif categoria == 'NOVILHA':
                        categoria_mapeada = 'novilha'

                    # Previsão com ML
                    previsao_ml = self.ml_price_service.prever_precos_futuros(
                        uf='MT',  # Focar em Mato Grosso
                        categoria=categoria,
                        meses_a_frente=6,
                        metodo='ensemble'
                    )

                    if previsao_ml.get('sucesso'):
                        previsoes['precos'][categoria] = previsao_ml

                except Exception as e:
                    logger.warning(f'Erro na previsão ML para {categoria}: {e}')

            # 2. Previsões de natalidade
            try:
                natalidade_ml = self.ml_natalidade_service.prever_taxa_natalidade(
                    self.propriedade.id,
                    'Multípara',  # Categoria mais comum
                    periodo_meses=12
                )
                if natalidade_ml.get('sucesso'):
                    previsoes['natalidade'] = natalidade_ml
            except Exception as e:
                logger.warning(f'Erro na previsão de natalidade ML: {e}')

            # 3. Previsões de mortalidade
            try:
                mortalidade_ml = self.ml_natalidade_service.prever_taxa_mortalidade(
                    self.propriedade.id,
                    'Bezerros (0-12m)',  # Categoria crítica
                    periodo_meses=12
                )
                if mortalidade_ml.get('sucesso'):
                    previsoes['mortalidade'] = mortalidade_ml
            except Exception as e:
                logger.warning(f'Erro na previsão de mortalidade ML: {e}')

            previsoes['disponivel'] = True

        except Exception as e:
            logger.error(f'Erro geral nas previsões ML: {e}')

        return previsoes
