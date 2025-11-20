# 🏦 MÓDULO: DÍVIDAS BANCÁRIAS E PROJETOS BANCÁRIOS

**Data:** Dezembro 2025  
**Objetivo:** Módulo central que consolida TODOS os dados e gera o projeto bancário completo

---

## 🎯 **CONCEITO DO MÓDULO**

### **O QUE É:**
Módulo central que **consolida todas as informações** dos outros módulos (Pecuária, Agricultura, Bens, Financeiro) e gera o **projeto bancário completo** para análise de crédito.

### **COMO FUNCIONA:**
```
Coleta dados de TODOS os módulos
     ↓
Consolida em análise única
     ↓
Calcula indicadores bancários
     ↓
Gera projeto completo
     ↓
Exporta relatório profissional
```

---

## 📊 **FUNCIONALIDADES DO MÓDULO**

### **1. DÍVIDAS BANCÁRIAS** 💳

#### **Cadastro de Dívidas:**
- 📋 **Financiamentos bancários**
  - Valor principal
  - Taxa de juros
  - Número de parcelas
  - Valor da parcela
  - Data de início
  - Data de vencimento
  - Status (Ativo, Quitado, Atrasado)

- 💰 **Empréstimos**
  - Valor contratado
  - Taxa efetiva
  - Forma de pagamento
  - Garantias oferecidas

- 📊 **Consórcios**
  - Valor do bem
  - Data de contemplação
  - Valor das parcelas

#### **Controle de Pagamentos:**
- ✅ Histórico de pagamentos
- ⏰ Próximos vencimentos
- ⚠️ Alertas de atraso
- 📈 Evolução da dívida

#### **Cálculos Automáticos:**
- 📉 Saldo devedor atualizado
- 💵 Valor total de parcelas anuais
- 📊 Taxa de endividamento
- ⏳ Prazo médio de quitação

---

### **2. PROJETO BANCÁRIO** 📋

#### **2.1 Consolidação de Dados**

##### **Do Módulo Pecuária:**
- 🐄 Receitas projetadas de vendas
- 📊 Evolução do rebanho
- 💰 Receita bruta anual
- 📈 Crescimento projetado

##### **Do Módulo Agricultura:**
- 🌾 Receitas de safras
- 💵 Receita agrícola projetada
- 📅 Calendário de safras
- 📊 Produção estimada

##### **Do Módulo Bens e Patrimônio:**
- 🏢 Valor do patrimônio
- 📉 Depreciação anual
- 💼 Garantia real
- 📊 Evolução patrimonial

##### **Do Módulo Financeiro:**
- 💸 Custos fixos e variáveis
- 📊 DRE consolidada
- 💰 Fluxo de caixa
- 📈 Indicadores de rentabilidade

---

#### **2.2 Cálculos Bancários**

##### **A. Capacidade de Pagamento**
```python
def calcular_capacidade_pagamento():
    """
    Calcula:
    - Receita Bruta Total (Pecuária + Agricultura)
    - Custos Totais (Fixos + Variáveis)
    - Lucro Bruto
    - Dívidas Anuais
    - Capacidade de Pagamento
    - Taxa de Cobertura (Receita / Dívidas)
    """
```

**Exemplo:**
- Receita Total: R$ 500.000/ano
- Custos: R$ 300.000/ano
- Lucro Bruto: R$ 200.000/ano
- Dívidas: R$ 120.000/ano
- **Capacidade:** R$ 80.000/ano disponível
- **Cobertura:** 1,67x (167% das dívidas cobertas)

---

##### **B. Garantias e Cobertura**
```python
def calcular_garantias():
    """
    Calcula:
    - Valor do Rebanho
    - Valor das Terras
    - Patrimônio Total
    - LTV (Loan-to-Value)
    - Margem de Cobertura
    """
```

**Exemplo:**
- Valor Rebanho: R$ 800.000
- Valor Terras: R$ 1.200.000
- Patrimônio: R$ 2.000.000
- Dívida Total: R$ 1.200.000
- **LTV:** 60% (dívida representa 60% do patrimônio)
- **Cobertura:** 1,67x (patrimônio cobre 167% da dívida)

---

