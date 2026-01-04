# Guia para Corrigir Problemas do Sistema

Este guia ajuda a resolver os problemas mais comuns ao colocar o sistema no ar:
- Tabelas não criadas
- Usuário demo não funciona
- Templates não encontrados
- Problemas ao salvar arquivos

## 🚀 Solução Rápida (Recomendado)

Execute o script PowerShell que faz tudo automaticamente:

```powershell
.\CORRIGIR_SISTEMA_COMPLETO.ps1
```

Este script irá:
1. ✅ Aplicar todas as migrations pendentes
2. ✅ Executar diagnóstico completo
3. ✅ Coletar arquivos estáticos
4. ✅ Criar/atualizar usuário demo

## 📋 Solução Passo a Passo

### 1. Aplicar Migrations

As migrations criam todas as tabelas necessárias no banco de dados:

```bash
python manage.py migrate
```

Se houver erros, tente:

```bash
python manage.py migrate --run-syncdb
```

### 2. Garantir Sistema Configurado

Use o comando de gerenciamento que verifica e corrige tudo:

```bash
python manage.py garantir_sistema_configurado
```

Este comando verifica:
- ✅ Migrations aplicadas
- ✅ Tabelas críticas existem
- ✅ Usuário demo criado
- ✅ Templates existem
- ✅ Permissões de arquivos

### 3. Criar Usuário Demo Manualmente

Se o usuário demo não foi criado automaticamente:

```bash
python manage.py shell
```

No shell Python:

```python
from django.contrib.auth.models import User

# Criar usuário demo
demo_user, created = User.objects.get_or_create(
    username='demo_monpec',
    defaults={
        'email': 'demo@monpec.com.br',
        'is_staff': True,
        'is_superuser': False,
        'is_active': True,
    }
)

if created:
    demo_user.set_password('demo123')
    demo_user.save()
    print('✅ Usuário demo criado!')
else:
    print('✅ Usuário demo já existe!')
    # Atualizar senha se necessário
    demo_user.set_password('demo123')
    demo_user.save()
    print('✅ Senha atualizada!')
```

### 4. Verificar Templates

Verifique se os templates existem:

```bash
# Windows PowerShell
Test-Path "templates\gestao_rural\demo\demo_loading.html"
Test-Path "templates\gestao_rural\demo_setup.html"
Test-Path "templates\gestao_rural\login_clean.html"
```

Se algum template não existir, você precisa copiá-lo do repositório ou criá-lo.

### 5. Verificar Permissões de Arquivos

Certifique-se de que os diretórios existem e têm permissão de escrita:

```bash
# Windows PowerShell
New-Item -ItemType Directory -Force -Path "media"
New-Item -ItemType Directory -Force -Path "staticfiles"
```

## 🔍 Diagnóstico Detalhado

Para um diagnóstico completo, execute:

```bash
python diagnosticar_e_corrigir_sistema.py
```

Este script verifica:
- ✅ Tabelas do banco de dados
- ✅ Migrations aplicadas
- ✅ Usuário demo
- ✅ Templates
- ✅ Permissões de arquivos

## 🐛 Problemas Comuns e Soluções

### Problema: "Tabela não existe"

**Solução:**
```bash
python manage.py migrate
```

Se ainda não funcionar:
```bash
python manage.py migrate --run-syncdb
python manage.py migrate --fake-initial
```

### Problema: "Usuário demo não consegue fazer login"

**Solução:**
1. Verifique se o usuário existe:
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
user = User.objects.get(username='demo_monpec')
print(f"Usuário existe: {user.username}, Ativo: {user.is_active}")
```

2. Se não existir, crie:
```bash
python manage.py garantir_sistema_configurado
```

### Problema: "Template não encontrado"

**Solução:**
1. Verifique se o template existe no diretório `templates/`
2. Verifique se `TEMPLATES` em `settings.py` está configurado corretamente
3. Execute `collectstatic` se necessário:
```bash
python manage.py collectstatic --noinput
```

### Problema: "Erro ao salvar arquivos"

**Solução:**
1. Verifique se o diretório `media/` existe e tem permissão de escrita
2. Verifique `MEDIA_ROOT` em `settings.py`
3. No Windows, certifique-se de que o usuário tem permissão de escrita

## 📝 Checklist de Deploy

Antes de colocar o sistema no ar, verifique:

- [ ] Migrations aplicadas (`python manage.py migrate`)
- [ ] Usuário demo criado (`python manage.py garantir_sistema_configurado`)
- [ ] Templates existem
- [ ] Diretórios `media/` e `staticfiles/` existem e têm permissão de escrita
- [ ] Arquivos estáticos coletados (`python manage.py collectstatic`)
- [ ] Variáveis de ambiente configuradas (`.env`)
- [ ] Banco de dados configurado e acessível
- [ ] Servidor web configurado (se aplicável)

## 🆘 Ainda com Problemas?

Se ainda tiver problemas após seguir este guia:

1. Verifique os logs do Django:
```bash
python manage.py runserver
# Veja os erros no console
```

2. Verifique os logs do servidor web (se aplicável)

3. Execute o diagnóstico completo:
```bash
python diagnosticar_e_corrigir_sistema.py
```

4. Verifique se todas as dependências estão instaladas:
```bash
pip install -r requirements.txt
```

## 📞 Informações Úteis

- **Usuário demo padrão:** `demo_monpec` / `demo123`
- **Email demo:** `demo@monpec.com.br`
- **Comando de diagnóstico:** `python manage.py garantir_sistema_configurado`
- **Script PowerShell:** `.\CORRIGIR_SISTEMA_COMPLETO.ps1`


