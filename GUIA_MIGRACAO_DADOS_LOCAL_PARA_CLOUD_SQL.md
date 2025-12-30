# 📊 GUIA COMPLETO: MIGRAÇÃO DE DADOS DO LOCALHOST PARA O CLOUD SQL

## 🎯 SITUAÇÃO ATUAL

- **Banco Local**: SQLite (`db.sqlite3`)
- **Banco Cloud SQL**: PostgreSQL (`monpec-db`)
- **Problema**: SQLite não pode ser restaurado diretamente no PostgreSQL (formato diferente)

---

## ✅ OPÇÕES DISPONÍVEIS PARA MIGRAR SEUS DADOS

Você tem **3 opções principais** para migrar seus dados:

### **OPÇÃO 1: Converter SQLite para PostgreSQL (RECOMENDADO para muitos dados)**

Esta é a melhor opção se você já tem muitos dados cadastrados (proprietários, propriedades, animais, etc.).

#### Passo 1: Exportar dados do SQLite para formato compatível

No seu computador local, dentro da pasta do projeto:

```bash
# Ativar ambiente virtual (se estiver usando)
# .\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Exportar dados usando Django dumpdata
python manage.py dumpdata --natural-foreign --natural-primary -o dados_local.json

# OU exportar apenas apps específicos (mais seguro)
python manage.py dumpdata gestao_rural --natural-foreign --natural-primary -o dados_gestao_rural.json
python manage.py dumpdata auth.user --natural-foreign --natural-primary -o dados_usuarios.json
```

#### Passo 2: Fazer upload do arquivo JSON para o Cloud Shell

1. No Cloud Shell, use a opção de **Upload** (ícone de upload na barra superior)
2. Faça upload do arquivo `dados_local.json` ou `dados_gestao_rural.json`
3. Mova o arquivo para a pasta do projeto:
   ```bash
   mv dados_local.json ~/Monpec_GestaoRural/
   ```

#### Passo 3: Importar dados no Cloud SQL

No Cloud Shell, após o deploy estar completo:

```bash
cd ~/Monpec_GestaoRural

# Conectar ao Cloud SQL e executar migrações primeiro
gcloud sql connect monpec-db --user=monpec_user --quiet

# Dentro do psql, garantir que as tabelas existem
# (sair do psql pressionando \q)

# Agora importar os dados usando Django loaddata
python3 manage.py loaddata dados_local.json

# OU se exportou separado:
python3 manage.py loaddata dados_usuarios.json
python3 manage.py loaddata dados_gestao_rural.json
```

⚠️ **ATENÇÃO**: Se houver conflitos de chaves primárias (IDs duplicados), você pode precisar ajustar o arquivo JSON ou usar `--ignorenonexistent`.

---

### **OPÇÃO 2: Usar Scripts Django de Popular Dados (Para dados iniciais ou de teste)**

Se você tem apenas dados de configuração inicial ou quer popular com dados de exemplo, use os comandos Django disponíveis:

#### Carregar Categorias de Animais (Dados Padrão)

```bash
cd ~/Monpec_GestaoRural

# Carregar categorias padrão
python3 manage.py loaddata categorias_animais.json

# OU usar o comando customizado
python3 manage.py carregar_categorias
```

#### Popular Dados de Teste/Exemplo

```bash
cd ~/Monpec_GestaoRural

# Criar dados de exemplo básicos
python3 manage.py criar_dados_exemplo --usuario=admin

# OU popular dados mais completos
python3 manage.py populate_data

# OU popular dados completos para planejamento
python3 manage.py seed_planejamento --usuario=admin --ano=2025
```

---

### **OPÇÃO 3: Migração Manual via Django Admin (Para poucos dados)**

Se você tem poucos registros (menos de 50), a forma mais segura é recriar manualmente:

1. Acesse o sistema no Cloud Run: `https://SEU-URL.run.app/admin`
2. Faça login com usuário admin
3. Recrie manualmente:
   - Proprietários Rurais
   - Propriedades
   - Animais
   - Outros registros

---

## 🔧 PROCEDIMENTO RECOMENDADO PASSO A PASSO

### **Antes do Deploy:**

1. **Exportar dados do SQLite local:**
   ```bash
   # No seu computador local
   python manage.py dumpdata --natural-foreign --natural-primary -o dados_backup.json
   ```

2. **Verificar o arquivo gerado:**
   - O arquivo `dados_backup.json` deve estar na raiz do projeto
   - Verifique o tamanho: se for muito grande (>100MB), considere exportar apenas apps específicos

### **Durante/Depois do Deploy:**

3. **Fazer upload do arquivo JSON para o Cloud Shell:**
   - Use a interface de upload do Cloud Shell
   - Ou use `gcloud storage cp` se o arquivo for muito grande

