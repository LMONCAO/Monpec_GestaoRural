# Guia Rápido - Resolver Problema com Dumpdata

## Problema
```
CommandError: Unable to serialize database: no such table: gestao_rural_anexolancamentofinanceiro
```

## Solução Rápida (Recomendada)

Execute na ordem:

### 1. Forçar Migração 0034
```batch
FORCAR_MIGRACAO_0034.bat
```

OU

```bash
python forcar_migracao_0034.py
```

### 2. Se ainda não funcionar, aplicar todas as migrações
```bash
python aplicar_todas_migracoes.py
```

### 3. Fazer o dump
```batch
set PYTHONIOENCODING=utf-8
python manage.py dumpdata --natural-foreign --natural-primary -o dados_backup.json
```

## Solução Automática Completa

Execute o script atualizado que faz tudo automaticamente:

```batch
RESOLVER_DUMPDATA.bat
```

Este script agora:
1. Cria migrações se necessário
2. Aplica todas as migrações
3. **Força a migração 0034 especificamente**
4. Verifica se a tabela foi criada
5. Faz o dump com encoding UTF-8

## Solução Alternativa (Se não precisar dos dados da tabela)

Se você não precisa dos dados de `AnexoLancamentoFinanceiro` (provavelmente está vazia):

```batch
set PYTHONIOENCODING=utf-8
python manage.py dumpdata --natural-foreign --natural-primary --exclude gestao_rural.AnexoLancamentoFinanceiro -o dados_backup.json
```

## Arquivos Disponíveis

1. **FORCAR_MIGRACAO_0034.bat** / **forcar_migracao_0034.py**
   - Força a criação da tabela `gestao_rural_anexolancamentofinanceiro`
   - Cria manualmente se a migração falhar

2. **aplicar_todas_migracoes.py**
   - Aplica todas as migrações de forma robusta
   - Verifica se a tabela foi criada

3. **RESOLVER_DUMPDATA.bat** (ATUALIZADO)
   - Script completo que faz tudo automaticamente
   - Agora inclui verificação e forçar migração 0034

## Verificação Manual

Para verificar se a tabela foi criada:

```bash
python manage.py dbshell
```

No SQLite:
```sql
.tables
SELECT name FROM sqlite_master WHERE type='table' AND name='gestao_rural_anexolancamentofinanceiro';
```

## Ordem de Execução Recomendada

1. **Primeiro**: Execute `FORCAR_MIGRACAO_0034.bat`
2. **Se falhar**: Execute `python aplicar_todas_migracoes.py`
3. **Depois**: Execute `RESOLVER_DUMPDATA.bat` para fazer o dump

OU simplesmente execute `RESOLVER_DUMPDATA.bat` que agora faz tudo automaticamente!

