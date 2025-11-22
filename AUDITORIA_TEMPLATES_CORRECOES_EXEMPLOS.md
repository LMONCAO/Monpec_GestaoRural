# 🔧 Exemplos de Correções - Auditoria de Templates

Este documento contém exemplos práticos de como corrigir os problemas identificados na auditoria.

---

## 1. Correção de Vulnerabilidades XSS

### ❌ ANTES (Vulnerável)

```javascript
// templates/gestao_rural/curral_dashboard_v2.html
function mostrarLog(hora, mensagem) {
    const logItem = document.createElement('div');
    logItem.innerHTML = `<span class="simulacao-log-time">${hora}</span><span class="simulacao-log-message">${mensagem}</span>`;
    // ... código ...
}
```

### ✅ DEPOIS (Seguro)

**Opção 1: Usando textContent e createElement**

```javascript
function mostrarLog(hora, mensagem) {
    const logItem = document.createElement('div');
    logItem.className = 'simulacao-log';
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'simulacao-log-time';
    timeSpan.textContent = hora;
    
    const messageSpan = document.createElement('span');
    messageSpan.className = 'simulacao-log-message';
    messageSpan.textContent = mensagem;
    
    logItem.appendChild(timeSpan);
    logItem.appendChild(messageSpan);
    // ... código ...
}
```

**Opção 2: Usando DOMPurify**

```javascript
// Instalar: npm install dompurify
import DOMPurify from 'dompurify';

function mostrarLog(hora, mensagem) {
    const logItem = document.createElement('div');
    const html = `<span class="simulacao-log-time">${DOMPurify.sanitize(hora)}</span><span class="simulacao-log-message">${DOMPurify.sanitize(mensagem)}</span>`;
    logItem.innerHTML = html;
    // ... código ...
}
```

**Opção 3: Usando template strings seguras**

```javascript
function mostrarLog(hora, mensagem) {
    // Escapar manualmente se não usar DOMPurify
    const escapeHtml = (text) => {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    };
    
    const logItem = document.createElement('div');
    logItem.innerHTML = `
        <span class="simulacao-log-time">${escapeHtml(hora)}</span>
        <span class="simulacao-log-message">${escapeHtml(mensagem)}</span>
    `;
    // ... código ...
}
```

---

## 2. Correção do Uso de `|safe`

### ❌ ANTES (Inseguro)

```django
<!-- templates/propriedades_lista.html -->
<span class="stat-box-value">{{ propriedade.valor_total|default:"R$ 0"|safe }}</span>
```

### ✅ DEPOIS (Seguro)

**Opção 1: Remover `|safe` se não necessário**

```django
<span class="stat-box-value">{{ propriedade.valor_total|default:"R$ 0"|floatformat:2 }}</span>
```

**Opção 2: Usar template tag customizada**

```python
# gestao_rural/templatetags/formatacao_br.py
from django import template

register = template.Library()

@register.filter
def moeda_br(valor):
    """Formata valor como moeda brasileira"""
    if valor is None:
        return "R$ 0,00"
    try:
        return f"R$ {float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return "R$ 0,00"
```

```django
{% load formatacao_br %}
<span class="stat-box-value">{{ propriedade.valor_total|moeda_br }}</span>
```

---

## 3. Correção de Dados em JavaScript

### ❌ ANTES (Inseguro)

```django
<!-- templates/gestao_rural/relatorio_inventario.html -->
<script>
    const categorias = {{ inventario_por_categoria.keys|safe }};
    const quantidades = {{ inventario_por_categoria.values|safe }};
</script>
```

### ✅ DEPOIS (Seguro)

**Opção 1: Usar `|escapejs` e `json_script`**

```django
{% load static %}

<!-- No template -->
{{ inventario_por_categoria|json_script:"inventario-data" }}

<script>
    const inventarioData = JSON.parse(document.getElementById('inventario-data').textContent);
    const categorias = Object.keys(inventarioData);
    const quantidades = Object.values(inventarioData).map(item => item.quantidade);
</script>
```

