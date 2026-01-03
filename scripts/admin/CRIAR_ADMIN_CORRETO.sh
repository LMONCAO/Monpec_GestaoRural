#!/bin/bash
# Criar admin CORRETO - garantindo que NÃO seja tratado como demo

echo "🔐 Criando admin CORRETO (sem marcação de demo)"
echo "================================================"
echo ""

CONNECTION_NAME=$(gcloud sql instances describe monpec-db --format="value(connectionName)")
PROJECT_ID=$(gcloud config get-value project)
DB_PASS='Monpec2025!SenhaSegura'

# Criar script Python que garante admin correto
cat > /tmp/criar_admin_correto.py << 'PYTHON_SCRIPT'
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = 'admin'
email = 'admin@monpec.com.br'
password = 'L6171r12@@'

try:
    # Criar ou atualizar admin
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"✅ Usuário '{username}' encontrado, atualizando...")
    else:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_superuser=True,
            is_staff=True,
            is_active=True
        )
        print(f"✅ Usuário '{username}' criado")
    
    # Garantir que é superuser/staff/ativo
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.is_active = True
    user.email = email
    user.save()
    
    # IMPORTANTE: Remover registro UsuarioAtivo se existir (para não ser tratado como demo)
    try:
        from gestao_rural.models_auditoria import UsuarioAtivo
        UsuarioAtivo.objects.filter(usuario=user).delete()
        print("✅ Removido registro UsuarioAtivo (não é demo)")
    except Exception as e:
        print(f"ℹ️  Não foi possível verificar UsuarioAtivo: {e}")
    
    print()
    print("=" * 60)
    print("ADMIN CONFIGURADO CORRETAMENTE")
    print("=" * 60)
    print(f"Usuário: {user.username}")
    print(f"Email: {user.email}")
    print(f"Senha: {password}")
    print(f"Superuser: {user.is_superuser}")
    print(f"Staff: {user.is_staff}")
    print(f"Ativo: {user.is_active}")
    print("=" * 60)
    print()
    print("✅ Admin pronto para uso (NÃO é usuário demo)")
    
except Exception as e:
    print(f"❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

echo "▶ Criando job para criar admin correto..."
gcloud run jobs create criar-admin-correto \
  --image gcr.io/$PROJECT_ID/monpec \
  --region us-central1 \
  --command python \
  --args /tmp/criar_admin_correto.py \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=$DB_PASS,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME,SECRET_KEY=django-insecure-temp" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 600 \
  --memory 1Gi \
  --cpu 1 2>&1 | grep -v "already exists" || true

echo ""
echo "▶ Executando job..."
gcloud run jobs execute criar-admin-correto --region us-central1 --wait

echo ""
echo "🧹 Limpando..."
gcloud run jobs delete criar-admin-correto --region us-central1 --quiet 2>&1 || true

echo ""
echo "✅ Concluído!"
echo ""
echo "🌐 Teste o login em: https://monpec-29862706245.us-central1.run.app/login/"
echo "   Usuário: admin"
echo "   Senha: L6171r12@@"








