# 🚀 Configuração Rápida - OAuth2 Gmail

## ✅ O que foi configurado

1. ✅ Backend OAuth2 criado
2. ✅ Script de autenticação criado  
3. ✅ Bibliotecas instaladas

## 📋 Próximos Passos

### 1. Obter Credenciais do Google Cloud Console

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto (ou selecione existente)
3. Ative a Gmail API:
   - Vá em "APIs & Services" > "Library"
   - Procure "Gmail API" e clique em "Enable"
4. Crie credenciais OAuth2:
   - Vá em "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "OAuth client ID"
   - Tipo: "Desktop app"
   - Nome: "MONPEC Gmail"
   - Clique em "Create"
5. Baixe o JSON e salve como `gmail_credentials.json` na raiz do projeto

### 2. Executar Script de Autenticação

```bash
python autenticar_gmail.py
```

Este script vai:
- Abrir seu navegador
- Pedir permissão para acessar l.moncaosilva@gmail.com
- Salvar o token em `gmail_token.json`

### 3. Configurar .env

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

### 4. Reiniciar Servidor

Reinicie o servidor Django para aplicar as mudanças.

## 🎉 Pronto!

Agora você pode criar convites de cotação e os emails serão enviados automaticamente usando OAuth2!

## 📖 Documentação Completa

Veja `COMO_AUTENTICAR_GMAIL_OAUTH2.md` para instruções detalhadas.



































