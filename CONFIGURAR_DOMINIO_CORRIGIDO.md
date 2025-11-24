# 🌐 Configurar Domínio - Comando Corrigido

## ⚠️ Erro Resolvido

O comando precisa usar `gcloud beta` em vez de `gcloud` para a flag `--region`.

## ✅ Comando Corrigido

Execute este comando no Cloud Shell:

```bash
gcloud beta run domain-mappings create --service monpec --domain monpec.com.br --region us-central1 && gcloud beta run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1 && echo "" && echo "========================================" && echo "✅ Domínios mapeados com sucesso!" && echo "========================================" && echo "" && echo "📋 Agora configure o DNS no seu provedor:" && echo "" && gcloud beta run domain-mappings describe monpec.com.br --region us-central1
```

---

## 📋 Ou Execute Passo a Passo

### 1. Mapear domínio principal
```bash
gcloud beta run domain-mappings create --service monpec --domain monpec.com.br --region us-central1
```

### 2. Mapear www (opcional)
```bash
gcloud beta run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1
```

### 3. Ver instruções de DNS
```bash
gcloud beta run domain-mappings describe monpec.com.br --region us-central1
```

---

## 🔍 Diferença

- ❌ **Errado:** `gcloud run domain-mappings create --region ...`
- ✅ **Correto:** `gcloud beta run domain-mappings create --region ...`

---

## 📝 Próximos Passos

1. **Execute o comando corrigido acima**
2. **Copie as instruções de DNS** que aparecerem
3. **Configure no seu provedor de domínio** (Registro.br, etc.)
4. **Aguarde propagação DNS** (15 min a 48h)
5. **Teste:** https://monpec.com.br

---

**O arquivo `COMANDO_DOMINIO_CORRIGIDO.txt` contém o comando completo!**













