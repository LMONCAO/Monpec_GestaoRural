# 🔐 Autenticar no Google Cloud

## ❌ Problema Identificado

O script detectou que você **não está autenticado** no Google Cloud.

## ✅ Solução: Fazer Login

Execute no **PowerShell** ou **Cloud Shell**:

```powershell
gcloud auth login
```

Isso vai:
1. Abrir seu navegador
2. Pedir para você fazer login na sua conta Google
3. Autorizar o acesso
4. Concluir a autenticação

## 🔄 Após Autenticar

Depois de fazer login, execute o deploy novamente:

```powershell
.\DEPLOY_COMPLETO_AUDITADO_POWERSHELL.ps1
```

**OU** se estiver no Cloud Shell:

```bash
bash deploy_completo_auditado.sh
```

## 📋 Passo a Passo

1. **Execute:** `gcloud auth login`
2. **Faça login** na sua conta Google no navegador
3. **Autorize** o acesso
4. **Volte ao terminal** e execute o deploy novamente

## ⚠️ Importante

- Use a mesma conta Google que tem acesso ao projeto `monpec-sistema-rural`
- Se não tiver acesso, peça para o administrador do projeto adicionar você

---

**Execute `gcloud auth login` e depois rode o deploy novamente!** 🚀


