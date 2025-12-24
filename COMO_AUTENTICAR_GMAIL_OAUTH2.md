# 🔐 Como Configurar Autenticação OAuth2 do Google para Gmail

Este guia mostra como configurar o envio de emails usando OAuth2 do Google, sem precisar de senha de app.

## 📋 Pré-requisitos

1. Conta Google (l.moncaosilva@gmail.com)
2. Acesso ao Google Cloud Console

## 🚀 Passo a Passo

### 1. Criar Projeto no Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Clique em "Select a project" > "New Project"
3. Nome do projeto: `MONPEC Gmail` (ou qualquer nome)
4. Clique em "Create"

### 2. Ativar Gmail API

1. No menu lateral, vá em "APIs & Services" > "Library"
2. Procure por "Gmail API"
3. Clique em "Gmail API" e depois em "Enable"

### 3. Criar Credenciais OAuth2

1. Vá em "APIs & Services" > "Credentials"
2. Clique em "Create Credentials" > "OAuth client ID"
3. Se aparecer uma tela de configuração:
   - Nome do app: `MONPEC`
   - Tipo de app: `Desktop app`
   - Clique em "Create"
4. Baixe o arquivo JSON
5. Renomeie o arquivo para `gmail_credentials.json`
6. Mova o arquivo para a raiz do projeto (mesmo nível do `manage.py`)

### 4. Configurar OAuth Consent Screen (se necessário)

Se for solicitado:

1. Vá em "APIs & Services" > "OAuth consent screen"
2. Escolha "External" (para desenvolvimento)
3. Preencha:
   - Nome do app: `MONPEC`
   - Email de suporte: `l.moncaosilva@gmail.com`
4. Clique em "Save and Continue"
5. Em "Scopes", adicione:
   - `https://www.googleapis.com/auth/gmail.send`
6. Continue até finalizar

### 5. Executar Script de Autenticação

```bash
python autenticar_gmail.py
```

Este script vai:
- Abrir seu navegador
- Pedir permissão para acessar sua conta Google
- Salvar o token em `gmail_token.json`

### 6. Configurar arquivo .env

Edite o arquivo `.env` na raiz do projeto:

```env
EMAIL_BACKEND=gestao_rural.backends.email_backend_oauth2.GmailOAuth2Backend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=l.moncaosilva@gmail.com
DEFAULT_FROM_EMAIL=l.moncaosilva@gmail.com
SITE_URL=http://localhost:8000
```

**Nota:** Não precisa preencher `EMAIL_HOST_PASSWORD` quando usar OAuth2.

### 7. Reiniciar Servidor

Reinicie o servidor Django para aplicar as mudanças.

## ✅ Teste

1. Acesse o módulo de Compras
2. Crie um novo convite de cotação
3. O email será enviado automaticamente usando OAuth2!

## 🔄 Renovar Token

O token OAuth2 expira após algum tempo. Se receber erro de autenticação:

1. Execute novamente: `python autenticar_gmail.py`
2. O script vai atualizar o token automaticamente

## 📁 Arquivos Gerados

- `gmail_credentials.json` - Credenciais OAuth2 (baixado do Google Cloud Console)
- `gmail_token.json` - Token de acesso (gerado pelo script)

**⚠️ IMPORTANTE:** 
- Não commite esses arquivos no Git!
- Eles já estão no `.gitignore`
- Mantenha-os seguros

## 🐛 Solução de Problemas

### Erro: "gmail_credentials.json não encontrado"

- Verifique se baixou o arquivo do Google Cloud Console
- Verifique se o arquivo está na raiz do projeto
- Verifique se o nome está correto: `gmail_credentials.json`

### Erro: "Token expirado"

- Execute novamente: `python autenticar_gmail.py`
- O script vai renovar o token automaticamente

### Erro: "Access denied"

- Verifique se ativou a Gmail API no Google Cloud Console
- Verifique se adicionou o escopo correto no OAuth consent screen

## 🎉 Pronto!

Agora você pode enviar emails usando OAuth2 do Google, sem precisar de senha de app!

















