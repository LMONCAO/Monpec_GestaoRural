# 🔄 Ordem Correta: Verificar e Mapear Domínio

## ⚠️ Situação Atual

- ✅ Arquivo de verificação configurado: `google40933139f3b0d469.html`
- ✅ Funcionando em: `monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html`
- ❌ Domínio `monpec.com.br` ainda não mapeado no Cloud Run
- ❌ Google Search Console precisa do arquivo em `monpec.com.br`

---

## 🎯 Solução: Duas Opções

### Opção 1: Verificar Primeiro com URL do Cloud Run (Recomendado)

**Vantagem:** Você pode verificar agora, sem esperar mapear o domínio.

1. **No Google Search Console:**
   - Adicione propriedade: `https://monpec-29862706245.us-central1.run.app`
   - Use o arquivo: `/google40933139f3b0d469.html`
   - Verifique ✅

2. **Depois, quando mapear `monpec.com.br`:**
   - Adicione nova propriedade: `https://monpec.com.br`
   - Use o mesmo arquivo
   - Verifique novamente ✅

---

### Opção 2: Mapear Domínio Primeiro (Mais Completo)

**Vantagem:** Tudo funcionando direto com `monpec.com.br`.

#### Passo 1: Verificar Domínio no Google Cloud

1. **Acesse:** https://console.cloud.google.com/run/domains
2. **Clique em:** "Verify a new domain"
3. **Digite:** `monpec.com.br`
4. **Escolha:** "HTML tag" (meta tag)
5. **Copie a meta tag** fornecida
6. **Adicione ao template** `templates/base.html`
7. **Faça deploy**
8. **Volte ao console** e clique em "Verify"

#### Passo 2: Mapear Domínio no Cloud Run

Depois de verificado, execute no Cloud Shell:

```bash
gcloud beta run domain-mappings create --service monpec --domain monpec.com.br --region us-central1
gcloud beta run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1
```

#### Passo 3: Configurar DNS

O comando acima vai retornar instruções de DNS. Configure no seu provedor.

#### Passo 4: Aguardar Propagação DNS

⏳ Pode levar de 15 minutos a 48 horas

#### Passo 5: Verificar no Google Search Console

Agora que `monpec.com.br` está mapeado:

1. **Acesse:** https://search.google.com/search-console
2. **Adicione propriedade:** `https://monpec.com.br`
3. **Use o arquivo:** `/google40933139f3b0d469.html`
4. **Verifique** ✅

---

## 📋 Resumo das Opções

### Opção 1 (Rápida):
1. ✅ Verificar com URL Cloud Run agora
2. ⏳ Mapear domínio depois
3. ✅ Adicionar propriedade `monpec.com.br` depois

### Opção 2 (Completa):
1. ⏳ Verificar domínio no Google Cloud
2. ⏳ Mapear domínio no Cloud Run
3. ⏳ Configurar DNS
4. ⏳ Aguardar propagação
5. ✅ Verificar no Google Search Console

---

## 🚀 Recomendação

**Use a Opção 1** para verificar agora e começar a usar o Google Search Console. Depois, quando mapear o domínio, adicione `monpec.com.br` como propriedade adicional.

---

**Próximo passo:** Escolha uma opção e siga os passos!














