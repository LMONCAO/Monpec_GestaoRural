# 🔧 Como Aplicar as Migrations 0071 e 0072 Corrigidas

## ⚠️ **IMPORTANTE: Estas migrations foram CORRIGIDAS**

As migrations 0071 e 0072 foram refeitas para evitar o erro 500 após login.

### 🔍 **O que foi corrigido:**

1. **Migration 0071**: Campo `ncm` agora permite NULL inicialmente (será tratado na 0072)
2. **Migration 0072**: Preenche valores NULL antes de tornar o campo obrigatório

---

## 📋 **Opção 1: Se as migrations AINDA NÃO FORAM aplicadas**

Se você ainda não aplicou as migrations 0071 e 0072 no servidor:

### Passo a passo:

```bash
# 1. Verificar status atual
python manage.py showmigrations gestao_rural | Select-String "007[0-4]"

# 2. Aplicar normalmente (agora estão corretas)
python manage.py migrate gestao_rural 0071
python manage.py migrate gestao_rural 0072
python manage.py migrate gestao_rural 0073
python manage.py migrate gestao_rural 0074

# 3. Continuar com as demais
python manage.py migrate
```

---

## 📋 **Opção 2: Se as migrations JÁ FORAM aplicadas (com erro)**

Se você já tentou aplicar e deu erro 500:

### Passo 1: Verificar estado atual

```bash
python manage.py showmigrations gestao_rural | Select-String "007[0-4]"
```

### Passo 2: Se 0071 e 0072 foram aplicadas (mas com erro)

Você precisa fazer rollback e reaplicar:

```bash
# 1. Fazer rollback até a 0070
python manage.py migrate gestao_rural 0070

# 2. Verificar se há produtos no banco
python manage.py shell
```

No shell do Django:
```python
from gestao_rural.models_compras_financeiro import Produto
print(f"Produtos existentes: {Produto.objects.count()}")
# Se houver produtos, anote quantos são
exit()
```

### Passo 3: Limpar tabelas se necessário (CUIDADO!)

Se houver produtos criados com a migration antiga:

```bash
python manage.py shell
```

```python
from gestao_rural.models_compras_financeiro import Produto, CategoriaProduto
from gestao_rural.models_compras_financeiro import ItemNotaFiscal

# Verificar se há produtos
if Produto.objects.exists():
    print(f"⚠️ Existem {Produto.objects.count()} produtos.")
    print("Você precisa decidir: deletar ou manter")
    # Se quiser deletar (CUIDADO!):
    # ItemNotaFiscal.objects.filter(produto__isnull=False).update(produto=None)
    # Produto.objects.all().delete()
    # CategoriaProduto.objects.all().delete()

exit()
```

### Passo 4: Fazer rollback (se necessário)

```bash
# Fazer rollback até antes da 0071
python manage.py migrate gestao_rural 0070

# Se der erro, pode precisar fazer manualmente no banco
# ou usar --fake para marcar como não aplicadas
```

### Passo 5: Reaplicar com as versões corrigidas

```bash
# Agora aplicar as versões corrigidas
python manage.py migrate gestao_rural 0071
python manage.py migrate gestao_rural 0072
python manage.py migrate gestao_rural 0073
python manage.py migrate gestao_rural 0074
python manage.py migrate
```

---

## 📋 **Opção 3: Usar --fake para substituir (MAIS SEGURO)**

Se as migrations já foram aplicadas parcialmente:

```bash
# 1. Marcar 0072 como não aplicada (fake)
python manage.py migrate gestao_rural 0071 --fake

# 2. Reverter a alteração do campo ncm no banco (se necessário)
# Isso precisa ser feito manualmente no banco de dados:
# ALTER TABLE gestao_rural_produto ALTER COLUMN ncm DROP NOT NULL;
# (Se usar PostgreSQL)

# 3. Aplicar novamente (agora com a versão corrigida)
python manage.py migrate gestao_rural 0072 --fake
python manage.py migrate gestao_rural 0072
```

---

## 🔍 **Verificação Pós-Aplicação**

Após aplicar as migrations corrigidas, verifique:

```bash
python manage.py shell
```

```python
from gestao_rural.models_compras_financeiro import Produto

# Verificar se há produtos sem NCM
produtos_sem_ncm = Produto.objects.filter(ncm__isnull=True) | Produto.objects.filter(ncm='')
print(f"Produtos sem NCM: {produtos_sem_ncm.count()}")

# Se houver, eles deveriam ter sido preenchidos com '0000.00.00'
produtos_genericos = Produto.objects.filter(ncm='0000.00.00')
print(f"Produtos com NCM genérico: {produtos_genericos.count()}")

if produtos_genericos.exists():
    print("⚠️ Lembre-se de atualizar o NCM correto desses produtos!")
    
exit()
```

---

## ✅ **Checklist Final**

- [ ] Migration 0071 aplicada corretamente
- [ ] Migration 0072 aplicada corretamente (com preenchimento de NULLs)
- [ ] Não há produtos com NCM=NULL
- [ ] Campo NCM é obrigatório no banco
- [ ] Sistema funciona após login (sem erro 500)
- [ ] Produtos com NCM genérico foram identificados

---

## 🆘 **Se ainda der erro 500**

1. Verifique os logs do servidor para ver o erro exato
2. Verifique se o campo NCM realmente não aceita NULL no banco
3. Execute a função de preenchimento manualmente:

```python
python manage.py shell

from gestao_rural.models_compras_financeiro import Produto
Produto.objects.filter(ncm__isnull=True).update(ncm='0000.00.00')
Produto.objects.filter(ncm='').update(ncm='0000.00.00')

exit()
```

Depois tente fazer login novamente.






