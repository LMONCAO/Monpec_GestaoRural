#!/bin/bash
# 🔥 RESETAR GOOGLE CLOUD - EXCLUIR TUDO E PREPARAR PARA NOVO DEPLOY
# ⚠️ ATENÇÃO: Este script EXCLUI TODOS os recursos do projeto!
# Use apenas se deseja resetar completamente o ambiente

set -e  # Parar em caso de erro (mas vamos tratar erros manualmente)

# Configurações
PROJECT_ID="monpec-sistema-rural"
SERVICE_NAME="monpec"
REGION="us-central1"
INSTANCE_NAME="monpec-db"
IMAGE_NAME="gcr.io/$PROJECT_ID/monpec"
DOMAIN="monpec.com.br"
WWW_DOMAIN="www.monpec.com.br"

echo ""
echo "========================================"
echo "🔥 RESETAR GOOGLE CLOUD - EXCLUIR TUDO"
echo "========================================"
echo ""
echo "⚠️  ATENÇÃO: Este script vai EXCLUIR todos os recursos!"
echo "   • Serviços Cloud Run"
echo "   • Jobs Cloud Run"
echo "   • Instância Cloud SQL (E TODOS OS DADOS!)"
echo "   • Domain Mappings"
echo "   • Imagens Docker no Container Registry"
echo ""

# Confirmação
read -p "Digite 'CONFIRMAR' para continuar (qualquer outra coisa cancela): " confirm
if [ "$confirm" != "CONFIRMAR" ]; then
    echo "Operação cancelada pelo usuário."
    exit 0
fi

echo ""
echo "Configurando projeto..."
gcloud config set project $PROJECT_ID
echo "✅ Projeto configurado: $PROJECT_ID"
echo ""

# PARTE 1: EXCLUIR DOMAIN MAPPINGS
echo "========================================"
echo "PARTE 1: EXCLUINDO DOMAIN MAPPINGS"
echo "========================================"
echo ""

echo "Excluindo domain mapping para $DOMAIN..."
gcloud run domain-mappings delete $DOMAIN --region $REGION --quiet 2>&1 || echo "Domain mapping não encontrado: $DOMAIN"

echo "Excluindo domain mapping para $WWW_DOMAIN..."
gcloud run domain-mappings delete $WWW_DOMAIN --region $REGION --quiet 2>&1 || echo "Domain mapping não encontrado: $WWW_DOMAIN"

echo ""

# PARTE 2: EXCLUIR JOBS DO CLOUD RUN
echo "========================================"
echo "PARTE 2: EXCLUINDO JOBS DO CLOUD RUN"
echo "========================================"
echo ""

JOB_NAMES=("migrate-monpec" "collectstatic-monpec" "create-superuser")
for JOB_NAME in "${JOB_NAMES[@]}"; do
    echo "Excluindo job: $JOB_NAME..."
    gcloud run jobs delete $JOB_NAME --region $REGION --quiet 2>&1 || echo "Job não encontrado: $JOB_NAME"
done

# Excluir todos os jobs (caso haja outros)
echo "Listando todos os jobs restantes..."
ALL_JOBS=$(gcloud run jobs list --region $REGION --format="value(name)" 2>&1 || echo "")
if [ -n "$ALL_JOBS" ]; then
    while IFS= read -r JOB; do
        JOB_SHORT=$(basename $JOB)
        echo "Excluindo job: $JOB_SHORT..."
        gcloud run jobs delete $JOB_SHORT --region $REGION --quiet 2>&1 || echo "Erro ao excluir job: $JOB_SHORT"
    done <<< "$ALL_JOBS"
fi

echo ""

# PARTE 3: EXCLUIR SERVIÇO CLOUD RUN
echo "========================================"
echo "PARTE 3: EXCLUINDO SERVIÇO CLOUD RUN"
echo "========================================"
echo ""

echo "Excluindo serviço: $SERVICE_NAME..."
gcloud run services delete $SERVICE_NAME --region $REGION --quiet 2>&1 || echo "Serviço não encontrado: $SERVICE_NAME"

# Excluir todos os serviços (caso haja outros)
echo "Listando todos os serviços restantes..."
ALL_SERVICES=$(gcloud run services list --region $REGION --format="value(name)" 2>&1 || echo "")
if [ -n "$ALL_SERVICES" ]; then
    while IFS= read -r SERVICE; do
        SERVICE_SHORT=$(basename $SERVICE)
        echo "Excluindo serviço: $SERVICE_SHORT..."
        gcloud run services delete $SERVICE_SHORT --region $REGION --quiet 2>&1 || echo "Erro ao excluir serviço: $SERVICE_SHORT"
    done <<< "$ALL_SERVICES"
