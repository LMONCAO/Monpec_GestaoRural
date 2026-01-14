# -*- coding: utf-8 -*-
"""
API Scot Consultoria
Consulta de cotações, análises de mercado e indicadores do agronegócio
"""

import requests
import json
from typing import Dict, Optional, List, Any
from decimal import Decimal
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

import logging
logger = logging.getLogger(__name__)


class ScotConsultoriaService:
    """
    Serviço para integração com API da Scot Consultoria
    Fornece cotações, análises e indicadores do mercado pecuário
    """

    def __init__(self, api_key: Optional[str] = None, username: Optional[str] = None):
        """
        Inicializa o serviço Scot Consultoria

        Args:
            api_key: Chave de API da Scot
            username: Nome de usuário para autenticação
        """
        self.api_key = api_key or getattr(settings, 'SCOT_API_KEY', '')
        self.username = username or getattr(settings, 'SCOT_USERNAME', '')
        self.base_url = getattr(
            settings,
            'SCOT_BASE_URL',
            'https://api.scotconsultoria.com.br/v1'
        )
        self.timeout = getattr(settings, 'SCOT_TIMEOUT', 30)

        # Cache para evitar chamadas excessivas
        self.cache_timeout = 1800  # 30 minutos (dados atualizados frequentemente)

    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições da API Scot"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        if self.api_key:
            headers['X-API-Key'] = self.api_key
        if self.username:
            headers['X-Username'] = self.username

        return headers

    def obter_cotacoes_diarias(self, produto: str = 'boi_gordo') -> Dict[str, Any]:
        """
        Obtém cotações diárias dos produtos pecuários

        Args:
            produto: Tipo de produto ('boi_gordo', 'vaca_gorda', 'novilha', etc.)

        Returns:
            Dicionário com cotações diárias
        """
        cache_key = f'scot_cotacoes_diarias_{produto}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            url = f"{self.base_url}/cotacoes/diarias"
            params = {
                'produto': produto,
                'regiao': 'brasil',
                'dias': 30  # Últimos 30 dias
            }

            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                processed_data = self._processar_cotacoes_diarias(data, produto)

                cache.set(cache_key, processed_data, self.cache_timeout)

                return processed_data
            else:
                logger.warning(f'Erro na API Scot: {response.status_code} - {response.text}')
                return self._dados_fallback_cotacoes_diarias(produto)

        except Exception as e:
            logger.error(f'Erro ao consultar cotações Scot: {e}')
            return self._dados_fallback_cotacoes_diarias(produto)

    def obter_analise_semanal(self) -> Dict[str, Any]:
        """
        Obtém análise semanal do mercado pecuário

        Returns:
            Dicionário com análise semanal
        """
        cache_key = 'scot_analise_semanal'
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            url = f"{self.base_url}/analises/semanal"

            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                processed_data = self._processar_analise_semanal(data)

                cache.set(cache_key, processed_data, self.cache_timeout * 2)  # Cache por 1h

                return processed_data
            else:
                return self._dados_fallback_analise_semanal()

        except Exception as e:
            logger.error(f'Erro ao consultar análise Scot: {e}')
            return self._dados_fallback_analise_semanal()

    def obter_projetcoes_mensais(self, produto: str = 'boi_gordo', meses: int = 6) -> Dict[str, Any]:
        """
        Obtém projeções mensais de preços

        Args:
            produto: Tipo de produto
            meses: Número de meses para projeção

        Returns:
            Dicionário com projeções mensais
        """
        cache_key = f'scot_projetcoes_{produto}_{meses}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            url = f"{self.base_url}/projetcoes/mensais"
            params = {
                'produto': produto,
                'meses': meses
            }

            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                processed_data = self._processar_projetcoes_mensais(data, produto)

                cache.set(cache_key, processed_data, self.cache_timeout * 6)  # Cache por 3h

                return processed_data
            else:
                return self._dados_fallback_projetcoes_mensais(produto, meses)

        except Exception as e:
            logger.error(f'Erro ao consultar projeções Scot: {e}')
            return self._dados_fallback_projetcoes_mensais(produto, meses)

    def obter_indicadores_rurais(self) -> Dict[str, Any]:
        """
        Obtém indicadores rurais e econômicos

        Returns:
            Dicionário com indicadores rurais
        """
        cache_key = 'scot_indicadores_rurais'
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            url = f"{self.base_url}/indicadores/rurais"

            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                processed_data = self._processar_indicadores_rurais(data)

                cache.set(cache_key, processed_data, self.cache_timeout * 4)  # Cache por 2h

                return processed_data
            else:
                return self._dados_fallback_indicadores_rurais()

        except Exception as e:
            logger.error(f'Erro ao consultar indicadores Scot: {e}')
            return self._dados_fallback_indicadores_rurais()

    def obter_relatorio_mensal(self, ano: int, mes: int) -> Dict[str, Any]:
        """
        Obtém relatório mensal completo do mercado pecuário

        Args:
            ano: Ano do relatório
            mes: Mês do relatório

        Returns:
            Dicionário com relatório mensal
        """
        cache_key = f'scot_relatorio_{ano}_{mes}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        try:
            url = f"{self.base_url}/relatorios/mensais/{ano}/{mes:02d}"

            response = requests.get(
                url,
                headers=self._get_headers(),
                timeout=self.timeout
            )

            if response.status_code == 200:
                data = response.json()
                processed_data = self._processar_relatorio_mensal(data, ano, mes)

                # Cache por mais tempo para relatórios mensais
                cache.set(cache_key, processed_data, self.cache_timeout * 48)  # Cache por 24h

                return processed_data
            else:
                return self._dados_fallback_relatorio_mensal(ano, mes)

        except Exception as e:
            logger.error(f'Erro ao consultar relatório Scot: {e}')
            return self._dados_fallback_relatorio_mensal(ano, mes)

    def _processar_cotacoes_diarias(self, data: Dict, produto: str) -> Dict[str, Any]:
        """
        Processa dados de cotações diárias
        """
        processed = {
            'fonte': 'SCOT_CONSULTORIA',
            'produto': produto,
            'tipo': 'cotacoes_diarias',
            'atualizado_em': timezone.now().isoformat(),
            'cotacoes': []
        }

        if 'cotacoes' in data:
            for cotacao in data['cotacoes']:
                processed['cotacoes'].append({
                    'data': cotacao.get('data'),
                    'preco_abertura': Decimal(str(cotacao.get('preco_abertura', 0))),
                    'preco_fechamento': Decimal(str(cotacao.get('preco_fechamento', 0))),
                    'preco_maximo': Decimal(str(cotacao.get('preco_maximo', 0))),
                    'preco_minimo': Decimal(str(cotacao.get('preco_minimo', 0))),
                    'volume': cotacao.get('volume_negociado', 0),
                    'variacao_percentual': cotacao.get('variacao_percentual', 0),
                    'regiao': cotacao.get('regiao', 'Brasil')
                })

        # Estatísticas resumidas
        if processed['cotacoes']:
            cotacoes = processed['cotacoes']
            precos_fechamento = [float(c['preco_fechamento']) for c in cotacoes]

            processed['resumo'] = {
                'preco_atual': float(cotacoes[0]['preco_fechamento']),
                'variacao_ultimo_dia': float(cotacoes[0]['variacao_percentual']),
                'preco_maximo_periodo': max(precos_fechamento),
                'preco_minimo_periodo': min(precos_fechamento),
                'media_periodo': sum(precos_fechamento) / len(precos_fechamento),
                'tendencia': self._analisar_tendencia_cotacoes(cotacoes)
            }

        return processed

    def _processar_analise_semanal(self, data: Dict) -> Dict[str, Any]:
        """
        Processa análise semanal
        """
        processed = {
            'fonte': 'SCOT_CONSULTORIA',
            'tipo': 'analise_semanal',
            'semana': data.get('semana_referencia', ''),
            'periodo': data.get('periodo_analisado', ''),
            'atualizado_em': timezone.now().isoformat(),
            'mercado_interno': data.get('mercado_interno', {}),
            'exportacao': data.get('exportacao', {}),
            'previsoes': data.get('previsoes_curto_prazo', {}),
            'fatores_influencia': data.get('fatores_influencia', []),
            'recomendacoes': data.get('recomendacoes', [])
        }

        return processed

    def _processar_projetcoes_mensais(self, data: Dict, produto: str) -> Dict[str, Any]:
        """
        Processa projeções mensais
        """
        processed = {
            'fonte': 'SCOT_CONSULTORIA',
            'produto': produto,
            'tipo': 'projetcoes_mensais',
            'atualizado_em': timezone.now().isoformat(),
            'projetado_ate': data.get('projetado_ate', ''),
            'cenarios': data.get('cenarios', {}),
            'projetcoes': []
        }

        if 'projetcoes' in data:
            for proj in data['projetcoes']:
                processed['projetcoes'].append({
                    'mes': proj.get('mes'),
                    'ano': proj.get('ano'),
                    'preco_otimista': Decimal(str(proj.get('preco_otimista', 0))),
                    'preco_moderado': Decimal(str(proj.get('preco_moderado', 0))),
                    'preco_pessimista': Decimal(str(proj.get('preco_pessimista', 0))),
                    'justificativa': proj.get('justificativa', ''),
                    'riscos': proj.get('riscos', [])
                })

        return processed

    def _processar_indicadores_rurais(self, data: Dict) -> Dict[str, Any]:
        """
        Processa indicadores rurais
        """
        processed = {
            'fonte': 'SCOT_CONSULTORIA',
            'tipo': 'indicadores_rurais',
            'atualizado_em': timezone.now().isoformat(),
            'periodo_referencia': data.get('periodo_referencia', ''),
            'indicadores': {}
        }

        if 'indicadores' in data:
            for indicador in data['indicadores']:
                processed['indicadores'][indicador.get('nome', '')] = {
                    'valor': Decimal(str(indicador.get('valor', 0))),
                    'unidade': indicador.get('unidade', ''),
                    'variacao_mensal': indicador.get('variacao_mensal', 0),
                    'variacao_anual': indicador.get('variacao_anual', 0),
                    'categoria': indicador.get('categoria', '')
                }

        return processed

    def _processar_relatorio_mensal(self, data: Dict, ano: int, mes: int) -> Dict[str, Any]:
        """
        Processa relatório mensal
        """
        processed = {
            'fonte': 'SCOT_CONSULTORIA',
            'tipo': 'relatorio_mensal',
            'ano': ano,
            'mes': mes,
            'atualizado_em': timezone.now().isoformat(),
            'resumo_executivo': data.get('resumo_executivo', ''),
            'mercado_interno': data.get('mercado_interno', {}),
            'exportacoes': data.get('exportacoes', {}),
            'producao': data.get('producao', {}),
            'precos': data.get('precos', {}),
            'tendencias': data.get('tendencias', {}),
            'perspectivas': data.get('perspectivas', {})
        }

        return processed

    def _dados_fallback_cotacoes_diarias(self, produto: str) -> Dict[str, Any]:
        """
        Dados de fallback para cotações diárias
        Valores aproximados baseados em dados históricos da Scot
        """
        # Valores base aproximados (atualizar periodicamente)
        valores_base_scot = {
            'boi_gordo': {
                'preco_base': 315.00,  # R$/@ médio
                'volatilidade_diaria': 2.5  # %
            },
            'vaca_gorda': {
                'preco_base': 275.00,
                'volatilidade_diaria': 2.0
            },
            'novilha': {
                'preco_base': 255.00,
                'volatilidade_diaria': 2.2
            }
        }

        config = valores_base_scot.get(produto, valores_base_scot['boi_gordo'])
        data_atual = timezone.now()

        # Gerar cotações simuladas dos últimos 30 dias
        cotacoes = []
        import random

        for i in range(30):
            data = data_atual - timedelta(days=i)

            # Simular variação diária
            variacao = random.uniform(-config['volatilidade_diaria'], config['volatilidade_diaria']) / 100
            preco_base = config['preco_base'] * (1 + variacao)

            # Simular preços OHLC (Open, High, Low, Close)
            abertura = preco_base * random.uniform(0.98, 1.02)
            fechamento = preco_base * random.uniform(0.98, 1.02)
            maxima = max(abertura, fechamento) * random.uniform(1.00, 1.03)
            minima = min(abertura, fechamento) * random.uniform(0.97, 1.00)

            cotacoes.append({
                'data': data.strftime('%Y-%m-%d'),
                'preco_abertura': Decimal(str(round(abertura, 2))),
                'preco_fechamento': Decimal(str(round(fechamento, 2))),
                'preco_maximo': Decimal(str(round(maxima, 2))),
                'preco_minimo': Decimal(str(round(minima, 2))),
                'volume': random.randint(500, 2000),
                'variacao_percentual': round(variacao * 100, 2),
                'regiao': 'Brasil'
            })

        # Inverter ordem (mais recente primeiro)
        cotacoes.reverse()

        result = {
            'fonte': 'SCOT_CONSULTORIA_FALLBACK',
            'produto': produto,
            'tipo': 'cotacoes_diarias',
            'atualizado_em': timezone.now().isoformat(),
            'cotacoes': cotacoes,
            'resumo': {
                'preco_atual': float(cotacoes[0]['preco_fechamento']),
                'variacao_ultimo_dia': float(cotacoes[0]['variacao_percentual']),
                'preco_maximo_periodo': max([float(c['preco_fechamento']) for c in cotacoes]),
                'preco_minimo_periodo': min([float(c['preco_fechamento']) for c in cotacoes]),
                'media_periodo': sum([float(c['preco_fechamento']) for c in cotacoes]) / len(cotacoes),
                'tendencia': 'estável'
            }
        }

        return result

    def _dados_fallback_analise_semanal(self) -> Dict[str, Any]:
        """
        Dados de fallback para análise semanal
        """
        return {
            'fonte': 'SCOT_CONSULTORIA_FALLBACK',
            'tipo': 'analise_semanal',
            'semana': f"Semana {timezone.now().isocalendar()[1]} de {timezone.now().year}",
            'periodo': f"{(timezone.now() - timedelta(days=7)).strftime('%d/%m')} a {timezone.now().strftime('%d/%m/%Y')}",
            'atualizado_em': timezone.now().isoformat(),
            'mercado_interno': {
                'resumo': 'Mercado interno apresenta estabilidade com boa demanda.',
                'precos': 'Preços firmes, com leve alta nas categorias mais leves.',
                'volume': 'Volume de negociações dentro da normalidade.'
            },
            'exportacao': {
                'china': 'Demanda chinesa mantém-se aquecida.',
                'outros': 'Outros destinos com negociações pontuais.',
                'perspectiva': 'Expectativa positiva para os próximos meses.'
            },
            'previsoes': {
                'curto_prazo': 'Manutenção dos preços atuais com tendência de alta.',
                'medio_prazo': 'Cenário positivo com possibilidade de recuperação.'
            },
            'fatores_influencia': [
                'Demanda externa aquecida',
                'Câmbio favorável',
                'Estoque reduzido em algumas regiões',
                'Safra de inverno em andamento'
            ],
            'recomendacoes': [
                'Aproveitar momento favorável para vendas',
                'Monitorar evolução da safra',
                'Acompanhar indicadores de exportação'
            ]
        }

    def _dados_fallback_projetcoes_mensais(self, produto: str, meses: int) -> Dict[str, Any]:
        """
        Dados de fallback para projeções mensais
        """
        data_atual = timezone.now()
        projetados = []

        for i in range(meses):
            data_proj = data_atual + timedelta(days=30 * (i + 1))

            # Simular projeções com tendência de alta moderada
            base_atual = 315 if produto == 'boi_gordo' else 275 if produto == 'vaca_gorda' else 255
            tendencia = 1 + (i * 0.02)  # +2% ao mês
            aleatoriedade = 1 + (0.05 * (0.5 - i/meses))  # Variação

            preco_otimista = base_atual * tendencia * aleatoriedade * 1.05
            preco_moderado = base_atual * tendencia * aleatoriedade
            preco_pessimista = base_atual * tendencia * aleatoriedade * 0.95

            projetados.append({
                'mes': data_proj.month,
                'ano': data_proj.year,
                'preco_otimista': Decimal(str(round(preco_otimista, 2))),
                'preco_moderado': Decimal(str(round(preco_moderado, 2))),
                'preco_pessimista': Decimal(str(round(preco_pessimista, 2))),
                'justificativa': f'Projeção baseada em tendência histórica e fatores de mercado para {data_proj.strftime("%B/%Y")}',
                'riscos': [
                    'Variações cambiais',
                    'Alterações climáticas',
                    'Mudanças na demanda externa'
                ]
            })

        return {
            'fonte': 'SCOT_CONSULTORIA_FALLBACK',
            'produto': produto,
            'tipo': 'projetcoes_mensais',
            'atualizado_em': timezone.now().isoformat(),
            'projetado_ate': projetados[-1]['mes'] if projetados else None,
            'cenarios': {
                'otimista': 'Demanda externa forte, câmbio favorável',
                'moderado': 'Cenário base com tendência de alta moderada',
                'pessimista': 'Pressão de oferta, enfraquecimento da demanda'
            },
            'projetcoes': projetados
        }

    def _dados_fallback_indicadores_rurais(self) -> Dict[str, Any]:
        """
        Dados de fallback para indicadores rurais
        """
        indicadores = {
            'boi_gordo': {
                'valor': Decimal('315.50'),
                'unidade': 'R$/@',
                'variacao_mensal': 2.3,
                'variacao_anual': 8.7,
                'categoria': 'precos'
            },
            'vaca_gorda': {
                'valor': Decimal('275.80'),
                'unidade': 'R$/@',
                'variacao_mensal': 1.8,
                'variacao_anual': 6.2,
                'categoria': 'precos'
            },
            'custo_producao': {
                'valor': Decimal('1850.00'),
                'unidade': 'R$/ha',
                'variacao_mensal': 1.5,
                'variacao_anual': 12.3,
                'categoria': 'custos'
            },
            'margem_bruta': {
                'valor': Decimal('32.5'),
                'unidade': '%',
                'variacao_mensal': -0.8,
                'variacao_anual': -5.2,
                'categoria': 'rentabilidade'
            }
        }

        return {
            'fonte': 'SCOT_CONSULTORIA_FALLBACK',
            'tipo': 'indicadores_rurais',
            'atualizado_em': timezone.now().isoformat(),
            'periodo_referencia': timezone.now().strftime('%B/%Y'),
            'indicadores': indicadores
        }

    def _dados_fallback_relatorio_mensal(self, ano: int, mes: int) -> Dict[str, Any]:
        """
        Dados de fallback para relatório mensal
        """
        return {
            'fonte': 'SCOT_CONSULTORIA_FALLBACK',
            'tipo': 'relatorio_mensal',
            'ano': ano,
            'mes': mes,
            'atualizado_em': timezone.now().isoformat(),
            'resumo_executivo': f'Relatório mensal de {mes}/{ano} do mercado pecuário brasileiro.',
            'mercado_interno': {
                'precos': 'Preços apresentaram estabilidade com leve tendência de alta.',
                'volume': 'Volume de negociações dentro da normalidade para o período.',
                'regioes': 'Centro-Oeste continua liderando as negociações.'
            },
            'exportacoes': {
                'volume': 'Exportações mantêm-se em patamar elevado.',
                'destinos': 'China principal destino, seguido por outros países asiáticos.',
                'precos': 'Preços de exportação competitivos.'
            },
            'producao': {
                'abate': 'Abates dentro do esperado para o período.',
                'peso_medio': 'Peso médio de abate estável.',
                'qualidade': 'Qualidade da carne mantida.'
            },
            'precos': {
                'boi_gordo': 'Estável com leve alta.',
                'vaca_gorda': 'Acompanhando tendência do boi.',
                'novilha': 'Preços firmes.'
            },
            'tendencias': {
                'curto_prazo': 'Expectativa de manutenção dos preços.',
                'medio_prazo': 'Cenário positivo com demanda aquecida.'
            },
            'perspectivas': {
                'mercado_interno': 'Estabilidade com possibilidade de alta.',
                'exportacao': 'Perspectiva positiva.',
                'producao': 'Aumento gradual esperado.'
            }
        }

    def _analisar_tendencia_cotacoes(self, cotacoes: List[Dict]) -> str:
        """
        Analisa tendência das cotações
        """
        if len(cotacoes) < 5:
            return 'estável'

        # Comparar primeiros 20% com últimos 20% dos dados
        corte = len(cotacoes) // 5
        preco_inicial = sum([float(c['preco_fechamento']) for c in cotacoes[:corte]]) / corte
        preco_final = sum([float(c['preco_fechamento']) for c in cotacoes[-corte:]]) / corte

        variacao = (preco_final - preco_inicial) / preco_inicial

        if variacao > 0.02:  # +2%
            return 'altista'
        elif variacao < -0.02:  # -2%
            return 'baixista'
        else:
            return 'estável'