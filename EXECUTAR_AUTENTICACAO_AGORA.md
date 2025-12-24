# 🔐 Executar Autenticação OAuth2 - Agora com Celular Ligado

## ✅ Arquivo de Credenciais

O arquivo `gmail_credentials.json` já está na raiz do projeto!

## 🚀 Próximo Passo: Executar Autenticação

Quando seu celular estiver ligado e pronto para receber notificações do Google:

### Execute no terminal/PowerShell:

```bash
python autenticar_gmail.py
```

## 📱 O que vai acontecer:

1. O script vai abrir seu navegador automaticamente
2. Você verá uma página do Google pedindo para fazer login
3. Faça login com: `l.moncaosilva@gmail.com`
4. O Google vai pedir verificação no celular (código ou notificação)
5. **Tenha o celular por perto** para autorizar
6. Depois de autorizar, o token será salvo automaticamente

## ✅ Após Autenticar:

1. O arquivo `gmail_token.json` será criado automaticamente
2. Você pode reiniciar o servidor Django
3. Teste criando um convite de cotação - o email será enviado!

---

## ⚠️ Importante:

- Certifique-se que seu celular está ligado e conectado
- Você precisa estar logado no Google no navegador ou ter acesso ao celular para autenticação de dois fatores
- A autenticação só precisa ser feita uma vez (o token fica salvo)

---

## 🔄 Se der erro:

Se der algum erro, execute novamente:
```bash
python autenticar_gmail.py
```

O script vai tentar usar o token existente ou pedir nova autenticação se necessário.
















