# 🔐 Criar Usuário Administrador - MONPEC

## Credenciais de Acesso

- **Username:** `admin`
- **Senha:** `L6171r12@@`
- **Email:** `admin@monpec.com.br`

## 📋 Como Criar o Usuário Admin

### Opção 1: Executar Localmente (Desenvolvimento)

1. Abra o terminal/PowerShell no diretório do projeto
2. Execute:

```bash
python criar_admin.py
```

Ou no Windows:
```cmd
criar_admin.bat
```

### Opção 2: Executar no Cloud Run (Produção)

#### Linux/Mac:
```bash
./criar_admin_cloud_run.sh SEU_PROJECT_ID us-central1
```

#### Windows PowerShell:
```powershell
.\criar_admin_cloud_run.ps1 SEU_PROJECT_ID us-central1
```

### Opção 3: Via Django Shell (Manual)

```bash
python manage.py shell
```

No shell do Django:
```python
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.create_user(
    username='admin',
    email='admin@monpec.com.br',
    password='L6171r12@@',
    is_staff=True,
    is_superuser=True,
    is_active=True
)
print("✅ Usuário admin criado!")
```

### Opção 4: Via Django Management Command

```bash
python manage.py createsuperuser
```

Quando solicitado:
- Username: `admin`
- Email: `admin@monpec.com.br`
- Password: `L6171r12@@`

## ✅ Verificar se o Usuário Foi Criado

Após criar o usuário, você pode verificar:

```bash
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

admin = User.objects.get(username='admin')
print(f"Username: {admin.username}")
print(f"Email: {admin.email}")
print(f"Is Staff: {admin.is_staff}")
print(f"Is Superuser: {admin.is_superuser}")
print(f"Is Active: {admin.is_active}")
```

## 🔒 Segurança

⚠️ **IMPORTANTE:** 
- Altere a senha padrão após o primeiro acesso
- Use uma senha forte em produção
- Não compartilhe as credenciais
- Considere usar autenticação de dois fatores

## 📝 Notas

- O script `criar_admin.py` cria ou atualiza o usuário admin automaticamente
- Se o usuário já existir, a senha será atualizada
- O usuário terá todas as permissões de administrador (is_staff=True, is_superuser=True)




















