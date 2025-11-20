# 🖥️ CONFIGURAR VIA CONSOLE WEB DA LOCAWEB

## 📋 QUANDO SSH NÃO FUNCIONA

### 🎯 **USAR CONSOLE WEB:**

1. **Acessar painel da Locaweb**
2. **Ir em "VMs" → Sua VM**
3. **Clicar em "Console" ou "Acesso via navegador"**
4. **Fazer login** com usuário/senha da VM

---

## 🚀 **CONFIGURAÇÃO VIA CONSOLE WEB**

### **1. LOGIN NA VM**
```bash
# Usar credenciais da VM (fornecidas pela Locaweb)
# Geralmente: ubuntu/ubuntu ou root/senha_fornecida
```

### **2. ATUALIZAR SISTEMA**
```bash
sudo apt update && sudo apt upgrade -y
```

### **3. INSTALAR DEPENDÊNCIAS**
```bash
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git curl wget
```

### **4. CONFIGURAR POSTGRESQL**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
sudo -u postgres psql -c "CREATE DATABASE monpec_db;"
sudo -u postgres psql -c "CREATE USER monpec_user WITH PASSWORD 'Monpec2025!';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE monpec_db TO monpec_user;"
```

### **5. CLONAR REPOSITÓRIO**
```bash
cd /var/www
sudo git clone https://github.com/LMONCAO/Monpec_projetista.git monpec.com.br
sudo chown -R www-data:www-data monpec.com.br
```

### **6. CONFIGURAR AMBIENTE**
```bash
cd monpec.com.br
sudo python3 -m venv venv
sudo chown -R www-data:www-data venv
source venv/bin/activate
pip install -r requirements_producao.txt
```

### **7. CONFIGURAR SETTINGS**
```bash
# Criar arquivo de configuração
sudo nano sistema_rural/settings_producao.py
```

**Conteúdo:**
```python
import os
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['*']  # Permitir qualquer IP

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

### **8. EXECUTAR MIGRAÇÕES**
```bash
export DJANGO_SETTINGS_MODULE=sistema_rural.settings_producao
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### **9. CONFIGURAR NGINX**
```bash
sudo nano /etc/nginx/sites-available/monpec.com.br
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
sudo ln -s /etc/nginx/sites-available/monpec.com.br /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### **10. CONFIGURAR GUNICORN**
```bash
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
sudo systemctl daemon-reload
sudo systemctl enable monpec
sudo systemctl start monpec
```

### **11. CONFIGURAR FIREWALL**
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### **12. TESTAR SISTEMA**
```bash
# Verificar status
sudo systemctl status monpec
sudo systemctl status nginx

# Testar acesso
curl http://localhost:8000
```

---

## 🌐 **ACESSAR O SISTEMA**

### **URLs para testar:**
- **Local:** `http://localhost:8000`
- **IP da VM:** `http://[IP_DA_VM]:8000`
- **Via domínio:** `http://monpec.com.br` (após configurar DNS)

### **Credenciais:**
- **Usuário:** `admin`
- **Senha:** `123456` (ou a que você criou)

---

## 🔧 **TROUBLESHOOTING**

### **Se não funcionar:**
```bash
# Verificar logs
sudo journalctl -u monpec -f
sudo tail -f /var/log/nginx/error.log

# Verificar porta
sudo netstat -tlnp | grep :8000

# Reiniciar serviços
sudo systemctl restart monpec
sudo systemctl restart nginx
```

### **Verificar IP público:**
```bash
curl ifconfig.me
```

---

## ✅ **RESULTADO FINAL**

Após seguir todos os passos:
- ✅ Sistema rodando na VM
- ✅ Acessível via IP público
- ✅ Banco PostgreSQL configurado
- ✅ Nginx + Gunicorn funcionando
- ✅ Pronto para configurar domínio

**🎯 Seu sistema estará funcionando na Locaweb!**