##### **C. Análise de Riscos**
```python
def analisar_riscos():
    """
    Analisa:
    - Concentração de receitas
    - Diversificação de atividades
    - Estabilidade financeira
    - Histórico de pagamento
    - Score de risco
    """
```

**Critérios:**
- 📊 **Concentração:** <70% de uma fonte = BOM
- 🌾 **Diversificação:** Múltiplas atividades = MELHOR
- 💰 **Estabilidade:** Margem >20% = BOM
- ✅ **Histórico:** Sem atrasos = BOM
- 🎯 **Score:** 0-100 (quanto maior melhor)

---

##### **D. Projeções Futuras**
```python
def projecao_5anos():
    """
    Projeta:
    - Evolução das receitas
    - Crescimento do rebanho
    - Evolução de safras
    - Capacidade de pagamento futura
    - Patrimônio projetado
    """
```

**Output:**
| Ano | Receita | Lucro | Dívidas | Saldo Livre |
|-----|---------|-------|---------|-------------|
| 2025 | R$ 500k | R$ 200k | R$ 120k | R$ 80k |
| 2026 | R$ 550k | R$ 240k | R$ 110k | R$ 130k |
| 2027 | R$ 600k | R$ 280k | R$ 100k | R$ 180k |
| 2028 | R$ 650k | R$ 320k | R$ 90k | R$ 230k |
| 2029 | R$ 700k | R$ 360k | R$ 80k | R$ 280k |

---

### **3. GERAÇÃO DO PROJETO BANCÁRIO** 📄

#### **Seção 1: Capa e Identificação**
- Logo do banco
- Nome do solicitante
- Valor solicitado
- Prazo e finalidade
- Data de emissão

---

#### **Seção 2: Resumo Executivo** (2 páginas)
```markdown
1. DADOS DO CRÉDITO
   - Valor: R$ XXX.XXX
   - Prazo: XX anos
   - Finalidade: [Descrição]
   - Garantia: Patrimônio rural

2. CAPACIDADE DE PAGAMENTO
   - Receita Anual: R$ XXX.XXX
   - Lucro Bruto: R$ XXX.XXX
   - Taxa de Cobertura: X,Xx
   - Saldo Livre: R$ XXX.XXX

3. GARANTIAS
   - Rebanho: R$ XXX.XXX
   - Terras: R$ XXX.XXX
   - LTV: XX%
   - Cobertura: X,Xx

4. ANÁLISE DE RISCOS
   - Score: XX/100
   - Nível: [BAIXO/MÉDIO/ALTO]
   - Recomendação: [APROVADO/CONDICIONAL/REPROVADO]
```

---

#### **Seção 3: Análise Detalhada**

##### **3.1 Histórico do Proponente**
- Nome, CPF/CNPJ
- Endereço completo
- Atividades desenvolvidas
- Tempo no ramo
- Outras dívidas

##### **3.2 Caracterização da Propriedade**
- Localização
- Área total
- Tipo de propriedade
- Infraestrutura
- Status fundiário

##### **3.3 Análise Técnica - Pecuária**
- Estrutura do rebanho
- Evolução projetada
- Parâmetros técnicos
- Receitas esperadas

##### **3.4 Análise Técnica - Agricultura**
- Culturas plantadas
- Área e produtividade
- Safras projetadas
- Receitas esperadas

##### **3.5 Análise Econômico-Financeira**
- Receitas consolidadas
- Custos e despesas
- Resultado projetado
- Indicadores financeiros

##### **3.6 Análise de Garantias**
- Patrimônio total
- Comprovação documental
- Avaliação técnica
- Cobertura

---

#### **Seção 4: Projeções e Cenários**

##### **4.1 Fluxo de Caixa 5 Anos**
```
Mês    Receita    Custo    Saldo    Saldo Acum.
Jan    R$ 50k     R$ 30k   R$ 20k   R$ 20k
Fev    R$ 45k     R$ 30k   R$ 15k   R$ 35k
Mar    R$ 60k     R$ 35k   R$ 25k   R$ 60k
...
```

##### **4.2 Cenários de Stress**
- **Otimista:** +10% receita
- **Realista:** Base
- **Pessimista:** -20% receita

---

#### **Seção 5: Recomendações e Condicionantes**

##### **Recomendações:**
- ✅ Aprovar crédito
- ⚠️ Aprovar com condições
- ❌ Reprovar

