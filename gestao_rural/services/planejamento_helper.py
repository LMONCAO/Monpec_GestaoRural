"""Funções auxiliares para criar e integrar planejamentos com outros módulos."""

from decimal import Decimal
from datetime import date
from django.utils import timezone
from django.db import transaction

from gestao_rural.models import (
    Propriedade,
    PlanejamentoAnual,
    CategoriaAnimal,
    InventarioRebanho,
    MovimentacaoProjetada,
)
from gestao_rural.models import (
    CenarioPlanejamento,
    AtividadePlanejada,
    MetaComercialPlanejada,
    MetaFinanceiraPlanejada,
    IndicadorPlanejado,
)


def criar_planejamento_automatico(propriedade: Propriedade, ano: int = None) -> PlanejamentoAnual:
    """
    Cria um planejamento anual automaticamente baseado no inventário e projeções existentes.
    
    Args:
        propriedade: Propriedade para criar o planejamento
        ano: Ano do planejamento (default: ano atual)
    
    Returns:
        PlanejamentoAnual criado ou existente
    
    Raises:
        ValueError: Se não houver inventário cadastrado
    """
    if ano is None:
        ano = timezone.now().year
    
    # VALIDAÇÃO: Verificar se há inventário
    inventario_existe = InventarioRebanho.objects.filter(propriedade=propriedade).exists()
    if not inventario_existe:
        raise ValueError(
            "É necessário ter um inventário cadastrado antes de criar o planejamento. "
            "Acesse a página de Inventário para cadastrar."
        )
    
    # Criar ou obter planejamento
    planejamento, criado = PlanejamentoAnual.objects.get_or_create(
        propriedade=propriedade,
        ano=ano,
        defaults={
            'descricao': f'Planejamento automático gerado para {ano}',
            'status': 'EM_ANDAMENTO',
        }
    )
    
    # Criar cenário baseline se não existir
    if not planejamento.cenarios.filter(is_baseline=True).exists():
        CenarioPlanejamento.objects.create(
            planejamento=planejamento,
            nome='Baseline / Geral',
            descricao='Cenário oficial aprovado pelo comitê.',
            is_baseline=True,
            ajuste_preco_percentual=Decimal('0.00'),
            ajuste_custo_percentual=Decimal('0.00'),
            ajuste_producao_percentual=Decimal('0.00'),
        )
    
    # Popular com dados do inventário e projeções
    _popular_planejamento_com_inventario(planejamento, propriedade)
    _popular_planejamento_com_projecoes(planejamento, propriedade, ano)
    
    return planejamento


def _popular_planejamento_com_inventario(planejamento: PlanejamentoAnual, propriedade: Propriedade):
    """Popula o planejamento com dados do inventário mais recente."""
    inventario_recente = InventarioRebanho.objects.filter(
        propriedade=propriedade
    ).order_by('-data_inventario').first()
    
    if not inventario_recente:
        return
    
    # Buscar inventário completo da mesma data
    inventario_completo = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario=inventario_recente.data_inventario
    ).select_related('categoria')
    
    # Criar metas comerciais baseadas no inventário
    for item in inventario_completo:
        categoria = item.categoria
        
        # Criar meta comercial apenas para categorias de venda
        if _categoria_eh_venda(categoria.nome):
            MetaComercialPlanejada.objects.get_or_create(
                planejamento=planejamento,
                categoria=categoria,
                defaults={
                    'quantidade_animais': item.quantidade,
                    'arrobas_totais': Decimal('0'),  # Será calculado depois
                    'preco_medio_esperado': item.valor_por_cabeca or Decimal('0'),
                    'canal_venda': 'Mercado',
                }
            )


