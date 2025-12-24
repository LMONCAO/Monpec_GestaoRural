# 🎯 Próximos Passos - Você já está no Google Cloud Console!

Vejo que você já tem o projeto "monpec-sistema-rural" criado. Agora siga estes passos:

## 1️⃣ Ativar Gmail API

**Opção A (rápida):**
- Clique no card "APIs e serviços" na seção "Acesso rápido" que aparece na tela

**Opção B:**
- No menu lateral (hamburger menu), vá em: "APIs e serviços" > "Biblioteca"
- Procure por: `Gmail API`
- Clique em "Gmail API"
- Clique no botão azul "ATIVAR" (ou "ENABLE")

## 2️⃣ Configurar OAuth Consent Screen

- No menu lateral: "APIs e serviços" > "Tela de consentimento OAuth"
- Se for a primeira vez:
  - Tipo de usuário: escolha "Externo" > "CRIAR"
  - Preencha:
    - Nome do app: `MONPEC`
    - Email de suporte ao usuário: `l.moncaosilva@gmail.com`
    - Email do desenvolvedor: `l.moncaosilva@gmail.com`
  - Clique em "SALVAR E CONTINUAR"
  
  - Na seção "Escopos":
    - Clique em "ADICIONAR OU REMOVER ESCOPOS"
    - Procure: `gmail.send` ou `https://www.googleapis.com/auth/gmail.send`
    - Marque a checkbox
    - Clique em "ATUALIZAR" > "SALVAR E CONTINUAR"
  
  - Na seção "Usuários de teste":
    - Clique em "ADICIONAR USUÁRIOS"
    - Digite: `l.moncaosilva@gmail.com`
    - Clique em "ADICIONAR"
    - Continue clicando "SALVAR E CONTINUAR" até finalizar

## 3️⃣ Criar Credenciais OAuth2

- No menu lateral: "APIs e serviços" > "Credenciais"
- Clique em "CRIAR CREDENCIAIS" (botão azul no topo)
- Escolha: "ID do cliente OAuth"
- Preencha:
  - Tipo de aplicativo: **"Aplicativo da área de trabalho"** (Desktop app)
  - Nome: `MONPEC Gmail`
- Clique em "CRIAR"

## 4️⃣ Baixar Credenciais

Após criar as credenciais:
- Você verá uma janela popup com suas credenciais
- Clique no ícone de **download** (seta para baixo ⬇️)
- Salve o arquivo JSON
- **Renomeie para:** `gmail_credentials.json`
- **Mova para a raiz do projeto** (mesma pasta onde está o `manage.py`)

## 5️⃣ Executar Script de Autenticação

Depois que colocar o arquivo `gmail_credentials.json` na raiz do projeto, execute:

```bash
python autenticar_gmail.py
```

Isso vai:
- Abrir seu navegador
- Pedir para fazer login com `l.moncaosilva@gmail.com`
- Pedir permissão para enviar emails
- Salvar o token automaticamente

## 6️⃣ Pronto!

Depois disso, reinicie o servidor Django e teste criando um convite de cotação!

---

## 📍 Onde você está agora:

✅ Projeto criado: "monpec-sistema-rural"
⏭️ Próximo: Ativar Gmail API
















