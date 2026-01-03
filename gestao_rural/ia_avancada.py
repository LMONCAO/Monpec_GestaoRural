# -*- coding: utf-8 -*-
"""
IA Avançada para Projeção Pecuária
Sistema inteligente que analisa o perfil da fazenda e projeta receitas/despesas/crescimento
"""

import json
from decimal import Decimal
from typing import Dict, List, Any, Optional
from .ia_perfis_fazendas import (
    PERFIS_FAZENDAS, TipoFazenda, PerfilFazenda,
    detectar_perfil_fazenda, calcular_projecao_inteligente, gerar_recomendacoes_perfil
)

class IAPecuariaAvancada:
    """Classe principal da IA para projeção pecuária"""
    
    def __init__(self):
        self.perfis = PERFIS_FAZENDAS
        self.analise_atual = None
    
    def analisar_fazenda(self, inventario: Dict[str, int], parametros_usuario: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa a fazenda e retorna projeção inteligente
        """
        try:
            # Detectar perfil da fazenda
            perfil_tipo = detectar_perfil_fazenda(inventario, parametros_usuario)
            perfil = self.perfis[perfil_tipo]
            
            # Calcular projeção
            projecao = calcular_projecao_inteligente(perfil, inventario, parametros_usuario)
            
            # Gerar recomendações
            recomendacoes = gerar_recomendacoes_perfil(perfil, projecao)
            
            # Análise completa
            self.analise_atual = {
                'perfil_detectado': {
                    'tipo': perfil.tipo.value,
                    'nome': perfil.nome,
                    'descricao': perfil.descricao,
                    'caracteristicas': perfil.caracteristicas,
                    'categorias_principais': perfil.categorias_principais
                },
                'estrategias': {
                    'vendas': perfil.estrategia_vendas,
                    'compras': perfil.estrategia_compras
                },
                'parametros_otimizados': perfil.parametros_producao,
                'projecao': projecao,
                'recomendacoes': recomendacoes,
                'indicadores_financeiros': perfil.indicadores_financeiros,
                'metas_crescimento': perfil.metas_crescimento
            }
            
            return self.analise_atual
            
        except Exception as e:
            return {
                'erro': f"Erro na análise: {str(e)}",
                'perfil_detectado': {'tipo': 'Erro', 'nome': 'Análise Falhou'},
                'projecao': {'lucro_total': 0, 'crescimento_rebanho': 0},
                'recomendacoes': ['Erro na análise da fazenda']
            }
    
    def obter_configuracao_otimizada(self, perfil_tipo: TipoFazenda) -> Dict[str, Any]:
        """
        Retorna configuração otimizada baseada no perfil
        """
        perfil = self.perfis[perfil_tipo]
        
        return {
            'natalidade': perfil.parametros_producao['natalidade'],
            'mortalidade_bezerros': perfil.parametros_producao['mortalidade_bezerros'],
            'mortalidade_adultos': perfil.parametros_producao['mortalidade_adultos'],
            'periodicidade': 'MENSAL',
            'anos_projecao': 5,
            'estrategia_vendas': perfil.estrategia_vendas,
            'estrategia_compras': perfil.estrategia_compras
        }
    
    def calcular_viabilidade_economica(self, inventario: Dict[str, int], perfil: PerfilFazenda) -> Dict[str, Any]:
        """
        Calcula viabilidade econômica da fazenda
        """
        total_animais = sum(inventario.values())
        
        # Receitas projetadas
        receita_anual = total_animais * perfil.indicadores_financeiros['receita_por_animal_ano']
        
        # Despesas projetadas
        despesa_anual = total_animais * perfil.indicadores_financeiros['custo_por_animal_ano']
        
        # Lucro
        lucro_anual = receita_anual - despesa_anual
        margem_lucro = (lucro_anual / receita_anual) * 100 if receita_anual > 0 else 0
        
        # ROI
        investimento_total = total_animais * perfil.indicadores_financeiros['investimento_inicial_por_animal']
        roi = (lucro_anual / investimento_total) * 100 if investimento_total > 0 else 0
        
        # Payback
        payback_anos = investimento_total / lucro_anual if lucro_anual > 0 else 0
        
        return {
            'receita_anual': receita_anual,
            'despesa_anual': despesa_anual,
            'lucro_anual': lucro_anual,
            'margem_lucro': margem_lucro,
            'roi': roi,
            'payback_anos': payback_anos,
            'investimento_total': investimento_total,
            'viabilidade': 'ALTA' if roi > 15 else 'MÉDIA' if roi > 10 else 'BAIXA'
        }
    
    def gerar_cenarios(self, inventario: Dict[str, int], perfil: PerfilFazenda) -> Dict[str, Any]:
        """
        Gera cenários otimista, realista e pessimista
        """
        cenarios = {}
        
        # Cenário Otimista (+20% receita, -10% despesa)
        receita_otimista = sum(inventario.values()) * perfil.indicadores_financeiros['receita_por_animal_ano'] * 1.2
        despesa_otimista = sum(inventario.values()) * perfil.indicadores_financeiros['custo_por_animal_ano'] * 0.9
        lucro_otimista = receita_otimista - despesa_otimista
        
        cenarios['otimista'] = {
            'receita': receita_otimista,
            'despesa': despesa_otimista,
            'lucro': lucro_otimista,
            'margem': (lucro_otimista / receita_otimista) * 100 if receita_otimista > 0 else 0
        }
        
        # Cenário Realista (valores base)
        receita_realista = sum(inventario.values()) * perfil.indicadores_financeiros['receita_por_animal_ano']
        despesa_realista = sum(inventario.values()) * perfil.indicadores_financeiros['custo_por_animal_ano']
        lucro_realista = receita_realista - despesa_realista
        
        cenarios['realista'] = {
            'receita': receita_realista,
            'despesa': despesa_realista,
            'lucro': lucro_realista,
            'margem': (lucro_realista / receita_realista) * 100 if receita_realista > 0 else 0
        }
        
        # Cenário Pessimista (-10% receita, +20% despesa)
        receita_pessimista = sum(inventario.values()) * perfil.indicadores_financeiros['receita_por_animal_ano'] * 0.9
        despesa_pessimista = sum(inventario.values()) * perfil.indicadores_financeiros['custo_por_animal_ano'] * 1.2
        lucro_pessimista = receita_pessimista - despesa_pessimista
        
        cenarios['pessimista'] = {
            'receita': receita_pessimista,
            'despesa': despesa_pessimista,
            'lucro': lucro_pessimista,
            'margem': (lucro_pessimista / receita_pessimista) * 100 if receita_pessimista > 0 else 0
        }
        
        return cenarios
    
    def obter_benchmarking(self, perfil: PerfilFazenda) -> Dict[str, Any]:
        """
        Retorna benchmarking do setor para o perfil
        """
        benchmarks = {
            TipoFazenda.SO_CRIA: {
                'margem_lucro_setor': 35,
                'crescimento_rebanho_setor': 25,
                'produtividade_setor': 0.9,
                'eficiencia_setor': 'ALTA'
            },
            TipoFazenda.SO_ENGORDA: {
                'margem_lucro_setor': 25,
                'crescimento_rebanho_setor': 15,
                'produtividade_setor': 1.2,
                'eficiencia_setor': 'ALTA'
            },
            TipoFazenda.CONFINAMENTO: {
                'margem_lucro_setor': 22,
                'crescimento_rebanho_setor': 12,
                'produtividade_setor': 1.5,
                'eficiencia_setor': 'MUITO ALTA'
            },
            TipoFazenda.CICLO_COMPLETO: {
                'margem_lucro_setor': 25,
                'crescimento_rebanho_setor': 15,
                'produtividade_setor': 1.0,
                'eficiencia_setor': 'MÉDIA'
            }
        }
        
        return benchmarks.get(perfil.tipo, {
            'margem_lucro_setor': 20,
            'crescimento_rebanho_setor': 15,
            'produtividade_setor': 1.0,
            'eficiencia_setor': 'MÉDIA'
        })
    
    def gerar_relatorio_completo(self, inventario: Dict[str, int], parametros_usuario: Dict[str, Any]) -> str:
        """
        Gera relatório completo em HTML
        """
        analise = self.analisar_fazenda(inventario, parametros_usuario)
        
        if 'erro' in analise:
            return f"<div class='alert alert-danger'>Erro: {analise['erro']}</div>"
        
        perfil = analise['perfil_detectado']
        projecao = analise['projecao']
        recomendacoes = analise['recomendacoes']
        
        html = f"""
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4><i class="fas fa-robot"></i> Análise IA - {perfil['nome']}</h4>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h5><i class="fas fa-info-circle"></i> Perfil Detectado</h5>
                        <p><strong>Tipo:</strong> {perfil['tipo']}</p>
                        <p><strong>Descrição:</strong> {perfil['descricao']}</p>
                        
                        <h6>Características:</h6>
                        <ul>
        """
        
        for caracteristica in perfil['caracteristicas']:
            html += f"<li>{caracteristica}</li>"
        
        html += f"""
                        </ul>
                        
                        <h6>Categorias Principais:</h6>
                        <ul>
        """
        
        for categoria in perfil['categorias_principais']:
            html += f"<li>{categoria}</li>"
        
        html += f"""
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h5><i class="fas fa-chart-line"></i> Projeção Financeira</h5>
                        <p><strong>Receita Total ({projecao['anos_projecao']} anos):</strong> R$ {projecao['receita_total']:,.2f}</p>
                        <p><strong>Despesa Total ({projecao['anos_projecao']} anos):</strong> R$ {projecao['despesa_total']:,.2f}</p>
                        <p><strong>Lucro Total ({projecao['anos_projecao']} anos):</strong> R$ {projecao['lucro_total']:,.2f}</p>
                        <p><strong>Crescimento do Rebanho:</strong> {projecao['crescimento_rebanho']:.1f}%</p>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-12">
                        <h5><i class="fas fa-lightbulb"></i> Recomendações</h5>
                        <ul>
        """
        
        for recomendacao in recomendacoes:
            html += f"<li>{recomendacao}</li>"
        
        html += """
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html

# Instância global da IA
ia_pecuaria = IAPecuariaAvancada()



