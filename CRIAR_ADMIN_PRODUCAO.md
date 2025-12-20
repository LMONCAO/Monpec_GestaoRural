# Como Criar Admin no Cloud Run

## Opção 1: Tentar primeiro estas credenciais
- **Usuário:** `admin`
- **Senha:** `Monpec2025!`

## Opção 2: Executar comando Django no Cloud Run

Se a senha acima não funcionar, execute:

```powershell
gcloud run jobs create criar-admin `
    --image gcr.io/monpec-sistema-rural/monpec:latest `
    --region us-central1 `
    --command python `
    --args criar_admin_cloud_run.py `
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False"

gcloud run jobs execute criar-admin --region us-central1
```

## Opção 3: Executar via shell do Cloud SQL (alternativa)

Se tiver acesso ao banco via psql:

```powershell
gcloud sql connect monpec-db --user=monpec_user
```

Depois, você precisaria criar o usuário via Django shell ou usando SQL direto.

