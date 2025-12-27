# 🚀 EXECUTAR CONFIGURAÇÃO AGORA - Guia Rápido

## ✅ Execute estes comandos na ordem:

### 1️⃣ Verificar se está tudo pronto (OPCIONAL):
```powershell
.\VERIFICAR_CONFIGURACAO_DEPLOY.ps1
```

### 2️⃣ Executar configuração automática:
```powershell
.\CONFIGURAR_DEPLOY_AUTOMATICO.ps1
```

Este script vai:
- ✅ Verificar/criar Service Account no Google Cloud
- ✅ Configurar todas as permissões necessárias
- ✅ Habilitar APIs necessárias
- ✅ Criar chave JSON para autenticação
- ✅ Adicionar arquivo ao .gitignore

**⏱️ Tempo estimado: 2-3 minutos**

### 3️⃣ Configurar Secret no GitHub:

Após executar o script, você terá um arquivo `github-actions-deploy-key.json`

1. **Abra o arquivo** `github-actions-deploy-key.json` no bloco de notas
2. **Copie TODO o conteúdo** (desde o `{` inicial até o `}` final)
3. **Acesse**: https://github.com/LMONCAO/monpec/settings/secrets/actions
4. **Clique em**: "New repository secret"
5. **Preencha**:
   - Name: `GCP_SA_KEY`
   - Secret: Cole o conteúdo do arquivo JSON
6. **Clique em**: "Add secret"

### 4️⃣ Fazer Push do Código:

```powershell
git add .github/workflows/deploy-gcp.yml
git add *.md
git add .gitignore
git commit -m "Configurar deploy automático GitHub Actions"
git push origin main
```

(Se sua branch for `master`, use: `git push origin master`)

### 5️⃣ Verificar Deploy:

1. **Acesse**: https://github.com/LMONCAO/monpec/actions
2. **Você verá** o workflow executando automaticamente
3. **Clique no workflow** para ver o progresso em tempo real

---

## 🎉 Pronto!

Após esses passos, **todo push para `main` fará deploy automático** no Google Cloud Run!

---

## 🆘 Se algo der errado:

### Erro: "gcloud não encontrado"
- Instale o Google Cloud SDK: https://cloud.google.com/sdk/docs/install

### Erro: "Não autenticado"
- O script vai pedir para fazer login. Siga as instruções na tela.

### Erro: "Permission denied"
- Certifique-se de ter permissões de Owner ou Editor no projeto GCP

### Erro no GitHub: "Secret not found"
- Verifique se o secret foi criado com o nome exato: `GCP_SA_KEY` (tudo maiúsculo)

---

## 📚 Documentação Completa:

- `DEPLOY_AGORA_PASSO_A_PASSO.md` - Guia passo a passo detalhado
- `CONFIGURAR_DEPLOY_AUTOMATICO_GITHUB.md` - Documentação técnica completa

