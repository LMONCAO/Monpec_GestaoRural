"""
Sistema de análise de cenários e risco para pecuária
Implementa análise de múltiplos cenários e gestão de risco
"""

from decimal import Decimal
from datetime import datetime, timedelta
from .ia_pecuaria_data import obter_cenario_risco, CENARIOS_RISCO

class IACenariosRisco:
    """Classe para análise de cenários e gestão de risco"""
    
    def __init__(self, propriedade, inventario_atual, dados_regiao):
        self.propriedade = propriedade
        self.inventario = inventario_atual
        self.dados_regiao = dados_regiao
    
    def analisar_cenarios_multiplos(self, estrategia_base):
        """Analisa múltiplos cenários de risco"""
        cenarios = {}
        
        for nome_cenario, dados_cenario in CENARIOS_RISCO.items():
            cenarios[nome_cenario] = self._simular_cenario(
                estrategia_base, 
                dados_cenario, 
                nome_cenario
            )
        
        return cenarios
    
    def _simular_cenario(self, estrategia_base, dados_cenario, nome_cenario):
        """Simula um cenário específico"""
        # Aplicar fatores do cenário
        fator_preco = dados_cenario['fator_preco']
        fator_produtividade = dados_cenario['fator_produtividade']
        fator_custos = dados_cenario['fator_custos']
        
        # Simular 5 anos
        projecao_anos = []
        for ano in range(1, 6):
            ano_data = self._calcular_ano_cenario(
                estrategia_base, 
                ano, 
                fator_preco, 
                fator_produtividade, 
                fator_custos
            )
            projecao_anos.append(ano_data)
        
        # Calcular métricas consolidadas
        metricas = self._calcular_metricas_cenario(projecao_anos)
        
        return {
            'nome': nome_cenario.title(),
            'probabilidade': dados_cenario['probabilidade'],
            'descricao': dados_cenario['descricao'],
            'projecao_anos': projecao_anos,
            'metricas': metricas,
            'recomendacoes': self._gerar_recomendacoes_cenario(nome_cenario, metricas)
        }
    
    def _calcular_ano_cenario(self, estrategia_base, ano, fator_preco, fator_produtividade, fator_custos):
        """Calcula dados para um ano específico do cenário"""
        # Crescimento do rebanho
        crescimento_base = estrategia_base.get('crescimento_anual', 10)
        crescimento_ajustado = crescimento_base * fator_produtividade
        
        # Receita
        receita_base = estrategia_base.get('receita_anual', 100000)
        receita_ajustada = receita_base * (1 + crescimento_ajustado/100) ** ano * fator_preco
        
        # Custos
        custos_base = estrategia_base.get('custos_anuais', 80000)
        custos_ajustados = custos_base * (1.05 ** ano) * fator_custos  # 5% inflação + fator cenário
        
        # Lucro
        lucro = receita_ajustada - custos_ajustados
        margem_lucro = (lucro / receita_ajustada * 100) if receita_ajustada > 0 else 0
        
        # ROI
        roi = (lucro / custos_ajustados * 100) if custos_ajustados > 0 else 0
        
        return {
            'ano': datetime.now().year + ano,
            'receita': receita_ajustada,
            'custos': custos_ajustados,
            'lucro': lucro,
            'margem_lucro': margem_lucro,
            'roi': roi,
            'crescimento_rebanho': crescimento_ajustado,
            'valor_rebanho': receita_ajustada * 0.8  # Estimativa
        }
    
    def _calcular_metricas_cenario(self, projecao_anos):
        """Calcula métricas consolidadas do cenário"""
        if not projecao_anos:
            return {}
        
        # Métricas de receita
        receita_total = sum(ano['receita'] for ano in projecao_anos)
        receita_media = receita_total / len(projecao_anos)
        crescimento_receita = self._calcular_crescimento_anual(
            projecao_anos[0]['receita'], 
            projecao_anos[-1]['receita'], 
            len(projecao_anos)
        )
        
        # Métricas de lucro
        lucro_total = sum(ano['lucro'] for ano in projecao_anos)
        lucro_medio = lucro_total / len(projecao_anos)
        margem_media = sum(ano['margem_lucro'] for ano in projecao_anos) / len(projecao_anos)
        
        # Métricas de risco
        lucros_anos = [ano['lucro'] for ano in projecao_anos]
        volatilidade = self._calcular_volatilidade(lucros_anos)
        valor_em_risco = self._calcular_var(lucros_anos, 5)  # VaR 5%
        
        # Métricas de crescimento
        crescimento_rebanho_medio = sum(ano['crescimento_rebanho'] for ano in projecao_anos) / len(projecao_anos)
        
        return {
            'receita_total_5_anos': receita_total,
            'receita_media_anual': receita_media,
            'crescimento_receita_anual': crescimento_receita,
            'lucro_total_5_anos': lucro_total,
            'lucro_medio_anual': lucro_medio,
            'margem_lucro_media': margem_media,
            'volatilidade_lucro': volatilidade,
            'valor_em_risco': valor_em_risco,
            'crescimento_rebanho_medio': crescimento_rebanho_medio,
            'score_risco': self._calcular_score_risco(volatilidade, valor_em_risco, margem_media)
        }
    
    def _calcular_crescimento_anual(self, valor_inicial, valor_final, anos):
        """Calcula crescimento anual composto"""
        if valor_inicial <= 0 or anos <= 0:
            return 0
        return ((valor_final / valor_inicial) ** (1/anos) - 1) * 100
    
    def _calcular_volatilidade(self, valores):
        """Calcula volatilidade (desvio padrão)"""
        if len(valores) < 2:
            return 0
        
        media = sum(valores) / len(valores)
        variancia = sum((x - media) ** 2 for x in valores) / (len(valores) - 1)
        return (variancia ** 0.5) / abs(media) * 100 if media != 0 else 0
    
    def _calcular_var(self, valores, percentil):
        """Calcula Value at Risk (VaR)"""
        if not valores:
            return 0
        
        valores_ordenados = sorted(valores)
        indice = int(len(valores_ordenados) * percentil / 100)
        return valores_ordenados[indice] if indice < len(valores_ordenados) else valores_ordenados[0]
    
    def _calcular_score_risco(self, volatilidade, var, margem_lucro):
        """Calcula score de risco (0-100, onde 100 = sem risco)"""
        score = 100
        
        # Penalizar alta volatilidade
        if volatilidade > 30:
            score -= 30
        elif volatilidade > 20:
            score -= 20
        elif volatilidade > 10:
            score -= 10
        
        # Penalizar VaR negativo
        if var < 0:
            score -= 25
        elif var < 10000:  # VaR baixo
            score -= 10
        
        # Bonificar margem de lucro alta
        if margem_lucro > 25:
            score += 10
        elif margem_lucro > 15:
            score += 5
        elif margem_lucro < 5:
            score -= 15
        
        return max(0, min(100, score))
    
    def _gerar_recomendacoes_cenario(self, nome_cenario, metricas):
        """Gera recomendações específicas para o cenário"""
        recomendacoes = []
        
        if nome_cenario == 'pessimista':
            if metricas['margem_lucro_media'] < 5:
                recomendacoes.append("Reduzir custos operacionais urgentemente")
                recomendacoes.append("Considerar venda de parte do rebanho")
            
            if metricas['volatilidade_lucro'] > 30:
                recomendacoes.append("Diversificar fontes de receita")
                recomendacoes.append("Implementar hedge de preços")
            
            recomendacoes.append("Manter reserva de emergência")
            recomendacoes.append("Revisar estratégia de crescimento")
        
        elif nome_cenario == 'otimista':
            if metricas['margem_lucro_media'] > 25:
                recomendacoes.append("Aproveitar para investir em melhorias")
                recomendacoes.append("Considerar expansão do rebanho")
            
            recomendacoes.append("Manter disciplina nos custos")
            recomendacoes.append("Planejar para tempos mais difíceis")
        
        else:  # realista
            if metricas['score_risco'] < 50:
                recomendacoes.append("Implementar medidas de redução de risco")
                recomendacoes.append("Diversificar estratégias de venda")
            
            if metricas['crescimento_rebanho_medio'] < 5:
                recomendacoes.append("Focar em melhorias de produtividade")
                recomendacoes.append("Revisar estratégia reprodutiva")
            
            recomendacoes.append("Monitorar indicadores regularmente")
            recomendacoes.append("Manter flexibilidade operacional")
        
        return recomendacoes
    
    def gerar_plano_contingencia(self, cenarios):
        """Gera plano de contingência baseado nos cenários"""
        plano = {
            'alertas_risco': self._identificar_alertas_risco(cenarios),
            'acoes_preventivas': self._definir_acoes_preventivas(cenarios),
            'acoes_corretivas': self._definir_acoes_corretivas(cenarios),
            'indicadores_monitoramento': self._definir_indicadores_monitoramento(),
            'niveis_alerta': self._definir_niveis_alerta()
        }
        
        return plano
    
    def _identificar_alertas_risco(self, cenarios):
        """Identifica alertas de risco baseados nos cenários"""
        alertas = []
        
        # Analisar cenário pessimista
        cenario_pessimista = cenarios.get('pessimista', {})
        if cenario_pessimista:
            metricas = cenario_pessimista.get('metricas', {})
            
            if metricas.get('margem_lucro_media', 0) < 0:
                alertas.append({
                    'tipo': 'CRITICO',
                    'descricao': 'Risco de prejuízo no cenário pessimista',
                    'acao': 'Revisar imediatamente custos e receitas'
                })
            
            if metricas.get('volatilidade_lucro', 0) > 40:
                alertas.append({
                    'tipo': 'ALTO',
                    'descricao': 'Alta volatilidade nos resultados',
                    'acao': 'Implementar medidas de estabilização'
                })
        
        # Analisar cenário realista
        cenario_realista = cenarios.get('realista', {})
        if cenario_realista:
            metricas = cenario_realista.get('metricas', {})
            
            if metricas.get('score_risco', 100) < 60:
                alertas.append({
                    'tipo': 'MEDIO',
                    'descricao': 'Score de risco moderado',
                    'acao': 'Monitorar indicadores mais de perto'
                })
        
        return alertas
    
    def _definir_acoes_preventivas(self, cenarios):
        """Define ações preventivas baseadas nos cenários"""
        acoes = []
        
        # Ações baseadas em cenário pessimista
        cenario_pessimista = cenarios.get('pessimista', {})
        if cenario_pessimista:
            acoes.extend([
                "Manter reserva de caixa equivalente a 6 meses de custos",
                "Diversificar canais de venda",
                "Implementar controle rigoroso de custos",
                "Estabelecer contratos de fornecimento a longo prazo"
            ])
        
        # Ações baseadas em volatilidade
        for nome, cenario in cenarios.items():
            metricas = cenario.get('metricas', {})
            if metricas.get('volatilidade_lucro', 0) > 25:
                acoes.append(f"Implementar hedge de preços para {nome}")
        
        return list(set(acoes))  # Remove duplicatas
    
    def _definir_acoes_corretivas(self, cenarios):
        """Define ações corretivas para situações de crise"""
        acoes = []
        
        cenario_pessimista = cenarios.get('pessimista', {})
        if cenario_pessimista:
            metricas = cenario_pessimista.get('metricas', {})
            
            if metricas.get('margem_lucro_media', 0) < 0:
                acoes.extend([
                    "Vender animais de menor valor",
                    "Suspender investimentos não essenciais",
                    "Renegociar contratos de fornecimento",
                    "Buscar financiamento de emergência"
                ])
            
            if metricas.get('valor_em_risco', 0) < -50000:
                acoes.extend([
                    "Reduzir drasticamente custos operacionais",
                    "Vender parte significativa do rebanho",
                    "Considerar parcerias estratégicas",
                    "Avaliar venda da propriedade"
                ])
        
        return acoes
    
    def _definir_indicadores_monitoramento(self):
        """Define indicadores para monitoramento de risco"""
        return [
            {
                'indicador': 'Margem de Lucro Mensal',
                'meta': '> 15%',
                'critico': '< 5%',
                'frequencia': 'Mensal'
            },
            {
                'indicador': 'Crescimento do Rebanho',
                'meta': '> 10% ao ano',
                'critico': '< 0%',
                'frequencia': 'Trimestral'
            },
            {
                'indicador': 'Custo por Cabeça',
                'meta': 'Estável ou decrescente',
                'critico': '> 20% de aumento',
                'frequencia': 'Mensal'
            },
            {
                'indicador': 'Preço de Venda',
                'meta': 'Acima da média regional',
                'critico': '< 80% da média',
                'frequencia': 'Semanal'
            },
            {
                'indicador': 'Taxa de Mortalidade',
                'meta': '< 5%',
                'critico': '> 10%',
                'frequencia': 'Mensal'
            }
        ]
    
    def _definir_niveis_alerta(self):
        """Define níveis de alerta e ações correspondentes"""
        return {
            'VERDE': {
                'condicao': 'Todos os indicadores dentro da meta',
                'acao': 'Manter operação normal',
                'cor': '#28a745'
            },
            'AMARELO': {
                'condicao': '1-2 indicadores fora da meta',
                'acao': 'Aumentar monitoramento',
                'cor': '#ffc107'
            },
            'LARANJA': {
                'condicao': '3-4 indicadores fora da meta',
                'acao': 'Implementar ações preventivas',
                'cor': '#fd7e14'
            },
            'VERMELHO': {
                'condicao': '5+ indicadores críticos',
                'acao': 'Implementar ações corretivas imediatas',
                'cor': '#dc3545'
            }
        }
    
    def calcular_risco_portfolio(self, cenarios):
        """Calcula risco do portfólio considerando todos os cenários"""
        if not cenarios:
            return {}
        
        # Calcular métricas ponderadas por probabilidade
        receita_esperada = 0
        lucro_esperado = 0
        var_esperado = 0
        
        for nome, cenario in cenarios.items():
            probabilidade = cenario.get('probabilidade', 0) / 100
            metricas = cenario.get('metricas', {})
            
            receita_esperada += metricas.get('receita_media_anual', 0) * probabilidade
            lucro_esperado += metricas.get('lucro_medio_anual', 0) * probabilidade
            var_esperado += metricas.get('valor_em_risco', 0) * probabilidade
        
        # Calcular Sharpe Ratio simplificado
        volatilidade_media = sum(
            cenario.get('metricas', {}).get('volatilidade_lucro', 0) * 
            cenario.get('probabilidade', 0) / 100
            for cenario in cenarios.values()
        )
        
        sharpe_ratio = (lucro_esperado / volatilidade_media) if volatilidade_media > 0 else 0
        
        return {
            'receita_esperada': receita_esperada,
            'lucro_esperado': lucro_esperado,
            'var_esperado': var_esperado,
            'volatilidade_media': volatilidade_media,
            'sharpe_ratio': sharpe_ratio,
            'classificacao_risco': self._classificar_risco_portfolio(sharpe_ratio, var_esperado)
        }
    
    def _classificar_risco_portfolio(self, sharpe_ratio, var_esperado):
        """Classifica o risco do portfólio"""
        if sharpe_ratio > 2 and var_esperado > -10000:
            return 'BAIXO'
        elif sharpe_ratio > 1 and var_esperado > -50000:
            return 'MEDIO'
        elif sharpe_ratio > 0:
            return 'ALTO'
        else:
            return 'MUITO_ALTO'



