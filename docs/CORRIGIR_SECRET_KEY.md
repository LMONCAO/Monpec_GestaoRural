# 🔧 Corrigir Erro SECRET_KEY

## ❌ Problema

O erro `ValueError: SECRET_KEY não configurada!` significa que a variável de ambiente `SECRET_KEY` não está configurada no Cloud Run.

## ✅ Solução

O script `DEPLOY_COMPLETO_POWERSHELL.ps1` foi **atualizado** para incluir a SECRET_KEY automaticamente.

### Execute o script atualizado:

```powershell
.\DEPLOY_COMPLETO_POWERSHELL.ps1
```

O script agora inclui a SECRET_KEY nas variáveis de ambiente automaticamente.

## 🔍 Verificar se SECRET_KEY está configurada

Após o deploy, verifique:

```powershell
gcloud run services describe monpec --region=us-central1 --format="value(spec.template.spec.containers[0].env)" | Select-String "SECRET_KEY"
```

## 📝 SECRET_KEY Usada

O script usa uma SECRET_KEY padrão para produção. **Em produção real, você deve usar uma chave única e segura.**

Para gerar uma nova SECRET_KEY:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

## ⚠️ Importante

- A SECRET_KEY agora está incluída automaticamente no deploy
- Execute o script atualizado: `.\DEPLOY_COMPLETO_POWERSHELL.ps1`
- O erro de SECRET_KEY não deve mais aparecer


