# 🔄 Sistema de Backup e Recuperação de Senha - MONPEC

## 📋 ÍNDICE

1. [Sistema de Backup](#sistema-de-backup)
2. [Recuperação de Senha](#recuperação-de-senha)
3. [Configuração](#configuração)
4. [Uso](#uso)

---

## 💾 SISTEMA DE BACKUP

### **Comando de Backup Manual**

```bash
# Backup de todos os tenants
python311\python.exe manage.py backup_tenants

# Backup de um tenant específico
python311\python.exe manage.py backup_tenants --tenant-id 1

# Backup comprimido (ZIP)
python311\python.exe manage.py backup_tenants --compress

# Backup em diretório específico
python311\python.exe manage.py backup_tenants --output-dir C:\backups\monpec
```

### **Características do Backup**

✅ **Backup automático de todos os tenants ativos**  
✅ **Compressão opcional (ZIP)**  
✅ **Metadados incluídos** (tenant_id, usuário, data, tamanho)  
✅ **Limpeza automática** de backups antigos (30 dias)  
✅ **Backup individual** por tenant  

### **Estrutura dos Backups**

```
backups/
├── tenant_1_alias_20250115_020000.sqlite3
├── tenant_1_alias_20250115_020000.metadata.json
├── tenant_2_alias_20250115_020000.sqlite3.zip
└── tenant_2_alias_20250115_020000.metadata.json
```

**Arquivo de Metadados:**
```json
{
  "tenant_id": 1,
  "alias": "tenant_1",
  "assinatura_id": 1,
  "usuario": "joao@fazenda.com",
  "data_backup": "20250115_020000",
  "tamanho_bytes": 1048576,
  "comprimido": false
}
```

### **Backup Automático Agendado**

#### **Windows (Task Scheduler):**

1. Abra o **Agendador de Tarefas**
2. Criar Tarefa Básica
3. Nome: "Backup MONPEC"
4. Disparador: Diariamente às 02:00
5. Ação: Iniciar programa
6. Programa: `python311\python.exe`
7. Argumentos: `backup_automatico.py`
8. Iniciar em: `C:\Monpec_projetista`

#### **Linux (Crontab):**

```bash
# Editar crontab
crontab -e

# Adicionar linha (backup diário às 02:00)
0 2 * * * cd /caminho/para/monpec && /usr/bin/python3 backup_automatico.py >> /var/log/monpec_backup.log 2>&1
```

### **Restaurar Backup**

```bash
# Restaurar backup
python311\python.exe manage.py restaurar_backup --backup-file backups/tenant_1_alias_20250115_020000.sqlite3

# Restaurar backup comprimido
python311\python.exe manage.py restaurar_backup --backup-file backups/tenant_1_alias_20250115_020000.sqlite3.zip

# Restaurar forçando (sobrescreve banco existente)
python311\python.exe manage.py restaurar_backup --backup-file backups/tenant_1.sqlite3 --force
```

**O sistema irá:**
- ✅ Detectar automaticamente o tenant_id do backup
- ✅ Fazer backup do banco atual antes de restaurar
- ✅ Restaurar o banco de dados
- ✅ Validar integridade

---

## 🔐 RECUPERAÇÃO DE SENHA

### **Como Funciona**

1. **Usuário solicita recuperação:**
   - Acessa: `/recuperar-senha/`
   - Informa e-mail cadastrado

2. **Sistema envia e-mail:**
   - Gera token único e seguro
   - Envia link de recuperação
   - Token expira em 24 horas

3. **Usuário redefine senha:**
   - Clica no link do e-mail
   - Define nova senha (atende requisitos de segurança)
   - Confirma nova senha

4. **Login com nova senha:**
   - Token é invalidado após uso
   - Usuário pode fazer login normalmente

### **URLs Disponíveis**

- `/recuperar-senha/` - Solicitar recuperação
- `/recuperar-senha/enviado/` - Confirmação de envio
- `/recuperar-senha/confirmar/<uid>/<token>/` - Redefinir senha
- `/recuperar-senha/concluido/` - Confirmação de conclusão

### **Requisitos da Nova Senha**

- ✅ Mínimo de **12 caracteres**
- ✅ Pelo menos **1 letra maiúscula**
- ✅ Pelo menos **1 letra minúscula**
- ✅ Pelo menos **1 número**
- ✅ Pelo menos **1 caractere especial** (!@#$%^&*...)

---

## ⚙️ CONFIGURAÇÃO

### **1. Configurar E-mail (settings.py)**

```python
# Para produção (Gmail)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'sua-senha-app'  # Use senha de app do Gmail
DEFAULT_FROM_EMAIL = 'noreply@monpec.com.br'

# Para desenvolvimento (console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### **2. Variáveis de Ambiente (Recomendado)**

```bash
# .env ou variáveis de ambiente
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
DEFAULT_FROM_EMAIL=noreply@monpec.com.br
BACKUP_DIR=C:\backups\monpec
```

### **3. Configurar Gmail (Senha de App)**

1. Acesse: https://myaccount.google.com/apppasswords
2. Gere uma senha de app
3. Use essa senha no `EMAIL_HOST_PASSWORD`

---

## 📖 USO

### **Backup Manual**

```bash
# Fazer backup agora
python311\python.exe manage.py backup_tenants --compress

# Verificar backups criados
dir backups\
```

### **Recuperação de Senha**

1. **Usuário esqueceu senha:**
   - Acessa: `http://seudominio.com/recuperar-senha/`
   - Informa e-mail
   - Recebe e-mail com link

2. **Usuário clica no link:**
   - Redirecionado para página de redefinição
   - Define nova senha
   - Confirma nova senha

3. **Login:**
   - Usa nova senha para fazer login

### **Restaurar Backup**

```bash
# Listar backups disponíveis
dir backups\tenant_*.sqlite3*

# Restaurar backup específico
python311\python.exe manage.py restaurar_backup --backup-file backups\tenant_1_alias_20250115_020000.sqlite3

# Verificar se restaurou
python311\python.exe manage.py shell
>>> from gestao_rural.models import TenantWorkspace
>>> tenant = TenantWorkspace.objects.get(id=1)
>>> print(tenant.caminho_banco)
```

---

## 🔒 SEGURANÇA

### **Backup**

- ✅ Backups são armazenados localmente
- ✅ Metadados incluem informações de auditoria
- ✅ Limpeza automática de backups antigos
- ✅ Backup do banco atual antes de restaurar

### **Recuperação de Senha**

- ✅ Token único e seguro (Django padrão)
- ✅ Token expira em 24 horas
- ✅ Token só pode ser usado uma vez
- ✅ Validação de senha forte obrigatória
- ✅ E-mail não revela informações sensíveis

---

## 📝 CHECKLIST

- [x] Comando de backup criado
- [x] Comando de restauração criado
- [x] Templates de recuperação de senha criados
- [x] URLs de recuperação configuradas
- [x] Configuração de e-mail no settings
- [ ] E-mail configurado (próximo passo)
- [ ] Backup automático agendado (próximo passo)
- [ ] Testes realizados

---

## 🚀 PRÓXIMOS PASSOS

1. **Configurar E-mail:**
   - Configurar SMTP no `settings.py`
   - Testar envio de e-mail

2. **Agendar Backup:**
   - Configurar Task Scheduler (Windows) ou Cron (Linux)
   - Testar backup automático

3. **Testar Recuperação:**
   - Solicitar recuperação de senha
   - Verificar recebimento do e-mail
   - Redefinir senha

---

**Última atualização:** Janeiro 2025






