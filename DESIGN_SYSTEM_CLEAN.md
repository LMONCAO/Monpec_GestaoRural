# 🎨 DESIGN SYSTEM CLEAN - MONPEC

## 📋 VISÃO GERAL

Design profissional, minimalista e elegante para o Sistema Monpec.

**Características:**
- ✅ Visual limpo e organizado (clean design)
- ✅ SEM ícones ou figuras desnecessárias
- ✅ Tipografia elegante e hierárquica
- ✅ Espaçamento generoso
- ✅ Cores sutis e profissionais
- ✅ Foco no conteúdo e usabilidade

---

## 🎨 PALETA DE CORES

### Cores Primárias
- **Azul Marinho (Primary):** `#1e3a5f`
  - Uso: Títulos principais, botões primários, elementos de destaque
  - Variação clara: `#2d5082`

- **Marrom Terra (Accent):** `#8b6f47`
  - Uso: Destaques secundários, badges importantes
  - Variação clara: `#a68a5c`

- **Cinza Claro (Background):** `#f5f7fa`
  - Uso: Fundo das páginas

### Cores de Suporte
- **Branco:** `#ffffff` - Cards e elementos de conteúdo
- **Borda Cinza:** `#e1e8ed` - Bordas sutis
- **Texto Primário:** `#2c3e50` - Texto principal
- **Texto Secundário:** `#5a6c7d` - Texto de suporte

---

## 📝 TIPOGRAFIA

### Famílias de Fonte

**1. Inter (Texto Geral)**
- Fonte: `'Inter', -apple-system, BlinkMacSystemFont, sans-serif`
- Pesos: 300 (light), 400 (regular), 500 (medium), 600 (semibold), 700 (bold)
- Uso: Corpo do texto, botões, formulários, tabelas

**2. Playfair Display (Títulos)**
- Fonte: `'Playfair Display', Georgia, serif`
- Pesos: 600 (semibold), 700 (bold)
- Uso: Títulos principais (h1, h2, h3), logo, valores em destaque

### Hierarquia Tipográfica

```
H1 (Page Title)
- Família: Playfair Display
- Tamanho: 2.5rem (40px)
- Peso: 700
- Cor: Azul Marinho
- Letter-spacing: -0.02em

H2 (Section Title)
- Família: Playfair Display
- Tamanho: 2rem (32px)
- Peso: 700
- Cor: Azul Marinho
- Letter-spacing: -0.01em

H3 (Card Title)
- Família: Playfair Display
- Tamanho: 1.5rem (24px)
- Peso: 600
- Cor: Azul Marinho

Corpo de Texto
- Família: Inter
- Tamanho: 15px
- Peso: 400
- Cor: Texto Secundário
- Line-height: 1.6

Texto Pequeno
- Tamanho: 14px
- Peso: 400
- Cor: Texto Secundário

Labels
- Tamanho: 14px
- Peso: 500
- Cor: Texto Primário
- Letter-spacing: 0.01em

Uppercase Labels
- Tamanho: 13px
- Peso: 500
- Transform: uppercase
- Letter-spacing: 0.05em
```

---

## 📦 COMPONENTES

### 1. Botões

#### Botão Primário
```css
background: #1e3a5f (Azul Marinho)
color: white
padding: 0.75rem 1.5rem
border-radius: 8px
font-weight: 500
letter-spacing: 0.02em

hover: background #2d5082, transform translateY(-1px), shadow
```

#### Botão Secundário
```css
background: white
color: #1e3a5f
border: 1px solid #e1e8ed
padding: 0.75rem 1.5rem
border-radius: 8px

hover: border-color #1e3a5f, background #f5f7fa
```

#### Botão Accent
```css
background: #8b6f47 (Marrom Terra)
color: white
padding: 0.75rem 1.5rem
border-radius: 8px

hover: background #a68a5c, transform translateY(-1px)
```

### 2. Cards

```css
background: white
border: 1px solid #e1e8ed
border-radius: 12px
padding: 2rem
margin-bottom: 1.5rem

hover: border-color #1e3a5f, shadow, transform translateY(-2px)
```

**Estrutura:**
- Card Title (h3): Playfair Display, 1.25rem, Azul Marinho
- Card Description: Inter, 14px, Texto Secundário

### 3. Tabelas

```css
background: white
border: 1px solid #e1e8ed
border-radius: 12px
overflow: hidden
```

**Header:**
- Background: #f5f7fa
- Texto: 13px, uppercase, letter-spacing 0.05em
- Cor: Texto Secundário

**Rows:**
- Padding: 1.5rem
- Border-top: 1px solid #e1e8ed
- Hover: background #f5f7fa

### 4. Formulários

**Labels:**
```css
font-weight: 500
font-size: 14px
color: #2c3e50
letter-spacing: 0.01em
```

