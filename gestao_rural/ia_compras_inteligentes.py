# -*- coding: utf-8 -*-
"""
IA para Compras Inteligentes
Detecta necessidades, melhor época, preços e oportunidades de compra
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Tuple, Optional
import statistics


class IAComprasInteligentes:
    """
    IA que analisa o rebanho e sugere compras inteligentes baseadas em:
    - Estoque mínimo por categoria
    - Sazonalidade de preços
    - Previsão de necessidade futura
    - Oportunidades de mercado
    - ROI esperado
    """
    
    def __init__(self):
        # Preços médios de mercado por categoria (R$)
        self.precos_mercado = {
            'Bezerros (0-12m)': {
                'preco_medio': Decimal('1800.00'),
                'preco_minimo': Decimal('1500.00'),
                'preco_maximo': Decimal('2200.00'),
                'melhor_mes_compra': [4, 5, 6],  # Abril a junho
                'pior_mes_compra': [11, 12, 1],  # Nov, dez, jan
            },
            'Bezerras (0-12m)': {
                'preco_medio': Decimal('1600.00'),
                'preco_minimo': Decimal('1300.00'),
                'preco_maximo': Decimal('2000.00'),
                'melhor_mes_compra': [4, 5, 6],
                'pior_mes_compra': [11, 12, 1],
            },
            'Garrotes (12-24m)': {
                'preco_medio': Decimal('3200.00'),
                'preco_minimo': Decimal('2800.00'),
                'preco_maximo': Decimal('3800.00'),
                'melhor_mes_compra': [7, 8, 9],
                'pior_mes_compra': [12, 1, 2],
            },
            'Novilhas (12-24m)': {
                'preco_medio': Decimal('3800.00'),
                'preco_minimo': Decimal('3300.00'),
                'preco_maximo': Decimal('4500.00'),
                'melhor_mes_compra': [7, 8, 9],
                'pior_mes_compra': [12, 1, 2],
            },
            'Bois Magros (24-36m)': {
                'preco_medio': Decimal('3800.00'),
                'preco_minimo': Decimal('3200.00'),
                'preco_maximo': Decimal('4500.00'),
                'melhor_mes_compra': [8, 9, 10],
                'pior_mes_compra': [1, 2, 3],
            },
            'Multíparas (>36m)': {
                'preco_medio': Decimal('4500.00'),
                'preco_minimo': Decimal('3800.00'),
                'preco_maximo': Decimal('5500.00'),
                'melhor_mes_compra': [5, 6, 7],
                'pior_mes_compra': [10, 11, 12],
            },
        }
        
        # Estoque mínimo recomendado por categoria (% do rebanho total)
        self.estoque_minimo_recomendado = {
            'Bezerros (0-12m)': 0.15,  # 15% do rebanho
            'Bezerras (0-12m)': 0.15,
            'Garrotes (12-24m)': 0.12,
            'Novilhas (12-24m)': 0.12,
            'Bois Magros (24-36m)': 0.10,
            'Multíparas (>36m)': 0.20,  # 20% - base reprodutiva
            'Primíparas (24-36m)': 0.10,
        }
    
    def analisar_necessidade_compras(
        self,
        inventario_atual: Dict[str, int],
        perfil_fazenda: str,
        mes_atual: int
    ) -> List[Dict[str, Any]]:
        """
        Analisa inventário e retorna sugestões inteligentes de compra
        """
        total_rebanho = sum(inventario_atual.values())
        sugestoes = []
        
        # Para cada categoria, analisar necessidade
        for categoria, dados_mercado in self.precos_mercado.items():
            # Quantidade atual
            quantidade_atual = inventario_atual.get(categoria, 0)
            
            # Quantidade mínima recomendada
            quantidade_minima = int(
                total_rebanho * self.estoque_minimo_recomendado.get(categoria, 0.10)
            )
            
            # Verificar se está abaixo do mínimo
            deficit = quantidade_minima - quantidade_atual
            
            if deficit > 0:
                # Calcular prioridade da compra
                prioridade = self._calcular_prioridade_compra(
                    categoria,
                    deficit,
                    quantidade_minima,
                    mes_atual,
                    perfil_fazenda
                )
                
                # Calcular melhor momento e preço
                momento_compra = self._calcular_melhor_momento_compra(
                    categoria,
                    mes_atual,
                    dados_mercado
                )
                
                # Calcular ROI esperado
                roi_esperado = self._calcular_roi_esperado(
                    categoria,
                    momento_compra['preco_estimado'],
                    perfil_fazenda
                )
                
                sugestao = {
                    'categoria': categoria,
                    'quantidade_atual': quantidade_atual,
                    'quantidade_minima': quantidade_minima,
                    'deficit': deficit,
                    'quantidade_sugerida': deficit + int(deficit * 0.10),  # +10% margem
                    'prioridade': prioridade,
                    'momento_compra': momento_compra,
                    'roi_esperado': roi_esperado,
                    'justificativa': self._gerar_justificativa_compra(
                        categoria,
                        deficit,
                        prioridade,
                        momento_compra
                    )
                }
                
                sugestoes.append(sugestao)
        
        # Ordenar por prioridade (maior primeiro)
        sugestoes.sort(key=lambda x: x['prioridade'], reverse=True)
        
        return sugestoes
    
    def detectar_oportunidades_mercado(
        self,
        preco_atual_categoria: Dict[str, Decimal],
        mes_atual: int
    ) -> List[Dict[str, Any]]:
        """
        Detecta oportunidades de compra quando preços estão abaixo da média
        """
        oportunidades = []
        
        for categoria, preco_atual in preco_atual_categoria.items():
            if categoria not in self.precos_mercado:
                continue
            
            dados_mercado = self.precos_mercado[categoria]
            preco_medio = dados_mercado['preco_medio']
            
            # Calcular desconto percentual
            desconto = ((preco_medio - preco_atual) / preco_medio) * 100
            
            # Oportunidade se desconto > 10%
            if desconto >= 10:
                # Avaliar se é bom momento (sazonalidade)
                momento = self._avaliar_momento_sazonal(categoria, mes_atual)
                
                oportunidade = {
                    'categoria': categoria,
                    'preco_atual': float(preco_atual),
                    'preco_medio': float(preco_medio),
                    'desconto_percentual': float(desconto),
                    'economia_por_cabeca': float(preco_medio - preco_atual),
                    'momento_sazonal': momento['classificacao'],
                    'score_oportunidade': self._calcular_score_oportunidade(
                        desconto,
                        momento['score'],
                        mes_atual
                    ),
                    'recomendacao': self._gerar_recomendacao_oportunidade(
                        categoria,
                        desconto,
                        momento
                    )
                }
                
                oportunidades.append(oportunidade)
        
        # Ordenar por score (maior primeiro)
        oportunidades.sort(key=lambda x: x['score_oportunidade'], reverse=True)
        
        return oportunidades
    
    def calcular_investimento_necessario(
        self,
        sugestoes_compra: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calcula investimento total necessário para as compras sugeridas
        """
        investimento_total = Decimal('0.00')
        investimento_por_categoria = {}
        roi_medio_ponderado = 0
        
        for sugestao in sugestoes_compra:
            categoria = sugestao['categoria']
            quantidade = sugestao['quantidade_sugerida']
            preco_unitario = sugestao['momento_compra']['preco_estimado']
            
            investimento_categoria = quantidade * preco_unitario
            investimento_por_categoria[categoria] = {
                'quantidade': quantidade,
                'preco_unitario': float(preco_unitario),
                'investimento_total': float(investimento_categoria),
                'roi_esperado': sugestao['roi_esperado']
            }
            
            investimento_total += investimento_categoria
            roi_medio_ponderado += sugestao['roi_esperado'] * float(investimento_categoria)
        
        if investimento_total > 0:
            roi_medio_ponderado /= float(investimento_total)
        
        return {
            'investimento_total': float(investimento_total),
            'investimento_por_categoria': investimento_por_categoria,
            'roi_medio_esperado': roi_medio_ponderado,
            'retorno_estimado_12_meses': float(investimento_total * (roi_medio_ponderado / 100)),
            'numero_categorias': len(investimento_por_categoria),
            'total_animais': sum(cat['quantidade'] for cat in investimento_por_categoria.values())
        }
    
    def _calcular_prioridade_compra(
        self,
        categoria: str,
        deficit: int,
        quantidade_minima: int,
        mes_atual: int,
        perfil_fazenda: str
    ) -> float:
        """
        Calcula prioridade da compra (0-100)
        Maior número = maior prioridade
        """
        # Base: quanto maior o deficit relativo, maior a prioridade
        prioridade_base = (deficit / quantidade_minima) * 50
        
        # Ajuste por categoria estratégica
        if 'Multíparas' in categoria or 'Primíparas' in categoria:
            prioridade_base *= 1.3  # Matrizes são prioritárias
        elif 'Bezerro' in categoria or 'Bezerra' in categoria:
            prioridade_base *= 1.2  # Animais jovens também
        
        # Ajuste por perfil da fazenda
        if perfil_fazenda == 'SO_CRIA' and 'Multíparas' in categoria:
            prioridade_base *= 1.4
        elif perfil_fazenda == 'SO_RECRIA' and 'Bezerro' in categoria:
            prioridade_base *= 1.3
        elif perfil_fazenda == 'SO_ENGORDA' and 'Garrotes' in categoria:
            prioridade_base *= 1.3
        
        # Ajuste por sazonalidade (se está no melhor mês para comprar)
        if categoria in self.precos_mercado:
            melhores_meses = self.precos_mercado[categoria]['melhor_mes_compra']
            if mes_atual in melhores_meses:
                prioridade_base *= 1.15  # Bônus por momento
        
        return min(100, prioridade_base)
    
    def _calcular_melhor_momento_compra(
        self,
        categoria: str,
        mes_atual: int,
        dados_mercado: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula o melhor momento para realizar a compra
        """
        melhores_meses = dados_mercado['melhor_mes_compra']
        piores_meses = dados_mercado['pior_mes_compra']
        preco_medio = dados_mercado['preco_medio']
        preco_minimo = dados_mercado['preco_minimo']
        preco_maximo = dados_mercado['preco_maximo']
        
        # Estimar preço atual baseado no mês
        if mes_atual in melhores_meses:
            # Preço tende a ser mais baixo
            preco_estimado = preco_minimo + (preco_medio - preco_minimo) * Decimal('0.3')
            momento = 'ÓTIMO'
        elif mes_atual in piores_meses:
            # Preço tende a ser mais alto
            preco_estimado = preco_medio + (preco_maximo - preco_medio) * Decimal('0.5')
            momento = 'RUIM'
        else:
            # Preço médio
            preco_estimado = preco_medio
            momento = 'REGULAR'
        
        # Calcular economia se esperar pelo melhor mês
        if mes_atual not in melhores_meses:
            meses_ate_melhor = self._calcular_meses_ate_proximo(mes_atual, melhores_meses)
            economia_esperando = preco_estimado - preco_minimo
        else:
            meses_ate_melhor = 0
            economia_esperando = Decimal('0.00')
        
        return {
            'momento': momento,
            'mes_atual': mes_atual,
            'preco_estimado': preco_estimado,
            'melhores_meses': melhores_meses,
            'meses_ate_melhor_momento': meses_ate_melhor,
            'economia_esperando_por_cabeca': economia_esperando,
            'recomendacao_timing': self._gerar_recomendacao_timing(
                momento,
                meses_ate_melhor,
                economia_esperando
            )
        }
    
    def _calcular_meses_ate_proximo(self, mes_atual: int, meses_alvo: List[int]) -> int:
        """Calcula quantos meses faltam até o próximo mês alvo"""
        meses_ate = []
        for mes_alvo in meses_alvo:
            if mes_alvo >= mes_atual:
                meses_ate.append(mes_alvo - mes_atual)
            else:
                meses_ate.append((12 - mes_atual) + mes_alvo)
        
        return min(meses_ate)
    
    def _calcular_roi_esperado(
        self,
        categoria: str,
        preco_compra: Decimal,
        perfil_fazenda: str
    ) -> float:
        """
        Calcula ROI esperado em 12 meses
        """
        # ROI base por categoria e perfil
        roi_base = {
            'SO_CRIA': {
                'Bezerros (0-12m)': 0,  # Cria não compra bezerros
                'Bezerras (0-12m)': 0,
                'Multíparas (>36m)': 25,  # 25% ROI com matrizes
                'Primíparas (24-36m)': 22,
            },
            'SO_RECRIA': {
                'Bezerros (0-12m)': 18,  # Compra bezerros, vende garrotes
                'Bezerras (0-12m)': 18,
                'Garrotes (12-24m)': 0,  # Não compra garrotes
                'Novilhas (12-24m)': 0,
            },
            'SO_ENGORDA': {
                'Garrotes (12-24m)': 15,  # Compra garrotes, vende bois
                'Novilhas (12-24m)': 15,
                'Bois Magros (24-36m)': 12,  # Engorda final
            },
            'CICLO_COMPLETO': {
                'Bezerros (0-12m)': 8,
                'Bezerras (0-12m)': 8,
                'Garrotes (12-24m)': 10,
                'Novilhas (12-24m)': 12,
                'Multíparas (>36m)': 20,
                'Primíparas (24-36m)': 18,
            }
        }
        
        # Obter ROI base
        roi = roi_base.get(perfil_fazenda, {}).get(categoria, 10.0)
        
        # Ajustar ROI baseado no preço de compra
        # Se comprar abaixo do preço médio, ROI aumenta
        if categoria in self.precos_mercado:
            preco_medio = self.precos_mercado[categoria]['preco_medio']
            if preco_compra < preco_medio:
                desconto_percentual = ((preco_medio - preco_compra) / preco_medio) * 100
                roi += desconto_percentual * 0.5  # Cada 1% de desconto adiciona 0.5% ao ROI
        
        return round(roi, 2)
    
    def _avaliar_momento_sazonal(self, categoria: str, mes_atual: int) -> Dict[str, Any]:
        """Avalia o momento sazonal para compra"""
        if categoria not in self.precos_mercado:
            return {'classificacao': 'DESCONHECIDO', 'score': 50}
        
        dados = self.precos_mercado[categoria]
        melhores_meses = dados['melhor_mes_compra']
        piores_meses = dados['pior_mes_compra']
        
        if mes_atual in melhores_meses:
            return {'classificacao': 'ÓTIMO', 'score': 90}
        elif mes_atual in piores_meses:
            return {'classificacao': 'RUIM', 'score': 30}
        else:
            return {'classificacao': 'REGULAR', 'score': 60}
    
    def _calcular_score_oportunidade(
        self,
        desconto: float,
        momento_score: int,
        mes_atual: int
    ) -> float:
        """Calcula score final da oportunidade (0-100)"""
        # Peso do desconto: 60%
        score_desconto = min(100, desconto * 5) * 0.6
        
        # Peso do momento sazonal: 40%
        score_momento = momento_score * 0.4
        
        return score_desconto + score_momento
    
    def _gerar_justificativa_compra(
        self,
        categoria: str,
        deficit: int,
        prioridade: float,
        momento_compra: Dict[str, Any]
    ) -> str:
        """Gera justificativa para a compra sugerida"""
        justificativa = f"Déficit de {deficit} animais em {categoria}. "
        
        if prioridade >= 80:
            justificativa += "URGENTE: "
        elif prioridade >= 60:
            justificativa += "ALTA PRIORIDADE: "
        
        justificativa += f"Momento para compra: {momento_compra['momento']}. "
        
        if momento_compra['momento'] == 'ÓTIMO':
            justificativa += "É o melhor período do ano para essa categoria!"
        elif momento_compra['meses_ate_melhor_momento'] > 0:
            justificativa += f"Aguardar {momento_compra['meses_ate_melhor_momento']} meses pode economizar R$ {momento_compra['economia_esperando_por_cabeca']:.2f}/cabeça."
        
        return justificativa
    
    def _gerar_recomendacao_timing(
        self,
        momento: str,
        meses_ate_melhor: int,
        economia_esperando: Decimal
    ) -> str:
        """Gera recomendação sobre o timing da compra"""
        if momento == 'ÓTIMO':
            return "COMPRE AGORA! Este é o melhor momento do ano."
        elif momento == 'RUIM' and meses_ate_melhor <= 3:
            return f"AGUARDE {meses_ate_melhor} meses. Economia estimada: R$ {economia_esperando:.2f}/cabeça."
        elif momento == 'RUIM' and meses_ate_melhor > 3:
            return "Momento ruim, mas se houver urgência, pode comprar. Considere negociar o preço."
        else:
            return "Momento regular. Pode comprar se necessário ou aguardar pelo melhor momento."
    
    def _gerar_recomendacao_oportunidade(
        self,
        categoria: str,
        desconto: float,
        momento: Dict[str, Any]
    ) -> str:
        """Gera recomendação para oportunidade detectada"""
        if desconto >= 20 and momento['classificacao'] == 'ÓTIMO':
            return f"🔥 OPORTUNIDADE EXCEPCIONAL! {desconto:.1f}% abaixo da média em época favorável. COMPRE JÁ!"
        elif desconto >= 15:
            return f"✅ BOA OPORTUNIDADE! {desconto:.1f}% de desconto. Recomendado comprar."
        elif desconto >= 10:
            return f"💡 Oportunidade interessante. {desconto:.1f}% abaixo da média. Considere comprar."
        else:
            return "Preço próximo da média. Avaliar necessidade."


# Instância global da IA
ia_compras_inteligentes = IAComprasInteligentes()

