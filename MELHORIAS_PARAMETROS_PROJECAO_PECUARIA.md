# Melhorias em Parâmetros e Projeção - Módulo Pecuária

## Data: 27 de Outubro de 2025

## 📋 Resumo

Análise completa dos módulos de **Parâmetros** e **Projeção** da Pecuária com sugestões de melhorias.

---

## 🎯 Melhorias em Parâmetros

### 1. **Validação de Parâmetros**

**Problema:** Falta validação para garantir que parâmetros estão corretos

**Solução:**
```python
# Em forms.py
class ParametrosProjecaoForm(forms.ModelForm):
    class Meta:
        model = ParametrosProjecaoRebanho
        fields = [
            'taxa_natalidade_anual',
            'taxa_mortalidade_bezerros_anual',
            'taxa_mortalidade_adultos_anual',
            'percentual_venda_machos_anual',
            'percentual_venda_femeas_anual',
            'periodicidade'
        ]
    
    def clean_taxa_natalidade_anual(self):
        taxa = self.cleaned_data.get('taxa_natalidade_anual')
        if taxa and (taxa <= 0 or taxa > 100):
            raise forms.ValidationError('Taxa de natalidade deve estar entre 0 e 100.')
        return taxa
    
    def clean_taxa_mortalidade_bezerros_anual(self):
        taxa = self.cleaned_data.get('taxa_mortalidade_bezerros_anual')
        if taxa and (taxa < 0 or taxa > 100):
            raise forms.ValidationError('Taxa de mortalidade de bezerros deve estar entre 0 e 100.')
        return taxa
    
    def clean(self):
        cleaned_data = super().clean()
        natalidade = cleaned_data.get('taxa_natalidade_anual')
        mortalidade = cleaned_data.get('taxa_mortalidade_bezerros_anual')
        
        if natalidade and mortalidade and natalidade < mortalidade:
            raise forms.ValidationError(
                'Taxa de natalidade não pode ser menor que taxa de mortalidade.'
            )
        
        return cleaned_data
```

### 2. **Presets de Parâmetros por Tipo de Ciclo**

**Melhoria:** Adicionar presets por tipo de ciclo

**Solução:**
```python
def obter_presets_parametros(tipo_ciclo):
    """Retorna parâmetros padrão baseado no tipo de ciclo"""
    presets = {
        'CRIA': {
            'taxa_natalidade_anual': Decimal('85'),
            'taxa_mortalidade_bezerros_anual': Decimal('5'),
            'taxa_mortalidade_adultos_anual': Decimal('3'),
            'percentual_venda_machos_anual': Decimal('10'),
            'percentual_venda_femeas_anual': Decimal('15'),
        },
        'RECRIA': {
            'taxa_natalidade_anual': Decimal('75'),
            'taxa_mortalidade_bezerros_anual': Decimal('3'),
            'taxa_mortalidade_adultos_anual': Decimal('2'),
            'percentual_venda_machos_anual': Decimal('20'),
            'percentual_venda_femeas_anual': Decimal('25'),
        },
        'ENGORDA': {
            'taxa_natalidade_anual': Decimal('60'),
            'taxa_mortalidade_bezerros_anual': Decimal('2'),
            'taxa_mortalidade_adultos_anual': Decimal('1'),
            'percentual_venda_machos_anual': Decimal('80'),
            'percentual_venda_femeas_anual': Decimal('50'),
        },
        'CICLO_COMPLETO': {
            'taxa_natalidade_anual': Decimal('70'),
            'taxa_mortalidade_bezerros_anual': Decimal('4'),
            'taxa_mortalidade_adultos_anual': Decimal('2'),
            'percentual_venda_machos_anual': Decimal('40'),
            'percentual_venda_femeas_anual': Decimal('30'),
        },
    }
    return presets.get(tipo_ciclo, {})
```

### 3. **Explicação de Parâmetros com Help Text**

**Melhoria:** Adicionar help texts explicativos

**Solução:**
```python
class ParametrosProjecaoForm(forms.ModelForm):
    class Meta:
        model = ParametrosProjecaoRebanho
        fields = [...]
        help_texts = {
            'taxa_natalidade_anual': 'Percentual de fêmeas que parirão por ano (0-100%)',
            'taxa_mortalidade_bezerros_anual': 'Percentual de bezerros que morrerão por ano (0-100%)',
            'taxa_mortalidade_adultos_anual': 'Percentual de adultos que morrerão por ano (0-100%)',
            'percentual_venda_machos_anual': 'Percentual de machos vendidos por ano (0-100%)',
            'percentual_venda_femeas_anual': 'Percentual de fêmeas vendidas por ano (0-100%)',
        }
```

---

## 🎯 Melhorias em Projeção

### 1. **Visualização Interativa com Gráficos**

**Melhoria:** Adicionar gráficos Chart.js para visualização

**Solução:**
```javascript
// Em template de projeção
<canvas id="projecaoChart"></canvas>

<script>
const ctx = document.getElementById('projecaoChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [{% for ano in anos %}'{{ ano }}',{% endfor %}],
        datasets: [
            {
                label: 'Total de Animais',
                data: [{% for total in total_animais %}{{ total }},{% endfor %}],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            },
            {
                label: 'Receitas',
                data: [{% for receita in receitas %}{{ receita }},{% endfor %}],
                borderColor: 'rgb(54, 162, 235)',
                tension: 0.1
            }
        ]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Projeção do Rebanho (5 Anos)'
            }
        }
    }
});
</script>
```

### 2. **Exportar Projeção para Excel**

**Melhoria:** Permitir exportar projeção para Excel

