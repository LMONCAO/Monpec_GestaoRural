# 🚀 Instruções Completas de Deploy - Sistema MONPEC

Este guia contém todas as instruções necessárias para fazer o deploy completo do sistema MONPEC no servidor de produção.

## 📋 Pré-requisitos

- Servidor Linux (Ubuntu/Debian recomendado) ou Windows Server
- Python 3.11 ou superior
- PostgreSQL (para produção) ou SQLite (para desenvolvimento)
- Servidor web (Apache ou Nginx)
- Acesso SSH ao servidor (para Linux)

## 🔧 Passo 1: Preparar o Servidor

### Linux (Ubuntu/Debian)

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib
sudo apt install -y apache2 libapache2-mod-wsgi-py3  # Para Apache
# OU
sudo apt install -y nginx  # Para Nginx

# Instalar Gunicorn (se usar Nginx)
pip3 install gunicorn
```

### Windows

- Instalar Python 3.11+ do site oficial
- Instalar PostgreSQL
- Instalar Apache ou IIS

## 📦 Passo 2: Fazer Upload dos Arquivos

Faça upload de todos os arquivos do projeto para o servidor:

```bash
# Via SCP (Linux)
scp -r /caminho/local/projeto usuario@servidor:/caminho/destino/

# Via SFTP ou FTP
# Use um cliente como FileZilla ou WinSCP
```

## 🔐 Passo 3: Configurar Variáveis de Ambiente

### Criar arquivo .env_producao

No servidor, crie o arquivo `.env_producao` na raiz do projeto:

```bash
cd /caminho/para/projeto
nano .env_producao
```

Conteúdo mínimo:

```env
DEBUG=False
SECRET_KEY=sua-chave-secreta-muito-segura-aqui-gerada-aleatoriamente
DB_NAME=monpec_db
DB_USER=monpec_user
DB_PASSWORD=SenhaSegura123!
DB_HOST=localhost
DB_PORT=5432
```

**⚠️ IMPORTANTE**: Gere uma SECRET_KEY segura:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🗄️ Passo 4: Configurar Banco de Dados PostgreSQL

### Linux

```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Criar banco de dados e usuário
CREATE DATABASE monpec_db;
CREATE USER monpec_user WITH PASSWORD 'SenhaSegura123!';
ALTER ROLE monpec_user SET client_encoding TO 'utf8';
ALTER ROLE monpec_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE monpec_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;
\q
```

## 🚀 Passo 5: Executar Deploy

### Linux

```bash
cd /caminho/para/projeto

# Dar permissão de execução
chmod +x DEPLOY_COMPLETO_PRODUCAO.sh

# Executar deploy
./DEPLOY_COMPLETO_PRODUCAO.sh
```

### Windows (PowerShell)

```powershell
cd C:\caminho\para\projeto

# Executar deploy
.\DEPLOY_COMPLETO_PRODUCAO.ps1
```

O script irá:
- ✅ Verificar dependências
- ✅ Instalar pacotes Python
- ✅ Aplicar migrações
- ✅ Coletar arquivos estáticos
- ✅ Verificar configurações
- ✅ Executar diagnóstico

## 🌐 Passo 6: Configurar Servidor Web

### Opção A: Apache (mod_wsgi)

1. **Copiar configuração**:
```bash
sudo cp configurar_apache_monpec.conf /etc/apache2/sites-available/monpec.conf
```

2. **Editar configuração**:
```bash
sudo nano /etc/apache2/sites-available/monpec.conf
```

Substitua:
- `/caminho/para/projeto` → caminho real do projeto
- `/caminho/para/venv` → caminho real do venv

3. **Habilitar site**:
```bash
sudo a2ensite monpec.conf
sudo a2enmod wsgi
sudo systemctl restart apache2
```

### Opção B: Nginx + Gunicorn

1. **Configurar Gunicorn**:
```bash
sudo cp gunicorn_monpec.service /etc/systemd/system/
sudo nano /etc/systemd/system/gunicorn_monpec.service
```

Substitua os caminhos e ajuste usuário/grupo.

2. **Iniciar Gunicorn**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn_monpec.service
sudo systemctl start gunicorn_monpec.service
sudo systemctl status gunicorn_monpec.service
```

