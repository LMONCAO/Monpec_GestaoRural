# 🌐 Configurar Domínio - Comando Direto

## ⚡ Execute Este Comando no Cloud Shell

Copie e cole este comando completo:

```bash
gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1 && gcloud run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1 && echo "" && echo "========================================" && echo "✅ Domínios mapeados com sucesso!" && echo "========================================" && echo "" && echo "📋 Agora configure o DNS no seu provedor:" && echo "" && gcloud run domain-mappings describe monpec.com.br --region us-central1
```

---

## 📋 Ou Execute Passo a Passo

### 1. Mapear domínio principal
```bash
gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1
```

### 2. Mapear www (opcional)
```bash
gcloud run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1
```

### 3. Ver instruções de DNS
```bash
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

---

## 🔍 O que o comando faz:

1. ✅ Mapeia `monpec.com.br` para o serviço Cloud Run
2. ✅ Mapeia `www.monpec.com.br` para o serviço Cloud Run
3. ✅ Mostra as instruções de DNS que você precisa configurar

---

## 📝 Próximos Passos:

1. **Execute o comando acima no Cloud Shell**
2. **Copie as instruções de DNS** que aparecerem
3. **Configure no seu provedor de domínio** (Registro.br, GoDaddy, etc.)
4. **Aguarde propagação DNS** (15 min a 48h)
5. **Teste:** https://monpec.com.br

---

**Dica:** O arquivo `COMANDO_DOMINIO_CLOUD_SHELL.txt` contém o comando completo para copiar facilmente!














