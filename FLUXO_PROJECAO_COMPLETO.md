# 📋 FLUXO COMPLETO DE GERAÇÃO DE PROJEÇÃO PECUÁRIA

## 🎯 VISÃO GERAL
O sistema gera automaticamente uma projeção completa do rebanho ao longo de vários anos, simulando todas as movimentações (nascimentos, mortes, vendas, compras, transferências e evolução de idade) baseado em parâmetros configurados e no perfil inteligente da fazenda.

---

## 📍 ETAPA 1: INICIALIZAÇÃO E VALIDAÇÃO

### 1.1. Acesso à View (`pecuaria_projecao`)
- **Localização**: `gestao_rural/views.py` - função `pecuaria_projecao()`
- **Validações**:
  - ✅ Verifica se existe inventário inicial cadastrado
  - ✅ Verifica se existem parâmetros de projeção configurados
  - ✅ Busca o inventário mais recente da propriedade

### 1.2. Processamento do POST (Geração)
- Usuário informa número de anos para projeção (1-20 anos)
- Chama função `gerar_projecao(propriedade, anos_projecao)`

---

## 🤖 ETAPA 2: IDENTIFICAÇÃO INTELIGENTE DO PERFIL

### 2.1. Sistema de Identificação (`SistemaIdentificacaoFazendas`)
- **Localização**: `gestao_rural/ia_identificacao_fazendas.py`
- **Função**: Analisa inventário e parâmetros para identificar o perfil da fazenda
- **Perfis possíveis**:
  - 🐄 **SO_CRIA**: Apenas cria (foco em reprodução)
  - 🐄 **SO_RECRIA**: Apenas recria (desenvolvimento de jovens)
  - 🐄 **SO_ENGORDA**: Apenas engorda (terminação)
  - 🐄 **CICLO_COMPLETO**: Sistema completo (cria + recria + engorda)

### 2.2. Estratégias Geradas
- Baseado no perfil, o sistema gera estratégias automáticas de:
  - Vendas por categoria
  - Compras por categoria
  - Transferências
  - Reposição

---

## 🔄 ETAPA 3: GERAÇÃO DE MOVIMENTAÇÕES POR ANO

### 3.1. Loop Principal (Anos)
Para cada ano da projeção:
```python
for ano in range(anos_projecao):
    ano_atual = datetime.now().year + ano
```

### 3.2. Cálculo de Saldos Iniciais do Ano
- **Primeiro ano**: Usa inventário inicial cadastrado
- **Anos seguintes**: Calcula saldos baseado nas movimentações do ano anterior
- **Função**: `_calcular_saldos_iniciais_ano()`

---

## 📅 ETAPA 4: PROCESSAMENTO MENSAL (12 meses por ano)

Para cada mês (1 a 12), o sistema processa as movimentações na seguinte ordem:

### 4.1. NASCIMENTOS (Estação: Julho a Dezembro)
**Quando**: Apenas nos meses 7, 8, 9, 10, 11, 12

**Cálculo de Matrizes**:
- ✅ **Vacas em Reprodução +36 M**: 100% são matrizes
- ✅ **Primíparas 24-36 M**: 80% são matrizes (em reprodução)
- ❌ **20% das Primíparas**: Não são contadas (serão vendidas)

**Cálculo de Nascimentos**:
```
Total de Matrizes = Vacas + (Primíparas × 0.80)
Nascimentos na Estação = Matrizes × Taxa_Natalidade / 100
Nascimentos por Mês = Nascimentos_Estação / 6 meses
```

**Distribuição**:
- 50% bezerros (machos)
- 50% bezerras (fêmeas)

**Exemplo**:
- 4.800 vacas + (1.173 primíparas × 0.80) = 5.738 matrizes
- 5.738 × 70% = 4.017 nascimentos na estação
- 4.017 / 6 = ~670 nascimentos por mês

### 4.2. DESCARTE E VENDAS DE PRIMÍPARAS (Apenas em Julho)
**Quando**: Apenas no mês 7 (julho)

**Descarte de Matrizes**:
- 20% das matrizes que não pariram são descartadas (vendidas)
- Apenas "Vacas em Reprodução +36 M" são consideradas para descarte

**Venda de Primíparas Não Prenhas**:
- 20% das primíparas são vendidas (não ficaram prenhas)
- 80% das primíparas permanecem em reprodução

**Resultado**:
- 70% das matrizes: Pariram (geraram nascimentos)
- 20% das matrizes: Descarte (vendidas)
- 10% das matrizes: Ficam na fazenda para nova chance

### 4.3. MORTES
**Baseado em**:
- Taxa de mortalidade de bezerros (anual, dividida por 12)
- Taxa de mortalidade de adultos (anual, dividida por 12)

**Aplicação**:
- Mortalidade mensal = Taxa_Anual / 100 / 12
- Aplicada sobre o saldo inicial do mês

