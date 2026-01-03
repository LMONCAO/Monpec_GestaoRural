#!/bin/bash
# Comando final para criar admin - Execute no Cloud Shell

gcloud config set project monpec-sistema-rural

gcloud run jobs create monpec-admin-final-v2 \
  --image gcr.io/monpec-sistema-rural/monpec \
  --region us-central1 \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False" \
  --command python \
  --args -c,'import os,django;os.environ.setdefault("DJANGO_SETTINGS_MODULE","sistema_rural.settings_gcp");django.setup();from django.contrib.auth import get_user_model,authenticate;User=get_user_model();u=User.objects.filter(username="admin").first();[u.delete() for u in [u] if u];u=User.objects.create_user(username="admin",email="admin@monpec.com.br",password="L6171r12@@");u.is_staff=u.is_superuser=u.is_active=True;u.save();print("✅ Admin criado! Username: admin, Password: L6171r12@@");auth=authenticate(username="admin",password="L6171r12@@");print("✅ Autenticação:",auth is not None)' \
  --max-retries 1 \
  --task-timeout 300

gcloud run jobs execute monpec-admin-final-v2 --region us-central1 --wait










































