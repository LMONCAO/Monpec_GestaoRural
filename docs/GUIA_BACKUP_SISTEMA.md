# 📦 Guia Completo de Backup do Sistema - MonPEC Gestão Rural

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [O que é feito backup](#o-que-é-feito-backup)
3. [Como fazer backup](#como-fazer-backup)
4. [Restaurar backup](#restaurar-backup)
5. [Backup automático](#backup-automático)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

O sistema possui um comando Django completo que faz backup de:
- ✅ Banco de dados principal (`db.sqlite3`)
- ✅ Bancos de dados de todos os tenants ativos
- ✅ Arquivos media (uploads, certificados digitais, documentos)
- ✅ Arquivos static (opcional)

---

## 📦 O que é feito backup

### 1. Banco de Dados Principal
- Arquivo: `db.sqlite3`
- Contém: Usuários, assinaturas, configurações gerais, tenants

### 2. Bancos de Dados dos Tenants
- Um arquivo por tenant ativo
- Contém: Dados específicos de cada cliente (propriedades, animais, etc.)
- Inclui arquivo de metadados com informações do tenant

### 3. Arquivos Media
- Certificados digitais (`.p12`, `.pfx`)
- Documentos enviados
- Imagens e arquivos de upload
- Qualquer arquivo salvo em `MEDIA_ROOT`

### 4. Arquivos Static (opcional)
- Arquivos CSS, JavaScript coletados
- Geralmente não precisa de backup (podem ser regenerados)

---

## 🚀 Como fazer backup

### Método 1: Comando Django (Recomendado)

#### Backup Completo (Recomendado)
```bash
python manage.py backup_completo
```

#### Backup Completo Comprimido (Economiza espaço)
```bash
python manage.py backup_completo --compress
```

#### Backup Apenas Bancos de Dados
```bash
python manage.py backup_completo --only-db
```

#### Backup Apenas Arquivos Media
```bash
python manage.py backup_completo --only-media
```

#### Especificar Diretório de Saída
```bash
python manage.py backup_completo --output-dir /caminho/para/backups
```

#### Manter Backups dos Últimos X Dias
```bash
python manage.py backup_completo --keep-days 60  # Manter 60 dias
```

### Método 2: Scripts Automatizados

#### Windows
```batch
scripts\manutencao\BACKUP_COMPLETO.bat
```

#### Linux/Mac
```bash
chmod +x scripts/manutencao/BACKUP_COMPLETO.sh
./scripts/manutencao/BACKUP_COMPLETO.sh
```

### Método 3: Backup Apenas de Tenants

Se precisar fazer backup apenas dos tenants:
```bash
python manage.py backup_tenants
python manage.py backup_tenants --compress
python manage.py backup_tenants --tenant-id 123  # Backup de tenant específico
```

---

## 🔄 Restaurar backup

### Restaurar Banco Principal

#### SQLite
```bash
# 1. Parar o servidor Django
# 2. Fazer backup do banco atual (caso algo dê errado)
cp db.sqlite3 db.sqlite3.backup

# 3. Copiar backup sobre o banco atual
cp backups/backup_completo_YYYYMMDD_HHMMSS/db_principal_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3

# 4. Reiniciar servidor
```

#### PostgreSQL (se migrado)
```bash
# Restaurar dump
pg_restore -d nome_banco -U usuario arquivo_backup.dump
```

### Restaurar Tenant Específico

```bash
python manage.py restaurar_backup --backup-file backups/tenant_123_alias_20240101_120000.sqlite3 --tenant-id 123
```

Ou com força (sobrescreve banco existente):
```bash
python manage.py restaurar_backup --backup-file backups/tenant_123_alias_20240101_120000.sqlite3 --tenant-id 123 --force
```

### Restaurar Arquivos Media

```bash
# 1. Parar servidor
# 2. Fazer backup do media atual
cp -r media media.backup

# 3. Copiar backup
cp -r backups/backup_completo_YYYYMMDD_HHMMSS/media/* media/

# 4. Ajustar permissões (Linux)
chmod -R 755 media/
chown -R www-data:www-data media/  # Ajustar usuário conforme necessário
```

---

## ⏰ Backup Automático

### Windows - Agendador de Tarefas

1. Abrir "Agendador de Tarefas"
2. Criar Tarefa Básica
3. Configurar:
   - **Nome**: Backup Diário MonPEC
   - **Gatilho**: Diariamente às 02:00
   - **Ação**: Iniciar programa
   - **Programa**: `C:\caminho\para\python.exe`
   - **Argumentos**: `manage.py backup_completo --compress`
   - **Iniciar em**: `C:\caminho\para\projeto`

### Linux - Cron

Editar crontab:
```bash
crontab -e
```

Adicionar linha (backup diário às 2h da manhã):
```cron
0 2 * * * cd /caminho/para/projeto && /usr/bin/python3 manage.py backup_completo --compress >> /var/log/monpec_backup.log 2>&1
```

Ou usar o script:
```cron
0 2 * * * /caminho/para/projeto/scripts/manutencao/BACKUP_COMPLETO.sh >> /var/log/monpec_backup.log 2>&1
```

### Usando o Script Python Direto

```bash
# Executar via cron
0 2 * * * /usr/bin/python3 /caminho/para/projeto/scripts/manutencao/backup_automatico.py
```

---

## 📁 Estrutura dos Backups

```
backups/
├── backup_completo_20240101_120000/
│   ├── db_principal_20240101_120000.sqlite3
│   ├── tenants/
│   │   ├── tenant_1_cliente1_20240101_120000.sqlite3
│   │   ├── tenant_1_cliente1_20240101_120000.sqlite3.metadata.json
│   │   ├── tenant_2_cliente2_20240101_120000.sqlite3
│   │   └── tenant_2_cliente2_20240101_120000.sqlite3.metadata.json
│   ├── media/
│   │   ├── certificados_digitais/
│   │   ├── documentos/
│   │   └── ...
│   ├── staticfiles/
│   │   └── ...
│   └── backup_metadata.json
└── backup_completo_20240101_120000.zip  # Se usado --compress
```

---

## 🔍 Verificar Backups

### Listar Backups Disponíveis
```bash
# Windows
dir backups\backup_completo_*

# Linux
ls -lh backups/backup_completo_*
```

### Verificar Tamanho dos Backups
```bash
# Windows
dir /s backups

# Linux
du -sh backups/*
```

### Verificar Conteúdo de Backup ZIP
```bash
# Windows
# Usar 7-Zip ou WinRAR

# Linux
unzip -l backups/backup_completo_YYYYMMDD_HHMMSS.zip
```

### Ver Metadados do Backup
```bash
# Windows
type backups\backup_completo_YYYYMMDD_HHMMSS\backup_metadata.json

# Linux
cat backups/backup_completo_YYYYMMDD_HHMMSS/backup_metadata.json | python -m json.tool
```

---

## 🛠️ Troubleshooting

### Erro: "Banco de dados não encontrado"
**Causa**: Caminho do banco está incorreto ou banco não existe.

**Solução**:
1. Verificar `settings.py` - `DATABASES['default']['NAME']`
2. Verificar se o arquivo existe
3. Verificar permissões de leitura

### Erro: "Permissão negada"
**Causa**: Sem permissão para escrever no diretório de backup.

**Solução**:
```bash
# Linux
chmod 755 backups/
chown usuario:grupo backups/

# Windows
# Executar como Administrador ou ajustar permissões da pasta
```

### Erro: "Espaço em disco insuficiente"
**Causa**: Disco cheio.

**Solução**:
1. Limpar backups antigos manualmente
2. Usar `--keep-days` menor
3. Usar `--compress` para economizar espaço
4. Mover backups para outro disco

### Backup muito lento
**Causa**: Muitos arquivos ou disco lento.

**Soluções**:
1. Usar `--only-db` para backup rápido apenas de bancos
2. Fazer backup de media separadamente (`--only-media`)
3. Considerar backup incremental (futuro)

### Como limpar backups antigos manualmente

```bash
# Manter apenas últimos 7 dias
python manage.py backup_completo --keep-days 7

# Ou deletar manualmente
# Windows
forfiles /p backups /m backup_completo_* /d -30 /c "cmd /c del /q @path"

# Linux
find backups/ -name "backup_completo_*" -mtime +30 -exec rm -rf {} \;
```

---

## 📊 Boas Práticas

### 1. Frequência de Backup
- **Produção**: Diário (preferencialmente à noite)
- **Desenvolvimento**: Antes de mudanças importantes
- **Antes de migrações**: Sempre fazer backup completo

### 2. Localização dos Backups
- ✅ **Recomendado**: Servidor separado ou cloud storage
- ✅ **Mínimo**: Disco diferente do servidor principal
- ❌ **Evitar**: Mesmo disco do sistema

### 3. Retenção
- **Backups diários**: Manter 30 dias
- **Backups semanais**: Manter 3 meses
- **Backups mensais**: Manter 1 ano

### 4. Teste de Restauração
- Testar restauração **pelo menos mensalmente**
- Verificar integridade dos dados após restauração
- Documentar processo de restauração

### 5. Monitoramento
- Configurar alertas se backup falhar
- Verificar logs regularmente
- Monitorar espaço em disco

---

## 🔐 Segurança

### Proteger Backups com Dados Sensíveis

```bash
# Criptografar backup (exemplo com GPG)
gpg --encrypt --recipient email@exemplo.com backup_completo_YYYYMMDD_HHMMSS.zip

# Ou usar senha
zip -P senha_segura backup_completo_YYYYMMDD_HHMMSS.zip -r backup_completo_YYYYMMDD_HHMMSS/
```

### Permissões de Arquivo
```bash
# Linux - Apenas proprietário pode ler
chmod 600 backups/backup_completo_*.zip
```

---

## 📞 Suporte

Em caso de problemas:
1. Verificar logs do Django
2. Verificar espaço em disco
3. Verificar permissões
4. Consultar este guia
5. Contatar suporte técnico

---

**Última atualização**: 2024
**Versão do sistema**: 1.0






