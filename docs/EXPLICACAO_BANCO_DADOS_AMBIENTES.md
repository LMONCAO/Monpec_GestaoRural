# 📊 Explanação: Configuração de Banco de Dados por Ambiente

## ✅ **Não há conflito entre SQLite (local) e PostgreSQL (produção)**

O projeto está configurado corretamente para usar bancos diferentes em ambientes diferentes.

---

## 🏗️ Arquitetura

### **Desenvolvimento Local (Windows)**
- **Arquivo de Settings**: `sistema_rural/settings.py`
- **Banco de Dados**: SQLite (`db.sqlite3`)
- **Como ativa**: Automático quando você roda `python manage.py runserver` localmente

### **Produção (Google Cloud)**
- **Arquivo de Settings**: `sistema_rural/settings_gcp.py`
- **Banco de Dados**: PostgreSQL 15 (Cloud SQL)
- **Como ativa**: Via variável de ambiente `DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp`

---

## 🔄 Como Funciona a Separação

### 1. **Local (settings.py)**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 2. **Produção (settings_gcp.py)**
```python
# Primeiro importa tudo de settings.py
from .settings import *

# Depois SOBRESCREVE apenas a configuração de banco
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': f'/cloudsql/{CLOUD_SQL_CONNECTION_NAME}',
        'PORT': '',
    }
}
```

### 3. **No Deploy (configurado automaticamente)**
- **Dockerfile**: Define `ENV DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp`
- **Scripts de Deploy**: Passam `DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp` nas variáveis de ambiente
- **Resultado**: O Django automaticamente usa PostgreSQL no Google Cloud

---

## ✅ Por Que Não Há Conflito

1. **Django usa apenas UM arquivo de settings por execução**
   - Controlado pela variável `DJANGO_SETTINGS_MODULE`
   - Local não define essa variável → usa `settings.py` (SQLite)
   - Produção define explicitamente → usa `settings_gcp.py` (PostgreSQL)

2. **Separação clara de ambientes**
   - Você nunca roda os dois ao mesmo tempo
   - SQLite só existe no seu computador
   - PostgreSQL só existe no Google Cloud

3. **Migrações são compatíveis**
   - O Django abstrai as diferenças entre bancos
   - Migrações escritas corretamente funcionam em ambos

---

## ⚠️ Pontos de Atenção

### **1. Recursos específicos do SQLite**
Se você usar código SQLite-específico, pode não funcionar no PostgreSQL:

```python
# ❌ EVITAR (específico do SQLite)
cursor.execute("SELECT * FROM tabela WHERE nome LIKE ?", (valor,))

# ✅ CORRETO (compatível com ambos)
cursor.execute("SELECT * FROM tabela WHERE nome LIKE %s", (valor,))
```

### **2. Tipos de dados específicos**
- SQLite aceita quase tudo como string
- PostgreSQL é mais rígido com tipos
- **Solução**: Use sempre os tipos corretos nas migrações

### **3. Testes**
- Teste sempre localmente antes de fazer deploy
- Considere testar localmente com PostgreSQL também

---

## 🧪 Como Testar com PostgreSQL Localmente (Opcional)

Se quiser testar com PostgreSQL localmente antes de fazer deploy:

### **1. Instalar PostgreSQL no Windows**
- Baixar: https://www.postgresql.org/download/windows/
- Criar banco: `createdb monpec_test`

### **2. Criar settings_local_postgres.py**
```python
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'monpec_test',
        'USER': 'postgres',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### **3. Rodar com PostgreSQL local**
```bash
set DJANGO_SETTINGS_MODULE=sistema_rural.settings_local_postgres
python manage.py migrate
python manage.py runserver
```

---

## 📋 Checklist Antes do Deploy

- [ ] Migrações funcionam localmente com SQLite
- [ ] Não há código SQLite-específico no projeto
- [ ] Todas as migrations foram testadas
- [ ] Variável `DJANGO_SETTINGS_MODULE=sistema_rural.settings_gcp` está configurada no deploy
- [ ] Credenciais do PostgreSQL estão nas variáveis de ambiente

---

## 🚀 Resumo

✅ **SQLite local** → Desenvolvimento rápido, sem instalar PostgreSQL  
✅ **PostgreSQL produção** → Performance e recursos avançados  
✅ **Sem conflito** → Django gerencia isso automaticamente  
✅ **Deploy seguro** → Scripts configuram tudo automaticamente  

**O projeto está configurado corretamente!** 🎉

---

**Última atualização:** 26/12/2025






