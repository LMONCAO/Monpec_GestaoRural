#!/bin/bash
# Script para obter credenciais para configurar GitHub Secrets manualmente

PROJECT_ID="monpec-sistema-rural"
SERVICE_ACCOUNT_EMAIL="monpec-cloudrun-sa@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="/tmp/monpec-sa-key.json"

echo "========================================"
echo "  OBTER CREDENCIAIS PARA GITHUB SECRETS"
echo "========================================"
echo ""

# Criar/obter chave JSON do Service Account
echo "▶ Obtendo chave JSON do Service Account..."
gcloud iam service-accounts keys create "$KEY_FILE" \
    --iam-account="$SERVICE_ACCOUNT_EMAIL" \
    --quiet 2>/dev/null || \
gcloud iam service-accounts keys list --iam-account="$SERVICE_ACCOUNT_EMAIL" --format="value(name)" | head -1 | xargs -I {} gcloud iam service-accounts keys get-public-key {} --iam-account="$SERVICE_ACCOUNT_EMAIL" > /dev/null 2>&1

echo "✅ Chave JSON criada/obtida"
echo ""

# Ler valores do banco
DB_PASSWORD=$(gcloud sql users describe monpec_user --instance=monpec-db --format="value(password)" 2>/dev/null || echo "")

echo "📋 CREDENCIAIS PARA GITHUB SECRETS:"
echo "========================================"
echo ""
echo "1. GCP_SA_KEY:"
echo "   (Cole o conteúdo completo do arquivo JSON abaixo)"
echo ""
cat "$KEY_FILE"
echo ""
echo ""
echo "2. SECRET_KEY:"
echo "   (Gere uma nova ou use a que você já tem)"
echo "   Execute: openssl rand -base64 50 | tr -d '=+/' | cut -c1-50"
echo ""
echo "3. DB_NAME:"
echo "   monpec_db"
echo ""
echo "4. DB_USER:"
echo "   monpec_user"
echo ""
echo "5. DB_PASSWORD:"
if [ -n "$DB_PASSWORD" ]; then
    echo "   $DB_PASSWORD"
else
    echo "   (Senha não pode ser recuperada. Use a que foi gerada no bootstrap)"
    echo "   Ou redefina: gcloud sql users set-password monpec_user --instance=monpec-db --password=NOVA_SENHA"
fi
echo ""
echo "6. DJANGO_SUPERUSER_PASSWORD:"
echo "   (Gere uma nova: openssl rand -base64 32 | tr -d '=+/' | cut -c1-20)"
echo ""
echo "========================================"
echo "🔗 Configure em: https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions"
echo "========================================"
echo ""

# Não remover a chave para que o usuário possa copiá-la
echo "⚠️  Chave JSON salva em: $KEY_FILE"
echo "   Você pode removê-la depois com: rm $KEY_FILE"
echo ""

