# 🌐 Obter Registros DNS para o Registro.br - Passo a Passo Detalhado

## 🎯 Objetivo

Obter os registros DNS exatos que você precisa adicionar no Registro.br para que `monpec.com.br` aponte para o Cloud Run.

---

## 📋 PASSO 1: Mapear Domínio no Cloud Run

### 1.1 Acessar o Console do Google Cloud

1. Abra seu navegador
2. Acesse: **https://console.cloud.google.com/run**
3. Faça login se necessário
4. Certifique-se de que o projeto **monpec-sistema-rural** está selecionado (no topo da tela)

### 1.2 Encontrar o Serviço monpec

1. Na lista de serviços Cloud Run, procure por **"monpec"**
2. **Clique no serviço "monpec"**
3. Você verá a página de detalhes do serviço

### 1.3 Acessar a Aba de Domínios Customizados

1. No topo da página do serviço, você verá várias **abas** (tabs)
2. Procure pela aba: **"DOMÍNIOS CUSTOMIZADOS"** ou **"Custom Domains"**
   - Pode estar escrito em português ou inglês
   - Geralmente é a última aba à direita
3. **Clique nessa aba**

### 1.4 Adicionar Mapeamento de Domínio

1. Na aba de domínios, você verá um botão:
   - **"ADICIONAR Mapeamento de Domínio"** (português)
   - **"Add Mapping"** ou **"Map Domain"** (inglês)
2. **Clique nesse botão**

### 1.5 Digitar o Domínio

1. Aparecerá um campo para digitar o domínio
2. Digite exatamente: **monpec.com.br**
3. Clique em **"CONTINUAR"** ou **"Continue"**

### 1.6 ⚠️ IMPORTANTE: Anotar os Registros DNS

Após clicar em "CONTINUAR", o Google Cloud vai mostrar uma tela com os **REGISTROS DNS** que você precisa adicionar no Registro.br.

**📝 ANOTE TODOS OS REGISTROS QUE APARECEREM!**

**Exemplo do que você verá:**

```
Registro A:
Nome: @
Valor: 151.101.1.195
Tipo: A
TTL: 3600

Registro CNAME:
Nome: www
Valor: ghs.googlehosted.com
Tipo: CNAME
TTL: 3600
```

**⚠️ IMPORTANTE:** 
- Os valores reais serão DIFERENTES!
- Use os valores EXATOS que aparecerem na tela
- Tire uma foto da tela ou copie os valores para um documento

---

## 📋 PASSO 2: Se Não Encontrar a Aba "DOMÍNIOS CUSTOMIZADOS"

Se você não encontrar a aba "DOMÍNIOS CUSTOMIZADOS" no Cloud Run:

### Opção A: Usar o Menu de Navegação

1. No menu lateral esquerdo do Google Cloud Console
2. Procure por: **"Cloud Run"** → **"Domínios"** ou **"Domain Mappings"**
3. Clique nessa opção
4. Você verá uma lista de mapeamentos de domínio
5. Clique em **"ADICIONAR Mapeamento"** ou **"Add Mapping"**

### Opção B: Usar a URL Direta

Acesse diretamente:
```
https://console.cloud.google.com/run/domains?project=monpec-sistema-rural
```

### Opção C: Usar Linha de Comando (Cloud Shell)

Se não conseguir pela interface web, use o Cloud Shell:

```bash
# Mapear o domínio
gcloud beta run domain-mappings create \
    --service monpec \
    --domain monpec.com.br \
    --region us-central1

# Obter os registros DNS
gcloud beta run domain-mappings describe \
    --domain monpec.com.br \
    --region us-central1 \
    --format="yaml"
```

Isso vai mostrar os registros DNS no formato YAML.

---

## 📋 PASSO 3: Configurar DNS no Registro.br

Agora que você tem os registros DNS do Google Cloud:

### 3.1 Acessar o Painel do Registro.br

1. Abra seu navegador
2. Acesse: **https://registro.br/painel/**
3. Faça login na sua conta
4. Selecione o domínio **monpec.com.br**

### 3.2 Encontrar a Seção de DNS

No painel do Registro.br, procure por uma dessas opções:

