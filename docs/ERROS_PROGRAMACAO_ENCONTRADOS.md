# Erros de Programação Encontrados - Curral V4

**Data da Verificação:** 2025-01-XX  
**Verificador:** Análise Profunda de Código

---

## 🔴 ERROS CRÍTICOS

### 1. **Função `atualizarFichaCadastralV4` NÃO está sendo chamada**

**Localização:** `templates/gestao_rural/curral_dashboard_v2.html` - função `processarAnimalIdentificado` (linha ~12360)

**Problema:**
A correção que adicionei para chamar `atualizarFichaCadastralV4` não está presente no código. A busca por `atualizarFichaCadastralV4` retorna ZERO resultados, indicando que a chamada não foi adicionada ou foi removida.

**Impacto:**
- Ficha cadastral continua vazia mesmo após identificar animal
- Campos não são preenchidos

**Correção Necessária:**
Adicionar chamada na função `tentarAtualizar()` dentro de `processarAnimalIdentificado`.

---

### 2. **Possível Erro no Cálculo de Desempenho - Verificação de Tipo**

**Localização:** `gestao_rural/views_curral.py` - função `curral_identificar_codigo` (linha 1400)

**Problema:**
O código acessa `pesagem_atual.data_evento.date()` sem verificar se `pesagem_atual` é um objeto `CurralEvento` válido. Embora haja verificação de `if pesagem_atual and pesagem_anterior`, não há verificação explícita de que são objetos do tipo correto.

**Código Atual:**
```python
periodo_dias = (pesagem_atual.data_evento.date() - pesagem_anterior.data_evento.date()).days
```

**Risco:**
Se `pesagem_atual` for None ou não tiver o atributo `data_evento`, causará AttributeError.

**Correção Necessária:**
Adicionar verificação mais robusta ou usar try/except.

---

### 3. **Problema na API `curral_animais_sessao_api` - Formato de Sexo**

**Localização:** `gestao_rural/views_curral.py` - função `curral_animais_sessao_api` (linha 3793)

**Problema:**
O código tenta usar `animal.get_sexo_display()` mas o fallback pode retornar o valor bruto do campo (ex: 'M' ou 'F') em vez de um texto formatado. Isso pode causar inconsistência na exibição.

**Código Atual:**
```python
'sexo': animal.get_sexo_display() if hasattr(animal, 'get_sexo_display') else (animal.sexo or '—'),
```

**Correção Necessária:**
Garantir que sempre retorne texto formatado ('Macho' ou 'Fêmea').

---

### 4. **Race Condition na Função `carregarAnimaisSessao`**

**Localização:** `templates/gestao_rural/curral_dashboard_v2.html` - função `carregarAnimaisSessao` (linha 20907)

**Problema:**
A função usa `setTimeout` de 1 segundo, mas isso não garante que `window.animaisRegistradosTabela` e `window.atualizarTabelaAnimaisRegistrados` estejam inicializados. Pode haver race condition.

**Correção Necessária:**
Implementar verificação mais robusta ou usar eventos customizados.

---

## 🟡 PROBLEMAS MENORES

### 5. **Falta de Tratamento de Erro na API `curral_animais_sessao_api`**

**Localização:** `gestao_rural/views_curral.py` - função `curral_animais_sessao_api`

**Problema:**
Não há tratamento de exceções. Se houver erro ao buscar eventos ou animais, a API retornará erro 500 sem mensagem útil.

**Correção Necessária:**
Adicionar try/except com logging.

---

### 6. **Validação de Dados Faltante na API**

**Localização:** `gestao_rural/views_curral.py` - função `curral_animais_sessao_api`

**Problema:**
Não há validação se `propriedade_id` é válido antes de fazer queries. Embora `get_object_or_404` trate isso, seria melhor ter validação explícita.

---

## 📋 CHECKLIST DE CORREÇÕES

- [ ] Adicionar chamada para `atualizarFichaCadastralV4` em `processarAnimalIdentificado`
- [ ] Melhorar verificação de tipos no cálculo de desempenho
- [ ] Corrigir formato de sexo na API `curral_animais_sessao_api`
- [ ] Melhorar inicialização de `carregarAnimaisSessao` para evitar race conditions
- [ ] Adicionar tratamento de erros na API `curral_animais_sessao_api`
- [ ] Adicionar validações adicionais

---

**Fim da Análise**


