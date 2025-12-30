# 📋 Instruções para Criar Admin no Cloud Shell

## ⚠️ IMPORTANTE: Você tentou executar código Python no bash!

O código Python precisa ser executado **dentro do Python**, não no bash.

## ✅ SOLUÇÃO CORRETA

### Opção 1: Executar Script Python (MAIS FÁCIL)

1. No Cloud Shell, baixe o arquivo `criar_admin_cloud_shell.py` ou crie-o:

```bash
# Criar o arquivo
cat > criar_admin_cloud_shell.py << 'EOF'
#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
sys.path.insert(0, '/app')

django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'admin'
password = 'L6171r12@@'
email = 'admin@monpec.com.br'

try:
    user = User.objects.get(username=username)
    print(f"✅ Usuário encontrado: {user.username}")
except User.DoesNotExist:
    user = User.objects.create_user(username=username, email=email, password=password)
    print(f"✅ Usuário criado: {user.username}")

user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.email = email
user.save()

print(f"✅ Admin configurado! Username: {username}, Password: {password}")
EOF
```

2. Execute via Cloud Run Job:

```bash
gcloud run jobs create monpec-admin-final \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
  --command python \
  --args criar_admin_cloud_shell.py \
  --max-retries 1 \
  --task-timeout 300

gcloud run jobs execute monpec-admin-final --region us-central1 --wait
```

### Opção 2: Usar Django Shell (INTERATIVO)

1. Execute o Django shell via Cloud Run:

```bash
# Criar job para shell interativo
gcloud run jobs create monpec-shell \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
  --command python \
  --args manage.py,shell \
  --max-retries 1 \
  --task-timeout 300
```

2. **MAS** o shell interativo não funciona bem em jobs. Melhor usar a Opção 1.

### Opção 3: Executar Código Python Diretamente (SEM SHELL)

Execute este comando completo de uma vez:

```bash
gcloud run jobs create monpec-admin-oneline \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
  --command python \
  --args -c,"import os,django;os.environ.setdefault('DJANGO_SETTINGS_MODULE','sistema_rural.settings_gcp');django.setup();from django.contrib.auth import get_user_model;User=get_user_model();u,created=User.objects.get_or_create(username='admin',defaults={'email':'admin@monpec.com.br'});u.set_password('L6171r12@@');u.is_staff=u.is_superuser=u.is_active=True;u.save();print('✅ Admin criado!')" \
  --max-retries 1 \
  --task-timeout 300

gcloud run jobs execute monpec-admin-oneline --region us-central1 --wait
```

## 🔍 Verificar se Funcionou

Depois de executar, verifique os logs:

```bash
gcloud logging read "resource.type=cloud_run_job" --limit 20 --format="table(timestamp,textPayload)" --project monpec-sistema-rural
```

## 📝 Credenciais

- **URL**: https://monpec-fzzfjppzva-uc.a.run.app
- **Usuário**: admin
- **Senha**: L6171r12@@

## ⚠️ O QUE NÃO FAZER

❌ **NÃO** execute código Python diretamente no bash (como você fez)
❌ **NÃO** cole código Python no terminal bash
✅ **SIM** execute scripts Python com `python script.py`
✅ **SIM** use Cloud Run Jobs para executar código Python










































