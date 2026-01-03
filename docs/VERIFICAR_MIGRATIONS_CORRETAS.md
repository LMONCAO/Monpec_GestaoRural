# ✅ Verificação das Migrations 0071 e 0072 Corrigidas

## 📋 **Checklist de Verificação**

Execute os seguintes comandos no diretório do projeto (onde está o `manage.py`):

### 1️⃣ **Verificar Status das Migrations**

```bash
python manage.py showmigrations gestao_rural | findstr "007"
```

**Resultado esperado:**
- Se **NÃO aplicadas**: Verá `[ ]` (vazio) antes dos números
- Se **JÁ aplicadas**: Verá `[X]` (marcado) antes dos números

---

### 2️⃣ **Verificar Estrutura das Migrations Corrigidas**

✅ **Migration 0071 está correta se:**
- Campo `ncm` tem `blank=True, null=True` (permite NULL inicialmente)
- Linha 40 do arquivo tem: `('ncm', models.CharField(blank=True, ..., null=True, ...))`

✅ **Migration 0072 está correta se:**
- Tem função `preencher_ncm_vazio()` antes do `AlterField`
- O `AlterField` do NCM vem DEPOIS do `RunPython`
- Campo NCM tem `blank=False, null=False` no `AlterField`

---

### 3️⃣ **Verificar Banco de Dados (se já aplicadas)**

```bash
python manage.py shell
```

No shell Python:
```python
from django.db import connection
cursor = connection.cursor()

# Verificar se tabela existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gestao_rural_produto'")
if cursor.fetchone():
    print("✅ Tabela gestao_rural_produto existe")
    
    # Verificar estrutura do campo NCM
    cursor.execute("PRAGMA table_info(gestao_rural_produto)")
    cols = cursor.fetchall()
    for col in cols:
        if 'ncm' in col[1].lower():
            permite_null = col[3]  # 0 = NOT NULL, 1 = NULL permitido
            if permite_null == 0:
                print("✅ Campo NCM é NOT NULL (obrigatório)")
            else:
                print("⚠️ Campo NCM permite NULL (pode causar erro)")
else:
    print("❌ Tabela gestao_rural_produto NÃO existe (migration não aplicada)")

exit()
```

---

### 4️⃣ **Verificar Modelo Python**

```bash
python manage.py shell
```

```python
from gestao_rural.models_compras_financeiro import Produto

# Verificar campo NCM no modelo
campo_ncm = Produto._meta.get_field('ncm')
print(f"Campo NCM - null: {campo_ncm.null}, blank: {campo_ncm.blank}")

if campo_ncm.null:
    print("⚠️ PROBLEMA: Campo NCM permite NULL no modelo Python")
    print("   Mas deveria ser obrigatório após migration 0072")
else:
    print("✅ Campo NCM é obrigatório no modelo Python")

# Verificar produtos existentes
produtos_count = Produto.objects.count()
print(f"\nProdutos no banco: {produtos_count}")

if produtos_count > 0:
    produtos_sem_ncm = Produto.objects.filter(ncm__isnull=True) | Produto.objects.filter(ncm='')
    count_sem_ncm = produtos_sem_ncm.count()
    
    if count_sem_ncm > 0:
        print(f"⚠️ {count_sem_ncm} produto(s) sem NCM encontrado(s)")
        print("   Execute: Produto.objects.filter(ncm__isnull=True).update(ncm='0000.00.00')")
    else:
        print("✅ Todos os produtos têm NCM")

exit()
```

---

## 🎯 **Interpretação dos Resultados**

### ✅ **Cenário 1: Migrations NÃO aplicadas ainda**
```
[ ] 0071_adicionar_produtos_cadastro_fiscal
[ ] 0072_adicionar_campos_obrigatorios_nfe_produto
```

**Ação:** Aplicar normalmente (estão corretas):
```bash
python manage.py migrate gestao_rural 0071
python manage.py migrate gestao_rural 0072
python manage.py migrate gestao_rural 0073
python manage.py migrate gestao_rural 0074
```

---

### ✅ **Cenário 2: Migrations já aplicadas CORRETAMENTE**
```
[X] 0071_adicionar_produtos_cadastro_fiscal
[X] 0072_adicionar_campos_obrigatorios_nfe_produto
```

E:
- Campo NCM no banco é `NOT NULL` ✅
- Campo NCM no modelo Python é `null=False` ✅
- Não há produtos com `ncm=NULL` ✅

**Ação:** Nada a fazer, está tudo correto! ✅

---

### ⚠️ **Cenário 3: Migrations aplicadas MAS com problema**
```
[X] 0071_adicionar_produtos_cadastro_fiscal
[X] 0072_adicionar_campos_obrigatorios_nfe_produto
```

Mas:
- Campo NCM no banco permite `NULL` ⚠️
- OU há produtos com `ncm=NULL` ⚠️
- OU campo no modelo Python permite `null=True` ⚠️

**Ação:** Precisa corrigir (veja próximo passo)

---

## 🔧 **Se Precisa Corrigir**

### Opção A: Rollback e Reaplicar (Recomendado)

```bash
# 1. Rollback até antes da 0071
python manage.py migrate gestao_rural 0070

# 2. Se houver produtos, decidir:
#    - Deletar: python manage.py shell (veja código acima)
#    - OU manter (será tratado na 0072 corrigida)

# 3. Reaplicar com versões corrigidas
python manage.py migrate gestao_rural 0071
python manage.py migrate gestao_rural 0072
python manage.py migrate gestao_rural 0073
python manage.py migrate gestao_rural 0074
```

### Opção B: Corrigir Manualmente (Mais rápido)

Se já aplicadas mas campo permite NULL:

```python
python manage.py shell

from gestao_rural.models_compras_financeiro import Produto
from django.db import connection

# 1. Preencher produtos sem NCM
Produto.objects.filter(ncm__isnull=True).update(ncm='0000.00.00')
Produto.objects.filter(ncm='').update(ncm='0000.00.00')

# 2. Tornar campo NOT NULL no banco (SQLite)
cursor = connection.cursor()
# Nota: SQLite não suporta ALTER COLUMN diretamente
# Você precisaria recriar a tabela ou usar uma migration adicional

exit()
```

---

## 📊 **Resumo de Verificação**

| Item | Como Verificar | Resultado Esperado |
|------|---------------|-------------------|
| Migration 0071 aplicada | `showmigrations` | `[X]` |
| Migration 0072 aplicada | `showmigrations` | `[X]` |
| Campo NCM no banco | `PRAGMA table_info` | `NOT NULL` |
| Campo NCM no modelo | `Produto._meta.get_field('ncm').null` | `False` |
| Produtos sem NCM | `Produto.objects.filter(ncm__isnull=True)` | `0` |
| Tabela existe | `SELECT name FROM sqlite_master` | `gestao_rural_produto` |

---

## ✅ **Conclusão**

Se todos os itens acima estão corretos, **está tudo OK!** ✅

As migrations 0071 e 0072 corrigidas estão prontas e não devem mais causar erro 500.






