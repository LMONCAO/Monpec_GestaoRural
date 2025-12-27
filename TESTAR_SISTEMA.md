# ✅ Como Verificar se o Deploy Funcionou

## 🚀 Método Rápido (1 comando)

No Cloud Shell, execute:

```bash
chmod +x VERIFICAR_DEPLOY.sh && ./VERIFICAR_DEPLOY.sh
```

Este comando verifica tudo automaticamente e mostra o resultado!

---

## 📋 Verificação Manual (Passo a Passo)

### **1. Verificar se o serviço existe**

```bash
gcloud run services list --region us-central1
```

**Resultado esperado:** Você deve ver `monpec` na lista

---

### **2. Obter URL do serviço**

```bash
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

**Resultado esperado:** Uma URL como `https://monpec-xxxxx-uc.a.run.app`

---

### **3. Verificar status**

```bash
gcloud run services describe monpec --region us-central1 --format="table(status.conditions[0].type,status.conditions[0].status)"
```

**Resultado esperado:** Status deve ser `True`

---

### **4. Ver logs (últimas 30 linhas)**

```bash
gcloud run services logs read monpec --region us-central1 --limit=30
```

**O que procurar:**
- ✅ `200 OK` ou `GET /` - Sistema funcionando
- ❌ `500 Internal Server Error` - Erro na aplicação
- ❌ `Database connection failed` - Problema com banco
- ❌ `ModuleNotFoundError` - Dependência faltando

---

### **5. Testar no navegador**

1. Copie a URL obtida no passo 2
2. Abra no navegador
3. Você deve ver a página inicial do sistema

**Se aparecer:**
- ✅ Página do sistema → **FUNCIONOU!** 🎉
- ❌ "Internal Server Error" → Veja os logs (passo 4)
- ❌ Página em branco → Veja os logs (passo 4)
- ❌ Timeout → Serviço pode não estar rodando

---

## 🔍 Verificações Específicas

### **Verificar se o build foi concluído**

```bash
gcloud builds list --limit=5
```

Procure por builds com status `SUCCESS`

---

### **Verificar variáveis de ambiente**

```bash
gcloud run services describe monpec --region us-central1 --format="yaml(spec.template.spec.containers[0].env)"
```

Verifique se todas as variáveis estão configuradas:
- `DJANGO_SETTINGS_MODULE`
- `SECRET_KEY`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `CLOUD_SQL_CONNECTION_NAME`

---

### **Verificar conexão com Cloud SQL**

```bash
gcloud sql instances describe monpec-db
```

Verifique se a instância está rodando

---

## ✅ Checklist de Sucesso

- [ ] Serviço aparece na lista de serviços
- [ ] URL é retornada corretamente
- [ ] Status do serviço é `True`
- [ ] Logs não mostram erros críticos
- [ ] Página abre no navegador
- [ ] Sistema carrega corretamente
- [ ] Login funciona (se testar)

---

## 🐛 Problemas Comuns

### **Erro: "Service not found"**

O deploy não foi concluído. Execute o deploy novamente.

### **Erro: "500 Internal Server Error"**

1. Veja os logs: `gcloud run services logs read monpec --region us-central1 --limit=50`
2. Procure por erros específicos
3. Verifique se as migrações foram aplicadas

### **Erro: "Database connection failed"**

1. Verifique se Cloud SQL está rodando
2. Verifique as variáveis de ambiente
3. Verifique se o Cloud SQL está conectado ao serviço

### **Erro: "Module not found"**

1. Verifique o `requirements.txt`
2. Faça build novamente
3. Verifique os logs do build

---

## 🎯 Resumo

**Comando mais rápido:**
```bash
./VERIFICAR_DEPLOY.sh
```

**Ou manualmente:**
```bash
gcloud run services describe monpec --region us-central1 --format="value(status.url)"
```

Depois abra a URL no navegador!

---

**Se tudo estiver OK, você verá o sistema funcionando na URL fornecida!** 🎉









