# Melhorias Pendentes - Módulo Pecuária

## Data: 27 de Outubro de 2025

## 📋 Melhorias Pendentes para Implementação Futura

### 1. **Gráficos Chart.js - Visualização Interativa** ⏳

#### Objetivo
Implementar visualização interativa com gráficos Chart.js para projeções.

#### Implementação Sugerida

**Passo 1:** Adicionar Chart.js ao template
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

**Passo 2:** Criar canvas para gráficos
```html
<div class="row mb-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>Evolução do Rebanho (5 Anos)</h5>
            </div>
            <div class="card-body">
                <canvas id="rebanhoChart"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card">
            <div class="card-header">
                <h5>Receitas e Custos</h5>
            </div>
            <div class="card-body">
                <canvas id="financeiroChart"></canvas>
            </div>
        </div>
    </div>
</div>
```

**Passo 3:** JavaScript para gerar gráficos
```javascript
// Preparar dados
const dadosRebanho = {
    labels: {{ anos|safe }},
    datasets: [{
        label: 'Total de Animais',
        data: {{ total_animais|safe }},
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
    }, {
        label: 'Fêmeas',
        data: {{ femeas|safe }},
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1
    }, {
        label: 'Machos',
        data: {{ machos|safe }},
        borderColor: 'rgb(54, 162, 235)',
        tension: 0.1
    }]
};

// Criar gráfico
const ctx1 = document.getElementById('rebanhoChart').getContext('2d');
new Chart(ctx1, {
    type: 'line',
    data: dadosRebanho,
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: 'Evolução do Rebanho' }
        },
        scales: {
            y: { beginAtZero: true }
        }
    }
});

// Gráfico de receitas e custos
const dadosFinanceiro = {
    labels: {{ anos|safe }},
    datasets: [{
        label: 'Receitas',
        data: {{ receitas|safe }},
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        borderColor: 'rgb(75, 192, 192)',
    }, {
        label: 'Custos',
        data: {{ custos|safe }},
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgb(255, 99, 132)',
    }]
};

const ctx2 = document.getElementById('financeiroChart').getContext('2d');
new Chart(ctx2, {
    type: 'bar',
    data: dadosFinanceiro,
    options: {
        responsive: true,
        plugins: {
            legend: { position: 'top' },
            title: { display: true, text: 'Receitas vs Custos' }
        }
    }
});
```

#### Benefícios
- ✅ Visualização clara das tendências
- ✅ Fácil comparação de dados
- ✅ Interatividade (zoom, hover)
- ✅ Gráficos responsivos

---

### 2. **Análise de Cenários - Múltiplos Cenários** ⏳

#### Objetivo
Permitir testar diferentes cenários (otimista, realista, conservador) de projeção.

#### Implementação Sugerida

**Passo 1:** Criar view para cenários
```python
@login_required
def gerar_cenarios_projecao(request, propriedade_id):
    """Gera múltiplos cenários de projeção"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    parametros = ParametrosProjecaoRebanho.objects.get(propriedade=propriedade)
    
    cenarios = {
        'otimista': {
            'taxa_natalidade': parametros.taxa_natalidade_anual * 1.15,
            'taxa_mortalidade': parametros.taxa_mortalidade_bezerros_anual * 0.85,
            'cor': 'success',
            'descricao': 'Cenário com melhores condições (15% melhor natalidade, 15% menos mortalidade)',
        },
        'realista': {
            'taxa_natalidade': parametros.taxa_natalidade_anual,
            'taxa_mortalidade': parametros.taxa_mortalidade_bezerros_anual,
            'cor': 'primary',
            'descricao': 'Cenário baseado nos parâmetros atuais',
        },
        'conservador': {
            'taxa_natalidade': parametros.taxa_natalidade_anual * 0.85,
            'taxa_mortalidade': parametros.taxa_mortalidade_bezerros_anual * 1.15,
            'cor': 'warning',
            'descricao': 'Cenário com condições adversas (15% menor natalidade, 15% mais mortalidade)',
        }
    }
    
    # Calcular projeções para cada cenário
    for nome, cenario in cenarios.items():
        cenario['projecao'] = calcular_projecao_cenario(
            propriedade, 
            cenario['taxa_natalidade'],
            cenario['taxa_mortalidade']
        )
    
    return render(request, 'gestao_rural/cenarios_projecao.html', {
        'propriedade': propriedade,
        'cenarios': cenarios,
    })
```

