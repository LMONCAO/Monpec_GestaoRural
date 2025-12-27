"""
Views para IA de Chat de Planejamento
Sistema de chat que guia o usuário na criação de planejamentos através de perguntas e respostas
"""

import json
import logging
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction

from .decorators import obter_propriedade_com_permissao
from .models import (
    Propriedade,
    PlanejamentoAnual,
    CategoriaAnimal,
    AtividadePlanejada,
    MetaComercialPlanejada,
    MetaFinanceiraPlanejada,
    IndicadorPlanejado,
    CenarioPlanejamento,
)
from .services.ia_planejamento_avancada import IAPlanejamentoAvancada

logger = logging.getLogger(__name__)


class PlanejamentoIAChat:
    """
    Classe que gerencia o fluxo de conversa da IA para criação de planejamento
    Agora com IA avançada que aprende e pesquisa informações
    """
    
    def __init__(self, propriedade_id, ano=None, carregar_analise_ia=True):
        self.propriedade_id = propriedade_id
        self.ano = ano or timezone.now().year
        self.etapa_atual = 0
        self.dados_coletados = {
            'ano': self.ano,
            'descricao': '',
            'metas_comerciais': [],
            'metas_financeiras': [],
            'atividades': [],
            'indicadores': [],
        }
        
        # Inicializar IA avançada
        try:
            propriedade = Propriedade.objects.get(id=propriedade_id)
            self.ia_avancada = IAPlanejamentoAvancada(propriedade)
            self.analise_ia = None  # Será preenchida quando necessário
        except Propriedade.DoesNotExist:
            self.ia_avancada = None
            self.analise_ia = None
        except Exception as e:
            logger.warning(f'Erro ao inicializar IA avançada: {e}')
            self.ia_avancada = None
            self.analise_ia = None
        
        # Buscar análise da IA antes de começar (não crítico se falhar)
        # Só carregar se solicitado (evitar recarregar quando recriando chat)
        if carregar_analise_ia:
            try:
                self._carregar_analise_ia()
            except Exception as e:
                logger.warning(f'Erro ao carregar análise inicial da IA: {e}')
                self.analise_ia = None
        
        # Fluxo de perguntas (agora com insights da IA)
        self.perguntas = [
            {
                'id': 'ano',
                'pergunta': self._gerar_pergunta_com_insight(
                    f'Para qual ano você deseja criar o planejamento? (Atual: {self.ano})',
                    'ano'
                ),
                'tipo': 'numero',
                'opcional': True,
                'default': str(self.ano),
            },
            {
                'id': 'descricao',
                'pergunta': 'Qual é a descrição ou objetivo principal deste planejamento?',
                'tipo': 'texto',
                'opcional': True,
            },
            {
                'id': 'meta_comercial_inicio',
                'pergunta': 'Vamos começar com as metas comerciais. Você tem metas de vendas para este ano? (sim/não)',
                'tipo': 'sim_nao',
            },
            {
                'id': 'meta_comercial_categoria',
                'pergunta': 'Qual categoria de animal você planeja vender? (ex: Boi, Novilho, Garrote)',
                'tipo': 'categoria',
                'condicao': 'se_meta_comercial',
            },
            {
                'id': 'meta_comercial_quantidade',
                'pergunta': 'Quantos animais desta categoria você planeja vender?',
                'tipo': 'numero',
                'condicao': 'se_meta_comercial',
            },
            {
                'id': 'meta_comercial_preco',
                'pergunta': self._gerar_pergunta_com_insight(
                    'Qual o preço médio esperado por cabeça ou arroba? (R$)',
                    'preco'
                ),
                'tipo': 'decimal',
                'condicao': 'se_meta_comercial',
            },
            {
                'id': 'meta_comercial_mais',
                'pergunta': 'Deseja adicionar outra meta comercial? (sim/não)',
                'tipo': 'sim_nao',
                'condicao': 'se_meta_comercial',
            },
            {
                'id': 'meta_financeira_inicio',
                'pergunta': 'Agora vamos para as metas financeiras. Você tem custos ou investimentos planejados? (sim/não)',
                'tipo': 'sim_nao',
            },
            {
                'id': 'meta_financeira_tipo',
                'pergunta': 'Qual o tipo de custo? (Fixo, Variável, Investimento, Taxas, Outros)',
                'tipo': 'opcoes',
                'opcoes': ['FIXO', 'VARIAVEL', 'INVESTIMENTO', 'TAXA', 'OUTROS'],
                'condicao': 'se_meta_financeira',
            },
            {
                'id': 'meta_financeira_descricao',
                'pergunta': 'Descreva este custo ou investimento:',
                'tipo': 'texto',
                'condicao': 'se_meta_financeira',
            },
            {
                'id': 'meta_financeira_valor',
                'pergunta': 'Qual o valor anual previsto? (R$)',
                'tipo': 'decimal',
                'condicao': 'se_meta_financeira',
            },
            {
                'id': 'meta_financeira_mais',
                'pergunta': 'Deseja adicionar outra meta financeira? (sim/não)',
                'tipo': 'sim_nao',
                'condicao': 'se_meta_financeira',
            },
            {
                'id': 'atividade_inicio',
                'pergunta': 'Agora vamos para as metas financeiras. Você tem custos ou investimentos planejados? (sim/não)',
                'tipo': 'sim_nao',
            },
            {
                'id': 'meta_financeira_tipo',
                'pergunta': 'Qual o tipo de custo? (Fixo, Variável, Investimento, Taxas, Outros)',
                'tipo': 'opcoes',
                'opcoes': ['FIXO', 'VARIAVEL', 'INVESTIMENTO', 'TAXA', 'OUTROS'],
                'condicao': 'se_meta_financeira',
            },
            {
                'id': 'meta_financeira_descricao',
                'pergunta': 'Descreva este custo ou investimento:',
                'tipo': 'texto',
                'condicao': 'se_meta_financeira',
            },
            {
                'id': 'meta_financeira_valor',
                'pergunta': 'Qual o valor anual previsto? (R$)',
                'tipo': 'decimal',
                'condicao': 'se_meta_financeira',
            },
            {
                'id': 'atividade_inicio',
                'pergunta': 'Você tem atividades operacionais planejadas? (sim/não)',
                'tipo': 'sim_nao',
            },
            {
                'id': 'atividade_tipo',
                'pergunta': 'Qual o tipo de atividade? (ex: Vacinação, IATF, Desmama, Venda)',
                'tipo': 'texto',
                'condicao': 'se_atividade',
            },
            {
                'id': 'atividade_data',
                'pergunta': 'Quando esta atividade deve ocorrer? (DD/MM/AAAA)',
                'tipo': 'data',
                'condicao': 'se_atividade',
            },
            {
                'id': 'atividade_mais',
                'pergunta': 'Deseja adicionar outra atividade? (sim/não)',
                'tipo': 'sim_nao',
                'condicao': 'se_atividade',
            },
            {
                'id': 'indicador_inicio',
                'pergunta': 'Por fim, você tem indicadores de desempenho que deseja acompanhar? (sim/não)',
                'tipo': 'sim_nao',
            },
            {
                'id': 'indicador_nome',
                'pergunta': 'Qual indicador? (ex: Taxa de Natalidade, Taxa de Mortalidade, Ganho de Peso)',
                'tipo': 'texto',
                'condicao': 'se_indicador',
            },
            {
                'id': 'indicador_valor',
                'pergunta': 'Qual a meta para este indicador?',
                'tipo': 'decimal',
                'condicao': 'se_indicador',
            },
            {
                'id': 'indicador_unidade',
                'pergunta': 'Qual a unidade? (%, kg, cabeças, etc)',
                'tipo': 'texto',
                'condicao': 'se_indicador',
            },
            {
                'id': 'indicador_mais',
                'pergunta': 'Deseja adicionar outro indicador? (sim/não)',
                'tipo': 'sim_nao',
                'condicao': 'se_indicador',
            },
            {
                'id': 'finalizar',
                'pergunta': 'Perfeito! Deseja criar o planejamento agora? (sim/não)',
                'tipo': 'sim_nao',
            },
            ]
    
    def _carregar_analise_ia(self):
        """
        Carrega a análise da IA avançada para usar nos insights
        """
        try:
            if self.ia_avancada:
                # Buscar planejamento existente para o ano (se houver)
                planejamento = None
                try:
                    propriedade = Propriedade.objects.get(id=self.propriedade_id)
                    planejamento = PlanejamentoAnual.objects.filter(
                        propriedade=propriedade,
                        ano=self.ano
                    ).first()
                except:
                    pass
                
                # Carregar análise da IA
                self.analise_ia = self.ia_avancada.analisar_planejamento_com_ia(
                    planejamento=planejamento,
                    incluir_pesquisa_web=True
                )
            else:
                self.analise_ia = None
        except Exception as e:
            logger.error(f'Erro ao carregar análise da IA: {e}', exc_info=True)
            self.analise_ia = None
    
    def _gerar_pergunta_com_insight(self, pergunta_base: str, tipo_insight: str) -> str:
        """
        Gera uma pergunta enriquecida com insights da IA
        """
        if not self.analise_ia or not self.analise_ia.get('sucesso'):
            return pergunta_base
        
        insight_texto = ""
        
        try:
            if tipo_insight == 'ano':
                # Insights sobre o ano do planejamento
                insights = self.analise_ia.get('insights', [])
                if insights:
                    insight_texto = f" ({insights[0] if insights else ''})"
            
            elif tipo_insight == 'preco':
                # Insights sobre preços de mercado
                dados_mercado = self.analise_ia.get('dados_mercado', {})
                precos = dados_mercado.get('precos_mercado', {})
                if precos:
                    # Pegar o primeiro preço disponível como exemplo
                    primeiro_preco = list(precos.values())[0] if precos else {}
                    if isinstance(primeiro_preco, dict) and 'preco_arroba' in primeiro_preco:
                        preco_ref = primeiro_preco['preco_arroba']
                        insight_texto = f" (Preço de mercado de referência: R$ {preco_ref:.2f}/arroba)"
        except Exception as e:
            logger.debug(f'Erro ao gerar insight: {e}')
        
        return pergunta_base + insight_texto
    
    def obter_recomendacoes_inteligentes(self):
        """
        Retorna recomendações inteligentes da IA
        """
        if not self.analise_ia or not self.analise_ia.get('sucesso'):
            return []
        
        return self.analise_ia.get('recomendacoes', [])
    
    def obter_insights_gerais(self):
        """
        Retorna insights gerais da IA
        """
        if not self.analise_ia or not self.analise_ia.get('sucesso'):
            return []
        
        return self.analise_ia.get('insights', [])
    
    def processar_resposta(self, resposta, contexto_anterior=None):
        """
        Processa a resposta do usuário e retorna a próxima pergunta
        """
        if self.etapa_atual >= len(self.perguntas):
            return {
                'tipo': 'finalizado',
                'mensagem': 'Planejamento concluído!',
                'dados': self.dados_coletados,
            }
        
        pergunta_atual = self.perguntas[self.etapa_atual]
        
        # Verificar condições
        if 'condicao' in pergunta_atual:
            if not self._verificar_condicao(pergunta_atual['condicao']):
                self.etapa_atual += 1
                return self.processar_resposta('', contexto_anterior)
        
        # Processar resposta
        resposta_processada, mensagem_erro = self._processar_resposta_tipo(resposta, pergunta_atual)
        
        # Se houver erro na validação, retornar mensagem de erro sem avançar
        if mensagem_erro:
            return {
                'tipo': 'erro_validacao',
                'pergunta': pergunta_atual['pergunta'],
                'mensagem_erro': mensagem_erro,
                'tipo_resposta': pergunta_atual['tipo'],
                'opcoes': pergunta_atual.get('opcoes', []),
                'etapa': self.etapa_atual + 1,
                'total': len(self.perguntas),
            }
        
        if resposta_processada is not None:
            # Salvar resposta nos dados coletados
            self._salvar_resposta(pergunta_atual['id'], resposta_processada)
            
            # Verificar se precisa voltar para adicionar mais itens
            if pergunta_atual['id'] == 'meta_comercial_mais' and resposta_processada:
                # Voltar para pergunta de categoria
                self.etapa_atual = self._encontrar_indice_pergunta('meta_comercial_categoria')
            elif pergunta_atual['id'] == 'meta_financeira_mais' and resposta_processada:
                # Voltar para pergunta de tipo
                self.etapa_atual = self._encontrar_indice_pergunta('meta_financeira_tipo')
            elif pergunta_atual['id'] == 'atividade_mais' and resposta_processada:
                # Voltar para pergunta de tipo
                self.etapa_atual = self._encontrar_indice_pergunta('atividade_tipo')
            elif pergunta_atual['id'] == 'indicador_mais' and resposta_processada:
                # Voltar para pergunta de nome
                self.etapa_atual = self._encontrar_indice_pergunta('indicador_nome')
            else:
                # Avançar para próxima pergunta normalmente
                self.etapa_atual += 1
        else:
            # Se resposta não foi processada e não há erro, avançar mesmo assim (caso opcional)
            if pergunta_atual.get('opcional'):
                self.etapa_atual += 1
            else:
                # Se não é opcional e não foi processada, retornar erro
                return {
                    'tipo': 'erro_validacao',
                    'pergunta': pergunta_atual['pergunta'],
                    'mensagem_erro': 'Por favor, forneça uma resposta válida.',
                    'tipo_resposta': pergunta_atual['tipo'],
                    'opcoes': pergunta_atual.get('opcoes', []),
                    'etapa': self.etapa_atual + 1,
                    'total': len(self.perguntas),
                }
        
        # Buscar próxima pergunta válida
        while self.etapa_atual < len(self.perguntas):
            proxima_pergunta = self.perguntas[self.etapa_atual]
            
            # Verificar condições
            if 'condicao' in proxima_pergunta:
                if not self._verificar_condicao(proxima_pergunta['condicao']):
                    self.etapa_atual += 1
                    continue
            
            # Pergunta válida encontrada
            break
        
        if self.etapa_atual >= len(self.perguntas):
            return {
                'tipo': 'finalizar',
                'mensagem': 'Deseja criar o planejamento agora?',
                'dados': self.dados_coletados,
            }
        
        proxima_pergunta = self.perguntas[self.etapa_atual]
        
        return {
            'tipo': 'pergunta',
            'pergunta': proxima_pergunta['pergunta'],
            'tipo_resposta': proxima_pergunta['tipo'],
            'opcoes': proxima_pergunta.get('opcoes', []),
            'etapa': self.etapa_atual + 1,
            'total': len(self.perguntas),
        }
    
    def _encontrar_indice_pergunta(self, pergunta_id):
        """Encontra o índice de uma pergunta pelo ID"""
        for i, pergunta in enumerate(self.perguntas):
            if pergunta['id'] == pergunta_id:
                return i
        return len(self.perguntas)  # Se não encontrar, retorna o final
    
    def _verificar_condicao(self, condicao):
        """Verifica se a condição para fazer a pergunta foi atendida"""
        if condicao == 'se_meta_comercial':
            return self.dados_coletados.get('tem_meta_comercial', False)
        elif condicao == 'se_meta_financeira':
            return self.dados_coletados.get('tem_meta_financeira', False)
        elif condicao == 'se_atividade':
            return self.dados_coletados.get('tem_atividade', False)
        elif condicao == 'se_indicador':
            return self.dados_coletados.get('tem_indicador', False)
        return True
    
    def _processar_resposta_tipo(self, resposta, pergunta):
        """
        Processa a resposta de acordo com o tipo esperado
        Retorna: (valor_processado, mensagem_erro) onde mensagem_erro é None se sucesso
        """
        resposta = resposta.strip()
        
        if pergunta['tipo'] == 'sim_nao':
            if resposta.lower() in ['sim', 's', 'yes', 'y']:
                return (True, None)
            elif resposta.lower() in ['não', 'nao', 'n', 'no']:
                return (False, None)
            return (None, 'Por favor, responda apenas com "sim" ou "não" (ou "s"/"n").')
        
        elif pergunta['tipo'] == 'numero':
            if not resposta:
                if pergunta.get('opcional'):
                    default = pergunta.get('default')
                    if default:
                        try:
                            return (int(default), None)
                        except:
                            return (None, None)
                    return (None, None)
                return (None, 'Por favor, informe um número (exemplo: 100, 250, 500).')
            try:
                valor = int(resposta)
                if valor < 0:
                    return (None, 'Por favor, informe um número positivo (exemplo: 100, 250, 500).')
                return (valor, None)
            except ValueError:
                exemplo = pergunta.get('default', '2025')
                return (None, f'Por favor, informe apenas números (exemplo: {exemplo}).')
        
        elif pergunta['tipo'] == 'decimal':
            if not resposta:
                return (None, 'Por favor, informe um valor (exemplo: 2500.00 ou 2.500,00).')
            try:
                # Remover R$ e espaços
                resposta_limpa = resposta.replace('R$', '').replace('$', '').strip()
                # Tentar diferentes formatos
                if ',' in resposta_limpa and '.' in resposta_limpa:
                    # Formato: 1.234,56 ou 1,234.56
                    if resposta_limpa.rindex(',') > resposta_limpa.rindex('.'):
                        # 1.234,56 (padrão brasileiro)
                        resposta_limpa = resposta_limpa.replace('.', '').replace(',', '.')
                    else:
                        # 1,234.56 (padrão americano)
                        resposta_limpa = resposta_limpa.replace(',', '')
                elif ',' in resposta_limpa:
                    # Formato: 234,56
                    resposta_limpa = resposta_limpa.replace(',', '.')
                else:
                    # Já está no formato correto
                    pass
                
                valor = Decimal(resposta_limpa)
                if valor < 0:
                    return (None, 'Por favor, informe um valor positivo (exemplo: 2500.00 ou R$ 2.500,00).')
                return (valor, None)
            except (ValueError, InvalidOperation):
                return (None, 'Formato inválido. Informe um valor numérico (exemplo: 2500.00 ou R$ 2.500,00).')
        
        elif pergunta['tipo'] == 'data':
            if not resposta:
                return (None, 'Por favor, informe uma data (exemplo: 15/03/2025 ou 15-03-2025).')
            try:
                # Tentar formatos DD/MM/AAAA ou DD-MM-AAAA
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y', '%d-%m-%y']:
                    try:
                        return (datetime.strptime(resposta, fmt).date(), None)
                    except:
                        continue
                return (None, 'Formato de data inválido. Use o formato DD/MM/AAAA (exemplo: 15/03/2025).')
            except Exception:
                return (None, 'Data inválida. Use o formato DD/MM/AAAA (exemplo: 15/03/2025).')
        
        elif pergunta['tipo'] == 'categoria':
            if not resposta:
                return (None, 'Por favor, informe o nome de uma categoria (exemplo: Boi, Novilho, Garrote).')
            # Buscar categoria no banco
            try:
                categoria = CategoriaAnimal.objects.filter(
                    nome__icontains=resposta
                ).first()
                if categoria:
                    return (categoria.id, None)
                else:
                    # Tentar buscar categorias disponíveis para sugerir
                    categorias_disponiveis = CategoriaAnimal.objects.filter(ativo=True).values_list('nome', flat=True)[:5]
                    sugestoes = ', '.join(categorias_disponiveis)
                    return (None, f'Categoria não encontrada. Categorias disponíveis: {sugestoes}.')
            except Exception:
                return (None, 'Erro ao buscar categoria. Por favor, tente novamente.')
        
        elif pergunta['tipo'] == 'opcoes':
            if not resposta:
                opcoes_str = ', '.join(pergunta.get('opcoes', []))
                return (None, f'Por favor, escolha uma das opções: {opcoes_str}.')
            # Verificar se resposta está nas opções
            resposta_upper = resposta.upper()
            for opcao in pergunta.get('opcoes', []):
                if opcao.upper() == resposta_upper or opcao.upper().startswith(resposta_upper[:2]):
                    return (opcao, None)
            opcoes_str = ', '.join(pergunta.get('opcoes', []))
            return (None, f'Opção inválida. Escolha uma das opções: {opcoes_str}.')
        
        else:  # texto
            if not resposta and not pergunta.get('opcional'):
                return (None, 'Por favor, informe uma resposta.')
            return (resposta if resposta else None, None)
    
    def _salvar_resposta(self, pergunta_id, resposta):
        """Salva a resposta nos dados coletados"""
        if pergunta_id == 'ano' and resposta:
            self.dados_coletados['ano'] = resposta
            self.ano = resposta
        
        elif pergunta_id == 'descricao':
            self.dados_coletados['descricao'] = resposta or f'Planejamento {self.ano}'
        
        elif pergunta_id == 'meta_comercial_inicio':
            self.dados_coletados['tem_meta_comercial'] = resposta
        
        elif pergunta_id == 'meta_comercial_categoria' and resposta:
            if not self.dados_coletados.get('meta_comercial_atual'):
                self.dados_coletados['meta_comercial_atual'] = {}
            self.dados_coletados['meta_comercial_atual']['categoria_id'] = resposta
        
        elif pergunta_id == 'meta_comercial_quantidade' and resposta:
            if not self.dados_coletados.get('meta_comercial_atual'):
                self.dados_coletados['meta_comercial_atual'] = {}
            self.dados_coletados['meta_comercial_atual']['quantidade'] = resposta
        
        elif pergunta_id == 'meta_comercial_preco' and resposta:
            if not self.dados_coletados.get('meta_comercial_atual'):
                self.dados_coletados['meta_comercial_atual'] = {}
            self.dados_coletados['meta_comercial_atual']['preco'] = resposta
            # Finalizar meta comercial atual
            if self.dados_coletados.get('meta_comercial_atual') and self.dados_coletados['meta_comercial_atual'].get('categoria_id'):
                self.dados_coletados['metas_comerciais'].append(
                    self.dados_coletados['meta_comercial_atual'].copy()
                )
                self.dados_coletados['meta_comercial_atual'] = {}
        
        elif pergunta_id == 'meta_financeira_inicio':
            self.dados_coletados['tem_meta_financeira'] = resposta
        
        elif pergunta_id == 'meta_financeira_tipo' and resposta:
            if not self.dados_coletados.get('meta_financeira_atual'):
                self.dados_coletados['meta_financeira_atual'] = {}
            self.dados_coletados['meta_financeira_atual']['tipo'] = resposta
        
        elif pergunta_id == 'meta_financeira_descricao' and resposta:
            if not self.dados_coletados.get('meta_financeira_atual'):
                self.dados_coletados['meta_financeira_atual'] = {}
            self.dados_coletados['meta_financeira_atual']['descricao'] = resposta
        
        elif pergunta_id == 'meta_financeira_valor' and resposta:
            if not self.dados_coletados.get('meta_financeira_atual'):
                self.dados_coletados['meta_financeira_atual'] = {}
            self.dados_coletados['meta_financeira_atual']['valor'] = resposta
            # Finalizar meta financeira atual
            if self.dados_coletados.get('meta_financeira_atual'):
                self.dados_coletados['metas_financeiras'].append(
                    self.dados_coletados['meta_financeira_atual'].copy()
                )
                self.dados_coletados['meta_financeira_atual'] = {}
        
        elif pergunta_id == 'atividade_inicio':
            self.dados_coletados['tem_atividade'] = resposta
        
        elif pergunta_id == 'atividade_tipo' and resposta:
            if not self.dados_coletados.get('atividade_atual'):
                self.dados_coletados['atividade_atual'] = {}
            self.dados_coletados['atividade_atual']['tipo'] = resposta
        
        elif pergunta_id == 'atividade_data' and resposta:
            if not self.dados_coletados.get('atividade_atual'):
                self.dados_coletados['atividade_atual'] = {}
            self.dados_coletados['atividade_atual']['data'] = resposta
            # Finalizar atividade atual
            if self.dados_coletados.get('atividade_atual'):
                self.dados_coletados['atividades'].append(
                    self.dados_coletados['atividade_atual'].copy()
                )
                self.dados_coletados['atividade_atual'] = {}
        
        elif pergunta_id == 'indicador_inicio':
            self.dados_coletados['tem_indicador'] = resposta
        
        elif pergunta_id == 'indicador_nome' and resposta:
            if not self.dados_coletados.get('indicador_atual'):
                self.dados_coletados['indicador_atual'] = {}
            self.dados_coletados['indicador_atual']['nome'] = resposta
        
        elif pergunta_id == 'indicador_valor' and resposta:
            if not self.dados_coletados.get('indicador_atual'):
                self.dados_coletados['indicador_atual'] = {}
            self.dados_coletados['indicador_atual']['valor'] = resposta
        
        elif pergunta_id == 'indicador_unidade' and resposta:
            if not self.dados_coletados.get('indicador_atual'):
                self.dados_coletados['indicador_atual'] = {}
            self.dados_coletados['indicador_atual']['unidade'] = resposta
            # Finalizar indicador atual
            if self.dados_coletados.get('indicador_atual') and self.dados_coletados['indicador_atual'].get('nome'):
                self.dados_coletados['indicadores'].append(
                    self.dados_coletados['indicador_atual'].copy()
                )
                self.dados_coletados['indicador_atual'] = {}
        
        elif pergunta_id == 'meta_comercial_mais':
            if resposta:  # Se quer adicionar mais, voltar para categoria
                # Manter tem_meta_comercial = True
                pass
            else:  # Se não quer adicionar mais
                self.dados_coletados['meta_comercial_atual'] = {}  # Limpar estado atual
        
        elif pergunta_id == 'meta_financeira_mais':
            if resposta:  # Se quer adicionar mais, voltar para tipo
                # Manter tem_meta_financeira = True
                pass
            else:  # Se não quer adicionar mais
                self.dados_coletados['meta_financeira_atual'] = {}  # Limpar estado atual
        
        elif pergunta_id == 'atividade_mais':
            if resposta:  # Se quer adicionar mais, voltar para tipo
                # Manter tem_atividade = True
                pass
            else:  # Se não quer adicionar mais
                self.dados_coletados['atividade_atual'] = {}  # Limpar estado atual
        
        elif pergunta_id == 'indicador_mais':
            if resposta:  # Se quer adicionar mais, voltar para nome
                # Manter tem_indicador = True
                pass
            else:  # Se não quer adicionar mais
                self.dados_coletados['indicador_atual'] = {}  # Limpar estado atual
        
        elif pergunta_id == 'meta_financeira_mais':
            if not resposta:  # Se não quer adicionar mais
                self.dados_coletados['meta_financeira_atual'] = {}  # Limpar estado atual
        
        elif pergunta_id == 'atividade_mais':
            if not resposta:  # Se não quer adicionar mais
                self.dados_coletados['atividade_atual'] = {}  # Limpar estado atual
        
        elif pergunta_id == 'indicador_mais':
            if not resposta:  # Se não quer adicionar mais
                self.dados_coletados['indicador_atual'] = {}  # Limpar estado atual
    
    def _converter_dados_para_serializavel(self, dados):
        """
        Converte dados coletados para formato serializável (para salvar na sessão)
        """
        dados_serializavel = {}
        for key, value in dados.items():
            if isinstance(value, Decimal):
                dados_serializavel[key] = float(value)
            elif isinstance(value, date):
                dados_serializavel[key] = value.isoformat()
            elif isinstance(value, dict):
                dados_serializavel[key] = {}
                for k, v in value.items():
                    if isinstance(v, Decimal):
                        dados_serializavel[key][k] = float(v)
                    elif isinstance(v, date):
                        dados_serializavel[key][k] = v.isoformat()
                    else:
                        dados_serializavel[key][k] = v
            elif isinstance(value, list):
                dados_serializavel[key] = []
                for item in value:
                    if isinstance(item, dict):
                        item_serializavel = {}
                        for k, v in item.items():
                            if isinstance(v, Decimal):
                                item_serializavel[k] = float(v)
                            elif isinstance(v, date):
                                item_serializavel[k] = v.isoformat()
                            else:
                                item_serializavel[k] = v
                        dados_serializavel[key].append(item_serializavel)
                    else:
                        dados_serializavel[key].append(item)
            else:
                dados_serializavel[key] = value
        return dados_serializavel
    
    def criar_planejamento(self, propriedade):
        """
        Cria o planejamento com os dados coletados
        """
        try:
            with transaction.atomic():
                # Criar planejamento
                planejamento = PlanejamentoAnual.objects.create(
                    propriedade=propriedade,
                    ano=self.dados_coletados['ano'],
                    descricao=self.dados_coletados.get('descricao') or f'Planejamento {self.ano}',
                    status='RASCUNHO',
                )
                
                # Criar cenário baseline
                CenarioPlanejamento.objects.create(
                    planejamento=planejamento,
                    nome='Baseline / Geral',
                    descricao='Cenário oficial criado via IA.',
                    is_baseline=True,
                    ajuste_preco_percentual=Decimal('0.00'),
                    ajuste_custo_percentual=Decimal('0.00'),
                    ajuste_producao_percentual=Decimal('0.00'),
                )
                
                # Criar metas comerciais
                for meta in self.dados_coletados.get('metas_comerciais', []):
                    categoria = None
                    if meta.get('categoria_id'):
                        try:
                            categoria = CategoriaAnimal.objects.get(id=meta['categoria_id'])
                        except:
                            pass
                    
                    MetaComercialPlanejada.objects.create(
                        planejamento=planejamento,
                        categoria=categoria,
                        quantidade_animais=meta.get('quantidade', 0),
                        preco_medio_esperado=meta.get('preco', Decimal('0.00')),
                        canal_venda='Mercado',
                    )
                
                # Criar metas financeiras
                for meta in self.dados_coletados.get('metas_financeiras', []):
                    MetaFinanceiraPlanejada.objects.create(
                        planejamento=planejamento,
                        descricao=meta.get('descricao', ''),
                        tipo_custo=meta.get('tipo', 'VARIAVEL'),
                        valor_anual_previsto=meta.get('valor', Decimal('0.00')),
                    )
                
                # Criar atividades
                for atividade in self.dados_coletados.get('atividades', []):
                    AtividadePlanejada.objects.create(
                        planejamento=planejamento,
                        tipo_atividade=atividade.get('tipo', ''),
                        data_inicio_prevista=atividade.get('data', date.today()),
                        status='AGENDADA',
                    )
                
                # Criar indicadores
                for indicador in self.dados_coletados.get('indicadores', []):
                    IndicadorPlanejado.objects.create(
                        planejamento=planejamento,
                        nome=indicador.get('nome', ''),
                        valor_meta=indicador.get('valor', Decimal('0.00')),
                        unidade=indicador.get('unidade', ''),
                    )
                
                return planejamento
        except Exception as e:
            logger.error(f'Erro ao criar planejamento: {e}', exc_info=True)
            raise


