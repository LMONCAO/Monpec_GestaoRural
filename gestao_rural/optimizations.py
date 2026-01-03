"""
Módulo de otimizações de queries do banco de dados
Contém funções helper para otimizar queries comuns
"""
from django.db.models import Prefetch, Q
from typing import Optional


def otimizar_query_produtores(queryset):
    """
    Otimiza query de produtores com select_related e prefetch_related
    """
    return queryset.select_related(
        'usuario_responsavel'
    ).prefetch_related(
        'propriedade_set'
    ).only(
        'id', 'nome', 'cpf_cnpj', 'email', 'telefone', 
        'usuario_responsavel_id', 'data_cadastro'
    )


def otimizar_query_propriedades(queryset):
    """
    Otimiza query de propriedades com select_related
    """
    return queryset.select_related(
        'produtor',
        'produtor__usuario_responsavel'
    ).only(
        'id', 'nome_propriedade', 'produtor_id', 'municipio', 
        'uf', 'area_total_ha', 'tipo_operacao', 'data_cadastro'
    )


def otimizar_query_inventario(queryset):
    """
    Otimiza query de inventário com select_related
    """
    return queryset.select_related(
        'propriedade',
        'propriedade__produtor',
        'categoria'
    )


def otimizar_query_movimentacoes(queryset):
    """
    Otimiza query de movimentações projetadas
    """
    return queryset.select_related(
        'propriedade',
        'categoria',
        'planejamento'
    ).prefetch_related(
        'vendas_geradas'
    )


def otimizar_query_lancamentos_financeiros(queryset):
    """
    Otimiza query de lançamentos financeiros
    """
    return queryset.select_related(
        'propriedade',
        'propriedade__produtor',
        'categoria',
        'centro_custo',
        'conta_origem',
        'conta_destino'
    )


def otimizar_query_animais(queryset):
    """
    Otimiza query de animais individuais
    """
    return queryset.select_related(
        'propriedade',
        'propriedade__produtor',
        'categoria',
        'lote_atual'
    ).prefetch_related(
        'pesagens',
        'movimentacoes'
    )


def otimizar_query_iatf(queryset):
    """
    Otimiza query de IATFs
    """
    return queryset.select_related(
        'animal_individual',
        'animal_individual__categoria',
        'animal_individual__lote_atual',
        'touro_semen',
        'inseminador',
        'lote_iatf',
        'lote_iatf__protocolo',
        'protocolo',
        'propriedade'
    )

