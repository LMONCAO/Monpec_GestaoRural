# Configuração do Banco de Dados para Múltiplas Máquinas

## Problema
O sistema estava usando SQLite (banco local), o que impede o uso em múltiplas máquinas.

## Solução
O sistema agora suporta três tipos de banco de dados configuráveis via variáveis de ambiente:

1. **SQLite** (padrão - desenvolvimento local)
2. **PostgreSQL** (recomendado para produção/múltiplas máquinas)
3. **MySQL** (alternativa)

## Como Configurar

### Opção 1: SQLite (Desenvolvimento Local)
Não precisa fazer nada! O sistema usa SQLite por padrão.

### Opção 2: PostgreSQL (Recomendado para Produção)

1. **Instale o PostgreSQL** na máquina servidor:
   ```bash
   # Windows (usando Chocolatey)
   choco install postgresql
   
   # Linux (Ubuntu/Debian)
   sudo apt-get install postgresql postgresql-contrib
   ```

2. **Crie o banco de dados**:
   ```sql
   CREATE DATABASE sistema_rural;
   CREATE USER django_user WITH PASSWORD 'sua_senha_segura';
   GRANT ALL PRIVILEGES ON DATABASE sistema_rural TO django_user;
   ```

3. **Crie o arquivo `.env`** na raiz do projeto:
   ```env
   DEBUG=True
   SECRET_KEY=sua-chave-secreta-aqui
   ALLOWED_HOSTS=127.0.0.1,localhost,seu-ip-aqui
   
   DB_ENGINE=postgresql
   DB_NAME=sistema_rural
   DB_USER=django_user
   DB_PASSWORD=sua_senha_segura
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Execute as migrações**:
   ```bash
   python manage.py migrate
   ```

### Opção 3: MySQL

1. **Instale o MySQL** na máquina servidor

2. **Crie o banco de dados**:
   ```sql
   CREATE DATABASE sistema_rural CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'django_user'@'localhost' IDENTIFIED BY 'sua_senha_segura';
   GRANT ALL PRIVILEGES ON sistema_rural.* TO 'django_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Crie o arquivo `.env`**:
   ```env
   DB_ENGINE=mysql
   DB_NAME=sistema_rural
   DB_USER=django_user
   DB_PASSWORD=sua_senha_segura
   DB_HOST=localhost
   DB_PORT=3306
   ```

4. **Instale as dependências**:
   ```bash
   pip install mysqlclient
   pip install -r requirements.txt
   ```

## Usando em Múltiplas Máquinas

### Cenário 1: Banco de Dados na Nuvem
Use um serviço como:
- **AWS RDS** (PostgreSQL/MySQL)
- **Google Cloud SQL**
- **Azure Database**
- **ElephantSQL** (PostgreSQL gratuito)

Configure o `.env` com as credenciais do serviço:
```env
DB_ENGINE=postgresql
DB_NAME=seu_banco
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=seu-host.rds.amazonaws.com
DB_PORT=5432
```

### Cenário 2: Servidor Dedicado
1. Instale PostgreSQL/MySQL em um servidor
2. Configure firewall para permitir conexões
3. Em cada máquina cliente, configure o `.env` apontando para o servidor:
```env
DB_HOST=192.168.1.100  # IP do servidor
DB_PORT=5432
```

## Migração de Dados

Se você já tem dados no SQLite e quer migrar para PostgreSQL:

1. **Exporte os dados do SQLite**:
   ```bash
   python manage.py dumpdata > backup.json
   ```

2. **Configure o PostgreSQL** no `.env`

3. **Crie as tabelas no PostgreSQL**:
   ```bash
   python manage.py migrate
   ```

4. **Importe os dados**:
   ```bash
   python manage.py loaddata backup.json
   ```

## Segurança

⚠️ **IMPORTANTE**:
- **NUNCA** commite o arquivo `.env` no Git
- Use senhas fortes para o banco de dados
- Em produção, use SSL/TLS para conexões com o banco
- Configure firewall adequadamente

## Arquivo .env de Exemplo

Crie um arquivo `.env` na raiz do projeto com este conteúdo:

```env
# Desenvolvimento
DEBUG=True
SECRET_KEY=django-insecure-change-in-production
ALLOWED_HOSTS=127.0.0.1,localhost

# Banco de dados (SQLite - padrão)
DB_ENGINE=sqlite3

# Para PostgreSQL, descomente e configure:
# DB_ENGINE=postgresql
# DB_NAME=sistema_rural
# DB_USER=django_user
# DB_PASSWORD=sua_senha
# DB_HOST=localhost
# DB_PORT=5432
```

## Verificação

Para verificar se está funcionando:
```bash
python manage.py dbshell
```

Se conectar ao banco, está tudo OK!












