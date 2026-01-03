#!/usr/bin/env bash
#
# Bootstrap "uma vez só" para GCP (Cloud Run + Cloud Build + Cloud SQL) + GitHub Actions
#
# O que este script faz:
# - Ativa APIs necessárias
# - Cria/valida Cloud SQL Postgres (instância, database, usuário)
# - Cria/valida Service Account para GitHub Actions + permissões
# - Gera chave JSON da SA (para usar no secret GCP_SA_KEY)
# - (Opcional) cadastra secrets no GitHub automaticamente via "gh"
#
# Requisitos:
# - gcloud instalado e autenticado (no Cloud Shell já vem pronto)
# - gh instalado e autenticado (opcional, para cadastrar secrets)
#
# Uso recomendado (Cloud Shell):
#   bash deploy/gcp/bootstrap_gcp.sh --set-github-secrets
#
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-monpec-sistema-rural}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-monpec}"
DB_INSTANCE="${DB_INSTANCE:-monpec-db}"
DB_NAME="${DB_NAME:-monpec_db}"
DB_USER="${DB_USER:-monpec_user}"

SA_NAME="${SA_NAME:-github-actions-deploy}"
SA_EMAIL="${SA_EMAIL:-${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com}"

SET_GITHUB_SECRETS="false"
REPO="${REPO:-}"
SECRETS_OUT="${SECRETS_OUT:-.bootstrap-secrets.env}"

usage() {
  cat <<'EOF'
Uso:
  bootstrap_gcp.sh [--set-github-secrets] [--repo owner/name]

Variáveis opcionais (env):
  PROJECT_ID, REGION, SERVICE_NAME
  DB_INSTANCE, DB_NAME, DB_USER
  DB_PASSWORD, DJANGO_SUPERUSER_PASSWORD, SECRET_KEY
  SA_NAME, SA_EMAIL
  SECRETS_OUT (arquivo para salvar os valores gerados localmente)

Exemplos:
  bash deploy/gcp/bootstrap_gcp.sh
  bash deploy/gcp/bootstrap_gcp.sh --set-github-secrets --repo dono/repositorio
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --set-github-secrets)
      SET_GITHUB_SECRETS="true"
      shift
      ;;
    --repo)
      REPO="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Argumento desconhecido: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || { echo "❌ ERRO: comando '$1' não encontrado." >&2; exit 1; }
}

need_cmd gcloud

ACTIVE_ACCOUNT="$(gcloud auth list --filter=status:ACTIVE --format='value(account)' 2>/dev/null || true)"
if [[ -z "${ACTIVE_ACCOUNT}" ]]; then
  cat <<EOF >&2
❌ ERRO: gcloud não está autenticado.

No Cloud Shell:
  gcloud auth list

Se precisar autenticar:
  gcloud auth login
  gcloud auth application-default login

Depois rode este script novamente.
EOF
  exit 1
fi

gcloud config set project "${PROJECT_ID}" >/dev/null
gcloud config set run/region "${REGION}" >/dev/null

PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
RUNTIME_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "✅ Projeto: ${PROJECT_ID}"
echo "✅ Região:  ${REGION}"
echo "✅ Conta gcloud ativa: ${ACTIVE_ACCOUNT}"
echo ""

echo "==> Ativando APIs…"
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  sqladmin.googleapis.com \
  containerregistry.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  --quiet

echo "==> Cloud SQL (Postgres): garantindo instância '${DB_INSTANCE}'…"
if gcloud sql instances describe "${DB_INSTANCE}" --project "${PROJECT_ID}" --quiet >/dev/null 2>&1; then
  echo "✅ Instância Cloud SQL já existe."
else
  gcloud sql instances create "${DB_INSTANCE}" \
    --database-version=POSTGRES_15 \
    --region="${REGION}" \
    --tier=db-custom-1-3840 \
    --storage-type=SSD \
    --storage-size=20 \
    --availability-type=zonal \
    --quiet
  echo "✅ Instância Cloud SQL criada."
fi

echo "==> Cloud SQL: garantindo database '${DB_NAME}'…"
if gcloud sql databases describe "${DB_NAME}" --instance="${DB_INSTANCE}" --quiet >/dev/null 2>&1; then
  echo "✅ Database já existe."
else
  gcloud sql databases create "${DB_NAME}" --instance="${DB_INSTANCE}" --quiet
  echo "✅ Database criada."
fi

gen_secret() {
  # Gera um segredo forte via Python (preferível)
  python3 - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
}

DB_PASSWORD="${DB_PASSWORD:-}"
DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-}"
SECRET_KEY="${SECRET_KEY:-}"

need_cmd python3

if [[ -z "${DB_PASSWORD}" ]]; then DB_PASSWORD="$(gen_secret)"; fi
if [[ -z "${DJANGO_SUPERUSER_PASSWORD}" ]]; then DJANGO_SUPERUSER_PASSWORD="$(gen_secret)"; fi
if [[ -z "${SECRET_KEY}" ]]; then SECRET_KEY="$(gen_secret)"; fi