### 4.4. EVOLUÇÃO DE IDADE (PROMOÇÕES)
**⚠️ IMPORTANTE**: Acontece ANTES das vendas!

**Evoluções Automáticas**:
- Bezerro(a) 0-12 M → Novilha/Novilho 12-24 M (após 12 meses)
- Novilha 12-24 M → Primípara 24-36 M (após 12 meses)
- Primípara 24-36 M → Vaca em Reprodução +36 M (após 12 meses)
- Garrote 12-24 M → Boi 24-36 M (após 12 meses)
- Boi 24-36 M → Boi +36 M (após 12 meses)

**Tipos de Movimentação**:
- `PROMOCAO_SAIDA`: Saída da categoria origem
- `PROMOCAO_ENTRADA`: Entrada na categoria destino

### 4.5. VENDAS
**Proteções**:
- ❌ Não vende bezerros recém-nascidos no mesmo ano
- ❌ Vacas de descarte e garrotes são transferências (não vendas)
- ✅ Usa políticas de vendas configuradas pelo usuário
- ✅ Respeita percentuais de venda por categoria

**Cálculo**:
- Quantidade disponível = Saldo após evolução
- Se for bezerro recém-nascido: Subtrai nascimentos do ano
- Quantidade a vender = Disponível × Percentual_Venda / 100

### 4.6. COMPRAS
- Baseado no perfil da fazenda
- Respeita estratégias automáticas ou políticas configuradas

### 4.7. TRANSFERÊNCIAS (Apenas em Janeiro)
**Quando**: Apenas no mês 1 (janeiro) de cada ano

**Categorias**:
- ✅ Vacas de Descarte: Transferidas (não vendidas)
- ✅ Garrotes: Transferidos (não vendidos)

**Importante**:
- Usa apenas o **estoque inicial do ano** (não animais criados durante o ano)
- Transfere 100% do estoque inicial (ou conforme configuração)

### 4.8. Cálculo do Saldo Final do Mês
Após todas as movimentações:
```
Saldo Final = Saldo Inicial 
            + Nascimentos 
            + Compras 
            + Transferências Entrada 
            + Promoções Entrada
            - Vendas 
            - Mortes 
            - Transferências Saída 
            - Promoções Saída
```

**Atualização**:
- Saldo final do mês vira saldo inicial do próximo mês

---

## 📊 ETAPA 5: PROCESSAMENTO E APRESENTAÇÃO DOS DADOS

### 5.1. Agregação por Ano
**Função**: `gerar_resumo_projecao_por_ano()`
- Agrupa todas as movimentações por ano
- Calcula totais por categoria
- Calcula totais gerais (nascimentos, vendas, mortes, transferências)
- Calcula valores financeiros

### 5.2. Estrutura de Dados Gerada
```python
resumo_projecao_por_ano = {
    ano: {
        'categorias': {
            'Categoria Nome': {
                'saldo_inicial': int,
                'nascimentos': int,
                'compras': int,
                'vendas': int,
                'mortes': int,
                'transferencias_entrada': int,
                'transferencias_saida': int,
                'evolucao_categoria': str,
                'saldo_final': int,
                'valor_total': Decimal
            }
        },
        'totais': {
            'saldo_inicial_total': int,
            'nascimentos_total': int,
            'compras_total': int,
            'vendas_total': int,
            'mortes_total': int,
            'transferencias_entrada_total': int,
            'transferencias_saida_total': int,
            'saldo_final_total': int,
            'valor_total_geral': Decimal,
            'receitas_total': Decimal,
            'custos_total': Decimal,
            'lucro_total': Decimal
        }
    }
}
```

### 5.3. Evolução do Rebanho (Gráfico)
**Função**: `gerar_evolucao_detalhada_rebanho()`
- Calcula saldo inicial e final por ano
- Prepara dados para gráfico Chart.js
- Mostra evolução visual do rebanho

---

## 🎨 ETAPA 6: RENDERIZAÇÃO NO TEMPLATE

### 6.1. Template Principal
**Arquivo**: `templates/gestao_rural/pecuaria_projecao.html`

### 6.2. Elementos Exibidos

#### 6.2.1. Gráfico de Evolução
- Gráfico de linha (Chart.js)
- Mostra saldo inicial e final por ano
- Eixo X: Anos (2025, 2026, 2027...)
- Eixo Y: Quantidade de animais

#### 6.2.2. Tabelas Anuais (Paginação Visual)
Para cada ano:
- **Cabeçalho**: 
  - Nome do Proprietário - Nome da Propriedade - IE: [CPF/CNPJ]
  - "Projeção do Ano XXXX"
  - Saldo inicial (inventário ou saldo final do ano anterior)
  
