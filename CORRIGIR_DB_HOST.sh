#!/bin/bash
# Script para corrigir DB_HOST para formato Cloud SQL Unix Socket

SERVICE_NAME="monpec"
JOB_NAME="migrate-monpec"
REGION="us-central1"

echo "========================================"
echo "🔧 Corrigindo DB_HOST para Cloud SQL"
echo "========================================"
echo ""

# 1. Verificar DB_HOST atual
echo "1️⃣  Verificando DB_HOST atual..."
SERVICE_ENV=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null)

if [ -z "$SERVICE_ENV" ]; then
    echo "❌ Não foi possível obter variáveis do serviço"
    exit 1
fi

echo "Variáveis atuais:"
echo "$SERVICE_ENV" | tr ',' '\n' | grep "DB_"
echo ""

# 2. Verificar se DB_HOST está errado
if echo "$SERVICE_ENV" | grep -q "DB_HOST=127.0.0.1\|DB_HOST=localhost"; then
    echo "⚠️  DB_HOST está usando IP local (127.0.0.1) - ERRADO!"
    echo ""
    echo "Para Cloud Run Jobs, DB_HOST deve estar no formato:"
    echo "  /cloudsql/PROJECT_ID:REGION:INSTANCE_NAME"
    echo ""
    
    # Solicitar informações corretas
    read -p "PROJECT_ID [monpec-sistema-rural]: " PROJECT_ID
    PROJECT_ID=${PROJECT_ID:-monpec-sistema-rural}
    
    read -p "REGION do Cloud SQL [us-central1]: " SQL_REGION
    SQL_REGION=${SQL_REGION:-us-central1}
    
    read -p "INSTANCE_NAME do Cloud SQL: " INSTANCE_NAME
    
    if [ -z "$INSTANCE_NAME" ]; then
        echo "❌ Nome da instância é obrigatório"
        exit 1
    fi
    
    DB_HOST="/cloudsql/$PROJECT_ID:$SQL_REGION:$INSTANCE_NAME"
    echo ""
    echo "DB_HOST correto: $DB_HOST"
    echo ""
    
    # 3. Atualizar serviço
    echo "2️⃣  Atualizando serviço com DB_HOST correto..."
    # Extrair outras variáveis e atualizar DB_HOST
    NEW_ENV=$(echo "$SERVICE_ENV" | sed "s|DB_HOST=[^,]*|DB_HOST=$DB_HOST|")
    
    gcloud run services update $SERVICE_NAME --region $REGION --update-env-vars "$NEW_ENV"
    
    if [ $? -eq 0 ]; then
        echo "✅ Serviço atualizado"
    else
        echo "❌ Erro ao atualizar serviço"
        exit 1
    fi
    echo ""
    
    # 4. Atualizar job
    echo "3️⃣  Atualizando job com DB_HOST correto..."
    gcloud run jobs update $JOB_NAME --region $REGION --update-env-vars "$NEW_ENV"
    
    if [ $? -eq 0 ]; then
        echo "✅ Job atualizado"
    else
        echo "❌ Erro ao atualizar job"
        exit 1
    fi
    echo ""
    
    # 5. Verificar se precisa adicionar Cloud SQL instance
    echo "4️⃣  Verificando conexão Cloud SQL..."
    echo "O job precisa ter acesso ao Cloud SQL instance."
    echo ""
    echo "Adicionando Cloud SQL instance ao job..."
    gcloud run jobs update $JOB_NAME --region $REGION --add-cloudsql-instances "$DB_HOST"
    
    echo ""
    echo "✅ Configuração atualizada!"
    echo ""
    echo "5️⃣  Executando migração..."
    gcloud run jobs execute $JOB_NAME --region $REGION --wait
    
else
    echo "✅ DB_HOST parece estar correto"
    echo ""
    echo "Verificando se o job tem acesso ao Cloud SQL..."
    
    # Verificar se o job tem Cloud SQL instance configurado
    JOB_CLOUDSQL=$(gcloud run jobs describe $JOB_NAME --region $REGION --format="value(spec.template.spec.containers[0].env)" 2>/dev/null | grep -o "cloudsql-instances" || echo "")
    
    if [ -z "$JOB_CLOUDSQL" ]; then
        DB_HOST=$(echo "$SERVICE_ENV" | grep -o "DB_HOST=[^,]*" | cut -d= -f2)
        if [[ "$DB_HOST" == /cloudsql/* ]]; then
            echo "Adicionando Cloud SQL instance ao job..."
            gcloud run jobs update $JOB_NAME --region $REGION --add-cloudsql-instances "$DB_HOST"
        fi
    fi
    
    echo ""
    echo "Executando migração..."
    gcloud run jobs execute $JOB_NAME --region $REGION --wait
fi