@login_required
def planejamento_ia_chat(request, propriedade_id):
    """
    View para iniciar o chat de planejamento com IA
    """
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    ano = request.GET.get('ano', timezone.now().year)
    try:
        ano = int(ano)
    except:
        ano = timezone.now().year
    
    # Buscar categorias disponíveis para ajudar nas perguntas
    categorias = CategoriaAnimal.objects.filter(ativo=True).order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'ano': ano,
        'categorias': categorias,
    }
    
    return render(request, 'gestao_rural/planejamento_ia_chat.html', context)


@login_required
@require_http_methods(["POST"])
def planejamento_ia_api(request, propriedade_id):
    """
    API endpoint para processar mensagens do chat
    """
    propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
    
    try:
        data = json.loads(request.body)
        acao = data.get('acao')
        
        if acao == 'iniciar':
            # Iniciar novo chat
            ano = data.get('ano', timezone.now().year)
            chat = PlanejamentoIAChat(propriedade_id, ano)
            
            # Salvar estado na sessão
            request.session[f'planejamento_ia_{propriedade_id}'] = {
                'etapa_atual': chat.etapa_atual,
                'dados_coletados': chat.dados_coletados,
                'ano': chat.ano,
            }
            
            # Primeira pergunta
            primeira_pergunta = chat.perguntas[0] if chat.perguntas else None
            if primeira_pergunta:
                return JsonResponse({
                    'tipo': 'pergunta',
                    'pergunta': primeira_pergunta['pergunta'],
                    'tipo_resposta': primeira_pergunta['tipo'],
                    'opcoes': primeira_pergunta.get('opcoes', []),
                    'etapa': 1,
                    'total': len(chat.perguntas),
                })
        
        elif acao == 'responder':
            # Processar resposta
            resposta = data.get('resposta', '').strip()
            
            # Recuperar estado da sessão
            session_key = f'planejamento_ia_{propriedade_id}'
            estado = request.session.get(session_key)
            
            if not estado:
                return JsonResponse({
                    'erro': 'Sessão expirada. Por favor, inicie novamente.',
                }, status=400)
            
            # Recriar chat com estado salvo (não recarregar análise da IA)
            try:
                chat = PlanejamentoIAChat(propriedade_id, estado.get('ano'), carregar_analise_ia=False)
                chat.etapa_atual = estado.get('etapa_atual', 0)
                # Restaurar dados coletados, convertendo tipos se necessário
                dados_restaurados = estado.get('dados_coletados', {})
                chat.dados_coletados = dados_restaurados
                
                # Não recarregar análise da IA ao recriar (já foi carregada inicialmente)
                # Apenas manter a análise existente se houver
                
                # Verificar se é a pergunta final e resposta é "sim"
                if chat.etapa_atual < len(chat.perguntas):
                    pergunta_atual = chat.perguntas[chat.etapa_atual]
                    if pergunta_atual.get('id') == 'finalizar':
                        resposta_lower = resposta.lower()
                        if resposta_lower in ['sim', 's', 'yes', 'y']:
                            # Criar planejamento diretamente
                            try:
                                planejamento = chat.criar_planejamento(propriedade)
                                del request.session[session_key]
                                return JsonResponse({
                                    'sucesso': True,
                                    'mensagem': f'Planejamento criado com sucesso!',
                                    'planejamento_id': planejamento.id,
                                    'redirect_url': f'/propriedade/{propriedade_id}/pecuaria/planejamento/?planejamento={planejamento.id}',
                                })
                            except Exception as e:
                                logger.error(f'Erro ao criar planejamento: {e}', exc_info=True)
                                return JsonResponse({
                                    'erro': f'Erro ao criar planejamento: {str(e)}',
                                }, status=500)
                
                # Processar resposta normalmente
                try:
                    resultado = chat.processar_resposta(resposta)
                    
                    # Salvar novo estado (garantir que dados_coletados seja serializável)
                    try:
                        dados_coletados_serializavel = chat._converter_dados_para_serializavel(chat.dados_coletados)
                    except Exception as e_conv:
                        logger.warning(f'Erro ao converter dados para serializável: {e_conv}')
                        # Se falhar, usar dados originais (pode causar erro na sessão mas é melhor que quebrar)
                        dados_coletados_serializavel = chat.dados_coletados
                    
                    request.session[session_key] = {
                        'etapa_atual': chat.etapa_atual,
                        'dados_coletados': dados_coletados_serializavel,
                        'ano': chat.ano,
                    }
                    
                    return JsonResponse(resultado)
                except Exception as e_processar:
                    logger.error(f'Erro ao processar resposta: {e_processar}', exc_info=True)
                    return JsonResponse({
                        'erro': f'Erro ao processar resposta: {str(e_processar)}',
                    }, status=500)
            except Exception as e:
                logger.error(f'Erro ao recriar chat ou processar: {e}', exc_info=True)
                import traceback
                logger.error(traceback.format_exc())
                return JsonResponse({
                    'erro': f'Erro ao processar resposta: {str(e)}',
                }, status=500)
        
        elif acao == 'criar':
            # Criar planejamento com dados coletados
            session_key = f'planejamento_ia_{propriedade_id}'
            estado = request.session.get(session_key)
            
            if not estado:
                return JsonResponse({
                    'erro': 'Sessão expirada. Por favor, inicie novamente.',
                }, status=400)
            
            # Recriar chat com estado salvo (não recarregar análise da IA)
            chat = PlanejamentoIAChat(propriedade_id, estado.get('ano'), carregar_analise_ia=False)
            # Restaurar dados coletados, convertendo tipos se necessário
            dados_restaurados = estado.get('dados_coletados', {})
            chat.dados_coletados = dados_restaurados
            
            # Criar planejamento
            planejamento = chat.criar_planejamento(propriedade)
            
            # Limpar sessão
            del request.session[session_key]
            
            return JsonResponse({
                'sucesso': True,
                'mensagem': f'Planejamento criado com sucesso!',
                'planejamento_id': planejamento.id,
                'redirect_url': f'/propriedade/{propriedade_id}/pecuaria/planejamento/?planejamento={planejamento.id}',
            })
        
        elif acao == 'recomendacoes':
            # Retornar recomendações da IA
            session_key = f'planejamento_ia_{propriedade_id}'
            estado = request.session.get(session_key)
            
            if not estado:
                return JsonResponse({
                    'erro': 'Sessão expirada.',
                }, status=400)
            
            chat = PlanejamentoIAChat(propriedade_id, estado.get('ano'), carregar_analise_ia=False)
            # Carregar análise da IA se necessário
            if not chat.analise_ia:
                try:
                    chat._carregar_analise_ia()
                except:
                    pass
            recomendacoes = chat.obter_recomendacoes_inteligentes()
            insights = chat.obter_insights_gerais()
            
            return JsonResponse({
                'recomendacoes': recomendacoes,
                'insights': insights,
            })
        
        elif acao == 'cancelar':
            # Cancelar e limpar sessão
            session_key = f'planejamento_ia_{propriedade_id}'
            if session_key in request.session:
                del request.session[session_key]
            
            return JsonResponse({
                'sucesso': True,
                'mensagem': 'Chat cancelado.',
            })
        
        else:
            return JsonResponse({
                'erro': 'Ação não reconhecida.',
            }, status=400)
    
    except Exception as e:
        logger.error(f'Erro na API de planejamento IA: {e}', exc_info=True)
        return JsonResponse({
            'erro': f'Erro ao processar: {str(e)}',
        }, status=500)