def _popular_planejamento_com_projecoes(planejamento: PlanejamentoAnual, propriedade: Propriedade, ano: int):
    """Popula o planejamento com dados das movimentações projetadas."""
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        data_movimentacao__year=ano
    ).select_related('categoria')
    
    if not movimentacoes.exists():
        return
    
    # Agrupar movimentações por tipo e categoria
    vendas_por_categoria = {}
    compras_por_categoria = {}
    nascimentos_total = 0
    
    for mov in movimentacoes:
        categoria_nome = mov.categoria.nome if mov.categoria else 'Geral'
        
        if mov.tipo_movimentacao == 'VENDA':
            if categoria_nome not in vendas_por_categoria:
                vendas_por_categoria[categoria_nome] = {
                    'quantidade': 0,
                    'valor_total': Decimal('0'),
                    'arrobas': Decimal('0'),
                }
            vendas_por_categoria[categoria_nome]['quantidade'] += mov.quantidade
            vendas_por_categoria[categoria_nome]['valor_total'] += mov.valor_total or Decimal('0')
            vendas_por_categoria[categoria_nome]['arrobas'] += mov.arrobas or Decimal('0')
        
        elif mov.tipo_movimentacao == 'COMPRA':
            if categoria_nome not in compras_por_categoria:
                compras_por_categoria[categoria_nome] = {
                    'quantidade': 0,
                    'valor_total': Decimal('0'),
                }
            compras_por_categoria[categoria_nome]['quantidade'] += mov.quantidade
            compras_por_categoria[categoria_nome]['valor_total'] += mov.valor_total or Decimal('0')
        
        elif mov.tipo_movimentacao == 'NASCIMENTO':
            nascimentos_total += mov.quantidade
    
    # Atualizar ou criar metas comerciais
    for categoria_nome, dados in vendas_por_categoria.items():
        try:
            categoria = CategoriaAnimal.objects.get(nome=categoria_nome)
        except CategoriaAnimal.DoesNotExist:
            continue
        
        preco_medio = (
            dados['valor_total'] / dados['quantidade']
            if dados['quantidade'] > 0
            else Decimal('0')
        )
        
        MetaComercialPlanejada.objects.update_or_create(
            planejamento=planejamento,
            categoria=categoria,
            defaults={
                'quantidade_animais': dados['quantidade'],
                'arrobas_totais': dados['arrobas'],
                'preco_medio_esperado': preco_medio,
                'canal_venda': 'Mercado',
            }
        )
    
    # Criar indicadores básicos
    if not planejamento.indicadores_planejados.exists():
        IndicadorPlanejado.objects.create(
            planejamento=planejamento,
            nome='Taxa de Natalidade',
            unidade='%',
            valor_meta=Decimal('85.0'),
            prioridade=1,
        )
        
        IndicadorPlanejado.objects.create(
            planejamento=planejamento,
            nome='Taxa de Mortalidade',
            unidade='%',
            valor_meta=Decimal('3.0'),
            prioridade=1,
        )


def _categoria_eh_venda(categoria_nome: str) -> bool:
    """Verifica se a categoria é normalmente vendida."""
    categorias_venda = [
        'Boi', 'Garrote', 'Novilho', 'Touro', 'Vaca Descarte',
        'Bezerro', 'Bezerra'
    ]
    return any(cat.lower() in categoria_nome.lower() for cat in categorias_venda)


def sincronizar_planejamento_com_projecoes(planejamento: PlanejamentoAnual):
    """
    Sincroniza o planejamento com as movimentações projetadas mais recentes.
    Atualiza metas comerciais e atividades baseadas nas projeções.
    """
    propriedade = planejamento.propriedade
    ano = planejamento.ano
    
    # Limpar atividades antigas baseadas em projeções
    planejamento.atividades.filter(
        tipo_atividade__in=['VENDA_PROJETADA', 'COMPRA_PROJETADA', 'NASCIMENTO_PROJETADO']
    ).delete()
    
    # Buscar movimentações do ano
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        data_movimentacao__year=ano
    ).select_related('categoria').order_by('data_movimentacao')
    
    # Atualizar metas comerciais com dados das projeções
    _popular_planejamento_com_projecoes(planejamento, propriedade, ano)
    
    # Criar atividades baseadas nas movimentações
    for mov in movimentacoes:
        tipo_atividade = {
            'VENDA': 'VENDA_PROJETADA',
            'COMPRA': 'COMPRA_PROJETADA',
            'NASCIMENTO': 'NASCIMENTO_PROJETADO',
        }.get(mov.tipo_movimentacao)
        
        if tipo_atividade:
            AtividadePlanejada.objects.get_or_create(
                planejamento=planejamento,
                tipo_atividade=tipo_atividade,
                categoria=mov.categoria,
                data_inicio_prevista=mov.data_movimentacao,
                defaults={
                    'descricao': f'{mov.tipo_movimentacao} de {mov.quantidade} animais',
                    'custo_previsto': mov.valor_total or Decimal('0'),
                }
            )


def verificar_planejamento_desatualizado(planejamento: PlanejamentoAnual) -> dict:
    """
    Verifica se o planejamento está desatualizado comparando com projeções mais recentes.
    
    Returns:
        dict com informações sobre atualização:
        {
            'desatualizado': bool,
            'ultima_projecao': datetime ou None,
            'ultima_atualizacao': datetime,
            'dias_desatualizado': int ou None
        }
    """
    propriedade = planejamento.propriedade
    ano = planejamento.ano
    
    # Buscar última movimentação projetada do ano
    ultima_movimentacao = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade,
        data_movimentacao__year=ano
    ).order_by('-data_movimentacao').first()
    
    resultado = {
        'desatualizado': False,
        'ultima_projecao': None,
        'ultima_atualizacao': planejamento.data_atualizacao,
        'dias_desatualizado': None,
    }
    
    if ultima_movimentacao:
        resultado['ultima_projecao'] = ultima_movimentacao.data_movimentacao
        
        # Se a última projeção é mais recente que a última atualização do planejamento
        if ultima_movimentacao.data_movimentacao > planejamento.data_atualizacao.date():
            resultado['desatualizado'] = True
            delta = timezone.now().date() - ultima_movimentacao.data_movimentacao
            resultado['dias_desatualizado'] = delta.days
    
    return resultado

