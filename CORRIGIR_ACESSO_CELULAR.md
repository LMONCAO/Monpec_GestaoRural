# 📱 CORRIGIR ACESSO PELO CELULAR

## 🔍 PROBLEMAS IDENTIFICADOS

O sistema não está acessível pelo celular devido a:

1. **SECURE_SSL_REDIRECT = True** - Força HTTPS, mas sem certificado SSL configurado
2. **ALLOWED_HOSTS** pode não incluir o IP correto
3. **Servidor pode estar escutando apenas em 127.0.0.1** ao invés de 0.0.0.0
4. **Firewall pode estar bloqueando** conexões externas

---

## ✅ SOLUÇÃO COMPLETA

### **PASSO 1: Verificar IP do Servidor**

No servidor, execute:
```bash
# Ver IP público (se for servidor na internet)
curl -s ifconfig.me

# Ver IP local (se for na mesma rede Wi-Fi)
hostname -I
# ou
ip addr show | grep "inet " | grep -v 127.0.0.1
```

**Anote o IP que aparecer!**

---

### **PASSO 2: Corrigir settings_producao.py**

Edite o arquivo `sistema_rural/settings_producao.py`:

```python
# DESABILITAR SSL temporariamente para teste
SECURE_SSL_REDIRECT = False  # ⚠️ Mude de True para False

# Adicionar IP do servidor no ALLOWED_HOSTS
ALLOWED_HOSTS = [
    'monpec.com.br',
    'www.monpec.com.br',
    '10.1.1.234',  # IP da VM Locaweb
    'localhost',
    '127.0.0.1',
    '0.0.0.0',  # ✅ ADICIONAR ESTA LINHA
    # ✅ ADICIONAR O IP DO SEU SERVIDOR AQUI (exemplo: '192.168.1.100')
]

# Adicionar IP no CSRF_TRUSTED_ORIGINS
CSRF_TRUSTED_ORIGINS = [
    'https://monpec.com.br',
    'https://www.monpec.com.br',
    'http://10.1.1.234',  # ✅ ADICIONAR IP COM HTTP
    'http://localhost:8000',
    # ✅ ADICIONAR: 'http://SEU_IP_AQUI:8000'
]

# DESABILITAR cookies seguros temporariamente
SESSION_COOKIE_SECURE = False  # ⚠️ Mude de True para False
CSRF_COOKIE_SECURE = False  # ⚠️ Mude de True para False
```

---

### **PASSO 3: Garantir que o Servidor Escuta em 0.0.0.0**

O servidor Django DEVE escutar em `0.0.0.0` para aceitar conexões externas:

```bash
# ✅ CORRETO - Aceita conexões de qualquer IP
python manage.py runserver 0.0.0.0:8000

# ❌ ERRADO - Aceita apenas conexões locais
python manage.py runserver 127.0.0.1:8000
```

**Se estiver usando Gunicorn:**
```bash
gunicorn --bind 0.0.0.0:8000 sistema_rural.wsgi:application
```

---

### **PASSO 4: Verificar e Configurar Firewall**

No servidor, execute:

```bash
# Verificar status do firewall
sudo ufw status

# Permitir porta 8000 (se estiver usando runserver)
sudo ufw allow 8000/tcp

# Permitir porta 80 (se estiver usando Nginx)
sudo ufw allow 80/tcp

# Permitir porta 443 (se estiver usando HTTPS)
sudo ufw allow 443/tcp

# Ativar firewall
sudo ufw enable
```

**Se estiver na mesma rede Wi-Fi:**
- O firewall do roteador pode estar bloqueando
- Tente desabilitar temporariamente o firewall do Windows/Linux para teste

---

### **PASSO 5: Testar Acesso**

**No celular, tente acessar:**

1. **Se estiver na mesma rede Wi-Fi:**
   ```
   http://192.168.1.XXX:8000
   ```
   (Substitua XXX pelo IP local do servidor)

2. **Se o servidor estiver na internet:**
   ```
   http://10.1.1.234:8000
   ```
   ou
   ```
   http://monpec.com.br
   ```

---

## 🚨 PROBLEMAS COMUNS E SOLUÇÕES

### **Erro: "DisallowedHost"**
**Causa:** IP não está em ALLOWED_HOSTS

**Solução:**
```python
# Adicione o IP em settings_producao.py
ALLOWED_HOSTS = [
    'monpec.com.br',
    'www.monpec.com.br',
    '10.1.1.234',
    'SEU_IP_AQUI',  # ✅ ADICIONAR
    '0.0.0.0',
]
```

---

### **Erro: "Connection Refused"**
**Causa:** Servidor não está escutando em 0.0.0.0 ou firewall bloqueando

**Solução:**
```bash
# Verificar se está escutando
netstat -tlnp | grep :8000

# Deve mostrar: 0.0.0.0:8000
# Se mostrar: 127.0.0.1:8000, está errado!

# Reiniciar servidor corretamente
python manage.py runserver 0.0.0.0:8000
```

---

### **Erro: "SSL Required" ou redirecionamento infinito**
**Causa:** SECURE_SSL_REDIRECT = True sem certificado SSL

**Solução:**
```python
# Em settings_producao.py, desabilitar temporariamente:
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
```

---

### **Erro: "CSRF verification failed"**
**Causa:** IP não está em CSRF_TRUSTED_ORIGINS

**Solução:**
```python
# Em settings_producao.py:
CSRF_TRUSTED_ORIGINS = [
    'http://10.1.1.234:8000',  # ✅ ADICIONAR COM PORTA
    'http://SEU_IP:8000',  # ✅ ADICIONAR SEU IP
]
```

---

## 📋 CHECKLIST RÁPIDO

- [ ] IP do servidor identificado
- [ ] ALLOWED_HOSTS atualizado com o IP
- [ ] CSRF_TRUSTED_ORIGINS atualizado
- [ ] SECURE_SSL_REDIRECT = False (para teste)
- [ ] Servidor escutando em 0.0.0.0:8000
- [ ] Firewall permitindo porta 8000
- [ ] Testado no celular

---

## 🔧 COMANDOS RÁPIDOS PARA EXECUTAR NO SERVIDOR

```bash
# 1. Parar servidor atual
pkill -f "python.*manage.py runserver"

# 2. Ir para o diretório do projeto
cd /var/www/monpec.com.br  # ou caminho do seu projeto

# 3. Ativar ambiente virtual
source venv/bin/activate

# 4. Verificar IP
hostname -I

# 5. Iniciar servidor corretamente
python manage.py runserver 0.0.0.0:8000 --settings=sistema_rural.settings_producao
```

---

## 📱 TESTE NO CELULAR

1. **Conecte o celular na mesma rede Wi-Fi do servidor**
2. **Abra o navegador no celular**
3. **Digite:** `http://IP_DO_SERVIDOR:8000`
   - Exemplo: `http://192.168.1.100:8000`
   - Ou: `http://10.1.1.234:8000`

**Se não funcionar:**
- Verifique se o IP está correto
- Verifique se o servidor está rodando
- Verifique firewall
- Tente desabilitar temporariamente o firewall do servidor para teste

---

## ✅ DEPOIS QUE FUNCIONAR

Quando conseguir acessar pelo celular, você pode:

1. **Configurar SSL corretamente** (Let's Encrypt)
2. **Reativar SECURE_SSL_REDIRECT = True**
3. **Configurar domínio** (monpec.com.br)
4. **Usar Nginx como proxy reverso**

---

**Última atualização:** Dezembro 2025







