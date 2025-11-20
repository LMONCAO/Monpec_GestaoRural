# -*- coding: utf-8 -*-
"""
IA Aprimorada para Nascimentos Automáticos
Implementa sazonalidade, proporção M/F, mortalidade neonatal e previsões inteligentes
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Tuple
from .models import MovimentacaoProjetada, CategoriaAnimal


class IANascimentosAprimorada:
    """
    IA avançada para previsão e geração de nascimentos com:
    - Sazonalidade (épocas de monta)
    - Proporção machos/fêmeas configurável
    - Mortalidade neonatal diferenciada
    - Taxa de natalidade variável por estação
    """
    
    # Meses de alta estação de monta (setembro a dezembro)
    MESES_ALTA_ESTACAO = [9, 10, 11, 12]
    
    # Meses de nascimento (9 meses após monta) - junho a setembro
    MESES_NASCIMENTO_ALTO = [6, 7, 8, 9]
    
    def __init__(self):
        self.configuracoes = {
            # Proporções naturais
            'proporcao_machos': 0.52,  # 52% machos
            'proporcao_femeas': 0.48,  # 48% fêmeas
            
            # Taxas de natalidade por estação
            'natalidade_alta_estacao': 0.85,  # 85% em alta estação
            'natalidade_baixa_estacao': 0.65,  # 65% em baixa estação
            
            # Mortalidade neonatal (primeiros dias de vida)
            'mortalidade_neonatal_7dias': 0.03,  # 3% nos primeiros 7 dias
            'mortalidade_neonatal_30dias': 0.02,  # 2% de 7 a 30 dias
            
            # Gestação (meses)
            'tempo_gestacao': 9,
            
            # Intervalo entre partos (meses)
            'intervalo_entre_partos': 12,
        }
    
    def gerar_nascimentos_inteligentes(
        self,
        propriedade,
        data_referencia: datetime,
        saldos_iniciais: Dict[str, int],
        parametros,
        perfil_fazenda: str = 'CICLO_COMPLETO'
    ) -> List[MovimentacaoProjetada]:
        """
        Gera nascimentos com IA aprimorada considerando todos os fatores
        """
        nascimentos = []
        
        # 1. Calcular número de matrizes disponíveis
        matrizes_disponiveis = self._calcular_matrizes_disponiveis(saldos_iniciais)
        
        if matrizes_disponiveis == 0:
            return nascimentos
        
        # 2. Verificar se é época de nascimento (baseado na sazonalidade)
        taxa_natalidade = self._calcular_taxa_natalidade_mes(data_referencia.month, parametros)
        
        if taxa_natalidade == 0:
            return nascimentos
        
        # 3. Calcular total de nascimentos esperados no mês
        total_nascimentos = self._calcular_total_nascimentos(
            matrizes_disponiveis,
            taxa_natalidade,
            data_referencia
        )
        
        if total_nascimentos == 0:
            return nascimentos
        
        # 4. Distribuir nascimentos por sexo
        bezerros, bezerras = self._distribuir_por_sexo(total_nascimentos)
        
        # 5. Aplicar mortalidade neonatal
        bezerros_sobreviventes, bezerras_sobreviventes = self._aplicar_mortalidade_neonatal(
            bezerros, bezerras
        )
        
        # 6. Criar movimentações de nascimento
        try:
            categoria_bezerros = CategoriaAnimal.objects.get(nome='Bezerros (0-12m)')
            categoria_bezerras = CategoriaAnimal.objects.get(nome='Bezerras (0-12m)')
            
            # Registrar nascimentos de bezerros
            if bezerros_sobreviventes > 0:
                nascimentos.append(MovimentacaoProjetada(
                    propriedade=propriedade,
                    data_movimentacao=data_referencia,
                    tipo_movimentacao='NASCIMENTO',
                    categoria=categoria_bezerros,
                    quantidade=bezerros_sobreviventes,
                    observacao=self._gerar_observacao_nascimento(
                        bezerros_sobreviventes,
                        bezerros - bezerros_sobreviventes,
                        'machos',
                        taxa_natalidade,
                        data_referencia.month
                    )
                ))
            
            # Registrar nascimentos de bezerras
            if bezerras_sobreviventes > 0:
                nascimentos.append(MovimentacaoProjetada(
                    propriedade=propriedade,
                    data_movimentacao=data_referencia,
                    tipo_movimentacao='NASCIMENTO',
                    categoria=categoria_bezerras,
                    quantidade=bezerras_sobreviventes,
                    observacao=self._gerar_observacao_nascimento(
                        bezerras_sobreviventes,
                        bezerras - bezerras_sobreviventes,
                        'fêmeas',
                        taxa_natalidade,
                        data_referencia.month
                    )
                ))
            
            # 7. Registrar mortalidade neonatal (se houver)
            if (bezerros - bezerros_sobreviventes) > 0 or (bezerras - bezerras_sobreviventes) > 0:
                nascimentos.extend(self._registrar_mortalidade_neonatal(
                    propriedade,
                    data_referencia,
                    categoria_bezerros,
                    categoria_bezerras,
                    bezerros - bezerros_sobreviventes,
                    bezerras - bezerras_sobreviventes
                ))
            
            print(f"    👶 Nascimentos Inteligentes:")
            print(f"       • {bezerros_sobreviventes} bezerros (♂)")
            print(f"       • {bezerras_sobreviventes} bezerras (♀)")
            print(f"       • Total: {bezerros_sobreviventes + bezerras_sobreviventes}")
            print(f"       • Taxa natalidade: {taxa_natalidade*100:.1f}%")
            print(f"       • Época: {'Alta' if data_referencia.month in self.MESES_NASCIMENTO_ALTO else 'Normal'}")
            
            if (bezerros + bezerras) != (bezerros_sobreviventes + bezerras_sobreviventes):
                mortes = (bezerros + bezerras) - (bezerros_sobreviventes + bezerras_sobreviventes)
                print(f"       ⚠️ Mortalidade neonatal: {mortes} ({mortes/(bezerros+bezerras)*100:.1f}%)")
        
        except CategoriaAnimal.DoesNotExist:
            print("    ⚠️ Categorias de bezerros não encontradas")
        
        return nascimentos
    
    def _calcular_matrizes_disponiveis(self, saldos_iniciais: Dict[str, int]) -> int:
        """Calcula o número de matrizes disponíveis para reprodução"""
        multiparas = saldos_iniciais.get('Multíparas (>36m)', 0)
        primiparas = saldos_iniciais.get('Primíparas (24-36m)', 0)
        
        # Primíparas têm taxa de concepção 85% das multíparas
        primiparas_ajustadas = int(primiparas * 0.85)
        
        return multiparas + primiparas_ajustadas
    
    def _calcular_taxa_natalidade_mes(self, mes: int, parametros) -> float:
        """
        Calcula taxa de natalidade baseada na sazonalidade
        Nascimentos ocorrem 9 meses após a monta
        """
        # Taxa base anual
        taxa_base_anual = parametros.taxa_natalidade_anual / 100
        
        # Verificar se é época de nascimento (alta estação)
        if mes in self.MESES_NASCIMENTO_ALTO:
            # Alta estação: 60% dos nascimentos ocorrem nesses meses
            # Distribuir 60% dos nascimentos anuais em 4 meses
            taxa_mensal = (taxa_base_anual * 0.60) / 4
        else:
            # Baixa estação: 40% dos nascimentos nos outros 8 meses
            taxa_mensal = (taxa_base_anual * 0.40) / 8
        
        return taxa_mensal
    
    def _calcular_total_nascimentos(
        self,
        matrizes: int,
        taxa_natalidade: float,
        data_referencia: datetime
    ) -> int:
        """
        Calcula total de nascimentos esperados considerando todos os fatores
        """
        # Nascimentos base
        nascimentos_base = matrizes * taxa_natalidade
        
        # Ajuste por fatores ambientais (exemplo: clima)
        fator_ambiental = self._calcular_fator_ambiental(data_referencia.month)
        
        # Ajuste por estresse do rebanho (simplificado)
        fator_estresse = 0.95  # 5% de redução por estresse médio
        
        # Total ajustado
        total = int(nascimentos_base * fator_ambiental * fator_estresse)
        
        return max(0, total)
    
    def _calcular_fator_ambiental(self, mes: int) -> float:
        """
        Calcula fator de ajuste ambiental por mês
        Considera clima, disponibilidade de pasto, etc.
        """
        # Meses favoráveis (junho-setembro): melhor clima pós-parto
        if mes in [6, 7, 8, 9]:
            return 1.05  # 5% a mais
        # Meses de seca extrema (outubro-novembro)
        elif mes in [10, 11]:
            return 0.92  # 8% a menos
        # Meses de chuva intensa (janeiro-março)
        elif mes in [1, 2, 3]:
            return 0.95  # 5% a menos
        # Outros meses: normal
        else:
            return 1.0
    
    def _distribuir_por_sexo(self, total_nascimentos: int) -> Tuple[int, int]:
        """
        Distribui nascimentos entre machos e fêmeas
        Usa proporção natural com pequena variação aleatória
        """
        import random
        
        # Proporção base
        prop_machos = self.configuracoes['proporcao_machos']
        
        # Adicionar pequena variação aleatória (+/- 5%)
        variacao = random.uniform(-0.05, 0.05)
        prop_machos_ajustada = max(0.45, min(0.55, prop_machos + variacao))
        
        bezerros = int(total_nascimentos * prop_machos_ajustada)
        bezerras = total_nascimentos - bezerros
        
        return bezerros, bezerras
    
    def _aplicar_mortalidade_neonatal(
        self,
        bezerros: int,
        bezerras: int
    ) -> Tuple[int, int]:
        """
        Aplica mortalidade neonatal (primeiros 30 dias)
        """
        # Taxa total de mortalidade neonatal (primeiros 30 dias)
        taxa_mortalidade = (
            self.configuracoes['mortalidade_neonatal_7dias'] +
            self.configuracoes['mortalidade_neonatal_30dias']
        )
        
        # Aplicar mortalidade
        bezerros_sobreviventes = int(bezerros * (1 - taxa_mortalidade))
        bezerras_sobreviventes = int(bezerras * (1 - taxa_mortalidade))
        
        # Garantir pelo menos 0
        return max(0, bezerros_sobreviventes), max(0, bezerras_sobreviventes)
    
    def _gerar_observacao_nascimento(
        self,
        quantidade_sobrevivente: int,
        quantidade_morta: int,
        sexo: str,
        taxa_natalidade: float,
        mes: int
    ) -> str:
        """Gera observação detalhada sobre o nascimento"""
        epoca = 'Alta Estação' if mes in self.MESES_NASCIMENTO_ALTO else 'Estação Normal'
        
        obs = f"Nascimentos IA - {quantidade_sobrevivente} {sexo} ({epoca})"
        obs += f" | Natalidade: {taxa_natalidade*100:.1f}%"
        
        if quantidade_morta > 0:
            taxa_mort = (quantidade_morta / (quantidade_sobrevivente + quantidade_morta)) * 100
            obs += f" | Mortalidade neonatal: {quantidade_morta} ({taxa_mort:.1f}%)"
        
        return obs
    
    def _registrar_mortalidade_neonatal(
        self,
        propriedade,
        data_referencia: datetime,
        categoria_bezerros: CategoriaAnimal,
        categoria_bezerras: CategoriaAnimal,
        mortes_bezerros: int,
        mortes_bezerras: int
    ) -> List[MovimentacaoProjetada]:
        """Registra mortes neonatais como movimentações"""
        mortes = []
        
        # Mortes ocorrem alguns dias após o nascimento
        data_morte = data_referencia + timedelta(days=15)
        
        if mortes_bezerros > 0:
            mortes.append(MovimentacaoProjetada(
                propriedade=propriedade,
                data_movimentacao=data_morte,
                tipo_movimentacao='MORTE',
                categoria=categoria_bezerros,
                quantidade=mortes_bezerros,
                observacao=f'Mortalidade neonatal - {mortes_bezerros} bezerros (primeiros 30 dias)'
            ))
        
        if mortes_bezerras > 0:
            mortes.append(MovimentacaoProjetada(
                propriedade=propriedade,
                data_movimentacao=data_morte,
                tipo_movimentacao='MORTE',
                categoria=categoria_bezerras,
                quantidade=mortes_bezerras,
                observacao=f'Mortalidade neonatal - {mortes_bezerras} bezerras (primeiros 30 dias)'
            ))
        
        return mortes
    
    def prever_nascimentos_proximo_ano(
        self,
        matrizes_atuais: int,
        parametros
    ) -> Dict[int, int]:
        """
        Prevê nascimentos mês a mês para o próximo ano
        Útil para planejamento
        """
        previsao = {}
        
        for mes in range(1, 13):
            taxa_mensal = self._calcular_taxa_natalidade_mes(mes, parametros)
            fator_ambiental = self._calcular_fator_ambiental(mes)
            
            nascimentos_previstos = int(
                matrizes_atuais * taxa_mensal * fator_ambiental * 0.95
            )
            
            # Aplicar mortalidade neonatal prevista
            taxa_sobrevivencia = 1 - (
                self.configuracoes['mortalidade_neonatal_7dias'] +
                self.configuracoes['mortalidade_neonatal_30dias']
            )
            
            nascimentos_liquidos = int(nascimentos_previstos * taxa_sobrevivencia)
            
            previsao[mes] = nascimentos_liquidos
        
        return previsao
    
    def calcular_capacidade_reproducao(
        self,
        inventario_atual: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Calcula capacidade reprodutiva do rebanho
        Útil para decisões estratégicas
        """
        # Matrizes atuais
        multiparas = inventario_atual.get('Multíparas (>36m)', 0)
        primiparas = inventario_atual.get('Primíparas (24-36m)', 0)
        novilhas = inventario_atual.get('Novilhas (12-24m)', 0)
        bezerras = inventario_atual.get('Bezerras (0-12m)', 0)
        
        # Touros
        touros = inventario_atual.get('Touros', 0)
        
        # Capacidade atual
        capacidade_atual = multiparas + (primiparas * 0.85)
        
        # Capacidade futura (em 1 ano)
        capacidade_1ano = capacidade_atual + novilhas
        
        # Capacidade futura (em 2 anos)
        capacidade_2anos = capacidade_1ano + bezerras
        
        # Relação touro:vaca ideal (1:25)
        touros_necessarios = int(capacidade_atual / 25) + 1
        
        return {
            'capacidade_atual': int(capacidade_atual),
            'capacidade_1ano': int(capacidade_1ano),
            'capacidade_2anos': int(capacidade_2anos),
            'multiparas': multiparas,
            'primiparas': primiparas,
            'novilhas_futuras': novilhas,
            'bezerras_futuras': bezerras,
            'touros_atuais': touros,
            'touros_necessarios': touros_necessarios,
            'deficit_touros': max(0, touros_necessarios - touros),
            'taxa_reposicao_anual': 0.20,  # 20% de reposição recomendada
            'femeas_reposicao_necessarias': int(capacidade_atual * 0.20)
        }


# Instância global da IA
ia_nascimentos_aprimorada = IANascimentosAprimorada()

