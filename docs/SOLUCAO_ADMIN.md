# 🔐 Solução para Acesso Admin

## Problema
Não consegue fazer login com:
- **Usuário**: admin
- **Senha**: L6171r12@@

## Soluções

### Solução 1: Criar Admin via Django Shell (Recomendado)

Execute no Cloud Shell ou localmente conectado ao banco de dados:

```python
python manage.py shell
```

Depois execute:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

username = 'admin'
password = 'L6171r12@@'
email = 'admin@monpec.com.br'

# Criar ou obter usuário
try:
    user = User.objects.get(username=username)
    print(f"Usuário encontrado: {user.username}")
except User.DoesNotExist:
    user = User.objects.create_user(username=username, email=email, password=password)
    print(f"Usuário criado: {user.username}")

# Configurar permissões
user.set_password(password)
user.is_staff = True
user.is_superuser = True
user.is_active = True
user.email = email
user.save()

print(f"✅ Admin configurado!")
print(f"Username: {username}")
print(f"Password: {password}")
```

### Solução 2: Via Cloud Run Exec

Execute diretamente no container:

```bash
gcloud run services exec monpec --region us-central1 --command "python manage.py shell"
```

Depois execute o código Python acima.

### Solução 3: Criar via Script Local

Se você tem acesso ao banco de dados localmente:

1. Configure as variáveis de ambiente para apontar para o banco do Cloud Run
2. Execute: `python corrigir_senha_admin.py`

### Solução 4: Verificar se o Usuário Existe

Verifique se o usuário existe no banco:

```python
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Listar todos os usuários
for user in User.objects.all():
    print(f"Username: {user.username}, Email: {user.email}, Ativo: {user.is_active}, Staff: {user.is_staff}, Superuser: {user.is_superuser}")

# Verificar usuário admin especificamente
try:
    admin = User.objects.get(username='admin')
    print(f"\nAdmin encontrado:")
    print(f"  - Username: {admin.username}")
    print(f"  - Email: {admin.email}")
    print(f"  - Ativo: {admin.is_active}")
    print(f"  - Staff: {admin.is_staff}")
    print(f"  - Superuser: {admin.is_superuser}")
    print(f"  - Senha definida: {admin.has_usable_password()}")
except User.DoesNotExist:
    print("\n❌ Usuário admin NÃO existe!")
```

## Verificar Problemas Comuns

### 1. Usuário não existe
- Execute a Solução 1 para criar

### 2. Senha incorreta
- Execute a Solução 1 para redefinir a senha

### 3. Usuário desativado
- Execute: `user.is_active = True; user.save()`

### 4. Problemas de autenticação
- Verifique se o banco de dados está acessível
- Verifique se as configurações do Django estão corretas

## Acesso Rápido

**URL do Sistema**: https://monpec-fzzfjppzva-uc.a.run.app

**Credenciais Esperadas**:
- Usuário: `admin`
- Senha: `L6171r12@@`
- Email: `admin@monpec.com.br`










