- **Tabela com colunas**:
  1. **Categoria**: Nome da categoria de animal
  2. **Saldo Inicial**: Quantidade no início do ano
  3. **Nascimentos**: Quantidade nascida (apenas julho-dezembro)
  4. **Compras**: Quantidade comprada
  5. **Vendas**: Quantidade vendida
  6. **Mortes**: Quantidade que morreu
  7. **Transferências**: Entrada (+) e Saída (-) entre fazendas
  8. **Evolução**: Mudanças de categoria (promoções)
  9. **Saldo Final**: Quantidade no final do ano
  10. **Valor Total (R$)**: Valor monetário do rebanho na categoria

- **Rodapé**:
  - Totais de todas as colunas
  - Resumo financeiro (Receitas, Custos, Lucro)
  - Nota sobre próximo ano

---

## 🔑 REGRAS DE NEGÓCIO IMPORTANTES

### ✅ Nascimentos
- **Estação**: Apenas julho a dezembro
- **Matrizes**: Vacas + 80% das Primíparas
- **Taxa**: Aplicada sobre saldo inicial do ano
- **Distribuição**: 50% machos, 50% fêmeas
- **Proteção**: Bezerros recém-nascidos não são vendidos no mesmo ano

### ✅ Descarte e Vendas de Primíparas
- **Quando**: Apenas em julho
- **Descarte**: 20% das matrizes que não pariram
- **Venda Primíparas**: 20% das primíparas não prenhas
- **Resultado**: 70% pariram, 20% descarte, 10% nova chance

### ✅ Evolução de Idade
- **Ordem**: ANTES das vendas (crítico!)
- **Frequência**: Mensal (animais evoluem após 12 meses na categoria)
- **Tipos**: PROMOCAO_ENTRADA e PROMOCAO_SAIDA

### ✅ Vendas
- **Proteção**: Bezerros recém-nascidos não são vendidos
- **Exclusão**: Vacas de descarte e garrotes são transferências
- **Base**: Políticas configuradas ou estratégias automáticas

### ✅ Transferências
- **Quando**: Apenas em janeiro
- **O que**: Apenas estoque inicial do ano
- **Categorias**: Vacas de descarte e garrotes
- **Sem valor**: Apenas quantidades (não gera receita)

### ✅ Saldos entre Anos
- Saldo final do ano N = Saldo inicial do ano N+1
- Todas as movimentações são consideradas
- Saldos nunca ficam negativos

---

## 📈 EXEMPLO PRÁTICO

### Cenário: 4.800 Vacas + 1.173 Primíparas, Taxa 70%

**Ano 2025 - Janeiro**:
- Saldo Inicial: 4.800 vacas, 1.173 primíparas
- Transferências: 512 vacas descarte, 1.180 garrotes (estoque inicial)

**Ano 2025 - Julho** (Início da Estação):
- Matrizes: 4.800 + (1.173 × 0.80) = 5.738 matrizes
- Descarte: 20% das 4.800 vacas = 960 vacas
- Venda Primíparas: 20% de 1.173 = 235 primíparas
- Nascimentos: 5.738 × 70% / 6 = ~670 nascimentos (julho)

**Ano 2025 - Agosto a Dezembro**:
- Nascimentos: ~670 por mês
- Total na estação: ~4.017 nascimentos

**Ano 2025 - Durante o Ano**:
- Evolução: Bezerros → Garrotes, Novilhas → Primíparas
- Vendas: Conforme políticas (exceto bezerros recém-nascidos)
- Mortes: Conforme taxas configuradas

**Ano 2026 - Janeiro**:
- Saldo Inicial: Saldo final de 2025
- Transferências: Novamente estoque inicial de 2026

---

## 🎯 RESULTADO FINAL

O sistema gera uma projeção completa e realista que:
- ✅ Simula o ciclo completo do rebanho
- ✅ Respeita estações de nascimento
- ✅ Considera evolução de idade
- ✅ Aplica políticas de vendas
- ✅ Calcula transferências entre fazendas
- ✅ Protege animais recém-nascidos
- ✅ Apresenta dados de forma clara e paginada
- ✅ Inclui informações do proprietário e propriedade

---

## 🔧 ARQUIVOS PRINCIPAIS

1. **View**: `gestao_rural/views.py` - `pecuaria_projecao()`
2. **Geração**: `gestao_rural/ia_movimentacoes_automaticas.py` - `SistemaMovimentacoesAutomaticas`
3. **Identificação**: `gestao_rural/ia_identificacao_fazendas.py` - `SistemaIdentificacaoFazendas`
4. **Template**: `templates/gestao_rural/pecuaria_projecao.html`
5. **Agregação**: `gestao_rural/views.py` - `gerar_resumo_projecao_por_ano()`

---

## 📝 NOTAS TÉCNICAS

- Todas as movimentações são salvas como `MovimentacaoProjetada`
- Cálculos usam `Decimal` para precisão financeira
- Saldos são atualizados incrementalmente mês a mês
- Cache é usado para otimizar consultas
- Logs detalhados são gerados para debug



