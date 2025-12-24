# 🚀 Passo a Passo Simples - Configurar OAuth2 Gmail

## ⚡ Rápido (5 minutos)

### 1️⃣ Abra este link no navegador:
**https://console.cloud.google.com/**

### 2️⃣ Crie um projeto:
- Clique em "Select a project" (topo)
- Clique em "New Project"
- Nome: `MONPEC`
- Clique em "Create"

### 3️⃣ Ative Gmail API:
- Menu lateral: "APIs & Services" → "Library"
- Procure: `Gmail API`
- Clique em "Gmail API"
- Clique em "ENABLE" (botão azul)

### 4️⃣ Configure OAuth Consent Screen:
- Menu lateral: "APIs & Services" → "OAuth consent screen"
- Escolha: "External" → "CREATE"
- Preencha:
  - App name: `MONPEC`
  - User support email: `l.moncaosilva@gmail.com`
  - Developer contact: `l.moncaosilva@gmail.com`
- Clique em "SAVE AND CONTINUE"
- Em "Scopes" → "ADD OR REMOVE SCOPES"
  - Procure: `gmail.send`
  - Selecione: `.../auth/gmail.send`
  - Clique em "UPDATE" → "SAVE AND CONTINUE"
- Em "Test users" → "ADD USERS"
  - Adicione: `l.moncaosilva@gmail.com`
  - Clique em "ADD" → "SAVE AND CONTINUE" (vá até finalizar)

### 5️⃣ Crie credenciais:
- Menu lateral: "APIs & Services" → "Credentials"
- Clique em "CREATE CREDENTIALS" → "OAuth client ID"
- Application type: **"Desktop app"**
- Name: `MONPEC Gmail`
- Clique em "CREATE"

### 6️⃣ Baixe o arquivo:
- Clique no ícone de download (⭣) ao lado das credenciais
- Salve como: `gmail_credentials.json`
- Mova para a raiz do projeto (mesma pasta do `manage.py`)

### 7️⃣ Execute o script:

No terminal/PowerShell, execute:

```bash
python autenticar_gmail.py
```

- Vai abrir o navegador
- Faça login com: `l.moncaosilva@gmail.com`
- Clique em "Allow" para autorizar
- O token será salvo automaticamente

### 8️⃣ Pronto! 

O arquivo `.env` já está configurado. Reinicie o servidor Django e teste criando um convite de cotação!

---

## ✅ Checklist

- [ ] Projeto criado no Google Cloud
- [ ] Gmail API ativada
- [ ] OAuth consent screen configurado
- [ ] Credenciais OAuth2 criadas (Desktop app)
- [ ] Arquivo `gmail_credentials.json` baixado e colocado na raiz
- [ ] Script `autenticar_gmail.py` executado com sucesso
- [ ] Token `gmail_token.json` gerado
- [ ] Servidor Django reiniciado
- [ ] Testado criando um convite de cotação

---

## 🆘 Problemas?

**"gmail_credentials.json não encontrado"**
→ Verifique se baixou o arquivo e colocou na raiz do projeto

**"Token expirado"**
→ Execute novamente: `python autenticar_gmail.py`

**Erro de autenticação**
→ Verifique se adicionou `l.moncaosilva@gmail.com` como test user no OAuth consent screen
















