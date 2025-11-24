# ✅ Deploy Concluído - Testar Verificação do Google Search Console

## 🎉 Status Atual

✅ **Deploy bem-sucedido!**
- Serviço: `monpec`
- Revisão: `monpec-00023-n16`
- URL: `https://monpec-29862706245.us-central1.run.app`

---

## 🔍 Passo 1: Testar o Arquivo de Verificação

### No Navegador

Abra esta URL no seu navegador:

```
https://monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html
```

### O que você deve ver:

O arquivo deve exibir apenas este conteúdo:
```
google-site-verification: google40933139f3b0d469.html
```

### Se funcionar:
✅ O arquivo está acessível e correto!
✅ Você pode prosseguir para a verificação no Google Search Console

### Se não funcionar (404 ou erro):
❌ Verifique se a rota está configurada corretamente
❌ Verifique os logs do Cloud Run

---

## 🔍 Passo 2: Verificar no Google Search Console

1. **Volte para a tela do Google Search Console**
   - A tela onde você baixou o arquivo `google40933139f3b0d469.html`

2. **Clique no botão "VERIFICAR"**

3. **Aguarde alguns segundos**

4. **Resultado esperado:**
   - ✅ **Sucesso:** "Propriedade verificada com sucesso!"
   - ❌ **Erro:** Se der erro, veja a seção de problemas abaixo

---

## 🆘 Problemas Comuns

### Problema 1: "Arquivo não encontrado" (404)

**Solução:**
1. Verifique se a rota está em `sistema_rural/urls.py` linha 39:
   ```python
   path('google40933139f3b0d469.html', gestao_views.google_search_console_verification, name='google_search_console_verification'),
   ```

2. Verifique se a view existe em `gestao_rural/views.py` linha 23

3. Verifique os logs do Cloud Run:
   ```bash
   gcloud run services logs read monpec --region us-central1 --limit 50
   ```

### Problema 2: "Conteúdo incorreto"

**Solução:**
1. O arquivo deve conter exatamente:
   ```
   google-site-verification: google40933139f3b0d469.html
   ```

2. Sem espaços extras ou quebras de linha

3. Verifique a view em `gestao_rural/views.py`:
   ```python
   content = "google-site-verification: google40933139f3b0d469.html"
   ```

### Problema 3: "Verificação falhou"

**Solução:**
1. Aguarde 2-3 minutos após o deploy
2. Tente verificar novamente no Google Search Console
3. Verifique se o arquivo está acessível publicamente (sem autenticação)
4. Verifique se não há redirecionamentos HTTPS/HTTP

---

## 📋 Checklist Final

Antes de verificar no Google Search Console:

- [ ] Deploy concluído com sucesso
- [ ] Arquivo acessível em: `https://monpec-29862706245.us-central1.run.app/google40933139f3b0d469.html`
- [ ] Conteúdo exibido corretamente no navegador
- [ ] Aguardou 2-3 minutos após o deploy
- [ ] Pronto para clicar em "VERIFICAR" no Google Search Console

---

## 🎯 Próximos Passos Após Verificação

Depois que o Google Search Console verificar o domínio com sucesso:

### 1. Configurar Domínio Customizado no Cloud Run

1. Acesse: https://console.cloud.google.com/run
2. Clique no serviço `monpec`
3. Vá na aba **"DOMÍNIOS CUSTOMIZADOS"** ou **"Custom Domains"**
4. Clique em **"ADICIONAR Mapeamento de Domínio"**
5. Digite: `monpec.com.br`
6. Clique em **"CONTINUAR"**
7. **ANOTE os registros DNS** que o Google Cloud fornecer

### 2. Configurar DNS no Registro.br

1. Acesse: https://registro.br/painel/
2. Vá em **"Zona DNS"** ou **"Registros DNS"**
3. Adicione os registros **A** e **CNAME** fornecidos pelo Google Cloud
4. Aguarde propagação (15 min - 2 horas)

### 3. Testar o Domínio

1. Aguarde 15 minutos - 2 horas
2. Acesse: `https://monpec.com.br`
3. Verifique se o site carrega corretamente
4. O SSL pode levar até 24 horas para aparecer

---

## 🚀 Comandos Úteis

### Ver Logs do Cloud Run

```bash
gcloud run services logs read monpec --region us-central1 --limit 50
```

### Ver Logs em Tempo Real

```bash
gcloud run services logs tail monpec --region us-central1
```

### Verificar Status do Serviço

```bash
gcloud run services describe monpec --region us-central1
```

---

**🎉 Deploy concluído! Agora teste o arquivo de verificação e complete a verificação no Google Search Console!**
