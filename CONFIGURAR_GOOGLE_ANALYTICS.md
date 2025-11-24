# 📊 Configurar Google Analytics no MONPEC

## ✅ O que foi implementado

1. **Configuração no Django Settings**
   - Adicionada variável `GOOGLE_ANALYTICS_ID` em `sistema_rural/settings.py`
   - Configuração também disponível em `sistema_rural/settings_gcp.py` para produção

2. **Context Processor**
   - Adicionado `google_analytics_id` ao context processor
   - Disponível em todos os templates automaticamente

3. **Tags do Google Analytics**
   - Adicionadas nos templates principais:
     - `templates/base.html`
     - `templates/base_identidade_visual.html`
     - `templates/site/landing_page.html`

4. **Domínio Configurado**
   - `monpec.com.br` já está em `ALLOWED_HOSTS` no `settings_gcp.py`
   - `www.monpec.com.br` também configurado
   - CSRF_TRUSTED_ORIGINS configurado para HTTPS

---

## 🚀 Como Configurar

### **Opção 1: Variável de Ambiente (Recomendado para Produção)**

#### **No Google Cloud Run:**

```bash
# Definir variável de ambiente no Cloud Run
gcloud run services update monpec \
    --region us-central1 \
    --update-env-vars GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

**Substitua `G-XXXXXXXXXX` pelo seu ID de medição do Google Analytics 4**

#### **Via Console Web do Google Cloud:**

1. Acesse [Google Cloud Console](https://console.cloud.google.com)
2. Vá em **Cloud Run** > Selecione o serviço `monpec`
3. Clique em **Edit & Deploy New Revision**
4. Vá na aba **Variables & Secrets**
5. Adicione:
   - **Name:** `GOOGLE_ANALYTICS_ID`
   - **Value:** `G-XXXXXXXXXX` (seu ID do Google Analytics)
6. Clique em **Deploy**

---

### **Opção 2: Arquivo .env (Desenvolvimento Local)**

Crie um arquivo `.env` na raiz do projeto:

```bash
GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

E configure o Django para ler o arquivo `.env` (se ainda não estiver configurado).

---

### **Opção 3: Direto no settings.py (Apenas para Teste)**

⚠️ **Não recomendado para produção!**

Edite `sistema_rural/settings.py`:

```python
GOOGLE_ANALYTICS_ID = 'G-XXXXXXXXXX'  # Substitua pelo seu ID
```

---

## 📋 Como Obter o ID do Google Analytics

1. Acesse [Google Analytics](https://analytics.google.com)
2. Selecione sua propriedade (ou crie uma nova)
3. Vá em **Administrador** (ícone de engrenagem)
4. Em **Propriedade**, clique em **Informações da propriedade**
5. Copie o **ID de medição** (formato: `G-XXXXXXXXXX`)

---

## ✅ Verificar se Está Funcionando

### **1. Verificar no Código-Fonte**

1. Acesse seu site: `https://monpec.com.br`
2. Pressione **Ctrl+U** (ou botão direito → "Ver código-fonte")
3. Procure por: `gtag.js` ou `googletagmanager.com`
4. Deve aparecer algo como:
   ```html
   <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
   ```

### **2. Verificar no Google Analytics**

1. Acesse [Google Analytics](https://analytics.google.com)
2. Vá em **Relatórios** > **Tempo Real**
3. Acesse seu site em outra aba
4. Você deve ver sua visita aparecer em tempo real

### **3. Usar Google Tag Assistant**

1. Instale a extensão [Google Tag Assistant](https://chrome.google.com/webstore/detail/tag-assistant-legacy-by-g/kejbdjndbnbjgmefkgdddjlbokphdefk)
2. Acesse seu site
3. Clique no ícone da extensão
4. Deve mostrar o Google Analytics como "Detected"

---

## 🔧 Troubleshooting

### **Problema: Tag não aparece no código-fonte**

**Solução:**
- Verifique se a variável `GOOGLE_ANALYTICS_ID` está definida
- Verifique se o valor não está vazio
- Limpe o cache do navegador (Ctrl+Shift+Delete)
- Verifique os logs do Django para erros

### **Problema: Google Analytics não está rastreando**

**Solução:**
- Verifique se o ID está correto (formato: `G-XXXXXXXXXX`)
- Verifique se não há bloqueadores de anúncios ativos
- Aguarde alguns minutos (pode levar até 24h para aparecer dados)
- Verifique se está usando HTTPS (necessário para GA4)

### **Problema: Erro no console do navegador**

**Solução:**
- Verifique se o ID do Google Analytics está correto
- Verifique se não há conflitos com outros scripts
- Verifique a console do navegador (F12) para erros JavaScript

---

## 📝 Resumo das Alterações

### **Arquivos Modificados:**

1. `sistema_rural/settings.py`
   - Adicionada configuração `GOOGLE_ANALYTICS_ID`

2. `sistema_rural/settings_gcp.py`
   - Adicionada configuração `GOOGLE_ANALYTICS_ID` para produção

3. `gestao_rural/context_processors.py`
   - Adicionado `google_analytics_id` ao contexto

4. `templates/base.html`
   - Adicionada tag do Google Analytics

5. `templates/base_identidade_visual.html`
   - Adicionada tag do Google Analytics

6. `templates/site/landing_page.html`
   - Adicionada tag do Google Analytics

---

## 🎯 Próximos Passos

1. ✅ Obter ID do Google Analytics
2. ✅ Configurar variável de ambiente no Cloud Run
3. ✅ Fazer novo deploy (se necessário)
4. ✅ Verificar se a tag está aparecendo no site
5. ✅ Aguardar dados no Google Analytics (pode levar algumas horas)

---

## 📚 Referências

- [Google Analytics 4 - Documentação](https://developers.google.com/analytics/devguides/collection/ga4)
- [Google Tag Manager - Documentação](https://developers.google.com/tag-manager)
- [Configurar Google Analytics no Django](https://docs.djangoproject.com/en/stable/topics/settings/)

---

**Última atualização:** Dezembro 2025












