# 🛡️ Guia Completo: Segurança de Dados e Rollback Rápido

## 📋 Resumo Executivo

**SIM, seus dados sempre serão preservados** se você seguir as práticas abaixo. Este guia explica:
1. ✅ Por que seus dados estão seguros
2. ✅ Como fazer backup antes de cada atualização
3. ✅ Como restaurar o sistema imediatamente em caso de erro
4. ✅ Estratégias de versionamento e deploy seguro

---

## 🔒 Por Que Seus Dados Estão Seguros

### 1. Separação entre Código e Dados

**Código (aplicação):**
- Arquivos Python (`.py`)
- Templates HTML
- Arquivos estáticos (CSS, JS)
- Configurações

**Dados (banco de dados):**
- Armazenados em arquivos separados (SQLite) ou banco de dados (PostgreSQL/Cloud SQL)
- **NÃO são afetados por erros no código**
- Permanecem intactos mesmo se a aplicação cair

### 2. O Que Acontece em Caso de Erro

**Cenário 1: Erro de Programação**
- ❌ Sistema pode parar de funcionar
- ✅ **Dados permanecem intactos no banco**
- ✅ Restaurar código anterior resolve o problema

**Cenário 2: Erro em Migração de Banco**
- ⚠️ Pode afetar estrutura do banco
- ✅ **Dados antigos permanecem** (se você fez backup antes)
- ✅ Restaurar backup resolve

**Cenário 3: Erro Crítico no Servidor**
- ❌ Servidor pode ficar inacessível
- ✅ **Dados permanecem no banco de dados**
- ✅ Restaurar código + banco resolve

---

## 🚀 Estratégia de Backup e Rollback

### Fase 1: ANTES de Cada Atualização (OBRIGATÓRIO)

#### 1.1. Fazer Backup Completo

```bash
# No servidor de produção
python manage.py backup_completo --compress
```

Ou usando o script:
```bash
# Windows
scripts\manutencao\BACKUP_COMPLETO.bat

# Linux/Mac
./scripts/manutencao/BACKUP_COMPLETO.sh
```

**O que é feito:**
- ✅ Backup do banco principal (`db.sqlite3`)
- ✅ Backup de todos os tenants
- ✅ Backup de arquivos media (certificados, documentos)
- ✅ Compactação em ZIP
- ✅ Metadados com data/hora

**Localização:** `backups/backup_completo_YYYYMMDD_HHMMSS.zip`

#### 1.2. Verificar Git (Versionamento)

```bash
# Verificar se está tudo commitado
git status

# Se houver mudanças, fazer commit
git add .
git commit -m "Backup antes de atualização - [DESCRIÇÃO]"

# Criar tag para fácil rollback
git tag -a v1.0.0-backup-$(date +%Y%m%d) -m "Backup antes de atualização"
git push origin --tags
```

#### 1.3. Verificar Funcionamento Atual

```bash
# Testar se sistema está funcionando
python manage.py check

# Verificar migrações pendentes
python manage.py showmigrations
```

---

### Fase 2: DURANTE a Atualização

#### 2.1. Deploy Gradual (Recomendado)

**Opção A: Deploy com Revisão**
1. Fazer deploy em ambiente de teste primeiro
2. Testar funcionalidades críticas
3. Se tudo OK, fazer deploy em produção

**Opção B: Deploy Direto (com backup)**
1. ✅ Backup completo feito (Fase 1)
2. ✅ Código versionado no Git
3. Fazer deploy
4. Monitorar logs imediatamente

#### 2.2. Monitorar Após Deploy

```bash
# Verificar logs do servidor
# Google Cloud Run
gcloud run services logs read monpec --limit 50

# Ou verificar logs locais
tail -f logs/django.log
```

**Sinais de Problema:**
- ❌ Erro 500 (Internal Server Error)
- ❌ Erro 503 (Service Unavailable)
- ❌ Página em branco
- ❌ Erro de importação de módulos
- ❌ Erro de migração

---

### Fase 3: EM CASO DE ERRO - Rollback Imediato

#### 3.1. Rollback do Código (Git)

**Método Rápido - Reverter para versão anterior:**

```bash
# Ver histórico de commits
git log --oneline -10

# Reverter para commit anterior
git reset --hard HEAD~1

# Ou reverter para tag específica
git reset --hard v1.0.0-backup-20240101

# Forçar push (CUIDADO: apenas se necessário)
git push origin --force
```

