# 🚀 DEPLOY RÁPIDO - SISTEMA RURAL COM IA

## 📋 **INFORMAÇÕES DO SERVIDOR**
- **IP:** 45.32.219.76
- **Senha:** 5hW(gsA.ftY,@UXj
- **Painel Vultr:** https://my.vultr.com/subs/?id=198f1d54-4602-4e0f-bd16-b9244d186c78

## ⚡ **DEPLOY EM 3 PASSOS**

### **1. Conectar ao Servidor**
```bash
ssh root@45.32.219.76
# Senha: 5hW(gsA.ftY,@UXj
```

### **2. Fazer Upload dos Arquivos**
```bash
# No seu computador local, comprimir o projeto
tar -czf sistema-rural.tar.gz --exclude=venv --exclude=__pycache__ --exclude=db.sqlite3 .

# Upload para o servidor
scp sistema-rural.tar.gz root@45.32.219.76:/tmp/

# No servidor, extrair arquivos
cd /tmp
tar -xzf sistema-rural.tar.gz -C /home/django/sistema-rural/
```

### **3. Executar Deploy Automático**
```bash
# No servidor, executar script de deploy
cd /home/django/sistema-rural
chmod +x deploy_automatico.sh
./deploy_automatico.sh
```

## 🎯 **RESULTADO**
- ✅ Sistema disponível em: **http://45.32.219.76**
- ✅ Admin: **http://45.32.219.76/admin**
- ✅ Usuário: **admin** / Senha: **admin123**

## 🔧 **COMANDOS ÚTEIS**

### **Verificar Status**
```bash
sudo systemctl status sistema-rural
sudo systemctl status nginx
```

### **Ver Logs**
```bash
sudo journalctl -u sistema-rural -f
```

### **Reiniciar Sistema**
```bash
sudo systemctl restart sistema-rural
sudo systemctl restart nginx
```

### **Atualizar Sistema**
```bash
cd /home/django/sistema-rural
git pull  # se usando git
sudo systemctl restart sistema-rural
```

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Se o serviço não iniciar:**
```bash
sudo journalctl -u sistema-rural -n 50
sudo chown -R django:django /home/django/sistema-rural
sudo systemctl restart sistema-rural
```

### **Se Nginx não funcionar:**
```bash
sudo nginx -t
sudo systemctl restart nginx
```

## 🔐 **SEGURANÇA**

### **Configurar SSL (Certificado Gratuito)**
```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d 45.32.219.76
```

---

## ✅ **SISTEMA PRONTO!**

O **Sistema Rural com IA Inteligente** estará rodando com:
- 🏭 **Identificação automática de fazendas**
- 🤖 **IA para movimentações automáticas** 
- 📊 **Projeções inteligentes**
- 💰 **Cálculos financeiros precisos**
- 🔄 **Evolução automática de rebanho**

**🌐 Acesse: http://45.32.219.76**



