# Guia de Ajustes Visuais - Curral Dashboard V2

## 📍 Localização dos Elementos Principais

### 1. **Header "Super Tela MONPEC CURRAL - Fazenda Monpec"**

**HTML:** Linha **6151** (dentro de `<div class="curral-v2-header">`)
**CSS:** Linhas **2542-2585**

```css
/* Linha 2542 */
.curral-v2-header {
  background: var(--monpec-primary);
  color: #fff;
  padding: 14px 20px;
  /* ... */
}
```

**Ajustes comuns:**
- Largura: já tem `width: 100%` e `box-sizing: border-box` (linha 2542)
- Cor de fundo: `background: var(--monpec-primary);` (linha 2543)
- Padding: `padding: 14px 20px;` (linha 2545)

---

### 2. **Card "ANIMAIS NA SESSÃO"**

**HTML:** Linha **6771**
```html
<div class="card-curral animais-na-sessao-full-width" style="margin-top: 20px; box-sizing: border-box; overflow-x: auto;">
```

**CSS:** Linhas **2225-2234**
```css
/* Linha 2225 */
.animais-na-sessao-full-width {
  width: 100vw !important;
  max-width: 100vw !important;
  margin-left: calc(-50vw + 50%) !important;
  margin-right: calc(-50vw + 50%) !important;
  /* ... */
}
```

**Ajustes comuns:**
- Largura: altere `width` e `max-width` na linha 2227-2228
- Margens: altere `margin-left` e `margin-right` na linha 2229-2230
- Padding: altere `padding-left` e `padding-right` na linha 2233-2234

---

### 3. **Card "BALANÇA ELETRÔNICA"**

**HTML:** Linha **6669**
```html
<div class="balanca-eletronica-grande">
```

**CSS:** Linhas **2502-2514**
```css
/* Linha 2502 */
.balanca-eletronica-grande {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  border-radius: 12px;
  padding: 32px;
  width: 100%;
  box-sizing: border-box;
  /* ... */
}
```

**Ajustes comuns:**
- Cor de fundo: altere `background` na linha 2503
- Padding: altere `padding: 32px;` na linha 2505
- Largura: já tem `width: 100%` (linha 2513)

---

### 4. **Cards de Manejo (Manejo Sanitário, IATF/REPRODUÇÃO, MOVIMENTAÇÃO)**

**HTML:** 
- Manejo Sanitário: Linha **6726**
- IATF/REPRODUÇÃO: Linha **6738**
- MOVIMENTAÇÃO: Linha **6750**

**Grid Container:** Linha **6713**
```html
<div class="row g-2" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; ...">
```

**CSS do Grid:** Linha **2266**
```css
.pesagem-manejos-wrapper .row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  /* ... */
}
```

**Ajustes comuns:**
- Altura dos cards: cada card tem `flex: 1` no body (linhas 6720, 6732, 6744)
- Padding do header: `padding: 18px;` (linhas 6717, 6729, 6741)
- Padding do body: `padding: 20px;` (linhas 6719, 6731, 6743)
- Cores dos títulos: 
  - Manejo Sanitário: `color: #d32f2f;` (linha 6730)
  - IATF/REPRODUÇÃO: `color: #7b1fa2;` (linha 6742)
  - MOVIMENTAÇÃO: `color: #f57c00;` (linha 6754)

---

### 5. **Botão "GRAVAR DADOS"**

**HTML:** Linha **6764**
```html
<button type="button" class="btn btn-primary btn-lg" id="btnFinalizarGravarV2" 
        style="width: 100%; max-width: 100%; padding: 16px; ...">
```

**Ajustes comuns:**
- Largura: `width: 100%; max-width: 100%;` (já configurado)
- Padding: `padding: 16px;` (altere para aumentar/diminuir)
- Cor de fundo: `background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);`
- Margem superior: `margin-top: auto;` (alinha ao final do container)

---

### 6. **Wrapper Principal**

**CSS:** Linha **2217**
```css
.curral-v2-wrapper {
  max-width: 95%;
  width: 100%;
  margin: 20px auto 40px;
  padding: 0 20px;
  overflow-x: visible;
}
```

**Ajustes comuns:**
- Largura máxima: `max-width: 95%;` (altere para 100% para ocupar toda tela)
- Padding lateral: `padding: 0 20px;` (altere para mudar espaçamento)

---

### 7. **Layout de Duas Colunas**

**CSS:** Linha **2235**
```css
.curral-v4-layout {
  display: grid;
  grid-template-columns: 65% 35%;
  gap: 20px;
  /* ... */
}
```

**Ajustes comuns:**
- Proporção das colunas: `grid-template-columns: 65% 35%;`
  - Exemplo: `70% 30%` ou `60% 40%`
- Espaçamento entre colunas: `gap: 20px;`

---

## 🎨 Exemplos de Ajustes Rápidos

### Aumentar largura do wrapper para 100%:
```css
/* Linha 2218 */
max-width: 100%;  /* em vez de 95% */
```

### Aumentar altura dos cards de manejo:
```html
<!-- Linha 6719, 6731, 6743 -->
<div class="card-curral-body" style="padding: 40px 20px; ...">
<!-- Aumente o primeiro valor (40px) para mais altura -->
```

### Mudar cor do card da balança:
```css
/* Linha 2503 */
background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
/* Ou uma cor sólida: */
background: #1976d2;
```

### Ajustar largura do card ANIMAIS NA SESSÃO:
```css
/* Linha 2227-2228 */
width: calc(100% + 40px) !important;  /* em vez de 100vw */
max-width: calc(100% + 40px) !important;
```

---

## 📝 Notas Importantes

1. **Sempre salve o arquivo** após fazer alterações
2. **Recarregue a página** com Ctrl+F5 (ou Cmd+Shift+R) para ver mudanças
3. **Use `!important`** apenas quando necessário (já está em alguns lugares)
4. **Teste em diferentes tamanhos de tela** após ajustes de largura

---

## 🔍 Como Encontrar Elementos Rapidamente

Use Ctrl+F (ou Cmd+F) no arquivo e busque por:
- `ANIMAIS NA SESSÃO` → linha 6771
- `BALANÇA ELETRÔNICA` → linha 6669
- `GRAVAR DADOS` → linha 6764
- `Manejo Sanitário` → linha 6726
- `Super Tela` → linha 6166
- `.curral-v2-wrapper` → linha 2217 (CSS)
- `.curral-v2-header` → linha 2542 (CSS)








