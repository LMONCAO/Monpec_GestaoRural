# 🚀 Guia: Deploy Completo Perfeito via GitHub + Google Cloud

Este guia explica como fazer um deploy completo mantendo **TUDO** igual ao local: dados, layout, templates, imagens e funcionalidades.

---

## ✅ O Que Será Deployado

- ✅ **Landing Page** completa com todas as imagens (foto1-6.jpeg)
- ✅ **Layout Mobile** otimizado (mostra apenas botões "Demonstração" e "Já sou assinante" no topo)
- ✅ **Formulário de Criação de Usuário Demo** funcionando
- ✅ **Templates** idênticos ao local
- ✅ **Dados Demo** (podem ser populados após deploy)
- ✅ **Arquivos Estáticos** (CSS, JS, imagens) coletados corretamente

---

## 🎯 Passo a Passo Completo

### **Passo 1: Preparar o Código Local**

Certifique-se de que tudo está funcionando localmente:

1. **Verificar templates:**
   - Landing page: `templates/site/landing_page.html`
   - Layout mobile ajustado (só botões no header)

2. **Verificar imagens:**
   - Imagens devem estar em `static/site/`: foto1.jpeg até foto6.jpeg

3. **Verificar formulário demo:**
   - View: `gestao_rural/views.py` → `criar_usuario_demonstracao`
   - URL: `/criar-usuario-demonstracao/`

---

### **Passo 2: Configurar GitHub Actions (Primeira Vez)**

Se ainda não configurou, siga o guia `GUIA_SINCRONIZAR_GITHUB_GCLOUD.md` para:

1. Criar Service Account no Google Cloud
2. Adicionar Secrets no GitHub:
   - `GCP_SA_KEY`
   - `SECRET_KEY`
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`
   - `DJANGO_SUPERUSER_PASSWORD`

---

### **Passo 3: Fazer Deploy via GitHub**

Execute o script:

```cmd
DEPLOY_COMPLETO_PERFEITO.bat
```

**OU** faça manualmente:

```cmd
git add .
git commit -m "Deploy completo: atualização de templates, layout mobile e configurações"
git push origin master
```

O workflow `.github/workflows/deploy-completo.yml` será executado automaticamente!

---

### **Passo 4: Acompanhar o Deploy**

1. Acesse: https://github.com/LMONCAO/Monpec_GestaoRural/actions
2. Clique no workflow mais recente
3. Acompanhe os logs em tempo real
4. Aguarde conclusão (10-20 minutos)

---

### **Passo 5: Executar Migrações e Criar Admin**

Após o deploy completar:

```cmd
EXECUTAR_MIGRACOES_E_CRIAR_ADMIN.bat
```

Isso vai:
- ✅ Criar todas as tabelas no banco
- ✅ Criar usuário admin
- ✅ Popular dados demo (opcional)

---

### **Passo 6: Popular Dados Demo (Opcional)**

Para popular dados demo para demonstração:

**No Cloud Shell ou via Cloud Run Jobs:**

```bash
# Criar/executar job para popular dados
gcloud run jobs create popular-dados-demo \
    --image=gcr.io/monpec-sistema-rural/monpec:latest \
    --region=us-central1 \
    --add-cloudsql-instances=monpec-sistema-rural:us-central1:monpec-db \
    --set-env-vars "DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp,DEBUG=False,SECRET_KEY=...,DB_NAME=monpec_db,DB_USER=monpec_user,DB_PASSWORD=...,GOOGLE_CLOUD_PROJECT=monpec-sistema-rural" \
    --memory=2Gi \
    --cpu=2 \
    --command=sh \
    --args=-c,"python manage.py migrate --noinput && python manage.py popular_monpec1_demo --force"

# Executar o job
gcloud run jobs execute popular-dados-demo --region=us-central1 --wait
```

---

## 🔍 Verificar se Tudo Funcionou

### **1. Landing Page**
- Acesse a URL do Cloud Run (ex: `https://monpec-xxxxx-uc.a.run.app`)
- Verifique se as imagens aparecem no slideshow
- Teste no celular: deve mostrar só os botões no topo

### **2. Formulário Demo**
- Clique em "Demonstração" na landing page
- Preencha o formulário
- Verifique se o usuário é criado e redirecionado para login

### **3. Layout Mobile**
- Abra no celular ou use DevTools (F12 → Toggle device toolbar)
- No header, deve aparecer apenas:
  - Logo
  - Botão "Demonstração"
  - Botão "Já sou assinante"
- Links "Início", "Soluções", etc. devem estar ocultos

### **4. Admin**
- Faça login com: `admin` / `L6171r12@@`
- Verifique se tudo está funcionando

---

## 🎨 Ajustes de Layout Mobile

O layout mobile foi otimizado para mostrar apenas os botões principais no header:

**CSS aplicado:**
- Em telas menores que 768px, links de navegação são ocultados
- Apenas botões "Demonstração" e "Já sou assinante" ficam visíveis
- Logo e botões ficam em linha horizontal compacta

**Para ajustar mais:**
- Edite `templates/site/landing_page.html`
- Procure por `@media (max-width: 768px)`
- Ajuste conforme necessário

---

## 📋 Checklist de Deploy

Antes de fazer deploy, verifique:

- [ ] Templates atualizados e funcionando localmente
- [ ] Imagens em `static/site/` (foto1-6.jpeg)
- [ ] Layout mobile testado localmente
- [ ] Formulário demo funcionando localmente
- [ ] GitHub Actions configurado (se primeira vez)
- [ ] Secrets configurados no GitHub
- [ ] Código commitado e push feito
- [ ] Deploy acompanhado no GitHub Actions
- [ ] Migrações executadas
- [ ] Admin criado
- [ ] Dados demo populados (se necessário)
- [ ] Sistema testado em produção

---

## ⚠️ Problemas Comuns

### **Imagens não aparecem**
- Verifique se estão em `static/site/`
- Execute `collectstatic` localmente para testar
- Verifique logs do Cloud Run para erros

### **Layout mobile não funciona**
- Limpe cache do navegador (Ctrl+F5)
- Verifique se o CSS está sendo carregado
- Teste em dispositivo real ou DevTools

### **Formulário demo não funciona**
- Verifique logs do Cloud Run
- Verifique se a URL `/criar-usuario-demonstracao/` está configurada
- Verifique CSRF tokens

### **Dados não aparecem**
- Execute migrações: `EXECUTAR_MIGRACOES_E_CRIAR_ADMIN.bat`
- Popule dados demo se necessário
- Verifique conexão com banco

---

## 🎯 Resultado Final

Após seguir todos os passos:

✅ **Landing page** funcionando perfeitamente
✅ **Imagens** aparecendo no slideshow
✅ **Layout mobile** otimizado (só botões no topo)
✅ **Formulário demo** criando usuários
✅ **Templates** idênticos ao local
✅ **Dados demo** disponíveis (se populados)
✅ **Sistema completo** funcionando

---

## 📞 Próximos Passos

1. Teste tudo no ambiente de produção
2. Configure monitoramento (opcional)
3. Configure domínio personalizado (opcional)
4. Configure backup automático (opcional)

---

**✅ Pronto! Seu deploy completo está configurado e funcionando!**

A cada push no GitHub, o sistema será atualizado automaticamente mantendo tudo igual ao local! 🚀

