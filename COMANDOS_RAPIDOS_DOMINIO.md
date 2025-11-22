# 🚀 Comandos Rápidos - Configurar monpec.com.br

## ⚡ Configuração Rápida (1 comando)

```bash
gcloud run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1
```

---

## 📋 Depois, configure o DNS:

### No Registro.br ou seu provedor:
- **Tipo:** CNAME
- **Nome:** @ (ou monpec.com.br)
- **Valor:** `ghs.googlehosted.com`

---

## ✅ Verificar Status

```bash
# Status do mapeamento
gcloud run domain-mappings describe monpec.com.br --region us-central1

# Verificar DNS
nslookup -type=CNAME monpec.com.br

# Listar todos os mapeamentos
gcloud run domain-mappings list --region us-central1
```

---

## 🔧 Usando Scripts PowerShell

```powershell
# Configurar domínio
.\configurar_dominio_cloud_run.ps1

# Verificar status
.\verificar_dominio_cloud_run.ps1
```

---

## ⏳ Tempo de Propagação

- **Típico:** 1-2 horas
- **Máximo:** 48 horas
- **Verificar:** [whatsmydns.net](https://www.whatsmydns.net/#CNAME/monpec.com.br)

---

**Documentação completa:** `CONFIGURAR_DOMINIO_MONPEC_COM_BR.md`

