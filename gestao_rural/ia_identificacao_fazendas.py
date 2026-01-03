# -*- coding: utf-8 -*-
"""
Sistema de Identificação Inteligente de Fazendas e Movimentações Automáticas
Identifica o perfil da fazenda e automatiza todas as movimentações conforme o ciclo pecuário
"""

from decimal import Decimal
from typing import Dict, List, Any, Tuple
from enum import Enum
from .models import InventarioRebanho, CategoriaAnimal, ParametrosProjecaoRebanho
from .ia_perfis_fazendas import TipoFazenda, PERFIS_FAZENDAS

class PerfilFazenda(Enum):
    """Perfis de fazendas identificados automaticamente"""
    SO_CRIA = "Só Cria"
    SO_RECRIA = "Só Recria" 
    SO_ENGORDA = "Só Engorda"
    RECRIA_ENGORDA = "Recria + Engorda"
    CICLO_COMPLETO = "Ciclo Completo"
    CONFINAMENTO = "Confinamento"
    CONFINAMENTO_RECRIA = "Confinamento + Recria"
    CONFINAMENTO_ENGORDA = "Confinamento + Engorda"
    CONFINAMENTO_COMPLETO = "Confinamento Completo"

class SistemaIdentificacaoFazendas:
    """Sistema que identifica automaticamente o perfil da fazenda e gera movimentações"""
    
    def __init__(self):
        self.perfis = PERFIS_FAZENDAS
        
    def identificar_perfil_fazenda(self, inventario: List[InventarioRebanho], parametros: ParametrosProjecaoRebanho) -> Dict[str, Any]:
        """
        Identifica automaticamente o perfil da fazenda baseado no inventário e parâmetros
        """
        # Analisar composição do inventário
        analise_inventario = self._analisar_composicao_inventario(inventario)
        
        # Analisar parâmetros de vendas e compras
        analise_parametros = self._analisar_parametros(parametros)
        
        # Detectar perfil baseado na análise
        perfil_detectado = self._detectar_perfil(analise_inventario, analise_parametros)
        
        # Gerar estratégias de movimentação
        estrategias = self._gerar_estrategias_movimentacao(perfil_detectado, analise_inventario)
        
        return {
            'perfil_detectado': perfil_detectado,
            'nome_perfil': perfil_detectado.value,
            'analise_inventario': analise_inventario,
            'analise_parametros': analise_parametros,
            'estrategias': estrategias,
            'movimentacoes_automaticas': self._gerar_movimentacoes_automaticas(perfil_detectado, analise_inventario)
        }
    
    def _analisar_composicao_inventario(self, inventario: List[InventarioRebanho]) -> Dict[str, Any]:
        """Analisa a composição do inventário para identificar o perfil"""
        total_animais = sum(item.quantidade for item in inventario)
        
        # Categorizar animais por tipo
        femeas_reprodutoras = 0  # Multíparas, Primíparas
        femeas_em_crescimento = 0  # Bezerras, Novilhas
        machos_comerciais = 0  # Bois, Garrotes
        machos_reprodutores = 0  # Touros
        bezerros_ambos = 0  # Bezerros e Bezerras
        
        for item in inventario:
            categoria = item.categoria.nome.lower()
            quantidade = item.quantidade
            
            if 'multípara' in categoria or 'primípara' in categoria:
                femeas_reprodutoras += quantidade
            elif 'novilha' in categoria:
                femeas_em_crescimento += quantidade
            elif 'boi' in categoria or 'garrote' in categoria:
                machos_comerciais += quantidade
            elif 'touro' in categoria:
                machos_reprodutores += quantidade
            elif 'bezerro' in categoria or 'bezerra' in categoria:
                bezerros_ambos += quantidade
        
        # Calcular percentuais
        percent_femeas_reprodutoras = (femeas_reprodutoras / total_animais * 100) if total_animais > 0 else 0
        percent_machos_comerciais = (machos_comerciais / total_animais * 100) if total_animais > 0 else 0
        percent_bezerros = (bezerros_ambos / total_animais * 100) if total_animais > 0 else 0
        
        return {
            'total_animais': total_animais,
            'femeas_reprodutoras': femeas_reprodutoras,
            'femeas_em_crescimento': femeas_em_crescimento,
            'machos_comerciais': machos_comerciais,
            'machos_reprodutores': machos_reprodutores,
            'bezerros_ambos': bezerros_ambos,
            'percent_femeas_reprodutoras': percent_femeas_reprodutoras,
            'percent_machos_comerciais': percent_machos_comerciais,
            'percent_bezerros': percent_bezerros,
            'tem_matrizes': femeas_reprodutoras > 0,
            'tem_machos_comerciais': machos_comerciais > 0,
            'tem_touros': machos_reprodutores > 0,
            'relacao_touro_vaca': (machos_reprodutores / femeas_reprodutoras) if femeas_reprodutoras > 0 else 0
        }
    
    def _analisar_parametros(self, parametros: ParametrosProjecaoRebanho) -> Dict[str, Any]:
        """Analisa os parâmetros de vendas e compras"""
        return {
            'percentual_venda_machos': parametros.percentual_venda_machos_anual,
            'percentual_venda_femeas': parametros.percentual_venda_femeas_anual,
            'natalidade': parametros.taxa_natalidade_anual,
            'mortalidade_bezerros': parametros.taxa_mortalidade_bezerros_anual,
            'mortalidade_adultos': parametros.taxa_mortalidade_adultos_anual,
            'periodicidade': parametros.periodicidade,
            'foca_vendas': parametros.percentual_venda_machos_anual > 80,
            'foca_crescimento': parametros.percentual_venda_femeas_anual < 20,
            'alta_natalidade': parametros.taxa_natalidade_anual > 85
        }
    
    def _detectar_perfil(self, analise_inventario: Dict[str, Any], analise_parametros: Dict[str, Any]) -> PerfilFazenda:
        """Detecta o perfil da fazenda baseado na análise"""
        
        # Regras de detecção
        if analise_inventario['tem_matrizes'] and analise_inventario['tem_touros']:
            if analise_inventario['percent_machos_comerciais'] > 60:
                return PerfilFazenda.SO_ENGORDA
            elif analise_inventario['percent_bezerros'] > 40:
                return PerfilFazenda.SO_CRIA
            elif analise_inventario['femeas_em_crescimento'] > analise_inventario['femeas_reprodutoras']:
                return PerfilFazenda.SO_RECRIA
            else:
                return PerfilFazenda.CICLO_COMPLETO
        
        elif analise_inventario['tem_matrizes'] and not analise_inventario['tem_touros']:
            return PerfilFazenda.SO_CRIA
        
        elif not analise_inventario['tem_matrizes'] and analise_inventario['tem_machos_comerciais']:
            if analise_inventario['femeas_em_crescimento'] > 0:
                return PerfilFazenda.RECRIA_ENGORDA
            else:
                return PerfilFazenda.SO_ENGORDA
        
        else:
            return PerfilFazenda.SO_RECRIA
    
    def _gerar_estrategias_movimentacao(self, perfil: PerfilFazenda, analise_inventario: Dict[str, Any]) -> Dict[str, Any]:
        """Gera estratégias de movimentação baseadas no perfil detectado"""
        
        estrategias = {
            'vendas': {},
            'compras': {},
            'transferencias': {},
            'reposicao': {},
            'evolucao_idade': {}
        }
        
        if perfil == PerfilFazenda.SO_CRIA:
            estrategias.update({
                'vendas': {
                    'Bezerros (0-12m)': 0.90,  # Vende 90% dos bezerros
                    'Bezerras (0-12m)': 0.40,  # Vende 40% das bezerras
                },
                'compras': {
                    'Novilhas (12-24m)': 20,  # Compra novilhas para reposição
                },
                'transferencias': {
                    'saida': ['Bezerros (0-12m)', 'Bezerras (0-12m)'],
                    'entrada': ['Novilhas (12-24m)']
                },
                'reposicao': {
                    'descarte_multiparas': 0.15,  # 15% de descarte anual
                    'reposicao_primiparas': 0.20   # 20% de reposição
                }
            })
        
        elif perfil == PerfilFazenda.SO_RECRIA:
            estrategias.update({
                'vendas': {
                    'Garrotes (12-24m)': 0.80,  # Vende garrotes prontos
                    'Novilhas (12-24m)': 0.60,  # Vende novilhas prontas
                },
                'compras': {
                    'Bezerros (0-12m)': 50,  # Compra bezerros para recria
                    'Bezerras (0-12m)': 30,  # Compra bezerras para recria
                },
                'transferencias': {
                    'saida': ['Garrotes (12-24m)', 'Novilhas (12-24m)'],
                    'entrada': ['Bezerros (0-12m)', 'Bezerras (0-12m)']
                }
            })
        
        elif perfil == PerfilFazenda.SO_ENGORDA:
            estrategias.update({
                'vendas': {
                    'Bois (24-36m)': 0.95,  # Vende bois prontos
                    'Bois Magros (24-36m)': 0.90,  # Vende bois magros
                },
                'compras': {
                    'Garrotes (12-24m)': 40,  # Compra garrotes para engorda
                },
                'transferencias': {
                    'saida': ['Bois (24-36m)', 'Bois Magros (24-36m)'],
                    'entrada': ['Garrotes (12-24m)']
                }
            })
        
        elif perfil == PerfilFazenda.CICLO_COMPLETO:
            estrategias.update({
                'vendas': {
                    'Bois (24-36m)': 0.90,  # Vende bois
                    'Vacas de Descarte': 0.85,  # Vende vacas de descarte
                },
                'compras': {
                    'Novilhas (12-24m)': 10,  # Reposição mínima
                },
                'transferencias': {
                    'saida': ['Bois (24-36m)', 'Vacas de Descarte'],
                    'entrada': ['Novilhas (12-24m)']
                },
                'reposicao': {
                    'descarte_multiparas': 0.12,
                    'reposicao_primiparas': 0.15
                }
            })
        
        # Estratégias de evolução de idade
        estrategias['evolucao_idade'] = {
            'Bezerros (0-12m)': 'Garrotes (12-24m)',
            'Bezerras (0-12m)': 'Novilhas (12-24m)',
            'Garrotes (12-24m)': 'Bois (24-36m)',
            'Novilhas (12-24m)': 'Primíparas (24-36m)',
            'Primíparas (24-36m)': 'Multíparas (>36m)'
        }
        
        return estrategias
    
    def _gerar_movimentacoes_automaticas(self, perfil: PerfilFazenda, analise_inventario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gera lista de movimentações automáticas baseadas no perfil"""
        movimentacoes = []
        
        if perfil == PerfilFazenda.SO_CRIA:
            # Fazenda de cria vende bezerros e compra novilhas
            movimentacoes.extend([
                {
                    'tipo': 'VENDA',
                    'categoria': 'Bezerros (0-12m)',
                    'quantidade_porcentagem': 90,
                    'frequencia': 'BIMESTRAL',
                    'justificativa': 'Venda estratégica de bezerros - fazenda de cria'
                },
                {
                    'tipo': 'VENDA',
                    'categoria': 'Bezerras (0-12m)',
                    'quantidade_porcentagem': 40,
                    'frequencia': 'TRIMESTRAL',
                    'justificativa': 'Venda de excedente de bezerras'
                },
                {
                    'tipo': 'COMPRA',
                    'categoria': 'Novilhas (12-24m)',
                    'quantidade_fixa': 20,
                    'frequencia': 'ANUAL',
                    'justificativa': 'Reposição de matrizes'
                }
            ])
        
        elif perfil == PerfilFazenda.SO_RECRIA:
            # Fazenda de recria compra bezerros e vende animais prontos
            movimentacoes.extend([
                {
                    'tipo': 'COMPRA',
                    'categoria': 'Bezerros (0-12m)',
                    'quantidade_fixa': 50,
                    'frequencia': 'BIMESTRAL',
                    'justificativa': 'Compra de bezerros para recria'
                },
                {
                    'tipo': 'VENDA',
                    'categoria': 'Garrotes (12-24m)',
                    'quantidade_porcentagem': 80,
                    'frequencia': 'TRIMESTRAL',
                    'justificativa': 'Venda de garrotes prontos'
                }
            ])
        
        elif perfil == PerfilFazenda.SO_ENGORDA:
            # Fazenda de engorda compra animais para engorda e vende prontos
            movimentacoes.extend([
                {
                    'tipo': 'COMPRA',
                    'categoria': 'Garrotes (12-24m)',
                    'quantidade_fixa': 40,
                    'frequencia': 'MENSAL',
                    'justificativa': 'Compra de garrotes para engorda'
                },
                {
                    'tipo': 'VENDA',
                    'categoria': 'Bois (24-36m)',
                    'quantidade_porcentagem': 95,
                    'frequencia': 'BIMESTRAL',
                    'justificativa': 'Venda de bois prontos para abate'
                }
            ])
        
        return movimentacoes
    
    def calcular_valores_por_categoria(self, inventario: List[InventarioRebanho]) -> Dict[str, Decimal]:
        """Calcula valores por categoria baseado no inventário atual"""
        valores = {}
        
        for item in inventario:
            if item.valor_por_cabeca and item.valor_por_cabeca > 0:
                valores[item.categoria.nome] = item.valor_por_cabeca
            else:
                # Usar valores padrão por categoria
                valores[item.categoria.nome] = self._obter_valor_padrao_categoria(item.categoria.nome)
        
        return valores
    
    def _obter_valor_padrao_categoria(self, categoria: str) -> Decimal:
        """Retorna valor padrão por categoria"""
        valores_padrao = {
            'Bezerros (0-12m)': Decimal('2000.00'),
            'Bezerras (0-12m)': Decimal('1800.00'),
            'Garrotes (12-24m)': Decimal('3500.00'),
            'Novilhas (12-24m)': Decimal('4000.00'),
            'Bois (24-36m)': Decimal('4500.00'),
            'Bois Magros (24-36m)': Decimal('4000.00'),
            'Multíparas (>36m)': Decimal('4000.00'),
            'Primíparas (24-36m)': Decimal('4500.00'),
            'Vacas de Descarte': Decimal('3000.00'),
            'Touros': Decimal('6000.00')
        }
        return valores_padrao.get(categoria, Decimal('2500.00'))
    
    def gerar_relatorio_identificacao(self, resultado: Dict[str, Any]) -> str:
        """Gera relatório HTML da identificação da fazenda"""
        perfil = resultado['perfil_detectado']
        analise = resultado['analise_inventario']
        estrategias = resultado['estrategias']
        
        html = f"""
        <div class="card border-success">
            <div class="card-header bg-success text-white">
                <h5><i class="fas fa-search"></i> Identificação Automática da Fazenda</h5>
                <p class="mb-0">Perfil detectado: <strong>{perfil.value}</strong></p>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6><i class="fas fa-chart-pie"></i> Composição do Inventário</h6>
                        <ul class="list-unstyled">
                            <li><strong>Total de Animais:</strong> {analise['total_animais']}</li>
                            <li><strong>Fêmeas Reprodutoras:</strong> {analise['femeas_reprodutoras']} ({analise['percent_femeas_reprodutoras']:.1f}%)</li>
                            <li><strong>Machos Comerciais:</strong> {analise['machos_comerciais']} ({analise['percent_machos_comerciais']:.1f}%)</li>
                            <li><strong>Bezerros/Bezerras:</strong> {analise['bezerros_ambos']} ({analise['percent_bezerros']:.1f}%)</li>
                            <li><strong>Touros:</strong> {analise['machos_reprodutores']}</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h6><i class="fas fa-cogs"></i> Estratégias Automáticas</h6>
                        <ul class="list-unstyled">
        """
        
        # Adicionar estratégias de vendas
        if estrategias['vendas']:
            html += "<li><strong>Vendas Automáticas:</strong></li>"
            for categoria, percentual in estrategias['vendas'].items():
                html += f"<li class='ms-3'>• {categoria}: {percentual*100:.0f}%</li>"
        
        # Adicionar estratégias de compras
        if estrategias['compras']:
            html += "<li><strong>Compras Automáticas:</strong></li>"
            for categoria, quantidade in estrategias['compras'].items():
                html += f"<li class='ms-3'>• {categoria}: {quantidade} cabeças</li>"
        
        html += """
                        </ul>
                    </div>
                </div>
                
                <div class="alert alert-info mt-3">
                    <h6><i class="fas fa-robot"></i> Sistema Inteligente Ativo</h6>
                    <p class="mb-0">Todas as movimentações serão geradas automaticamente conforme o perfil detectado: <strong>""" + perfil.value + """</strong></p>
                </div>
            </div>
        </div>
        """
        
        return html

# Instância global do sistema
sistema_identificacao = SistemaIdentificacaoFazendas()



