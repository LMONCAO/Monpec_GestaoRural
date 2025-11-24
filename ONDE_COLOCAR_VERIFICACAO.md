# 📍 Onde Colocar a Verificação - Guia Completo

## ⚠️ IMPORTANTE: Duas Coisas Diferentes!

Existem **DOIS métodos** de verificação, e cada um vai em um lugar diferente:

1. **Meta Tag HTML** → Vai no **template do Django** (NÃO no Registro.br)
2. **Registro TXT DNS** → Vai no **Registro.br** (Zona DNS)

---

## 🎯 Método 1: Meta Tag HTML (Recomendado - Mais Fácil)

### Onde Colocar: NO TEMPLATE DO DJANGO

**NÃO vai no Registro.br!** Vai no arquivo `templates/base.html` do seu projeto Django.

### Passo a Passo:

#### 1. Obter o Código de Verificação

No Cloud Shell, execute:
```bash
gcloud domains verify monpec.com.br --web-resource
```

Isso vai mostrar algo como:
```
Add this HTML tag to the home page of https://monpec.com.br:
<meta name="google-site-verification" content="CODIGO_AQUI" />
```

#### 2. Atualizar o Template Django

1. **Abra o arquivo:** `templates/base.html`
2. **Encontre a seção** `<head>` (geralmente no início do arquivo)
3. **Procure pela meta tag existente:**
   ```html
   <meta name="google-site-verification" content="google40933139f3b0d469.html" />
   ```
4. **Substitua pelo código novo** que o Google Cloud forneceu:
   ```html
   <meta name="google-site-verification" content="CODIGO_AQUI" />
   ```
   (Onde `CODIGO_AQUI` é o código que o comando `gcloud domains verify` mostrou)

#### 3. Fazer Deploy

```bash
# Build
gcloud builds submit --tag gcr.io/monpec-sistema-rural/monpec

# Deploy
gcloud run deploy monpec \
    --image gcr.io/monpec-sistema-rural/monpec \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated
```

#### 4. Verificar

```bash
gcloud domains verify monpec.com.br --web-resource --check
```

---

## 🎯 Método 2: Registro TXT DNS (Alternativa)

### Onde Colocar: NO REGISTRO.BR (Zona DNS)

Este método usa um registro DNS TXT que você adiciona no Registro.br.

### Passo a Passo:

#### 1. Obter o Registro TXT

No Cloud Shell, execute:
```bash
gcloud domains verify monpec.com.br --dns
```

Isso vai mostrar algo como:
```
Add this TXT record to your DNS configuration:
Name: @
Value: google-site-verification=CODIGO_AQUI
```

#### 2. Adicionar no Registro.br

1. **Acesse:** https://registro.br/painel/
2. **Faça login** na sua conta
3. **Selecione o domínio:** `monpec.com.br`
4. **Vá em:** "Zona DNS" ou "Registros DNS"
   - Se não encontrar, clique em "UTILIZAR DNS DO REGISTRO.BR"
5. **Clique em:** "Adicionar Registro" ou "+ Novo Registro"
6. **Preencha:**
   - **Tipo:** Selecione **"TXT"**
   - **Nome/Host:** Digite **"@"** (arrobas) ou deixe em branco
   - **Valor/Destino:** Digite o valor completo que o Google Cloud forneceu
     - Exemplo: `google-site-verification=CODIGO_AQUI`
   - **TTL:** Digite **3600** ou deixe o padrão
7. **Salve** o registro

#### 3. Aguardar Propagação DNS

- Aguarde **15 minutos a 2 horas**
- Verifique propagação em: https://dnschecker.org
- Digite: `monpec.com.br`
- Selecione: Tipo **TXT**
- Verifique se o registro aparece

#### 4. Verificar

```bash
gcloud domains verify monpec.com.br --dns --check
```

---

## 📋 Comparação dos Métodos

| Característica | Meta Tag HTML | Registro TXT DNS |
|----------------|---------------|------------------|
| **Onde colocar** | Template Django | Registro.br |
| **Velocidade** | Mais rápido (só deploy) | Mais lento (aguarda DNS) |
| **Facilidade** | Mais fácil | Requer acesso ao DNS |
| **Recomendado** | ✅ Sim | Se não puder usar meta tag |

---

## 🎯 Qual Método Usar?

### Use Meta Tag HTML se:
- ✅ Você pode fazer deploy rapidamente
- ✅ Você quer verificar rápido
- ✅ Você prefere não mexer no DNS agora

### Use Registro TXT DNS se:
- ✅ Você não pode fazer deploy agora
- ✅ Você já está configurando o DNS no Registro.br
- ✅ Você prefere usar DNS

---

## 📍 Resumo: Onde Cada Coisa Vai

### Meta Tag HTML:
- ❌ **NÃO vai no Registro.br**
- ✅ **Vai em:** `templates/base.html` (template Django)
- ✅ **Depois:** Fazer deploy

### Registro TXT DNS:
- ✅ **Vai no Registro.br** → Zona DNS → Tipo TXT
- ❌ **NÃO vai no template**

---

## 🚀 Recomendação

**Use o Método 1 (Meta Tag HTML)** porque:
- É mais rápido
- Não precisa aguardar propagação DNS
- Você só precisa atualizar o template e fazer deploy

**Passos:**
1. Execute: `gcloud domains verify monpec.com.br --web-resource`
2. Copie a meta tag que aparecer
3. Me envie o código e eu atualizo o `templates/base.html` para você
4. Você faz o deploy
5. Verifica: `gcloud domains verify monpec.com.br --web-resource --check`

---

**🎯 Resumo: A meta tag vai no template Django, NÃO no Registro.br!**












