# -*- coding: utf-8 -*-
"""
IA para Vendas Otimizadas
Calcula ponto ideal de venda, prevê preços e identifica melhor momento
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Tuple, Optional
import statistics


class IAVendasOtimizadas:
    """
    IA que otimiza vendas baseada em:
    - Ponto ideal de venda (peso × idade × preço)
    - Previsão de preços futuros
    - Sazonalidade de mercado
    - Margem de lucro por categoria
    - Simulação de cenários
    """
    
    def __init__(self):
        # Dados de mercado por categoria
        self.dados_vendas = {
            'Bezerros (0-12m)': {
                'idade_ideal_meses': 8,  # 8 meses
                'peso_ideal_kg': 220,
                'preco_medio_kg': Decimal('17.00'),
                'preco_medio_cabeca': Decimal('2000.00'),
                'melhor_mes_venda': [10, 11, 12],  # Out, nov, dez
                'pior_mes_venda': [4, 5, 6],
                'margem_lucro_tipica': 0.25,  # 25%
                'tendencia_preco': 'ESTÁVEL',
            },
            'Bezerras (0-12m)': {
                'idade_ideal_meses': 8,
                'peso_ideal_kg': 200,
                'preco_medio_kg': Decimal('16.00'),
                'preco_medio_cabeca': Decimal('1800.00'),
                'melhor_mes_venda': [10, 11, 12],
                'pior_mes_venda': [4, 5, 6],
                'margem_lucro_tipica': 0.25,
                'tendencia_preco': 'ESTÁVEL',
            },
            'Garrotes (12-24m)': {
                'idade_ideal_meses': 18,
                'peso_ideal_kg': 380,
                'preco_medio_kg': Decimal('18.00'),
                'preco_medio_cabeca': Decimal('3500.00'),
                'melhor_mes_venda': [1, 2, 3],  # Jan, fev, mar
                'pior_mes_venda': [7, 8, 9],
                'margem_lucro_tipica': 0.20,
                'tendencia_preco': 'ALTA',
            },
            'Novilhas (12-24m)': {
                'idade_ideal_meses': 24,
                'peso_ideal_kg': 420,
                'preco_medio_kg': Decimal('19.00'),
                'preco_medio_cabeca': Decimal('4000.00'),
                'melhor_mes_venda': [1, 2, 3],
                'pior_mes_venda': [7, 8, 9],
                'margem_lucro_tipica': 0.22,
                'tendencia_preco': 'ALTA',
            },
            'Bois Magros (24-36m)': {
                'idade_ideal_meses': 30,
                'peso_ideal_kg': 480,
                'preco_medio_kg': Decimal('20.00'),
                'preco_medio_cabeca': Decimal('4500.00'),
                'melhor_mes_venda': [3, 4, 5],  # Mar, abr, mai
                'pior_mes_venda': [10, 11, 12],
                'margem_lucro_tipica': 0.18,
                'tendencia_preco': 'ALTA',
            },
            'Vacas de Descarte': {
                'idade_ideal_meses': 120,  # 10 anos+
                'peso_ideal_kg': 450,
                'preco_medio_kg': Decimal('14.00'),
                'preco_medio_cabeca': Decimal('3000.00'),
                'melhor_mes_venda': [5, 6, 7],
                'pior_mes_venda': [11, 12, 1],
                'margem_lucro_tipica': 0.10,
                'tendencia_preco': 'ESTÁVEL',
            },
        }
    
    def analisar_oportunidades_venda(
        self,
        inventario_atual: Dict[str, int],
        idade_media_categoria: Dict[str, int],  # meses
        peso_medio_categoria: Dict[str, float],  # kg
        mes_atual: int,
        perfil_fazenda: str = 'CICLO_COMPLETO'
    ) -> List[Dict[str, Any]]:
        """
        Analisa inventário e identifica melhores oportunidades de venda
        """
        oportunidades = []
        
        for categoria, quantidade in inventario_atual.items():
            if quantidade == 0 or categoria not in self.dados_vendas:
                continue
            
            dados_venda = self.dados_vendas[categoria]
            idade_atual = idade_media_categoria.get(categoria, dados_venda['idade_ideal_meses'])
            peso_atual = peso_medio_categoria.get(categoria, dados_venda['peso_ideal_kg'])
            
            # Calcular ponto ideal de venda
            ponto_ideal = self._calcular_ponto_ideal_venda(
                categoria,
                idade_atual,
                peso_atual,
                dados_venda
            )
            
            # Calcular momento de venda
            momento_venda = self._avaliar_momento_venda(
                categoria,
                mes_atual,
                dados_venda
            )
            
            # Prever preço futuro (3 meses)
            previsao_preco = self._prever_preco_futuro(
                categoria,
                mes_atual,
                dados_venda
            )
            
            # Calcular margem de lucro esperada
            margem_lucro = self._calcular_margem_lucro(
                categoria,
                peso_atual,
                momento_venda['preco_estimado'],
                perfil_fazenda
            )
            
            # Simular cenários
            cenarios = self._simular_cenarios_venda(
                quantidade,
                peso_atual,
                momento_venda['preco_estimado'],
                previsao_preco
            )
            
            oportunidade = {
                'categoria': categoria,
                'quantidade_disponivel': quantidade,
                'idade_atual_meses': idade_atual,
                'peso_atual_kg': peso_atual,
                'ponto_ideal': ponto_ideal,
                'momento_venda': momento_venda,
                'previsao_preco': previsao_preco,
                'margem_lucro': margem_lucro,
                'cenarios': cenarios,
                'recomendacao': self._gerar_recomendacao_venda(
                    ponto_ideal,
                    momento_venda,
                    margem_lucro
                ),
                'score_oportunidade': self._calcular_score_venda(
                    ponto_ideal['score'],
                    momento_venda['score'],
                    margem_lucro['percentual']
                )
            }
            
            oportunidades.append(oportunidade)
        
        # Ordenar por score (maior primeiro)
        oportunidades.sort(key=lambda x: x['score_oportunidade'], reverse=True)
        
        return oportunidades
    
    def calcular_receita_estimada(
        self,
        oportunidades_venda: List[Dict[str, Any]],
        percentual_venda: float = 1.0  # 100% = vender tudo
    ) -> Dict[str, Any]:
        """
        Calcula receita estimada das vendas sugeridas
        """
        receita_total = Decimal('0.00')
        lucro_total = Decimal('0.00')
        receita_por_categoria = {}
        
        for oportunidade in oportunidades_venda:
            categoria = oportunidade['categoria']
            quantidade_vender = int(oportunidade['quantidade_disponivel'] * percentual_venda)
            
            if quantidade_vender == 0:
                continue
            
            preco_unitario = oportunidade['momento_venda']['preco_estimado']
            receita_categoria = quantidade_vender * preco_unitario
            
            # Calcular custo (baseado na margem de lucro)
            margem = oportunidade['margem_lucro']['percentual'] / 100
            custo_categoria = receita_categoria * (1 - margem)
            lucro_categoria = receita_categoria - custo_categoria
            
            receita_por_categoria[categoria] = {
                'quantidade': quantidade_vender,
                'preco_unitario': float(preco_unitario),
                'receita_total': float(receita_categoria),
                'custo_total': float(custo_categoria),
                'lucro_total': float(lucro_categoria),
                'margem_percentual': oportunidade['margem_lucro']['percentual']
            }
            
            receita_total += receita_categoria
            lucro_total += lucro_categoria
        
        margem_media = (lucro_total / receita_total * 100) if receita_total > 0 else 0
        
        return {
            'receita_total': float(receita_total),
            'custo_total': float(receita_total - lucro_total),
            'lucro_total': float(lucro_total),
            'margem_media_percentual': float(margem_media),
            'receita_por_categoria': receita_por_categoria,
            'numero_categorias': len(receita_por_categoria),
            'total_animais': sum(cat['quantidade'] for cat in receita_por_categoria.values())
        }
    
    def _calcular_ponto_ideal_venda(
        self,
        categoria: str,
        idade_atual: int,
        peso_atual: float,
        dados_venda: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula se o animal está no ponto ideal de venda
        Score: 0-100
        """
        idade_ideal = dados_venda['idade_ideal_meses']
        peso_ideal = dados_venda['peso_ideal_kg']
        
        # Score de idade (quanto mais próximo do ideal, melhor)
        diferenca_idade = abs(idade_atual - idade_ideal)
        if diferenca_idade == 0:
            score_idade = 100
        elif diferenca_idade <= 2:
            score_idade = 90 - (diferenca_idade * 10)
        elif diferenca_idade <= 4:
            score_idade = 70 - ((diferenca_idade - 2) * 15)
        else:
            score_idade = max(30, 70 - (diferenca_idade * 5))
        
        # Score de peso (quanto mais próximo do ideal, melhor)
        diferenca_peso = abs(peso_atual - peso_ideal) / peso_ideal
        if diferenca_peso <= 0.05:  # +/- 5%
            score_peso = 100
        elif diferenca_peso <= 0.10:  # +/- 10%
            score_peso = 85
        elif diferenca_peso <= 0.20:  # +/- 20%
            score_peso = 70
        else:
            score_peso = max(40, 70 - (diferenca_peso * 100))
        
        # Score final (média ponderada: idade 40%, peso 60%)
        score_final = (score_idade * 0.4) + (score_peso * 0.6)
        
        # Classificação
        if score_final >= 90:
            classificacao = 'ÓTIMO - Ponto ideal de venda'
        elif score_final >= 75:
            classificacao = 'BOM - Próximo do ideal'
        elif score_final >= 60:
            classificacao = 'REGULAR - Pode melhorar'
        else:
            classificacao = 'AGUARDAR - Ainda não está no ponto'
        
        return {
            'score': score_final,
            'classificacao': classificacao,
            'idade_atual': idade_atual,
            'idade_ideal': idade_ideal,
            'peso_atual': peso_atual,
            'peso_ideal': peso_ideal,
            'diferenca_idade_meses': idade_atual - idade_ideal,
            'diferenca_peso_kg': peso_atual - peso_ideal,
            'recomendacao_ponto': self._gerar_recomendacao_ponto(
                score_final,
                idade_atual,
                idade_ideal,
                peso_atual,
                peso_ideal
            )
        }
    
    def _avaliar_momento_venda(
        self,
        categoria: str,
        mes_atual: int,
        dados_venda: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Avalia se é bom momento sazonal para vender
        """
        melhores_meses = dados_venda['melhor_mes_venda']
        piores_meses = dados_venda['pior_mes_venda']
        preco_medio = dados_venda['preco_medio_cabeca']
        
        # Estimar preço baseado no mês
        if mes_atual in melhores_meses:
            preco_estimado = preco_medio * Decimal('1.15')  # +15%
            momento = 'ÓTIMO'
            score = 95
        elif mes_atual in piores_meses:
            preco_estimado = preco_medio * Decimal('0.88')  # -12%
            momento = 'RUIM'
            score = 40
        else:
            preco_estimado = preco_medio
            momento = 'REGULAR'
            score = 70
        
        # Meses até melhor momento
        if mes_atual not in melhores_meses:
            meses_ate_melhor = self._calcular_meses_ate_proximo(mes_atual, melhores_meses)
            ganho_esperando = (preco_medio * Decimal('1.15')) - preco_estimado
        else:
            meses_ate_melhor = 0
            ganho_esperando = Decimal('0.00')
        
        return {
            'momento': momento,
            'score': score,
            'mes_atual': mes_atual,
            'preco_estimado': preco_estimado,
            'preco_medio': preco_medio,
            'melhores_meses': melhores_meses,
            'meses_ate_melhor_momento': meses_ate_melhor,
            'ganho_esperando_por_cabeca': ganho_esperando,
            'recomendacao_timing': self._gerar_recomendacao_timing_venda(
                momento,
                meses_ate_melhor,
                ganho_esperando
            )
        }
    
    def _prever_preco_futuro(
        self,
        categoria: str,
        mes_atual: int,
        dados_venda: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prevê preço para os próximos 3 meses
        """
        preco_atual = dados_venda['preco_medio_cabeca']
        tendencia = dados_venda['tendencia_preco']
        
        previsoes = {}
        
        for i in range(1, 4):  # Próximos 3 meses
            mes_futuro = ((mes_atual + i - 1) % 12) + 1
            
            # Ajuste sazonal
            if mes_futuro in dados_venda['melhor_mes_venda']:
                ajuste_sazonal = 1.15
            elif mes_futuro in dados_venda['pior_mes_venda']:
                ajuste_sazonal = 0.88
            else:
                ajuste_sazonal = 1.0
            
            # Ajuste de tendência
            if tendencia == 'ALTA':
                ajuste_tendencia = 1 + (0.005 * i)  # +0.5% ao mês
            elif tendencia == 'BAIXA':
                ajuste_tendencia = 1 - (0.005 * i)  # -0.5% ao mês
            else:
                ajuste_tendencia = 1.0
            
            preco_previsto = preco_atual * Decimal(str(ajuste_sazonal * ajuste_tendencia))
            
            previsoes[f'mes_{i}'] = {
                'mes': mes_futuro,
                'preco_previsto': preco_previsto,
                'diferenca_atual': preco_previsto - preco_atual,
                'percentual_mudanca': float(((preco_previsto - preco_atual) / preco_atual) * 100)
            }
        
        return previsoes
    
    def _calcular_margem_lucro(
        self,
        categoria: str,
        peso_kg: float,
        preco_venda: Decimal,
        perfil_fazenda: str
    ) -> Dict[str, Any]:
        """
        Calcula margem de lucro estimada
        """
        # Custos base por categoria (R$/kg de peso vivo)
        custos_base = {
            'Bezerros (0-12m)': Decimal('12.00'),
            'Bezerras (0-12m)': Decimal('11.50'),
            'Garrotes (12-24m)': Decimal('14.00'),
            'Novilhas (12-24m)': Decimal('14.50'),
            'Bois Magros (24-36m)': Decimal('15.50'),
            'Vacas de Descarte': Decimal('10.00'),
        }
        
        custo_kg = custos_base.get(categoria, Decimal('12.00'))
        custo_total = custo_kg * Decimal(str(peso_kg))
        
        lucro = preco_venda - custo_total
        margem_percentual = (lucro / preco_venda * 100) if preco_venda > 0 else 0
        
        # Classificar margem
        if margem_percentual >= 25:
            classificacao = 'EXCELENTE'
        elif margem_percentual >= 20:
            classificacao = 'BOA'
        elif margem_percentual >= 15:
            classificacao = 'REGULAR'
        else:
            classificacao = 'BAIXA'
        
        return {
            'custo_total': custo_total,
            'preco_venda': preco_venda,
            'lucro': lucro,
            'percentual': float(margem_percentual),
            'classificacao': classificacao
        }
    
    def _simular_cenarios_venda(
        self,
        quantidade: int,
        peso_kg: float,
        preco_atual: Decimal,
        previsao_futura: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Simula cenários: vender agora vs esperar
        """
        receita_agora = quantidade * preco_atual
        
        cenarios = {
            'vender_agora': {
                'quantidade': quantidade,
                'preco_unitario': float(preco_atual),
                'receita_total': float(receita_agora)
            }
        }
        
        for periodo, previsao in previsao_futura.items():
            receita_futura = quantidade * previsao['preco_previsto']
            diferenca = receita_futura - receita_agora
            
            cenarios[f'esperar_{periodo}'] = {
                'mes': previsao['mes'],
                'quantidade': quantidade,
                'preco_unitario': float(previsao['preco_previsto']),
                'receita_total': float(receita_futura),
                'diferenca_vs_agora': float(diferenca),
                'vale_a_pena': diferenca > (receita_agora * Decimal('0.03'))  # > 3%
            }
        
        return cenarios
    
    def _calcular_meses_ate_proximo(self, mes_atual: int, meses_alvo: List[int]) -> int:
        """Calcula quantos meses faltam até o próximo mês alvo"""
        meses_ate = []
        for mes_alvo in meses_alvo:
            if mes_alvo >= mes_atual:
                meses_ate.append(mes_alvo - mes_atual)
            else:
                meses_ate.append((12 - mes_atual) + mes_alvo)
        return min(meses_ate)
    
    def _gerar_recomendacao_ponto(
        self,
        score: float,
        idade_atual: int,
        idade_ideal: int,
        peso_atual: float,
        peso_ideal: float
    ) -> str:
        """Gera recomendação sobre o ponto de venda"""
        if score >= 90:
            return "Animal no ponto ideal! Considere vender."
        elif idade_atual < idade_ideal and peso_atual < peso_ideal:
            return f"Aguardar. Faltam {idade_ideal - idade_atual} meses e {peso_ideal - peso_atual:.0f}kg."
        elif peso_atual >= peso_ideal * 1.1:
            return "Animal acima do peso ideal. Venda recomendada para evitar custos extras."
        else:
            return "Próximo do ponto ideal. Avaliar momento de mercado."
    
    def _gerar_recomendacao_timing_venda(
        self,
        momento: str,
        meses_ate_melhor: int,
        ganho_esperando: Decimal
    ) -> str:
        """Gera recomendação sobre timing da venda"""
        if momento == 'ÓTIMO':
            return "VENDA AGORA! Melhor época do ano para essa categoria."
        elif momento == 'RUIM' and meses_ate_melhor <= 2:
            return f"AGUARDE {meses_ate_melhor} meses. Ganho esperado: R$ {ganho_esperando:.2f}/cabeça."
        elif momento == 'RUIM':
            return "Momento ruim. Se houver urgência, negocie bem o preço."
        else:
            return "Momento regular. Pode vender ou aguardar melhor época."
    
    def _gerar_recomendacao_venda(
        self,
        ponto_ideal: Dict[str, Any],
        momento_venda: Dict[str, Any],
        margem_lucro: Dict[str, Any]
    ) -> str:
        """Gera recomendação final de venda"""
        score_ponto = ponto_ideal['score']
        score_momento = momento_venda['score']
        margem = margem_lucro['percentual']
        
        # Decisão baseada em scores combinados
        score_final = (score_ponto * 0.4) + (score_momento * 0.4) + (margem * 0.2)
        
        if score_final >= 85 and margem >= 20:
            return "🔥 VENDA RECOMENDADA! Ponto ideal, bom momento e boa margem."
        elif score_final >= 70:
            return "✅ BOA OPORTUNIDADE. Considere vender."
        elif score_final >= 50:
            return "💡 Oportunidade regular. Avaliar urgência."
        else:
            return "⏳ AGUARDAR. Melhorar ponto ou esperar melhor momento."
    
    def _calcular_score_venda(
        self,
        score_ponto: float,
        score_momento: float,
        margem: float
    ) -> float:
        """Calcula score final de oportunidade de venda (0-100)"""
        # Pesos: ponto 40%, momento 40%, margem 20%
        return (score_ponto * 0.4) + (score_momento * 0.4) + (margem * 0.2)


# Instância global da IA
ia_vendas_otimizadas = IAVendasOtimizadas()

