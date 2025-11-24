# ✅ Guia: Verificar Domínio no Google Search Console

## 🎯 Objetivo
Verificar a propriedade do domínio `monpec.com.br` no Google Search Console para poder configurar o domínio customizado no Cloud Run.

---

## 📋 Passo a Passo

### Passo 1: Baixar o Arquivo HTML

1. No Google Search Console, você já está vendo a tela de verificação
2. Clique no botão **"google40933139f3b0d469.html"** para baixar o arquivo
3. Salve o arquivo em um local fácil de encontrar (ex: Desktop)

### Passo 2: Verificar o Conteúdo do Arquivo

Abra o arquivo baixado e verifique o conteúdo. Ele deve conter algo como:

```
google-site-verification: google40933139f3b0d469.html
```

**⚠️ IMPORTANTE:** Anote o conteúdo exato do arquivo!

### Passo 3: Atualizar a View no Django

O arquivo já está configurado no projeto! A view `google_search_console_verification` em `gestao_rural/views.py` já está servindo o arquivo.

**Se o conteúdo do arquivo baixado for diferente**, você precisa atualizar a view:

1. Abra: `gestao_rural/views.py`
2. Encontre a função `google_search_console_verification` (linha 23)
3. Atualize o conteúdo para corresponder exatamente ao arquivo baixado

### Passo 4: Fazer Deploy no Cloud Run

Após atualizar (se necessário), faça o deploy:

```powershell
# No Cloud Shell ou PowerShell com gcloud configurado
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
gcloud run deploy monpec `
    --image gcr.io/monpec-sistema-rural/monpec `
    --region us-central1 `
    --platform managed
```

### Passo 5: Verificar se o Arquivo Está Acessível

Após o deploy, teste se o arquivo está acessível:

1. Acesse: **https://monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html**
2. Você deve ver o conteúdo do arquivo de verificação
3. Se funcionar, volte ao Google Search Console e clique em **"VERIFICAR"**

### Passo 6: Verificar no Google Search Console

1. Volte para a tela do Google Search Console
2. Clique no botão **"VERIFICAR"**
3. Aguarde alguns segundos
4. Se tudo estiver correto, você verá uma mensagem de sucesso!

---

## 🔍 Verificação Atual

### Status da Configuração

✅ **Rota configurada:** `sistema_rural/urls.py` linha 39
✅ **View criada:** `gestao_rural/views.py` linha 23
✅ **Arquivo HTML criado:** `google40933139f3b0d469.html` na raiz do projeto

### Testar Localmente (Opcional)

Se quiser testar localmente antes de fazer deploy:

```powershell
# Ativar ambiente virtual (se tiver)
# Executar servidor Django
python manage.py runserver

# Em outro terminal, testar:
# Acesse: http://localhost:8000/google40933139f3b0d469.html
```

---

## 🆘 Problemas Comuns

### Problema 1: "Arquivo não encontrado" (404)

**Solução:**
- Verifique se a rota está configurada em `sistema_rural/urls.py`
- Verifique se a view existe em `gestao_rural/views.py`
- Faça o deploy novamente no Cloud Run

### Problema 2: "Conteúdo incorreto"

**Solução:**
- Abra o arquivo baixado do Google Search Console
- Copie o conteúdo exato
- Atualize a view `google_search_console_verification` em `gestao_rural/views.py`
- Faça o deploy novamente

### Problema 3: "Verificação falhou"

**Solução:**
- Verifique se o arquivo está acessível em: `https://monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html`
- Verifique se o conteúdo corresponde exatamente ao arquivo baixado
- Aguarde alguns minutos e tente novamente

---

## ✅ Checklist

- [ ] Arquivo HTML baixado do Google Search Console
- [ ] Conteúdo do arquivo verificado
- [ ] View atualizada (se necessário) em `gestao_rural/views.py`
- [ ] Deploy realizado no Cloud Run
- [ ] Arquivo acessível em: `https://monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html`
- [ ] Verificação concluída no Google Search Console

---

## 📞 Próximos Passos

Após verificar o domínio no Google Search Console:

1. **Configurar domínio customizado no Cloud Run:**
   - Acesse: https://console.cloud.google.com/run
   - Adicione o domínio customizado `monpec.com.br`
   - Obtenha os registros DNS

2. **Configurar DNS no Registro.br:**
   - Adicione os registros DNS fornecidos pelo Google Cloud
   - Aguarde a propagação (15 min - 2 horas)

3. **Testar o acesso:**
   - Acesse: https://monpec.com.br
   - Verifique se o site carrega corretamente

---

**🎉 Boa sorte com a verificação!**












