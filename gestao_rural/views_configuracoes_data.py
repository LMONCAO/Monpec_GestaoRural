# -*- coding: utf-8 -*-
"""
Dados de Configuração dos Módulos
Estrutura que define quais cadastros cada módulo possui.
"""

CONFIGURACOES_MODULOS = {
    'financeiro': {
        'nome': 'Financeiro',
        'icone': 'bi-cash-stack',
        'cadastros': [
            {
                'id': 'categorias',
                'nome': 'Categorias Financeiras',
                'modelo': 'CategoriaFinanceira',
                'url_lista': 'financeiro_categorias',
                'url_novo': 'financeiro_categoria_nova',
                'url_editar': 'financeiro_categoria_editar',
                'icone': 'bi-tags',
                'descricao': 'Categorias para classificar receitas e despesas'
            },
            {
                'id': 'centros_custo',
                'nome': 'Centros de Custo',
                'modelo': 'CentroCusto',
                'url_lista': 'financeiro_centros_custo',
                'url_novo': 'financeiro_centro_custo_novo',
                'url_editar': 'financeiro_centro_custo_editar',
                'icone': 'bi-diagram-3',
                'descricao': 'Centros de custo para rateio de despesas'
            },
            {
                'id': 'planos_conta',
                'nome': 'Planos de Contas',
                'modelo': 'PlanoConta',
                'url_lista': None,
                'url_novo': 'cadastro_rapido_plano_conta',
                'url_editar': None,
                'icone': 'bi-journal-text',
                'descricao': 'Plano de contas contábil'
            },
            {
                'id': 'contas_financeiras',
                'nome': 'Contas Financeiras',
                'modelo': 'ContaFinanceira',
                'url_lista': 'financeiro_contas',
                'url_novo': 'financeiro_conta_nova',
                'url_editar': 'financeiro_conta_editar',
                'icone': 'bi-wallet2',
                'descricao': 'Contas bancárias e caixa'
            },
        ]
    },
    'nutricao': {
        'nome': 'Nutrição',
        'icone': 'bi-cup-straw',
        'cadastros': [
            {
                'id': 'tipos_distribuicao',
                'nome': 'Tipos de Distribuição',
                'modelo': 'TipoDistribuicao',
                'url_lista': None,
                'url_novo': None,
                'url_editar': None,
                'icone': 'bi-box-seam',
                'descricao': 'Tipos de distribuição (sal, ração, suplemento)'
            },
            {
                'id': 'cochos',
                'nome': 'Cochos',
                'modelo': 'Cocho',
                'url_lista': 'cochos_lista',
                'url_novo': None,
                'url_editar': None,
                'icone': 'bi-bucket',
                'descricao': 'Cadastro de cochos para controle de consumo'
            },
        ]
    },
    'compras': {
        'nome': 'Compras',
        'icone': 'bi-cart',
        'cadastros': [
            {
                'id': 'fornecedores',
                'nome': 'Fornecedores',
                'modelo': 'FornecedorCompras',
                'url_lista': 'fornecedores_lista',
                'url_novo': 'fornecedor_novo',
                'url_editar': None,
                'icone': 'bi-building',
                'descricao': 'Cadastro de fornecedores'
            },
            {
                'id': 'insumos',
                'nome': 'Insumos/Produtos',
                'modelo': 'Insumo',
                'url_lista': None,
                'url_novo': None,
                'url_editar': None,
                'icone': 'bi-box-seam',
                'descricao': 'Cadastro de insumos e produtos para compra'
            },
            {
                'id': 'categorias_insumo',
                'nome': 'Categorias de Insumos',
                'modelo': 'CategoriaInsumo',
                'url_lista': None,
                'url_novo': None,
                'url_editar': None,
                'icone': 'bi-tags-fill',
                'descricao': 'Categorias para classificar insumos'
            },
            {
                'id': 'setores',
                'nome': 'Setores de Compra',
                'modelo': 'SetorCompra',
                'url_lista': 'setores_compra_lista',
                'url_novo': 'setor_compra_novo',
                'url_editar': 'setor_compra_editar',
                'icone': 'bi-diagram-2',
                'descricao': 'Setores para organização de compras'
            },
            {
                'id': 'categorias_produto',
                'nome': 'Categorias de Produtos',
                'modelo': 'CategoriaProduto',
                'url_lista': None,
                'url_novo': 'categoria_produto_nova',
                'url_editar': None,
                'icone': 'bi-tags-fill',
                'descricao': 'Categorias para classificar produtos'
            },
        ]
    },
    'vendas': {
        'nome': 'Vendas',
        'icone': 'bi-cart-check',
        'cadastros': [
            {
                'id': 'clientes',
                'nome': 'Clientes',
                'modelo': 'Cliente',
                'url_lista': None,
                'url_novo': None,
                'url_editar': None,
                'icone': 'bi-people',
                'descricao': 'Cadastro de clientes para vendas'
            },
            {
                'id': 'frigorificos',
                'nome': 'Frigoríficos',
                'modelo': 'Frigorifico',
                'url_lista': None,
                'url_novo': None,
                'url_editar': None,
                'icone': 'bi-building',
                'descricao': 'Cadastro de frigoríficos'
            },
            {
                'id': 'parametros_categoria',
                'nome': 'Parâmetros por Categoria',
                'modelo': 'ParametroVendaCategoria',
                'url_lista': 'vendas_por_categoria_lista',
                'url_novo': 'vendas_por_categoria_novo',
                'url_editar': 'vendas_por_categoria_editar',
                'icone': 'bi-sliders',
                'descricao': 'Configurações de preço e política de vendas por categoria'
            },
            {
                'id': 'series_nfe',
                'nome': 'Séries de NF-e',
                'modelo': 'NumeroSequencialNFE',
                'url_lista': 'vendas_configurar_series_nfe',
                'url_novo': None,
                'url_editar': None,
                'icone': 'bi-receipt',
                'descricao': 'Configuração de séries para emissão de notas fiscais'
            },
        ]
    },
    'pecuaria': {
        'nome': 'Pecuária',
        'icone': 'bi-heart-pulse',
        'cadastros': [
            {
                'id': 'categorias_animais',
                'nome': 'Categorias de Animais',
                'modelo': 'CategoriaAnimal',
                'url_lista': 'categorias_lista',
                'url_novo': 'categoria_nova',
                'url_editar': 'categoria_editar',
                'icone': 'bi-collection',
                'descricao': 'Categorias do rebanho (bezerros, novilhas, matrizes, etc.)'
            },
        ]
    },
    'operacoes': {
        'nome': 'Operações',
        'icone': 'bi-gear',
        'cadastros': [
            {
                'id': 'equipamentos',
                'nome': 'Equipamentos',
                'modelo': 'Equipamento',
                'url_lista': 'equipamentos_lista',
                'url_novo': None,
                'url_editar': None,
                'icone': 'bi-tools',
                'descricao': 'Cadastro de equipamentos e máquinas'
            },
        ]
    },
}






