# ✅ COMANDO CORRIGIDO - Executar Admin

## 🎉 Ótimo! O job foi criado com sucesso!

Agora você só precisa executá-lo corretamente.

## ❌ Erros no comando anterior:

1. `--waitgcloud` → deve ser `--wait`
2. `us-centrall` → deve ser `us-central1` (com "1" no final, não "ll")

## ✅ COMANDO CORRETO:

Execute este comando no Cloud Shell:

```bash
gcloud run jobs execute monpec-admin-final --region us-central1 --wait
```

**IMPORTANTE**: 
- Use `--wait` (não `--waitgcloud`)
- Use `us-central1` (não `us-centrall`)

## 📋 Sequência Completa (caso precise recriar):

```bash
# 1. Configurar projeto
gcloud config set project monpec-sistema-rural

# 2. Criar job
gcloud run jobs create monpec-admin-final \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
  --command python \
  --args -c,'import os,django;os.environ.setdefault("DJANGO_SETTINGS_MODULE","sistema_rural.settings_gcp");django.setup();from django.contrib.auth import get_user_model;User=get_user_model();u,created=User.objects.get_or_create(username="admin",defaults={"email":"admin@monpec.com.br"});u.set_password("L6171r12@@");u.is_staff=u.is_superuser=u.is_active=True;u.save();print("✅ Admin criado!")' \
  --max-retries 1 \
  --task-timeout 300

# 3. Executar (COMANDO CORRETO)
gcloud run jobs execute monpec-admin-final --region us-central1 --wait
```

## 🔍 Verificar se funcionou:

Depois de executar, você verá mensagens como:
- "Creating execution..."
- "Provisioning resources..."
- "Running execution..."
- "Done."
- "✅ Admin criado!"

## 📝 Credenciais após sucesso:

- **URL**: https://monpec-fzzfjppzva-uc.a.run.app
- **Usuário**: admin
- **Senha**: L6171r12@@
















