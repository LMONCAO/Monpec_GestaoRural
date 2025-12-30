# Solução para Problemas com Dumpdata

## Problemas Identificados

1. **Tabela não existe**: `gestao_rural_anexolancamentofinanceiro`
2. **Erro de encoding**: `'charmap' codec can't encode character '\u03b1'`
3. **Migrações não aplicadas**: O comando `migrate` indicou que não há migrações para aplicar, mas há mudanças nos modelos

## Soluções Disponíveis

### Opção 1: Script Automático (Recomendado)

Execute um dos scripts criados:

#### Windows (Batch):
```batch
RESOLVER_DUMPDATA.bat
```

#### Python (Multiplataforma):
```bash
python resolver_dumpdata.py
```

Estes scripts irão:
1. Criar migrações se necessário
2. Aplicar todas as migrações pendentes
3. Fazer o dump com encoding UTF-8 correto

### Opção 2: Comandos Manuais

#### Passo 1: Criar migrações
```bash
python manage.py makemigrations
```

#### Passo 2: Aplicar migrações
```bash
python manage.py migrate
```

#### Passo 3: Verificar status
```bash
python manage.py showmigrations gestao_rural
```

#### Passo 4: Fazer dump com UTF-8
```bash
set PYTHONIOENCODING=utf-8
python manage.py dumpdata --natural-foreign --natural-primary -o dados_backup.json
```

### Opção 3: Criar Tabela Específica

Se apenas a tabela `AnexoLancamentoFinanceiro` estiver faltando:

```bash
python criar_tabela_anexo.py
```

### Opção 4: Dump Excluindo a Tabela Problemática

Se você não precisa dos dados dessa tabela (provavelmente está vazia):

```bash
set PYTHONIOENCODING=utf-8
python manage.py dumpdata --natural-foreign --natural-primary --exclude gestao_rural.AnexoLancamentoFinanceiro -o dados_backup.json
```

## Resolver Problema de Encoding

O erro `'charmap' codec can't encode character` ocorre porque o Windows usa codificação diferente. Para resolver:

### Windows PowerShell:
```powershell
$env:PYTHONIOENCODING="utf-8"
python manage.py dumpdata --natural-foreign --natural-primary -o dados_backup.json
```

### Windows CMD:
```cmd
set PYTHONIOENCODING=utf-8
python manage.py dumpdata --natural-foreign --natural-primary -o dados_backup.json
```

## Verificação

Após executar as migrações, verifique se a tabela foi criada:

```bash
python manage.py dbshell
```

No SQLite:
```sql
.tables
```

Ou verifique diretamente:
```sql
SELECT name FROM sqlite_master WHERE type='table' AND name='gestao_rural_anexolancamentofinanceiro';
```

## Notas Importantes

1. **Backup antes de migrar**: Sempre faça backup do banco de dados antes de aplicar migrações em produção
2. **Encoding UTF-8**: Sempre configure `PYTHONIOENCODING=utf-8` ao fazer dump em Windows
3. **Migrações pendentes**: Se `makemigrations` criar novas migrações, aplique-as com `migrate` antes de fazer o dump

## Arquivos Criados

- `resolver_dumpdata.py` - Script Python completo
- `RESOLVER_DUMPDATA.bat` - Script Batch para Windows
- `criar_tabela_anexo.py` - Script para criar apenas a tabela específica
- `SOLUCAO_DUMPDATA.md` - Este documento

