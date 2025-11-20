# 🚀 GUIA RÁPIDO - DEPLOY NA LOCAWEB

## 📋 INFORMAÇÕES DO SERVIDOR

- **IP da VM:** `10.1.1.234`
- **Usuário:** `ubuntu` (ou o usuário configurado na VM)
- **Chave SSH:** `@MONPEC.key (1-28)`
- **Domínio:** `monpec.com.br`

---

## 🎯 OPÇÃO 1: DEPLOY AUTOMÁTICO (RECOMENDADO)

### **Passo 1: Executar Script PowerShell**

No Windows PowerShell, execute:

```powershell
cd C:\Monpec_projetista
.\DEPLOY_LOCAWEB.ps1
```

### **Passo 2: Aguardar Configuração**

O script irá:
- ✅ Verificar conexão com servidor
- ✅ Fazer upload dos arquivos
- ✅ Instalar dependências
- ✅ Configurar banco de dados
- ✅ Configurar Nginx e Gunicorn
- ✅ Iniciar serviços

---

## 🎯 OPÇÃO 2: DEPLOY MANUAL VIA SSH

### **Passo 1: Conectar no Servidor**

```bash
ssh -i "@MONPEC.key (1-28)" ubuntu@10.1.1.234
```

**OU** se não tiver a chave SSH:

```bash
ssh ubuntu@10.1.1.234
# (inserir senha quando solicitado)
```

### **Passo 2: Executar Script de Configuração**

No servidor, execute:

```bash
cd /var/www
sudo git clone https://github.com/LMONCAO/Monpec_projetista.git monpec.com.br
cd monpec.com.br
sudo chmod +x configurar_locaweb.sh
sudo ./configurar_locaweb.sh
```

---

## 🎯 OPÇÃO 3: DEPLOY VIA CONSOLE WEB DA LOCAWEB

### **Passo 1: Acessar Console Web**

1. Acesse o painel da Locaweb
2. Vá em **VMs** → Sua VM
3. Clique em **Console** ou **Acesso via navegador**
4. Faça login com usuário/senha da VM

### **Passo 2: Executar Comandos**

No console web, execute:

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx git

# Clonar repositório
cd /var/www
sudo git clone https://github.com/LMONCAO/Monpec_projetista.git monpec.com.br
cd monpec.com.br

# Executar script de configuração
sudo chmod +x configurar_locaweb.sh
sudo ./configurar_locaweb.sh
```

---

## 🔧 CONFIGURAÇÕES IMPORTANTES

### **Banco de Dados PostgreSQL**

- **Nome:** `monpec_db`
- **Usuário:** `monpec_user`
- **Senha:** `Monpec2025!`
- **Host:** `localhost`
- **Porta:** `5432`

### **Credenciais Padrão do Admin**

- **Usuário:** `admin`
- **Senha:** `123456`

⚠️ **IMPORTANTE:** Altere a senha após o primeiro login!

---

## 📊 COMANDOS ÚTEIS APÓS DEPLOY

### **Verificar Status dos Serviços**

```bash
sudo systemctl status monpec
sudo systemctl status nginx
```

### **Ver Logs**

```bash
# Logs do Django
sudo tail -f /var/log/monpec/django.log

# Logs do Nginx
sudo tail -f /var/log/nginx/error.log

# Logs do sistema
sudo journalctl -u monpec -f
```

### **Reiniciar Serviços**

```bash
sudo systemctl restart monpec
sudo systemctl restart nginx
```

### **Atualizar Código**

```bash
cd /var/www/monpec.com.br
sudo git pull
source venv/bin/activate
pip install -r requirements_producao.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart monpec
```

---

## 🌐 CONFIGURAR DOMÍNIO E SSL

### **1. Configurar DNS**

No painel da Locaweb:
1. Acesse **DNS** do domínio `monpec.com.br`
2. Configure registros:
   - Tipo `A` → `monpec.com.br` → `10.1.1.234`
   - Tipo `A` → `www.monpec.com.br` → `10.1.1.234`
3. Aguarde propagação (até 24h)

### **2. Configurar SSL (HTTPS)**

No servidor, execute:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d monpec.com.br -d www.monpec.com.br
```

O certificado será renovado automaticamente.

---

## ✅ VERIFICAÇÃO FINAL

### **Testar Acesso**

1. **Por IP:** http://10.1.1.234
2. **Por Domínio:** http://monpec.com.br (após DNS)
3. **HTTPS:** https://monpec.com.br (após SSL)

### **Verificar Funcionalidades**

- ✅ Login funciona
- ✅ Dashboard carrega
- ✅ Arquivos estáticos carregam
- ✅ Banco de dados conecta

---

## 🆘 RESOLUÇÃO DE PROBLEMAS

### **Erro 502 Bad Gateway**

```bash
# Verificar se Gunicorn está rodando
sudo systemctl status monpec

# Reiniciar serviço
sudo systemctl restart monpec
```

### **Erro de Permissões**

```bash
sudo chown -R www-data:www-data /var/www/monpec.com.br
sudo chmod -R 755 /var/www/monpec.com.br
```

### **Erro de Banco de Dados**

```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Testar conexão
sudo -u postgres psql -c "\l"
```

### **Arquivos Estáticos Não Carregam**

```bash
cd /var/www/monpec.com.br
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

---

## 📞 SUPORTE

Se encontrar problemas:

1. Verifique os logs: `sudo tail -f /var/log/monpec/django.log`
2. Verifique status dos serviços: `sudo systemctl status monpec nginx`
3. Consulte a documentação completa: `CONFIGURAR_LOCAWEB.md`

---

**🎉 Sistema configurado e rodando na Locaweb!**






