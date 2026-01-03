# Bootstrap do GCP (uma vez só)

Este diretório contém o bootstrap para preparar o Google Cloud para o deploy via **GitHub Actions** usando **Cloud Run + Cloud Build + Cloud SQL**.

## O que o script faz

- Ativa APIs necessárias
- Cria/valida **Cloud SQL Postgres** (instância, database, usuário)
- Cria/valida **Service Account** do GitHub Actions e permissões
- Gera a chave JSON da SA e (opcionalmente) cadastra secrets no GitHub

## Como rodar (recomendado)

No **Google Cloud Shell** (já vem com `gcloud` autenticado):

```bash
bash deploy/gcp/bootstrap_gcp.sh --set-github-secrets
```

Se o repo não for detectado automaticamente, informe:

```bash
bash deploy/gcp/bootstrap_gcp.sh --set-github-secrets --repo dono/repositorio
```

## O que ele vai criar/configurar no GitHub

Se você passar `--set-github-secrets`, o script tenta cadastrar:

- `GCP_SA_KEY`
- `SECRET_KEY`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DJANGO_SUPERUSER_PASSWORD`

## Segurança

O script salva os valores gerados em `.bootstrap-secrets.env` (já está no `.gitignore`).
Não comite esse arquivo.