fi

echo ""

# PARTE 4: EXCLUIR INSTÂNCIA CLOUD SQL (CUIDADO - EXCLUI TODOS OS DADOS!)
echo "========================================"
echo "PARTE 4: EXCLUINDO INSTÂNCIA CLOUD SQL"
echo "========================================"
echo ""
echo "⚠️  ATENÇÃO: Isso vai EXCLUIR TODOS OS DADOS do banco de dados!"
echo ""

read -p "Digite 'EXCLUIR' para excluir o banco de dados (qualquer outra coisa mantém o banco): " confirm_db
if [ "$confirm_db" = "EXCLUIR" ]; then
    echo "Excluindo instância Cloud SQL: $INSTANCE_NAME..."
    gcloud sql instances delete $INSTANCE_NAME --quiet 2>&1 || echo "Instância não encontrada: $INSTANCE_NAME (pode já ter sido excluída)"
    echo "✅ Instância Cloud SQL excluída: $INSTANCE_NAME"
    echo "⚠️  Todos os dados foram excluídos permanentemente!"
else
    echo "Instância Cloud SQL mantida (não foi excluída)"
    echo "Se você desejar excluir depois, execute:"
    echo "   gcloud sql instances delete $INSTANCE_NAME"
fi

echo ""

# PARTE 5: EXCLUIR IMAGENS DO CONTAINER REGISTRY
echo "========================================"
echo "PARTE 5: EXCLUINDO IMAGENS DO CONTAINER REGISTRY"
echo "========================================"
echo ""

echo "Listando imagens no Container Registry..."
IMAGES=$(gcloud container images list --repository=gcr.io/$PROJECT_ID --format="value(name)" 2>&1 || echo "")
if [ -n "$IMAGES" ]; then
    while IFS= read -r IMAGE; do
        echo "Listando tags da imagem: $IMAGE..."
        TAGS=$(gcloud container images list-tags $IMAGE --format="value(digest)" 2>&1 || echo "")
        if [ -n "$TAGS" ]; then
            echo "Excluindo imagem: $IMAGE..."
            gcloud container images delete $IMAGE --force-delete-tags --quiet 2>&1 || echo "Erro ao excluir imagem: $IMAGE"
            echo "✅ Imagem excluída: $IMAGE"
        fi
    done <<< "$IMAGES"
else
    echo "Nenhuma imagem encontrada no Container Registry"
fi

# Excluir imagem específica também
echo "Tentando excluir imagem específica: $IMAGE_NAME..."
gcloud container images delete $IMAGE_NAME --force-delete-tags --quiet 2>&1 || echo "Imagem não encontrada ou já excluída: $IMAGE_NAME"

echo ""

# PARTE 6: EXCLUIR BUILD HISTORY (OPCIONAL)
echo "========================================"
echo "PARTE 6: LIMPANDO HISTÓRICO DE BUILDS"
echo "========================================"
echo ""

echo "Listando builds recentes..."
BUILDS=$(gcloud builds list --limit=50 --format="value(id)" 2>&1 || echo "")
if [ -n "$BUILDS" ]; then
    echo "⚠️  Existem builds no histórico (não serão excluídos automaticamente)"
    echo "Se desejar excluir builds antigos, use:"
    echo "   gcloud builds list --limit=50"
    echo "   gcloud builds delete [BUILD_ID]"
else
    echo "Nenhum build encontrado"
fi

echo ""

# RESUMO FINAL
echo "========================================"
echo "✅ RESET CONCLUÍDO!"
echo "========================================"
echo ""

echo "📋 RECURSOS EXCLUÍDOS:"
echo "  ✅ Domain Mappings (se existiam)"
echo "  ✅ Jobs Cloud Run (se existiam)"
echo "  ✅ Serviços Cloud Run (se existiam)"
if [ "$confirm_db" = "EXCLUIR" ]; then
    echo "  ✅ Instância Cloud SQL (E TODOS OS DADOS!)"
else
    echo "  ⏸️  Instância Cloud SQL (mantida)"
fi
echo "  ✅ Imagens Docker no Container Registry"
echo ""

echo "🚀 PRÓXIMOS PASSOS:"
echo ""
echo "Para fazer um novo deploy limpo, execute:"
echo "   ./DEPLOY_COMPLETO_AUTOMATICO_FINAL.ps1  (PowerShell)"
echo "   ou"
echo "   ./DEPLOY_GOOGLE_CLOUD_SHELL.sh  (Bash/Cloud Shell)"
echo ""
echo "🎉 Ambiente resetado com sucesso!"
echo ""