- **"DNS"** → **"Zona DNS"**
- **"DNS"** → **"Registros DNS"**
- **"Gerenciar"** → **"DNS"**
- **"Gerenciar"** → **"Zona DNS"**

### 3.3 Se Você NÃO Encontrar "Zona DNS"

Se você só vê "ALTERAR SERVIDORES DNS" e não vê "Zona DNS":

1. Procure por um botão: **"UTILIZAR DNS DO REGISTRO.BR"** ou **"Ativar DNS Hosting"**
2. **Clique nesse botão**
3. Aguarde alguns minutos
4. **Atualize a página** (F5)
5. Agora você deve ver uma seção para **"Zona DNS"** ou **"Registros DNS"**

### 3.4 Adicionar o Registro A

1. Procure por um botão: **"Adicionar Registro"** ou **"+ Novo Registro"** ou **"Adicionar"**
2. **Clique nesse botão**
3. Uma janela ou formulário vai aparecer
4. Preencha com os valores que você anotou do Google Cloud:

   **Tipo:** Selecione **"A"** (ou **"Tipo A"**)
   
   **Nome/Host:** Digite **"@"** (arrobas) ou deixe em branco (depende da interface)
   
   **Valor/Destino:** Digite o **IP** que o Google Cloud forneceu (exemplo: 151.101.1.195)
   
   **TTL:** Digite **3600** ou deixe o valor padrão
   
5. **Salve** ou clique em **"OK"** ou **"Adicionar"**

### 3.5 Adicionar o Registro CNAME (para www)

1. **Clique novamente** em **"Adicionar Registro"** ou **"+ Novo Registro"**
2. Preencha com os valores do Google Cloud:

   **Tipo:** Selecione **"CNAME"** (ou **"Tipo CNAME"**)
   
   **Nome/Host:** Digite **"www"** (só www, sem ponto)
   
   **Valor/Destino:** Digite o valor fornecido pelo Google Cloud (geralmente: ghs.googlehosted.com)
   
   **TTL:** Digite **3600** ou deixe o valor padrão
   
3. **Salve** ou clique em **"OK"** ou **"Adicionar"**

### 3.6 Verificar se Tudo Foi Salvo

1. Verifique se os registros aparecem na lista
2. Confirme que os valores estão corretos
3. Se algo estiver errado, clique em **"Editar"** ou **"Modificar"** no registro

---

## ⏰ PASSO 4: Aguardar Propagação DNS

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

## ✅ PASSO 5: Testar o Site

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

## 🆘 Problemas Comuns

### Problema 1: "Não encontro a aba DOMÍNIOS CUSTOMIZADOS"

**Solução:**
- Use a URL direta: https://console.cloud.google.com/run/domains?project=monpec-sistema-rural
- Ou use o menu lateral: Cloud Run → Domínios
- Ou use a linha de comando no Cloud Shell (veja Passo 2, Opção C)

### Problema 2: "Não encontro a seção Zona DNS no Registro.br"

**Solução:**
- Ligue para o suporte do Registro.br: **0800 777 0001**
- Peça para ativar o "DNS Hosting" ou "Zona DNS" para seu domínio monpec.com.br
- Eles vão te ajudar a encontrar onde adicionar os registros

### Problema 3: "O Google Cloud não mostra os registros DNS"

**Solução:**
- Certifique-se de que o domínio foi mapeado com sucesso
- Verifique se há algum erro na tela
- Tente usar a linha de comando (veja Passo 2, Opção C)

### Problema 4: "Não sei qual é o projeto correto"

**Solução:**
- O projeto deve ser: **monpec-sistema-rural**
- Verifique no topo da tela do Google Cloud Console
- Se estiver diferente, clique e selecione o projeto correto

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

1. **Acesse:** https://console.cloud.google.com/run
2. **Clique no serviço:** monpec
3. **Vá na aba:** "DOMÍNIOS CUSTOMIZADOS"
4. **Adicione domínio:** monpec.com.br
5. **ANOTE os registros DNS** fornecidos
6. **No Registro.br:** Adicione os registros A e CNAME
7. **Aguarde propagação:** 15 min - 2 horas
8. **Teste:** https://monpec.com.br

---

**🚀 Siga os passos acima e você conseguirá obter os registros DNS corretos!**










