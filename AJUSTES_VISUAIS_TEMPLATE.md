# Guia de Ajustes Visuais - Template Curral Dashboard V2

Este arquivo mostra os principais pontos do template onde você pode fazer ajustes visuais.

## 📍 Localização do Arquivo
`templates/gestao_rural/curral_dashboard_v2.html`

## 🎨 Principais Áreas para Ajustes

### 1. **Cores Principais (Variáveis CSS)**
**Localização:** Linha ~1875

```css
:root {
  --monpec-primary: #2c3e50;        /* Cor principal (azul escuro) */
  --monpec-primary-dark: #1a252f;   /* Cor principal escura */
  --monpec-accent: #3498db;         /* Cor de destaque */
  --monpec-bg: #ecf0f1;             /* Cor de fundo */
  --monpec-success: #27ae60;        /* Verde (sucesso) */
  --monpec-danger: #e74c3c;         /* Vermelho (erro) */
  --monpec-warning: #f39c12;        /* Laranja (aviso) */
  --monpec-text: #2c3e50;           /* Cor do texto */
  --monpec-text-light: #7f8c8d;     /* Texto secundário */
  --monpec-border: #bdc3c7;         /* Cor das bordas */
  --monpec-card-bg: #ffffff;        /* Cor de fundo dos cards */
}
```

**O que ajustar aqui:**
- Altere as cores hexadecimais para suas preferências
- Exemplo: `--monpec-primary: #1976d2;` para um azul mais vibrante

---

### 2. **Layout de Duas Colunas**
**Localização:** Linha ~1928

```css
.curral-v4-layout {
  display: grid;
  grid-template-columns: 42% 58%;  /* Ajuste a proporção aqui */
  gap: 20px;                        /* Espaçamento entre colunas */
  margin-top: 20px;
}
```

**O que ajustar:**
- `grid-template-columns`: Altere `42% 58%` para outras proporções, ex: `40% 60%` ou `45% 55%`
- `gap`: Aumente ou diminua o espaçamento entre as colunas
- `margin-top`: Ajuste o espaçamento superior

---

### 3. **Cards (Painéis)**
**Localização:** Linha ~2193

```css
.card-curral {
  background: var(--monpec-card-bg);
  border-radius: 4px;               /* Arredondamento das bordas */
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);  /* Sombra */
  border: 1px solid var(--monpec-border);
  margin-top: 16px;                 /* Espaçamento entre cards */
}
```

**O que ajustar:**
- `border-radius`: Aumente para cards mais arredondados (ex: `8px` ou `12px`)
- `box-shadow`: Ajuste a sombra (ex: `0 2px 8px rgba(0,0,0,0.1)` para sombra mais forte)
- `margin-top`: Espaçamento vertical entre cards

---

### 4. **Cabeçalho dos Cards**
**Localização:** Linha ~2202

```css
.card-curral-header {
  padding: 12px 16px;               /* Espaçamento interno */
  border-bottom: 2px solid var(--monpec-border);
  background: #f8f9fa;              /* Cor de fundo do cabeçalho */
}
```

**O que ajustar:**
- `padding`: Espaçamento interno (ex: `16px 20px` para mais espaço)
- `background`: Cor de fundo do cabeçalho
- `border-bottom`: Espessura e cor da linha inferior

---

### 5. **Botões**
**Localização:** Procurar por `.btn` ou botões específicos

**Exemplos de ajustes:**
- Tamanho dos botões: `padding: 8px 16px;`
- Cores: `background-color: #sua-cor;`
- Arredondamento: `border-radius: 6px;`

---

### 6. **Ficha Cadastral (Grid)**
**Localização:** Linha ~2063

```css
.ficha-cadastral-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;  /* 2 colunas - altere para 1fr 1fr 1fr para 3 colunas */
  gap: 12px;                        /* Espaçamento entre itens */
  padding: 16px;                    /* Espaçamento interno */
}
```

**O que ajustar:**
- `grid-template-columns`: Altere para `1fr` (1 coluna) ou `1fr 1fr 1fr` (3 colunas)
- `gap`: Espaçamento entre os campos
- `padding`: Espaçamento interno do card

---

### 7. **Balança Eletrônica (Card de Pesagem)**
**Localização:** Linha ~2385

```css
.peso-display-v2 {
  min-height: 600px;                /* Altura mínima do card */
  padding: 24px 24px;               /* Espaçamento interno */
}
```

**O que ajustar:**
- `min-height`: Altura mínima do card de pesagem
- `padding`: Espaçamento interno
- `background`: Cor de fundo

---

### 8. **Tabs de Configuração**
**Localização:** Linha ~1956

```css
.config-sessao-tab {
  padding: 12px 16px;               /* Espaçamento das tabs */
  /* Cores específicas por tab */
}

.config-sessao-tab.active {
  /* Estilo da tab ativa */
}
```

**O que ajustar:**
- Cores de cada tab (PESAGEM, SANITÁRIO, REPRODUTIVO, etc.)
- Tamanho e espaçamento das tabs
- Estilo da tab ativa

---

### 9. **Tabela de Animais**
**Localização:** Procurar por estilos de tabela

```css
/* Exemplo */
.table-wrapper {
  max-height: 400px;
  overflow-y: auto;
}
```

**O que ajustar:**
- Altura máxima da tabela
- Estilo das linhas (hover, cores alternadas)
- Tamanho das colunas

---

### 10. **Fontes e Textos**
**Localização:** Linha ~1891

```css
body.curral-v2 {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 14px;                  /* Tamanho base da fonte */
  color: var(--monpec-text);
}
```

**O que ajustar:**
- `font-family`: Altere a fonte (ex: `'Roboto', sans-serif`)
- `font-size`: Tamanho base da fonte (ex: `15px` ou `16px`)

---

## 🛠️ Como Fazer os Ajustes

1. **Abra o arquivo:**
   ```
   templates/gestao_rural/curral_dashboard_v2.html
   ```

2. **Localize a seção CSS:**
   - Procure por `<style>` ou `{% block extra_css %}`
   - Os estilos principais começam na linha ~1874

3. **Faça as alterações:**
   - Edite os valores CSS diretamente
   - Salve o arquivo
   - Recarregue a página no navegador

4. **Use o Inspetor do Navegador (F12):**
   - Pressione F12 para abrir as ferramentas de desenvolvedor
   - Use a ferramenta de seleção para ver os estilos aplicados
   - Teste mudanças diretamente no navegador antes de aplicar no arquivo

---

## 💡 Dicas

- **Faça backup:** Antes de fazer grandes mudanças, faça uma cópia do arquivo
- **Teste gradualmente:** Faça pequenos ajustes e teste cada vez
- **Use variáveis CSS:** Aproveite as variáveis `--monpec-*` para manter consistência
- **Inspetor do navegador:** Use F12 para testar mudanças em tempo real
- **Responsividade:** Verifique se os ajustes funcionam bem em diferentes tamanhos de tela

---

## 📝 Exemplo de Ajuste Rápido

**Quer deixar os cards mais arredondados e com sombra mais suave?**

Encontre:
```css
.card-curral {
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
```

Altere para:
```css
.card-curral {
  border-radius: 12px;              /* Mais arredondado */
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);  /* Sombra mais suave */
}
```

---

## 🎯 Áreas Mais Frequentes de Ajuste

1. **Cores principais** (linha ~1875)
2. **Proporção das colunas** (linha ~1928)
3. **Tamanho dos cards** (linha ~2193)
4. **Espaçamentos** (vários locais, procure por `padding` e `margin`)
5. **Tamanhos de fonte** (procure por `font-size`)