**Passo 2:** Template para comparação de cenários
```django
<div class="row">
    <div class="col-md-4">
        <div class="card border-success">
            <div class="card-header bg-success text-white">
                <h5><i class="bi bi-arrow-up-circle"></i> Cenário Otimista</h5>
            </div>
            <div class="card-body">
                <h3>R$ {{ cenarios.otimista.total|floatformat:2 }}</h3>
                <p class="text-muted">Receita em 5 anos</p>
                <p class="small">{{ cenarios.otimista.descricao }}</p>
                <ul class="list-unstyled">
                    <li>Natalidade: {{ cenarios.otimista.taxa_natalidade }}%</li>
                    <li>Mortalidade: {{ cenarios.otimista.taxa_mortalidade }}%</li>
                </ul>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card border-primary">
            <div class="card-header bg-primary text-white">
                <h5><i class="bi bi-graph-up"></i> Cenário Realista</h5>
            </div>
            <div class="card-body">
                <h3>R$ {{ cenarios.realista.total|floatformat:2 }}</h3>
                <p class="text-muted">Receita em 5 anos</p>
                <p class="small">{{ cenarios.realista.descricao }}</p>
                <ul class="list-unstyled">
                    <li>Natalidade: {{ cenarios.realista.taxa_natalidade }}%</li>
                    <li>Mortalidade: {{ cenarios.realista.taxa_mortalidade }}%</li>
                </ul>
            </div>
        </div>
    </div>
    
    <div class="col-md-4">
        <div class="card border-warning">
            <div class="card-header bg-warning text-white">
                <h5><i class="bi bi-arrow-down-circle"></i> Cenário Conservador</h5>
            </div>
            <div class="card-body">
                <h3>R$ {{ cenarios.conservador.total|floatformat:2 }}</h3>
                <p class="text-muted">Receita em 5 anos</p>
                <p class="small">{{ cenarios.conservador.descricao }}</p>
                <ul class="list-unstyled">
                    <li>Natalidade: {{ cenarios.conservador.taxa_natalidade }}%</li>
                    <li>Mortalidade: {{ cenarios.conservador.taxa_mortalidade }}%</li>
                </ul>
            </div>
        </div>
    </div>
</div>
```

#### Benefícios
- ✅ Teste de diferentes hipóteses
- ✅ Planejamento mais robusto
- ✅ Análise de risco
- ✅ Decisões mais informadas

---

### 3. **Cache de Projeções - Desempenho** ⏳

#### Objetivo
Implementar cache para melhorar performance de projeções.

#### Implementação Sugerida

**Passo 1:** Implementar função com cache
```python
from django.core.cache import cache
import hashlib
import json

def gerar_projecao_cached(propriedade_id, anos, parametros):
    """Gera projeção com cache de 30 minutos"""
    # Criar chave única baseada nos parâmetros
    cache_key = f'projecao_{propriedade_id}_{anos}_{hashlib.md5(json.dumps(parametros).encode()).hexdigest()}'
    
    # Verificar cache
    projecao = cache.get(cache_key)
    
    if not projecao:
        print("Cache miss - gerando nova projeção...")
        projecao = gerar_projecao(propriedade_id, anos, parametros)
        cache.set(cache_key, projecao, 1800)  # 30 minutos
    else:
        print("Cache hit - usando projeção em cache")
    
    return projecao
```

**Passo 2:** Invalidar cache quando necessário
```python
def invalidar_cache_projecao(propriedade_id):
    """Invalida cache de projeções da propriedade"""
    cache.delete_pattern(f'projecao_{propriedade_id}_*')
```

#### Benefícios
- ✅ Melhor performance (cache de 30 min)
- ✅ Redução de processamento
- ✅ Respostas mais rápidas

---

### 4. **Relatórios PDF - ReportLab** ⏳

#### Objetivo
Gerar relatórios em PDF das projeções.

#### Implementação Sugerida

**Passo 1:** Instalar ReportLab (já está no requirements.txt)
```bash
pip install reportlab
```

**Passo 2:** Criar view para gerar PDF
```python
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from reportlab.lib.units import inch

@login_required
def gerar_relatorio_pdf(request, propriedade_id):
    """Gera relatório em PDF"""
    from .models import Propriedade, MovimentacaoProjetada
    
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    movimentacoes = MovimentacaoProjetada.objects.filter(propriedade=propriedade)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="relatorio_{propriedade.id}.pdf"'
    
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    
    # Título
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, height - 50, f"Relatório de Projeção - {propriedade.nome_propriedade}")
    
    # Data
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 70, f"Gerado em: {timezone.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Dados
    y = height - 120
    for mov in movimentacoes:
        p.setFont("Helvetica", 10)
        p.drawString(100, y, f"{mov.data_movimentacao.strftime('%d/%m/%Y')}")
        p.drawString(200, y, f"{mov.get_tipo_movimentacao_display()}")
        p.drawString(300, y, f"{mov.categoria.nome}")
        p.drawString(450, y, f"{mov.quantidade}")
        
        if y < 100:
            p.showPage()
            y = height - 50
        else:
            y -= 20
    
    p.showPage()
    p.save()
    return response
```

#### Benefícios
- ✅ Relatórios profissionais
- ✅ Fácil compartilhamento
- ✅ Impressão direta
- ✅ Documentação permanente

---

## 📊 Ordem de Implementação Sugerida

### Prioridade Alta:
1. **Cache de Projeções** - Melhor desempenho imediato
2. **Gráficos Chart.js** - Melhor visualização

### Prioridade Média:
3. **Análise de Cenários** - Funcionalidade avançada
4. **Relatórios PDF** - Exportação profissional

---

## 🎯 Estimativa de Tempo

| Melhoria | Tempo Estimado |
|----------|----------------|
| Cache | 30 minutos |
| Gráficos | 1-2 horas |
| Cenários | 2-3 horas |
| PDF | 1-2 horas |

**Total:** 4-7 horas de desenvolvimento

---

## 📝 Notas

- Todas as melhorias são incrementais
- Podem ser implementadas independentemente
- Não afetam funcionalidades existentes
- Melhoram significativamente a UX

---

**Data:** 27 de Outubro de 2025

