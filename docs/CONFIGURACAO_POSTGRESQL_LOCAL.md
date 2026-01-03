# Configuração PostgreSQL Local

Este guia explica como configurar PostgreSQL localmente para desenvolvimento, mantendo compatibilidade com o Google Cloud.

## Por que PostgreSQL Local?

- **Compatibilidade**: O Google Cloud usa PostgreSQL, então usar o mesmo banco localmente evita problemas de compatibilidade
- **Testes Realistas**: Testar com o mesmo tipo de banco que será usado em produção
- **Migrações**: Garantir que todas as migrações funcionem corretamente antes do deploy

## Pré-requisitos

1. **PostgreSQL instalado** no Windows
   - Download: https://www.postgresql.org/download/windows/
   - Ou via Chocolatey: `choco install postgresql`

2. **Python e Django** já configurados no projeto

3. **psycopg2-binary** instalado (já está no requirements.txt)

## Instalação Rápida

### Opção 1: Script Automático (Recomendado)

```powershell
# Execute o script de configuração
.\configurar_postgresql_local.ps1
```

O script irá:
- Verificar se PostgreSQL está instalado
- Criar o banco de dados
- Configurar o arquivo `.env.local`

### Opção 2: Manual

1. **Instalar PostgreSQL** (se ainda não tiver)

2. **Criar banco de dados**:
```sql
CREATE DATABASE monpec_db_local;
```

3. **Criar arquivo `.env.local`** na raiz do projeto:
```env
DEBUG=True
SECRET_KEY=django-insecure-dev-local-2025-temp-key

DB_NAME=monpec_db_local
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui
DB_HOST=localhost
DB_PORT=5432
```

4. **Aplicar migrações**:
```powershell
python manage.py migrate
```

## Aplicar Migrações

Após configurar o PostgreSQL, execute:

```powershell
# Script automático
.\aplicar_migracoes_postgresql.ps1

# Ou manualmente
python manage.py migrate
```

## Verificar Estado das Migrações

```powershell
# Ver todas as migrações
python manage.py showmigrations

# Ver apenas pendentes
python manage.py showmigrations | Select-String "\[ \]"
```

## Estrutura de Arquivos

```
Monpec_GestaoRural/
├── .env.local              # Configurações locais (NÃO commitar no git)
├── .env_gcp                # Configurações Google Cloud
├── .env_producao            # Configurações produção
├── configurar_postgresql_local.ps1
├── aplicar_migracoes_postgresql.ps1
└── sistema_rural/
    └── settings.py          # Detecta PostgreSQL automaticamente
```

## Como Funciona

O `settings.py` foi configurado para:

1. **Ler variáveis de ambiente** do arquivo `.env.local` (via python-decouple)
2. **Detectar PostgreSQL**: Se `DB_NAME`, `DB_USER` e `DB_PASSWORD` estiverem configurados, usa PostgreSQL
3. **Fallback para SQLite**: Se as variáveis não estiverem configuradas, usa SQLite para desenvolvimento rápido

## Solução de Problemas

### Erro: "psql não é reconhecido"

**Solução**: Adicione PostgreSQL ao PATH do sistema:
1. Encontre o diretório de instalação (geralmente `C:\Program Files\PostgreSQL\XX\bin`)
2. Adicione ao PATH do sistema

### Erro: "password authentication failed"

**Solução**: Verifique a senha do usuário PostgreSQL no arquivo `.env.local`

### Erro: "database does not exist"

**Solução**: Crie o banco de dados:
```sql
CREATE DATABASE monpec_db_local;
```

### Erro: "relation does not exist"

**Solução**: As migrações não foram aplicadas. Execute:
```powershell
python manage.py migrate
```

### Migrações com conflitos

Se houver migrações duplicadas ou conflitantes:

```powershell
# Ver migrações aplicadas
python manage.py showmigrations

# Fake uma migração específica (se necessário)
python manage.py migrate --fake gestao_rural 0090

# Aplicar todas as migrações
python manage.py migrate
```

## Migração de SQLite para PostgreSQL

Se você já tem dados no SQLite e quer migrar para PostgreSQL:

1. **Fazer backup do SQLite**:
```powershell
Copy-Item db.sqlite3 db.sqlite3.backup
```

2. **Configurar PostgreSQL** (seguir passos acima)

3. **Aplicar migrações no PostgreSQL**:
```powershell
python manage.py migrate
```

4. **Exportar dados do SQLite** (se necessário):
```powershell
python manage.py dumpdata > dados_backup.json
```

5. **Importar no PostgreSQL**:
```powershell
python manage.py loaddata dados_backup.json
```

**Nota**: Alguns tipos de dados podem precisar de ajustes entre SQLite e PostgreSQL.

## Variáveis de Ambiente

O sistema prioriza as variáveis nesta ordem:

1. **Variáveis de ambiente do sistema** (mais alta prioridade)
2. **Arquivo `.env.local`** (desenvolvimento local)
3. **SQLite** (fallback se nada estiver configurado)

## Segurança

⚠️ **IMPORTANTE**: 
- O arquivo `.env.local` contém senhas e não deve ser commitado no git
- Adicione `.env.local` ao `.gitignore`
- Use variáveis de ambiente do sistema em produção

## Próximos Passos

Após configurar PostgreSQL local:

1. ✅ Aplicar todas as migrações
2. ✅ Verificar se todas as tabelas foram criadas
3. ✅ Testar o sistema localmente
4. ✅ Fazer deploy para Google Cloud (já está configurado)

## Suporte

Se encontrar problemas:
1. Verifique os logs do PostgreSQL
2. Verifique o arquivo `.env.local`
3. Execute `python manage.py check` para verificar configurações
4. Consulte a documentação do Django sobre PostgreSQL

