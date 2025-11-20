# 🌐 CONFIGURAÇÃO LOCAWEB CLOUD - MONPEC.COM.BR

## 📋 GUIA COMPLETO PARA CONFIGURAR NA LOCAWEB

### 🎯 **SITUAÇÃO ATUAL:**
- ✅ VM já criada: `VM-7ca5fc65-ba17-4f33-a5ed-2d2aab2ff847`
- ✅ Status: `Executando`
- ✅ IP: `10.1.1.234`
- ✅ Conta: `LOCAWEB-monpec`

---

## 🚀 **PASSO A PASSO PARA CONFIGURAR**

### **1. CONECTAR NA VM**
```bash
# Conectar via SSH na sua VM
ssh usuario@10.1.1.234

# Ou se tiver chave SSH configurada
ssh -i sua_chave_privada.pem usuario@10.1.1.234
```

### **2. ATUALIZAR SISTEMA**
```bash
# Atualizar pacotes
sudo apt update && sudo apt upgrade -y

# Instalar dependências básicas
sudo apt install -y curl wget git vim htop
```

### **3. INSTALAR PYTHON E DEPENDÊNCIAS**
```bash
# Instalar Python 3 e pip
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Instalar dependências do sistema
sudo apt install -y postgresql postgresql-contrib nginx certbot python3-certbot-nginx
```

### **4. CONFIGURAR POSTGRESQL**
```bash
# Iniciar PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar banco e usuário
sudo -u postgres psql -c "CREATE DATABASE monpec_db;"
sudo -u postgres psql -c "CREATE USER monpec_user WITH PASSWORD 'Monpec2025!';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;"
```

### **5. FAZER UPLOAD DO CÓDIGO**
```bash
# Opção 1: Via Git (recomendado)
cd /var/www
sudo git clone https://github.com/LMONCAO/Monpec_projetista.git monpec.com.br
sudo chown -R www-data:www-data monpec.com.br

# Opção 2: Via SCP (do seu computador)
# scp -r C:\Monpec_projetista\* usuario@10.1.1.234:/tmp/monpec/
```

### **6. CONFIGURAR AMBIENTE VIRTUAL**
```bash
cd /var/www/monpec.com.br
sudo python3 -m venv venv
sudo chown -R www-data:www-data venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_producao.txt
```

### **7. CONFIGURAR SETTINGS DE PRODUÇÃO**
```bash
# Criar arquivo de configuração de produção
sudo nano sistema_rural/settings_producao.py
```

**Conteúdo do arquivo:**
```python
import os
from .settings import *

# Configurações de produção
DEBUG = False
ALLOWED_HOSTS = ['monpec.com.br', 'www.monpec.com.br', '10.1.1.234', 'localhost']

# Banco de dados PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'monpec_db',
        'USER': 'monpec_user',
        'PASSWORD': 'Monpec2025!',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Configurações de segurança
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# Arquivos estáticos
STATIC_ROOT = '/var/www/monpec.com.br/static'
MEDIA_ROOT = '/var/www/monpec.com.br/media'

# Logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/monpec/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### **8. EXECUTAR MIGRAÇÕES**
```bash
# Configurar variável de ambiente
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### **9. CONFIGURAR NGINX**
```bash
# Criar configuração do Nginx
sudo nano /etc/nginx/sites-available/monpec.com.br
```

**Conteúdo:**
```nginx
server {
    listen 80;
    server_name monpec.com.br www.monpec.com.br 10.1.1.234;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/monpec.com.br/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/monpec.com.br/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/monpec.com.br /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### **10. CONFIGURAR GUNICORN**
```bash
# Criar serviço do Gunicorn
sudo nano /etc/systemd/system/monpec.service
```

**Conteúdo:**
```ini
[Unit]
Description=Monpec Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/monpec.com.br
Environment=DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
ExecStart=/var/www/monpec.com.br/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 sistema_rural.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable monpec
sudo systemctl start monpec
```

### **11. CONFIGURAR FIREWALL**
```bash
# Configurar UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### **12. CONFIGURAR DOMÍNIO**
```bash
# No painel da Locaweb, configurar:
# 1. DNS do domínio monpec.com.br apontando para 10.1.1.234
# 2. Configurar certificado SSL (Let's Encrypt)
```

---

## 🔧 **COMANDOS RÁPIDOS PARA EXECUTAR**

### **Script Completo:**
```bash
#!/bin/bash
# Configuração completa na Locaweb

# 1. Atualizar sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# 3. Configurar PostgreSQL
sudo -u postgres psql -c "CREATE DATABASE monpec_db;"
sudo -u postgres psql -c "CREATE USER monpec_user WITH PASSWORD 'Monpec2025!';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;"

# 4. Clonar repositório
cd /var/www
sudo git clone https://github.com/LMONCAO/Monpec_projetista.git monpec.com.br
sudo chown -R www-data:www-data monpec.com.br

# 5. Configurar ambiente
cd monpec.com.br
sudo python3 -m venv venv
sudo chown -R www-data:www-data venv
source venv/bin/activate
pip install -r requirements_producao.txt

# 6. Executar migrações
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
python manage.py migrate
python manage.py collectstatic --noinput

# 7. Configurar Nginx e Gunicorn (usar configurações acima)
# 8. Iniciar serviços
sudo systemctl restart nginx
sudo systemctl start monpec
```

---

## 🌐 **CONFIGURAÇÃO DO DOMÍNIO**

### **No painel da Locaweb:**
1. **Acessar DNS** do domínio monpec.com.br
2. **Configurar registros:**
   - `A` → `monpec.com.br` → `10.1.1.234`
   - `A` → `www.monpec.com.br` → `10.1.1.234`
3. **Aguardar propagação** (até 24h)

### **Configurar SSL:**
```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot --nginx -d monpec.com.br -d www.monpec.com.br
```

---

## ✅ **VERIFICAÇÃO FINAL**

### **Testar sistema:**
```bash
# 1. Verificar serviços
sudo systemctl status monpec
sudo systemctl status nginx

# 2. Testar acesso local
curl http://localhost:8000

# 3. Testar acesso externo
curl http://10.1.1.234
```

### **Logs para monitoramento:**
```bash
# Logs do Django
tail -f /var/log/monpec/django.log

# Logs do Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Logs do sistema
journalctl -u monpec -f
```

---

## 🎯 **RESULTADO FINAL**

- ✅ **URL:** `https://monpec.com.br`
- ✅ **IP:** `10.1.1.234`
- ✅ **SSL:** Certificado automático
- ✅ **Banco:** PostgreSQL
- ✅ **Servidor:** Nginx + Gunicorn
- ✅ **Backup:** Configurado

**🌐 Seu sistema estará rodando na Locaweb Cloud!**