**Método Seguro - Criar branch de rollback:**

```bash
# Criar branch a partir da versão que funcionava
git checkout -b rollback-emergencia v1.0.0-backup-20240101

# Fazer deploy desta branch
# (seguir processo de deploy normal)
```

#### 3.2. Rollback do Banco de Dados (se necessário)

**⚠️ APENAS se migrações causaram problema:**

```bash
# 1. Parar servidor
# 2. Restaurar banco principal
cp backups/backup_completo_YYYYMMDD_HHMMSS/db_principal_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3

# 3. Restaurar tenant específico (se necessário)
python manage.py restaurar_backup --backup-file backups/.../tenant_X_YYYYMMDD.sqlite3 --tenant-id X --force

# 4. Reiniciar servidor
```

#### 3.3. Rollback no Google Cloud

**Cloud Run:**
```bash
# Listar revisões
gcloud run revisions list --service monpec

# Fazer rollback para revisão anterior
gcloud run services update monpec --revision-suffix=REVISION-ANTERIOR
```

**App Engine:**
```bash
# Listar versões
gcloud app versions list

# Fazer rollback para versão anterior
gcloud app versions migrate VERSION-ANTERIOR --service default
```

---

## 📝 Checklist de Segurança

### ✅ Antes de Cada Deploy

- [ ] Backup completo feito (`backup_completo --compress`)
- [ ] Código commitado no Git
- [ ] Tag criada no Git para fácil rollback
- [ ] Migrações testadas localmente
- [ ] Sistema funcionando antes do deploy
- [ ] Logs verificados (sem erros)

### ✅ Durante o Deploy

- [ ] Monitorar logs em tempo real
- [ ] Testar funcionalidades críticas após deploy
- [ ] Verificar se migrações foram aplicadas corretamente

### ✅ Após Deploy (Primeiros 30 minutos)

- [ ] Verificar se sistema está acessível
- [ ] Testar login
- [ ] Testar funcionalidades principais
- [ ] Verificar logs para erros
- [ ] Monitorar uso de recursos

---

## 🔧 Scripts de Emergência

### Script 1: Backup Rápido Antes de Deploy

Criar arquivo: `scripts/emergencia/backup_antes_deploy.sh`

```bash
#!/bin/bash
# Backup rápido antes de deploy

echo "🔄 Fazendo backup antes de deploy..."
python manage.py backup_completo --compress --keep-days 7

echo "📦 Verificando Git..."
git status
git add .
git commit -m "Backup automático antes de deploy - $(date +%Y%m%d_%H%M%S)" || true

echo "🏷️ Criando tag de backup..."
git tag -a "backup-$(date +%Y%m%d_%H%M%S)" -m "Backup automático antes de deploy"
git push origin --tags || true

echo "✅ Backup concluído!"
```

### Script 2: Rollback Rápido

Criar arquivo: `scripts/emergencia/rollback_rapido.sh`

```bash
#!/bin/bash
# Rollback rápido do sistema

echo "⚠️ INICIANDO ROLLBACK DE EMERGÊNCIA"
echo ""

# 1. Listar backups disponíveis
echo "📦 Backups disponíveis:"
ls -lt backups/backup_completo_*.zip | head -5

# 2. Listar tags Git
echo ""
echo "🏷️ Tags Git disponíveis:"
git tag -l "backup-*" | tail -5

# 3. Perguntar qual versão restaurar
read -p "Digite a tag Git para restaurar (ex: backup-20240101_120000): " TAG

if [ -z "$TAG" ]; then
    echo "❌ Tag não especificada. Abortando."
    exit 1
fi

# 4. Fazer rollback do código
echo ""
echo "🔄 Revertendo código para tag: $TAG"
git fetch origin
git checkout -b rollback-emergencia-$TAG $TAG

# 5. Perguntar se precisa restaurar banco
read -p "Restaurar banco de dados também? (s/N): " RESTAURAR_DB

if [ "$RESTAURAR_DB" = "s" ] || [ "$RESTAURAR_DB" = "S" ]; then
    echo ""
    echo "📦 Listando backups de banco:"
    ls -lt backups/backup_completo_*/db_principal_*.sqlite3 | head -5
    
    read -p "Digite o caminho completo do backup do banco: " BACKUP_DB
    
    if [ -f "$BACKUP_DB" ]; then
        echo "🔄 Restaurando banco de dados..."
        cp db.sqlite3 db.sqlite3.backup-antes-rollback-$(date +%Y%m%d_%H%M%S)
        cp "$BACKUP_DB" db.sqlite3
        echo "✅ Banco restaurado!"
    else
        echo "❌ Arquivo de backup não encontrado!"
    fi
fi

echo ""
echo "✅ Rollback concluído!"
echo "⚠️ LEMBRE-SE: Fazer novo deploy após rollback!"
```