**Opção 2: Endpoint JSON separado**

```python
# views.py
from django.http import JsonResponse

def inventario_json(request, propriedade_id):
    data = {
        'categorias': list(inventario_por_categoria.keys()),
        'quantidades': list(inventario_por_categoria.values())
    }
    return JsonResponse(data)
```

```javascript
// No template
fetch(`/propriedade/${propriedadeId}/inventario/json/`)
    .then(response => response.json())
    .then(data => {
        const categorias = data.categorias;
        const quantidades = data.quantidades;
    });
```

---

## 4. Correção de CSRF Token

### ❌ ANTES (Expõe token em JavaScript)

```django
<!-- templates/gestao_rural/curral_dashboard_v2.html -->
<script>
    const csrfToken = "{{ csrf_token }}";
</script>
```

### ✅ DEPOIS (Seguro)

**Opção 1: Meta tag no head**

```django
<!-- No template base -->
<meta name="csrf-token" content="{{ csrf_token }}">
```

```javascript
// JavaScript
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrfToken = getCookie('csrftoken') || document.querySelector('meta[name="csrf-token"]')?.content;
```

**Opção 2: Função helper compartilhada**

```javascript
// static/js/csrf.js
window.getCSRFToken = function() {
    const cookieValue = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    
    if (cookieValue) return cookieValue;
    
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    return metaTag ? metaTag.content : null;
};
```

```html
<!-- Incluir no template base -->
<script src="{% static 'js/csrf.js' %}"></script>

<!-- Usar em outros scripts -->
<script>
    const csrfToken = window.getCSRFToken();
</script>
```

---

## 5. Separar JavaScript do HTML

### ❌ ANTES (JavaScript inline gigante)

```django
<!-- templates/gestao_rural/curral_dashboard_v2.html -->
{% block extra_js %}
<script>
    // 10.000+ linhas de JavaScript aqui...
    function gravarPesagemDireto() {
        // ...
    }
    // ... mais código ...
</script>
{% endblock %}
```

### ✅ DEPOIS (Organizado)

**Estrutura de arquivos:**

```
static/
  js/
    curral/
      dashboard-v2.js
      pesagem.js
      simulacao.js
      utils.js
```

**template:**

```django
{% block extra_js %}
{% load static %}
<script src="{% static 'js/curral/utils.js' %}"></script>
<script src="{% static 'js/curral/pesagem.js' %}"></script>
<script src="{% static 'js/curral/simulacao.js' %}"></script>
<script src="{% static 'js/curral/dashboard-v2.js' %}"></script>
{% endblock %}
```

**static/js/curral/pesagem.js:**

```javascript
// static/js/curral/pesagem.js
(function() {
    'use strict';
    
    window.gravarPesagemDireto = async function() {
        // ... código da função ...
    };
    
    // ... outras funções relacionadas a pesagem ...
})();
```

---

## 6. Remover Console.log em Produção

### ❌ ANTES

```javascript
function buscarAnimal(codigo) {
    console.log('Buscando animal:', codigo);
    console.log('URL:', url);
    // ...
    console.log('Animal encontrado:', data);
}
```

### ✅ DEPOIS

**Opção 1: Logger condicional**

```javascript
// static/js/logger.js
window.logger = {
    debug: function(...args) {
        if (window.DEBUG) {
            console.log('[DEBUG]', ...args);
        }
    },
    info: function(...args) {
        if (window.DEBUG) {
            console.info('[INFO]', ...args);
        }
    },
    warn: function(...args) {
        console.warn('[WARN]', ...args);
    },
    error: function(...args) {
        console.error('[ERROR]', ...args);
    }
};
```

```django
<!-- No template base -->
<script>
    window.DEBUG = {% if debug %}true{% else %}false{% endif %};
</script>
<script src="{% static 'js/logger.js' %}"></script>
```

```javascript
// Usar em outros scripts
function buscarAnimal(codigo) {
    logger.debug('Buscando animal:', codigo);
    logger.debug('URL:', url);
    // ...
    logger.info('Animal encontrado:', data);
}
```

