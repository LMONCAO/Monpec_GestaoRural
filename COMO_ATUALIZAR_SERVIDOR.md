# 🚀 GUIA DE ATUALIZAÇÃO DO SERVIDOR

## 📋 Como Atualizar o Sistema Monpec no Servidor Locaweb

---

## ⚡ MÉTODO RÁPIDO (Recomendado)

### **No PowerShell do Windows:**

```powershell
# 1. Navegar para o projeto
cd C:\Monpec_projetista

# 2. Fazer backup remoto
ssh -i "C:\Users\lmonc\Downloads\monpecprojetista.key" root@191.252.225.106 "cd /var/www && tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz monpec.com.br/"

# 3. Transferir novos arquivos
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" -r gestao_rural/ia_*.py root@191.252.225.106:/var/www/monpec.com.br/gestao_rural/

# 4. Transferir documentação
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" *.md root@191.252.225.106:/var/www/monpec.com.br/

# 5. Reiniciar Django
ssh -i "C:\Users\lmonc\Downloads\monpecprojetista.key" root@191.252.225.106 "pkill -9 python && cd /var/www/monpec.com.br && source venv/bin/activate && nohup python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &"

# 6. Verificar
ssh -i "C:\Users\lmonc\Downloads\monpecprojetista.key" root@191.252.225.106 "ps aux | grep python && curl http://127.0.0.1:8000"
```

---

## 📝 MÉTODO MANUAL (Console Web)

### **1. Fazer Backup**

```bash
cd /var/www
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz monpec.com.br/
ls -lh backup_*.tar.gz
```

### **2. Criar Novos Arquivos de IA**

**Opção A:** Copiar via SSH (do Windows)
```powershell
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" -r gestao_rural/ia_*.py root@191.252.225.106:/var/www/monpec.com.br/gestao_rural/
```

**Opção B:** Criar manualmente no servidor
```bash
cd /var/www/monpec.com.br/gestao_rural/

# Criar cada arquivo
nano ia_nascimentos_aprimorado.py
# [Colar conteúdo do arquivo]
# Salvar: Ctrl+O, Enter, Ctrl+X

nano ia_compras_inteligentes.py
# [Colar conteúdo]

nano ia_vendas_otimizadas.py
# [Colar conteúdo]
```

### **3. Verificar Arquivos**

```bash
cd /var/www/monpec.com.br/gestao_rural/
ls -la ia_*.py

# Deve mostrar:
# ia_nascimentos_aprimorado.py
# ia_compras_inteligentes.py
# ia_vendas_otimizadas.py
# [outros arquivos ia_*.py existentes]
```

### **4. Reiniciar Sistema**

```bash
# Parar Django
pkill -9 python

# Ativar ambiente
cd /var/www/monpec.com.br
source venv/bin/activate

# Iniciar Django
nohup python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &

# Aguardar
sleep 3

# Verificar
ps aux | grep python
curl http://127.0.0.1:8000
```

---

## 🔄 MÉTODO GIT (Para Futuro)

### **Setup Inicial (Uma Vez):**

```bash
# No servidor
cd /var/www/monpec.com.br
git init
git remote add origin https://github.com/LMONCAO/Monpec_projetista.git

# No Windows
cd C:\Monpec_projetista
git add .
git commit -m "Adicionadas IAs aprimoradas"
git push origin main
```

### **Atualizações Futuras:**

```bash
# No servidor
cd /var/www/monpec.com.br
git pull origin main
source venv/bin/activate
python manage.py migrate
pkill -9 python
nohup python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &
```

---

## ✅ CHECKLIST DE ATUALIZAÇÃO

