# 🇧🇷 GUIA DE FORMATAÇÃO BRASILEIRA - SISTEMA MONPEC

## 📊 FORMATAÇÃO DE NÚMEROS E MOEDAS

---

## 🎯 TEMPLATE TAGS DISPONÍVEIS

### **1. Formatação de Moeda: `moeda_br`**

**Uso:**
```django
{% load formatacao_br %}

{{ valor|moeda_br }}
```

**Exemplos:**
| Valor | Resultado |
|-------|-----------|
| 1000 | R$ 1.000,00 |
| 10000 | R$ 10.000,00 |
| 100000 | R$ 100.000,00 |
| 1234.56 | R$ 1.234,56 |
| 0.50 | R$ 0,50 |

---

### **2. Formatação de Número: `numero_br`**

**Uso:**
```django
{% load formatacao_br %}

{{ valor|numero_br }}          {# Sem decimais #}
{{ valor|numero_br:2 }}        {# Com 2 decimais #}
```

**Exemplos:**

**Sem decimais (padrão):**
| Valor | Resultado |
|-------|-----------|
| 1000 | 1.000 |
| 10000 | 10.000 |
| 100000 | 100.000 |
| 1500000 | 1.500.000 |

**Com decimais:**
| Valor | Código | Resultado |
|-------|--------|-----------|
| 1000.5 | `{{ valor\|numero_br:1 }}` | 1.000,5 |
| 1152.38 | `{{ valor\|numero_br:2 }}` | 1.152,38 |
| 50.456 | `{{ valor\|numero_br:3 }}` | 50,456 |

---

### **3. Formatação de Percentual: `percentual_br`**

**Uso:**
```django
{% load formatacao_br %}

{{ valor|percentual_br }}       {# 1 decimal (padrão) #}
{{ valor|percentual_br:2 }}     {# 2 decimais #}
```

**Exemplos:**
| Valor | Código | Resultado |
|-------|--------|-----------|
| 23.5 | `{{ valor\|percentual_br }}` | 23,5% |
| 15.75 | `{{ valor\|percentual_br:2 }}` | 15,75% |
| 8 | `{{ valor\|percentual_br }}` | 8,0% |

---

### **4. Número Abreviado: `numero_abreviado`**

**Uso:**
```django
{% load formatacao_br %}

{{ valor|numero_abreviado }}
```

**Exemplos:**
| Valor | Resultado |
|-------|-----------|
| 1500 | 1,5k |
| 15000 | 15,0k |
| 1500000 | 1,5M |
| 1500000000 | 1,5B |

---

### **5. Moeda com Classe CSS: `moeda_com_classe`**

**Uso:**
```django
{% load formatacao_br %}

{% moeda_com_classe valor %}
```

**Resultado:**
- Valor positivo: `<span class="text-success"><i class="fas fa-arrow-up"></i> R$ 1.000,00</span>`
- Valor negativo: `<span class="text-danger"><i class="fas fa-arrow-down"></i> R$ -500,00</span>`
- Valor zero: `<span class="text-muted">R$ 0,00</span>`

---

### **6. Variação Percentual: `variacao_percentual`**

**Uso:**
```django
{% load formatacao_br %}

{% variacao_percentual valor_atual valor_anterior %}
```

**Exemplos:**
```django
{% variacao_percentual 1500 1200 %}
{# Resultado: <span class="text-success"><i class="fas fa-arrow-up"></i> +25,0%</span> #}

{% variacao_percentual 1000 1500 %}
{# Resultado: <span class="text-danger"><i class="fas fa-arrow-down"></i> 33,3%</span> #}
```

---

## 📝 EXEMPLOS DE USO EM TEMPLATES

### **Exemplo 1: Inventário**

```django
{% load formatacao_br %}

<h3>Total de Animais: {{ total_animais|numero_br }}</h3>
{# Resultado: Total de Animais: 1.430 #}

<h3>Valor Total: {{ valor_total|moeda_br }}</h3>
{# Resultado: Valor Total: R$ 125.000,00 #}

<p>Crescimento: {{ crescimento|percentual_br:2 }}</p>
{# Resultado: Crescimento: 12,35% #}
```

---

### **Exemplo 2: Tabela de Projeções**

