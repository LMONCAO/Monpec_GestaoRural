"""Serviços auxiliares para análise e consolidação do planejamento pecuário."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterable, List, Optional, Tuple

from django.db.models import Q, Sum
from django.utils import timezone

from gestao_rural.models import (
    CategoriaAnimal,
    InventarioRebanho,
    MovimentacaoIndividual,
    MovimentacaoProjetada,
    PlanejamentoAnual,
    Propriedade,
)
try:
    from gestao_rural.models_financeiro import MovimentoFinanceiro
except ImportError:  # pragma: no cover - compatibilidade com variações do projeto
    MovimentoFinanceiro = None
from gestao_rural.models_reproducao import Nascimento

DECIMAL_ZERO = Decimal("0")
UZ_PESO_PADRAO = Decimal("450")
ARROBA_PESO_PADRAO = Decimal("15")

MATRIZES_KEYWORDS = ['vaca', 'matriz', 'primípara', 'primipara', 'multípara', 'multipara']
DESCARTE_KEYWORDS = ['descarte']
ENGORDA_KEYWORDS = ['engorda', 'boi', 'garrote', 'touro', 'terminado']


def _categoria_tem_keywords(nome_categoria: str, keywords: Iterable[str]) -> bool:
    nome = (nome_categoria or '').lower()
    return any(kw in nome for kw in keywords)


def _estimar_peso_categoria(categoria: Optional[CategoriaAnimal]) -> Decimal:
    if not categoria:
        return Decimal('380')
    if getattr(categoria, 'peso_medio_kg', None):
        return categoria.peso_medio_kg
    nome = (categoria.nome or '').lower()
    if 'bezerra' in nome or 'bezerr' in nome:
        return Decimal('180')
    if 'novilha' in nome:
        return Decimal('320')
    if 'garrote' in nome:
        return Decimal('360')
    if 'boi' in nome or 'touro' in nome or 'engorda' in nome:
        return Decimal('430')
    if 'vaca' in nome or 'matriz' in nome or 'multípara' in nome or 'multipara' in nome:
        return Decimal('420')
    return Decimal('380')


def _calcular_valor_movimentacao_planejada(mov: MovimentacaoProjetada) -> Decimal:
    if mov.valor_total is not None:
        return mov.valor_total
    if mov.valor_por_cabeca is not None:
        return mov.valor_por_cabeca * Decimal(mov.quantidade)
    return DECIMAL_ZERO


def _obter_categoria_movimentacao(mov: MovimentacaoIndividual) -> Optional[CategoriaAnimal]:
    if getattr(mov, 'categoria_nova', None):
        return mov.categoria_nova
    if getattr(mov, 'categoria_anterior', None):
        return mov.categoria_anterior
    if mov.animal_id and getattr(mov.animal, 'categoria', None):
        return mov.animal.categoria
    return None


def _decimal_or(valor: Optional[Decimal]) -> Decimal:
    return valor if valor is not None else DECIMAL_ZERO


@dataclass
class FinanceiroResumo:
    planejado_receitas: Decimal = DECIMAL_ZERO
    planejado_custos: Decimal = DECIMAL_ZERO
    planejado_investimentos: Decimal = DECIMAL_ZERO
    realizado_receitas: Decimal = DECIMAL_ZERO
    realizado_custos: Decimal = DECIMAL_ZERO

    @property
    def planejado_resultado(self) -> Decimal:
        return self.planejado_receitas - (self.planejado_custos + self.planejado_investimentos)

    @property
    def realizado_resultado(self) -> Decimal:
        return self.realizado_receitas - self.realizado_custos


class PlanejamentoAnalyzer:
    """Consolida dados planejados x realizados de uma propriedade/ano."""

    def __init__(
        self,
        propriedade: Propriedade,
        planejamento: Optional[PlanejamentoAnual] = None,
        cenario=None,
        ano: Optional[int] = None,
    ) -> None:
        self.propriedade = propriedade
        self.planejamento = planejamento
        self.cenario = cenario
        self.ano = ano or (planejamento.ano if planejamento else timezone.now().year)

        self._inventario_cache: Optional[Dict[str, object]] = None
        self._movimentos_planejados_cache: Optional[Dict[str, object]] = None
        self._movimentos_realizados_cache: Optional[Dict[str, object]] = None
        self._financeiro_cache: Optional[FinanceiroResumo] = None
        self._movimentos_mensais: Dict[str, Dict[str, Dict[str, Decimal]]] = {}

    # ------------------------------------------------------------------ Inventário
    def inventario_resumo(self) -> Dict[str, object]:
        if self._inventario_cache is not None:
            return self._inventario_cache

        qs = (
            InventarioRebanho.objects.filter(propriedade=self.propriedade)
            .select_related('categoria')
            .order_by('-data_inventario', 'categoria__nome')
        )

        inventario: List[InventarioRebanho] = []
        data_recente = None
        if qs.exists():
            data_recente = qs.first().data_inventario
            inventario = list(qs.filter(data_inventario=data_recente))
            if not inventario:
                inventario = list(qs)

        total_animais = sum(item.quantidade for item in inventario)
        valor_total_rebanho = sum(item.valor_total for item in inventario) if inventario else DECIMAL_ZERO

        matrizes = sum(
            item.quantidade
            for item in inventario
            if _categoria_tem_keywords(item.categoria.nome, MATRIZES_KEYWORDS)
        )
        vacas_descarte = sum(
            item.quantidade
            for item in inventario
            if _categoria_tem_keywords(item.categoria.nome, DESCARTE_KEYWORDS)
        )
        animais_engorda = sum(
            item.quantidade
            for item in inventario
            if _categoria_tem_keywords(item.categoria.nome, ENGORDA_KEYWORDS)
        )

        ua_total = DECIMAL_ZERO
        arrobas_total = DECIMAL_ZERO
        for item in inventario:
            peso_estimado = _estimar_peso_categoria(item.categoria)
            ua_total += (peso_estimado / UZ_PESO_PADRAO) * Decimal(item.quantidade)
            arrobas_total += (peso_estimado / ARROBA_PESO_PADRAO) * Decimal(item.quantidade)

        area_total = self.propriedade.area_total_ha or DECIMAL_ZERO
        ua_por_hectare = (ua_total / area_total) if area_total else DECIMAL_ZERO
        animais_por_hectare = (Decimal(total_animais) / area_total) if area_total else DECIMAL_ZERO
        valor_por_hectare = (valor_total_rebanho / area_total) if area_total else DECIMAL_ZERO

        self._inventario_cache = {
            'itens': inventario,
            'data': data_recente,
            'total_animais': total_animais,
            'valor_total_rebanho': valor_total_rebanho,
            'matrizes': matrizes,
            'vacas_descarte': vacas_descarte,
            'animais_engorda': animais_engorda,
            'ua_total': ua_total,
            'ua_por_hectare': ua_por_hectare,
            'animais_por_hectare': animais_por_hectare,
            'valor_por_hectare': valor_por_hectare,
            'arrobas_inventario': arrobas_total,
        }
        return self._inventario_cache

    # ------------------------------------------------------------ Movimentações
    def _init_slot_mes(self, chave_mes: str) -> Dict[str, Dict[str, Decimal]]:
        return self._movimentos_mensais.setdefault(
            chave_mes,
            {
                'planejado': defaultdict(lambda: Decimal('0')),
                'realizado': defaultdict(lambda: Decimal('0')),
            },
        )

    def movimentacoes_planejadas(self) -> Dict[str, object]:
        if self._movimentos_planejados_cache is not None:
            return self._movimentos_planejados_cache

        qs = MovimentacaoProjetada.objects.filter(propriedade=self.propriedade)
        if self.planejamento:
            qs = qs.filter(Q(planejamento=self.planejamento) | Q(planejamento__isnull=True))
        if self.cenario:
            qs = qs.filter(cenario=self.cenario)

        qs = qs.select_related('categoria').order_by('data_movimentacao')

        totais = {
            'COMPRA': {'quantidade': 0, 'valor': DECIMAL_ZERO},
            'VENDA': {'quantidade': 0, 'valor': DECIMAL_ZERO, 'arrobas': DECIMAL_ZERO},
            'NASCIMENTO': {'quantidade': 0},
            'MORTE': {'quantidade': 0},
            'TRANSFERENCIA_ENTRADA': {'quantidade': 0},
            'TRANSFERENCIA_SAIDA': {'quantidade': 0},
        }

        for mov in qs:
            chave_mes = mov.data_movimentacao.strftime('%Y-%m')
            slot = self._init_slot_mes(chave_mes)
            valor = _calcular_valor_movimentacao_planejada(mov)

            if mov.tipo_movimentacao == 'COMPRA':
                totais['COMPRA']['quantidade'] += mov.quantidade
                totais['COMPRA']['valor'] += valor
                slot['planejado']['compras'] += Decimal(mov.quantidade)
            elif mov.tipo_movimentacao == 'VENDA':
                totais['VENDA']['quantidade'] += mov.quantidade
                totais['VENDA']['valor'] += valor
                peso_est = _estimar_peso_categoria(mov.categoria)
                arrobas = (peso_est / ARROBA_PESO_PADRAO) * Decimal(mov.quantidade)
                totais['VENDA']['arrobas'] += arrobas
                slot['planejado']['vendas'] += Decimal(mov.quantidade)
            elif mov.tipo_movimentacao == 'NASCIMENTO':
                totais['NASCIMENTO']['quantidade'] += mov.quantidade
                slot['planejado']['nascimentos'] += Decimal(mov.quantidade)
            elif mov.tipo_movimentacao == 'MORTE':
                totais['MORTE']['quantidade'] += mov.quantidade
                slot['planejado']['mortes'] += Decimal(mov.quantidade)
            elif mov.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA':
                totais['TRANSFERENCIA_ENTRADA']['quantidade'] += mov.quantidade
                slot['planejado']['transferencias_entrada'] += Decimal(mov.quantidade)
            elif mov.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
                totais['TRANSFERENCIA_SAIDA']['quantidade'] += mov.quantidade
                slot['planejado']['transferencias_saida'] += Decimal(mov.quantidade)

        investimento_previsto = totais['COMPRA']['valor']
        resultado_planejado = totais['VENDA']['valor'] - totais['COMPRA']['valor']

        self._movimentos_planejados_cache = {
            'totais': totais,
            'investimento_previsto': investimento_previsto,
            'resultado_planejado': resultado_planejado,
        }
        return self._movimentos_planejados_cache

    def _movimento_relevante_para_propriedade(self, mov: MovimentacaoIndividual) -> bool:
        tipo = mov.tipo_movimentacao
        prop = self.propriedade

        if tipo in {'PESAGEM', 'VACINACAO', 'TRATAMENTO', 'OUTROS', 'MUDANCA_CATEGORIA'}:
            return False
        if tipo in {'COMPRA', 'TRANSFERENCIA_ENTRADA'}:
            return mov.propriedade_destino_id == prop.id
        if tipo in {'VENDA', 'TRANSFERENCIA_SAIDA'}:
            return mov.propriedade_origem_id == prop.id
        if tipo == 'NASCIMENTO':
            return (
                mov.propriedade_destino_id == prop.id
                or mov.propriedade_origem_id == prop.id
                or (mov.animal_id and mov.animal.propriedade_id == prop.id)
            )
        if tipo == 'MORTE':
            return (
                mov.propriedade_origem_id == prop.id
                or (mov.animal_id and mov.animal.propriedade_id == prop.id)
            )
        return False

    def movimentacoes_realizadas(self) -> Dict[str, object]:
        if self._movimentos_realizados_cache is not None:
            return self._movimentos_realizados_cache

        qs = (
            MovimentacaoIndividual.objects.filter(data_movimentacao__year=self.ano)
            .filter(
                Q(propriedade_origem=self.propriedade)
                | Q(propriedade_destino=self.propriedade)
                | Q(animal__propriedade=self.propriedade)
            )
            .select_related('animal__categoria', 'categoria_anterior', 'categoria_nova')
            .order_by('data_movimentacao')
        )

        totais = {
            'COMPRA': {'quantidade': 0, 'valor': DECIMAL_ZERO},
            'VENDA': {'quantidade': 0, 'valor': DECIMAL_ZERO, 'arrobas': DECIMAL_ZERO},
            'NASCIMENTO': {'quantidade': 0},
            'MORTE': {'quantidade': 0},
            'TRANSFERENCIA_ENTRADA': {'quantidade': 0},
            'TRANSFERENCIA_SAIDA': {'quantidade': 0},
        }

        for mov in qs:
            if not self._movimento_relevante_para_propriedade(mov):
                continue

            chave_mes = mov.data_movimentacao.strftime('%Y-%m')
            slot = self._init_slot_mes(chave_mes)
            quantidade = getattr(mov, 'quantidade_animais', None) or 1
            quantidade_decimal = Decimal(quantidade)
            valor = _decimal_or(mov.valor)
            categoria = _obter_categoria_movimentacao(mov)

            if mov.tipo_movimentacao == 'COMPRA':
                totais['COMPRA']['quantidade'] += quantidade
                totais['COMPRA']['valor'] += valor
                slot['realizado']['compras'] += quantidade_decimal
            elif mov.tipo_movimentacao == 'VENDA':
                totais['VENDA']['quantidade'] += quantidade
                totais['VENDA']['valor'] += valor
                peso_est = _estimar_peso_categoria(categoria)
                arrobas = (peso_est / ARROBA_PESO_PADRAO) * quantidade_decimal
                totais['VENDA']['arrobas'] += arrobas
                slot['realizado']['vendas'] += quantidade_decimal
                slot['realizado']['arrobas_vendidas'] += arrobas
            elif mov.tipo_movimentacao == 'NASCIMENTO':
                totais['NASCIMENTO']['quantidade'] += quantidade
                slot['realizado']['nascimentos'] += quantidade_decimal
            elif mov.tipo_movimentacao == 'MORTE':
                totais['MORTE']['quantidade'] += quantidade
                slot['realizado']['mortes'] += quantidade_decimal
            elif mov.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA':
                totais['TRANSFERENCIA_ENTRADA']['quantidade'] += quantidade
                slot['realizado']['transferencias_entrada'] += quantidade_decimal
            elif mov.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
                totais['TRANSFERENCIA_SAIDA']['quantidade'] += quantidade
                slot['realizado']['transferencias_saida'] += quantidade_decimal

        self._movimentos_realizados_cache = {
            'totais': totais,
        }
        return self._movimentos_realizados_cache

    # --------------------------------------------------------------- Financeiro
    def financeiro_resumo(
        self,
        metas_financeiras: Optional[Iterable] = None,
        metas_comerciais: Optional[Iterable] = None,
    ) -> FinanceiroResumo:
        if self._financeiro_cache is not None:
            return self._financeiro_cache

        resumo = FinanceiroResumo()

        if metas_comerciais:
            for meta in metas_comerciais:
                quantidade = Decimal(meta.quantidade_animais or 0)
                preco = _decimal_or(meta.preco_medio_esperado)
                resumo.planejado_receitas += quantidade * preco
        if metas_financeiras:
            for meta in metas_financeiras:
                valor_meta = _decimal_or(meta.valor_anual_previsto)
                if getattr(meta, 'tipo_custo', '') == 'INVESTIMENTO':
                    resumo.planejado_investimentos += valor_meta
                else:
                    resumo.planejado_custos += valor_meta

        if MovimentoFinanceiro is not None:
            try:
                movimentos_fin = (
                    MovimentoFinanceiro.objects.filter(
                        conta__propriedade=self.propriedade,
                        data_movimento__year=self.ano,
                    )
                    .exclude(origem='TRANSFERENCIA')
                )
                total_receitas = movimentos_fin.filter(tipo='ENTRADA').aggregate(total=Sum('valor_liquido'))['total'] or DECIMAL_ZERO
                total_custos = movimentos_fin.filter(tipo='SAIDA').aggregate(total=Sum('valor_liquido'))['total'] or DECIMAL_ZERO

                resumo.realizado_receitas = total_receitas
                resumo.realizado_custos = abs(total_custos)
            except Exception:
                # Se a tabela não existir ou houver erro, usar valores zero
                resumo.realizado_receitas = DECIMAL_ZERO
                resumo.realizado_custos = DECIMAL_ZERO
        else:
            resumo.realizado_receitas = DECIMAL_ZERO
            resumo.realizado_custos = DECIMAL_ZERO

        self._financeiro_cache = resumo
        return resumo

    # --------------------------------------------------------------- Indicadores
    def indicadores_realizados(self, indicadores: Iterable) -> Dict[int, Dict[str, Optional[Decimal]]]:
        inventario = self.inventario_resumo()
        movimentos_planejados = self.movimentacoes_planejadas()
        movimentos_realizados = self.movimentacoes_realizadas()
        financeiro = self.financeiro_resumo()

        total_matrizes = inventario.get('matrizes', 0) or 0
        nascimentos_planejados = movimentos_planejados['totais']['NASCIMENTO']['quantidade']
        nascimentos_realizados = movimentos_realizados['totais']['NASCIMENTO']['quantidade']

        nascimentos_realizados_registrados = Nascimento.objects.filter(
            propriedade=self.propriedade,
            data_nascimento__year=self.ano,
        ).count()
        if nascimentos_realizados_registrados > nascimentos_realizados:
            nascimentos_realizados = nascimentos_realizados_registrados

        arrobas_vendidas = movimentos_realizados['totais']['VENDA']['arrobas']
        area_total = self.propriedade.area_total_ha or DECIMAL_ZERO
        total_animais = inventario.get('total_animais', 0) or 0

        resultados: Dict[int, Dict[str, Optional[Decimal]]] = {}

        for indicador in indicadores:
            codigo = (indicador.codigo or '').upper()
            valor_meta = indicador.valor_meta or DECIMAL_ZERO
            valor_realizado: Optional[Decimal] = None

            if codigo == 'TAXA_PRENHEZ':
                if total_matrizes:
                    valor_realizado = (Decimal(nascimentos_realizados) / Decimal(total_matrizes)) * Decimal('100')
            elif codigo == 'TAXA_NASCIMENTO':
                if total_matrizes:
                    valor_realizado = (Decimal(nascimentos_realizados) / Decimal(total_matrizes)) * Decimal('100')
            elif codigo == 'ARROBAS_VENDIDAS':
                valor_realizado = arrobas_vendidas
            elif codigo == 'CUSTO_ARROBA':
                if arrobas_vendidas:
                    valor_realizado = financeiro.realizado_custos / arrobas_vendidas
            elif codigo == 'MARGEM_OPERACIONAL':
                valor_realizado = financeiro.realizado_resultado
            elif codigo == 'LOTACAO_UA':
                valor_realizado = inventario.get('ua_por_hectare', DECIMAL_ZERO)
            elif codigo == 'ANIMAIS_POR_HECTARE':
                valor_realizado = inventario.get('animais_por_hectare', DECIMAL_ZERO)
            elif codigo == 'RECEITA_POR_ANIMAL':
                if total_animais:
                    valor_realizado = financeiro.realizado_receitas / Decimal(total_animais)
            elif codigo == 'LUCRO_POR_HECTARE':
                if area_total:
                    valor_realizado = financeiro.realizado_resultado / area_total
            elif codigo == 'RESULTADO_OPERACIONAL':
                valor_realizado = movimentos_realizados['totais']['VENDA']['valor'] - movimentos_realizados['totais']['COMPRA']['valor']

            if valor_realizado is not None:
                variacao = valor_realizado - valor_meta
                atingiu = False
                if indicador.direcao_meta == 'MAIOR':
                    atingiu = valor_realizado >= valor_meta
                elif indicador.direcao_meta == 'MENOR':
                    atingiu = valor_realizado <= valor_meta
                else:  # ALVO
                    atingiu = abs(variacao) <= Decimal('0.01')

                progresso_percentual = None
                if valor_meta and indicador.direcao_meta != 'ALVO':
                    progresso_percentual = (valor_realizado / valor_meta) * Decimal('100')

                resultados[indicador.id] = {
                    'valor_realizado': valor_realizado,
                    'variacao': variacao,
                    'atingiu_meta': atingiu,
                    'progresso_percentual': progresso_percentual,
                }
            else:
                resultados[indicador.id] = {
                    'valor_realizado': None,
                    'variacao': None,
                    'atingiu_meta': False,
                    'progresso_percentual': None,
                }

        return resultados

    # --------------------------------------------------------------- Utilidades
    def obter_meses_ordenados(self) -> List[Tuple[str, Dict[str, Dict[str, Decimal]]]]:
        """Retorna a lista de meses consolidados (planejado + realizado) ordenados."""
        self.movimentacoes_planejadas()
        self.movimentacoes_realizadas()

        def ordenar(chave: str) -> Tuple[int, int]:
            ano_str, mes_str = chave.split('-')
            return (int(ano_str), int(mes_str))

        itens = sorted(self._movimentos_mensais.items(), key=lambda item: ordenar(item[0]))
        return itens






