# 🌐 Configurar Domínio monpec.com.br no Google Cloud Run

## 📋 Pré-requisitos

- Domínio `monpec.com.br` registrado
- Acesso ao painel DNS do provedor do domínio
- Acesso ao Google Cloud Console com permissões de administrador
- Google Cloud CLI instalado (opcional, para comandos via terminal)

## 🚀 Passo a Passo Completo

### **PASSO 1: Mapear Domínio no Cloud Run** (5-10 minutos)

#### **Opção A: Via Console Web (Recomendado)**

1. **Acesse o Console do Google Cloud:**
   - Vá para: https://console.cloud.google.com/run
   - Selecione o projeto correto (verifique qual é o seu projeto)
   - Clique no serviço: `monpec`

2. **Adicionar Mapeamento de Domínio:**
   - Clique na aba **"DOMÍNIOS CUSTOMIZADOS"** (ou "Custom Domains")
   - Clique em **"ADICIONAR Mapeamento de Domínio"** (ou "Add Mapping")
   - Digite: `monpec.com.br`
   - Clique em **"CONTINUAR"** (ou "Continue")

3. **Anotar os Registros DNS:**
   - O Google Cloud mostrará os registros DNS que você precisa adicionar
   - **⚠️ ANOTE TODOS OS REGISTROS** (geralmente são 2-4 registros)
   - Você receberá registros do tipo:
     - **Tipo A** - para o domínio principal (@)
     - **Tipo AAAA** - para IPv6 (se aplicável)
     - **Tipo CNAME** - para www (subdomínio)

#### **Opção B: Via Linha de Comando (gcloud)**

```powershell
# Listar serviços do Cloud Run
gcloud run services list --region us-central1

# Criar mapeamento de domínio
gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1

# Ver os registros DNS necessários
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

### **PASSO 2: Configurar DNS no Provedor do Domínio** (10-15 minutos)

1. **Acesse o painel do seu provedor de domínio:**
   - Onde você comprou o domínio `monpec.com.br`
   - Procure por: **"DNS"**, **"Zona DNS"**, **"Gerenciar DNS"**, **"Registros DNS"** ou similar
   - Provedores comuns: Registro.br, Locaweb, Hostinger, GoDaddy, Namecheap, etc.

2. **Adicionar os Registros DNS:**
   - ⚠️ **Adicione EXATAMENTE os registros fornecidos pelo Google Cloud**
   - ⚠️ **NÃO use exemplos abaixo - use os valores que o Google Cloud forneceu**
   - Geralmente incluem:
     - **Tipo A** - para o domínio principal (nome: `@` ou `monpec.com.br`)
     - **Tipo AAAA** - para IPv6 (se fornecido)
     - **Tipo CNAME** - para subdomínio www (nome: `www`)

3. **Exemplo de Como os Registros Devem Ser Adicionados:**

   **Para Registro.br ou similares:**
   ```
   Tipo: A
   Nome/Host: @
   Valor/Destino: [IP fornecido pelo Google Cloud]
   TTL: 3600
   
   Tipo: CNAME
   Nome/Host: www
   Valor/Destino: ghs.googlehosted.com
   TTL: 3600
   ```

4. **Verificar antes de salvar:**
   - ✅ Nome do registro está correto
   - ✅ Tipo de registro está correto
   - ✅ Valor/Destino está EXATAMENTE como fornecido pelo Google Cloud
   - ✅ TTL está configurado (3600 ou valor sugerido)

5. **Salvar e Aguardar:**
   - Salve todos os registros
   - As alterações DNS geralmente levam alguns minutos para serem aplicadas

### **PASSO 3: Aguardar Propagação DNS** (5 minutos - 48 horas)

- ⏱️ **Propagação típica:** 15 minutos - 2 horas
- ⏱️ **Pode levar até:** 24-48 horas em casos raros
- 🔍 **Verificar propagação:**
  - Use: https://dnschecker.org
  - Digite: `monpec.com.br`
  - Selecione: **Tipo A** e verifique se aparece o IP correto em vários servidores DNS
  - Verifique também: `www.monpec.com.br` (tipo CNAME)

**Dica:** Você pode reduzir o tempo de propagação diminuindo o TTL ANTES de fazer as mudanças (altere para 300 por algumas horas, depois volte para 3600).

### **PASSO 4: Verificar Configuração** (5 minutos)

Após a propagação DNS, verifique o status:

#### **Via Console Web:**
1. Acesse: https://console.cloud.google.com/run
2. Vá para a aba **"DOMÍNIOS CUSTOMIZADOS"**
3. Verifique se o status mostra **"Ativo"** ou **"Active"** (não mais "Pendente")

#### **Via Linha de Comando:**

```powershell
# Verificar status do mapeamento de domínio
gcloud run domain-mappings describe monpec.com.br --region us-central1

# Listar todos os domínios mapeados
gcloud run domain-mappings list --region us-central1

