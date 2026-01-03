# Sistema de Configurações por Módulo

## Visão Geral

O sistema de **Configurações por Módulo** centraliza todos os cadastros necessários para o funcionamento correto de cada módulo em uma única página organizada com abas.

## Objetivo

Cada módulo do sistema (Financeiro, Nutrição, Compras, Vendas, etc.) possui cadastros específicos que precisam ser configurados antes de usar o módulo. Este sistema organiza esses cadastros de forma centralizada, evitando a criação de muitas páginas separadas.

## Como Funciona

### 1. Estrutura de Dados

Os cadastros de cada módulo são definidos no arquivo `gestao_rural/views_configuracoes.py` no dicionário `CONFIGURACOES_MODULOS`.

Cada módulo possui:
- **Nome**: Nome exibido do módulo
- **Ícone**: Ícone Bootstrap Icons
- **Cadastros**: Lista de cadastros necessários

Cada cadastro possui:
- **id**: Identificador único
- **nome**: Nome exibido
- **modelo**: Nome do modelo Django
- **url_lista**: URL para ver lista completa (opcional)
- **url_novo**: URL para criar novo registro (opcional)
- **url_editar**: URL para editar registro (opcional)
- **icone**: Ícone Bootstrap Icons
- **descricao**: Descrição do cadastro

### 2. Acesso às Configurações

Acesse as configurações de um módulo através da URL:

```
/propriedade/<propriedade_id>/configuracoes/<modulo>/
```

Exemplos:
- `/propriedade/1/configuracoes/financeiro/`
- `/propriedade/1/configuracoes/nutricao/`
- `/propriedade/1/configuracoes/compras/`
- `/propriedade/1/configuracoes/vendas/`

### 3. Interface

A página de configurações possui:
- **Sistema de Abas**: Cada cadastro tem sua própria aba
- **Contador de Registros**: Mostra quantos registros existem em cada cadastro
- **Botões de Ação**: Links para listas completas e criação de novos registros
- **Lista Dinâmica**: Carrega os registros via AJAX quando a aba é ativada

## Módulos Disponíveis

### Financeiro
- Categorias Financeiras
- Centros de Custo
- Planos de Contas
- Contas Financeiras

### Nutrição
- Tipos de Suplementação
- Cochos

### Compras
- Fornecedores
- Setores de Compra
- Categorias de Produtos

### Vendas
- Parâmetros por Categoria
- Séries de NF-e

### Pecuária
- Categorias de Animais

### Operações
- Equipamentos

## Adicionando Novos Cadastros

Para adicionar um novo cadastro a um módulo existente:

1. Abra `gestao_rural/views_configuracoes.py`
2. Localize o módulo em `CONFIGURACOES_MODULOS`
3. Adicione um novo item na lista `cadastros`:

```python
{
    'id': 'meu_cadastro',
    'nome': 'Meu Cadastro',
    'modelo': 'MeuModelo',
    'url_lista': 'minha_lista',
    'url_novo': 'meu_cadastro_novo',
    'url_editar': 'meu_cadastro_editar',
    'icone': 'bi-icon-name',
    'descricao': 'Descrição do cadastro'
}
```

4. Adicione o mapeamento do modelo em `configuracoes_modulo_ajax`:

```python
modelo_map = {
    # ... existentes
    'MeuModelo': 'gestao_rural.models_meu_modulo.MeuModelo',
}
```

## Criando um Novo Módulo

Para criar um novo módulo de configurações:

1. Adicione o módulo em `CONFIGURACOES_MODULOS`:

```python
'meu_modulo': {
    'nome': 'Meu Módulo',
    'icone': 'bi-icon',
    'cadastros': [
        # ... lista de cadastros
    ]
}
```

2. A URL estará automaticamente disponível:
   `/propriedade/<id>/configuracoes/meu_modulo/`

## Integração com Dashboards

Para adicionar um link de "Configurações" nos dashboards dos módulos:

```html
<a href="{% url 'configuracoes_modulo' propriedade.id 'financeiro' %}" 
   class="btn btn-outline-primary">
    <i class="bi bi-gear me-1"></i>
    Configurações
</a>
```

## Vantagens

1. **Organização**: Todos os cadastros de um módulo em um só lugar
2. **Facilidade**: Interface intuitiva com abas
3. **Manutenibilidade**: Fácil adicionar novos cadastros
4. **Consistência**: Mesma interface para todos os módulos
5. **Eficiência**: Menos páginas para gerenciar

## Exemplo de Uso

1. Usuário acessa o módulo Financeiro
2. Clica em "Configurações"
3. Vê todas as abas: Categorias, Centros de Custo, Planos de Contas, Contas
4. Clica na aba "Categorias"
5. Vê a lista de categorias cadastradas
6. Clica em "Novo Registro" para criar uma nova categoria
7. Repete para outros cadastros conforme necessário

## Notas Técnicas

- Os dados são carregados via AJAX para melhor performance
- O sistema suporta modelos com e sem relação com `propriedade`
- A contagem de registros é calculada automaticamente
- Os links para listas e formulários são opcionais








