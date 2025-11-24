# 💻 Configurar Ambiente Local para Desenvolvimento

## 📋 Pré-requisitos

- ✅ Python 3.8 ou superior
- ✅ Git instalado
- ✅ Editor de código (VS Code, PyCharm, etc.)

---

## 🚀 Passo a Passo

### 1. Verificar Python

```powershell
python --version
# ou
python3 --version
```

Deve mostrar Python 3.8 ou superior.

---

### 2. Criar Ambiente Virtual (Recomendado)

```powershell
# Navegar para a pasta do projeto
cd "C:\Users\lmonc\Desktop\MonPO-Monitor de Plano Orçamentario\Monpec_GestaoRural"

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1
```

**Nota:** Se der erro de política de execução, execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

### 3. Instalar Dependências

```powershell
# Com o ambiente virtual ativado
pip install --upgrade pip
pip install -r requirements.txt
```

Se não houver `requirements.txt`, instale manualmente:
```powershell
pip install django==4.2.7
pip install django-extensions
pip install python-decouple
# ... outras dependências conforme necessário
```

---

### 4. Configurar Banco de Dados

O sistema usa SQLite por padrão (desenvolvimento). O arquivo `db.sqlite3` será criado automaticamente.

---

### 5. Executar Migrações

```powershell
python manage.py migrate
```

---

### 6. Criar Superusuário (Opcional)

```powershell
python manage.py createsuperuser
```

Digite:
- Username: `admin`
- Email: (opcional)
- Password: (escolha uma senha)

---

### 7. Coletar Arquivos Estáticos

```powershell
python manage.py collectstatic --noinput
```

---

### 8. Executar Servidor de Desenvolvimento

```powershell
python manage.py runserver
```

O servidor iniciará em: **http://127.0.0.1:8000/**

---

## 🔧 Configurações Importantes

### Settings Local vs Produção

O sistema tem dois arquivos de settings:
- `settings.py` - Desenvolvimento local
- `settings_gcp.py` - Produção (Google Cloud)

Para desenvolvimento local, use `settings.py` (padrão).

---

### Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto:

```env
DEBUG=True
SECRET_KEY=sua-chave-secreta-local
DATABASE_URL=sqlite:///db.sqlite3
```

---

## 📝 Comandos Úteis

### Criar Migrações
```powershell
python manage.py makemigrations
```

### Aplicar Migrações
```powershell
python manage.py migrate
```

### Criar Superusuário
```powershell
python manage.py createsuperuser
```

### Shell do Django
```powershell
python manage.py shell
```

### Verificar URLs
```powershell
python manage.py show_urls
```

---

## 🐛 Resolver Problemas Comuns

### Erro: "ModuleNotFoundError"

```powershell
# Instalar dependências faltantes
pip install nome-do-modulo
```

### Erro: "No such table"

```powershell
# Executar migrações
python manage.py migrate
```

### Erro: "Port already in use"

```powershell
# Usar outra porta
python manage.py runserver 8001
```

---

## ✅ Checklist

- [ ] Python instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas
- [ ] Migrações executadas
- [ ] Superusuário criado (opcional)
- [ ] Servidor rodando em http://127.0.0.1:8000/

---

## 🎯 Próximos Passos

1. ✅ Acesse: http://127.0.0.1:8000/
2. ✅ Faça login (se criou superusuário)
3. ✅ Comece a desenvolver!

---

**Agora você pode desenvolver localmente!** 💻












