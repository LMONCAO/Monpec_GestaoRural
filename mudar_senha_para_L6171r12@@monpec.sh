#!/bin/bash
# Script para mudar senha do admin para L6171r12@@monpec
# Execute no Google Cloud Shell

set -e

echo "🔐 MUDANÇA DE SENHA DO ADMIN - MONPEC"
echo "======================================"

# Configurações
PROJECT_ID="monpec-sistema-rural"
REGION="us-central1"
SERVICE_NAME="monpec"
CONNECTION_NAME="$PROJECT_ID:$REGION:monpec-db"

# SENHA CONFIGURADA: L6171r12@@monpec
NOVA_SENHA="L6171r12@@monpec"

echo "📝 Senha configurada: $NOVA_SENHA"
echo "✅ Senha validada!"
echo ""

# Configurar projeto
echo "🔧 Configurando projeto..."
gcloud config set project $PROJECT_ID --quiet

# Executar mudança de senha
echo "🔄 Executando mudança de senha..."

gcloud run jobs create change-admin-password \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --region $REGION \
  --command python \
  --args -c,"
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()
from django.contrib.auth.models import User

print('🔐 Alterando senha do admin...')
admin_user = User.objects.filter(username='admin').first()
if admin_user:
    admin_user.set_password('$NOVA_SENHA')
    admin_user.save()
    print('✅ Senha alterada com sucesso!')
    print('👤 Usuário: admin')
    print('📧 Email: admin@monpec.com.br')
else:
    print('❌ Usuário admin não encontrado!')
" \
  --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,CLOUD_SQL_CONNECTION_NAME=$CONNECTION_NAME" \
  --set-cloudsql-instances $CONNECTION_NAME \
  --max-retries 1 \
  --task-timeout 300 \
  --memory 512Mi \
  --cpu 1 \
  --quiet

# Executar job
echo "⏱️  Executando..."
gcloud run jobs execute change-admin-password --region $REGION --wait

# Limpar job
gcloud run jobs delete change-admin-password --region $REGION --quiet 2>&1 || true

echo ""
echo "🎉 SENHA ALTERADA COM SUCESSO!"
echo "================================"
echo ""
echo "🌐 URLs de acesso:"
echo "   • https://monpec.com.br/login/"
echo "   • https://monpec-29862706245.us-central1.run.app/login/"
echo ""
echo "👤 Credenciais:"
echo "   Usuário: admin"
echo "   Email: admin@monpec.com.br"
echo "   Senha: L6171r12@@monpec"
echo ""
echo "📝 PRÓXIMO PASSO:"
echo "   Execute o script 'mudar_senha_para_L6171r12@@js.sh'"
echo "   para definir a senha final: L6171r12@@js"
echo ""
echo "⚠️ IMPORTANTE:"
echo "   • Anote sua senha atual: L6171r12@@monpec"
echo "   • A senha antiga (admin123) não funciona mais!"
echo ""
echo "✅ Processo concluído!"