# ✅ Gmail API Ativada! Próximos Passos

Parabéns! A Gmail API está ativada. Agora siga estes passos:

## 🔐 Passo 1: Configurar OAuth Consent Screen (se ainda não fez)

1. No menu lateral (hamburger menu), vá em:
   - "APIs e serviços" > "Tela de consentimento OAuth"

2. Se for a primeira vez:
   - Escolha: "Externo" (External) > Clique "CRIAR"
   - Preencha:
     - **Nome do app:** `MONPEC`
     - **Email de suporte ao usuário:** `l.moncaosilva@gmail.com`
     - **Email do desenvolvedor:** `l.moncaosilva@gmail.com`
   - Clique "SALVAR E CONTINUAR"

3. Na seção **"Escopos"**:
   - Clique em "ADICIONAR OU REMOVER ESCOPOS"
   - Procure por: `gmail.send` ou digite: `https://www.googleapis.com/auth/gmail.send`
   - Marque a checkbox
   - Clique "ATUALIZAR" > "SALVAR E CONTINUAR"

4. Na seção **"Usuários de teste"**:
   - Clique "ADICIONAR USUÁRIOS"
   - Digite: `l.moncaosilva@gmail.com`
   - Clique "ADICIONAR"
   - Continue clicando "SALVAR E CONTINUAR" até finalizar

## 🔑 Passo 2: Criar Credenciais OAuth2

1. No menu lateral: "APIs e serviços" > "Credenciais"

2. Clique no botão azul "CRIAR CREDENCIAIS" (topo da página)

3. Escolha: "ID do cliente OAuth"

4. **⚠️ IMPORTANTE - Preencha corretamente:**
   - **Tipo de aplicativo:** Escolha **"Aplicativo para computador"** (Desktop app)
     - ❌ NÃO escolha "Aplicativo da Web"
   - **Nome:** `MONPEC Gmail`

5. Clique "CRIAR"

6. Uma janela popup vai aparecer com suas credenciais

7. **Clique no ícone de download** (seta para baixo ⬇️) para baixar o JSON

8. Salve o arquivo como: `gmail_credentials.json`

9. **Mova o arquivo para a raiz do projeto** (mesma pasta onde está o `manage.py`)

## 🚀 Passo 3: Executar Autenticação

Depois que colocar o arquivo `gmail_credentials.json` na raiz do projeto, execute:

```bash
python autenticar_gmail.py
```

Isso vai:
- Abrir seu navegador
- Pedir para fazer login com `l.moncaosilva@gmail.com`
- Pedir permissão para enviar emails em seu nome
- Salvar o token automaticamente em `gmail_token.json`

## ✅ Passo 4: Testar

1. Reinicie o servidor Django
2. Crie um convite de cotação no sistema
3. O email será enviado automaticamente!

---

## 📍 Status Atual:

✅ Gmail API ativada
⏭️ Próximo: Configurar OAuth Consent Screen










































