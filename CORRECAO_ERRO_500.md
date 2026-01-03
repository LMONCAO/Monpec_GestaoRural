# ✅ Correção do Erro 500 - Variáveis de Ambiente

## 🔍 Problema Identificado

O erro 500 era causado por **variáveis de ambiente não configuradas corretamente**:
- `CLOUD_SQL_CONNECTION_NAME` não estava definida
- Isso causava erro na inicialização do Django

## ✅ Solução Aplicada

Atualizei todas as variáveis de ambiente do serviço Cloud Run:

```bash
gcloud run services update monpec --region us-central1 --update-env-vars="DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=0d0)yw=u#u=owx#=qo(&%-b+a_@_u3=1wt242v2fx_$1ap4+4t,CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=L6171r12@@jjms,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural"
```

## 📋 Variáveis Configuradas

- ✅ `DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp`
- ✅ `DEBUG=False`
- ✅ `SECRET_KEY` (configurada)
- ✅ `CLOUD_SQL_CONNECTION_NAME=monpec-sistema-rural:us-central1:monpec-db`
- ✅ `DB_NAME=monpec_db`
- ✅ `DB_USER=monpec_user`
- ✅ `DB_PASSWORD` (configurada)
- ✅ `GOOGLE_CLOUD_PROJECT=monpec-sistema-rural`

## 🧪 Testar Agora

Aguarde alguns segundos para o serviço reiniciar e então teste:

**URL:** https://monpec-29862706245.us-central1.run.app

Ou acesse via domínio: **https://monpec.com.br**

## ✅ Status

- [x] Variáveis de ambiente corrigidas
- [x] Serviço atualizado
- [ ] Verificar se erro foi resolvido (testar no navegador)

## 📊 Ver Logs

```bash
gcloud run services logs read monpec --region us-central1 --limit=50
```

