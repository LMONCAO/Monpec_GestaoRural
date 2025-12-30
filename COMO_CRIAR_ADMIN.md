# Como Criar Usuário Admin no Sistema MONPEC

Este guia explica como criar um usuário administrador para acessar o sistema.

## Opção 1: Usando o Script Batch (Mais Fácil - Windows)

### Método Simples (Recomendado)
Execute o arquivo `CRIAR_ADMIN_SIMPLES.bat`:
```
CRIAR_ADMIN_SIMPLES.bat
```

Este script oferece 3 opções:
1. **Criar admin com senha padrão** (`L6171r12@@`)
2. **Criar admin com senha personalizada**
3. **Criar admin com username e email personalizados**

### Método Interativo
Execute o arquivo `CRIAR_ADMIN.bat`:
```
CRIAR_ADMIN.bat
```

Este script solicita interativamente:
- Username (padrão: `admin`)
- Email (padrão: `admin@monpec.com.br`)
- Senha (mínimo 12 caracteres)

## Opção 2: Usando o Comando Django Diretamente

### Com senha padrão
```bash
python manage.py garantir_admin
```

### Com senha personalizada
```bash
python manage.py garantir_admin --senha "sua-senha-aqui"
```

### Com username e email personalizados
```bash
python manage.py garantir_admin --username "seu-usuario" --email "seu-email@exemplo.com" --senha "sua-senha-aqui"
```

### Forçar atualização de senha
Se o usuário já existir e você quiser atualizar a senha:
```bash
python manage.py garantir_admin --forcar --senha "nova-senha"
```

## Opção 3: Usando Script Python Direto

Execute o script Python interativo:
```bash
python criar_usuario_admin.py
```

Este script solicita interativamente todos os dados necessários.

## Opção 4: Usando Variável de Ambiente

Configure a variável de ambiente `ADMIN_PASSWORD` e execute:
```bash
set ADMIN_PASSWORD=sua-senha-segura
python manage.py garantir_admin
```

## Requisitos de Senha

⚠️ **IMPORTANTE**: A senha deve ter no mínimo **12 caracteres** conforme a configuração de segurança do sistema.

## Após Criar o Usuário

1. Acesse a página de login: `http://localhost:8000/login/` (local) ou `https://monpec.com.br/login/` (produção)
2. Use as credenciais criadas:
   - **Username**: `admin` (ou o que você definiu)
   - **Senha**: A senha que você configurou

## Verificar se o Usuário Foi Criado

Você pode verificar se o usuário foi criado corretamente executando:
```bash
python manage.py shell
```

E então no shell Python:
```python
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Is Staff: {user.is_staff}")
print(f"Is Superuser: {user.is_superuser}")
print(f"Is Active: {user.is_active}")
```

## Solução de Problemas

### Erro: "A senha deve ter no mínimo 12 caracteres"
- Certifique-se de que a senha tem pelo menos 12 caracteres

### Erro: "Usuário já existe"
- Use a opção `--forcar` para atualizar a senha:
  ```bash
  python manage.py garantir_admin --forcar --senha "nova-senha"
  ```

### Erro: "ModuleNotFoundError"
- Certifique-se de que o ambiente virtual está ativado
- Verifique se todas as dependências estão instaladas: `pip install -r requirements.txt`

## Notas de Segurança

- ⚠️ **NUNCA** compartilhe a senha do admin
- ⚠️ **SEMPRE** use senhas fortes (mínimo 12 caracteres, com letras, números e símbolos)
- ⚠️ Em produção, use variáveis de ambiente para senhas ao invés de hardcode
- ⚠️ Altere a senha padrão imediatamente após o primeiro acesso

