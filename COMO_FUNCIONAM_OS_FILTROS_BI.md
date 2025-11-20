# 🔍 Como Funcionam os Filtros BI no Dashboard

## 📊 **Sistema de Filtros Estilo Power BI**

O dashboard agora possui um sistema de filtros globais que funciona como um verdadeiro Business Intelligence (BI), onde **cada módulo reage aos filtros selecionados**.

---

## 🎯 **Tipos de Filtros**

### 1. **Filtro de Período**
- **O que faz:** Define o intervalo de datas para análise
- **Onde aplica:** Em TODOS os módulos que possuem dados com data
- **Opções:**
  - Últimos 7 dias
  - Últimos 15 dias
  - Últimos 30 dias (padrão)
  - Últimos 60 dias
  - Últimos 90 dias

### 2. **Filtro de Módulo**
- **O que faz:** Foca a análise em um módulo específico
- **Onde aplica:** Mostra apenas dados do módulo selecionado
- **Opções:**
  - Todos os módulos (padrão)
  - Pecuária
  - Rastreabilidade
  - Reprodução
  - Financeiro
  - Compras
  - Nutrição
  - Operações

---

## 🔄 **Como Cada Módulo Reage aos Filtros**

### **📈 FINANCEIRO**
- **Filtro de Período:** Filtra lançamentos por `data_competencia`
- **Filtro de Módulo:** Mostra apenas dados financeiros quando selecionado
- **O que é atualizado:**
  - Receitas do período
  - Despesas do período
  - Saldo do período
  - Gráfico de fluxo financeiro (dividido em intervalos)
  - Tendências comparadas com período anterior

### **🐄 PECUÁRIA**
- **Filtro de Período:** Filtra movimentações e nascimentos por data
- **Filtro de Módulo:** Mostra apenas dados pecuários quando selecionado
- **O que é atualizado:**
  - Movimentações recentes
  - Nascimentos no período
  - IATFs no período
  - Timeline de atividades

### **🌾 NUTRIÇÃO**
- **Filtro de Período:** Filtra distribuições por `data`
- **Filtro de Módulo:** Mostra apenas dados de nutrição quando selecionado
- **O que é atualizado:**
  - Distribuições no período
  - Valor distribuído
  - Consumo de suplementação

### **⚙️ OPERAÇÕES**
- **Filtro de Período:** Filtra consumos e manutenções por `data`
- **Filtro de Módulo:** Mostra apenas dados operacionais quando selecionado
- **O que é atualizado:**
  - Consumo de combustível no período
  - Valor do consumo
  - Manutenções no período
  - Custos operacionais

### **🛒 COMPRAS**
- **Filtro de Período:** Filtra requisições e ordens por `data_criacao` (se disponível)
- **Filtro de Módulo:** Mostra apenas dados de compras quando selecionado
- **O que é atualizado:**
  - Requisições pendentes no período
  - Ordens pendentes no período
  - Valor total das ordens

---

## 📊 **Gráficos e Visualizações**

### **Gráfico Financeiro (Linha)**
- **Reage ao filtro de período:** Divide o período selecionado em intervalos (até 6)
- **Exemplo:** Se selecionar 30 dias, divide em ~5 intervalos de 6 dias cada
- **Eixo X:** Datas do período selecionado
- **Eixo Y:** Valores em R$

### **Gráfico de Inventário (Rosca)**
- **Não reage ao filtro de período:** Mostra inventário atual (snapshot)
- **Reage ao filtro de módulo:** Se filtrar por Pecuária, mostra apenas categorias de animais

---

## 🎨 **Indicadores Visuais**

### **Badge de Filtro Ativo**
- Quando um módulo está filtrado, aparece um badge azul: **"Filtrado por: [MÓDULO]"**

### **Período Selecionado**
- Mostra as datas exatas do período: **"DD/MM/YYYY até DD/MM/YYYY"**

### **Tendências**
- As tendências comparam o período selecionado com o período anterior equivalente
- **Exemplo:** Se selecionar últimos 30 dias, compara com os 30 dias anteriores

---

## 🔧 **Como Usar**

1. **Selecionar Período:**
   - Escolha o período desejado no dropdown "Período de Análise"
   - Todos os dados são recalculados automaticamente

2. **Filtrar por Módulo:**
   - Escolha um módulo específico no dropdown "Módulo"
   - Apenas dados desse módulo são exibidos
   - Outros módulos mostram valores zerados ou ocultos

3. **Limpar Filtros:**
   - Clique em "Limpar" para voltar ao padrão (30 dias, todos os módulos)

4. **Ver Período Selecionado:**
   - O período exato é mostrado abaixo dos filtros

---

## 💡 **Exemplos Práticos**

### **Exemplo 1: Análise Financeira do Último Mês**
1. Selecionar "Últimos 30 dias"
2. Selecionar "Financeiro" no módulo
3. **Resultado:** Ver apenas receitas, despesas e gráficos financeiros dos últimos 30 dias

### **Exemplo 2: Operações da Última Semana**
1. Selecionar "Últimos 7 dias"
2. Selecionar "Operações" no módulo
3. **Resultado:** Ver apenas consumo de combustível, manutenções e custos da última semana

### **Exemplo 3: Visão Geral Trimestral**
1. Selecionar "Últimos 90 dias"
2. Deixar "Todos os módulos"
3. **Resultado:** Ver todos os dados consolidados do último trimestre

---

## ⚡ **Performance**

- Os filtros são aplicados no **backend (Python/Django)**
- As queries são otimizadas para usar índices de data
- Os gráficos são recalculados dinamicamente
- A página recarrega para aplicar os filtros (futuro: AJAX para atualização sem reload)

---

## 🚀 **Melhorias Futuras**

- [ ] Atualização via AJAX (sem recarregar página)
- [ ] Filtros de data customizados (calendário)
- [ ] Filtros por categoria/status
- [ ] Salvar filtros favoritos
- [ ] Exportar dados filtrados

---

**Data:** 2025-01-17
**Versão:** 1.0