- [ ] Backup criado
- [ ] Arquivos transferidos (ia_nascimentos_aprimorado.py)
- [ ] Arquivos transferidos (ia_compras_inteligentes.py)
- [ ] Arquivos transferidos (ia_vendas_otimizadas.py)
- [ ] Documentação transferida (*.md)
- [ ] Django reiniciado
- [ ] Sistema testado (curl http://127.0.0.1:8000)
- [ ] Acesso externo testado (http://191.252.225.106)

---

## 🔍 VERIFICAÇÃO DE PROBLEMAS

### **Se Django não iniciar:**

```bash
# Ver logs
tail -50 /tmp/django.log

# Verificar erros de sintaxe
cd /var/www/monpec.com.br
source venv/bin/activate
python manage.py check

# Testar imports
python -c "from gestao_rural.ia_nascimentos_aprimorado import ia_nascimentos_aprimorada; print('OK')"
python -c "from gestao_rural.ia_compras_inteligentes import ia_compras_inteligentes; print('OK')"
python -c "from gestao_rural.ia_vendas_otimizadas import ia_vendas_otimizadas; print('OK')"
```

### **Se houver erro de import:**

```bash
# Verificar se arquivos existem
ls -la /var/www/monpec.com.br/gestao_rural/ia_*.py

# Verificar permissões
chmod 644 /var/www/monpec.com.br/gestao_rural/ia_*.py

# Verificar sintaxe Python
python -m py_compile /var/www/monpec.com.br/gestao_rural/ia_nascimentos_aprimorado.py
```

---

## 📊 TESTE DAS NOVAS IAs

### **1. Testar IA de Nascimentos:**

```python
# No shell do Django
python manage.py shell

from gestao_rural.ia_nascimentos_aprimorado import ia_nascimentos_aprimorada
from datetime import datetime

# Testar previsão
previsao = ia_nascimentos_aprimorada.prever_nascimentos_proximo_ano(
    matrizes_atuais=100,
    parametros=None  # Use seus parâmetros reais
)
print(previsao)
```

### **2. Testar IA de Compras:**

```python
from gestao_rural.ia_compras_inteligentes import ia_compras_inteligentes

inventario = {'Bezerros (0-12m)': 50, 'Garrotes (12-24m)': 30}
sugestoes = ia_compras_inteligentes.analisar_necessidade_compras(
    inventario_atual=inventario,
    perfil_fazenda='SO_ENGORDA',
    mes_atual=10
)
print(sugestoes)
```

### **3. Testar IA de Vendas:**

```python
from gestao_rural.ia_vendas_otimizadas import ia_vendas_otimizadas

oportunidades = ia_vendas_otimizadas.analisar_oportunidades_venda(
    inventario_atual={'Garrotes (12-24m)': 100},
    idade_media_categoria={'Garrotes (12-24m)': 18},
    peso_medio_categoria={'Garrotes (12-24m)': 380},
    mes_atual=2
)
print(oportunidades)
```

---

## 🎯 PRÓXIMAS ATUALIZAÇÕES

Para aplicar as próximas melhorias:

1. **Dashboards:** Adicionar templates HTML + JavaScript
2. **Relatórios:** Instalar `reportlab` e `openpyxl`
3. **SSL:** Executar `certbot --nginx -d monpec.com.br`
4. **Performance:** Instalar e configurar Redis
5. **UI/UX:** Atualizar Bootstrap para versão 5

---

## 📞 COMANDOS ÚTEIS

### **Ver status do sistema:**
```bash
ps aux | grep python          # Processos Python
ss -tlnp | grep :8000        # Django na porta 8000
ss -tlnp | grep :80          # Nginx na porta 80
systemctl status nginx       # Status do Nginx
curl http://localhost:80     # Teste interno
```

### **Ver logs:**
```bash
tail -f /tmp/django.log              # Logs do Django
tail -f /var/log/nginx/error.log    # Logs de erro do Nginx
tail -f /var/log/nginx/access.log   # Logs de acesso do Nginx
```

### **Reiniciar serviços:**
```bash
pkill -9 python                      # Parar Django
systemctl restart nginx              # Reiniciar Nginx
systemctl restart sshd               # Reiniciar SSH
```

---

## 🎉 CONCLUSÃO

Com este guia, você pode atualizar o sistema sempre que houver melhorias!

**Tempo estimado de atualização:** 5-10 minutos

**Próxima atualização:** Implementar dashboards interativos e relatórios PDF/Excel

---

**Última atualização:** 23/10/2025
**Versão:** 2.0 - IAs Aprimoradas

