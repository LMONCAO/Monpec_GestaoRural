#!/bin/bash
# Script completo para gerar TODAS as credenciais necessárias para GitHub Secrets

echo "========================================"
echo "  GERAR TODAS AS CREDENCIAIS"
echo "========================================"
echo ""

# Gerar SECRET_KEY
echo "▶ Gerando SECRET_KEY..."
SECRET_KEY=$(openssl rand -base64 50 | tr -d '=+/' | cut -c1-50)
echo "✅ SECRET_KEY gerado"
echo ""

# Gerar DB_PASSWORD
echo "▶ Gerando DB_PASSWORD..."
DB_PASSWORD=$(openssl rand -base64 32 | tr -d '=+/' | cut -c1-25)
echo "✅ DB_PASSWORD gerado"
echo ""

# Gerar DJANGO_SUPERUSER_PASSWORD
echo "▶ Gerando DJANGO_SUPERUSER_PASSWORD..."
DJANGO_SUPERUSER_PASSWORD=$(openssl rand -base64 32 | tr -d '=+/' | cut -c1-20)
echo "✅ DJANGO_SUPERUSER_PASSWORD gerado"
echo ""

# Aplicar nova senha do banco
echo "▶ Aplicando nova senha no banco de dados..."
gcloud sql users set-password monpec_user \
    --instance=monpec-db \
    --password="$DB_PASSWORD" \
    --quiet
echo "✅ Senha do banco atualizada"
echo ""

# Obter GCP_SA_KEY (se não existir, criar)
echo "▶ Verificando Service Account Key..."
KEY_FILE="/tmp/monpec-sa-key.json"
if [ ! -f "$KEY_FILE" ]; then
    echo "   Criando nova chave..."
    gcloud iam service-accounts keys create "$KEY_FILE" \
        --iam-account=monpec-cloudrun-sa@monpec-sistema-rural.iam.gserviceaccount.com \
        --quiet
fi
echo "✅ Service Account Key pronto"
echo ""

echo "========================================"
echo "📋 TODAS AS CREDENCIAIS PARA GITHUB SECRETS:"
echo "========================================"
echo ""
echo "1. GCP_SA_KEY:"
echo "   (Conteúdo completo do JSON abaixo - copie TUDO)"
echo ""
cat "$KEY_FILE"
echo ""
echo ""
echo "2. SECRET_KEY:"
echo "   $SECRET_KEY"
echo ""
echo "3. DB_NAME:"
echo "   monpec_db"
echo ""
echo "4. DB_USER:"
echo "   monpec_user"
echo ""
echo "5. DB_PASSWORD:"
echo "   $DB_PASSWORD"
echo ""
echo "6. DJANGO_SUPERUSER_PASSWORD:"
echo "   $DJANGO_SUPERUSER_PASSWORD"
echo ""
echo "========================================"
echo "⚠️  IMPORTANTE:"
echo "   • Copie TODOS os valores acima AGORA"
echo "   • A senha do banco foi atualizada para: $DB_PASSWORD"
echo "   • Configure esses secrets em:"
echo "     https://github.com/LMONCAO/Monpec_GestaoRural/settings/secrets/actions"
echo "========================================"
echo ""

