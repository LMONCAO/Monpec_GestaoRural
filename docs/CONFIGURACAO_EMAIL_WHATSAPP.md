# Configuração de E-mail e WhatsApp para Envio de NF-e

Este documento explica como configurar o envio automático de Notas Fiscais Eletrônicas por e-mail e WhatsApp.

## ⚙️ Configuração Padrão

O sistema já vem com um e-mail padrão configurado (`l.moncaosilva@gmail.com`). Este e-mail será usado se nenhuma configuração personalizada for feita.

**Para usar seu próprio e-mail**, siga as instruções abaixo.

## 📧 Configuração de E-mail

### 1. Configuração via Arquivo .env (Recomendado)

Crie ou edite o arquivo `.env` na raiz do projeto e adicione:

```env
# E-mail personalizado (opcional - se não configurar, usará o padrão)
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=seu-email@gmail.com
```

**Nota:** Se você não configurar essas variáveis, o sistema usará o e-mail padrão (`l.moncaosilva@gmail.com`).

### 2. Configuração no Django Settings (Alternativa)

Se preferir, você pode adicionar diretamente no arquivo `settings.py` ou `settings_local.py`:

```python
# Configurações de E-mail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Para Gmail
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-de-app'  # Use senha de app, não a senha normal
DEFAULT_FROM_EMAIL = 'seu-email@gmail.com'
```

### 2. Configuração para Gmail

1. Ative a verificação em duas etapas na sua conta Google
2. Gere uma "Senha de app":
   - Acesse: https://myaccount.google.com/apppasswords
   - Selecione "App" e "Outro (nome personalizado)"
   - Digite "Monpec Gestão Rural"
   - Copie a senha gerada e use em `EMAIL_HOST_PASSWORD`

### 3. Configuração para Outlook/Hotmail

```python
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@outlook.com'
EMAIL_HOST_PASSWORD = 'sua-senha'
DEFAULT_FROM_EMAIL = 'seu-email@outlook.com'
```

### 4. Configuração para Servidor SMTP Personalizado

```python
EMAIL_HOST = 'smtp.seudominio.com.br'
EMAIL_PORT = 587  # ou 465 para SSL
EMAIL_USE_TLS = True  # ou EMAIL_USE_SSL = True para porta 465
EMAIL_HOST_USER = 'noreply@seudominio.com.br'
EMAIL_HOST_PASSWORD = 'sua-senha'
DEFAULT_FROM_EMAIL = 'noreply@seudominio.com.br'
```

### 5. Teste de Configuração

Para testar se o e-mail está configurado corretamente, você pode usar o shell do Django:

```python
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Teste de E-mail',
    'Este é um teste de configuração de e-mail.',
    'seu-email@gmail.com',
    ['destinatario@email.com'],
    fail_silently=False,
)
```

## 📱 Configuração de WhatsApp

### Opção 1: WhatsApp Business API (Recomendado)

O sistema suporta integração com APIs de WhatsApp Business como:
- Evolution API
- Twilio WhatsApp API
- WhatsApp Business Cloud API
- Outras APIs compatíveis

#### Configuração no Settings

Adicione no arquivo `settings.py`:

```python
# Configurações do WhatsApp API
WHATSAPP_API_URL = 'https://api.evolutionapi.com'  # URL da sua API
WHATSAPP_API_TOKEN = 'seu-token-de-autenticacao'
WHATSAPP_API_INSTANCE = 'sua-instancia'  # Opcional, dependendo da API
```

#### Exemplo com Evolution API

1. Instale e configure a Evolution API
2. Obtenha o token de autenticação
3. Configure as variáveis acima

#### Exemplo com Twilio

```python
WHATSAPP_API_URL = 'https://api.twilio.com/2010-04-01/Accounts'
WHATSAPP_API_TOKEN = 'seu-account-sid:seu-auth-token'
```

**Nota:** A implementação atual espera endpoints `/send-message` e `/send-file`. Se sua API usar endpoints diferentes, será necessário ajustar o código em `gestao_rural/views_vendas.py`.

