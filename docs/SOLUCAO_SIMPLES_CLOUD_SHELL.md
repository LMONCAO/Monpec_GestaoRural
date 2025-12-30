# ✅ SOLUÇÃO SIMPLES - Cloud Shell

## 🔴 Problema Identificado

O bash está interpretando o `!` na senha como expansão de histórico, causando erro.

## ✅ SOLUÇÃO CORRIGIDA

### Passo 1: Configurar o Projeto

```bash
gcloud config set project monpec-sistema-rural
```

### Passo 2: Criar o Job (COM ASPAS SIMPLES)

Use **aspas simples** para evitar que o bash interprete caracteres especiais:

```bash
gcloud run jobs create monpec-admin-final \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
  --command python \
  --args -c,'import os,django;os.environ.setdefault("DJANGO_SETTINGS_MODULE","sistema_rural.settings_gcp");django.setup();from django.contrib.auth import get_user_model;User=get_user_model();u,created=User.objects.get_or_create(username="admin",defaults={"email":"admin@monpec.com.br"});u.set_password("L6171r12@@");u.is_staff=u.is_superuser=u.is_active=True;u.save();print("✅ Admin criado!")' \
  --max-retries 1 \
  --task-timeout 300
```

**IMPORTANTE**: Note que usei **aspas simples** `'...'` ao redor do código Python, e **aspas duplas** `"..."` dentro do código Python para a senha.

### Passo 3: Executar o Job

```bash
gcloud run jobs execute monpec-admin-final --region us-central1 --wait
```

## 🔄 Alternativa: Usar Arquivo Python

Se o comando acima ainda der problema, crie um arquivo Python primeiro:

### Passo 1: Criar arquivo Python no Cloud Shell

```bash
cat > criar_admin.py << 'EOF'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
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

print(f"✅ Admin configurado!")
print(f"Username: {username}")
print(f"Password: {password}")
EOF
```

### Passo 2: Criar Job que executa o arquivo

```bash
gcloud config set project monpec-sistema-rural

gcloud run jobs create monpec-admin-file \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
  --command python \
  --args criar_admin.py \
  --max-retries 1 \
  --task-timeout 300

gcloud run jobs execute monpec-admin-file --region us-central1 --wait
```

**NOTA**: Este método requer que o arquivo `criar_admin.py` esteja na imagem Docker. Se não estiver, use o método anterior com `-c`.

## 📝 Credenciais

- **URL**: https://monpec-fzzfjppzva-uc.a.run.app
- **Usuário**: admin
- **Senha**: L6171r12@@

## ⚠️ Dica Importante

Sempre use **aspas simples** `'...'` no bash quando houver caracteres especiais como `!`, `@`, `$`, etc., para evitar expansão de histórico ou interpretação especial pelo shell.










































