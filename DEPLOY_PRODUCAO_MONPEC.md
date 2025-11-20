# 🚀 DEPLOY PRODUÇÃO - MONPEC.COM.BR

## 📋 GUIA COMPLETO PARA PRODUÇÃO

### 🎯 **OBJETIVO:**
Colocar o sistema Monpec_projetista em produção no domínio **monpec.com.br**

---

## 📋 **CHECKLIST PRÉ-DEPLOY**

### ✅ **1. PREPARAÇÃO DO SISTEMA**

#### **1.1 Configurações de Produção**
```bash
# 1. Instalar dependências de produção
pip install gunicorn psycopg2-binary whitenoise

# 2. Configurar settings.py para produção
DEBUG = False
ALLOWED_HOSTS = ['monpec.com.br', 'www.monpec.com.br', 'localhost']

# 3. Configurar banco de dados PostgreSQL (recomendado)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'monpec_db',
        'USER': 'monpec_user',
        'PASSWORD': 'senha_segura',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### **1.2 Configurações de Segurança**
```python
# settings.py - Configurações de produção
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 🖥️ **CONFIGURAÇÃO DO SERVIDOR**

### **2.1 Estrutura de Diretórios**
```bash
# Criar estrutura no servidor
sudo mkdir -p /var/www/monpec.com.br
sudo mkdir -p /var/log/monpec
sudo mkdir -p /etc/nginx/sites-available
sudo mkdir -p /etc/nginx/sites-enabled
```

### **2.2 Configuração Nginx**
```nginx
# /etc/nginx/sites-available/monpec.com.br
server {
    listen 80;
    server_name monpec.com.br www.monpec.com.br;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name monpec.com.br www.monpec.com.br;
    
    # Certificado SSL
    ssl_certificate /etc/letsencrypt/live/monpec.com.br/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monpec.com.br/privkey.pem;
    
    # Configurações SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Logs
    access_log /var/log/nginx/monpec_access.log;
    error_log /var/log/nginx/monpec_error.log;
    
    # Arquivos estáticos
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
    
    # Aplicação Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### **2.3 Configuração Gunicorn**
```bash
# /etc/systemd/system/monpec.service
[Unit]
Description=Monpec Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/monpec.com.br
ExecStart=/var/www/monpec.com.br/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 sistema_rural.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

---

## 🔧 **PROCESSO DE DEPLOY**

### **3.1 Script de Deploy Automático**
```bash
#!/bin/bash
# deploy_monpec.sh

echo "🚀 INICIANDO DEPLOY MONPEC.COM.BR"

# 1. Backup do sistema atual
echo "📦 Fazendo backup..."
sudo cp -r /var/www/monpec.com.br /var/www/monpec_backup_$(date +%Y%m%d_%H%M%S)

# 2. Atualizar código
echo "📥 Atualizando código..."
cd /var/www/monpec.com.br
git pull origin main

# 3. Ativar ambiente virtual
source venv/bin/activate

# 4. Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# 5. Executar migrações
echo "🗄️ Executando migrações..."
python manage.py migrate

# 6. Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# 7. Reiniciar serviços
echo "🔄 Reiniciando serviços..."
sudo systemctl restart monpec
sudo systemctl restart nginx

# 8. Verificar status
echo "✅ Verificando status..."
sudo systemctl status monpec
sudo systemctl status nginx

echo "🎉 DEPLOY CONCLUÍDO!"
echo "🌐 Acesse: https://monpec.com.br"
```

### **3.2 Configuração de Backup Automático**
```bash
#!/bin/bash
# backup_monpec.sh

# Backup diário do banco de dados
pg_dump monpec_db > /var/backups/monpec_$(date +%Y%m%d).sql

# Backup dos arquivos de mídia
tar -czf /var/backups/monpec_media_$(date +%Y%m%d).tar.gz /var/www/monpec.com.br/media/

# Manter apenas backups dos últimos 30 dias
find /var/backups/ -name "monpec_*" -mtime +30 -delete

echo "✅ Backup concluído: $(date)"
```

---

## 🔐 **CONFIGURAÇÃO SSL (Let's Encrypt)**

### **4.1 Instalar Certbot**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot --nginx -d monpec.com.br -d www.monpec.com.br
```

### **4.2 Renovação Automática**
```bash
# Adicionar ao crontab
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 📊 **MONITORAMENTO**

### **5.1 Logs do Sistema**
```bash
# Ver logs em tempo real
sudo tail -f /var/log/nginx/monpec_access.log
sudo tail -f /var/log/nginx/monpec_error.log
sudo journalctl -u monpec -f
```

### **5.2 Monitoramento de Performance**
```bash
# Instalar ferramentas de monitoramento
sudo apt install htop iotop nethogs

# Verificar uso de recursos
htop
df -h
free -h
```

---

## 🚀 **COMANDOS DE DEPLOY RÁPIDO**

### **Deploy Manual:**
```bash
# 1. Conectar ao servidor
ssh usuario@monpec.com.br

# 2. Executar deploy
cd /var/www/monpec.com.br
./deploy_monpec.sh

# 3. Verificar status
sudo systemctl status monpec
curl -I https://monpec.com.br
```

### **Deploy via Git (Recomendado):**
```bash
# 1. Configurar webhook no GitHub
# 2. Criar script de webhook no servidor
# 3. Deploy automático a cada push
```

---

## 🔧 **CONFIGURAÇÕES AVANÇADAS**

### **6.1 Otimizações de Performance**
```python
# settings.py - Otimizações
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Compressão
MIDDLEWARE = [
    'django.middleware.gzip.GZipMiddleware',
    # ... outros middlewares
]
```

### **6.2 Configuração de Email**
```python
# settings.py - Email de produção
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'contato@monpec.com.br'
EMAIL_HOST_PASSWORD = 'senha_app_gmail'
```

---

## ✅ **CHECKLIST FINAL**

- [ ] ✅ Domínio configurado (monpec.com.br)
- [ ] ✅ SSL configurado (Let's Encrypt)
- [ ] ✅ Nginx configurado
- [ ] ✅ Gunicorn configurado
- [ ] ✅ Banco de dados PostgreSQL
- [ ] ✅ Backup automático
- [ ] ✅ Monitoramento ativo
- [ ] ✅ Deploy automático
- [ ] ✅ Testes de funcionamento

---

## 🎯 **PRÓXIMOS PASSOS**

1. **Configurar servidor** com as especificações acima
2. **Fazer primeiro deploy** manual
3. **Configurar backup** automático
4. **Testar todas as funcionalidades**
5. **Configurar monitoramento**
6. **Automatizar deploy** via Git

**🌐 Seu sistema estará disponível em: https://monpec.com.br**