4. **Conectar ao Cloud SQL e preparar o banco:**
   ```bash
   cd ~/Monpec_GestaoRural
   
   # Executar migrações (se ainda não foi feito)
   python3 manage.py migrate
   
   # Criar superusuário (se necessário)
   python3 manage.py createsuperuser
   ```

5. **Importar os dados:**
   ```bash
   # Importar dados do backup
   python3 manage.py loaddata dados_backup.json
   
   # Se houver erros de chaves duplicadas, use:
   python3 manage.py loaddata dados_backup.json --ignorenonexistent
   ```

6. **Carregar categorias padrão (se necessário):**
   ```bash
   python3 manage.py carregar_categorias
   ```

---

## 🔍 VERIFICAR DADOS MIGRADOS

Após importar os dados, verifique se tudo foi migrado corretamente:

```bash
# Conectar ao banco via Django shell
python3 manage.py shell

# Dentro do shell Python:
from gestao_rural.models import ProdutorRural, Propriedade
from django.contrib.auth.models import User

# Verificar usuários
print(f"Usuários: {User.objects.count()}")
print(f"Proprietários: {ProdutorRural.objects.count()}")
print(f"Propriedades: {Propriedade.objects.count()}")
```

Ou acesse o sistema web e verifique:
- ✅ Proprietários aparecem na lista
- ✅ Propriedades aparecem na lista
- ✅ Usuários conseguem fazer login
- ✅ Dados históricos estão visíveis

---

## ⚠️ PROBLEMAS COMUNS E SOLUÇÕES

### **Erro: "IntegrityError: duplicate key value"**

**Causa**: IDs duplicados ou chaves primárias conflitantes.

**Solução**:
```bash
# Limpar dados existentes antes de importar (CUIDADO!)
python3 manage.py shell
# Dentro do shell:
from gestao_rural.models import *
from django.contrib.auth.models import User
User.objects.all().delete()  # CUIDADO: Remove todos os usuários!
ProdutorRural.objects.all().delete()  # Remove todos os produtores!

# OU usar --ignorenonexistent
python3 manage.py loaddata dados_backup.json --ignorenonexistent
```

### **Erro: "No such table"**

**Causa**: Migrações não foram executadas.

**Solução**:
```bash
python3 manage.py migrate
```

### **Erro: "Permission denied" ao conectar ao Cloud SQL**

**Causa**: Permissões não configuradas ou usuário incorreto.

**Solução**:
```bash
# Verificar usuário e senha
gcloud sql users list --instance=monpec-db

# Recriar usuário se necessário (no script de deploy)
```

### **Arquivo JSON muito grande (>100MB)**

**Solução**: Exportar por app específico:
```bash
# Exportar apenas gestao_rural
python3 manage.py dumpdata gestao_rural --natural-foreign --natural-primary -o dados_gestao.json

# Exportar apenas auth
python3 manage.py dumpdata auth --natural-foreign --natural-primary -o dados_auth.json
```

---

## 📝 NOTAS IMPORTANTES

1. **Senhas de Usuários**: O `dumpdata` NÃO exporta senhas em texto plano, mas sim hashes. Se você usar `--natural-foreign`, os usuários serão mantidos. Se criar novos usuários, precisará redefinir as senhas.

2. **IDs Auto-incrementais**: Se houver conflitos de IDs, considere usar `--natural-primary` no dumpdata (já incluído nos comandos acima).

3. **Relacionamentos**: O `--natural-foreign` garante que relacionamentos sejam mantidos corretamente.

4. **Backup**: Sempre faça backup do Cloud SQL antes de importar dados:
   ```bash
   gcloud sql backups create --instance=monpec-db
   ```

---

## ✅ CHECKLIST DE MIGRAÇÃO

- [ ] Dados exportados do SQLite local (`dumpdata`)
- [ ] Arquivo JSON criado e verificado
- [ ] Upload do arquivo para o Cloud Shell realizado
- [ ] Migrações executadas no Cloud SQL (`migrate`)
- [ ] Superusuário criado (se necessário)
- [ ] Dados importados com sucesso (`loaddata`)
- [ ] Categorias padrão carregadas (`carregar_categorias`)
- [ ] Verificação dos dados no sistema web
- [ ] Login testado com usuários existentes
- [ ] Backup do Cloud SQL criado

---

## 🆘 PRECISA DE AJUDA?

Se encontrar problemas:

1. Verifique os logs do Cloud Run:
   ```bash
   gcloud run services logs read monpec --limit=50
   ```

2. Verifique conexão com o banco:
   ```bash
   gcloud sql connect monpec-db --user=monpec_user
   ```

3. Verifique se as migrações estão atualizadas:
   ```bash
   python3 manage.py showmigrations
   ```

---

**Última atualização**: Janeiro 2025  
**Versão**: 1.0

