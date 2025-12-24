# 📐 GUIA DE AJUSTE DO LAYOUT VISUAL - TELA CURRAL

## 📍 Arquivo Principal
**Localização:** `templates/gestao_rural/curral_dashboard_v2.html`

Este arquivo contém TODO o CSS e HTML da tela de Curral. Todas as alterações visuais devem ser feitas aqui.

---

## 🎨 PRINCIPAIS PONTOS DE AJUSTE

### 1. **LAYOUT GERAL (Duas Colunas)**

**Localização:** Linha ~3420

```css
.curral-v4-layout {
  display: grid;
  grid-template-columns: 55% 45%;  /* ← AJUSTE AQUI: % da coluna esquerda e direita */
  gap: 16px;                        /* ← AJUSTE AQUI: Espaço entre as colunas */
  margin-top: 12px;                 /* ← AJUSTE AQUI: Espaço do topo */
}
```

**Como ajustar:**
- `grid-template-columns: 55% 45%` → Mude para `60% 40%` se quiser mais espaço à esquerda
- `gap: 16px` → Aumente para `20px` ou `24px` para mais espaço entre colunas
- `margin-top: 12px` → Aumente para `20px` se quiser mais espaço do topo

---

### 2. **CARDS DE CONFIGURAÇÃO DA SESSÃO**

**Localização:** Linha ~7783

```html
<div id="gridConfigCards" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 12px;">
```

**Como ajustar:**
- `grid-template-columns: repeat(4, 1fr)` → Mude para `repeat(2, 1fr)` para 2 colunas
- `gap: 10px` → Aumente para `12px` ou `16px` para mais espaço entre cards
- `margin-bottom: 12px` → Aumente para `20px` para mais espaço abaixo

**Altura dos Cards:** Linha ~7785

```html
<div style="position: relative; min-height: 120px;">
```

- `min-height: 120px` → Aumente para `150px` ou `180px` para cards maiores
- Reduza para `100px` para cards mais compactos

---

### 3. **ESPAÇAMENTO ENTRE ELEMENTOS**

**Localização:** Linha ~3483 e ~3495

```css
.curral-v4-painel-esquerdo {
  display: flex;
  flex-direction: column;
  gap: 12px;  /* ← AJUSTE AQUI: Espaço entre cards do painel esquerdo */
}

.curral-v4-painel-direito {
  display: flex;
  flex-direction: column;
  gap: 12px;  /* ← AJUSTE AQUI: Espaço entre cards do painel direito */
}
```

**Como ajustar:**
- `gap: 12px` → Aumente para `16px` ou `20px` para mais espaço vertical
- Reduza para `8px` ou `10px` para layout mais compacto

---

### 4. **PADDING DOS CARDS**

**Localização:** Linha ~3649 (CSS adicional)

```css
.curral-v4-painel-esquerdo .card-curral-header {
  padding: 10px 12px !important;  /* ← AJUSTE AQUI: Padding do cabeçalho */
}

.curral-v4-painel-esquerdo .card-curral-body {
  padding: 12px !important;  /* ← AJUSTE AQUI: Padding do corpo do card */
}
```

**Como ajustar:**
- `padding: 10px 12px` → Aumente para `14px 16px` para mais espaço interno
- `padding: 12px` → Aumente para `16px` ou `20px` para mais espaço

---

### 5. **TAMANHO DAS FONTES**

**Localização:** Linha ~3649

```css
.card-curral-header h2 {
  font-size: 0.95rem !important;  /* ← AJUSTE AQUI: Tamanho do título */
}
```

**Como ajustar:**
- `font-size: 0.95rem` → Aumente para `1rem` ou `1.1rem` para títulos maiores
- Reduza para `0.85rem` para títulos menores

**Títulos dos Cards de Configuração:** Linha ~7790