```django
{% load formatacao_br %}

<table class="table table-monpec">
    <thead>
        <tr>
            <th>Ano</th>
            <th>Animais</th>
            <th>Receita</th>
            <th>Lucro</th>
            <th>Margem</th>
        </tr>
    </thead>
    <tbody>
        {% for projecao in projecoes %}
        <tr>
            <td>{{ projecao.ano }}</td>
            <td>{{ projecao.total_animais|numero_br }}</td>
            <td>{{ projecao.receita|moeda_br }}</td>
            <td>{{ projecao.lucro|moeda_br }}</td>
            <td>{{ projecao.margem|percentual_br:1 }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

**Resultado:**
```
Ano | Animais | Receita          | Lucro          | Margem
2026| 1.545   | R$ 1.200.000,00  | R$ 290.400,00  | 24,2%
2027| 1.669   | R$ 1.380.000,00  | R$ 338.100,00  | 24,5%
```

---

### **Exemplo 3: Cards de KPI**

```django
{% load formatacao_br %}

<div class="kpi-card">
    <div class="kpi-label">Receita Mensal</div>
    <div class="kpi-value">{{ receita_mensal|moeda_br }}</div>
    <div class="kpi-trend">
        {% variacao_percentual receita_mensal receita_mes_anterior %}
    </div>
</div>
```

**Resultado:**
```html
<div class="kpi-card">
    <div class="kpi-label">Receita Mensal</div>
    <div class="kpi-value">R$ 133.000,00</div>
    <div class="kpi-trend">
        <span class="text-success"><i class="fas fa-arrow-up"></i> +12,5%</span>
    </div>
</div>
```

---

### **Exemplo 4: Resumo Financeiro**

```django
{% load formatacao_br %}

<div class="resumo-financeiro">
    <h4>Resumo do Mês</h4>
    <ul>
        <li>Total de Vendas: {{ total_vendas|numero_br }} animais</li>
        <li>Receita: {{ receita|moeda_br }}</li>
        <li>Despesas: {{ despesas|moeda_br }}</li>
        <li>Saldo: {% moeda_com_classe saldo %}</li>
        <li>Margem: {{ margem|percentual_br:1 }}</li>
    </ul>
