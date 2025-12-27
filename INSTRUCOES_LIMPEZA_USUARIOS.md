# Instruções para Limpar Usuários

## Opção 1: Executar via Cloud Shell (Recomendado)

1. Acesse o Google Cloud Shell
2. Execute os seguintes comandos:

```bash
# Conectar ao Cloud SQL
gcloud sql connect monpec-db --user=postgres

# No prompt do PostgreSQL, execute:
# (Não é necessário, vamos usar o comando Django)

# Ou execute via Cloud Run (se configurado):
gcloud run jobs execute limpar-usuarios-job --region us-central1
```

## Opção 2: Executar Localmente (se tiver acesso ao banco)

```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Executar comando
python manage.py limpar_usuarios --confirmar --senha-admin "L6171r12@@"
```

## Opção 3: Executar via Django Admin ou Shell

1. Acesse o Django Admin
2. Vá em "Usuários" e exclua manualmente todos exceto "admin"
3. Altere a senha do admin para: `L6171r12@@`

## Validação de Senhas

### Para Assinantes:
- Mínimo 8 caracteres
- Pelo menos 1 letra maiúscula
- Pelo menos 1 letra minúscula
- A senha será o email do usuário (conforme solicitado)

### Para Demonstração:
- Sem validação de complexidade
- Senha padrão: "monpec"

## Nota Importante

O comando `limpar_usuarios` irá:
- Manter apenas o usuário "admin"
- Definir a senha do admin como "L6171r12@@"
- Excluir TODOS os outros usuários

**ATENÇÃO**: Esta operação é irreversível! Faça backup antes se necessário.


