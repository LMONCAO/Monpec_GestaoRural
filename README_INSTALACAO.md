# 🚀 Guia de Instalação - MONPEC Gestão Rural

Este guia explica como instalar e executar o sistema MONPEC Gestão Rural em uma nova máquina.

## 📋 Pré-requisitos

- **Python 3.8 ou superior** ([Download](https://www.python.org/downloads/))
- **Git** (para clonar o repositório)
- **PostgreSQL** (opcional - apenas se quiser usar banco de dados remoto)

## 🔧 Instalação Automática (Recomendado)

### Windows

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/LMONCAO/Monpec_GestaoRural.git
   cd Monpec_GestaoRural
   ```

2. **Execute o instalador:**
   ```bash
   INSTALAR.bat
   ```

3. **Inicie o servidor:**
   ```bash
   INICIAR.bat
   ```

### Linux/Mac

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/LMONCAO/Monpec_GestaoRural.git
   cd Monpec_GestaoRural
   ```

2. **Dê permissão de execução:**
   ```bash
   chmod +x INSTALAR.sh INICIAR.sh
   ```

3. **Execute o instalador:**
   ```bash
   ./INSTALAR.sh
   ```

4. **Inicie o servidor:**
   ```bash
   ./INICIAR.sh
   ```

## 📝 Instalação Manual

Se preferir instalar manualmente:

### 1. Clone o repositório
```bash
git clone https://github.com/LMONCAO/Monpec_GestaoRural.git
cd Monpec_GestaoRural
```

### 2. Crie um ambiente virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o ambiente
Crie um arquivo `.env` na raiz do projeto:

```env
# Configurações do Sistema
DEBUG=True
SECRET_KEY=django-insecure-change-in-production
ALLOWED_HOSTS=127.0.0.1,localhost

# Banco de Dados - SQLite (padrão para desenvolvimento)
DB_ENGINE=sqlite3
```

**Para usar PostgreSQL:**
```env
DB_ENGINE=postgresql
DB_NAME=sistema_rural
DB_USER=django_user
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

### 5. Execute as migrações
```bash
python manage.py migrate
```

### 6. Colete arquivos estáticos
```bash
python manage.py collectstatic --noinput
```

### 7. Crie um superusuário (opcional)
```bash
python manage.py createsuperuser
```

### 8. Inicie o servidor
```bash
python manage.py runserver
```

Acesse: http://127.0.0.1:8000

## 🗄️ Configuração do Banco de Dados

### Opção 1: SQLite (Padrão - Desenvolvimento)
Não precisa fazer nada! O sistema usa SQLite por padrão.

### Opção 2: PostgreSQL (Produção/Múltiplas Máquinas)

1. **Instale o PostgreSQL:**
   - Windows: [Download](https://www.postgresql.org/download/windows/)
   - Linux: `sudo apt-get install postgresql postgresql-contrib`
   - Mac: `brew install postgresql`

2. **Crie o banco de dados:**
   ```sql
   CREATE DATABASE sistema_rural;
   CREATE USER django_user WITH PASSWORD 'sua_senha_segura';
   GRANT ALL PRIVILEGES ON DATABASE sistema_rural TO django_user;
   ```

3. **Configure o `.env`:**
   ```env
   DB_ENGINE=postgresql
   DB_NAME=sistema_rural
   DB_USER=django_user
   DB_PASSWORD=sua_senha_segura
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Instale o driver PostgreSQL:**
   ```bash
   pip install psycopg2-binary
   ```

5. **Execute as migrações:**
   ```bash
   python manage.py migrate
   ```

## 📦 Migração de Dados

Se você já tem dados em outra máquina e quer migrar:

### Exportar dados (máquina antiga)
```bash
python manage.py dumpdata > backup.json
```

### Importar dados (máquina nova)
```bash
python manage.py loaddata backup.json
```

## 🔐 Primeiro Acesso

1. Acesse: http://127.0.0.1:8000
2. Se não tiver usuário, crie um superusuário:
   ```bash
   python manage.py createsuperuser
   ```
3. Faça login com as credenciais criadas

## 🛠️ Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Erro: "No such file or directory: 'db.sqlite3'"
```bash
python manage.py migrate
```

### Erro: "Port 8000 already in use"
```bash
python manage.py runserver 8001
```

### Erro de conexão com PostgreSQL
- Verifique se o PostgreSQL está rodando
- Verifique as credenciais no arquivo `.env`
- Verifique se o firewall permite conexões na porta 5432

## 📚 Documentação Adicional

- **Configuração de Banco de Dados:** Veja `CONFIGURACAO_BANCO_DADOS.md`
- **Estrutura do Projeto:** Veja a documentação no código

## 🆘 Suporte

Em caso de problemas:
1. Verifique se todos os pré-requisitos estão instalados
2. Execute o instalador novamente
3. Verifique os logs de erro
4. Consulte a documentação

## ✅ Checklist de Instalação

- [ ] Python 3.8+ instalado
- [ ] Repositório clonado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` configurado
- [ ] Migrações executadas (`python manage.py migrate`)
- [ ] Servidor iniciado (`python manage.py runserver`)
- [ ] Acesso ao sistema funcionando

---

**Desenvolvido por MONPEC** 🚜












