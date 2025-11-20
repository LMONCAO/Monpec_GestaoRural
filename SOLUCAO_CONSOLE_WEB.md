# 🖥️ SOLUÇÃO: USAR CONSOLE WEB DA LOCAWEB

## 🎯 **PROBLEMA RESOLVIDO:**
- ❌ SSH não funciona (erro de conta)
- ❌ Chave SSH com erro
- ✅ **SOLUÇÃO: Console Web**

---

## 🚀 **PASSO A PASSO:**

### **1. ACESSAR CONSOLE WEB**
1. **No painel da Locaweb**
2. **Vá em "VMs" → Sua VM**
3. **Clique em "Console" ou "Acesso via navegador"**
4. **Faça login** com as credenciais da VM

### **2. CREDENCIAIS PADRÃO CENTOS:**
```
Usuário: centos
Senha: [senha fornecida pela Locaweb]
```

### **3. CONFIGURAR SISTEMA VIA CONSOLE**

#### **A. Atualizar Sistema:**
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip postgresql-server postgresql-contrib nginx git curl wget
```

#### **B. Configurar PostgreSQL:**
```bash
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar banco
sudo -u postgres psql -c "CREATE DATABASE monpec_db;"
sudo -u postgres psql -c "CREATE USER monpec_user WITH PASSWORD 'Monpec2025!';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;"
```

#### **C. Clonar Repositório:**
```bash
cd /var/www
sudo git clone https://github.com/LMONCAO/Monpec_projetista.git monpec.com.br
sudo chown -R nginx:nginx monpec.com.br
```

#### **D. Configurar Ambiente Python:**
```bash
cd monpec.com.br
sudo python3 -m venv venv
sudo chown -R nginx:nginx venv
source venv/bin/activate
pip install -r requirements_producao.txt
```

#### **E. Configurar Django:**
```bash
# Criar settings de produção
sudo nano sistema_rural/settings_producao.py
```

**Conteúdo:**
```python
import os
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['*']

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

STATIC_ROOT = '/var/www/monpec.com.br/static'
MEDIA_ROOT = '/var/www/monpec.com.br/media'
```

#### **F. Executar Migrações:**
```bash
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

#### **G. Configurar Nginx:**
```bash
sudo nano /etc/nginx/conf.d/monpec.conf
```

**Conteúdo:**
```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /var/www/monpec.com.br/static/;
    }
    
    location /media/ {
        alias /var/www/monpec.com.br/media/;
    }
}
```

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### **H. Configurar Gunicorn:**
```bash
sudo nano /etc/systemd/system/monpec.service
```

**Conteúdo:**
```ini
[Unit]
Description=Monpec Gunicorn daemon
After=network.target

[Service]
User=nginx
Group=nginx
WorkingDirectory=/var/www/monpec.com.br
Environment=DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
ExecStart=/var/www/monpec.com.br/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 sistema_rural.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable monpec
sudo systemctl start monpec
```

#### **I. Configurar Firewall:**
```bash
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

### **4. TESTAR SISTEMA:**
```bash
# Verificar status
sudo systemctl status monpec
sudo systemctl status nginx

# Testar acesso
curl http://localhost:8000
```

---

## 🌐 **ACESSAR O SISTEMA:**

### **URLs:**
- **Local:** `http://localhost:8000`
- **IP da VM:** `http://[IP_DA_VM]:8000`
- **Domínio:** `http://monpec.com.br` (após configurar DNS)

### **Credenciais:**
- **Usuário:** `admin`
- **Senha:** `123456` (ou a que você criou)

---

## ✅ **VANTAGENS DO CONSOLE WEB:**

- ✅ **Não precisa SSH**
- ✅ **Não precisa chaves**
- ✅ **Acesso direto**
- ✅ **Funciona sempre**
- ✅ **Mais fácil**

---

## 🎯 **RESULTADO:**

Após seguir todos os passos:
- ✅ Sistema rodando na VM CentOS
- ✅ Acessível via IP público
- ✅ Banco PostgreSQL configurado
- ✅ Nginx + Gunicorn funcionando
- ✅ Pronto para produção

**🚀 Seu sistema estará funcionando na Locaweb!**

