# -*- coding: utf-8 -*-
"""
IA para Evolução e Projeções de Rebanho
Machine Learning para prever crescimento, produção e benchmarking
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Tuple
import statistics


class IAEvolucaoProjecoes:
    """
    IA que prevê evolução do rebanho usando:
    - Modelos de crescimento
    - Análise histórica
    - Benchmarking com mercado
    - Projeções de produção
    - Metas inteligentes
    """
    
    def __init__(self):
        # Benchmarks de mercado por região
        self.benchmarks_mercado = {
            'CENTRO_OESTE': {
                'taxa_desfrute': 0.22,  # 22%
                'taxa_natalidade': 0.80,  # 80%
                'taxa_mortalidade': 0.03,  # 3%
                'gmd_bezerros': 0.650,  # kg/dia
                'gmd_recria': 0.550,    # kg/dia
                'gmd_engorda': 1.200,   # kg/dia
                'peso_abate_medio': 540,  # kg
                'idade_abate_media': 30,  # meses
                'receita_por_ua_ano': 3500.00,
                'custo_por_ua_ano': 2800.00
            },
            'SUL': {
                'taxa_desfrute': 0.24,
                'taxa_natalidade': 0.82,
                'taxa_mortalidade': 0.025,
                'gmd_bezerros': 0.700,
                'gmd_recria': 0.600,
                'gmd_engorda': 1.300,
                'peso_abate_medio': 550,
                'idade_abate_media': 28,
                'receita_por_ua_ano': 3800.00,
                'custo_por_ua_ano': 3000.00
            },
            'SUDESTE': {
                'taxa_desfrute': 0.23,
                'taxa_natalidade': 0.78,
                'taxa_mortalidade': 0.028,
                'gmd_bezerros': 0.680,
                'gmd_recria': 0.580,
                'gmd_engorda': 1.250,
                'peso_abate_medio': 545,
                'idade_abate_media': 29,
                'receita_por_ua_ano': 3650.00,
                'custo_por_ua_ano': 2900.00
            }
        }
    
    def projetar_evolucao_completa(
        self,
        inventario_atual: Dict[str, int],
        parametros_atuais: Dict[str, Any],
        anos_projecao: int = 5,
        regiao: str = 'CENTRO_OESTE',
        considerar_melhorias: bool = True
    ) -> Dict[str, Any]:
        """
        Projeta evolução completa do rebanho para N anos
        Considera melhorias graduais de performance
        """
        benchmark = self.benchmarks_mercado.get(regiao, self.benchmarks_mercado['CENTRO_OESTE'])
        
        # Análise inicial
        analise_inicial = self._analisar_situacao_atual(
            inventario_atual,
            parametros_atuais,
            benchmark
        )
        
        # Projetar ano a ano
        projecoes_anuais = []
        inventario_projetado = inventario_atual.copy()
        parametros_projetados = parametros_atuais.copy()
        
        for ano in range(1, anos_projecao + 1):
            # Aplicar melhorias graduais (se habilitado)
            if considerar_melhorias:
                parametros_projetados = self._aplicar_melhorias_graduais(
                    parametros_projetados,
                    benchmark,
                    ano
                )
            
            # Projetar o ano
            projecao_ano = self._projetar_ano(
                inventario_projetado,
                parametros_projetados,
                benchmark,
                ano
            )
            
            projecoes_anuais.append(projecao_ano)
            
            # Atualizar inventário para próximo ano
            inventario_projetado = projecao_ano['inventario_final']
        
        # Análise consolidada
        analise_consolidada = self._consolidar_projecoes(
            analise_inicial,
            projecoes_anuais,
            benchmark
        )
        
        return {
            'analise_inicial': analise_inicial,
            'projecoes_anuais': projecoes_anuais,
            'analise_consolidada': analise_consolidada,
            'benchmark_regiao': regiao,
            'recomendacoes_estrategicas': self._gerar_recomendacoes_estrategicas(
                analise_inicial,
                projecoes_anuais,
                benchmark
            )
        }
    
    def calcular_producao_estimada(
        self,
        inventario: Dict[str, int],
        parametros: Dict[str, Any],
        tipo_producao: str = 'CARNE'  # ou 'LEITE'
    ) -> Dict[str, Any]:
        """
        Calcula produção estimada (carne ou leite) baseada no rebanho
        """
        if tipo_producao == 'CARNE':
            return self._calcular_producao_carne(inventario, parametros)
        elif tipo_producao == 'LEITE':
            return self._calcular_producao_leite(inventario, parametros)
        else:
            return {}
    
    def comparar_com_benchmark(
        self,
        metricas_propriedade: Dict[str, float],
        regiao: str = 'CENTRO_OESTE'
    ) -> Dict[str, Any]:
        """
        Compara métricas da propriedade com benchmarks de mercado
        """
        benchmark = self.benchmarks_mercado.get(regiao, self.benchmarks_mercado['CENTRO_OESTE'])
        
        comparacoes = {}
        
        for metrica, valor_prop in metricas_propriedade.items():
            if metrica in benchmark:
                valor_bench = benchmark[metrica]
                diferenca = valor_prop - valor_bench
                diferenca_percentual = (diferenca / valor_bench * 100) if valor_bench != 0 else 0
                
                # Classificar desempenho
                if diferenca_percentual >= 10:
                    classificacao = 'ACIMA DO MERCADO'
                    emoji = '🔥'
                elif diferenca_percentual >= 0:
                    classificacao = 'NA MÉDIA'
                    emoji = '✅'
                elif diferenca_percentual >= -10:
                    classificacao = 'ABAIXO DA MÉDIA'
                    emoji = '⚠️'
                else:
                    classificacao = 'MUITO ABAIXO'
                    emoji = '🚨'
                
                comparacoes[metrica] = {
                    'valor_propriedade': valor_prop,
                    'valor_benchmark': valor_bench,
                    'diferenca': diferenca,
                    'diferenca_percentual': diferenca_percentual,
                    'classificacao': classificacao,
                    'emoji': emoji
                }
        
        return {
            'regiao': regiao,
            'comparacoes': comparacoes,
            'score_geral': self._calcular_score_geral(comparacoes),
            'pontos_melhoria': self._identificar_pontos_melhoria(comparacoes)
        }
    
    def _analisar_situacao_atual(
        self,
        inventario: Dict[str, int],
        parametros: Dict[str, Any],
        benchmark: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analisa situação atual do rebanho"""
        total_animais = sum(inventario.values())
        
        # Converter para UA
        from .ia_transferencias_inteligentes import ia_transferencias_inteligentes
        ua_total = 0
        for categoria, quantidade in inventario.items():
            fator = ia_transferencias_inteligentes.fator_ua.get(categoria, 0.75)
            ua_total += quantidade * fator
        
        # Calcular métricas atuais
        taxa_natalidade_atual = parametros.get('taxa_natalidade_anual', 75) / 100
        taxa_mortalidade_atual = parametros.get('taxa_mortalidade_adultos_anual', 3) / 100
        
        # Comparar com benchmark
        gap_natalidade = taxa_natalidade_atual - benchmark['taxa_natalidade']
        gap_mortalidade = taxa_mortalidade_atual - benchmark['taxa_mortalidade']
        
        return {
            'total_animais': total_animais,
            'total_ua': ua_total,
            'taxa_natalidade': taxa_natalidade_atual,
            'taxa_mortalidade': taxa_mortalidade_atual,
            'gap_natalidade': gap_natalidade,
            'gap_mortalidade': gap_mortalidade,
            'inventario_categorizado': inventario,
            'potencial_melhoria': self._calcular_potencial_melhoria(
                gap_natalidade,
                gap_mortalidade,
                total_animais
            )
        }
    
    def _projetar_ano(
        self,
        inventario_inicial: Dict[str, int],
        parametros: Dict[str, Any],
        benchmark: Dict[str, Any],
        ano: int
    ) -> Dict[str, Any]:
        """Projeta um ano completo"""
        total_inicial = sum(inventario_inicial.values())
        
        # Calcular movimentações do ano
        nascimentos_ano = int(total_inicial * parametros.get('taxa_natalidade', 0.75))
        mortes_ano = int(total_inicial * parametros.get('taxa_mortalidade', 0.03))
        vendas_ano = int(total_inicial * parametros.get('taxa_desfrute', 0.20))
        compras_ano = int(total_inicial * parametros.get('taxa_compra', 0.10))
        
        # Inventário final
        total_final = total_inicial + nascimentos_ano - mortes_ano - vendas_ano + compras_ano
        
        # Calcular financeiro
        receita_ano = vendas_ano * Decimal('4500.00')  # Preço médio
        custo_ano = total_inicial * Decimal('2800.00')  # Custo por UA/ano
        lucro_ano = receita_ano - custo_ano
        margem = (lucro_ano / receita_ano * 100) if receita_ano > 0 else 0
        
        # Comparar com benchmark
        desempenho = self._avaliar_desempenho_ano(parametros, benchmark)
        
        return {
            'ano': ano,
            'ano_calendario': datetime.now().year + ano,
            'inventario_inicial_total': total_inicial,
            'inventario_final_total': total_final,
            'inventario_final': self._projetar_inventario_detalhado(inventario_inicial, parametros),
            'movimentacoes': {
                'nascimentos': nascimentos_ano,
                'mortes': mortes_ano,
                'vendas': vendas_ano,
                'compras': compras_ano,
                'crescimento_liquido': total_final - total_inicial
            },
            'financeiro': {
                'receita': float(receita_ano),
                'custo': float(custo_ano),
                'lucro': float(lucro_ano),
                'margem_percentual': float(margem)
            },
            'desempenho_vs_benchmark': desempenho,
            'crescimento_percentual': ((total_final - total_inicial) / total_inicial * 100) if total_inicial > 0 else 0
        }
    
    def _aplicar_melhorias_graduais(
        self,
        parametros: Dict[str, Any],
        benchmark: Dict[str, Any],
        ano: int
    ) -> Dict[str, Any]:
        """
        Aplica melhorias graduais aos parâmetros ao longo dos anos
        Simula adoção de melhores práticas
        """
        parametros_melhorados = parametros.copy()
        
        # Fator de melhoria (5% ao ano, máximo 25% em 5 anos)
        fator_melhoria = min(0.05 * ano, 0.25)
        
        # Melhorar natalidade (tendendo ao benchmark)
        taxa_natal_atual = parametros.get('taxa_natalidade', 0.75)
        gap_natal = benchmark['taxa_natalidade'] - taxa_natal_atual
        if gap_natal > 0:
            parametros_melhorados['taxa_natalidade'] = taxa_natal_atual + (gap_natal * fator_melhoria)
        
        # Reduzir mortalidade (tendendo ao benchmark)
        taxa_mort_atual = parametros.get('taxa_mortalidade', 0.03)
        gap_mort = taxa_mort_atual - benchmark['taxa_mortalidade']
        if gap_mort > 0:
            parametros_melhorados['taxa_mortalidade'] = taxa_mort_atual - (gap_mort * fator_melhoria)
        
        # Aumentar desfrute (tendendo ao benchmark)
        taxa_desfrute_atual = parametros.get('taxa_desfrute', 0.18)
        gap_desfrute = benchmark['taxa_desfrute'] - taxa_desfrute_atual
        if gap_desfrute > 0:
            parametros_melhorados['taxa_desfrute'] = taxa_desfrute_atual + (gap_desfrute * fator_melhoria)
        
        return parametros_melhorados
    
    def _projetar_inventario_detalhado(
        self,
        inventario_inicial: Dict[str, int],
        parametros: Dict[str, Any]
    ) -> Dict[str, int]:
        """Projeta inventário detalhado por categoria após 1 ano"""
        inventario_projetado = {}
        
        # Lógica simplificada - pode ser expandida
        for categoria, quantidade in inventario_inicial.items():
            # Aplicar crescimento/redução baseado em movimentações típicas
            if 'Bezerro' in categoria or 'Bezerra' in categoria:
                # Bezerros: nascimentos menos evolução para garrote/novilha
                crescimento = parametros.get('taxa_natalidade', 0.75) - 0.83  # 83% evoluem
                quantidade_projetada = int(quantidade * (1 + crescimento))
            elif 'Garrote' in categoria or 'Novilha' in categoria:
                # Garrotes/Novilhas: recebem de bezerros, perdem para categorias superiores
                quantidade_projetada = int(quantidade * 1.05)  # Leve crescimento
            elif 'Multíparas' in categoria or 'Primíparas' in categoria:
                # Matrizes: reposição - descarte
                quantidade_projetada = int(quantidade * 1.02)  # Crescimento gradual
            else:
                # Outras categorias: manter relativamente estável
                quantidade_projetada = quantidade
            
            inventario_projetado[categoria] = max(0, quantidade_projetada)
        
        return inventario_projetado
    
    def _calcular_producao_carne(
        self,
        inventario: Dict[str, int],
        parametros: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula produção estimada de carne (kg e @)
        """
        # Taxa de desfrute (% do rebanho vendido/ano)
        taxa_desfrute = parametros.get('taxa_desfrute', 0.20)
        
        total_animais = sum(inventario.values())
        animais_abatidos = int(total_animais * taxa_desfrute)
        
        # Peso médio de abate por categoria
        peso_medio_abate = {
            'Garrotes (12-24m)': 420,
            'Bois Magros (24-36m)': 520,
            'Bois (24-36m)': 540,
            'Vacas de Descarte': 450,
            'Novilhas (12-24m)': 380
        }
        
        # Rendimento de carcaça (%)
        rendimento_carcaca = 0.52  # 52%
        
        # Calcular produção total
        producao_peso_vivo = 0
        producao_carcaca = 0
        producao_arrobas = 0
        
        for categoria, quantidade in inventario.items():
            if categoria in peso_medio_abate:
                peso_medio = peso_medio_abate[categoria]
                animais_categoria = int(quantidade * taxa_desfrute)
                
                peso_vivo_categoria = animais_categoria * peso_medio
                peso_carcaca_categoria = peso_vivo_categoria * rendimento_carcaca
                arrobas_categoria = peso_carcaca_categoria / 15  # 1 @ = 15kg
                
                producao_peso_vivo += peso_vivo_categoria
                producao_carcaca += peso_carcaca_categoria
                producao_arrobas += arrobas_categoria
        
        # Valor estimado da produção
        preco_arroba = Decimal('280.00')  # R$/arroba
        valor_total_producao = Decimal(str(producao_arrobas)) * preco_arroba
        
        return {
            'animais_abatidos': animais_abatidos,
            'taxa_desfrute': taxa_desfrute * 100,
            'producao_peso_vivo_kg': producao_peso_vivo,
            'producao_carcaca_kg': producao_carcaca,
            'producao_arrobas': producao_arrobas,
            'rendimento_carcaca_percentual': rendimento_carcaca * 100,
            'preco_arroba': float(preco_arroba),
            'valor_total_producao': float(valor_total_producao),
            'producao_por_animal_abatido': producao_carcaca / animais_abatidos if animais_abatidos > 0 else 0
        }
    
    def _calcular_producao_leite(
        self,
        inventario: Dict[str, int],
        parametros: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcula produção estimada de leite"""
        # Vacas em lactação
        multiparas = inventario.get('Multíparas (>36m)', 0)
        primiparas = inventario.get('Primíparas (24-36m)', 0)
        
        # Assumir 80% em lactação
        vacas_lactacao = int((multiparas + primiparas) * 0.80)
        
        # Produção média por vaca (litros/dia)
        producao_multiparas = 12.0  # litros/dia
        producao_primiparas = 10.0  # litros/dia
        
        # Produção anual
        dias_lactacao = 305  # dias/ano
        producao_anual_litros = (
            (multiparas * 0.80 * producao_multiparas * dias_lactacao) +
            (primiparas * 0.80 * producao_primiparas * dias_lactacao)
        )
        
        # Valor da produção
        preco_litro = Decimal('2.50')
        valor_total_producao = Decimal(str(producao_anual_litros)) * preco_litro
        
        return {
            'vacas_lactacao': vacas_lactacao,
            'producao_media_vaca_dia': (producao_anual_litros / vacas_lactacao / dias_lactacao) if vacas_lactacao > 0 else 0,
            'producao_anual_litros': producao_anual_litros,
            'preco_litro': float(preco_litro),
            'valor_total_producao': float(valor_total_producao),
            'dias_lactacao': dias_lactacao
        }
    
    def _consolidar_projecoes(
        self,
        analise_inicial: Dict[str, Any],
        projecoes_anuais: List[Dict[str, Any]],
        benchmark: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Consolida projeções de todos os anos"""
        # Totais acumulados
        receita_total = sum(proj['financeiro']['receita'] for proj in projecoes_anuais)
        custo_total = sum(proj['financeiro']['custo'] for proj in projecoes_anuais)
        lucro_total = receita_total - custo_total
        
        # Crescimento do rebanho
        rebanho_inicial = analise_inicial['total_animais']
        rebanho_final = projecoes_anuais[-1]['inventario_final_total']
        crescimento_total = ((rebanho_final - rebanho_inicial) / rebanho_inicial * 100) if rebanho_inicial > 0 else 0
        
        # Taxa de crescimento anual composta (CAGR)
        anos = len(projecoes_anuais)
        cagr = (((rebanho_final / rebanho_inicial) ** (1 / anos)) - 1) * 100 if rebanho_inicial > 0 else 0
        
        # Média de margem
        margem_media = statistics.mean([proj['financeiro']['margem_percentual'] for proj in projecoes_anuais])
        
        return {
            'periodo_anos': anos,
            'rebanho_inicial': rebanho_inicial,
            'rebanho_final': rebanho_final,
            'crescimento_total_percentual': crescimento_total,
            'cagr_percentual': cagr,
            'receita_total_acumulada': receita_total,
            'custo_total_acumulado': custo_total,
            'lucro_total_acumulado': lucro_total,
            'margem_media_percentual': margem_media,
            'roi_total_percentual': (lucro_total / custo_total * 100) if custo_total > 0 else 0
        }
    
    def _gerar_recomendacoes_estrategicas(
        self,
        analise_inicial: Dict[str, Any],
        projecoes: List[Dict[str, Any]],
        benchmark: Dict[str, Any]
    ) -> List[str]:
        """Gera recomendações estratégicas baseadas nas projeções"""
        recomendacoes = []
        
        # Análise de natalidade
        if analise_inicial['gap_natalidade'] < -0.05:  # 5% abaixo do benchmark
            recomendacoes.append("🐮 Melhorar taxa de natalidade: considere IATF, melhor nutrição das matrizes e touro de qualidade.")
        
        # Análise de mortalidade
        if analise_inicial['gap_mortalidade'] > 0.01:  # 1% acima do benchmark
            recomendacoes.append("⚕️ Reduzir mortalidade: implementar programa sanitário rigoroso e melhorar manejo.")
        
        # Análise de crescimento
        crescimento_projetado = projecoes[-1]['crescimento_percentual']
        if crescimento_projetado < 5:
            recomendacoes.append("📈 Crescimento baixo: avaliar compra de animais ou melhorar retenção de fêmeas.")
        
        # Análise financeira
        margem_media = statistics.mean([p['financeiro']['margem_percentual'] for p in projecoes])
        if margem_media < 15:
            recomendacoes.append("💰 Margem baixa: otimizar custos ou buscar melhores preços de venda.")
        
        # Oportunidades de melhoria
        if analise_inicial['potencial_melhoria']['receita_adicional'] > 100000:
            recomendacoes.append(f"🚀 Alto potencial: atingindo benchmarks, pode gerar +R$ {analise_inicial['potencial_melhoria']['receita_adicional']:,.0f}/ano!")
        
        return recomendacoes
    
    def _calcular_potencial_melhoria(
        self,
        gap_natalidade: float,
        gap_mortalidade: float,
        total_animais: int
    ) -> Dict[str, Any]:
        """Calcula potencial de melhoria atingindo benchmarks"""
        # Receita adicional por melhorar natalidade
        if gap_natalidade < 0:
            nascimentos_adicionais = int(abs(gap_natalidade) * total_animais)
            receita_adicional_natalidade = nascimentos_adicionais * Decimal('2000.00')
        else:
            nascimentos_adicionais = 0
            receita_adicional_natalidade = Decimal('0.00')
        
        # Economia por reduzir mortalidade
        if gap_mortalidade > 0:
            mortes_evitadas = int(gap_mortalidade * total_animais)
            economia_mortalidade = mortes_evitadas * Decimal('3000.00')
        else:
            mortes_evitadas = 0
            economia_mortalidade = Decimal('0.00')
        
        total_melhoria = receita_adicional_natalidade + economia_mortalidade
        
        return {
            'nascimentos_adicionais': nascimentos_adicionais,
            'mortes_evitadas': mortes_evitadas,
            'receita_adicional': float(total_melhoria)
        }
    
    def _avaliar_desempenho_ano(
        self,
        parametros: Dict[str, Any],
        benchmark: Dict[str, Any]
    ) -> Dict[str, str]:
        """Avalia desempenho comparado ao benchmark"""
        avaliacao = {}
        
        # Natalidade
        natal_prop = parametros.get('taxa_natalidade', 0.75)
        natal_bench = benchmark['taxa_natalidade']
        avaliacao['natalidade'] = '✅ Acima' if natal_prop >= natal_bench else '⚠️ Abaixo'
        
        # Mortalidade
        mort_prop = parametros.get('taxa_mortalidade', 0.03)
        mort_bench = benchmark['taxa_mortalidade']
        avaliacao['mortalidade'] = '✅ Melhor' if mort_prop <= mort_bench else '⚠️ Pior'
        
        # Desfrute
        desf_prop = parametros.get('taxa_desfrute', 0.20)
        desf_bench = benchmark['taxa_desfrute']
        avaliacao['desfrute'] = '✅ Acima' if desf_prop >= desf_bench else '⚠️ Abaixo'
        
        return avaliacao
    
    def _calcular_score_geral(self, comparacoes: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula score geral de desempenho (0-100)"""
        if not comparacoes:
            return {'score': 50, 'classificacao': 'SEM DADOS'}
        
        # Somar scores de cada métrica
        total_score = 0
        count = 0
        
        for metrica, comp in comparacoes.items():
            # Score baseado na diferença percentual
            diff_perc = comp['diferenca_percentual']
            
            # Métricas positivas (quanto maior, melhor)
            if metrica in ['taxa_natalidade', 'taxa_desfrute', 'receita_por_ua_ano']:
                if diff_perc >= 10:
                    score = 100
                elif diff_perc >= 0:
                    score = 75 + (diff_perc * 2.5)
                else:
                    score = max(0, 75 + (diff_perc * 5))
            # Métricas negativas (quanto menor, melhor)
            elif metrica in ['taxa_mortalidade', 'custo_por_ua_ano']:
                if diff_perc <= -10:
                    score = 100
                elif diff_perc <= 0:
                    score = 75 + (abs(diff_perc) * 2.5)
                else:
                    score = max(0, 75 - (diff_perc * 5))
            else:
                score = 75
            
            total_score += score
            count += 1
        
        score_medio = total_score / count if count > 0 else 50
        
        # Classificar
        if score_medio >= 85:
            classificacao = 'EXCELENTE'
        elif score_medio >= 70:
            classificacao = 'BOM'
        elif score_medio >= 55:
            classificacao = 'REGULAR'
        else:
            classificacao = 'PRECISA MELHORAR'
        
        return {
            'score': score_medio,
            'classificacao': classificacao
        }
    
    def _identificar_pontos_melhoria(
        self,
        comparacoes: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Identifica principais pontos de melhoria"""
        pontos = []
        
        for metrica, comp in comparacoes.items():
            if comp['classificacao'] in ['ABAIXO DA MÉDIA', 'MUITO ABAIXO']:
                gap = abs(comp['diferenca_percentual'])
                pontos.append(f"{comp['emoji']} {metrica}: {gap:.1f}% abaixo do mercado")
        
        return pontos


# Instância global da IA
ia_evolucao_projecoes = IAEvolucaoProjecoes()

