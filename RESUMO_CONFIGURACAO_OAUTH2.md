# ✅ Configuração OAuth2 - STATUS

## 🎉 O QUE JÁ ESTÁ PRONTO (100% automático)

- ✅ Backend OAuth2 criado (`gestao_rural/backends/email_backend_oauth2.py`)
- ✅ Script de autenticação (`autenticar_gmail.py`)
- ✅ Bibliotecas instaladas (google-auth, google-auth-oauthlib)
- ✅ Arquivo `.env` configurado com seu email: `l.moncaosilva@gmail.com`
- ✅ `.gitignore` atualizado (credenciais não serão commitadas)

---

## 📋 O QUE VOCÊ PRECISA FAZER (única parte manual - 5 minutos)

Como precisa fazer login no Google e autorizar, isso precisa ser feito por você. Mas está bem simples:

### 🚀 Método Rápido (recomendado):

Execute este script que abre tudo automaticamente:

```bash
python fazer_configuracao_oauth2.py
```

Ele vai abrir as páginas certas do Google Cloud Console e te guiar passo a passo.

---

### 📝 Método Manual (se preferir):

1. **Abra:** https://console.cloud.google.com/

2. **Crie projeto:**
   - Clique "Select a project" > "New Project"
   - Nome: `MONPEC`
   - Clique "Create"

3. **Ative Gmail API:**
   - Menu: "APIs & Services" > "Library"
   - Procure: `Gmail API`
   - Clique "ENABLE"

4. **Configure OAuth Consent Screen:**
   - Menu: "APIs & Services" > "OAuth consent screen"
   - Tipo: "External" > "CREATE"
   - App name: `MONPEC`
   - Email: `l.moncaosilva@gmail.com`
   - **Scopes:** adicione `.../auth/gmail.send`
   - **Test users:** adicione `l.moncaosilva@gmail.com`

5. **Crie credenciais:**
   - Menu: "APIs & Services" > "Credentials"
   - "CREATE CREDENTIALS" > "OAuth client ID"
   - Tipo: **"Desktop app"**
   - Nome: `MONPEC Gmail`
   - Clique "CREATE"
   - **Baixe o JSON** (ícone de download)
   - Salve como: `gmail_credentials.json`
   - Coloque na raiz do projeto (mesma pasta do `manage.py`)

6. **Execute autenticação:**
   ```bash
   python autenticar_gmail.py
   ```
   - Abrirá o navegador
   - Faça login com `l.moncaosilva@gmail.com`
   - Clique "Allow" para autorizar

7. **Pronto!** Reinicie o servidor Django.

---

## 📁 Arquivos Criados

- `gestao_rural/backends/email_backend_oauth2.py` - Backend OAuth2
- `autenticar_gmail.py` - Script de autenticação
- `fazer_configuracao_oauth2.py` - Script guiado (abre páginas automaticamente)
- `PASSO_A_PASSO_OAUTH2.md` - Guia detalhado
- `COMO_AUTENTICAR_GMAIL_OAUTH2.md` - Documentação completa
- `LEIA_ME_PRIMEIRO_OAUTH2.txt` - Resumo rápido

---

## ⚙️ Configuração do .env

O arquivo `.env` já está configurado assim:

```env
EMAIL_BACKEND=gestao_rural.backends.email_backend_oauth2.GmailOAuth2Backend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=l.moncaosilva@gmail.com
DEFAULT_FROM_EMAIL=l.moncaosilva@gmail.com
SITE_URL=http://localhost:8000
```

---

## ✅ Checklist Final

Após fazer os passos acima, verifique:

- [ ] `gmail_credentials.json` existe na raiz do projeto
- [ ] `gmail_token.json` foi criado (pelo script de autenticação)
- [ ] Servidor Django reiniciado
- [ ] Teste criando um convite de cotação

---

## 🆘 Problemas?

**"gmail_credentials.json não encontrado"**
→ Verifique se baixou e colocou na raiz do projeto

**"Token expirado"**  
→ Execute: `python autenticar_gmail.py` novamente

**Erro de autenticação**  
→ Verifique se adicionou seu email como "test user" no OAuth consent screen

---

## 🎯 Próximo Passo

Execute agora:
```bash
python fazer_configuracao_oauth2.py
```

Ou siga o guia: `PASSO_A_PASSO_OAUTH2.md`

















