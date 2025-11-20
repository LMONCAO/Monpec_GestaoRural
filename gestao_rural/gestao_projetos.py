# -*- coding: utf-8 -*-
"""
MÓDULO DE GESTÃO DE PROJETOS RURAIS
Sistema completo para planejamento e acompanhamento de projetos
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
from enum import Enum


class StatusProjeto(Enum):
    """Status do projeto"""
    PLANEJAMENTO = "planejamento"
    EM_ANDAMENTO = "em_andamento"
    PAUSADO = "pausado"
    CONCLUIDO = "concluido"
    CANCELADO = "cancelado"


class TipoProjeto(Enum):
    """Tipos de projetos rurais"""
    EXPANSAO = "expansao"
    MELHORIA = "melhoria"
    INFRAESTRUTURA = "infraestrutura"
    TECNOLOGIA = "tecnologia"
    SANITARIO = "sanitario"
    REPRODUCAO = "reproducao"
    PASTAGEM = "pastagem"


class GestorProjetos:
    """
    Sistema completo de gestão de projetos rurais
    """
    
    def __init__(self):
        self.tipos_projeto = {
            'EXPANSAO': {
                'nome': 'Expansão de Rebanho',
                'icon': 'fa-chart-line',
                'color': '#6495ed',
                'prazo_medio_meses': 24
            },
            'MELHORIA': {
                'nome': 'Melhoria Genética',
                'icon': 'fa-dna',
                'color': '#8b6f47',
                'prazo_medio_meses': 36
            },
            'INFRAESTRUTURA': {
                'nome': 'Infraestrutura',
                'icon': 'fa-warehouse',
                'color': '#2d7a4f',
                'prazo_medio_meses': 12
            },
            'TECNOLOGIA': {
                'nome': 'Tecnologia',
                'icon': 'fa-laptop',
                'color': '#2b6cb0',
                'prazo_medio_meses': 6
            },
            'SANITARIO': {
                'nome': 'Programa Sanitário',
                'icon': 'fa-syringe',
                'color': '#c53030',
                'prazo_medio_meses': 12
            },
            'REPRODUCAO': {
                'nome': 'Programa de Reprodução',
                'icon': 'fa-baby',
                'color': '#d69e2e',
                'prazo_medio_meses': 18
            },
            'PASTAGEM': {
                'nome': 'Manejo de Pastagem',
                'icon': 'fa-leaf',
                'color': '#38a169',
                'prazo_medio_meses': 12
            }
        }
    
    def criar_projeto(
        self,
        nome: str,
        tipo: str,
        propriedade,
        investimento_total: Decimal,
        data_inicio: datetime,
        prazo_meses: int,
        objetivos: List[str],
        responsavel: str
    ) -> Dict[str, Any]:
        """
        Cria um novo projeto rural
        """
        tipo_info = self.tipos_projeto.get(tipo, self.tipos_projeto['MELHORIA'])
        data_prevista_conclusao = data_inicio + timedelta(days=prazo_meses * 30)
        
        projeto = {
            'nome': nome,
            'tipo': tipo,
            'tipo_nome': tipo_info['nome'],
            'tipo_icon': tipo_info['icon'],
            'tipo_color': tipo_info['color'],
            'propriedade': propriedade.nome if hasattr(propriedade, 'nome') else 'Não definida',
            'status': StatusProjeto.PLANEJAMENTO.value,
            'investimento_total': float(investimento_total),
            'investimento_realizado': 0.0,
            'percentual_concluido': 0.0,
            'data_inicio': data_inicio,
            'data_prevista_conclusao': data_prevista_conclusao,
            'prazo_meses': prazo_meses,
            'objetivos': objetivos,
            'responsavel': responsavel,
            'etapas': self._gerar_etapas_padrao(tipo, prazo_meses),
            'riscos': self._identificar_riscos_potenciais(tipo),
            'kpis': self._definir_kpis_projeto(tipo)
        }
        
        return projeto
    
    def acompanhar_projeto(
        self,
        projeto_id: int,
        percentual_concluido: float,
        investimento_realizado: Decimal,
        observacoes: str = ''
    ) -> Dict[str, Any]:
        """
        Atualiza e acompanha progresso do projeto
        """
        # Simular busca do projeto
        projeto = self._buscar_projeto(projeto_id)
        
        # Atualizar dados
        projeto['percentual_concluido'] = percentual_concluido
        projeto['investimento_realizado'] = float(investimento_realizado)
        projeto['ultima_atualizacao'] = datetime.now()
        
        # Calcular status
        analise = self._analisar_saude_projeto(projeto)
        
        # Calcular desvios
        desvios = self._calcular_desvios_projeto(projeto)
        
        # Projetar conclusão
        projecao = self._projetar_conclusao_projeto(projeto)
        
        return {
            'projeto': projeto,
            'analise_saude': analise,
            'desvios': desvios,
            'projecao_conclusao': projecao,
            'alertas': self._gerar_alertas_projeto(analise, desvios)
        }
    
    def dashboard_projetos(self, propriedade) -> Dict[str, Any]:
        """
        Gera dashboard completo de todos os projetos
        """
        # Simular lista de projetos
        projetos = self._listar_projetos(propriedade)
        
        # Estatísticas gerais
        total_projetos = len(projetos)
        projetos_ativos = len([p for p in projetos if p['status'] == StatusProjeto.EM_ANDAMENTO.value])
        projetos_concluidos = len([p for p in projetos if p['status'] == StatusProjeto.CONCLUIDO.value])
        
        # Investimento total
        investimento_total = sum(Decimal(str(p['investimento_total'])) for p in projetos)
        investimento_realizado = sum(Decimal(str(p['investimento_realizado'])) for p in projetos)
        
        # Projetos por tipo
        por_tipo = {}
        for tipo_key in self.tipos_projeto.keys():
            por_tipo[tipo_key] = len([p for p in projetos if p['tipo'] == tipo_key])
        
        # Projetos em risco
        em_risco = [p for p in projetos if self._analisar_saude_projeto(p)['status'] == 'RISCO']
        
        return {
            'estatisticas': {
                'total_projetos': total_projetos,
                'projetos_ativos': projetos_ativos,
                'projetos_concluidos': projetos_concluidos,
                'taxa_conclusao': (projetos_concluidos / total_projetos * 100) if total_projetos > 0 else 0
            },
            'investimentos': {
                'total_planejado': float(investimento_total),
                'total_realizado': float(investimento_realizado),
                'percentual_executado': float(investimento_realizado / investimento_total * 100) if investimento_total > 0 else 0
            },
            'por_tipo': por_tipo,
            'projetos_em_risco': em_risco,
            'proximos_vencimentos': self._listar_proximos_vencimentos(projetos)
        }
    
    def _gerar_etapas_padrao(self, tipo: str, prazo_total_meses: int) -> List[Dict[str, Any]]:
        """Gera etapas padrão baseadas no tipo de projeto"""
        etapas_base = {
            'EXPANSAO': [
                {'nome': 'Planejamento e Análise', 'percentual': 10},
                {'nome': 'Aquisição de Animais', 'percentual': 40},
                {'nome': 'Adaptação e Manejo', 'percentual': 30},
                {'nome': 'Consolidação', 'percentual': 20}
            ],
            'INFRAESTRUTURA': [
                {'nome': 'Projeto e Orçamentos', 'percentual': 15},
                {'nome': 'Aprovações e Licenças', 'percentual': 10},
                {'nome': 'Execução da Obra', 'percentual': 60},
                {'nome': 'Finalização e Testes', 'percentual': 15}
            ],
            'TECNOLOGIA': [
                {'nome': 'Levantamento de Requisitos', 'percentual': 20},
                {'nome': 'Aquisição/Desenvolvimento', 'percentual': 30},
                {'nome': 'Implantação', 'percentual': 30},
                {'nome': 'Treinamento e Ajustes', 'percentual': 20}
            ]
        }
        
        etapas = etapas_base.get(tipo, etapas_base['EXPANSAO'])
        
        # Calcular datas
        dias_por_etapa = (prazo_total_meses * 30) / len(etapas)
        data_atual = datetime.now()
        
        etapas_com_datas = []
        for i, etapa in enumerate(etapas):
            data_inicio = data_atual + timedelta(days=i * dias_por_etapa)
            data_fim = data_inicio + timedelta(days=dias_por_etapa)
            
            etapas_com_datas.append({
                'numero': i + 1,
                'nome': etapa['nome'],
                'percentual_projeto': etapa['percentual'],
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'status': 'PENDENTE',
                'concluido': 0.0
            })
        
        return etapas_com_datas
    
    def _identificar_riscos_potenciais(self, tipo: str) -> List[Dict[str, str]]:
        """Identifica riscos potenciais por tipo de projeto"""
        riscos_por_tipo = {
            'EXPANSAO': [
                {'risco': 'Preço de compra acima do esperado', 'impacto': 'ALTO', 'probabilidade': 'MÉDIA'},
                {'risco': 'Adaptação dos animais', 'impacto': 'MÉDIO', 'probabilidade': 'MÉDIA'},
                {'risco': 'Disponibilidade de pasto', 'impacto': 'ALTO', 'probabilidade': 'BAIXA'}
            ],
            'INFRAESTRUTURA': [
                {'risco': 'Atraso na execução', 'impacto': 'MÉDIO', 'probabilidade': 'ALTA'},
                {'risco': 'Custo acima do orçado', 'impacto': 'ALTO', 'probabilidade': 'MÉDIA'},
                {'risco': 'Problemas climáticos', 'impacto': 'MÉDIO', 'probabilidade': 'MÉDIA'}
            ],
            'TECNOLOGIA': [
                {'risco': 'Resistência da equipe', 'impacto': 'MÉDIO', 'probabilidade': 'MÉDIA'},
                {'risco': 'Problemas técnicos', 'impacto': 'ALTO', 'probabilidade': 'BAIXA'},
                {'risco': 'Integração com sistemas existentes', 'impacto': 'MÉDIO', 'probabilidade': 'BAIXA'}
            ]
        }
        
        return riscos_por_tipo.get(tipo, [])
    
    def _definir_kpis_projeto(self, tipo: str) -> List[Dict[str, str]]:
        """Define KPIs para acompanhamento do projeto"""
        kpis_por_tipo = {
            'EXPANSAO': [
                {'kpi': 'Número de animais adquiridos', 'meta': '100 cabeças'},
                {'kpi': 'Taxa de mortalidade na adaptação', 'meta': '< 2%'},
                {'kpi': 'Ganho de peso médio', 'meta': '> 0.8 kg/dia'}
            ],
            'INFRAESTRUTURA': [
                {'kpi': 'Percentual de conclusão da obra', 'meta': '100%'},
                {'kpi': 'Desvio de orçamento', 'meta': '< 10%'},
                {'kpi': 'Prazo de execução', 'meta': 'Dentro do planejado'}
            ],
            'TECNOLOGIA': [
                {'kpi': 'Taxa de adoção da tecnologia', 'meta': '> 90%'},
                {'kpi': 'Redução de tempo em processos', 'meta': '> 40%'},
                {'kpi': 'Satisfação dos usuários', 'meta': '> 4.5/5'}
            ]
        }
        
        return kpis_por_tipo.get(tipo, [])
    
    def _buscar_projeto(self, projeto_id: int) -> Dict[str, Any]:
        """Busca projeto (simulado - implementar query real)"""
        return {
            'id': projeto_id,
            'nome': 'Expansão do Rebanho 2025',
            'tipo': 'EXPANSAO',
            'status': StatusProjeto.EM_ANDAMENTO.value,
            'investimento_total': 250000.0,
            'investimento_realizado': 125000.0,
            'percentual_concluido': 50.0,
            'data_inicio': datetime(2025, 6, 1),
            'data_prevista_conclusao': datetime(2027, 6, 1),
            'prazo_meses': 24
        }
    
    def _analisar_saude_projeto(self, projeto: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa saúde geral do projeto"""
        perc_concluido = projeto['percentual_concluido']
        perc_investido = (projeto['investimento_realizado'] / projeto['investimento_total'] * 100) if projeto['investimento_total'] > 0 else 0
        
        # Verificar alinhamento entre % concluído e % investido
        desvio_investimento = abs(perc_concluido - perc_investido)
        
        # Verificar prazo
        if 'data_inicio' in projeto and 'data_prevista_conclusao' in projeto:
            prazo_total = (projeto['data_prevista_conclusao'] - projeto['data_inicio']).days
            prazo_decorrido = (datetime.now() - projeto['data_inicio']).days
            perc_prazo_decorrido = (prazo_decorrido / prazo_total * 100) if prazo_total > 0 else 0
            
            desvio_prazo = perc_prazo_decorrido - perc_concluido
        else:
            perc_prazo_decorrido = 0
            desvio_prazo = 0
        
        # Determinar status de saúde
        if desvio_investimento > 15 or desvio_prazo > 20:
            status = 'RISCO'
            cor = '#c53030'
        elif desvio_investimento > 10 or desvio_prazo > 10:
            status = 'ATENÇÃO'
            cor = '#d69e2e'
        else:
            status = 'SAUDÁVEL'
            cor = '#2d7a4f'
        
        return {
            'status': status,
            'cor': cor,
            'percentual_concluido': perc_concluido,
            'percentual_investido': perc_investido,
            'percentual_prazo_decorrido': perc_prazo_decorrido,
            'desvio_investimento': desvio_investimento,
            'desvio_prazo': desvio_prazo
        }
    
    def _calcular_desvios_projeto(self, projeto: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula desvios de orçamento e prazo"""
        investimento_total = Decimal(str(projeto['investimento_total']))
        investimento_realizado = Decimal(str(projeto['investimento_realizado']))
        
        desvio_orcamento = investimento_realizado - (investimento_total * Decimal(str(projeto['percentual_concluido'] / 100)))
        
        return {
            'desvio_orcamento': float(desvio_orcamento),
            'desvio_orcamento_percentual': float(desvio_orcamento / investimento_total * 100) if investimento_total > 0 else 0,
            'esta_acima_orcamento': desvio_orcamento > 0,
            'previsao_estouro': float((investimento_realizado / Decimal(str(projeto['percentual_concluido'] / 100))) - investimento_total) if projeto['percentual_concluido'] > 0 else 0
        }
    
    def _projetar_conclusao_projeto(self, projeto: Dict[str, Any]) -> Dict[str, Any]:
        """Projeta data e custo de conclusão"""
        if projeto['percentual_concluido'] > 0:
            # Velocidade média
            if 'data_inicio' in projeto:
                dias_decorridos = (datetime.now() - projeto['data_inicio']).days
                velocidade_diaria = projeto['percentual_concluido'] / dias_decorridos if dias_decorridos > 0 else 0
                
                # Dias restantes
                percentual_restante = 100 - projeto['percentual_concluido']
                dias_restantes = int(percentual_restante / velocidade_diaria) if velocidade_diaria > 0 else 999
                
                data_conclusao_projetada = datetime.now() + timedelta(days=dias_restantes)
            else:
                data_conclusao_projetada = projeto['data_prevista_conclusao']
                dias_restantes = (data_conclusao_projetada - datetime.now()).days
            
            # Custo projetado
            custo_por_percentual = Decimal(str(projeto['investimento_realizado'])) / Decimal(str(projeto['percentual_concluido'])) if projeto['percentual_concluido'] > 0 else Decimal('0')
            custo_total_projetado = custo_por_percentual * Decimal('100')
        else:
            data_conclusao_projetada = projeto['data_prevista_conclusao']
            dias_restantes = (data_conclusao_projetada - datetime.now()).days
            custo_total_projetado = Decimal(str(projeto['investimento_total']))
        
        return {
            'data_conclusao_projetada': data_conclusao_projetada,
            'dias_restantes': dias_restantes,
            'custo_total_projetado': float(custo_total_projetado),
            'desvio_custo_projetado': float(custo_total_projetado - Decimal(str(projeto['investimento_total']))),
            'desvio_prazo_dias': (data_conclusao_projetada - projeto['data_prevista_conclusao']).days if 'data_prevista_conclusao' in projeto else 0
        }
    
    def _gerar_alertas_projeto(self, analise: Dict, desvios: Dict) -> List[str]:
        """Gera alertas sobre o projeto"""
        alertas = []
        
        if analise['status'] == 'RISCO':
            alertas.append('🚨 Projeto em RISCO! Ação imediata necessária.')
        
        if desvios['esta_acima_orcamento']:
            alertas.append(f"⚠️ Investimento {desvios['desvio_orcamento_percentual']:.1f}% acima do planejado.")
        
        if analise['desvio_prazo'] > 15:
            alertas.append(f"⏰ Projeto está {analise['desvio_prazo']:.1f}% atrasado no cronograma.")
        
        return alertas
    
    def _listar_projetos(self, propriedade) -> List[Dict[str, Any]]:
        """Lista todos os projetos (simulado)"""
        return [
            {
                'id': 1,
                'nome': 'Expansão do Rebanho 2025',
                'tipo': 'EXPANSAO',
                'status': StatusProjeto.EM_ANDAMENTO.value,
                'investimento_total': 250000.0,
                'investimento_realizado': 125000.0,
                'percentual_concluido': 50.0,
                'data_inicio': datetime(2025, 6, 1),
                'data_prevista_conclusao': datetime(2027, 6, 1),
                'prazo_meses': 24
            }
        ]
    
    def _listar_proximos_vencimentos(self, projetos: List[Dict]) -> List[Dict[str, Any]]:
        """Lista projetos próximos do vencimento"""
        proximos = []
        
        for projeto in projetos:
            if projeto['status'] == StatusProjeto.EM_ANDAMENTO.value:
                if 'data_prevista_conclusao' in projeto:
                    dias_restantes = (projeto['data_prevista_conclusao'] - datetime.now()).days
                    if 0 < dias_restantes <= 90:  # Próximos 90 dias
                        proximos.append({
                            'projeto': projeto['nome'],
                            'dias_restantes': dias_restantes,
                            'percentual_concluido': projeto['percentual_concluido']
                        })
        
        return sorted(proximos, key=lambda x: x['dias_restantes'])


# Instância global
gestor_projetos = GestorProjetos()

