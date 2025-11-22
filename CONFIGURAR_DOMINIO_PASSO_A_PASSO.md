# 🌐 Como Configurar monpec.com.br - Passo a Passo SUPER SIMPLES

## 🎯 O Que Você Precisa Fazer

**Em resumo:** Você precisa fazer 2 coisas:
1. **No Google Cloud** - Mapear o domínio (para obter os registros DNS)
2. **No Registro.br** - Adicionar os registros DNS fornecidos pelo Google

---

## 📍 PASSO 1: Mapear Domínio no Google Cloud (5 minutos)

### **1.1 - Abrir o Google Cloud Console**

1. Abra seu navegador
2. Vá para: **https://console.cloud.google.com/run**
3. Faça login na sua conta do Google (se necessário)

### **1.2 - Encontrar o Serviço monpec**

1. Se você tiver vários projetos, **selecione o projeto correto** (no topo da tela)
2. Na lista de serviços, procure por **"monpec"**
3. **Clique no serviço "monpec"**

### **1.3 - Adicionar Domínio Customizado**

1. No topo da página do serviço, procure por **abas** (tabs)
2. Procure pela aba **"DOMÍNIOS CUSTOMIZADOS"** ou **"Custom Domains"**
3. **Clique nessa aba**
4. Você verá um botão: **"ADICIONAR Mapeamento de Domínio"** ou **"Add Mapping"**
5. **Clique nesse botão**

### **1.4 - Digitar o Domínio**

1. Aparecerá um campo para digitar o domínio
2. Digite exatamente: **monpec.com.br**
3. Clique em **"CONTINUAR"** ou **"Continue"**

### **1.5 - ANOTAR OS REGISTROS DNS** ⚠️ IMPORTANTE!

Após clicar em "CONTINUAR", o Google vai mostrar uma tela com **REGISTROS DNS** que você precisa adicionar no Registro.br.

**📝 IMPORTANTE: Copie ou anote TODOS esses registros!**

Exemplo do que você verá:
```
Registro A:
Nome: @
Valor: 151.101.1.195

Registro CNAME:
Nome: www
Valor: ghs.googlehosted.com
```

**⚠️ Os valores reais serão DIFERENTES - use os que aparecerem na tela!**

**Dica:** Tire uma foto da tela ou copie os valores para um bloco de notas!

---

## 📍 PASSO 2: Configurar no Registro.br (10 minutos)

### **2.1 - Abrir o Painel do Registro.br**

1. Abra seu navegador
2. Vá para: **https://registro.br/painel/**
3. Faça login na sua conta

### **2.2 - Encontrar a Seção de DNS**

No painel do Registro.br, você precisa encontrar onde adicionar registros DNS.

**Procure por uma dessas opções no menu lateral:**
- **"DNS"** → **"Zona DNS"**
- **"DNS"** → **"Registros DNS"**
- **"Gerenciar"** → **"DNS"**
- **"Gerenciar"** → **"Zona DNS"**

### **2.3 - Se Você NÃO Encontrar "Zona DNS"**

Se você só vê "ALTERAR SERVIDORES DNS" e não vê "Zona DNS":

1. Procure por um botão que diz: **"UTILIZAR DNS DO REGISTRO.BR"** ou **"Ativar DNS Hosting"**
2. **Clique nesse botão**
3. Aguarde alguns minutos
4. **Atualize a página** (F5)
5. Agora você deve ver uma seção para **"Zona DNS"** ou **"Registros DNS"**

### **2.4 - Adicionar o Registro A**

1. Procure por um botão: **"Adicionar Registro"** ou **"+ Novo Registro"** ou **"Adicionar"**
2. **Clique nesse botão**
3. Uma janela ou formulário vai aparecer
4. Preencha com os valores que você anotou do Google Cloud:

   **Tipo:** Selecione **"A"** (ou **"Tipo A"**)
   
   **Nome/Host:** Digite **"@"** (arrobas) ou deixe em branco (depende da interface)
   
   **Valor/Destino:** Digite o **IP** que o Google Cloud forneceu (exemplo: 151.101.1.195)
   
   **TTL:** Digite **3600** ou deixe o valor padrão
   
5. **Salve** ou clique em **"OK"** ou **"Adicionar"**

### **2.5 - Adicionar o Registro CNAME (para www)**

1. **Clique novamente** em **"Adicionar Registro"** ou **"+ Novo Registro"**
2. Preencha com os valores do Google Cloud:

   **Tipo:** Selecione **"CNAME"** (ou **"Tipo CNAME"**)
   
   **Nome/Host:** Digite **"www"** (só www, sem ponto)
   
   **Valor/Destino:** Digite o valor fornecido pelo Google Cloud (geralmente: ghs.googlehosted.com)
   
   **TTL:** Digite **3600** ou deixe o valor padrão
   
3. **Salve** ou clique em **"OK"** ou **"Adicionar"**

### **2.6 - (OPCIONAL) Adicionar Registro TXT para Google Search Console**

