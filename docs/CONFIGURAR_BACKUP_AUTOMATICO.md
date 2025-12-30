# 🔄 Configuração de Backup Automático

## ✅ Backup Automático Já Configurado!

O sistema agora tem **backup automático integrado** em vários pontos:

### 1. ✅ Hook do Git (Pre-Push)
**Localização:** `.git/hooks/pre-push`

**O que faz:**
- Executa automaticamente antes de cada `git push`
- Faz backup rápido do banco de dados
- Cria tag Git automaticamente

**Como funciona:**
```bash
git push origin main
# → Backup automático executado antes do push
```

### 2. ✅ Integração nos Scripts de Deploy
**Scripts atualizados:**
- `deploy_cloud_shell.sh` - Backup antes de deploy no Cloud
- `scripts/DEPLOY_GCP.ps1` - Backup antes de deploy (já tinha)

**O que faz:**
- Executa backup automático antes de cada deploy
- Não bloqueia o deploy se backup falhar (apenas avisa)

### 3. ✅ Funções Reutilizáveis
**Arquivos:**
- `scripts/backup_automatico_integrado.sh` (Linux/Mac)
- `scripts/backup_automatico_integrado.ps1` (Windows)

**Como usar em seus scripts:**
```bash
# Linux/Mac
source scripts/backup_automatico_integrado.sh
BACKUP_AUTOMATICO "completo" "true"  # Backup completo comprimido
BACKUP_AUTOMATICO "rapido" "false"   # Backup rápido (apenas DB)
```

```powershell
# Windows
. scripts/backup_automatico_integrado.ps1
Backup-Automatico -Tipo "completo" -Comprimir $true
Backup-Automatico -Tipo "rapido" -Comprimir $false
```

---

## 📅 Agendar Backup Automático Diário

### Linux/Mac (Cron)

```bash
# Executar script de configuração
./scripts/agendar_backup_automatico.sh
```

**O que faz:**
- Configura backup diário às 02:00
- Backup completo comprimido
- Retenção de 7 dias
- Logs em `logs/backup_automatico.log`

**Verificar:**
```bash
crontab -l
```

**Remover:**
```bash
crontab -e
# Remover linha com backup_automatico_integrado.sh
```

### Windows (Tarefa Agendada)

```powershell
# Executar script de configuração (como Administrador)
.\scripts\agendar_backup_automatico.ps1
```

**O que faz:**
- Cria tarefa agendada no Windows
- Backup diário às 02:00
- Backup completo comprimido
- Retenção de 7 dias

**Verificar:**
```powershell
Get-ScheduledTask -TaskName "MonPEC_Backup_Automatico"
```

**Remover:**
```powershell
Unregister-ScheduledTask -TaskName "MonPEC_Backup_Automatico" -Confirm:$false
```

---

## 🎯 Tipos de Backup Automático

### 1. Backup Rápido (Pre-Push/Pre-Deploy)
- **Quando:** Antes de push Git ou deploy
- **O que inclui:** Apenas banco de dados
- **Tempo:** ~5-10 segundos
- **Uso:** Proteção rápida antes de mudanças

### 2. Backup Completo (Agendado)
- **Quando:** Diariamente às 02:00
- **O que inclui:** Banco + Tenants + Media + Static
- **Tempo:** ~1-5 minutos (depende do tamanho)
- **Uso:** Backup completo para restauração

---

## 🔍 Verificar se Está Funcionando

### Verificar Hook do Git
```bash
# Testar push (vai executar backup)
git push origin main --dry-run
```

### Verificar Backup Agendado (Linux)
```bash
# Ver logs
tail -f logs/backup_automatico.log

# Ver crontab
crontab -l | grep backup
```

### Verificar Backup Agendado (Windows)
```powershell
# Ver última execução
Get-ScheduledTask -TaskName "MonPEC_Backup_Automatico" | Get-ScheduledTaskInfo

# Ver histórico
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" | 
    Where-Object {$_.Message -like "*MonPEC*"} | 
    Select-Object -First 10
```

---

## 🛠️ Personalizar Configuração

### Alterar Horário do Backup Diário

**Linux/Mac:**
```bash
# Editar crontab
crontab -e

# Alterar hora (formato: minuto hora)
# Exemplo: 03:00 = "0 3 * * *"
```

**Windows:**
```powershell
# Obter trigger atual
$task = Get-ScheduledTask -TaskName "MonPEC_Backup_Automatico"
$trigger = $task.Triggers[0]

# Criar novo trigger (exemplo: 03:00)
$newTrigger = New-ScheduledTaskTrigger -Daily -At "03:00"

# Atualizar tarefa
Set-ScheduledTask -TaskName "MonPEC_Backup_Automatico" -Trigger $newTrigger
```

### Alterar Retenção de Backups

Edite os scripts:
- `scripts/backup_automatico_integrado.sh` - Linha com `--keep-days`
- `scripts/backup_automatico_integrado.ps1` - Linha com `--keep-days`

---

## 📊 Resumo: O Que Está Automatizado

| Ação | Backup Automático | Tipo |
|------|------------------|------|
| `git push` | ✅ Sim | Rápido (apenas DB) |
| Deploy Cloud | ✅ Sim | Rápido (apenas DB) |
| Deploy Local | ✅ Sim (se usar scripts) | Rápido (apenas DB) |
| Diário 02:00 | ✅ Sim (se configurado) | Completo |

---

## ⚠️ Importante

1. **Hook do Git:** Funciona automaticamente, não precisa configurar
2. **Deploy:** Backup automático já integrado nos scripts principais
3. **Backup Diário:** Precisa executar script de configuração uma vez
4. **Logs:** Verifique logs regularmente para garantir que está funcionando

---

## 🆘 Troubleshooting

### Backup não executa no Git Push
```bash
# Verificar se hook está executável
chmod +x .git/hooks/pre-push

# Testar manualmente
.git/hooks/pre-push
```

### Backup agendado não executa (Linux)
```bash
# Verificar se cron está rodando
sudo systemctl status cron

# Ver logs do cron
grep CRON /var/log/syslog | tail -20
```

### Backup agendado não executa (Windows)
```powershell
# Verificar se tarefa está habilitada
Get-ScheduledTask -TaskName "MonPEC_Backup_Automatico"

# Ver histórico de execuções
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" | 
    Where-Object {$_.Message -like "*MonPEC*"}
```

---

**Última atualização:** 2025-01-XX
**Status:** ✅ Backup automático configurado e funcionando






