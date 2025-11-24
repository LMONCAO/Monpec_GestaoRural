# 🚀 Sair do Prompt e Fazer Deploy

## ✅ Status Atual

O comando `sed` foi executado com sucesso! O `django-logging` foi removido do arquivo.

## 🔧 Sair do Prompt Interativo

O terminal está esperando uma escolha de região. Para sair:

### Opção 1: Cancelar (Recomendado)

Digite no terminal:
```
43
```
(Pressione Enter)

Isso vai cancelar a seleção de região.

### Opção 2: Usar Ctrl+C

Se a opção acima não funcionar:
- Pressione `Ctrl + C` para cancelar o comando atual
- Isso vai retornar ao prompt normal do terminal

---

## 🚀 Após Sair do Prompt

Depois de sair do prompt, execute os comandos de deploy:

### 1. Build da Imagem

```bash
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec
```

### 2. Deploy no Cloud Run

```bash
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated
```

---

## 📋 Comandos Completos (Copiar e Colar)

Se preferir, copie e cole tudo de uma vez:

```bash
# Sair do prompt (se ainda estiver ativo)
43

# Aguardar retornar ao prompt normal, depois:

# Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Deploy
gcloud run deploy monpec --image gcr.io/monpec-sistema-rural/monpec --region us-central1 --platform managed --allow-unauthenticated
```

---

## ✅ Verificação

Após o deploy bem-sucedido:

1. **Testar o arquivo de verificação do Google Search Console:**
   ```
   https://monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html
   ```

2. **Verificar no Google Search Console:**
   - Volte para a tela do Google Search Console
   - Clique em "VERIFICAR"
   - Aguarde a confirmação

---

**🎯 Próximo passo: Digite `43` no terminal para cancelar o prompt e depois execute os comandos de deploy!**










