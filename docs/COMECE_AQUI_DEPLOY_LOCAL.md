# 🚀 COMECE AQUI: Deploy do Código Local

## ❌ O Problema que Você Estava Tendo

Você estava fazendo deploy do **Cloud Shell**, mas o Cloud Shell tinha código **antigo**. Por isso a versão na web estava diferente da local.

## ✅ A Solução

Agora você tem o script **`DEPLOY_DEFINITIVO_LOCAL.ps1`** que faz deploy **DIRETO do seu código local**.

## 🎯 Como Usar (3 Passos)

### 1. Abra o PowerShell

No diretório do projeto:
```
C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural
```

### 2. Execute o Script

```powershell
.\DEPLOY_DEFINITIVO_LOCAL.ps1
```

**Se der erro de execução:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\DEPLOY_DEFINITIVO_LOCAL.ps1
```

### 3. Aguarde 10-15 Minutos

O script vai:
- ✅ Verificar seu código local
- ✅ Fazer build da imagem
- ✅ Fazer deploy no Cloud Run
- ✅ Mostrar a URL e credenciais

## 📋 O que Você Vai Ver

```
========================================
  DEPLOY DEFINITIVO - CÓDIGO LOCAL
========================================

▶ ETAPA 1: Verificando código local...
✅ Dockerfile.prod encontrado
✅ manage.py encontrado
✅ settings_gcp.py encontrado
✅ Código local verificado!

▶ ETAPA 2: Autenticando no Google Cloud...
✅ Autenticado: seu-email@gmail.com
✅ Projeto configurado

▶ ETAPA 3: Corrigindo senha do banco...
✅ Senha do banco atualizada

▶ ETAPA 4: Buildando imagem Docker (CÓDIGO LOCAL)
ℹ️  IMPORTANTE: O build vai usar os arquivos DESTE diretório local!
...
✅ Build concluído! Imagem: gcr.io/...

▶ ETAPA 5: Deployando no Cloud Run...
✅ Deploy concluído!

▶ ETAPA 6: Obtendo URL do serviço...

========================================
  ✅ DEPLOY CONCLUÍDO COM SUCESSO!
========================================

🔗 URL do Serviço:
   https://monpec-XXXXX.us-central1.run.app

📋 Credenciais para Login:
   Username: admin
   Senha: L6171r12@@
```

## ⚠️ Importante

- ✅ O script usa o código **deste diretório local**
- ✅ Certifique-se de que está no diretório correto
- ✅ Não precisa do Cloud Shell
- ✅ Não precisa fazer upload manual

## 🎉 Por que Funciona Agora?

O script usa `gcloud builds submit` que:
1. Pega os arquivos **deste diretório local**
2. Envia para o Google Cloud Build
3. Faz o build com esses arquivos
4. Deploy com a versão mais recente

**Resultado:** A versão na web será **exatamente igual** à local! 🎉

## 🔄 Para Próximas Atualizações

Sempre que quiser atualizar:

1. Faça suas alterações no código
2. Execute: `.\DEPLOY_DEFINITIVO_LOCAL.ps1`
3. Aguarde 10-15 minutos
4. Pronto!

---

**É simples assim! Não precisa mais se preocupar com versões antigas.** 🚀