</div>
```

**Resultado:**
```
Resumo do Mês
• Total de Vendas: 320 animais
• Receita: R$ 133.000,00
• Despesas: R$ 100.000,00
• Saldo: ↑ R$ 33.000,00 (verde)
• Margem: 24,8%
```

---

## 🎨 IDENTIDADE VISUAL EM TODOS OS TEMPLATES

### **Como Aplicar:**

**1. Trocar `extends`:**
```django
{# ANTES #}
{% extends "base.html" %}

{# DEPOIS #}
{% extends "base_identidade_visual.html" %}
```

**2. Usar classes Monpec:**
```django
{# Cards #}
<div class="card card-monpec">
    <div class="card-monpec-header">
        <h5>Título</h5>
    </div>
    <div class="card-body">
        Conteúdo
    </div>
</div>

{# Botões #}
<button class="btn btn-monpec btn-monpec-primary">Salvar</button>
<button class="btn btn-monpec btn-monpec-accent">Destacar</button>
<button class="btn btn-monpec btn-monpec-outline">Cancelar</button>

{# Tabelas #}
<table class="table table-monpec">
    <thead>
        <tr><th>Coluna</th></tr>
    </thead>
    <tbody>
        <tr><td>Dados</td></tr>
    </tbody>
</table>

{# Badges #}
<span class="badge badge-monpec badge-monpec-primary">Tag</span>

{# Alerts #}
<div class="alert alert-monpec alert-monpec-success">
    Mensagem de sucesso
</div>
```

---

## 📋 CHECKLIST DE MIGRAÇÃO

Para cada template do sistema:

- [ ] Adicionar `{% load formatacao_br %}` no topo
- [ ] Trocar `extends "base.html"` por `extends "base_identidade_visual.html"`
- [ ] Substituir `.card` por `.card-monpec`
- [ ] Substituir `.btn-primary` por `.btn-monpec-primary`
- [ ] Substituir `.table` por `.table-monpec`
- [ ] Formatar valores monetários com `|moeda_br`
- [ ] Formatar números com `|numero_br`
- [ ] Formatar percentuais com `|percentual_br`
- [ ] Testar responsividade mobile

---

## 🎨 CORES PADRÃO DO SISTEMA

### **Uso nas Classes:**

```css
/* Textos */
.text-azul-marinho { color: #1e3a5f; }
.text-marrom-terra { color: #8b6f47; }

/* Backgrounds */
.bg-azul-marinho { background: #1e3a5f; }
.bg-marrom-terra { background: #8b6f47; }
.bg-cinza-claro { background: #f5f7fa; }

/* Gradientes */
.gradient-primary { background: linear-gradient(135deg, #1e3a5f 0%, #2d5080 100%); }
.gradient-accent { background: linear-gradient(135deg, #8b6f47 0%, #a88b61 100%); }
.gradient-mixed { background: linear-gradient(135deg, #1e3a5f 0%, #8b6f47 100%); }
```

---

## 📊 EXEMPLO COMPLETO DE PÁGINA

```django
{% extends "base_identidade_visual.html" %}
{% load static %}
{% load formatacao_br %}

{% block title %}Relatório Financeiro - Monpec{% endblock %}

{% block content %}
<div class="container py-4">
    <!-- Card Principal -->
    <div class="card card-monpec">
        <div class="card-monpec-header">
            <h3><i class="fas fa-chart-line"></i> Relatório Financeiro</h3>
        </div>
        <div class="card-body">
            <!-- KPIs -->
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="text-center p-3 bg-cinza-claro rounded">
                        <small class="text-muted">Total de Animais</small>
                        <h4 class="text-azul-marinho mt-2">
                            {{ total_animais|numero_br }}
                        </h4>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center p-3 bg-cinza-claro rounded">
                        <small class="text-muted">Receita Mensal</small>
                        <h4 class="text-success mt-2">
                            {{ receita|moeda_br }}
                        </h4>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center p-3 bg-cinza-claro rounded">
                        <small class="text-muted">Margem de Lucro</small>
                        <h4 class="text-marrom-terra mt-2">
                            {{ margem|percentual_br:1 }}
                        </h4>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="text-center p-3 bg-cinza-claro rounded">
                        <small class="text-muted">Crescimento</small>
                        <h4 class="mt-2">
                            {% variacao_percentual receita_atual receita_anterior %}
                        </h4>
                    </div>
                </div>
            </div>
            
            <!-- Tabela -->
            <table class="table table-monpec">
                <thead>
                    <tr>
                        <th>Categoria</th>
                        <th>Quantidade</th>
                        <th>Valor Unitário</th>
                        <th>Valor Total</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in inventario %}
                    <tr>
                        <td>{{ item.categoria }}</td>
                        <td>{{ item.quantidade|numero_br }}</td>
                        <td>{{ item.valor_unitario|moeda_br }}</td>
                        <td class="fw-bold">{{ item.valor_total|moeda_br }}</td>
                    </tr>
                    {% endfor %}
                    <tr class="table-active">
                        <td colspan="3" class="fw-bold">TOTAL</td>
                        <td class="fw-bold text-azul-marinho">
                            {{ valor_total|moeda_br }}
                        </td>
                    </tr>
                </tbody>
            </table>
            
            <!-- Botões -->
            <div class="text-end mt-4">
                <button class="btn btn-monpec btn-monpec-outline me-2">
                    <i class="fas fa-times"></i> Cancelar
                </button>
                <button class="btn btn-monpec btn-monpec-primary">
                    <i class="fas fa-save"></i> Salvar
                </button>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 🔧 FORMATAÇÃO EM JAVASCRIPT

Para formatação dinâmica no frontend:

```javascript
// Funções globais (já incluídas no base_identidade_visual.html)

// Formatar moeda
formatarMoeda(1234.56)
// Resultado: "R$ 1.234,56"

// Formatar número
formatarNumero(1500, 0)
// Resultado: "1.500"

formatarNumero(1152.38, 2)
// Resultado: "1.152,38"

// Formatar percentual
formatarPercentual(23.5, 1)
// Resultado: "23,5%"
```

**Exemplo de uso:**
```html
<input type="number" id="valor" class="form-control">
<p>Formatado: <span id="valor-formatado"></span></p>

<script>
document.getElementById('valor').addEventListener('input', function(e) {
    const valorFormatado = formatarMoeda(e.target.value);
    document.getElementById('valor-formatado').textContent = valorFormatado;
});
</script>
```

---

## 🎨 GUIA RÁPIDO DE CORES

### **Quando Usar Cada Cor:**

**Azul Marinho (#1e3a5f):**
- ✅ Headers de páginas
- ✅ Navbar
- ✅ Botões principais
- ✅ Títulos importantes
- ✅ Tabelas (thead)

**Marrom Terra (#8b6f47):**
- ✅ Destaques e acentos
- ✅ Bordas de destaque
- ✅ Botões secundários
- ✅ Ícones especiais
- ✅ Totais e saldos

**Cinza Claro (#f5f7fa):**
- ✅ Background geral
- ✅ Cards secundários
- ✅ Áreas de conteúdo
- ✅ Separadores

**Verde (#2d7a4f):**
- ✅ Valores positivos
- ✅ Lucros
- ✅ Crescimento
- ✅ Confirmações

**Vermelho (#c53030):**
- ✅ Valores negativos
- ✅ Prejuízos
- ✅ Alertas críticos
- ✅ Erros

---

## 📦 ARQUIVOS NECESSÁRIOS

### **1. Template Tag:**
```
gestao_rural/templatetags/__init__.py
gestao_rural/templatetags/formatacao_br.py
```

### **2. Base Template:**
```
templates/base_identidade_visual.html
```

### **3. CSS:**
```
static/css/identidade_visual.css
```

---

## 🚀 COMO ATUALIZAR TODOS OS TEMPLATES

### **Passo 1: Criar lista de templates**
```bash
# Listar todos os templates
ls templates/*.html > lista_templates.txt
```

### **Passo 2: Para cada template:**
1. Abrir o arquivo
2. Adicionar no topo: `{% load formatacao_br %}`
3. Trocar `extends "base.html"` por `extends "base_identidade_visual.html"`
4. Encontrar todos os valores monetários e aplicar `|moeda_br`
5. Encontrar todos os números e aplicar `|numero_br`
6. Encontrar todos os percentuais e aplicar `|percentual_br`
7. Trocar classes Bootstrap por classes Monpec:
   - `.card` → `.card-monpec`
   - `.btn-primary` → `.btn-monpec-primary`
   - `.table` → `.table-monpec`
8. Salvar e testar

---

## ✅ VERIFICAÇÃO

### **Teste Manual:**

1. **Abra cada página do sistema**
2. **Verifique:**
   - [ ] Moedas estão como R$ 1.000,00
   - [ ] Números estão como 1.000
   - [ ] Decimais estão como 1.152,38
   - [ ] Percentuais estão como 23,5%
   - [ ] Cores seguem identidade (Azul Marinho + Terra)
   - [ ] Cards usam .card-monpec
   - [ ] Botões usam .btn-monpec-*
   - [ ] Tabelas usam .table-monpec

---

## 🎯 PRIORIDADE DE ATUALIZAÇÃO

### **Alta Prioridade (Atualizar Primeiro):**
1. Dashboard principal
2. Gestão Pecuária
3. Inventário
4. Projeções
5. Relatórios Financeiros

### **Média Prioridade:**
6. Propriedades
7. Movimentações
8. Projetos
9. Análises

### **Baixa Prioridade:**
10. Configurações
11. Admin
12. Páginas estáticas

---

## 📞 SUPORTE

**Dúvidas sobre formatação:**
- Consulte este guia
- Veja exemplos nos templates criados
- Teste no Django shell:

```python
from gestao_rural.templatetags.formatacao_br import moeda_br, numero_br

print(moeda_br(1234.56))      # R$ 1.234,56
print(numero_br(1000))         # 1.000
print(numero_br(1152.38, 2))  # 1.152,38
```

---

## 🎉 RESULTADO FINAL

Com essas formatações, todo o sistema terá:
- ✅ Padrão brasileiro de números
- ✅ Moedas sempre formatadas
- ✅ Identidade visual consistente
- ✅ Experiência profissional
- ✅ Fácil de ler e entender

**Sistema Monpec - 100% Brasileiro! 🇧🇷🐮**

---

*Versão: 2.0 | Data: 23/10/2025*

