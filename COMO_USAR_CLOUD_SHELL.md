# 🚀 Como Fazer Deploy Usando Cloud Shell

## ⚠️ IMPORTANTE

O comando em `COMANDO_DEPLOY_UNICO.txt` é para **Cloud Shell (Linux)**, não funciona no PowerShell do Windows!

## ✅ Solução: Usar Cloud Shell

### Passo 1: Abrir Cloud Shell

1. Acesse: **https://console.cloud.google.com/**
2. Clique no ícone do **Cloud Shell** no topo da página (ícone de terminal)
3. Aguarde o terminal abrir (pode levar alguns segundos)

### Passo 2: Copiar e Colar o Comando

1. Abra o arquivo `COMANDO_DEPLOY_UNICO.txt` no seu computador
2. **Selecione TODO o conteúdo** (Ctrl+A)
3. **Copie** (Ctrl+C)
4. **Cole no Cloud Shell** (clique no terminal e cole)
5. **Pressione Enter**

### Passo 3: Aguardar

- Build: ~10-15 minutos
- Deploy: ~2-3 minutos
- **Total: ~15-20 minutos**

### Passo 4: Ver URL

No final, a URL do serviço será exibida automaticamente.

---

## 🔍 Por que Cloud Shell?

- ✅ Já tem gcloud configurado
- ✅ Não precisa instalar nada
- ✅ Conexão direta com Google Cloud
- ✅ Mais rápido que local
- ✅ Funciona em qualquer navegador

---

## 📋 Comando Completo (para referência)

O comando faz tudo automaticamente:
- Atualiza código do GitHub
- Obtém informações do banco
- Gera SECRET_KEY
- Faz build da imagem Docker
- Faz deploy no Cloud Run
- Mostra a URL final

---

**Dica:** Deixe o Cloud Shell aberto durante o processo. Você verá o progresso em tempo real!