echo "==> Cloud SQL: garantindo usuário '${DB_USER}'…"
EXISTING_USERS="$(gcloud sql users list --instance="${DB_INSTANCE}" --format='value(name)' 2>/dev/null || true)"
if [[ " ${EXISTING_USERS} " == *" ${DB_USER} "* ]]; then
  # Atualiza senha (idempotente e garante que o secret do GitHub bate com o banco)
  gcloud sql users set-password "${DB_USER}" \
    --instance="${DB_INSTANCE}" \
    --password="${DB_PASSWORD}" \
    --quiet
  echo "✅ Usuário já existia; senha atualizada."
else
  gcloud sql users create "${DB_USER}" \
    --instance="${DB_INSTANCE}" \
    --password="${DB_PASSWORD}" \
    --quiet
  echo "✅ Usuário criado."
fi

echo "==> Service Account GitHub Actions: garantindo '${SA_EMAIL}'…"
if gcloud iam service-accounts describe "${SA_EMAIL}" --quiet >/dev/null 2>&1; then
  echo "✅ Service Account já existe."
else
  gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="GitHub Actions deploy (Cloud Run)" \
    --quiet
  echo "✅ Service Account criada."
fi

echo "==> Permissões (IAM)…"
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/run.admin" \
  --quiet >/dev/null

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudbuild.builds.editor" \
  --quiet >/dev/null

# Permite que o deploy "use" a runtime SA padrão do Cloud Run
gcloud iam service-accounts add-iam-policy-binding "${RUNTIME_SA}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/iam.serviceAccountUser" \
  --quiet >/dev/null

# Permite que o runtime do Cloud Run conecte ao Cloud SQL
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${RUNTIME_SA}" \
  --role="roles/cloudsql.client" \
  --quiet >/dev/null

echo "✅ IAM ok."

echo "==> Gerando chave JSON da Service Account (para o secret GCP_SA_KEY)…"
KEY_FILE="$(mktemp -t gcp-sa-key-XXXXXX.json)"
gcloud iam service-accounts keys create "${KEY_FILE}" --iam-account="${SA_EMAIL}" --quiet
echo "✅ Chave gerada (arquivo temporário)."

echo "==> Salvando secrets gerados em '${SECRETS_OUT}' (não comite este arquivo)…"
cat > "${SECRETS_OUT}" <<EOF
# Gerado por deploy/gcp/bootstrap_gcp.sh em $(date -u +"%Y-%m-%dT%H:%M:%SZ")
PROJECT_ID=${PROJECT_ID}
REGION=${REGION}
SERVICE_NAME=${SERVICE_NAME}
DB_INSTANCE=${DB_INSTANCE}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}
SECRET_KEY=${SECRET_KEY}
EOF

if [[ "${SET_GITHUB_SECRETS}" == "true" ]]; then
  need_cmd gh

  if [[ -z "${REPO}" ]]; then
    # tenta inferir do remote
    if command -v git >/dev/null 2>&1; then
      ORIGIN_URL="$(git remote get-url origin 2>/dev/null || true)"
      if [[ "${ORIGIN_URL}" == git@github.com:* ]]; then
        REPO="${ORIGIN_URL#git@github.com:}"
        REPO="${REPO%.git}"
      elif [[ "${ORIGIN_URL}" == https://github.com/* ]]; then
        REPO="${ORIGIN_URL#https://github.com/}"
        REPO="${REPO%.git}"
      fi
    fi
  fi

  if [[ -z "${REPO}" ]]; then
    echo "⚠️ Não consegui detectar o repo. Rode com: --repo dono/repositorio" >&2
    echo "   Vou pular o cadastro automático de secrets no GitHub."
  else
    echo "==> Cadastrando secrets no GitHub (${REPO})…"
    gh secret set GCP_SA_KEY --repo "${REPO}" --file "${KEY_FILE}" >/dev/null
    gh secret set SECRET_KEY --repo "${REPO}" --body "${SECRET_KEY}" >/dev/null
    gh secret set DB_NAME --repo "${REPO}" --body "${DB_NAME}" >/dev/null
    gh secret set DB_USER --repo "${REPO}" --body "${DB_USER}" >/dev/null
    gh secret set DB_PASSWORD --repo "${REPO}" --body "${DB_PASSWORD}" >/dev/null
    gh secret set DJANGO_SUPERUSER_PASSWORD --repo "${REPO}" --body "${DJANGO_SUPERUSER_PASSWORD}" >/dev/null
    echo "✅ Secrets cadastrados no GitHub."
  fi
fi

rm -f "${KEY_FILE}"

echo ""
echo "✅ Bootstrap concluído."
echo ""
echo "Próximo passo:"
echo " - Faça push na branch main/master para disparar o workflow (recomendado: .github/workflows/deploy-google-cloud.yml)."
echo " - Se já fez push e quer rodar manualmente: use 'Run workflow' no GitHub Actions."