**Inputs:**
```css
border: 1px solid #e1e8ed
border-radius: 8px
padding: 0.75rem 1rem
font-size: 14px

focus: border-color #1e3a5f, shadow 0 0 0 3px rgba(30,58,95,0.1)
```

### 5. Badges

```css
padding: 0.35rem 0.75rem
border-radius: 4px
font-size: 12px
font-weight: 500
letter-spacing: 0.02em
```

**Variações:**
- Navy: background #1e3a5f, color white
- Brown: background #8b6f47, color white
- Gray: background #e1e8ed, color #2c3e50

### 6. Stat Cards (Estatísticas)

```css
background: white
border: 1px solid #e1e8ed
border-radius: 12px
padding: 2rem
text-align: center
```

**Valor:**
- Família: Playfair Display
- Tamanho: 2.5rem
- Peso: 700
- Cor: Azul Marinho

**Label:**
- Tamanho: 13px
- Peso: 500
- Transform: uppercase
- Letter-spacing: 0.05em
- Cor: Texto Secundário

---

## 📏 ESPAÇAMENTO

Sistema de espaçamento consistente:

```css
--spacing-xs: 0.5rem   (8px)
--spacing-sm: 1rem     (16px)
--spacing-md: 1.5rem   (24px)
--spacing-lg: 2rem     (32px)
--spacing-xl: 3rem     (48px)
```

**Aplicação:**
- Espaçamento interno (padding): `md` para cards, `lg` para seções
- Margens entre elementos: `sm` para proximidade, `md` para separação
- Margens entre seções: `lg` ou `xl`

---

## 🎭 HIERARQUIA VISUAL

### Estrutura de Página

1. **Page Header** (Destaque máximo)
   - Background: white
   - Border: 1px sólida
   - Padding: 3rem 2rem
   - Título: Playfair Display, 2.5rem
   - Subtítulo: Inter, 1.1rem, texto secundário

2. **Section Headers**
   - Título: Playfair Display, 1.75-2rem
   - Margem bottom: 2rem

3. **Cards Grid**
   - Grid auto-fill, min 320px
   - Gap: 1.5rem

4. **Conteúdo**
   - Padding: 3rem 1.5rem
   - Max-width: 1400px
   - Margin: 0 auto

---

## 🔄 TRANSIÇÕES E ANIMAÇÕES

**Princípio:** Suaves e profissionais

```css
Transições padrão: 0.2s ease
Hover effects: transform translateY(-1px to -2px)
Shadow on hover: 0 8px 24px rgba(30,58,95,0.08)
```

**Elementos animados:**
- Botões: background, transform, shadow
- Cards: border-color, shadow, transform
- Links: color

---

## 📱 RESPONSIVIDADE

### Breakpoints

- **Mobile:** < 768px
  - Grid: 1 coluna
  - Fonte H1: 2rem
  - Padding reduzido: 1rem

- **Tablet:** 768px - 1024px
  - Grid: 2 colunas
  - Fonte padrão

- **Desktop:** > 1024px
  - Grid: 3-4 colunas
  - Max-width container: 1400px

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

Para cada nova página/template:

- [ ] Estende `base_clean.html`
- [ ] Usa Playfair Display para títulos
- [ ] Usa Inter para texto
- [ ] Cores da paleta oficial
- [ ] Espaçamento consistente
- [ ] SEM ícones ou imagens decorativas
- [ ] Bordas sutis (1px, #e1e8ed)
- [ ] Border-radius consistente (4px, 8px, 12px)
- [ ] Hover effects suaves
- [ ] Responsivo (mobile-first)
- [ ] Acessibilidade (contraste, labels)

---

## 📄 ARQUIVOS DO SISTEMA

### Templates Base
- `base_clean.html` - Template base com todo o design system

### Templates de Páginas
- `login_clean.html` - Página de login
- `propriedades_lista_clean.html` - Lista de propriedades
- `pecuaria_dashboard_clean.html` - Dashboard de pecuária

### Como Usar

Todos os templates devem estender o base:

```django
{% extends "base_clean.html" %}
{% load formatacao_br %}

{% block title %}Título da Página{% endblock %}

{% block content %}
<!-- Conteúdo aqui -->
{% endblock %}
```

---

## 🎯 PRINCÍPIOS DE DESIGN

1. **Clareza** - Informação clara e hierárquica
2. **Consistência** - Padrões visuais uniformes
3. **Elegância** - Design sofisticado e profissional
4. **Simplicidade** - Menos é mais, foco no conteúdo
5. **Profissionalismo** - Visual corporativo e confiável
6. **Usabilidade** - Interface intuitiva e funcional

---

## 📞 SUPORTE

Para dúvidas sobre o design system ou implementação, consulte este documento ou os templates de referência em `C:\Monpec_projetista\templates\`.

