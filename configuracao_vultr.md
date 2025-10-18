# 🚀 CONFIGURAÇÃO DO SERVIDOR VULTR - SISTEMA RURAL COM IA

## 📋 **INFORMAÇÕES DO SERVIDOR**
- **IP:** 45.32.219.76
- **Senha:** 5hW(gsA.ftY,@UXj
- **Painel:** https://my.vultr.com/subs/?id=198f1d54-4602-4e0f-bd16-b9244d186c78

## 🔧 **PASSOS PARA DEPLOY**

### **1. Conectar ao Servidor**
```bash
ssh root@45.32.219.76
# Senha: 5hW(gsA.ftY,@UXj
```

### **2. Atualizar Sistema**
```bash
apt update && apt upgrade -y
```

### **3. Instalar Dependências**
```bash
# Python e dependências
apt install -y python3 python3-pip python3-venv

# PostgreSQL (banco de dados)
apt install -y postgresql postgresql-contrib

# Nginx (servidor web)
apt install -y nginx

# Git (para clonar o projeto)
apt install -y git
```

### **4. Configurar PostgreSQL**
```bash
# Acessar PostgreSQL
sudo -u postgres psql

# Criar banco de dados
CREATE DATABASE sistema_rural;

# Criar usuário
CREATE USER django_user WITH PASSWORD 'sua_senha_segura_123';

# Dar permissões
GRANT ALL PRIVILEGES ON DATABASE sistema_rural TO django_user;

# Sair do PostgreSQL
\q
```

### **5. Criar Usuário para Aplicação**
```bash
# Criar usuário django
useradd -m -s /bin/bash django
usermod -aG sudo django

# Definir senha para o usuário django
passwd django
# Senha sugerida: Django2025@
```

### **6. Configurar Projeto Django**

#### **Opção A: Upload via SCP (Recomendado)**
```bash
# No seu computador local, comprimir o projeto
tar -czf sistema-rural.tar.gz --exclude=venv --exclude=__pycache__ --exclude=db.sqlite3 .

# Upload para o servidor
scp sistema-rural.tar.gz root@45.32.219.76:/tmp/
```

#### **Opção B: Clonar do GitHub**
```bash
# No servidor, clonar projeto (substitua pela URL do seu repositório)
cd /home/django
git clone https://github.com/seu-usuario/sistema-rural.git
cd sistema-rural
```

### **7. Configurar Ambiente Python**
```bash
# Mudar para usuário django
su - django
cd sistema-rural

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements_producao.txt
```

### **8. Configurar Variáveis de Ambiente**
```bash
# Criar arquivo .env
nano .env
```

**Conteúdo do arquivo .env:**
```env
DEBUG=False
SECRET_KEY=sua-chave-secreta-super-segura-aqui-123456789
DB_NAME=sistema_rural
DB_USER=django_user
DB_PASSWORD=sua_senha_segura_123
DB_HOST=localhost
DB_PORT=5432
```

### **9. Configurar Django para Produção**
```bash
# Coletar arquivos estáticos
python manage.py collectstatic --noinput --settings=sistema_rural.settings_producao

# Executar migrações
python manage.py migrate --settings=sistema_rural.settings_producao

# Criar superusuário
python manage.py createsuperuser --settings=sistema_rural.settings_producao
```

### **10. Configurar Gunicorn**
```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/sistema-rural.service
```

**Conteúdo do arquivo:**
```ini
[Unit]
Description=Gunicorn daemon for Sistema Rural
After=network.target

[Service]
User=django
Group=www-data
WorkingDirectory=/home/django/sistema-rural
ExecStart=/home/django/sistema-rural/venv/bin/gunicorn --workers 3 --bind unix:/home/django/sistema-rural/sistema_rural.sock sistema_rural.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### **11. Configurar Nginx**
```bash
# Criar configuração do site
sudo nano /etc/nginx/sites-available/sistema-rural
```

**Conteúdo do arquivo:**
```nginx
server {
    listen 80;
    server_name 45.32.219.76;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/django/sistema-rural;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/django/sistema-rural/sistema_rural.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **12. Ativar Serviços**
```bash
# Ativar site no Nginx
sudo ln -s /etc/nginx/sites-available/sistema-rural /etc/nginx/sites-enabled
sudo rm /etc/nginx/sites-enabled/default

# Recarregar configurações
sudo systemctl daemon-reload

# Iniciar serviços
sudo systemctl start sistema-rural
sudo systemctl enable sistema-rural
sudo systemctl restart nginx

# Verificar status
sudo systemctl status sistema-rural
sudo systemctl status nginx
```

### **13. Configurar Firewall**
```bash
# Permitir SSH, HTTP e HTTPS
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

## 🎯 **RESULTADO ESPERADO**

Após completar todos os passos, o sistema estará disponível em:
- **URL:** http://45.32.219.76
- **Admin:** http://45.32.219.76/admin

## 🔍 **VERIFICAÇÃO**

```bash
# Verificar logs
sudo journalctl -u sistema-rural -f

# Verificar status dos serviços
sudo systemctl status sistema-rural
sudo systemctl status nginx

# Testar conectividade
curl http://45.32.219.76
```

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Se o serviço não iniciar:**
```bash
# Verificar logs
sudo journalctl -u sistema-rural -n 50

# Verificar permissões
sudo chown -R django:django /home/django/sistema-rural
sudo chmod -R 755 /home/django/sistema-rural
```

### **Se Nginx não funcionar:**
```bash
# Verificar configuração
sudo nginx -t

# Recarregar Nginx
sudo systemctl reload nginx
```

## 🔐 **SEGURANÇA ADICIONAL**

### **Configurar SSL (Certificado Gratuito)**
```bash
# Instalar Certbot
apt install -y certbot python3-certbot-nginx

# Obter certificado SSL
certbot --nginx -d 45.32.219.76
```

## 📊 **MONITORAMENTO**

### **Logs do Sistema**
```bash
# Logs da aplicação
tail -f /home/django/sistema-rural/sistema_rural.log

# Logs do Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## ✅ **SISTEMA PRONTO!**

O Sistema Rural com IA Inteligente estará rodando em produção com:
- 🏭 **Identificação automática de fazendas**
- 🤖 **IA para movimentações automáticas**
- 📊 **Projeções inteligentes**
- 💰 **Cálculos financeiros precisos**
- 🔄 **Evolução automática de rebanho**

**URL de Acesso:** http://45.32.219.76