```html
<h3 style="margin: 0 0 4px 0; color: #1976d2; font-size: 0.9rem; font-weight: 700;">PESAGEM</h3>
<p style="margin: 0; color: #666; font-size: 0.75rem;">Clique para configurar</p>
```

- `font-size: 0.9rem` → Aumente para `1rem` para títulos maiores
- `font-size: 0.75rem` → Aumente para `0.85rem` para subtítulos maiores

---

### 6. **CORES DOS CARDS**

**Localização:** Linhas ~7790, ~7819, ~7848, ~7877

```html
<!-- PESAGEM - Azul -->
<h3 style="... color: #1976d2; ...">PESAGEM</h3>

<!-- SANITÁRIO - Vermelho -->
<h3 style="... color: #d32f2f; ...">SANITÁRIO</h3>

<!-- REPRODUÇÃO - Roxo -->
<h3 style="... color: #7b1fa2; ...">REPRODUÇÃO</h3>

<!-- MOVIMENTAÇÃO - Laranja -->
<h3 style="... color: #f57c00; ...">MOVIMENTAÇÃO</h3>
```

**Como ajustar:**
- Mude as cores hexadecimais (`#1976d2`, `#d32f2f`, etc.) para outras cores
- Exemplo: `#1976d2` (azul) → `#2196F3` (azul mais claro)

---

### 7. **RESPONSIVIDADE (Telas Menores)**

**Localização:** Linha ~3439

```css
@media (max-width: 1400px) {
  .curral-v4-layout {
    grid-template-columns: 1fr;  /* ← Muda para 1 coluna em telas menores */
    gap: 16px;
  }
}
```

**Como ajustar:**
- Mude `1400px` para `1200px` se quiser que mude mais cedo
- Mude para `1600px` se quiser que mude mais tarde

---

## 🔧 EXEMPLOS PRÁTICOS

### Exemplo 1: Aumentar Espaçamento Geral
```css
.curral-v4-layout {
  gap: 24px;  /* Era 16px, agora 24px */
}

.curral-v4-painel-esquerdo {
  gap: 16px;  /* Era 12px, agora 16px */
}
```

### Exemplo 2: Cards de Configuração Maiores
```html
<div style="position: relative; min-height: 150px;">  <!-- Era 120px -->
```

### Exemplo 3: Layout 50/50 (Igual)
```css
.curral-v4-layout {
  grid-template-columns: 50% 50%;  /* Era 55% 45% */
}
```

### Exemplo 4: Mais Padding nos Cards
```css
.curral-v4-painel-esquerdo .card-curral-body {
  padding: 16px !important;  /* Era 12px */
}
```

---

## 📝 COMO FAZER AS ALTERAÇÕES

1. **Abra o arquivo:** `templates/gestao_rural/curral_dashboard_v2.html`
2. **Use Ctrl+F** para encontrar o código que quer alterar
3. **Faça a alteração** no valor (ex: `12px` → `16px`)
4. **Salve o arquivo** (Ctrl+S)
5. **Recarregue a página** no navegador (F5)

---

## ⚠️ IMPORTANTE

- **Sempre faça backup** antes de alterar
- **Teste em diferentes tamanhos de tela** após alterar
- **Use `!important`** apenas quando necessário (já está sendo usado em alguns lugares)
- **Mantenha a consistência** - se aumentar um espaçamento, aumente outros também

---

## 🎯 DICAS

- **Para layout mais compacto:** Reduza `gap`, `padding` e `min-height`
- **Para layout mais espaçoso:** Aumente `gap`, `padding` e `min-height`
- **Para melhor visualização:** Aumente `font-size` dos títulos
- **Para cores diferentes:** Use um gerador de cores online (ex: coolors.co)

---

## 📞 PRECISA DE AJUDA?

Se precisar ajustar algo específico, me informe:
- O que quer mudar (ex: "aumentar espaço entre cards")
- Onde está (ex: "cards de configuração")
- Quanto quer mudar (ex: "mais 10px")

E eu faço a alteração para você! 🚀










