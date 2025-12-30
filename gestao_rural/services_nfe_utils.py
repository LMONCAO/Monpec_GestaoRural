# -*- coding: utf-8 -*-
"""
Utilitários para NF-e - Numeração e validações
"""

from django.db import transaction
from .models_compras_financeiro import NumeroSequencialNFE, NotaFiscal


def obter_proximo_numero_nfe(propriedade, serie='1'):
    """
    Obtém o próximo número sequencial de NF-e para a propriedade e série
    
    Args:
        propriedade: Instância do modelo Propriedade
        serie: Série da NF-e (padrão: '1')
        
    Returns:
        int: Próximo número sequencial
        
    Raises:
        ValueError: Se propriedade não for fornecida
    """
    if not propriedade:
        raise ValueError('Propriedade é obrigatória para obter número sequencial')
    
    # Usar transação para garantir que não haverá duplicação
    with transaction.atomic():
        sequencial = NumeroSequencialNFE.obter_ou_criar(propriedade, serie)
        return sequencial.obter_proximo_numero()


def validar_numero_nfe_unico(propriedade, numero, serie='1', nota_fiscal_id=None):
    """
    Valida se o número de NF-e é único para a propriedade e série
    
    Args:
        propriedade: Instância do modelo Propriedade
        numero: Número da NF-e a validar
        serie: Série da NF-e
        nota_fiscal_id: ID da nota fiscal atual (para edição, excluir da verificação)
        
    Returns:
        tuple: (bool, str) - (é_valido, mensagem_erro)
    """
    if not propriedade:
        return False, 'Propriedade é obrigatória'
    
    if not numero:
        return False, 'Número da NF-e é obrigatório'
    
    # Buscar nota fiscal com mesmo número e série na mesma propriedade
    filtro = NotaFiscal.objects.filter(
        propriedade=propriedade,
        numero=str(numero),
        serie=serie,
        tipo='SAIDA'  # Apenas notas de saída (vendas)
    )
    
    # Se estiver editando, excluir a nota atual da verificação
    if nota_fiscal_id:
        filtro = filtro.exclude(id=nota_fiscal_id)
    
    if filtro.exists():
        nota_existente = filtro.first()
        return False, f'Já existe uma NF-e com número {numero} e série {serie} para esta propriedade. Nota: {nota_existente.id}'
    
    return True, ''


def obter_series_disponiveis(propriedade):
    """
    Retorna as séries disponíveis para uma propriedade
    Inclui séries já configuradas e a série padrão '1'
    
    Args:
        propriedade: Instância do modelo Propriedade
        
    Returns:
        list: Lista de strings com as séries disponíveis
    """
    if not propriedade:
        return ['1']  # Retornar apenas série padrão se não houver propriedade
    
    # Buscar séries já configuradas
    series_configuradas = NumeroSequencialNFE.objects.filter(
        propriedade=propriedade
    ).values_list('serie', flat=True).distinct()
    
    # Sempre incluir série '1' (padrão)
    series = set(series_configuradas)
    series.add('1')
    
    return sorted(series, key=lambda x: int(x) if x.isdigit() else 999)


def configurar_serie_nfe(propriedade, serie, proximo_numero=1, observacoes=''):
    """
    Configura uma série de NF-e para uma propriedade
    
    Args:
        propriedade: Instância do modelo Propriedade
        serie: Série da NF-e
        proximo_numero: Próximo número a ser usado (padrão: 1)
        observacoes: Observações sobre a série
        
    Returns:
        NumeroSequencialNFE: Instância criada ou atualizada
    """
    if not propriedade:
        raise ValueError('Propriedade é obrigatória')
    
    sequencial, created = NumeroSequencialNFE.objects.get_or_create(
        propriedade=propriedade,
        serie=serie,
        defaults={
            'proximo_numero': proximo_numero,
            'observacoes': observacoes
        }
    )
    
    if not created:
        # Se já existe, atualizar apenas o próximo número se necessário
        if sequencial.proximo_numero < proximo_numero:
            sequencial.proximo_numero = proximo_numero
            sequencial.observacoes = observacoes
            sequencial.save()
    
    return sequencial