**Opção 2: Usar biblioteca de logging**

```javascript
// Instalar: npm install loglevel
import log from 'loglevel';

if (process.env.NODE_ENV === 'production') {
    log.setLevel('warn'); // Apenas warnings e errors
} else {
    log.setLevel('debug'); // Tudo
}

function buscarAnimal(codigo) {
    log.debug('Buscando animal:', codigo);
    // ...
}
```

---

## 7. Validar Entrada no Frontend

### ❌ ANTES (Sem validação)

```html
<form id="pesagem-form">
    <input type="text" id="brinco" name="brinco">
    <input type="number" id="peso" name="peso">
    <button type="submit">Salvar</button>
</form>
```

### ✅ DEPOIS (Com validação)

**Opção 1: HTML5 nativo**

```html
<form id="pesagem-form" novalidate>
    <input 
        type="text" 
        id="brinco" 
        name="brinco"
        required
        minlength="3"
        maxlength="20"
        pattern="[A-Z0-9]+"
        title="Código deve conter apenas letras maiúsculas e números">
    
    <input 
        type="number" 
        id="peso" 
        name="peso"
        required
        min="0.1"
        max="2000"
        step="0.1"
        title="Peso deve estar entre 0.1 e 2000 kg">
    
    <button type="submit">Salvar</button>
</form>
```

**Opção 2: JavaScript customizado**

```javascript
function validarPesagem(brinco, peso) {
    const erros = [];
    
    // Validar brinco
    if (!brinco || brinco.trim().length < 3) {
        erros.push('O código do brinco deve ter pelo menos 3 caracteres');
    }
    
    if (!/^[A-Z0-9]+$/.test(brinco.trim())) {
        erros.push('O código do brinco deve conter apenas letras maiúsculas e números');
    }
    
    // Validar peso
    const pesoNum = parseFloat(peso);
    if (isNaN(pesoNum) || pesoNum <= 0) {
        erros.push('O peso deve ser um número maior que zero');
    }
    
    if (pesoNum > 2000) {
        erros.push('O peso não pode ser maior que 2000 kg');
    }
    
    return erros;
}

document.getElementById('pesagem-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const brinco = document.getElementById('brinco').value;
    const peso = document.getElementById('peso').value;
    
    const erros = validarPesagem(brinco, peso);
    
    if (erros.length > 0) {
        mostrarErros(erros);
        return;
    }
    
    // Prosseguir com o envio
    enviarPesagem(brinco, peso);
});
```

---

## 8. Template Base Seguro

### Exemplo de template base seguro:

```django
{% load static %}
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token }}">
    
    <title>{% block title %}MONPEC{% endblock %}</title>
    
    <!-- CSS -->
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    
    <!-- Scripts no final -->
    <script>
        // Variáveis globais seguras
        window.DEBUG = {% if debug %}true{% else %}false{% endif %};
        window.CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]')?.content || 
                           document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '';
    </script>
    
    <script src="{% static 'js/utils.js' %}"></script>
    <script src="{% static 'js/csrf.js' %}"></script>
    <script src="{% static 'js/logger.js' %}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

---

## 📝 Checklist de Implementação

Ao aplicar as correções, verifique:

- [ ] Remover todos os usos inseguros de `innerHTML`
- [ ] Remover ou validar todos os usos de `|safe`
- [ ] Escapar dados antes de usar em JavaScript
- [ ] Mover CSRF token para meta tag ou cookie
- [ ] Separar JavaScript em arquivos externos
- [ ] Remover console.log em produção
- [ ] Adicionar validação de entrada
- [ ] Testar todas as funcionalidades após correções
- [ ] Verificar que não quebrou nada
- [ ] Documentar mudanças

---

**Próximos Passos:**
1. Implementar correções prioritárias (XSS e CSRF)
2. Separar JavaScript em arquivos externos
3. Adicionar validação de entrada
4. Testar extensivamente
5. Implementar sistema de logging adequado




