# 🔧 Resolver Verificação Google Search Console

## ⚠️ Problema

O Google Search Console está tentando acessar o arquivo em `monpec.com.br`, mas o domínio ainda não está mapeado. O arquivo só está acessível em `monpec-29862706245.us-central1.run.app`.

---

## ✅ Solução: Verificar com URL do Cloud Run

### Passo 1: Adicionar Propriedade com URL do Cloud Run

1. **Acesse:** https://search.google.com/search-console
2. **Clique em:** "Adicionar propriedade"
3. **Escolha:** "Prefixo de URL"
4. **Digite:** `https://monpec-29862706245.us-central1.run.app`
5. **Clique em:** "Continuar"

### Passo 2: Verificar com Arquivo HTML

1. **Escolha:** "Arquivo HTML"
2. **Baixe o arquivo** que o Google fornecer (ou anote o nome)
3. **O arquivo já está configurado!** Acesse:
   ```
   https://monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html
   ```
4. **Clique em:** "Verificar"

---

## 🔄 Depois de Mapear o Domínio

Quando você mapear `monpec.com.br` no Cloud Run:

1. **Adicione nova propriedade** no Google Search Console
2. **URL:** `https://monpec.com.br`
3. **Use o mesmo arquivo** de verificação
4. **Verifique novamente**

---

## 📋 Alternativa: Usar Meta Tag

Se preferir usar meta tag em vez de arquivo HTML:

1. **Escolha:** "Tag HTML" no Google Search Console
2. **Copie a meta tag** fornecida
3. **Adicione ao template** `templates/base.html`
4. **Faça deploy novamente**
5. **Verifique**

---

## 🎯 Resumo

**Agora:**
- ✅ Verifique usando: `https://monpec-29862706245.us-central1.run.app`
- ✅ Use o arquivo: `/google40933139f3b0d469.html`

**Depois (quando mapear domínio):**
- ✅ Adicione propriedade: `https://monpec.com.br`
- ✅ Use o mesmo arquivo de verificação

---

**Próximo passo:** Adicione a propriedade usando a URL do Cloud Run!