3. **Configurar Nginx**:
```bash
sudo cp configurar_nginx_gunicorn_monpec.conf /etc/nginx/sites-available/monpec
sudo ln -s /etc/nginx/sites-available/monpec /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔍 Passo 7: Verificar e Testar

### 1. Verificar serviços

```bash
# Apache
sudo systemctl status apache2

# Nginx
sudo systemctl status nginx

# Gunicorn (se usar)
sudo systemctl status gunicorn_monpec
```

### 2. Verificar logs

```bash
# Logs Django
tail -f /var/log/monpec/django.log

# Logs Apache
tail -f /var/log/apache2/monpec_error.log

# Logs Nginx
tail -f /var/log/nginx/monpec_error.log

# Logs Gunicorn
tail -f /var/log/monpec/gunicorn_error.log
```

### 3. Testar acesso

- Abra o navegador e acesse: `http://monpec.com.br`
- Verifique se a página carrega
- Teste o login
- Verifique se não há erros no console do navegador

## 🛠️ Passo 8: Executar Diagnóstico

Se houver problemas, execute o diagnóstico:

```bash
python diagnosticar_erro_producao.py
```

Este script irá verificar:
- ✅ Sistema operacional
- ✅ Python e Django
- ✅ Variáveis de ambiente
- ✅ Banco de dados
- ✅ Migrações
- ✅ Arquivos estáticos
- ✅ Logs
- ✅ Configurações WSGI

## 🔄 Passo 9: Manutenção

### Atualizar código

```bash
cd /caminho/para/projeto
git pull  # Se usar Git
# ou fazer upload dos arquivos atualizados

# Reexecutar deploy
./DEPLOY_COMPLETO_PRODUCAO.sh
```

### Aplicar novas migrações

```bash
python manage.py migrate --settings=sistema_rural.settings_producao
```

### Atualizar arquivos estáticos

```bash
python manage.py collectstatic --settings=sistema_rural.settings_producao --noinput
```

### Reiniciar serviços

```bash
# Apache
sudo systemctl restart apache2

# Nginx
sudo systemctl restart nginx

# Gunicorn
sudo systemctl restart gunicorn_monpec
```

## 🐛 Solução de Problemas

### Erro 500 (Internal Server Error)

1. Verificar logs:
```bash
tail -50 /var/log/monpec/django.log
```

2. Executar diagnóstico:
```bash
python diagnosticar_erro_producao.py
```

3. Verificar configurações:
```bash
python manage.py check --settings=sistema_rural.settings_producao --deploy
```

### Erro de conexão com banco de dados

1. Verificar se PostgreSQL está rodando:
```bash
sudo systemctl status postgresql
```

2. Testar conexão:
```bash
python manage.py dbshell --settings=sistema_rural.settings_producao
```

3. Verificar credenciais no `.env_producao`

### Arquivos estáticos não carregam

1. Verificar permissões:
```bash
sudo chown -R www-data:www-data /var/www/monpec.com.br/static
sudo chmod -R 755 /var/www/monpec.com.br/static
```

2. Recoletar arquivos:
```bash
python manage.py collectstatic --settings=sistema_rural.settings_producao --noinput
```

### Erro de permissão

```bash
# Dar permissões corretas
sudo chown -R www-data:www-data /caminho/para/projeto
sudo chmod -R 755 /caminho/para/projeto
sudo chmod -R 775 /caminho/para/projeto/media
```

## 📞 Suporte

Se o problema persistir:

1. Execute `diagnosticar_erro_producao.py` e compartilhe a saída
2. Verifique todos os logs mencionados acima
3. Verifique as configurações do servidor web
4. Verifique as permissões dos arquivos e diretórios

## ✅ Checklist Final

- [ ] Python e Django instalados
- [ ] PostgreSQL configurado e rodando
- [ ] Arquivo `.env_producao` criado e configurado
- [ ] Deploy executado com sucesso
- [ ] Migrações aplicadas
- [ ] Arquivos estáticos coletados
- [ ] Servidor web configurado (Apache ou Nginx)
- [ ] Gunicorn configurado e rodando (se usar Nginx)
- [ ] Serviços iniciados e habilitados
- [ ] Site acessível em http://monpec.com.br
- [ ] Logs sendo gerados corretamente
- [ ] Sem erros nos logs

---

**Última atualização**: 26/12/2025