Se você também quer verificar o domínio no Google Search Console:

1. **Clique novamente** em **"Adicionar Registro"**
2. Preencha:

   **Tipo:** Selecione **"TXT"** (ou **"Tipo TXT"**)
   
   **Nome/Host:** Digite **"@"** ou deixe em branco
   
   **Valor/Destino:** Digite: **google-site-verification=vy8t3EcEx9vc6NSvlKvFB6D2j5MkvkrXT9xXJI**
   
   **TTL:** Digite **3600** ou deixe o valor padrão
   
3. **Salve**

### **2.7 - Verificar se Tudo Foi Salvo**

1. Verifique se os registros aparecem na lista
2. Confirme que os valores estão corretos
3. Se algo estiver errado, clique em **"Editar"** ou **"Modificar"** no registro

---

## ⏰ PASSO 3: Aguardar Propagação (15 minutos - 2 horas)

Após adicionar os registros DNS:

1. **Aguarde de 15 minutos a 2 horas**
   - O tempo pode variar
   - Geralmente leva menos de 1 hora

2. **Verificar propagação:**
   - Acesse: **https://dnschecker.org**
   - Digite: **monpec.com.br**
   - Selecione: **Tipo A**
   - Clique em **"Search"**
   - Verifique se aparece o IP correto em vários servidores DNS

---

## ✅ PASSO 4: Testar o Site (2 minutos)

1. Aguarde pelo menos **15 minutos** após adicionar os registros
2. Abra seu navegador
3. Acesse: **https://monpec.com.br**
4. Verifique se o site carrega

**Se funcionar:**
- ✅ Pronto! Seu domínio está configurado!
- O SSL (cadeado verde) pode demorar até 24 horas para aparecer

**Se não funcionar:**
- Aguarde mais um pouco (pode levar até 2 horas)
- Verifique se os registros DNS foram salvos corretamente no Registro.br
- Confira se os valores estão exatamente como o Google Cloud forneceu

---

## 🆘 Se Você Estiver Com Dificuldades

### **Problema 1: Não Encontro a Seção "Zona DNS" no Registro.br**

**Solução:**
- Ligue para o suporte do Registro.br: **0800 777 0001**
- Peça para ativar o "DNS Hosting" ou "Zona DNS" para seu domínio monpec.com.br
- Eles vão te ajudar a encontrar onde adicionar os registros

### **Problema 2: Não Sei Qual é o Projeto Correto no Google Cloud**

**Solução:**
- Se você tiver vários projetos, procure pelo projeto que tem o serviço "monpec"
- Ou pergunte para quem configurou o Cloud Run qual é o projeto
- Se não souber, liste os projetos e verifique cada um

### **Problema 3: Não Vejo a Aba "DOMÍNIOS CUSTOMIZADOS" no Cloud Run**

**Solução:**
- Verifique se você está na página correta do serviço "monpec"
- Role a página para baixo - a aba pode estar mais abaixo
- Tente atualizar a página (F5)
- Verifique se você tem permissões de administrador no projeto

### **Problema 4: Não Entendo os Valores que o Google Cloud Mostrou**

**Solução:**
- Tire uma foto da tela com seu celular
- Ou copie todos os valores para um documento
- Os valores que você precisa são:
  - O **IP** do registro tipo **A**
  - O **nome** do registro tipo **CNAME** (geralmente "ghs.googlehosted.com")

---

## 📋 Checklist Rápido

Marque cada item conforme você faz:

- [ ] Acessei o Google Cloud Console
- [ ] Encontrei o serviço "monpec"
- [ ] Cliquei na aba "DOMÍNIOS CUSTOMIZADOS"
- [ ] Criei o mapeamento de domínio monpec.com.br
- [ ] Anotei os registros DNS fornecidos pelo Google Cloud
- [ ] Acessei o painel do Registro.br
- [ ] Encontrei a seção "Zona DNS" ou "Registros DNS"
- [ ] Adicionei o registro tipo A com o IP do Google Cloud
- [ ] Adicionei o registro tipo CNAME para www
- [ ] (Opcional) Adicionei o registro tipo TXT para Google Search Console
- [ ] Verifiquei que todos os registros foram salvos
- [ ] Aguardei 15 minutos - 2 horas
- [ ] Testei o acesso em https://monpec.com.br

---

## 📞 Contatos de Suporte

**Google Cloud:**
- Documentação: https://cloud.google.com/run/docs/mapping-custom-domains
- Suporte: Através do console do Google Cloud

**Registro.br:**
- Telefone: **0800 777 0001**
- Email: suporte@registro.br
- Chat: Disponível no site do Registro.br

---

## ✅ Pronto!

Depois de completar todos os passos e aguardar a propagação DNS, seu site estará acessível em:
- **https://monpec.com.br**
- **https://www.monpec.com.br**

O certificado SSL (cadeado verde) será configurado automaticamente pelo Google Cloud em até 24 horas.

**Boa sorte! 😊**


