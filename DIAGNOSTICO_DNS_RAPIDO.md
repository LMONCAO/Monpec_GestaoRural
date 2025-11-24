# 🔍 Diagnóstico Rápido de DNS - monpec.com.br

## ⚠️ Problema Comum

Se o site `https://monpec-29862706245.us-central1.run.app/` funciona, mas `https://monpec.com.br` não funciona, o problema está na configuração de DNS no Registro.br.

---

## ✅ Checklist de Verificação

### 1. O domínio está mapeado no Google Cloud Run?

**Execute no Cloud Shell ou PowerShell:**

```powershell
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

**Se der erro "NOT_FOUND":**
- ❌ O domínio NÃO está mapeado
- ✅ **Solução:** Mapeie primeiro (veja passo 2)

**Se mostrar informações:**
- ✅ O domínio está mapeado
- ✅ Anote os registros DNS que aparecem na saída
- ✅ Vá para o passo 3

---

### 2. Mapear Domínio no Cloud Run (se ainda não mapeou)

**Execute este comando:**

```powershell
gcloud run domain-mappings create `
    --service monpec `
    --domain monpec.com.br `
    --region us-central1
```

**⚠️ IMPORTANTE:** Após executar, o Google Cloud vai mostrar os registros DNS que você precisa adicionar no Registro.br. **ANOTE TODOS!**

**Exemplo do que você verá:**

```
status:
  conditions:
  - status: 'True'
    type: Ready
  resourceRecords:
  - name: monpec.com.br
    rrdata: 151.101.1.195
    type: A
  - name: www.monpec.com.br
    rrdata: ghs.googlehosted.com
    type: CNAME
```

---

### 3. Verificar o que está configurado no Registro.br

**No painel do Registro.br:**

1. Acesse: https://registro.br/painel/
2. Procure por: **"Zona DNS"** ou **"Registros DNS"**
3. Verifique quais registros estão configurados

**Se você NÃO encontrar "Zona DNS":**
- Clique em **"UTILIZAR DNS DO REGISTRO.BR"** (botão cinza)
- Aguarde alguns minutos
- Atualize a página (F5)
- Agora deve aparecer a seção "Zona DNS"

---

### 4. Configuração Correta no Registro.br

**Você precisa adicionar os registros EXATOS que o Google Cloud forneceu!**

**⚠️ NÃO use valores genéricos como `ghs.googlehosted.com` sem verificar primeiro!**

**O Google Cloud fornece valores específicos, por exemplo:**

```
Registro A:
- Tipo: A
- Nome: @ (ou monpec.com.br)
- Valor: 151.101.1.195 (IP específico fornecido pelo Google)
- TTL: 3600

Registro CNAME (para www):
- Tipo: CNAME
- Nome: www
- Valor: ghs.googlehosted.com (ou outro valor fornecido)
- TTL: 3600
```

**⚠️ IMPORTANTE:** 
- Use os valores EXATOS que aparecem quando você mapeia o domínio no Cloud Run
- Não use valores de exemplo ou de outros tutoriais
- Cada mapeamento gera valores únicos

---

### 5. Verificar Propagação DNS

**Aguarde 15 minutos - 2 horas após configurar no Registro.br**

**Verificar propagação:**

1. Acesse: https://dnschecker.org
2. Digite: `monpec.com.br`
3. Selecione: Tipo **A**
4. Clique em **"Search"**
5. Verifique se o IP correto aparece em vários servidores DNS

**Se o IP aparecer em vários servidores:**
- ✅ DNS propagado corretamente
- ✅ Teste o acesso: https://monpec.com.br

**Se o IP não aparecer ou estiver errado:**
- ❌ Verifique se os registros foram salvos corretamente no Registro.br
- ❌ Confira se os valores estão exatamente como o Google Cloud forneceu
- ❌ Aguarde mais um pouco (pode levar até 2 horas)

---

## 🆘 Problemas Comuns e Soluções

### Problema 1: "Não encontro a seção Zona DNS no Registro.br"

**Solução:**
- Ligue para o suporte do Registro.br: **0800 777 0001**
- Peça para ativar o "DNS Hosting" ou "Zona DNS" para monpec.com.br
- Eles vão te ajudar a encontrar onde adicionar os registros

---

### Problema 2: "Adicionei os registros mas ainda não funciona"

**Verifique:**

1. ✅ Os valores estão EXATAMENTE como o Google Cloud forneceu?
2. ✅ Os registros foram salvos corretamente no Registro.br?
3. ✅ Aguardou pelo menos 15 minutos após salvar?
4. ✅ Verificou a propagação em https://dnschecker.org?

**Se tudo estiver correto:**
- Aguarde mais um pouco (pode levar até 2 horas)
- O SSL/HTTPS pode levar até 24 horas para aparecer

---

### Problema 3: "Usei ghs.googlehosted.com mas não funciona"

**Causa comum:**
- Você pode ter usado um valor genérico sem mapear o domínio primeiro
- O Google Cloud precisa gerar valores específicos para seu domínio

**Solução:**
1. Mapeie o domínio no Cloud Run primeiro (passo 2)
2. Use os valores EXATOS que o Google Cloud fornecer
3. Não use valores de exemplo ou tutoriais

---

### Problema 4: "O site funciona por IP mas não por domínio"

**Isso significa:**
- ✅ O Cloud Run está funcionando
- ❌ O DNS não está configurado corretamente

**Solução:**
- Siga todos os passos acima
- Certifique-se de mapear o domínio no Cloud Run primeiro
- Use os valores exatos fornecidos pelo Google Cloud

---

## 📋 Comandos Úteis

### Verificar mapeamento de domínio:

```powershell
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

### Listar todos os mapeamentos:

```powershell
gcloud run domain-mappings list --region us-central1
```

### Verificar propagação DNS (Windows):

```powershell
nslookup monpec.com.br
```

### Verificar propagação DNS (Online):

- https://dnschecker.org
- https://www.whatsmydns.net

---

## ✅ Resultado Esperado

Após configurar tudo corretamente:

- ✅ `https://monpec.com.br` → Acessa seu site no Cloud Run
- ✅ `https://www.monpec.com.br` → Acessa seu site no Cloud Run
- ✅ SSL/HTTPS funciona automaticamente (pode levar até 24 horas)
- ✅ Certificado SSL aparece (cadeado verde no navegador)

---

## 📞 Suporte

**Registro.br:**
- Telefone: **0800 777 0001**
- Email: suporte@registro.br
- Chat: Disponível no site do Registro.br

**Google Cloud:**
- Documentação: https://cloud.google.com/run/docs/mapping-custom-domains
- Suporte: Através do console do Google Cloud

---

## 🎯 Resumo Rápido

1. **PRIMEIRO:** Mapeie o domínio no Cloud Run e anote os registros DNS
2. **SEGUNDO:** No Registro.br, encontre/ative a seção "Zona DNS"
3. **TERCEIRO:** Adicione os registros A e CNAME EXATOS fornecidos pelo Cloud Run
4. **QUARTO:** Aguarde a propagação DNS (15 min - 2 horas)
5. **QUINTO:** Teste o acesso e aguarde o SSL (até 24 horas)

---

**⚠️ LEMBRE-SE:** Use os valores EXATOS que o Google Cloud fornece quando você mapeia o domínio. Não use valores genéricos ou de exemplo!










