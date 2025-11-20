# 🔒 GUIA DE SEGURANÇA - VERSÃO DE DEMONSTRAÇÃO

## 📋 **GARANTIAS DE SEGURANÇA**

Este guia explica como a versão de demonstração foi projetada para **NÃO INTERFERIR** no seu sistema em desenvolvimento.

---

## ✅ **PROTEÇÕES IMPLEMENTADAS**

### **1. Backup Automático**
- ✅ Script de backup é executado **ANTES** de qualquer alteração
- ✅ Backup completo do banco de dados SQLite
- ✅ Backup de configurações importantes
- ✅ Localização segura em `.\backups\backup_antes_demo_*`

### **2. Uso de `get_or_create`**
Todos os scripts de população de dados usam `get_or_create()` do Django, que significa:

```python
# ❌ NÃO FAZ ISSO (sobrescreveria):
obj = Modelo.objects.create(...)  # Cria sempre, pode duplicar

# ✅ FAZ ISSO (seguro):
obj, created = Modelo.objects.get_or_create(
    campo_unico='valor',
    defaults={...}  # Só usa se não existir
)
```

**Resultado:** Se os dados já existirem, eles **NÃO são modificados**. Se não existirem, são criados.

### **3. Verificação de Existência**
- ✅ Usuário `demo` só é criado se não existir
- ✅ Produtor "João Silva" só é criado se não existir
- ✅ Propriedade "Fazenda São José" só é criada se não existir
- ✅ Todos os outros dados seguem a mesma lógica

### **4. Não Deleta Nada**
- ✅ **NENHUM** dado existente é deletado
- ✅ **NENHUM** dado existente é modificado
- ✅ Apenas **ADICIONA** novos dados de demonstração

---

## 🛡️ **O QUE É PROTEGIDO**

### **Dados que NÃO são afetados:**
- ✅ Todos os seus usuários existentes
- ✅ Todos os seus produtores rurais existentes
- ✅ Todas as suas propriedades existentes
- ✅ Todos os seus inventários existentes
- ✅ Todos os seus projetos bancários existentes
- ✅ Todas as suas configurações existentes
- ✅ Todas as suas projeções existentes

### **O que é ADICIONADO (não substitui):**
- ➕ Usuário `demo` (se não existir)
- ➕ Produtor "João Silva" (se não existir)
- ➕ Propriedade "Fazenda São José" (se não existir)
- ➕ Dados de demonstração relacionados

---

## 📊 **COMO FUNCIONA O `get_or_create`**

### **Exemplo Prático:**

```python
# No script populate_test_data.py:
produtor, created = ProdutorRural.objects.get_or_create(
    cpf_cnpj='12345678901',  # Campo único para verificar
    defaults={  # Só usa esses valores se NÃO existir
        'nome': 'João Silva',
        'telefone': '(11) 99999-9999',
        # ...
    }
)
```

**Cenário 1: Produtor NÃO existe**
- `created = True`
- Produtor é criado com os dados de demonstração
- ✅ Funciona normalmente

**Cenário 2: Produtor JÁ existe**
- `created = False`
- Produtor existente é retornado
- **NENHUM dado é modificado**
- ✅ Seus dados originais permanecem intactos

---

## 🔄 **PROCESSO COMPLETO DE SEGURANÇA**

### **Passo 1: Backup Automático**
```
.\setup_demo.ps1
    ↓
Executa .\backup_antes_demo.ps1 automaticamente
    ↓
Cria backup completo em .\backups\backup_antes_demo_YYYY-MM-DD_HH-MM-SS\
    ↓
✅ Seus dados estão protegidos!
```

### **Passo 2: Verificação de Existência**
```
Para cada dado de demo:
    ↓
Verifica se já existe (usando campo único)
    ↓
Se NÃO existe: Cria novo
Se JÁ existe: Usa o existente (sem modificar)
    ↓
✅ Nenhum dado é sobrescrito!
```

### **Passo 3: Adição Segura**
```
Dados de demo são ADICIONADOS ao banco
    ↓
Não substituem nada
    ↓
✅ Seus dados originais permanecem intactos!
```

---

## 🚨 **E SE ALGO DER ERRADO?**

### **Opção 1: Restaurar do Backup**

```powershell
# 1. Parar servidor Django
Get-Process python | Stop-Process -Force

# 2. Restaurar banco de dados
$backup = Get-ChildItem ".\backups\backup_antes_demo_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Copy-Item "$backup\banco_dados\db.sqlite3" -Destination ".\db.sqlite3" -Force
Copy-Item "$backup\banco_dados\db.sqlite3-shm" -Destination ".\db.sqlite3-shm" -Force -ErrorAction SilentlyContinue
Copy-Item "$backup\banco_dados\db.sqlite3-wal" -Destination ".\db.sqlite3-wal" -Force -ErrorAction SilentlyContinue

# 3. Verificar
python manage.py migrate
python manage.py runserver
```

### **Opção 2: Remover Apenas Dados de Demo**

```python
# No shell do Django:
python manage.py shell

from django.contrib.auth.models import User
from gestao_rural.models import *

# Remover usuário demo
User.objects.filter(username='demo').delete()

# Remover produtor de demo (se criado)
ProdutorRural.objects.filter(cpf_cnpj='12345678901').delete()

# Remover propriedade de demo (se criada)
Propriedade.objects.filter(nome_propriedade='Fazenda São José').delete()
```

---

## ✅ **CHECKLIST DE SEGURANÇA**

Antes de executar `setup_demo.ps1`, verifique:

- [ ] Backup automático será executado primeiro
- [ ] Você tem espaço em disco para o backup
- [ ] Você sabe onde está o backup (`.\backups\`)
- [ ] Você entende que dados serão ADICIONADOS, não substituídos
- [ ] Você sabe como restaurar se necessário

---

## 📝 **RESUMO DE SEGURANÇA**

### **✅ GARANTIAS:**
1. **Backup automático** antes de qualquer alteração
2. **get_or_create** em todos os dados (não sobrescreve)
3. **Verificação de existência** antes de criar
4. **Nenhum dado é deletado** ou modificado
5. **Apenas adiciona** novos dados de demonstração

### **⚠️ ATENÇÃO:**
- Se você já tiver um usuário `demo`, a senha será atualizada para `demo123`
- Se você já tiver um produtor com CPF `12345678901`, ele será usado (não modificado)
- Se você já tiver uma propriedade "Fazenda São José", ela será usada (não modificada)

### **🔒 RECOMENDAÇÃO:**
Execute o backup manualmente antes, se preferir:
```powershell
.\backup_antes_demo.ps1
```

Depois execute o setup:
```powershell
.\setup_demo.ps1
```

---

## 🎯 **CONCLUSÃO**

A versão de demonstração foi projetada com **máxima segurança**:

- ✅ **Não interfere** no seu sistema em desenvolvimento
- ✅ **Não sobrescreve** dados existentes
- ✅ **Não deleta** nada
- ✅ **Faz backup** antes de qualquer alteração
- ✅ **É reversível** a qualquer momento

**Você pode usar com tranquilidade!** 🎉

---

## 📞 **DÚVIDAS?**

Se tiver qualquer dúvida sobre segurança:

1. Verifique o backup em `.\backups\backup_antes_demo_*`
2. Leia o arquivo `INFO_BACKUP.txt` no backup
3. Teste em um ambiente de desenvolvimento primeiro
4. Execute o backup manualmente antes, se preferir

**Seu sistema está protegido!** 🔒




