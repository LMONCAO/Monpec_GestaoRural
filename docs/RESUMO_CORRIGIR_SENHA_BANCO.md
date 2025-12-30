# 🔧 Resumo: Corrigir Senha do Banco de Dados

## ❌ Problema

Erro nos logs: `password authentication failed for user "monpec_user"`

Isso significa que a senha do banco de dados PostgreSQL no Cloud SQL não está correta.

## ✅ Solução Rápida

Execute no **Cloud Shell**:

```bash
# 1. Corrigir senha do banco
gcloud sql users set-password monpec_user --instance=monpec-db --password=L6171r12@@jjms

# 2. Atualizar Cloud Run
gcloud run services update monpec --region=us-central1 --update-env-vars "DB_PASSWORD=L6171r12@@jjms"
```

## 🔍 Verificar se Funcionou

Aguarde 30 segundos e verifique os logs:

```bash
gcloud logging read \
    "resource.type=cloud_run_revision AND resource.labels.service_name=monpec AND severity>=ERROR" \
    --limit=5
```

Se não houver mais erros de autenticação, está resolvido! ✅

## 📚 Mais Detalhes

Veja o guia completo: `CORRIGIR_SENHA_BANCO_DADOS.md`


