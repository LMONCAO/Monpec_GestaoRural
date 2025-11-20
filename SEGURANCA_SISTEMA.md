# 🔒 Mecanismos de Segurança do Sistema MONPEC

Este documento descreve todas as medidas de segurança implementadas no sistema para proteger contra acessos não autorizados e ataques.

## 🛡️ Medidas de Segurança Implementadas

### 1. **Validação de Senha Forte**

O sistema exige senhas que atendam aos seguintes critérios:

- ✅ **Mínimo de 12 caracteres**
- ✅ **Pelo menos 1 letra maiúscula**
- ✅ **Pelo menos 1 letra minúscula**
- ✅ **Pelo menos 1 número**
- ✅ **Pelo menos 1 caractere especial** (!@#$%^&*...)
- ✅ **Não pode ser uma senha comum** (123456, password, admin, etc)
- ✅ **Não pode ter caracteres repetidos em sequência** (aaaa, 1111)
- ✅ **Não pode conter sequências comuns** (123, abc, qwe)

**Senhas bloqueadas automaticamente:**
- 123456, 123456789, password, admin, senha, qwerty, etc.

### 2. **Bloqueio por Tentativas de Login**

- ⚠️ **Limite:** 5 tentativas falhas em 15 minutos
- 🔒 **Bloqueio:** Usuário e IP são bloqueados por 15 minutos
- 📊 **Rastreamento:** Tentativas são rastreadas por usuário e por IP
- ✅ **Limpeza automática:** Tentativas são limpas após login bem-sucedido

### 3. **Proteção contra Usuários Padrão**

O sistema identifica e desabilita automaticamente usuários padrão perigosos:

**Usuários bloqueados:**
- admin, administrator, root, test, teste, demo, guest, user, usuario, default

**Como verificar:**
```bash
python manage.py verificar_seguranca
```

**Para desabilitar automaticamente:**
```bash
python manage.py verificar_seguranca --corrigir --desabilitar-padrao
```

### 4. **Rate Limiting**

- 🚫 **Limite:** 20 requisições por minuto por IP
- 🎯 **Aplicado em:** Páginas de login e admin
- ⏱️ **Tempo de bloqueio:** 1 minuto

### 5. **Headers de Segurança HTTP**

O sistema adiciona automaticamente os seguintes headers:

- `X-Frame-Options: DENY` - Previne clickjacking
- `X-Content-Type-Options: nosniff` - Previne MIME type sniffing
- `X-XSS-Protection: 1; mode=block` - Proteção XSS
- `Referrer-Policy: strict-origin-when-cross-origin` - Controle de referrer

### 6. **Logging de Segurança**

Todas as tentativas de login são registradas:

- ✅ Login bem-sucedido (usuário + IP)
- ⚠️ Tentativas falhas (usuário + IP + contador)
- 🔒 Bloqueios por tentativas excessivas

## 📋 Comandos de Verificação

### Verificar Problemas de Segurança

```bash
python manage.py verificar_seguranca
```

Este comando verifica:
- Usuários padrão perigosos
- Usuários sem senha
- Superusuários
- Senhas fracas

### Corrigir Problemas Automaticamente

```bash
python manage.py verificar_seguranca --corrigir --desabilitar-padrao
```

Este comando:
- Desabilita usuários padrão perigosos
- Identifica outros problemas de segurança

## ⚠️ Ações Obrigatórias Após Deploy

### 1. **Remover/Desabilitar Usuários Padrão**

Execute imediatamente após o deploy:

```bash
python manage.py verificar_seguranca --corrigir --desabilitar-padrao
```

### 2. **Alterar Senha do Admin (se existir)**

Se você tiver um usuário admin, altere a senha imediatamente:

```bash
python manage.py changepassword admin
```

**OU crie um novo superusuário seguro:**

```bash
python manage.py createsuperuser
```

**Requisitos para o superusuário:**
- Nome de usuário único (não "admin" ou "administrator")
- Email válido
- Senha forte (mínimo 12 caracteres)

### 3. **Verificar SECRET_KEY**

Certifique-se de que o `SECRET_KEY` no `settings.py` não é o padrão:

```python
# ❌ NUNCA USE:
SECRET_KEY = 'django-insecure-your-secret-key-here'

# ✅ USE variável de ambiente:
SECRET_KEY = os.getenv('SECRET_KEY', 'gere-uma-chave-segura-aqui')
```

**Gerar uma nova SECRET_KEY:**
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 4. **Configurar ALLOWED_HOSTS**

Em produção, configure apenas os domínios permitidos:

```python
# ❌ NUNCA USE EM PRODUÇÃO:
ALLOWED_HOSTS = ['*']

# ✅ USE:
ALLOWED_HOSTS = [
    'monpec.com.br',
    'www.monpec.com.br',
]
```

### 5. **Desabilitar DEBUG em Produção**

```python
# ❌ NUNCA EM PRODUÇÃO:
DEBUG = True

# ✅ EM PRODUÇÃO:
DEBUG = False
```

## 🔐 Boas Práticas de Segurança

### Para Administradores:

1. ✅ **Use senhas únicas e fortes** para cada conta
2. ✅ **Nunca compartilhe credenciais** por email ou mensagem
3. ✅ **Altere senhas regularmente** (a cada 90 dias)
4. ✅ **Use autenticação de dois fatores** quando disponível
5. ✅ **Monitore logs de segurança** regularmente

### Para Desenvolvedores:

1. ✅ **Nunca commite SECRET_KEY** no Git
2. ✅ **Use variáveis de ambiente** para dados sensíveis
3. ✅ **Mantenha Django atualizado** (correções de segurança)
4. ✅ **Revise logs de segurança** após cada deploy
5. ✅ **Teste medidas de segurança** regularmente

## 🚨 Alertas e Monitoramento

O sistema registra automaticamente:

- Tentativas de login falhas
- Bloqueios por rate limiting
- Tentativas de acesso a contas desabilitadas
- Acessos de IPs suspeitos

**Verificar logs:**
```bash
# Logs do Django
tail -f logs/django.log

# Ou no console Python
python manage.py shell
>>> from django.contrib.auth.models import User
>>> # Verificar últimos acessos
```

## 📞 Suporte

Se você encontrar problemas de segurança ou suspeitar de acesso não autorizado:

1. Execute `python manage.py verificar_seguranca`
2. Revise os logs do sistema
3. Altere todas as senhas imediatamente
4. Desabilite contas suspeitas
5. Entre em contato com o administrador do sistema

---

**Última atualização:** Dezembro 2025  
**Versão:** 1.0







