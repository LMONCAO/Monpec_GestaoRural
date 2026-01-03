# 🚀 Criar Admin Agora - Comandos Rápidos

## ⚡ Comando Rápido (Cloud Shell)

Execute este comando para criar/garantir o admin:

```bash
gcloud run jobs execute garantir-admin \
  --region=us-central1 \
  --args python,manage.py,garantir_admin
```

**OU** execute diretamente:

```bash
gcloud run jobs execute criar-admin \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model,authenticate;User=get_user_model();user,created=User.objects.get_or_create(username='admin',defaults={'email':'admin@monpec.com.br','is_staff':True,'is_superuser':True,'is_active':True});user.set_password('L6171r12@@');user.save();auth_test=authenticate(username='admin',password='L6171r12@@');print('✅ Admin criado!' if auth_test else '❌ Falha na autenticação')"
```

## 📋 Credenciais para Login

Após criar o admin, use:

- **Username:** `admin` (NÃO use o email!)
- **OU Email:** `admin@monpec.com.br`
- **Senha:** `L6171r12@@`

## 🔍 Verificar se Admin Existe

Para verificar se o admin já existe:

```bash
gcloud run jobs execute verificar-admin \
  --region=us-central1 \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model;User=get_user_model();admin=User.objects.filter(username='admin').first();print(f'✅ Admin existe: {admin.username} ({admin.email})' if admin else '❌ Admin não existe')"
```

## ⚠️ Importante

- Use **username** `admin` no login, não o email completo
- Se usar email, use `admin@monpec.com.br` (com @)
- A senha é: `L6171r12@@`


