# Configuração de Banco de Dados - MONPEC

Este guia explica como configurar o banco de dados, incluindo banco remoto.

## 🗄️ Banco de Dados Padrão (SQLite)

O sistema usa SQLite por padrão, que é um banco de dados embutido.

### Localização

- **Arquivo**: `db.sqlite3`
- **Localização**: Raiz do projeto

### Vantagens

- Não requer instalação adicional
- Fácil backup (apenas copiar o arquivo)
- Ideal para desenvolvimento e uso local

### Desvantagens

- Não suporta múltiplos usuários simultâneos
- Limitado para grandes volumes de dados

## 🔧 Configuração de Banco Remoto (PostgreSQL/MySQL)

Para produção ou uso com múltiplos usuários, recomenda-se PostgreSQL ou MySQL.

### PostgreSQL

#### 1. Instalar PostgreSQL

**Windows:**
- Baixe do site oficial: https://www.postgresql.org/download/windows/

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
```

**Mac:**
```bash
brew install postgresql
```

#### 2. Criar Banco de Dados

```sql
CREATE DATABASE monpec_db;
CREATE USER monpec_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;
```

#### 3. Configurar Django

Edite `sistema_rural/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'monpec_db',
        'USER': 'monpec_user',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### 4. Instalar Driver

```bash
pip install psycopg2-binary
```

### MySQL

#### 1. Instalar MySQL

**Windows:**
- Baixe do site oficial: https://dev.mysql.com/downloads/installer/

**Linux:**
```bash
sudo apt-get install mysql-server
```

**Mac:**
```bash
brew install mysql
```

#### 2. Criar Banco de Dados

```sql
CREATE DATABASE monpec_db;
CREATE USER 'monpec_user'@'localhost' IDENTIFIED BY 'sua_senha';
GRANT ALL PRIVILEGES ON monpec_db.* TO 'monpec_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 3. Configurar Django

Edite `sistema_rural/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'monpec_db',
        'USER': 'monpec_user',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

#### 4. Instalar Driver

```bash
pip install mysqlclient
```

## 🔄 Migrar de SQLite para Banco Remoto

### 1. Fazer Backup do SQLite

```batch
EXPORTAR_DADOS.bat
```

### 2. Configurar Novo Banco

Configure o banco remoto conforme instruções acima.

### 3. Aplicar Migrações

```batch
python manage.py migrate
```

### 4. Importar Dados (Opcional)

Se você exportou dados em JSON:

```batch
python manage.py loaddata dados_exportados.json
```

## 💾 Backup e Restauração

### Backup Automático

**Windows:**
```batch
EXPORTAR_DADOS.bat
```

**Linux/Mac:**
```bash
./EXPORTAR_DADOS.sh
```

### Backup Manual

#### SQLite

```batch
copy db.sqlite3 backup_db_%date%.sqlite3
```

#### PostgreSQL

```bash
pg_dump -U monpec_user monpec_db > backup.sql
```

#### MySQL

```bash
mysqldump -u monpec_user -p monpec_db > backup.sql
```

### Restauração

#### SQLite

```batch
copy backup_db.sqlite3 db.sqlite3
```

#### PostgreSQL

```bash
psql -U monpec_user monpec_db < backup.sql
```

#### MySQL

```bash
mysql -u monpec_user -p monpec_db < backup.sql
```

## 🔐 Segurança

### Boas Práticas

1. **Use senhas fortes** para o banco de dados
2. **Limite acesso** apenas ao necessário
3. **Faça backups regulares**
4. **Use SSL/TLS** para conexões remotas
5. **Mantenha o banco atualizado**

### Variáveis de Ambiente

Para maior segurança, use variáveis de ambiente:

```python
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

## 🐛 Solução de Problemas

### Erro: Não é possível conectar ao banco

**Soluções:**
- Verifique se o servidor está rodando
- Confirme usuário e senha
- Verifique firewall e permissões

### Erro: Tabela não existe

**Solução:**
```batch
python manage.py migrate
```

### Erro: Permissão negada

**Solução:**
- Verifique permissões do usuário do banco
- Garanta que o usuário tem privilégios necessários

## 📚 Recursos Adicionais

- [Documentação Django - Databases](https://docs.djangoproject.com/en/stable/ref/databases/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MySQL Documentation](https://dev.mysql.com/doc/)












