# 🎯 COMO O SISTEMA FUNCIONA - GUIA PRÁTICO

**Para:** Desenvolvedor  
**Objetivo:** Entender exatamente como o sistema funciona para começar a desenvolver

---

## 📋 **RESUMO EXECUTIVO**

### **O QUE O SISTEMA FAZ:**
1. Recebe dados de uma propriedade rural (rebanho, culturas, bens, custos)
2. **Junta tudo** em uma análise única
3. **Calcula** se o produtor consegue pagar um empréstimo
4. **Gera relatório** profissional para o banco

### **PARA QUEM É:**
- Projetistas que fazem projetos de crédito rural
- Bancos que analisam pedidos de empréstimo
- Produtores que precisam de crédito

---

## 🏗️ **ARQUITETURA DO SISTEMA**

### **ESTRUTURA BÁSICA:**

```
┌─────────────────────────────────────┐
│  Django Project (sistema_rural)    │
│  └─ gestao_rural (app principal)   │
└─────────────────────────────────────┘
         │
         ├─ models.py (banco de dados)
         ├─ views.py (lógica)
         ├─ urls.py (rotas)
         └─ templates/ (HTML)
```

### **MODELOS PRINCIPAIS:**
1. `ProdutorRural` - Quem tem a propriedade
2. `Propriedade` - A fazenda/propriedade
3. `InventarioRebanho` - Animais (Pecuária)
4. `CicloProducaoAgricola` - Culturas (Agricultura)
5. `BemImobilizado` - Máquinas, terras, etc.
6. `CustoFixo` / `CustoVariavel` - Gastos
7. `Financiamento` - Dívidas

---

## 💻 **COMO USUÁRIO USA O SISTEMA**

### **PASSO 1: LOGIN**
```
Usuário acessa: http://localhost:8000/login
              ↓
          Faz login
              ↓
     Vai para Dashboard
```

### **PASSO 2: CADASTRO DE PRODUTOR**
```
Dashboard → Cadastrar Produtor
              ↓
Preenche: Nome, CPF, endereço, telefone
              ↓
Salva no banco (tabela ProdutorRural)
```

### **PASSO 3: CADASTRO DE PROPRIEDADE**
```
Seleciona o produtor
              ↓
Cadastra propriedade:
- Nome da fazenda
- Endereço (município, UF)
- Área (hectares)
- Tipo: Própria ou Arrendada
              ↓
Salva no banco (tabela Propriedade)
```

### **PASSO 4: PREENCHER MÓDULOS**

#### **🐄 MÓDULO PECUÁRIA:**
```
Propriedade → Pecuária → Inventário
              ↓
Para cada categoria de animal:
- Bezerros: 50 cabeças × R$ 800 = R$ 40.000
- Vacas: 30 cabeças × R$ 3.000 = R$ 90.000
- etc.
              ↓
Sistema calcula TOTAL: R$ 350.000
              ↓
Clica em "Projeções"
              ↓
Sistema pergunta:
- Taxa de natalidade? (85%)
- Taxa de mortalidade? (5%)
- % vendas ao ano? (15%)
              ↓
Sistema gera projeção 5 anos:
- Ano 1: 450 cabeças
- Ano 2: 480 cabeças
- Ano 3: 510 cabeças
- etc.
```

#### **🌾 MÓDULO AGRICULTURA:**
```
Propriedade → Agricultura → Novo Ciclo
              ↓
Preenche:
- Cultura: Soja
- Safra: 2025/2026
- Área plantada: 100 hectares
- Produtividade: 50 sc/ha
- Custo/ha: R$ 3.000
- Preço venda: R$ 150/sc
              ↓
Sistema calcula:
- Produção: 100 ha × 50 sc/ha = 5.000 sc
- Receita: 5.000 sc × R$ 150 = R$ 750.000
- Custo: 100 ha × R$ 3.000 = R$ 300.000
- Lucro: R$ 750.000 - R$ 300.000 = R$ 450.000
```

#### **🏢 MÓDULO BENS:**
```
Propriedade → Bens e Patrimônio → Novo Bem
              ↓
Preenche:
- Tipo: Máquina
- Descrição: Trator John Deere 5075E
- Valor aquisição: R$ 350.000
- Data aquisição: 01/01/2020
- Depreciação: 10% ao ano
              ↓
Sistema calcula:
- Depreciação acumulada: R$ 175.000
- Valor atual: R$ 175.000
```

