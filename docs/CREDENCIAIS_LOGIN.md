# 🔐 Credenciais para Login no Sistema

## ✅ Credenciais do Admin

Após criar o admin (veja comandos abaixo), use:

### Opção 1: Usar Username
- **Campo:** Usuário ou E-mail
- **Valor:** `admin`
- **Senha:** `L6171r12@@`

### Opção 2: Usar Email
- **Campo:** Usuário ou E-mail  
- **Valor:** `admin@monpec.com.br`
- **Senha:** `L6171r12@@`

## 🚀 Criar Admin Agora

Se o admin não existe, execute no **Cloud Shell**:

```bash
gcloud run jobs execute criar-admin \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model,authenticate;User=get_user_model();user,created=User.objects.get_or_create(username='admin',defaults={'email':'admin@monpec.com.br','is_staff':True,'is_superuser':True,'is_active':True});user.set_password('L6171r12@@');user.save();auth_test=authenticate(username='admin',password='L6171r12@@');print('✅ Admin criado! Username: admin, Senha: L6171r12@@' if auth_test else '❌ Falha na autenticação')"
```

## 📝 Resumo

- **Username:** `admin`
- **Email:** `admin@monpec.com.br`
- **Senha:** `L6171r12@@`

**⚠️ IMPORTANTE:** 
- Use `admin` (sem @) no campo de login
- OU use `admin@monpec.com.br` (com @ completo)
- A senha é sempre: `L6171r12@@`


