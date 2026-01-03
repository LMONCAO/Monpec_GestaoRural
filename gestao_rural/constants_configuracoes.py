# -*- coding: utf-8 -*-
"""
Constantes e Configurações para Sistema de Configurações por Módulo
"""

# Mapeamento de nomes de modelos para seus caminhos completos
MODELO_MAP = {
    'CategoriaFinanceira': 'gestao_rural.models_financeiro.CategoriaFinanceira',
    'CentroCusto': 'gestao_rural.models_financeiro.CentroCusto',
    'PlanoConta': 'gestao_rural.models_financeiro.PlanoConta',
    'ContaFinanceira': 'gestao_rural.models_financeiro.ContaFinanceira',
    'Cocho': 'gestao_rural.models_controles_operacionais.Cocho',
    'TipoDistribuicao': 'gestao_rural.models_controles_operacionais.TipoDistribuicao',
    'FornecedorCompras': 'gestao_rural.models_compras.FornecedorCompras',
    'Insumo': 'gestao_rural.models_compras.Insumo',
    'CategoriaInsumo': 'gestao_rural.models_compras.CategoriaInsumo',
    'SetorCompra': 'gestao_rural.models_compras.SetorCompra',
    'CategoriaProduto': 'gestao_rural.models_compras.CategoriaProduto',
    'Cliente': 'gestao_rural.models_cadastros.Cliente',
    'Frigorifico': 'gestao_rural.models_cadastros.Frigorifico',
    'ParametroVendaCategoria': 'gestao_rural.models.VendaPorCategoria',
    'NumeroSequencialNFE': 'gestao_rural.models_compras_financeiro.NumeroSequencialNFE',
    'CategoriaAnimal': 'gestao_rural.models.CategoriaAnimal',
    'Equipamento': 'gestao_rural.models_operacional.Equipamento',
}

# Módulos permitidos para importação dinâmica (segurança)
ALLOWED_MODEL_MODULES = [
    'gestao_rural.models_financeiro',
    'gestao_rural.models_compras',
    'gestao_rural.models_controles_operacionais',
    'gestao_rural.models_cadastros',
    'gestao_rural.models',
    'gestao_rural.models_compras_financeiro',
    'gestao_rural.models_operacional',
]

# Configurações de paginação
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 1000
DEFAULT_PAGE = 1

# Configurações de cache
CACHE_TIMEOUT_TOTAL = 300  # 5 minutos para contagens
CACHE_PREFIX = 'config_modulo'








