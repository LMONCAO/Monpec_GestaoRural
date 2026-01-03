#!/bin/bash
# Script para criar admin no Cloud Run via Cloud Shell
# Execute: bash COMANDO_CLOUD_SHELL_CORRIGIDO.sh

# Configurar projeto
gcloud config set project monpec-sistema-rural

# Criar job com senha escapada corretamente
# Usando aspas simples para evitar expansão de histórico do bash
gcloud run jobs create monpec-admin-final \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
  --command python \
  --args -c,'import os,django;os.environ.setdefault("DJANGO_SETTINGS_MODULE","sistema_rural.settings_gcp");django.setup();from django.contrib.auth import get_user_model;User=get_user_model();u,created=User.objects.get_or_create(username="admin",defaults={"email":"admin@monpec.com.br"});u.set_password("L6171r12@@");u.is_staff=u.is_superuser=u.is_active=True;u.save();print("✅ Admin criado! Username: admin, Password: L6171r12@@")' \
  --max-retries 1 \
  --task-timeout 300

# Executar o job
echo "Executando criação do admin..."
gcloud run jobs execute monpec-admin-final --region us-central1 --wait

echo ""
echo "✅ Processo concluído!"
echo "Agora você pode fazer login com:"
echo "  Usuário: admin"
echo "  Senha: L6171r12@@"
echo "  URL: https://monpec-fzzfjppzva-uc.a.run.app"










































