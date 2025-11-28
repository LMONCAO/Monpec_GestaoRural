# 📋 FLUXO DE GERAÇÃO DE PROJEÇÃO - RESUMO EXECUTIVO

## 🎯 VISÃO GERAL
Sistema gera automaticamente projeção do rebanho ao longo de vários anos, simulando todas as movimentações baseado em parâmetros configurados e perfil inteligente da fazenda.

---

## 🔄 FLUXO PRINCIPAL (6 ETAPAS)

### 1️⃣ **INICIALIZAÇÃO**
- Usuário acessa página de projeção
- Sistema valida: inventário inicial ✅ e parâmetros ✅
- Usuário informa número de anos (1-20)

### 2️⃣ **IDENTIFICAÇÃO DO PERFIL**
- Sistema IA analisa inventário e parâmetros
- Identifica perfil: **Cria**, **Recria**, **Engorda** ou **Ciclo Completo**
- Gera estratégias automáticas de vendas/compras

### 3️⃣ **LOOP POR ANOS**
Para cada ano da projeção:
- Calcula saldo inicial (inventário ou saldo final do ano anterior)
- Processa 12 meses sequencialmente

### 4️⃣ **PROCESSAMENTO MENSAL** (Ordem Crítica!)
Para cada mês (1-12), na seguinte ordem:

1. **NASCIMENTOS** (julho-dezembro)
   - Matrizes = Vacas + 80% das Primíparas
   - 70% das matrizes pariram (distribuído em 6 meses)
   - 50% bezerros, 50% bezerras

2. **DESCARTE/VENDAS** (julho)
   - 20% das matrizes descartadas
   - 20% das primíparas vendidas (não prenhas)

3. **MORTES**
   - Taxa mensal = Taxa anual / 12

4. **EVOLUÇÃO DE IDADE** ⚠️ **ANTES DAS VENDAS!**
   - Animais evoluem de categoria após 12 meses
   - Ex: Bezerro → Garrote, Novilha → Primípara

5. **VENDAS**
   - Protege bezerros recém-nascidos (não vende no mesmo ano)
   - Exclui descarte e garrotes (são transferências)

6. **COMPRAS**
   - Baseado no perfil da fazenda

7. **TRANSFERÊNCIAS** (janeiro)
   - Apenas estoque inicial do ano
   - Vacas de descarte e garrotes

8. **SALDO FINAL**
   - Atualizado para próximo mês

### 5️⃣ **AGREGAÇÃO E CÁLCULOS**
- Agrupa movimentações por ano
- Calcula totais por categoria
- Calcula receitas (vendas) e custos (compras/mortes)
- Gera gráfico de evolução

### 6️⃣ **APRESENTAÇÃO**
- Gráfico de linha (saldo inicial vs final)
- Tabelas anuais paginadas com:
  - Cabeçalho: Proprietário - Propriedade - IE
  - Colunas: Saldo Inicial, Nascimentos, Compras, Vendas, Mortes, Transferências, Evolução, Saldo Final, Valor Total
  - Resumo financeiro: Receitas, Custos, Lucro

---

## 🔑 REGRAS DE NEGÓCIO CRÍTICAS

| Regra | Detalhes |
|-------|----------|
| **Nascimentos** | Apenas julho-dezembro. 70% das matrizes (Vacas + 80% Primíparas) |
| **Primíparas** | 80% em reprodução, 20% vendidas (não prenhas) |
| **Evolução** | **SEMPRE ANTES** das vendas (ordem crítica!) |
| **Vendas** | Não vende bezerros recém-nascidos no mesmo ano |
| **Transferências** | Apenas janeiro, apenas estoque inicial |
| **Saldos** | Saldo final do ano N = Saldo inicial do ano N+1 |

---

## 📊 EXEMPLO PRÁTICO

**Cenário**: 4.800 Vacas + 1.173 Primíparas, Taxa 70%

**Ano 2025 - Janeiro**:
- Transferências: 512 vacas descarte + 1.180 garrotes (estoque inicial)

**Ano 2025 - Julho** (Início da Estação):
- Matrizes: 4.800 + (1.173 × 0.80) = **5.738 matrizes**
- Descarte: 20% das 4.800 vacas = **960 vacas**
- Venda Primíparas: 20% de 1.173 = **235 primíparas**
- Nascimentos: 5.738 × 70% / 6 = **~670 nascimentos** (julho)

**Ano 2025 - Agosto a Dezembro**:
- Nascimentos: ~670 por mês
- Total na estação: **~4.017 nascimentos**

**Ano 2025 - Durante o Ano**:
- Evolução: Bezerros → Garrotes, Novilhas → Primíparas
- Vendas: Conforme políticas (exceto bezerros recém-nascidos)
- Mortes: Conforme taxas configuradas

**Ano 2026 - Janeiro**:
- Saldo Inicial = Saldo Final de 2025
- Transferências: Novamente estoque inicial de 2026

---

## 🎯 RESULTADO FINAL

O sistema gera uma projeção completa que:
- ✅ Simula o ciclo completo do rebanho
- ✅ Respeita estações de nascimento
- ✅ Considera evolução de idade
- ✅ Aplica políticas de vendas
- ✅ Calcula transferências entre fazendas
- ✅ Protege animais recém-nascidos
- ✅ Apresenta dados de forma clara e paginada
- ✅ Inclui informações do proprietário e propriedade
- ✅ Calcula receitas e custos corretamente

---

## 🔧 ARQUIVOS PRINCIPAIS

1. **View**: `gestao_rural/views.py` - `pecuaria_projecao()`
2. **Geração**: `gestao_rural/ia_movimentacoes_automaticas.py` - `SistemaMovimentacoesAutomaticas`
3. **Identificação**: `gestao_rural/ia_identificacao_fazendas.py` - `SistemaIdentificacaoFazendas`
4. **Template**: `templates/gestao_rural/pecuaria_projecao.html`
5. **Agregação**: `gestao_rural/views.py` - `gerar_resumo_projecao_por_ano()`

---

## ⚡ ORDEM DE PROCESSAMENTO (CRÍTICO!)

```
MÊS → Nascimentos → Mortes → Evolução → Vendas → Compras → Transferências → Saldo Final
```

**⚠️ IMPORTANTE**: A evolução DEVE acontecer ANTES das vendas, senão os animais não estarão nas categorias corretas para venda!