#### **💰 MÓDULO FINANCEIRO:**
```
Propriedade → Financeiro → Custos
              ↓
Cadastra custo fixo:
- Descrição: Salários
- Valor mensal: R$ 8.000
              ↓
Sistema calcula anual: R$ 96.000
```

---

## 🎯 **O MÓDULO CENTRAL: PROJETOS BANCÁRIOS**

### **O QUE ELE FAZ:**

Quando você acessa **Propriedade → Projetos Bancários**, o sistema:

#### **1. COLETA DADOS DE TODOS OS MÓDULOS:**

```python
# Python faz automaticamente:

# PEGA DA PECUÁRIA:
receitas_pecuaria = calcular_receitas_vendas_projetadas()
# Exemplo: R$ 200.000/ano

# PEGA DA AGRICULTURA:
receitas_agricultura = calcular_receitas_safras()
# Exemplo: R$ 450.000/ano

# PEGA DOS BENS:
valor_patrimonio = calcular_valor_total_bens()
# Exemplo: R$ 1.500.000

# PEGA DO FINANCEIRO:
custos_anuais = calcular_custos_totais()
# Exemplo: R$ 350.000/ano

dívidas_anuais = calcular_dividas_totais()
# Exemplo: R$ 120.000/ano
```

#### **2. CONSOLIDA TUDO:**

```python
# Soma receitas:
receita_total = receitas_pecuaria + receitas_agricultura
# R$ 200.000 + R$ 450.000 = R$ 650.000/ano

# Calcula lucro:
lucro_bruto = receita_total - custos_anuais
# R$ 650.000 - R$ 350.000 = R$ 300.000/ano

# Calcula capacidade:
capacidade_pagamento = lucro_bruto - dívidas_anuais
# R$ 300.000 - R$ 120.000 = R$ 180.000 disponível
```

#### **3. CALCULA INDICADORES:**

```python
# Taxa de Cobertura (cobertura da dívida):
cobertura = receita_total / dívidas_anuais
# R$ 650.000 / R$ 120.000 = 5,4x
# Significa: receita cobre 5,4 vezes a dívida

# Loan-to-Value (LTV):
ltv = dívidas_totais / valor_patrimonio
# R$ 400.000 / R$ 1.500.000 = 26,7%
# Significa: dívida representa 26,7% do patrimônio
```

#### **4. FAZ ANÁLISE DE RISCO:**

```python
# Calcula score de 0 a 100:
score = 0

# Cobertura alta = bom
if cobertura > 3:
    score += 30
elif cobertura > 1.5:
    score += 20
else:
    score += 10

# LTV baixo = bom
if ltv < 30:
    score += 30
elif ltv < 60:
    score += 20
else:
    score += 10

# Diversificação = bom
if tem_pecuaria_e_agricultura:
    score += 20

# Histórico bom = bom
if sem_atrasos:
    score += 20

# Exemplo final: score = 85/100
```

#### **5. GERA RECOMENDAÇÃO:**

```python
if score >= 80:
    recomendacao = "APROVAR ✅"
elif score >= 60:
    recomendacao = "APROVAR COM CONDIÇÕES ⚠️"
else:
    recomendacao = "REPROVAR ❌"
```

---

## 📊 **VISUALIZAÇÃO NO NAVEGADOR**

### **DASHBOARD DO MÓDULO PROJETOS BANCÁRIOS:**

```
┌────────────────────────────────────────────────────────────┐
│  🏦 PROJETOS BANCÁRIOS - Fazenda São João                  │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐│
│  │ 💰 CAPACIDADE   │  │ 💼 GARANTIAS    │  │ 🎯 RISCO     ││
│  │                 │  │                 │  │              ││
│  │ Receita Anual:  │  │ Patrimônio:     │  │ Score: 85/100││
│  │ R$ 650.000      │  │ R$ 1.500.000    │  │              ││
│  │                 │  │                 │  │ Nível: BAIXO ││
│  │ Saldo Livre:    │  │ LTV: 26,7%      │  │              ││
│  │ R$ 180.000      │  │ Cobertura: 3,8x │  │ ✅ APROVAR   ││
│  │                 │  │                 │  │              ││
│  │ Cobertura: 5,4x │  │                 │  │              ││
│  └─────────────────┘  └─────────────────┘  └──────────────┘│
│                                                             │
│  [📄 Gerar Relatório PDF]  [📊 Exportar Excel]             │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## 📄 **COMO O RELATÓRIO É GERADO**

### **Quando clica em "Gerar Relatório PDF":**

```python
# Sistema faz:

1. Consolida TODOS os dados (já explicado acima)

2. Gera PDF com ReportLab:
   - Página 1: CAPA
     - Logo do banco
     - "PROJETO DE CRÉDITO RURAL"
     - Nome do solicitante
     - Data
   
   - Página 2-3: RESUMO EXECUTIVO
     - Dados do crédito
     - Capacidade de pagamento
     - Garantias
     - Recomendação
   
   - Página 4-10: ANÁLISE COMPLETA
     - Dados do produtor
     - Propriedade
     - Pecuária (rebanho + projeções)
     - Agricultura (culturas + receitas)
     - Patrimônio
     - Análise financeira
   
   - Página 11-15: PROJEÇÕES E GRÁFICOS
     - Gráfico: Evolução do rebanho
     - Gráfico: Receitas x Custos
     - Tabela: Fluxo de caixa 5 anos
     - Cenários de stress

3. Retorna PDF pronto para download
```

---

## 🔧 **O QUE PRECISA SER DESENVOLVIDO**

### **FASE 1: CONSOLIDAÇÃO (CRÍTICO)**

Arquivo: `gestao_rural/consolidacao_financeira.py` (NOVO)

```python
def consolidar_dados_propriedade(propriedade):
    """
    Função principal que junta dados de todos os módulos
    """
    # Aqui você vai juntar:
    # - Pecuária
    # - Agricultura  
    # - Bens
    # - Custos
    # - Dívidas
    # E calcular todos os indicadores
```

### **FASE 2: VIEW DO PROJETO BANCÁRIO**

Arquivo: `gestao_rural/views_projetos_bancarios.py` (EXISTE, precisa completar)

```python
def dashboard_projeto_bancario(request, propriedade_id):
    """
    Tela principal onde usuário vê tudo consolidado
    """
    # Chama consolidar_dados_propriedade()
    # Passa dados para o template
    # Template mostra cards e botões
```

### **FASE 3: RELATÓRIO PDF**

Arquivo: `gestao_rural/relatorios_avancados.py` (EXISTE, incompleto)

```python
def gerar_relatorio_bancario_pdf(propriedade):
    """
    Gera o PDF completo
    """
    # Usa dados consolidados
    # Gera PDF com ReportLab
    # Retorna arquivo
```

---

## 🚀 **POR ONDE COMEÇAR**

### **PASSO 1: Entender os dados atuais**

```bash
# No terminal, acesse Django shell:
python manage.py shell

# Veja o que tem no banco:
from gestao_rural.models import *

# Liste produtores:
ProdutorRural.objects.all()

# Liste propriedades:
Propriedade.objects.all()

# Veja inventário:
InventarioRebanho.objects.all()

# Veja agricultura:
CicloProducaoAgricola.objects.all()
```

### **PASSO 2: Criar função de consolidação**

Arquivo: `gestao_rural/consolidacao_financeira.py` (CRIAR AGORA)

```python
from .models import *

def consolidar_dados_propriedade(propriedade):
    """Consolida dados de todos os módulos"""
    
    # 1. PECUÁRIA
    inventario = InventarioRebanho.objects.filter(
        propriedade=propriedade
    )
    valor_rebanho = sum(item.valor_total for item in inventario)
    
    # 2. AGRICULTURA
    ciclos = CicloProducaoAgricola.objects.filter(
        propriedade=propriedade
    )
    receita_agricola = sum(ciclo.receita_esperada_total for ciclo in ciclos)
    
    # 3. PATRIMÔNIO
    bens = BemImobilizado.objects.filter(
        propriedade=propriedade, 
        ativo=True
    )
    valor_patrimonio = sum(bem.valor_aquisicao for bem in bens)
    
    # 4. CUSTOS
    custos_fixos = CustoFixo.objects.filter(
        propriedade=propriedade, 
        ativo=True
    )
    total_custos = sum(custo.custo_anual for custo in custos_fixos)
    
    # 5. DÍVIDAS
    financiamentos = Financiamento.objects.filter(
        propriedade=propriedade, 
        ativo=True
    )
    total_dividas = sum(f.valor_parcela * 12 for f in financiamentos)
    
    # CONSOLIDA
    receita_total = valor_rebanho * 0.15 + receita_agricola
    lucro_bruto = receita_total - total_custos
    capacidade = lucro_bruto - total_dividas
    cobertura = receita_total / total_dividas if total_dividas > 0 else 0
    
    return {
        'receita_total': receita_total,
        'lucro_bruto': lucro_bruto,
        'capacidade_pagamento': capacidade,
        'cobertura': cobertura,
        'valor_patrimonio': valor_patrimonio,
        # ... mais dados
    }
