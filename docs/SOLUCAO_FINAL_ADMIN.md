# 🔧 SOLUÇÃO FINAL - Criar Admin Corretamente

## 🔴 Problema
O admin pode já existir com senha incorreta. Precisamos **DELETAR e RECRIAR**.

## ✅ SOLUÇÃO - Execute no Cloud Shell

### Passo 1: Configurar projeto
```bash
gcloud config set project monpec-sistema-rural
```

### Passo 2: Criar job que deleta e recria o admin

Copie e cole este comando **COMPLETO** no Cloud Shell:

```bash
gcloud run jobs create monpec-admin-final-v2 \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
  --command python \
  --args -c,'import os,django;os.environ.setdefault("DJANGO_SETTINGS_MODULE","sistema_rural.settings_gcp");django.setup();from django.contrib.auth import get_user_model,authenticate;User=get_user_model();u=User.objects.filter(username="admin").first();[u.delete() for u in [u] if u];u=User.objects.create_user(username="admin",email="admin@monpec.com.br",password="L6171r12@@");u.is_staff=u.is_superuser=u.is_active=True;u.save();print("✅ Admin criado! Username: admin, Password: L6171r12@@");auth=authenticate(username="admin",password="L6171r12@@");print("✅ Autenticação:",auth is not None)' \
  --max-retries 1 \
  --task-timeout 300
```

### Passo 3: Executar o job
```bash
gcloud run jobs execute monpec-admin-final-v2 --region us-central1 --wait
```

## 🔍 O que este comando faz:

1. ✅ **Deleta** o usuário admin existente (se houver)
2. ✅ **Cria** um novo usuário admin com senha correta
3. ✅ **Configura** todas as permissões (staff, superuser, active)
4. ✅ **Testa** a autenticação para garantir que funciona

## 📝 Credenciais

- **URL**: https://monpec-fzzfjppzva-uc.a.run.app
- **Usuário**: admin
- **Senha**: L6171r12@@

## ⚠️ Se ainda não funcionar

Verifique os logs:
```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=monpec-admin-final-v2" \
  --limit 30 \
  --format="table(timestamp,textPayload)" \
  --project monpec-sistema-rural
```










































