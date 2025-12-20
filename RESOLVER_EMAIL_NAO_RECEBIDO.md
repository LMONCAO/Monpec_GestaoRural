# 🚨 E-mail Não Recebido - Solução Rápida

## ❌ Problema Identificado

Se você não recebeu o e-mail e nem está no spam, o sistema provavelmente está usando o **backend de CONSOLE**, que apenas **imprime os e-mails no terminal** ao invés de enviá-los de verdade.

## ✅ Solução Rápida (5 minutos)

### Passo 1: Verificar o Terminal

Olhe o terminal onde o servidor Django está rodando. Você deve ver algo como:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Recuperação de Senha - MONPEC
From: noreply@monpec.com.br
To: seu-email@gmail.com
Date: ...
```

Se você vê isso, confirma que está usando o backend de console!

### Passo 2: Criar arquivo `.env`

Crie um arquivo chamado `.env` na **raiz do projeto** (mesmo nível do `manage.py`) com este conteúdo:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app-aqui
DEFAULT_FROM_EMAIL=seu-email@gmail.com
SITE_URL=http://localhost:8000
```

### Passo 3: Gerar Senha de App (Gmail)

**⚠️ IMPORTANTE:** Para Gmail, você NÃO pode usar sua senha normal!

1. Acesse: https://myaccount.google.com/apppasswords
2. Se não aparecer, ative a **Verificação em duas etapas** primeiro
3. Selecione "E-mail" e "Outro (nome personalizado)"
4. Digite "MONPEC" e clique em "Gerar"
5. Copie a senha gerada (16 caracteres, pode ter espaços)
6. Cole no arquivo `.env` no lugar de `sua-senha-de-app-aqui` (pode remover os espaços)

### Passo 4: Reiniciar o Servidor

**Pare o servidor** (Ctrl+C) e **inicie novamente**:

```powershell
python manage.py runserver
```

### Passo 5: Testar

Execute o script de teste:

```powershell
python testar_email.py
```

Ou teste pela interface:
1. Acesse: http://localhost:8000/recuperar-senha/
2. Digite um e-mail cadastrado
3. Verifique sua caixa de entrada!

---

## 🔍 Verificar Configuração Atual

Execute o diagnóstico:

```powershell
python diagnosticar_email.py
```

Este script vai mostrar:
- Se o arquivo `.env` existe
- Qual backend está sendo usado
- Se as credenciais estão configuradas
- O que está faltando

---

## 📋 Checklist Rápido

- [ ] Arquivo `.env` criado na raiz do projeto
- [ ] `EMAIL_BACKEND` configurado como `smtp.EmailBackend` (não `console`)
- [ ] `EMAIL_HOST_USER` com seu e-mail
- [ ] `EMAIL_HOST_PASSWORD` com Senha de App (Gmail)
- [ ] Servidor Django **reiniciado** após criar/editar `.env`
- [ ] Teste executado e e-mail recebido

---

## 🐛 Se Ainda Não Funcionar

### 1. Verificar se o `.env` está sendo lido

O Django lê variáveis de ambiente automaticamente. Se não estiver funcionando, verifique:

- O arquivo está na **raiz do projeto** (mesmo nível do `manage.py`)?
- O nome do arquivo é exatamente `.env` (com o ponto no início)?
- Você **reiniciou o servidor** após criar/editar o arquivo?

### 2. Verificar logs do terminal

Quando você solicita recuperação de senha, olhe o terminal. Se aparecer o conteúdo do e-mail impresso, ainda está usando console.

### 3. Testar conexão SMTP

Execute:

```powershell
python testar_email.py
```

Escolha a opção 2 (teste de conexão SMTP) para ver se consegue conectar no servidor.

### 4. Verificar firewall/antivírus

Alguns antivírus bloqueiam conexões SMTP. Tente:
- Desabilitar temporariamente o antivírus
- Adicionar exceção para Python
- Verificar se a porta 587 está liberada

### 5. Tentar outro provedor

Se Gmail não funcionar, tente Outlook:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@outlook.com
EMAIL_HOST_PASSWORD=sua-senha-normal
DEFAULT_FROM_EMAIL=seu-email@outlook.com
```

---

## 💡 Dica Importante

**Sempre reinicie o servidor Django após alterar o arquivo `.env`!**

O Django carrega as configurações na inicialização. Se você editar o `.env` sem reiniciar, as mudanças não terão efeito.

---

## 📞 Próximos Passos

1. Execute: `python diagnosticar_email.py` para ver o diagnóstico completo
2. Siga os passos acima
3. Teste novamente
4. Se ainda não funcionar, me mostre a saída do diagnóstico!