### Opção 2: WhatsApp Web (Fallback Automático)

Se a API do WhatsApp não estiver configurada, o sistema automaticamente usará o link do WhatsApp Web. Neste caso:

1. O sistema gera um link do WhatsApp Web com a mensagem pré-formatada
2. O usuário clica no link e o WhatsApp Web abre
3. O usuário precisa anexar manualmente os arquivos PDF e XML

**Vantagens:**
- Não requer configuração adicional
- Funciona imediatamente
- Não precisa de API externa

**Desvantagens:**
- Requer ação manual do usuário
- Arquivos não são anexados automaticamente

## 🔧 Instalação de Dependências

Se você for usar a API do WhatsApp, pode precisar instalar a biblioteca `requests`:

```bash
pip install requests
```

## 📝 Variáveis de Ambiente (Recomendado)

Para maior segurança, use variáveis de ambiente ao invés de colocar credenciais diretamente no código:

### No arquivo `.env`:

```env
# E-mail
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app
DEFAULT_FROM_EMAIL=seu-email@gmail.com

# WhatsApp (opcional)
WHATSAPP_API_URL=https://api.evolutionapi.com
WHATSAPP_API_TOKEN=seu-token
WHATSAPP_API_INSTANCE=sua-instancia
```

### No arquivo `settings.py`:

```python
import os
from decouple import config  # pip install python-decouple

# E-mail
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# WhatsApp
WHATSAPP_API_URL = config('WHATSAPP_API_URL', default=None)
WHATSAPP_API_TOKEN = config('WHATSAPP_API_TOKEN', default=None)
WHATSAPP_API_INSTANCE = config('WHATSAPP_API_INSTANCE', default=None)
```

## 🧪 Testando as Configurações

### Teste de E-mail

1. Acesse a emissão de uma NF-e
2. Complete todas as etapas
3. Após a emissão, clique em "Enviar por E-mail"
4. Digite um e-mail de teste
5. Verifique se o e-mail foi recebido com os anexos (PDF e XML)

### Teste de WhatsApp

1. Acesse a emissão de uma NF-e
2. Complete todas as etapas
3. Após a emissão, clique em "Enviar por WhatsApp"
4. Digite um número de telefone de teste
5. Se a API estiver configurada, a mensagem será enviada automaticamente
6. Se não estiver configurada, um link do WhatsApp Web será gerado

## ⚠️ Troubleshooting

### E-mail não está sendo enviado

1. **Verifique as configurações SMTP** - Certifique-se de que todas as configurações estão corretas
2. **Verifique as credenciais** - Use senha de app para Gmail, não a senha normal
3. **Verifique o firewall** - Certifique-se de que a porta SMTP não está bloqueada
4. **Verifique os logs** - Os erros são registrados no log do Django
5. **Teste com telnet** - Teste a conexão SMTP: `telnet smtp.gmail.com 587`

### WhatsApp não está funcionando

1. **Verifique a API** - Certifique-se de que a API do WhatsApp está configurada e funcionando
2. **Verifique o token** - O token de autenticação deve estar correto
3. **Verifique os endpoints** - A API deve ter os endpoints `/send-message` e `/send-file`
4. **Verifique os logs** - Os erros são registrados no log do Django
5. **Use WhatsApp Web** - Se a API não funcionar, o sistema automaticamente usa o link do WhatsApp Web

## 📚 Recursos Adicionais

- [Documentação Django Email](https://docs.djangoproject.com/en/stable/topics/email/)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
- [Evolution API Documentation](https://doc.evolution-api.com/)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)

## 🔒 Segurança

- **Nunca commite credenciais no Git** - Use variáveis de ambiente ou arquivos `.env` que estejam no `.gitignore`
- **Use senhas de app** - Para Gmail, sempre use senhas de app, nunca a senha principal
- **Rotacione tokens** - Periodicamente, altere os tokens de API do WhatsApp
- **Monitore logs** - Verifique regularmente os logs para detectar tentativas de acesso não autorizado