---

## 🎯 Estratégias Avançadas

### 1. Deploy Blue-Green (Zero Downtime)

**Conceito:** Manter duas versões rodando, alternar entre elas.

**Como fazer:**
1. Deploy nova versão em paralelo
2. Testar nova versão
3. Se OK, alternar tráfego para nova versão
4. Se erro, manter versão antiga

**Cloud Run:**
```bash
# Deploy nova revisão sem afetar atual
gcloud run deploy monpec --no-traffic

# Testar nova revisão
curl https://NOVA-REVISAO.run.app/health

# Se OK, alternar tráfego
gcloud run services update-traffic monpec --to-revisions=NOVA-REVISAO=100
```

### 2. Feature Flags

**Conceito:** Desabilitar funcionalidades problemáticas sem rollback completo.

**Implementação:**
```python
# settings.py
FEATURE_NOVA_FUNCIONALIDADE = os.getenv('FEATURE_NOVA_FUNCIONALIDADE', 'False') == 'True'

# views.py
if settings.FEATURE_NOVA_FUNCIONALIDADE:
    # Nova funcionalidade
else:
    # Funcionalidade antiga
```

**Vantagem:** Desabilitar feature problemática via variável de ambiente, sem redeploy.

### 3. Migrações Reversíveis

**Sempre criar migrações que podem ser revertidas:**

```python
# migrations/0001_exemplo.py
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(...),  # Pode ser revertido
    ]

# Para reverter:
python manage.py migrate app_name 0000  # Volta para antes desta migração
```

---

## 📊 Monitoramento e Alertas

### Configurar Alertas

**Google Cloud Monitoring:**
1. Ir para Cloud Console > Monitoring
2. Criar alerta para:
   - Erro 500 > 5 em 5 minutos
   - Erro 503 > 1 em 1 minuto
   - CPU > 90%
   - Memória > 90%

### Logs Importantes

**Verificar regularmente:**
- Erros de aplicação (500, 503)
- Erros de banco de dados
- Erros de migração
- Timeouts
- Falhas de autenticação

---

## 🆘 Procedimento de Emergência Completo

### Passo a Passo em Caso de Sistema Caído

1. **Identificar o Problema**
   ```bash
   # Verificar logs
   gcloud run services logs read monpec --limit 100
   ```

2. **Fazer Rollback Imediato**
   ```bash
   # Usar script de rollback
   ./scripts/emergencia/rollback_rapido.sh
   
   # Ou manualmente
   git reset --hard TAG_ANTERIOR
   gcloud run deploy monpec
   ```

3. **Verificar se Sistema Voltou**
   ```bash
   curl https://monpec.com.br/health
   ```

4. **Restaurar Banco (se necessário)**
   ```bash
   python manage.py restaurar_backup --backup-file CAMINHO_BACKUP
   ```

5. **Documentar o Problema**
   - O que causou o erro?
   - Como foi resolvido?
   - Como prevenir no futuro?

---

## ✅ Resumo: Seus Dados Estão Seguros Porque...

1. ✅ **Dados estão separados do código** - Banco de dados é independente
2. ✅ **Backups automáticos** - Sistema de backup completo implementado
3. ✅ **Versionamento Git** - Código versionado, fácil rollback
4. ✅ **Migrações reversíveis** - Pode voltar atrás em mudanças de banco
5. ✅ **Deploy gradual** - Pode testar antes de aplicar em produção
6. ✅ **Scripts de emergência** - Rollback rápido disponível

---

## 📞 Próximos Passos

1. **Testar processo de backup:**
   ```bash
   python manage.py backup_completo --compress
   ```

2. **Testar processo de rollback:**
   - Fazer mudança pequena
   - Fazer backup
   - Fazer deploy
   - Testar rollback

3. **Configurar alertas** no Google Cloud

4. **Documentar** procedimentos específicos do seu ambiente

---

**Última atualização:** 2025-01-XX
**Versão:** 1.0






