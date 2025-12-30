# 📧 Como Configurar Envio Real de E-mails no MONPEC

## 🔍 Situação Atual

Por padrão, o sistema está configurado para usar `console.EmailBackend`, que apenas **imprime os e-mails no terminal** ao invés de enviá-los de verdade. Este guia mostra como configurar o envio real de e-mails.

## ⚙️ Método 1: Configuração via Variáveis de Ambiente (Recomendado)

### Passo 1: Criar arquivo `.env` na raiz do projeto

Crie um arquivo chamado `.env` na raiz do projeto (mesmo nível do `manage.py`) com o seguinte conteúdo:

```env
# Configuração de E-mail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=noreply@monpec.com.br
SITE_URL=http://localhost:8000
```

### Passo 2: Configurar para diferentes provedores

#### 📮 Gmail

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app-gmail
DEFAULT_FROM_EMAIL=seu-email@gmail.com
```

**⚠️ IMPORTANTE para Gmail:**
1. Você precisa usar uma **Senha de App** (não sua senha normal)
2. Ative a verificação em duas etapas na sua conta Google
3. Vá em: [Conta Google > Segurança > Senhas de app](https://myaccount.google.com/apppasswords)
4. Gere uma senha de app e use ela no `EMAIL_HOST_PASSWORD`

#### 📧 Outlook/Hotmail

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@outlook.com
EMAIL_HOST_PASSWORD=sua-senha
DEFAULT_FROM_EMAIL=seu-email@outlook.com
```

#### 📬 Yahoo Mail

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@yahoo.com
EMAIL_HOST_PASSWORD=sua-senha-de-app-yahoo
DEFAULT_FROM_EMAIL=seu-email@yahoo.com
```

#### 🏢 Servidor SMTP Personalizado

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=mail.seudominio.com.br
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@seudominio.com.br
EMAIL_HOST_PASSWORD=sua-senha
DEFAULT_FROM_EMAIL=noreply@seudominio.com.br
```

### Passo 3: Instalar python-decouple (se ainda não tiver)

O sistema já está configurado para ler variáveis de ambiente, mas se precisar instalar:

```bash
pip install python-decouple
```

### Passo 4: Reiniciar o servidor

Após configurar o `.env`, reinicie o servidor Django:

```bash
# Windows (PowerShell)
python manage.py runserver

# Linux/Mac
python3 manage.py runserver
```

---

## ⚙️ Método 2: Configuração Direta no settings.py

Se preferir não usar arquivo `.env`, você pode editar diretamente o arquivo `sistema_rural/settings.py`:

### Localizar a seção de e-mail (linha ~180)

```python
# Configuração de E-mail (para recuperação de senha)
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@monpec.com.br')
SERVER_EMAIL = DEFAULT_FROM_EMAIL
```

### Alterar para valores fixos (exemplo Gmail):

```python
# Configuração de E-mail (para recuperação de senha)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-de-app-gmail'
DEFAULT_FROM_EMAIL = 'seu-email@gmail.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL
```

**⚠️ ATENÇÃO:** Não commite senhas no código! Use variáveis de ambiente.

---

## 🧪 Testar o Envio de E-mail

### Opção 1: Via Shell do Django

```bash
python manage.py shell
```

Depois execute:

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Teste de E-mail MONPEC',
    'Este é um e-mail de teste do sistema MONPEC.',
    settings.DEFAULT_FROM_EMAIL,
    ['seu-email-de-teste@gmail.com'],
    fail_silently=False,
)
```

### Opção 2: Via Interface Web

1. Acesse: `http://localhost:8000/recuperar-senha/`
2. Digite um e-mail cadastrado no sistema
3. Verifique se o e-mail chegou (incluindo pasta de spam)

---

## 🔒 Segurança e Boas Práticas

### 1. Nunca commite senhas no código

Adicione `.env` ao `.gitignore`:

```gitignore
# Arquivo de configuração local
.env
```

### 2. Use Senhas de App para Gmail

- Não use sua senha normal do Gmail
- Gere uma Senha de App específica
- Revogue senhas de app antigas regularmente

### 3. Para Produção

Configure variáveis de ambiente no servidor:

**Linux/Ubuntu:**
```bash
export EMAIL_HOST_USER=seu-email@gmail.com
export EMAIL_HOST_PASSWORD=sua-senha-de-app
```

**Windows (PowerShell):**
```powershell
$env:EMAIL_HOST_USER="seu-email@gmail.com"
$env:EMAIL_HOST_PASSWORD="sua-senha-de-app"
```

**Docker:**
```yaml
environment:
  - EMAIL_HOST_USER=seu-email@gmail.com
  - EMAIL_HOST_PASSWORD=sua-senha-de-app
```

---

## 🐛 Solução de Problemas

### Erro: "SMTPAuthenticationError"

**Causa:** Credenciais incorretas ou senha de app não configurada (Gmail)

**Solução:**
- Verifique se está usando Senha de App no Gmail
- Confirme que o e-mail e senha estão corretos
- Verifique se a verificação em duas etapas está ativada (Gmail)

### Erro: "Connection refused"

**Causa:** Porta bloqueada ou servidor SMTP incorreto

**Solução:**
- Verifique se a porta está correta (587 para TLS, 465 para SSL)
- Teste com `EMAIL_USE_SSL=True` e porta 465
- Verifique firewall/antivírus

### E-mails não chegam

**Causa:** E-mails indo para spam ou configuração incorreta

**Solução:**
- Verifique a pasta de spam
- Confirme que `DEFAULT_FROM_EMAIL` está correto
- Verifique logs do servidor Django
- Teste com outro provedor de e-mail

### Verificar logs

Ative logs detalhados no `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## 📋 Checklist de Configuração

- [ ] Arquivo `.env` criado na raiz do projeto
- [ ] Variáveis de e-mail configuradas no `.env`
- [ ] Senha de App gerada (se usar Gmail)
- [ ] `.env` adicionado ao `.gitignore`
- [ ] Servidor Django reiniciado
- [ ] E-mail de teste enviado com sucesso
- [ ] E-mail recebido na caixa de entrada (ou spam)

---

## 🚀 Configuração Rápida (Gmail)

1. **Criar arquivo `.env`** na raiz:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=seu-email@gmail.com
SITE_URL=http://localhost:8000
```

2. **Gerar Senha de App no Google:**
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "E-mail" e "Outro (nome personalizado)"
   - Digite "MONPEC" e clique em "Gerar"
   - Copie a senha gerada (16 caracteres com espaços)
   - Cole no `EMAIL_HOST_PASSWORD` (pode remover os espaços)

3. **Reiniciar servidor:**
```bash
python manage.py runserver
```

4. **Testar:**
   - Acesse: http://localhost:8000/recuperar-senha/
   - Digite um e-mail cadastrado
   - Verifique sua caixa de entrada!

---

## 📞 Suporte

Se tiver problemas, verifique:
1. Logs do Django no terminal
2. Configurações do provedor de e-mail
3. Firewall/antivírus bloqueando conexões SMTP
4. Senha de App correta (Gmail)

---

**✅ Pronto! Agora seus e-mails serão enviados de verdade!**


