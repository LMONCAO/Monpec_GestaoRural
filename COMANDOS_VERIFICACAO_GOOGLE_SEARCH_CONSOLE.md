# 🔍 Comandos Rápidos - Verificação Google Search Console

## 📋 O que você precisa fazer no Registro.br

### **Adicionar Registro TXT:**

1. Acesse: https://registro.br
2. Vá em **"DNS"** ou **"Zona DNS"** (NÃO no campo "Endereço do site")
3. Adicione um novo registro:
   - **Tipo:** `TXT`
   - **Nome:** `@` (ou monpec.com.br)
   - **Valor:** `google-site-verification=vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk`
   - **TTL:** `3600`

---

## ✅ Verificar se está configurado

```powershell
# Verificar registro TXT
nslookup -type=TXT monpec.com.br
```

**Resultado esperado:**
```
monpec.com.br
        text = "google-site-verification=vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk"
```

---

## 🔄 Usar o script de verificação

```powershell
.\verificar_dominio_cloud_run.ps1
```

O script agora verifica:
- ✅ Mapeamento no Cloud Run
- ✅ DNS CNAME (ghs.googlehosted.com)
- ✅ DNS TXT (verificação Google Search Console)
- ✅ Acesso HTTP/HTTPS

---

## ⚠️ Lembrete Importante

**Dois registros diferentes:**

1. **CNAME** (Endereço do site):
   - Campo: "Endereço do site"
   - Valor: `ghs.googlehosted.com`
   - Para: Fazer o domínio funcionar

2. **TXT** (Verificação):
   - Seção: "DNS" / "Zona DNS"
   - Valor: `google-site-verification=vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJIztghk`
   - Para: Verificar no Google Search Console

**Ambos são necessários!**

---

**Documentação completa:** `CONFIGURAR_VERIFICACAO_GOOGLE_SEARCH_CONSOLE.md`

