# ✅ Verificação Google Search Console via Arquivo HTML

A verificação via arquivo HTML foi configurada no Django!

---

## 📋 O que foi configurado

1. **View criada:** `google_search_console_verification()` em `gestao_rural/views.py`
2. **URL configurada:** `/google40933139f3b0d469.html` em `sistema_rural/urls.py`

---

## 🚀 Como usar

### **Passo 1: Fazer Deploy**

Faça o deploy do código atualizado no Google Cloud Run para que a URL fique acessível.

### **Passo 2: Verificar no Google Search Console**

1. Acesse: https://search.google.com/search-console
2. Selecione o método: **"Arquivo HTML"**
3. O arquivo já está configurado em: `https://monpec.com.br/google40933139f3b0d469.html`
4. Clique em **"VERIFICAR"**

### **Passo 3: Testar o Arquivo**

Após o deploy, você pode testar se o arquivo está acessível:

```bash
# Via navegador
https://monpec.com.br/google40933139f3b0d469.html

# Ou via Cloud Run (antes do DNS propagar)
https://monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html
```

**Resultado esperado:** O arquivo deve retornar o conteúdo de verificação.

---

## ⚠️ Se o Google fornecer um arquivo diferente

Se o Google Search Console gerar um arquivo HTML com conteúdo diferente do padrão:

### **Opção 1: Atualizar a view**

1. Baixe o arquivo HTML que o Google fornece
2. Abra o arquivo e copie todo o conteúdo
3. Atualize a view `google_search_console_verification()` em `gestao_rural/views.py`
4. Substitua o conteúdo na variável `content`

### **Opção 2: Usar template (recomendado)**

1. Crie um arquivo: `templates/google40933139f3b0d469.html`
2. Cole o conteúdo exato do arquivo HTML do Google
3. Atualize a view para usar `render()`:

```python
def google_search_console_verification(request):
    return render(request, 'google40933139f3b0d469.html')
```

---

## 🔍 Verificar se está funcionando

Após o deploy, teste a URL:

```powershell
# Testar localmente (se rodar servidor local)
curl http://localhost:8000/google40933139f3b0d469.html

# Testar em produção (após deploy)
curl https://monpec.com.br/google40933139f3b0d469.html
```

**O arquivo deve retornar o conteúdo de verificação do Google.**

---

## 📝 Notas

- ✅ O arquivo deve estar sempre disponível (não remova após verificação)
- ✅ Funciona tanto em HTTP quanto HTTPS
- ✅ Não requer autenticação
- ✅ O Google pode levar alguns minutos para verificar após o deploy

---

**Última atualização:** Dezembro 2025

