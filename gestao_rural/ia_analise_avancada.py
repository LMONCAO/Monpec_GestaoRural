"""
Sistema de análise inteligente avançada para pecuária
Combina dados reais, sazonalidade, clima e benchmarks da indústria
"""

from decimal import Decimal
from datetime import datetime, timedelta
from .ia_pecuaria_data import (
    obter_dados_regiao, calcular_preco_sazonal, 
    obter_benchmark_industria, obter_cenario_risco
)

class IAAnalisePecuaria:
    """Classe principal para análise inteligente de pecuária"""
    
    def __init__(self, propriedade, inventario_atual):
        self.propriedade = propriedade
        self.inventario = inventario_atual
        self.dados_regiao = obter_dados_regiao(propriedade.estado)
        self.mes_atual = datetime.now().strftime('%B').lower()
        
    def analisar_perfil_propriedade(self, respostas_questionario):
        """Análise completa do perfil da propriedade"""
        perfil = {
            'tipo_propriedade': self._detectar_tipo_propriedade(),
            'nivel_tecnico': self._avaliar_nivel_tecnico(),
            'potencial_crescimento': self._calcular_potencial_crescimento(),
            'viabilidade_economica': self._avaliar_viabilidade_economica(),
            'riscos_identificados': self._identificar_riscos(),
            'oportunidades': self._identificar_oportunidades(),
            'score_geral': 0
        }
        
        # Calcular score geral (0-100)
        perfil['score_geral'] = self._calcular_score_geral(perfil, respostas_questionario)
        
        return perfil
    
    def _detectar_tipo_propriedade(self):
        """Detecta o tipo de propriedade baseado no inventário"""
        total_animais = sum(item['quantidade'] for item in self.inventario.values())
        proporcao_vacas = self._calcular_proporcao_vacas()
        
        if total_animais < 50:
            return 'FAMILIAR'
        elif total_animais < 200:
            return 'COMERCIAL_PEQUENO'
        elif total_animais < 500:
            return 'COMERCIAL_MEDIO'
        elif total_animais < 1000:
            return 'COMERCIAL_GRANDE'
        else:
            return 'INDUSTRIAL'
    
    def _avaliar_nivel_tecnico(self):
        """Avalia o nível técnico da propriedade"""
        score = 0
        
        # Análise da estrutura do rebanho
        proporcao_vacas = self._calcular_proporcao_vacas()
        if proporcao_vacas > 0.6:
            score += 30  # Boa proporção de fêmeas
        elif proporcao_vacas > 0.4:
            score += 20
        else:
            score += 10
        
        # Análise da diversidade de categorias
        categorias = len(self.inventario)
        if categorias >= 8:
            score += 25  # Boa diversificação
        elif categorias >= 5:
            score += 15
        else:
            score += 5
        
        # Análise do valor por cabeça
        valor_medio = self._calcular_valor_medio_cabeca()
        if valor_medio > 2000:
            score += 25  # Alto valor
        elif valor_medio > 1500:
            score += 15
        else:
            score += 5
        
        # Análise da produtividade
        produtividade = self._calcular_produtividade()
        if produtividade > 2.0:
            score += 20  # Alta produtividade
        elif produtividade > 1.5:
            score += 10
        else:
            score += 5
        
        if score >= 80:
            return 'ALTO'
        elif score >= 60:
            return 'MEDIO'
        else:
            return 'BAIXO'
    
    def _calcular_potencial_crescimento(self):
        """Calcula o potencial de crescimento do rebanho"""
        dados = self.dados_regiao['caracteristicas']
        
        # Fatores que influenciam o crescimento
        fator_natalidade = dados['natalidade_media'] / 100
        fator_mortalidade = 1 - (dados['mortalidade_bezerros_media'] / 100)
        fator_descarte = 1 - (dados['descarte_vacas_vazias'] / 100)
        
        # Potencial teórico de crescimento
        crescimento_teorico = (fator_natalidade * fator_mortalidade * fator_descarte - 1) * 100
        
        # Ajustar baseado no nível técnico atual
        nivel_tecnico = self._avaliar_nivel_tecnico()
        if nivel_tecnico == 'ALTO':
            fator_ajuste = 1.2
        elif nivel_tecnico == 'MEDIO':
            fator_ajuste = 1.0
        else:
            fator_ajuste = 0.8
        
        crescimento_real = crescimento_teorico * fator_ajuste
        
        return {
            'crescimento_anual': max(0, crescimento_real),
            'crescimento_5_anos': max(0, crescimento_real * 5),
            'categoria': self._classificar_crescimento(crescimento_real)
        }
    
    def _avaliar_viabilidade_economica(self):
        """Avalia a viabilidade econômica da propriedade"""
        receita_projetada = self._calcular_receita_projetada()
        custos_projetados = self._calcular_custos_projetados()
        
        lucro_projetado = receita_projetada - custos_projetados
        margem_lucro = (lucro_projetado / receita_projetada * 100) if receita_projetada > 0 else 0
        
        # Comparar com benchmarks da indústria
        benchmark_bom = obter_benchmark_industria('margem_lucro_boa')
        benchmark_medio = obter_benchmark_industria('margem_lucro_media')
        
        if margem_lucro >= benchmark_bom:
            categoria = 'EXCELENTE'
        elif margem_lucro >= benchmark_medio:
            categoria = 'BOA'
        elif margem_lucro > 0:
            categoria = 'REGULAR'
        else:
            categoria = 'RUIM'
        
        return {
            'receita_anual': receita_projetada,
            'custos_anuais': custos_projetados,
            'lucro_anual': lucro_projetado,
            'margem_lucro': margem_lucro,
            'categoria': categoria,
            'roi_anual': (lucro_projetado / custos_projetados * 100) if custos_projetados > 0 else 0
        }
    
    def _identificar_riscos(self):
        """Identifica riscos específicos da propriedade"""
        riscos = []
        
        # Risco climático
        if self.dados_regiao['clima']['tipo'] in ['Semiárido', 'Equatorial']:
            riscos.append({
                'tipo': 'CLIMATICO',
                'severidade': 'ALTA',
                'descricao': f"Região {self.dados_regiao['clima']['tipo']} com alta variabilidade climática"
            })
        
        # Risco de mercado
        proporcao_vacas = self._calcular_proporcao_vacas()
        if proporcao_vacas < 0.4:
            riscos.append({
                'tipo': 'REPRODUTIVO',
                'severidade': 'MEDIA',
                'descricao': 'Baixa proporção de fêmeas pode limitar crescimento'
            })
        
        # Risco econômico
        viabilidade = self._avaliar_viabilidade_economica()
        if viabilidade['categoria'] == 'RUIM':
            riscos.append({
                'tipo': 'ECONOMICO',
                'severidade': 'ALTA',
                'descricao': 'Margem de lucro insuficiente para sustentabilidade'
            })
        
        return riscos
    
    def _identificar_oportunidades(self):
        """Identifica oportunidades de melhoria"""
        oportunidades = []
        
        # Oportunidade de crescimento
        potencial = self._calcular_potencial_crescimento()
        if potencial['crescimento_anual'] > 15:
            oportunidades.append({
                'tipo': 'CRESCIMENTO',
                'impacto': 'ALTO',
                'descricao': f"Potencial de crescimento de {potencial['crescimento_anual']:.1f}% ao ano"
            })
        
        # Oportunidade de melhoria técnica
        nivel_tecnico = self._avaliar_nivel_tecnico()
        if nivel_tecnico in ['BAIXO', 'MEDIO']:
            oportunidades.append({
                'tipo': 'TECNICO',
                'impacto': 'MEDIO',
                'descricao': 'Melhoria no manejo pode aumentar produtividade'
            })
        
        # Oportunidade de mercado
        preco_atual = self._calcular_preco_medio_atual()
        preco_sazonal = calcular_preco_sazonal(preco_atual, self.mes_atual)
        if preco_sazonal > preco_atual * 1.05:
            oportunidades.append({
                'tipo': 'MERCADO',
                'impacto': 'ALTO',
                'descricao': f"Preços sazonais favoráveis (+{(preco_sazonal/preco_atual-1)*100:.1f}%)"
            })
        
        return oportunidades
    
    def gerar_estrategia_otimizada(self, perfil, respostas_questionario):
        """Gera estratégia otimizada baseada na análise"""
        estrategia = {
            'nome': self._gerar_nome_estrategia(perfil),
            'objetivos': self._definir_objetivos(perfil),
            'acoes_imediata': self._definir_acoes_imediata(perfil),
            'acoes_curto_prazo': self._definir_acoes_curto_prazo(perfil),
            'acoes_longo_prazo': self._definir_acoes_longo_prazo(perfil),
            'parametros_otimizados': self._calcular_parametros_otimizados(perfil),
            'projecao_5_anos': self._gerar_projecao_5_anos(perfil),
            'indicadores_monitoramento': self._definir_indicadores_monitoramento(perfil)
        }
        
        return estrategia
    
    def _calcular_proporcao_vacas(self):
        """Calcula a proporção de vacas no rebanho"""
        total_animais = sum(item['quantidade'] for item in self.inventario.values())
        if total_animais == 0:
            return 0
        
        vacas = sum(
            item['quantidade'] for categoria, item in self.inventario.items()
            if any(termo in categoria.lower() for termo in ['vaca', 'multipara', 'primipara'])
        )
        
        return vacas / total_animais
    
    def _calcular_valor_medio_cabeca(self):
        """Calcula o valor médio por cabeça"""
        total_animais = sum(item['quantidade'] for item in self.inventario.values())
        if total_animais == 0:
            return 0
        
        valor_total = sum(item['valor_total'] for item in self.inventario.values())
        return valor_total / total_animais
    
    def _calcular_produtividade(self):
        """Calcula a produtividade em UA/ha"""
        # Assumindo 1 hectare por 2 UA (Unidade Animal)
        total_animais = sum(item['quantidade'] for item in self.inventario.values())
        return total_animais / 2  # Simplificado para exemplo
    
    def _calcular_receita_projetada(self):
        """Calcula receita projetada anual"""
        receita = 0
        for categoria, item in self.inventario.items():
            quantidade = item['quantidade']
            valor_unitario = item['valor_por_cabeca']
            
            # Aplicar sazonalidade
            preco_sazonal = calcular_preco_sazonal(valor_unitario, self.mes_atual)
            
            # Calcular vendas baseadas na categoria
            if any(termo in categoria.lower() for termo in ['boi', 'macho']):
                percentual_venda = self.dados_regiao['caracteristicas']['percentual_venda_machos_anual'] / 100
            else:
                percentual_venda = self.dados_regiao['caracteristicas']['percentual_venda_femeas_anual'] / 100
            
            vendas_anuais = quantidade * percentual_venda
            receita += vendas_anuais * preco_sazonal
        
        return receita
    
    def _calcular_custos_projetados(self):
        """Calcula custos projetados anuais"""
        total_animais = sum(item['quantidade'] for item in self.inventario.values())
        custos = self.dados_regiao['custos_operacionais']
        
        custo_total = (
            total_animais * custos['custo_animal_ano'] +
            total_animais * custos['custo_sanitario_ano'] +
            total_animais * custos['custo_reproducao_ano']
        )
        
        return custo_total
    
    def _calcular_preco_medio_atual(self):
        """Calcula preço médio atual do rebanho"""
        total_valor = sum(item['valor_total'] for item in self.inventario.values())
        total_animais = sum(item['quantidade'] for item in self.inventario.values())
        
        if total_animais == 0:
            return 0
        
        return total_valor / total_animais
    
    def _classificar_crescimento(self, crescimento):
        """Classifica o potencial de crescimento"""
        if crescimento >= 20:
            return 'MUITO_ALTO'
        elif crescimento >= 15:
            return 'ALTO'
        elif crescimento >= 10:
            return 'MEDIO'
        elif crescimento >= 5:
            return 'BAIXO'
        else:
            return 'MUITO_BAIXO'
    
    def _calcular_score_geral(self, perfil, respostas):
        """Calcula score geral da propriedade (0-100)"""
        score = 0
        
        # Score baseado no nível técnico (40%)
        nivel_scores = {'ALTO': 40, 'MEDIO': 25, 'BAIXO': 10}
        score += nivel_scores.get(perfil['nivel_tecnico'], 0)
        
        # Score baseado no potencial de crescimento (30%)
        crescimento = perfil['potencial_crescimento']['crescimento_anual']
        if crescimento >= 20:
            score += 30
        elif crescimento >= 15:
            score += 25
        elif crescimento >= 10:
            score += 20
        elif crescimento >= 5:
            score += 15
        else:
            score += 10
        
        # Score baseado na viabilidade econômica (30%)
        viabilidade = perfil['viabilidade_economica']['categoria']
        viabilidade_scores = {'EXCELENTE': 30, 'BOA': 25, 'REGULAR': 15, 'RUIM': 5}
        score += viabilidade_scores.get(viabilidade, 0)
        
        return min(100, max(0, score))
    
    def _gerar_nome_estrategia(self, perfil):
        """Gera nome da estratégia baseado no perfil"""
        tipo = perfil['tipo_propriedade']
        nivel = perfil['nivel_tecnico']
        crescimento = perfil['potencial_crescimento']['categoria']
        
        if tipo == 'INDUSTRIAL' and nivel == 'ALTO':
            return 'Estratégia Industrial Avançada'
        elif crescimento == 'MUITO_ALTO':
            return 'Estratégia de Crescimento Agressivo'
        elif perfil['viabilidade_economica']['categoria'] == 'EXCELENTE':
            return 'Estratégia de Alta Rentabilidade'
        else:
            return 'Estratégia de Consolidação'
    
    def _definir_objetivos(self, perfil):
        """Define objetivos baseados no perfil"""
        objetivos = []
        
        crescimento = perfil['potencial_crescimento']['crescimento_anual']
        if crescimento > 15:
            objetivos.append(f"Aumentar rebanho em {crescimento:.1f}% ao ano")
        
        viabilidade = perfil['viabilidade_economica']
        if viabilidade['categoria'] in ['REGULAR', 'RUIM']:
            objetivos.append(f"Melhorar margem de lucro para {obter_benchmark_industria('margem_lucro_media')}%")
        
        nivel = perfil['nivel_tecnico']
        if nivel == 'BAIXO':
            objetivos.append("Implementar melhorias técnicas no manejo")
        
        return objetivos
    
    def _definir_acoes_imediata(self, perfil):
        """Define ações imediatas (0-3 meses)"""
        acoes = []
        
        # Ações baseadas em riscos identificados
        for risco in perfil['riscos_identificados']:
            if risco['tipo'] == 'CLIMATICO':
                acoes.append("Implementar sistema de reserva de água e pasto")
            elif risco['tipo'] == 'REPRODUTIVO':
                acoes.append("Aumentar proporção de fêmeas no rebanho")
            elif risco['tipo'] == 'ECONOMICO':
                acoes.append("Revisar custos operacionais e otimizar despesas")
        
        # Ações baseadas em oportunidades
        for oportunidade in perfil['oportunidades']:
            if oportunidade['tipo'] == 'MERCADO':
                acoes.append("Aproveitar preços sazonais favoráveis para vendas")
        
        return acoes
    
    def _definir_acoes_curto_prazo(self, perfil):
        """Define ações de curto prazo (3-12 meses)"""
        acoes = []
        
        nivel = perfil['nivel_tecnico']
        if nivel == 'BAIXO':
            acoes.append("Capacitar equipe em técnicas de manejo")
            acoes.append("Implementar controle sanitário preventivo")
        
        crescimento = perfil['potencial_crescimento']
        if crescimento['categoria'] in ['ALTO', 'MUITO_ALTO']:
            acoes.append("Expandir infraestrutura para suportar crescimento")
            acoes.append("Aumentar capacidade de pasto e água")
        
        return acoes
    
    def _definir_acoes_longo_prazo(self, perfil):
        """Define ações de longo prazo (1-5 anos)"""
        acoes = []
        
        tipo = perfil['tipo_propriedade']
        if tipo in ['FAMILIAR', 'COMERCIAL_PEQUENO']:
            acoes.append("Planejar expansão para escala comercial")
        elif tipo == 'INDUSTRIAL':
            acoes.append("Implementar tecnologias de precisão")
        
        viabilidade = perfil['viabilidade_economica']
        if viabilidade['categoria'] == 'EXCELENTE':
            acoes.append("Considerar diversificação de atividades")
        
        return acoes
    
    def _calcular_parametros_otimizados(self, perfil):
        """Calcula parâmetros otimizados para a projeção"""
        dados = self.dados_regiao['caracteristicas']
        
        # Ajustar parâmetros baseado no perfil
        fator_ajuste = 1.0
        if perfil['nivel_tecnico'] == 'ALTO':
            fator_ajuste = 1.1
        elif perfil['nivel_tecnico'] == 'BAIXO':
            fator_ajuste = 0.9
        
        return {
            'taxa_natalidade': min(100, dados['natalidade_media'] * fator_ajuste),
            'taxa_mortalidade_bezerros': max(0, dados['mortalidade_bezerros_media'] / fator_ajuste),
            'taxa_mortalidade_adultos': max(0, dados['mortalidade_adultos_media'] / fator_ajuste),
            'percentual_venda_machos': dados['percentual_venda_machos_anual'],
            'percentual_venda_femeas': dados['percentual_venda_femeas_anual'],
            'periodicidade': 'MENSAL'
        }
    
    def _gerar_projecao_5_anos(self, perfil):
        """Gera projeção para 5 anos"""
        crescimento_anual = perfil['potencial_crescimento']['crescimento_anual']
        receita_atual = perfil['viabilidade_economica']['receita_anual']
        custos_atual = perfil['viabilidade_economica']['custos_anuais']
        
        projecao = []
        for ano in range(1, 6):
            fator_crescimento = (1 + crescimento_anual/100) ** ano
            fator_inflacao = 1.05 ** ano  # 5% de inflação ao ano
            
            receita_projetada = receita_atual * fator_crescimento * fator_inflacao
            custos_projetados = custos_atual * fator_inflacao
            lucro_projetado = receita_projetada - custos_projetados
            
            projecao.append({
                'ano': datetime.now().year + ano,
                'receita': receita_projetada,
                'custos': custos_projetados,
                'lucro': lucro_projetado,
                'margem_lucro': (lucro_projetado / receita_projetada * 100) if receita_projetada > 0 else 0,
                'crescimento_rebanho': (fator_crescimento - 1) * 100
            })
        
        return projecao
    
    def _definir_indicadores_monitoramento(self, perfil):
        """Define indicadores para monitoramento"""
        return [
            'Taxa de natalidade mensal',
            'Taxa de mortalidade por categoria',
            'Peso médio de abate',
            'Preço médio de venda',
            'Custo por cabeça',
            'Margem de lucro',
            'Produtividade por hectare',
            'Taxa de ocupação do pasto'
        ]