# Verificar se o domínio está apontando corretamente
nslookup monpec.com.br
```

### **PASSO 5: Configurar HTTPS/SSL** (Automático pelo Google Cloud)

O Google Cloud configura o certificado SSL automaticamente através do Let's Encrypt. 

⏱️ **Tempo de emissão:** 15 minutos - 24 horas após a propagação DNS

**Status do SSL:**
- O certificado SSL é emitido automaticamente
- Não é necessário configurar manualmente
- Verifique o status no Console do Cloud Run na aba "DOMÍNIOS CUSTOMIZADOS"

### **PASSO 6: Testar Acesso** (2 minutos)

1. **Acesse no navegador:**
   - `https://monpec.com.br` (sem www)
   - `https://www.monpec.com.br` (com www)

2. **Verificações:**
   - ✅ Site carrega corretamente
   - ✅ Certificado SSL está ativo (cadeado verde/seguro no navegador)
   - ✅ URL mostra `https://` (não `http://`)
   - ✅ Não aparece aviso de "Site não seguro"

3. **Se o SSL ainda não estiver ativo:**
   - Aguarde mais algumas horas (até 24 horas)
   - O Google Cloud emite automaticamente o certificado
   - Você pode verificar o status no Console do Cloud Run

## ⚠️ Troubleshooting - Resolução de Problemas

### **❌ Domínio não funciona após 48 horas:**

**Verificações:**
1. ✅ Verifique se os registros DNS foram salvos corretamente no provedor
2. ✅ Confirme que os valores estão EXATAMENTE como o Google Cloud forneceu
3. ✅ Verifique se não há erros de digitação nos registros
4. ✅ Confirme que o TTL está configurado (recomendado: 3600)
5. ✅ Use https://dnschecker.org para verificar propagação global

**Soluções:**
- Remova e recrie os registros DNS
- Entre em contato com o suporte do seu provedor de domínio
- Verifique se há algum firewall bloqueando as requisições

### **❌ Erro de certificado SSL não emitido:**

**Verificações:**
1. ✅ Verifique se o DNS já propagou completamente (use dnschecker.org)
2. ✅ Confirme que os registros DNS estão corretos
3. ✅ Verifique o status no Console do Cloud Run

**Soluções:**
- Aguarde até 24 horas após a propagação DNS completa
- Se persistir, remova e recrie o mapeamento de domínio
- Verifique se há problemas de conectividade entre o Google Cloud e seu domínio

### **❌ Site carrega mas mostra erro 404 ou página em branco:**

**Verificações:**
1. ✅ Verifique se o serviço Cloud Run está funcionando:
   ```powershell
   gcloud run services describe monpec --region us-central1
   ```

2. ✅ Verifique os logs do serviço:
   ```powershell
   gcloud run services logs read monpec --region us-central1 --limit 50
   ```

3. ✅ Confirme que o serviço está acessível pela URL original:
   - Teste: https://monpec-29862706245.us-central1.run.app/

### **❌ Erro 502 Bad Gateway:**

**Soluções:**
- Verifique se o serviço Cloud Run está rodando
- Verifique os logs para identificar erros na aplicação
- Confirme que o Dockerfile e configurações estão corretas

### **❌ www.monpec.com.br não funciona (apenas monpec.com.br funciona):**

**Solução:**
- Certifique-se de que adicionou o registro CNAME para `www`
- No Cloud Run, você pode mapear ambos os domínios separadamente ou usar um redirect

**Para mapear www separadamente:**
```powershell
gcloud run domain-mappings create --service monpec --domain www.monpec.com.br --region us-central1
```

### **🔄 Remover e Recriar Mapeamento (se necessário):**

```powershell
# Remover mapeamento existente
gcloud run domain-mappings delete monpec.com.br --region us-central1

# Recriar mapeamento
gcloud run domain-mappings create --service monpec --domain monpec.com.br --region us-central1

# Ver novos registros DNS
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

## ✅ Pronto! Checklist Final

Após completar todos os passos, seu site estará acessível em:
- ✅ `https://monpec.com.br` (domínio principal)
- ✅ `https://www.monpec.com.br` (subdomínio www)

**Recursos configurados automaticamente:**
- ✅ Certificado SSL/HTTPS (Let's Encrypt)
- ✅ Redirecionamento HTTP → HTTPS
- ✅ Balanceamento de carga global

## 📝 Comandos Úteis para Manutenção

```powershell
# Ver status do serviço
gcloud run services describe monpec --region us-central1

# Ver todos os domínios mapeados
gcloud run domain-mappings list --region us-central1

# Ver detalhes de um domínio específico
gcloud run domain-mappings describe monpec.com.br --region us-central1

# Ver logs do serviço
gcloud run services logs read monpec --region us-central1 --limit 100

# Ver tráfego recente
gcloud run services logs read monpec --region us-central1 --limit 20
```

## 🔐 Segurança

- O Google Cloud gerencia automaticamente os certificados SSL
- Renovação automática dos certificados
- Proteção DDoS básica incluída
- Firewall configurável no Cloud Run

## 📞 Suporte

Se precisar de ajuda adicional:
- **Documentação oficial:** https://cloud.google.com/run/docs/mapping-custom-domains
- **Status do Google Cloud:** https://status.cloud.google.com/
- **Logs do serviço:** Use os comandos acima para diagnosticar problemas

