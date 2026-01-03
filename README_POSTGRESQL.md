# 🐘 Configuração PostgreSQL Local - Guia Rápido

## Problema Identificado

- ✅ **Migrações aplicadas no SQLite**, mas faltam tabelas no banco
- ✅ **Banco local é SQLite**, mas Google Cloud usa **PostgreSQL**
- ✅ **Incompatibilidade** entre ambientes causa erros

## Solução Implementada

### 1. ✅ Settings.py Atualizado

O `sistema_rural/settings.py` agora:
- Detecta automaticamente se PostgreSQL está configurado
- Usa PostgreSQL se `DB_NAME`, `DB_USER` e `DB_PASSWORD` estiverem no `.env.local`
- Faz fallback para SQLite se não estiver configurado

### 2. ✅ Scripts Criados

#### `configurar_postgresql_local.ps1`
- Configura PostgreSQL local automaticamente
- Cria banco de dados
- Gera arquivo `.env.local`

#### `aplicar_migracoes_postgresql.ps1`
- Aplica todas as migrações no PostgreSQL
- Verifica estado das migrações

#### `verificar_migracoes_tabelas.ps1`
- Compara modelos do código com tabelas no banco
- Identifica tabelas faltantes

#### `corrigir_migracoes_problemas.ps1`
- Corrige problemas de migrações
- Opções para fake, reset, criar novas migrações

## 🚀 Como Usar

### Passo 1: Instalar PostgreSQL

```powershell
# Via Chocolatey (recomendado)
choco install postgresql

# Ou baixar de: https://www.postgresql.org/download/windows/
```

### Passo 2: Configurar PostgreSQL

```powershell
# Execute o script de configuração
.\configurar_postgresql_local.ps1
```

O script irá:
1. Verificar se PostgreSQL está instalado
2. Solicitar credenciais
3. Criar banco de dados `monpec_db_local`
4. Gerar arquivo `.env.local`

### Passo 3: Aplicar Migrações

```powershell
# Aplicar todas as migrações
.\aplicar_migracoes_postgresql.ps1

# Ou manualmente
python manage.py migrate
```

### Passo 4: Verificar

```powershell
# Verificar estado
.\verificar_migracoes_tabelas.ps1
```

## 📋 Estrutura de Arquivos

```
Monpec_GestaoRural/
├── .env.local                    # Configurações locais (criar a partir de .env.local.example)
├── .env.local.example            # Exemplo de configuração
├── configurar_postgresql_local.ps1
├── aplicar_migracoes_postgresql.ps1
├── verificar_migracoes_tabelas.ps1
├── corrigir_migracoes_problemas.ps1
├── docs/
│   └── CONFIGURACAO_POSTGRESQL_LOCAL.md  # Documentação completa
└── sistema_rural/
    └── settings.py              # ✅ Atualizado para suportar PostgreSQL
```

## ⚠️ Importante

1. **Arquivo `.env.local`**:
   - Copie `.env.local.example` para `.env.local`
   - Preencha com suas credenciais PostgreSQL
   - **NÃO commite** `.env.local` no git (já está no .gitignore)

2. **Migrações Duplicadas**:
   - Há duas migrações `0049_*` (isso é normal, foi resolvido na `0051_merge`)
   - O Django gerencia isso automaticamente

3. **Dados Existentes**:
   - Se você tem dados no SQLite, faça backup antes:
   ```powershell
   python manage.py dumpdata > backup_dados.json
   ```

## 🔍 Verificar Problemas

### Ver migrações pendentes:
```powershell
python manage.py showmigrations | Select-String "\[ \]"
```

### Verificar tabelas faltantes:
```powershell
.\verificar_migracoes_tabelas.ps1
```

### Corrigir problemas:
```powershell
.\corrigir_migracoes_problemas.ps1
```

## 📚 Documentação Completa

Veja `docs/CONFIGURACAO_POSTGRESQL_LOCAL.md` para:
- Guia detalhado passo a passo
- Solução de problemas
- Migração de SQLite para PostgreSQL
- Boas práticas

## ✅ Checklist

- [ ] PostgreSQL instalado
- [ ] Script `configurar_postgresql_local.ps1` executado
- [ ] Arquivo `.env.local` criado e configurado
- [ ] Migrações aplicadas (`python manage.py migrate`)
- [ ] Tabelas verificadas (`.verificar_migracoes_tabelas.ps1`)
- [ ] Sistema testado localmente

## 🎯 Próximos Passos

Após configurar PostgreSQL local:

1. ✅ Todas as migrações aplicadas
2. ✅ Todas as tabelas criadas
3. ✅ Sistema funcionando localmente
4. ✅ Compatível com Google Cloud (mesmo banco)
5. ✅ Pronto para deploy sem erros de migração

## 💡 Dicas

- Use PostgreSQL local para desenvolvimento
- Mantenha `.env.local` atualizado
- Faça backup antes de mudanças grandes
- Verifique migrações antes de cada deploy

---

**Criado em**: 2025-01-XX  
**Última atualização**: 2025-01-XX