```

### **PASSO 3: Criar view que usa a consolidação**

```python
# gestao_rural/views_projetos_bancarios.py

from .consolidacao_financeira import consolidar_dados_propriedade

def dashboard_projeto_bancario(request, propriedade_id):
    propriedade = Propriedade.objects.get(id=propriedade_id)
    
    # Chama consolidação
    dados = consolidar_dados_propriedade(propriedade)
    
    # Passa para template
    context = {
        'propriedade': propriedade,
        'dados': dados,
    }
    
    return render(request, 'projetos_bancarios/dashboard.html', context)
```

### **PASSO 4: Criar template HTML**

```html
<!-- templates/projetos_bancarios/dashboard.html -->

<div class="container">
    <h1>Projetos Bancários - {{ propriedade.nome_propriedade }}</h1>
    
    <!-- Cards de resumo -->
    <div class="row">
        <div class="col-md-4">
            <div class="card">
                <h3>💰 Capacidade</h3>
                <p>R$ {{ dados.capacidade_pagamento }}</p>
                <p>Cobertura: {{ dados.cobertura }}x</p>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <h3>💼 Patrimônio</h3>
                <p>R$ {{ dados.valor_patrimonio }}</p>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <h3>📊 Receitas</h3>
                <p>R$ {{ dados.receita_total }}/ano</p>
            </div>
        </div>
    </div>
    
    <!-- Botões -->
    <button onclick="exportarPDF()">Exportar PDF</button>
    <button onclick="exportarExcel()">Exportar Excel</button>
</div>
```

---

## ✅ **CHECKLIST DE DESENVOLVIMENTO**

### **SEMANA 1:**

- [ ] **Dia 1:** Entender estrutura atual do código
  - Ver models.py
  - Ver views.py
  - Ver templates
  
- [ ] **Dia 2:** Criar `consolidacao_financeira.py`
  - Função que pega dados de Pecuária
  - Função que pega dados de Agricultura
  - Função que pega dados de Bens
  - Função que calcula totalizadores

- [ ] **Dia 3:** Testar consolidação
  - Criar propriedade de teste
  - Preencher dados
  - Chamar função de consolidação
  - Verificar se calcula corretamente

- [ ] **Dia 4:** Criar view de projetos bancários
  - Completar `dashboard_projeto_bancario`
  - Passar dados para template

- [ ] **Dia 5:** Criar template HTML
  - Cards de resumo
  - Botões de exportação

---

## 🎯 **RESUMO PARA DESENVOLVER**

### **Você precisa:**

1. **Entender:** Como os dados estão salvos no banco
2. **Criar:** Função que junta todos os dados
3. **Criar:** Tela que mostra os dados consolidados
4. **Criar:** Botão que gera PDF

### **Arquivos principais:**

- `gestao_rural/models.py` - Banco de dados
- `gestao_rural/consolidacao_financeira.py` - **CRIAR** (consolida dados)
- `gestao_rural/views_projetos_bancarios.py` - **COMPLETAR** (lógica)
- `templates/projetos_bancarios/dashboard.html` - **CRIAR** (visual)

### **Fluxo de desenvolvimento:**

```
1. Criar função consolidar_dados_propriedade()
   ↓
2. Testar função (ver se calcula certo)
   ↓
3. Criar view que usa a função
   ↓
4. Criar template que mostra os dados
   ↓
5. Testar no navegador
   ↓
6. Criar botão de exportar PDF
   ↓
7. Implementar geração de PDF
```

---

## 💡 **DICA FINAL**

**Comece simples:**
1. Primeiro: Faça funcionar o básico (consolidar e mostrar)
2. Depois: Melhore os cálculos
3. Por último: Adicione PDF/Excel

**Teste cada passo:**
- Crie dados de teste
- Veja se calcula corretamente
- Ajuste até funcionar

**Use o que já existe:**
- Pecuária já funciona - pegue os dados dela
- Models já existem - use eles
- Templates já têm estilos - copie e adapte

---

**PRONTO PARA COMEÇAR?** 🚀

Comece criando o arquivo `consolidacao_financeira.py` e a função `consolidar_dados_propriedade()`. Essa é a base de tudo!
