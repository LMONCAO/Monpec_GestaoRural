# 🔍 Verificar Template da Landing Page

## ⚠️ Situação

O site está funcionando, mas parece estar mostrando uma versão antiga ou de outro projeto.

**Template atual em uso:** `templates/site/landing_page.html`

**Conteúdo que está aparecendo:**
- "GESTÃO RURAL INTELIGENTE"
- "Controle completo da sua fazenda: rebanho, custos, produção e projetos bancários"

---

## 📋 Verificações Necessárias

### 1. Qual é o projeto correto?

Você tem dois projetos possíveis:

**A) Monpec Gestão Rural** (sistema para fazendas)
- Gestão de rebanho, custos, produção
- Rastreabilidade de animais
- Controle financeiro rural

**B) Monpec Projetista** (sistema para projetistas)
- Projetos de crédito rural
- Gestão documental
- Automação de processos

---

### 2. Qual template deveria ser usado?

**Opção 1:** `templates/site/landing_page.html` (atual)
- Conteúdo: "GESTÃO RURAL INTELIGENTE"
- Para: Fazendas/Produtores

**Opção 2:** `templates/gestao_rural/landing.html`
- Conteúdo: "Monpec Projetista"
- Para: Projetistas de crédito rural

---

## 🔧 Como Corrigir

### Se o projeto correto é "Monpec Gestão Rural":

O template atual está correto. Mas se o conteúdo está desatualizado, você precisa:

1. Atualizar o conteúdo de `templates/site/landing_page.html`
2. Fazer push para o GitHub
3. Fazer novo deploy

### Se o projeto correto é "Monpec Projetista":

Precisa mudar a view para usar o template correto:

1. Editar `gestao_rural/views.py`:
   ```python
   return render(request, 'gestao_rural/landing.html', context)
   ```

2. Fazer push para o GitHub
3. Fazer novo deploy

---

## 📝 Próximos Passos

**Me diga:**
1. Qual é o projeto correto? (Gestão Rural ou Projetista)
2. O conteúdo que está aparecendo está correto ou precisa ser atualizado?
3. Se precisa atualizar, qual é o conteúdo correto?

---

**Última atualização:** Novembro 2025













