# -*- coding: utf-8 -*-
"""
IA para Transferências Inteligentes Entre Propriedades
Otimiza balanceamento de rebanho, capacidade e logística
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Any, Tuple, Optional
from .models import Propriedade, InventarioRebanho, CategoriaAnimal


class IATransferenciasInteligentes:
    """
    IA que otimiza transferências entre propriedades baseada em:
    - Capacidade de suporte (UA - Unidades Animais)
    - Balanceamento de rebanho
    - Custos de transporte
    - Logística otimizada
    - Necessidades estratégicas
    """
    
    def __init__(self):
        # Fatores de conversão para UA (Unidade Animal = vaca de 450kg)
        self.fator_ua = {
            'Bezerros (0-12m)': 0.25,      # 1 bezerro = 0.25 UA
            'Bezerras (0-12m)': 0.25,
            'Garrotes (12-24m)': 0.50,     # 1 garrote = 0.50 UA
            'Novilhas (12-24m)': 0.50,
            'Bois Magros (24-36m)': 0.75,  # 1 boi magro = 0.75 UA
            'Primíparas (24-36m)': 0.85,   # 1 primípara = 0.85 UA
            'Multíparas (>36m)': 1.00,     # 1 multípara = 1 UA
            'Touros': 1.25,                # 1 touro = 1.25 UA
            'Vacas de Descarte': 0.90,
        }
        
        # Custo de transporte base (R$/km/UA)
        self.custo_transporte_base = Decimal('2.50')
    
    def analisar_balanceamento_propriedades(
        self,
        produtor,
        incluir_recomendacoes: bool = True
    ) -> Dict[str, Any]:
        """
        Analisa balanceamento entre todas as propriedades de um produtor
        Identifica superlotação, subutilização e oportunidades de transferência
        """
        # Obter todas as propriedades do produtor
        propriedades = Propriedade.objects.filter(produtor=produtor)
        
        analise_propriedades = []
        total_ua_sistema = 0
        total_capacidade_sistema = 0
        
        for prop in propriedades:
            analise_prop = self._analisar_capacidade_propriedade(prop)
            analise_propriedades.append(analise_prop)
            total_ua_sistema += analise_prop['ua_total']
            total_capacidade_sistema += analise_prop['capacidade_ua']
        
        # Calcular utilização média do sistema
        utilizacao_media = (total_ua_sistema / total_capacidade_sistema * 100) if total_capacidade_sistema > 0 else 0
        
        # Identificar desequilíbrios
        desequilibrios = self._identificar_desequilibrios(analise_propriedades)
        
        # Gerar recomendações de transferência
        recomendacoes = []
        if incluir_recomendacoes:
            recomendacoes = self._gerar_recomendacoes_transferencia(
                analise_propriedades,
                desequilibrios
            )
        
        return {
            'produtor': produtor.nome,
            'total_propriedades': propriedades.count(),
            'total_ua_sistema': total_ua_sistema,
            'total_capacidade_sistema': total_capacidade_sistema,
            'utilizacao_media_percentual': utilizacao_media,
            'propriedades': analise_propriedades,
            'desequilibrios': desequilibrios,
            'recomendacoes_transferencia': recomendacoes,
            'status_sistema': self._classificar_status_sistema(utilizacao_media),
            'alertas': self._gerar_alertas_sistema(analise_propriedades, utilizacao_media)
        }
    
    def calcular_transferencia_otimizada(
        self,
        propriedade_origem,
        propriedade_destino,
        categoria: str,
        quantidade: int,
        distancia_km: float
    ) -> Dict[str, Any]:
        """
        Calcula os custos e viabilidade de uma transferência específica
        """
        # Análise de capacidade
        analise_origem = self._analisar_capacidade_propriedade(propriedade_origem)
        analise_destino = self._analisar_capacidade_propriedade(propriedade_destino)
        
        # Converter quantidade para UA
        ua_transferencia = quantidade * self.fator_ua.get(categoria, 0.75)
        
        # Verificar viabilidade
        viabilidade = self._verificar_viabilidade_transferencia(
            analise_origem,
            analise_destino,
            ua_transferencia
        )
        
        # Calcular custos
        custos = self._calcular_custos_transferencia(
            quantidade,
            ua_transferencia,
            distancia_km,
            categoria
        )
        
        # Benefícios esperados
        beneficios = self._calcular_beneficios_transferencia(
            analise_origem,
            analise_destino,
            ua_transferencia,
            custos['custo_total']
        )
        
        # ROI da transferência
        roi = self._calcular_roi_transferencia(beneficios, custos)
        
        return {
            'propriedade_origem': {
                'nome': propriedade_origem.nome,
                'ua_antes': analise_origem['ua_total'],
                'ua_depois': analise_origem['ua_total'] - ua_transferencia,
                'utilizacao_antes': analise_origem['percentual_utilizacao'],
                'utilizacao_depois': ((analise_origem['ua_total'] - ua_transferencia) / analise_origem['capacidade_ua'] * 100) if analise_origem['capacidade_ua'] > 0 else 0
            },
            'propriedade_destino': {
                'nome': propriedade_destino.nome,
                'ua_antes': analise_destino['ua_total'],
                'ua_depois': analise_destino['ua_total'] + ua_transferencia,
                'utilizacao_antes': analise_destino['percentual_utilizacao'],
                'utilizacao_depois': ((analise_destino['ua_total'] + ua_transferencia) / analise_destino['capacidade_ua'] * 100) if analise_destino['capacidade_ua'] > 0 else 0
            },
            'transferencia': {
                'categoria': categoria,
                'quantidade': quantidade,
                'ua_transferidas': ua_transferencia,
                'distancia_km': distancia_km
            },
            'viabilidade': viabilidade,
            'custos': custos,
            'beneficios': beneficios,
            'roi': roi,
            'recomendacao': self._gerar_recomendacao_transferencia(viabilidade, roi)
        }
    
    def sugerir_transferencias_automaticas(
        self,
        produtor,
        mes_atual: int
    ) -> List[Dict[str, Any]]:
        """
        Sugere transferências automáticas para balancear o sistema
        """
        # Analisar balanceamento
        analise = self.analisar_balanceamento_propriedades(produtor, incluir_recomendacoes=False)
        
        propriedades_superlotadas = []
        propriedades_subutilizadas = []
        
        for prop_analise in analise['propriedades']:
            utilizacao = prop_analise['percentual_utilizacao']
            
            if utilizacao > 85:
                propriedades_superlotadas.append(prop_analise)
            elif utilizacao < 50:
                propriedades_subutilizadas.append(prop_analise)
        
        # Gerar sugestões de transferência
        sugestoes = []
        
        for origem in propriedades_superlotadas:
            for destino in propriedades_subutilizadas:
                # Calcular quantidade ideal a transferir
                ua_excesso = origem['ua_excesso']
                ua_disponivel_destino = destino['ua_disponivel']
                
                ua_a_transferir = min(ua_excesso, ua_disponivel_destino * 0.80)  # 80% do disponível
                
                if ua_a_transferir >= 5:  # Mínimo de 5 UA
                    # Determinar categoria ideal para transferir
                    categoria_sugerida = self._determinar_categoria_transferencia(
                        origem['inventario'],
                        destino['perfil']
                    )
                    
                    if categoria_sugerida:
                        # Calcular quantidade de animais
                        fator = self.fator_ua.get(categoria_sugerida['nome'], 0.75)
                        quantidade_animais = int(ua_a_transferir / fator)
                        
                        # Estimar distância (simplificado - usar Google Maps API futuramente)
                        distancia = 50.0  # km (padrão)
                        
                        # Calcular viabilidade e custos
                        transferencia = self.calcular_transferencia_otimizada(
                            Propriedade.objects.get(id=origem['id']),
                            Propriedade.objects.get(id=destino['id']),
                            categoria_sugerida['nome'],
                            quantidade_animais,
                            distancia
                        )
                        
                        if transferencia['roi']['vale_a_pena']:
                            sugestoes.append(transferencia)
        
        # Ordenar por ROI (maior primeiro)
        sugestoes.sort(key=lambda x: x['roi']['roi_percentual'], reverse=True)
        
        return sugestoes
    
    def _analisar_capacidade_propriedade(self, propriedade) -> Dict[str, Any]:
        """
        Analisa capacidade de suporte e utilização de uma propriedade
        """
        # Obter inventário atual
        inventario = InventarioRebanho.objects.filter(propriedade=propriedade)
        
        # Calcular UA total
        ua_total = 0
        inventario_detalhado = {}
        
        for item in inventario:
            categoria = item.categoria.nome
            quantidade = item.quantidade
            fator = self.fator_ua.get(categoria, 0.75)
            ua_categoria = quantidade * fator
            
            ua_total += ua_categoria
            inventario_detalhado[categoria] = {
                'quantidade': quantidade,
                'fator_ua': fator,
                'ua_total': ua_categoria
            }
        
        # Calcular capacidade (baseado em área de pastagem)
        # 1 UA = 1 hectare (regra geral, pode ser ajustado)
        area_ha = propriedade.area_total if hasattr(propriedade, 'area_total') else 100
        capacidade_ua = area_ha * 1.0  # 1 UA por hectare
        
        # Ajustar por qualidade do pasto
        qualidade_pasto = getattr(propriedade, 'qualidade_pasto', 'MEDIA')
        if qualidade_pasto == 'ALTA':
            capacidade_ua *= 1.2
        elif qualidade_pasto == 'BAIXA':
            capacidade_ua *= 0.8
        
        # Calcular utilização
        percentual_utilizacao = (ua_total / capacidade_ua * 100) if capacidade_ua > 0 else 0
        
        # Calcular UA disponível ou excesso
        if percentual_utilizacao > 100:
            ua_excesso = ua_total - capacidade_ua
            ua_disponivel = 0
            status = 'SUPERLOTADA'
        elif percentual_utilizacao > 85:
            ua_excesso = 0
            ua_disponivel = capacidade_ua - ua_total
            status = 'LOTAÇÃO_ALTA'
        elif percentual_utilizacao < 50:
            ua_excesso = 0
            ua_disponivel = capacidade_ua - ua_total
            status = 'SUBUTILIZADA'
        else:
            ua_excesso = 0
            ua_disponivel = capacidade_ua - ua_total
            status = 'ADEQUADA'
        
        return {
            'id': propriedade.id,
            'nome': propriedade.nome,
            'area_ha': area_ha,
            'capacidade_ua': capacidade_ua,
            'ua_total': ua_total,
            'percentual_utilizacao': percentual_utilizacao,
            'ua_disponivel': ua_disponivel,
            'ua_excesso': ua_excesso,
            'status': status,
            'inventario': inventario_detalhado,
            'perfil': getattr(propriedade, 'perfil', 'CICLO_COMPLETO'),
            'total_animais': sum(item.quantidade for item in inventario)
        }
    
    def _identificar_desequilibrios(
        self,
        analise_propriedades: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identifica desequilíbrios que requerem ação"""
        desequilibrios = []
        
        for analise in analise_propriedades:
            if analise['status'] == 'SUPERLOTADA':
                desequilibrios.append({
                    'tipo': 'SUPERLOTAÇÃO',
                    'gravidade': 'ALTA' if analise['percentual_utilizacao'] > 110 else 'MÉDIA',
                    'propriedade': analise['nome'],
                    'ua_excesso': analise['ua_excesso'],
                    'acao_recomendada': f"Transferir {int(analise['ua_excesso'])} UA para outras propriedades"
                })
            elif analise['status'] == 'SUBUTILIZADA':
                desequilibrios.append({
                    'tipo': 'SUBUTILIZAÇÃO',
                    'gravidade': 'MÉDIA',
                    'propriedade': analise['nome'],
                    'ua_disponivel': analise['ua_disponivel'],
                    'acao_recomendada': f"Receber {int(analise['ua_disponivel'] * 0.5)} UA de outras propriedades"
                })
        
        return desequilibrios
    
    def _gerar_recomendacoes_transferencia(
        self,
        analise_propriedades: List[Dict[str, Any]],
        desequilibrios: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Gera recomendações concretas de transferência"""
        recomendacoes = []
        
        # Identificar propriedades origem e destino
        superlotadas = [p for p in analise_propriedades if p['status'] == 'SUPERLOTADA']
        subutilizadas = [p for p in analise_propriedades if p['status'] == 'SUBUTILIZADA']
        
        for origem in superlotadas:
            for destino in subutilizadas:
                # Calcular UA a transferir
                ua_transferir = min(origem['ua_excesso'], destino['ua_disponivel'] * 0.70)
                
                if ua_transferir >= 3:  # Mínimo de 3 UA
                    # Selecionar melhor categoria para transferir
                    categoria_melhor = self._selecionar_melhor_categoria_transferencia(
                        origem['inventario'],
                        destino['perfil'],
                        ua_transferir
                    )
                    
                    if categoria_melhor:
                        recomendacoes.append({
                            'origem': origem['nome'],
                            'destino': destino['nome'],
                            'categoria': categoria_melhor['nome'],
                            'quantidade': categoria_melhor['quantidade'],
                            'ua_transferidas': ua_transferir,
                            'motivo': f"Balanceamento: origem {origem['percentual_utilizacao']:.0f}%, destino {destino['percentual_utilizacao']:.0f}%",
                            'beneficio_estimado': self._estimar_beneficio_transferencia(
                                origem['percentual_utilizacao'],
                                destino['percentual_utilizacao'],
                                ua_transferir
                            ),
                            'prioridade': self._calcular_prioridade_transferencia(
                                origem['percentual_utilizacao'],
                                ua_transferir
                            )
                        })
        
        # Ordenar por prioridade
        recomendacoes.sort(key=lambda x: x['prioridade'], reverse=True)
        
        return recomendacoes
    
    def _verificar_viabilidade_transferencia(
        self,
        analise_origem: Dict[str, Any],
        analise_destino: Dict[str, Any],
        ua_transferencia: float
    ) -> Dict[str, Any]:
        """Verifica se a transferência é viável"""
        # Verificar origem
        if ua_transferencia > analise_origem['ua_total']:
            return {
                'viavel': False,
                'motivo': 'Quantidade maior que disponível na origem'
            }
        
        # Verificar destino
        nova_utilizacao_destino = ((analise_destino['ua_total'] + ua_transferencia) / analise_destino['capacidade_ua'] * 100) if analise_destino['capacidade_ua'] > 0 else 0
        
        if nova_utilizacao_destino > 95:
            return {
                'viavel': False,
                'motivo': f'Destino ficaria superlotado ({nova_utilizacao_destino:.0f}%)'
            }
        
        # Calcular melhoria
        melhoria_origem = analise_origem['percentual_utilizacao'] - ((analise_origem['ua_total'] - ua_transferencia) / analise_origem['capacidade_ua'] * 100)
        melhoria_destino = nova_utilizacao_destino - analise_destino['percentual_utilizacao']
        
        return {
            'viavel': True,
            'melhoria_origem_percentual': melhoria_origem,
            'melhoria_destino_percentual': melhoria_destino,
            'nova_utilizacao_origem': ((analise_origem['ua_total'] - ua_transferencia) / analise_origem['capacidade_ua'] * 100) if analise_origem['capacidade_ua'] > 0 else 0,
            'nova_utilizacao_destino': nova_utilizacao_destino
        }
    
    def _calcular_custos_transferencia(
        self,
        quantidade: int,
        ua: float,
        distancia_km: float,
        categoria: str
    ) -> Dict[str, Any]:
        """Calcula todos os custos envolvidos na transferência"""
        # Custo de transporte
        custo_transporte = ua * Decimal(str(distancia_km)) * self.custo_transporte_base
        
        # Custo de manejo (R$/animal)
        custo_manejo_por_animal = Decimal('50.00')
        custo_manejo = quantidade * custo_manejo_por_animal
        
        # Custo de medicação preventiva (R$/animal)
        custo_medicacao = quantidade * Decimal('30.00')
        
        # Custo administrativo (10% do total)
        custo_base = custo_transporte + custo_manejo + custo_medicacao
        custo_administrativo = custo_base * Decimal('0.10')
        
        custo_total = custo_base + custo_administrativo
        custo_por_animal = custo_total / quantidade if quantidade > 0 else Decimal('0.00')
        
        return {
            'custo_transporte': float(custo_transporte),
            'custo_manejo': float(custo_manejo),
            'custo_medicacao': float(custo_medicacao),
            'custo_administrativo': float(custo_administrativo),
            'custo_total': float(custo_total),
            'custo_por_animal': float(custo_por_animal),
            'detalhamento': {
                'transporte': f'R$ {custo_transporte:.2f} ({ua:.1f} UA × {distancia_km}km × R$ 2.50)',
                'manejo': f'R$ {custo_manejo:.2f} ({quantidade} animais × R$ 50.00)',
                'medicacao': f'R$ {custo_medicacao:.2f} ({quantidade} animais × R$ 30.00)'
            }
        }
    
    def _calcular_beneficios_transferencia(
        self,
        analise_origem: Dict[str, Any],
        analise_destino: Dict[str, Any],
        ua_transferencia: float,
        custo_transferencia: float
    ) -> Dict[str, Any]:
        """Calcula benefícios da transferência"""
        # Benefício 1: Redução de superlotação (evita perdas)
        if analise_origem['percentual_utilizacao'] > 85:
            # Superlotação causa perdas de 2% ao mês por UA excedente
            ua_excesso_antes = max(0, analise_origem['ua_total'] - (analise_origem['capacidade_ua'] * 0.85))
            perdas_evitadas_mensal = ua_excesso_antes * Decimal('2000.00') * Decimal('0.02')  # R$ 2000/UA × 2%
            beneficio_reducao_superlotacao = perdas_evitadas_mensal * 12  # Anual
        else:
            beneficio_reducao_superlotacao = Decimal('0.00')
        
        # Benefício 2: Melhor aproveitamento de pasto subutilizado
        if analise_destino['percentual_utilizacao'] < 60:
            # Pasto subutilizado perde valor (manutenção sem retorno)
            custo_pasto_ocioso = analise_destino['ua_disponivel'] * Decimal('500.00')  # R$ 500/UA/ano
            beneficio_aproveitamento = min(custo_pasto_ocioso, ua_transferencia * Decimal('500.00'))
        else:
            beneficio_aproveitamento = Decimal('0.00')
        
        # Benefício 3: Otimização de recursos
        beneficio_otimizacao = ua_transferencia * Decimal('300.00')  # R$ 300/UA/ano
        
        beneficio_total = beneficio_reducao_superlotacao + beneficio_aproveitamento + beneficio_otimizacao
        
        return {
            'beneficio_reducao_superlotacao': float(beneficio_reducao_superlotacao),
            'beneficio_aproveitamento_pasto': float(beneficio_aproveitamento),
            'beneficio_otimizacao_recursos': float(beneficio_otimizacao),
            'beneficio_total_anual': float(beneficio_total),
            'beneficio_total_mensal': float(beneficio_total / 12)
        }
    
    def _calcular_roi_transferencia(
        self,
        beneficios: Dict[str, Any],
        custos: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcula ROI da transferência"""
        custo_total = Decimal(str(custos['custo_total']))
        beneficio_anual = Decimal(str(beneficios['beneficio_total_anual']))
        
        if custo_total == 0:
            roi_percentual = 0
            payback_meses = 0
        else:
            roi_percentual = (beneficio_anual / custo_total * 100)
            payback_meses = (custo_total / (beneficio_anual / 12)) if beneficio_anual > 0 else 999
        
        vale_a_pena = roi_percentual >= 50  # ROI mínimo de 50% ao ano
        
        return {
            'custo_inicial': float(custo_total),
            'beneficio_anual': float(beneficio_anual),
            'roi_percentual': float(roi_percentual),
            'payback_meses': float(payback_meses),
            'vale_a_pena': vale_a_pena,
            'classificacao': self._classificar_roi(roi_percentual)
        }
    
    def _classificar_roi(self, roi_percentual: float) -> str:
        """Classifica o ROI da transferência"""
        if roi_percentual >= 100:
            return 'EXCELENTE (>100%)'
        elif roi_percentual >= 50:
            return 'BOM (50-100%)'
        elif roi_percentual >= 20:
            return 'REGULAR (20-50%)'
        else:
            return 'BAIXO (<20%)'
    
    def _gerar_recomendacao_transferencia(
        self,
        viabilidade: Dict[str, Any],
        roi: Dict[str, Any]
    ) -> str:
        """Gera recomendação sobre a transferência"""
        if not viabilidade['viavel']:
            return f"❌ NÃO RECOMENDADO: {viabilidade['motivo']}"
        
        if roi['vale_a_pena']:
            return f"✅ RECOMENDADO! ROI de {roi['roi_percentual']:.0f}% ao ano. Payback em {roi['payback_meses']:.1f} meses."
        else:
            return f"⚠️ Viável, mas ROI baixo ({roi['roi_percentual']:.0f}%). Avaliar urgência."
    
    def _classificar_status_sistema(self, utilizacao_media: float) -> str:
        """Classifica status geral do sistema"""
        if utilizacao_media > 90:
            return 'CRÍTICO - Sistema superlotado'
        elif utilizacao_media > 80:
            return 'ATENÇÃO - Utilização alta'
        elif utilizacao_media >= 60:
            return 'ADEQUADO - Bem balanceado'
        elif utilizacao_media >= 40:
            return 'REGULAR - Pode melhorar'
        else:
            return 'SUBUTILIZADO - Capacidade ociosa'
    
    def _gerar_alertas_sistema(
        self,
        analise_propriedades: List[Dict[str, Any]],
        utilizacao_media: float
    ) -> List[str]:
        """Gera alertas importantes sobre o sistema"""
        alertas = []
        
        # Alertas de superlotação
        props_superlotadas = [p for p in analise_propriedades if p['status'] == 'SUPERLOTADA']
        if props_superlotadas:
            alertas.append(f"🚨 {len(props_superlotadas)} propriedade(s) superlotada(s). Ação necessária!")
        
        # Alertas de subutilização
        props_subutilizadas = [p for p in analise_propriedades if p['status'] == 'SUBUTILIZADA']
        if len(props_subutilizadas) >= 2:
            alertas.append(f"💡 {len(props_subutilizadas)} propriedade(s) subutilizada(s). Oportunidade de consolidação!")
        
        # Alerta de desequilíbrio geral
        if utilizacao_media > 85:
            alertas.append("⚠️ Sistema próximo da capacidade máxima. Considere expansão.")
        elif utilizacao_media < 45:
            alertas.append("📊 Sistema com capacidade ociosa significativa. Oportunidade de crescimento!")
        
        return alertas
    
    def _determinar_categoria_transferencia(
        self,
        inventario_origem: Dict[str, Dict[str, Any]],
        perfil_destino: str
    ) -> Optional[Dict[str, str]]:
        """Determina qual categoria é melhor para transferir"""
        # Priorizar categorias com mais animais
        categorias_ordenadas = sorted(
            inventario_origem.items(),
            key=lambda x: x[1]['quantidade'],
            reverse=True
        )
        
        # Filtrar categorias compatíveis com perfil destino
        for categoria, dados in categorias_ordenadas:
            if dados['quantidade'] >= 5:  # Mínimo para transferir
                # Verificar compatibilidade
                if self._verificar_compatibilidade_categoria_perfil(categoria, perfil_destino):
                    return {'nome': categoria, 'quantidade': dados['quantidade']}
        
        return None
    
    def _selecionar_melhor_categoria_transferencia(
        self,
        inventario_origem: Dict[str, Dict[str, Any]],
        perfil_destino: str,
        ua_alvo: float
    ) -> Optional[Dict[str, Any]]:
        """Seleciona melhor categoria para transferência baseada em UA alvo"""
        melhor_opcao = None
        menor_diferenca = float('inf')
        
        for categoria, dados in inventario_origem.items():
            if dados['quantidade'] < 5:  # Mínimo
                continue
            
            # Verificar compatibilidade
            if not self._verificar_compatibilidade_categoria_perfil(categoria, perfil_destino):
                continue
            
            # Calcular quantidade para atingir UA alvo
            fator = self.fator_ua.get(categoria, 0.75)
            quantidade_necessaria = int(ua_alvo / fator)
            quantidade_disponivel = dados['quantidade']
            
            # Limitar a 80% do estoque da categoria
            quantidade_maxima = int(quantidade_disponivel * 0.80)
            quantidade_transferir = min(quantidade_necessaria, quantidade_maxima)
            
            if quantidade_transferir >= 5:
                ua_efetiva = quantidade_transferir * fator
                diferenca = abs(ua_efetiva - ua_alvo)
                
                if diferenca < menor_diferenca:
                    menor_diferenca = diferenca
                    melhor_opcao = {
                        'nome': categoria,
                        'quantidade': quantidade_transferir,
                        'ua_efetiva': ua_efetiva
                    }
        
        return melhor_opcao
    
    def _verificar_compatibilidade_categoria_perfil(
        self,
        categoria: str,
        perfil: str
    ) -> bool:
        """Verifica se a categoria é compatível com o perfil da fazenda destino"""
        compatibilidade = {
            'SO_CRIA': ['Multíparas', 'Primíparas', 'Novilhas', 'Touros'],
            'SO_RECRIA': ['Bezerros', 'Bezerras', 'Garrotes', 'Novilhas'],
            'SO_ENGORDA': ['Garrotes', 'Novilhas', 'Bois Magros'],
            'CONFINAMENTO': ['Garrotes', 'Bois Magros'],
            'CICLO_COMPLETO': ['Bezerros', 'Bezerras', 'Garrotes', 'Novilhas', 'Bois', 'Multíparas', 'Primíparas', 'Touros']
        }
        
        categorias_compativeis = compatibilidade.get(perfil, [])
        
        return any(cat in categoria for cat in categorias_compativeis)
    
    def _estimar_beneficio_transferencia(
        self,
        utilizacao_origem: float,
        utilizacao_destino: float,
        ua_transferidas: float
    ) -> Decimal:
        """Estima benefício financeiro da transferência"""
        # Benefício de reduzir superlotação
        if utilizacao_origem > 85:
            beneficio = ua_transferidas * Decimal('800.00')  # R$ 800/UA/ano
        else:
            beneficio = ua_transferidas * Decimal('400.00')
        
        # Benefício adicional se destino está muito subutilizado
        if utilizacao_destino < 50:
            beneficio += ua_transferidas * Decimal('200.00')
        
        return beneficio
    
    def _calcular_prioridade_transferencia(
        self,
        utilizacao_origem: float,
        ua_transferidas: float
    ) -> float:
        """Calcula prioridade da transferência (0-100)"""
        # Base: quanto mais superlotada a origem, maior a prioridade
        if utilizacao_origem > 100:
            prioridade_base = 100
        elif utilizacao_origem > 90:
            prioridade_base = 80
        elif utilizacao_origem > 80:
            prioridade_base = 60
        else:
            prioridade_base = 40
        
        # Ajuste por quantidade: transferências maiores são mais prioritárias
        ajuste_quantidade = min(20, ua_transferidas * 2)
        
        return min(100, prioridade_base + ajuste_quantidade)


# Instância global da IA
ia_transferencias_inteligentes = IATransferenciasInteligentes()