##### **Condicionantes (se aplicável):**
- Documentação pendente
- Garantias adicionais
- Redução de valor
- Prazo maior

---

## 📊 **DASHBOARD DO MÓDULO**

### **Cards de Resumo:**

```
┌──────────────────────────────────────┐
│  💳 DÍVIDAS                           │
│  Total: R$ XXX.XXX                   │
│  Taxa Endividamento: XX%             │
│  Próximo Vencimento: DD/MM/AAAA      │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  💰 CAPACIDADE DE PAGAMENTO          │
│  Receita Anual: R$ XXX.XXX           │
│  Saldo Livre: R$ XXX.XXX             │
│  Taxa Cobertura: X,Xx                │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  💼 GARANTIAS                         │
│  Patrimônio: R$ XXX.XXX              │
│  LTV: XX%                            │
│  Cobertura: X,Xx                     │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  🎯 RISCO                            │
│  Score: XX/100                       │
│  Nível: BAIXO/MÉDIO/ALTO             │
│  Recomendação: APROVAR               │
└──────────────────────────────────────┘
```

---

## 🎯 **FUNCIONALIDADES ESPECIAIS**

### **1. Simulador de Cenários**
```python
def simular_cenarios(valor_emprestimo, taxa_juros, prazo):
    """
    Simula diferentes cenários:
    - Taxa de juros variável
    - Prazo variável
    - Valor variável
    - Impacto na capacidade de pagamento
    """
```

### **2. Comparador de Propostas**
- Compara múltiplas propostas de crédito
- Mostra melhor custo-benefício
- Analisa impacto no fluxo de caixa

### **3. Alertas Inteligentes**
- ⚠️ Vencimento de parcelas
- 📉 Redução da capacidade
- 💰 Melhoria nas condições
- 📊 Oportunidades de refinanciamento

---

## 📤 **EXPORTAÇÃO DO PROJETO**

### **Formato PDF:**
- 📄 Capa profissional
- 📊 Gráficos coloridos
- 📈 Tabelas organizadas
- 📋 Anexos completos
- 🎨 Identidade visual do banco

### **Formato Excel:**
- 6 abas completas:
  1. Resumo Executivo
  2. Análise Técnica
  3. Análise Financeira
  4. Projeções
  5. Garantias
  6. Dados Originais

### **Opções de Envio:**
- 📧 Enviar por email
- 💾 Download direto
- ☁️ Salvar na nuvem
- 📱 Compartilhar link

---

## 🎯 **RESULTADO FINAL**

### **O QUE O BANCO RECEBE:**

1. ✅ **Projeto completo** profissional
2. ✅ **Todos os dados** consolidados
3. ✅ **Análise de riscos** detalhada
4. ✅ **Garantias** avaliadas
5. ✅ **Recomendação** fundamentada
6. ✅ **Condicionantes** (se houver)

### **TEMPO DE GERAÇÃO:**
- ⚡ **< 5 minutos** com todos os dados preenchidos
- 📊 **Relatório completo** pronto para análise
- 🎯 **Decisão** pode ser tomada imediatamente

---

## 🚀 **IMPLEMENTAÇÃO**

### **Arquivo: `gestao_rural/views_projetos_bancarios.py`**
- Já existe estrutura básica
- **Falta:** Completar lógica de consolidação

### **Arquivo: `gestao_rural/models_projetos.py`**
- Model `Projeto` já criado
- **Falta:** Relacionamentos com outros módulos

### **Templates:**
- ❌ Falta criar interface completa
- ❌ Falta formulários de cadastro
- ❌ Falta visualização de relatórios

---

## ✅ **CHECKLIST DE IMPLEMENTAÇÃO**

- [ ] Completar consolidação de dados
- [ ] Criar cálculos de indicadores bancários
- [ ] Implementar análise de riscos
- [ ] Desenvolver geração de PDF
- [ ] Desenvolver exportação Excel
- [ ] Criar dashboard do módulo
- [ ] Implementar simulador de cenários
- [ ] Criar sistema de alertas
- [ ] Testes de integração
- [ ] Documentação

---

**Status Atual:** 30% completo  
**Prioridade:** ALTA (módulo central do sistema)