**Solução:**
```python
from openpyxl import Workbook
from django.http import HttpResponse

def exportar_projecao_excel(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    movimentacoes = MovimentacaoProjetada.objects.filter(
        propriedade=propriedade
    ).select_related('categoria').order_by('data_movimentacao')
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Projeção"
    
    # Cabeçalhos
    ws['A1'] = 'Data'
    ws['B1'] = 'Tipo'
    ws['C1'] = 'Categoria'
    ws['D1'] = 'Quantidade'
    ws['E1'] = 'Valor Total'
    
    # Dados
    row = 2
    for mov in movimentacoes:
        ws[f'A{row}'] = mov.data_movimentacao.strftime('%d/%m/%Y')
        ws[f'B{row}'] = mov.get_tipo_movimentacao_display()
        ws[f'C{row}'] = mov.categoria.nome
        ws[f'D{row}'] = mov.quantidade
        ws[f'E{row}'] = float(mov.valor_total) if mov.valor_total else 0
        row += 1
    
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="projecao_{propriedade.id}.xlsx"'
    wb.save(response)
    return response
```

### 3. **Análise de Sensibilidade**

**Melhoria:** Permitir testar diferentes cenários

**Solução:**
```python
def gerar_cenarios_projecao(request, propriedade_id):
    """Gera múltiplos cenários de projeção"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    parametros_base = ParametrosProjecaoRebanho.objects.get(propriedade=propriedade)
    
    cenarios = {
        'otimista': {
            'taxa_natalidade': parametros_base.taxa_natalidade_anual * 1.1,
            'taxa_mortalidade': parametros_base.taxa_mortalidade_bezerros_anual * 0.9,
        },
        'realista': {
            'taxa_natalidade': parametros_base.taxa_natalidade_anual,
            'taxa_mortalidade': parametros_base.taxa_mortalidade_bezerros_anual,
        },
        'conservador': {
            'taxa_natalidade': parametros_base.taxa_natalidade_anual * 0.9,
            'taxa_mortalidade': parametros_base.taxa_mortalidade_bezerros_anual * 1.1,
        }
    }
    
    return render(request, 'gestao_rural/cenarios_projecao.html', {
        'propriedade': propriedade,
        'cenarios': cenarios,
    })
```

### 4. **Cache de Projeções**

**Melhoria:** Cachear projeções para melhor performance

**Solução:**
```python
from django.core.cache import cache

def gerar_projecao_cached(propriedade, anos):
    """Gera projeção com cache de 1 hora"""
    cache_key = f'projecao_{propriedade.id}_{anos}'
    projecao = cache.get(cache_key)
    
    if not projecao:
        projecao = gerar_projecao(propriedade, anos)
        cache.set(cache_key, projecao, 3600)  # 1 hora
    
    return projecao
```

---

## 🎨 Melhorias Visuais

### 1. **Dashboard de Parâmetros Interativo**

**Melhoria:** Cards informativos com sliders

**Solução:**
```django
<!-- Em template de parâmetros -->
<div class="card mb-3">
    <div class="card-header">
        <h5>Taxa de Natalidade</h5>
    </div>
    <div class="card-body">
        <input type="range" class="form-range" 
               min="0" max="100" 
               value="{{ form.taxa_natalidade_anual.value }}"
               id="natalidadeSlider">
        <div class="d-flex justify-content-between">
            <span>0%</span>
            <span id="natalidadeValue">{{ form.taxa_natalidade_anual.value }}%</span>
            <span>100%</span>
        </div>
    </div>
</div>

<script>
document.getElementById('natalidadeSlider').addEventListener('input', function() {
    document.getElementById('natalidadeValue').textContent = this.value + '%';
});
</script>
```

### 2. **Comparação de Cenários**

**Melhoria:** Visualização comparativa de cenários

**Solução:**
```django
<!-- Comparação de cenários -->
<div class="row">
    <div class="col-md-4">
        <div class="card text-center">
            <div class="card-header bg-success">
                <h5>Otimista</h5>
            </div>
            <div class="card-body">
                <h3>R$ {{ cenario_otimista.total }}</h3>
                <p class="text-muted">Receita em 5 anos</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card text-center">
            <div class="card-header bg-primary">
                <h5>Realista</h5>
            </div>
            <div class="card-body">
                <h3>R$ {{ cenario_realista.total }}</h3>
                <p class="text-muted">Receita em 5 anos</p>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card text-center">
            <div class="card-header bg-warning">
                <h5>Conservador</h5>
            </div>
            <div class="card-body">
                <h3>R$ {{ cenario_conservador.total }}</h3>
                <p class="text-muted">Receita em 5 anos</p>
            </div>
        </div>
    </div>
</div>
```

---

## 📊 Resumo de Melhorias

### Parâmetros:
1. ✅ Validação robusta de valores
2. ✅ Presets por tipo de ciclo
3. ✅ Help texts explicativos
4. ✅ Interface interativa com sliders

### Projeção:
1. ✅ Gráficos Chart.js
2. ✅ Exportação para Excel
3. ✅ Análise de sensibilidade
4. ✅ Cache de projeções
5. ✅ Comparação de cenários

---

**Total de Melhorias: 9**

---

## 🎉 Benefícios

1. **Melhor UX** - Interface mais intuitiva
2. **Validação Robusta** - Menos erros
3. **Performance** - Cache e otimizações
4. **Visualização** - Gráficos interativos
5. **Flexibilidade** - Múltiplos cenários
6. **Exportação** - Dados em Excel

---

**Data:** 27 de Outubro de 2025

