# Como Criar um Superusuário no Sistema MONPEC

## Opção 1: Usando o script interativo (Recomendado)

Execute no terminal:

```bash
python311\python.exe criar_superusuario.py
```

O script irá solicitar:
- Nome de usuário (use um nome único, não "admin")
- Email (opcional)
- Senha (deve atender aos requisitos de segurança)

## Opção 2: Via linha de comando (Não-interativo)

Execute:

```bash
python311\python.exe criar_superusuario_simples.py "seu_usuario" "seu@email.com" "SuaSenhaForte123!@#"
```

**Exemplo:**
```bash
python311\python.exe criar_superusuario_simples.py "joao" "joao@monpec.com.br" "MinhaSenh@Segura123"
```

## Opção 3: Usando o comando Django padrão

Execute no terminal PowerShell ou CMD:

```bash
python311\python.exe manage.py createsuperuser
```

Você será solicitado a informar:
- Username
- Email (opcional)
- Password (será solicitado duas vezes)

## Requisitos da Senha

A senha DEVE ter:
- ✅ Mínimo de **12 caracteres**
- ✅ Pelo menos **1 letra maiúscula** (A-Z)
- ✅ Pelo menos **1 letra minúscula** (a-z)
- ✅ Pelo menos **1 número** (0-9)
- ✅ Pelo menos **1 caractere especial** (!@#$%^&*()_+-=[]{}|;:,.<>?)

**Senhas bloqueadas:**
- ❌ 123456, password, admin, senha, qwerty, etc.

## Exemplos de Senhas Válidas

✅ `MinhaSenh@123!`  
✅ `SistemaMONPEC2025#`  
✅ `GestaoRural@Segura!`  
✅ `Admin@Monpec2025!`

## Exemplos de Senhas Inválidas

❌ `admin123` (muito curta e comum)  
❌ `123456789012` (só números)  
❌ `MinhaSenha` (sem números e símbolos)  
❌ `MINHASENHA123` (sem minúsculas e símbolos)

## Importante

1. **NÃO use "admin" como nome de usuário** - é um nome padrão perigoso
2. **Use um nome único** como seu nome ou algo específico
3. **Guarde a senha em local seguro** - não compartilhe
4. **Anote as credenciais** em um gerenciador de senhas

## Verificar Usuários Existentes

Para ver quais usuários existem:

```bash
python311\python.exe manage.py shell
```

Depois execute:
```python
from django.contrib.auth.models import User
for u in User.objects.all():
    print(f"{u.username} - {u.email} - Superuser: {u.is_superuser} - Ativo: {u.is_active}")
```

## Alterar Senha de Usuário Existente

```bash
python311\python.exe manage.py changepassword nome_do_usuario
```

---

**Dúvidas?** Consulte `SEGURANCA_SISTEMA.md` para mais informações sobre segurança.







