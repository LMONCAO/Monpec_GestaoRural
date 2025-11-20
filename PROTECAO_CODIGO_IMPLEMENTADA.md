# 🛡️ Proteção Contra Cópia de Código - MONPEC

## ✅ O QUE FOI IMPLEMENTADO

### 1️⃣ **Proteção JavaScript no Frontend**

✅ **Bloqueios implementados:**
- ❌ Menu de contexto (botão direito) desabilitado
- ❌ Seleção de texto desabilitada
- ❌ Cópia/Colar/Cortar desabilitados
- ❌ Atalhos bloqueados:
  - F12 (DevTools)
  - Ctrl+Shift+I (DevTools)
  - Ctrl+Shift+J (Console)
  - Ctrl+Shift+C (Inspect)
  - Ctrl+U (View Source)
  - Ctrl+S (Save Page)
  - Ctrl+P (Print)

✅ **Detecção de DevTools:**
- Detecta quando DevTools é aberto
- Bloqueia acesso e exibe mensagem
- Redireciona ou bloqueia página

✅ **Bloqueio de Console:**
- Console.log e métodos desabilitados
- Avisos de segurança no console
- Prevenção de execução de código

---

### 2️⃣ **Middleware de Proteção**

✅ **Proteções no servidor:**
- Bloqueio de user agents suspeitos (scrapers, bots)
- Rate limiting por IP (100 req/min)
- Proteção contra hotlinking
- Headers de segurança (CSP, X-Frame-Options, etc)
- Logs de tentativas de acesso não autorizado

✅ **Headers de segurança:**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Content-Security-Policy` (CSP)
- `Referrer-Policy: strict-origin-when-cross-origin`

---

### 3️⃣ **Watermarking e Rastreamento**

✅ **Watermark invisível:**
- Adicionado em cada página
- Contém timestamp e hash único
- Permite rastrear origem de cópia
- Invisível ao usuário (opacity: 0.01)

---

### 4️⃣ **Proteção de Templates**

✅ **Template tags:**
- `{% protecao_codigo_js %}` - Inclui proteção
- `{% watermark_codigo %}` - Adiciona watermark
- `{% ofuscar_texto %}` - Ofusca dados sensíveis

---

## 🚀 COMO FUNCIONA

### **Proteção no Frontend:**

```javascript
// 1. Bloqueia menu de contexto
document.addEventListener('contextmenu', e => e.preventDefault());

// 2. Bloqueia seleção
document.addEventListener('selectstart', e => e.preventDefault());

// 3. Bloqueia cópia
document.addEventListener('copy', e => e.preventDefault());

// 4. Detecta DevTools
setInterval(() => {
    if (window.outerHeight - window.innerHeight > 160) {
        // DevTools aberto - bloquear
    }
}, 500);
```

### **Proteção no Backend:**

```python
# Middleware verifica:
- User agent suspeito? → Bloquear
- Rate limit excedido? → Bloquear
- Hotlinking detectado? → Bloquear
- Adiciona headers de segurança
```

---

## 📋 ARQUIVOS CRIADOS

- ✅ `gestao_rural/middleware_protecao_codigo.py` - Middleware de proteção
- ✅ `static/js/protecao_codigo.js` - Script de proteção frontend
- ✅ `gestao_rural/templatetags/protecao_codigo.py` - Template tags
- ✅ `gestao_rural/management/commands/minificar_codigo.py` - Minificação

---

## ⚙️ CONFIGURAÇÃO

### **1. Middleware já adicionado ao settings.py**

✅ Middleware `ProtecaoCodigoMiddleware` já configurado

### **2. Template base atualizado**

✅ Proteção JavaScript incluída  
✅ Watermark adicionado

### **3. Apenas em produção**

✅ Proteções ativas apenas quando `DEBUG=False`  
✅ Em desenvolvimento, proteções desabilitadas

---

## 🛡️ PROTEÇÕES ATIVAS

### **Frontend:**
- ✅ Botão direito bloqueado
- ✅ Seleção de texto bloqueada
- ✅ Cópia/Colar bloqueados
- ✅ Atalhos de teclado bloqueados
- ✅ DevTools detectado e bloqueado
- ✅ Console bloqueado
- ✅ Watermark invisível

### **Backend:**
- ✅ Scrapers bloqueados
- ✅ Rate limiting
- ✅ Hotlinking bloqueado
- ✅ Headers de segurança
- ✅ Logs de tentativas

---

## ⚠️ LIMITAÇÕES

**Importante:** Nenhuma proteção frontend é 100% à prova de bypass. Um usuário determinado pode:
- Desabilitar JavaScript
- Usar extensões do navegador
- Modificar código no cliente
- Usar ferramentas avançadas

**Por isso, as proteções incluem:**
- ✅ Logs de tentativas (rastreamento)
- ✅ Watermarking (identificação)
- ✅ Proteção no servidor (mais segura)
- ✅ Rate limiting (prevenção)

---

## 📊 LOGS DE TENTATIVAS

Todas as tentativas de acesso não autorizado são registradas em:
- `/admin/gestao_rural/logauditoria/`
- Tipo: `ACESSO_NAO_AUTORIZADO`
- Nível: `ALTO` ou `CRITICO`

---

## ✅ CHECKLIST

- [x] Middleware de proteção criado
- [x] Script JavaScript de proteção criado
- [x] Template tags criadas
- [x] Template base atualizado
- [x] Middleware adicionado ao settings
- [x] Watermarking implementado
- [x] Headers de segurança configurados
- [ ] Minificação de código (opcional)
- [ ] Testes realizados

---

## 🎯 PRÓXIMOS PASSOS (OPCIONAL)

### **1. Minificar Código:**

```bash
python311\python.exe manage.py minificar_codigo
```

### **2. Ofuscar JavaScript (usando ferramentas externas):**

- UglifyJS
- JavaScript Obfuscator
- Closure Compiler

### **3. Proteção Adicional (se necessário):**

- Licenciamento de software
- Validação de licença online
- Criptografia de código sensível
- Servidor-side rendering para código crítico

---

## 🔒 PROTEÇÕES RECOMENDADAS ADICIONAIS

### **1. Licenciamento:**
- Validar licença no servidor
- Verificar periodicamente
- Bloquear se inválida

### **2. Código Sensível:**
- Manter lógica crítica no servidor
- Não expor APIs sensíveis
- Usar autenticação para todas as APIs

### **3. Monitoramento:**
- Monitorar logs de auditoria
- Alertas para tentativas suspeitas
- Análise de padrões de acesso

---

**Sistema protegido contra cópia básica!**

**Nota:** Para proteção máxima, considere também:
- Licenciamento de software
- Validação online de licença
- Criptografia de código crítico
- Servidor-side rendering






