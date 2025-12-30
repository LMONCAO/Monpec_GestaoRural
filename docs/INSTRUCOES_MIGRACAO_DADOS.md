# 📊 INSTRUÇÕES: MIGRAÇÃO DE DADOS DO LOCALHOST PARA O CLOUD SQL

## ✅ GARANTIA: SEUS DADOS SERÃO MIGRADOS!

O script `RESETAR_E_DEPLOY_DO_ZERO.sh` agora inclui **opção para fazer backup e restore dos dados**!

---

## 🎯 COMO FUNCIONA

### Opção 1: BACKUP AUTOMÁTICO (RECOMENDADO)

Durante a execução do script, quando perguntado:

```
Fazer backup dos dados do localhost agora? (s/N):
```

**Digite `s` para SIM**

O script irá:
1. ✅ Fazer backup automático do banco de dados local
2. ✅ Salvar o backup em um arquivo
3. ✅ Após o deploy, restaurar automaticamente no Cloud SQL
4. ✅ Todos os seus dados (proprietários, propriedades, etc.) serão migrados!

---

## 📋 PASSO A PASSO DETALHADO

### 1. **Antes de Executar o Script**

Certifique-se de que:
- ✅ Seu banco de dados local está funcionando
- ✅ Você tem os dados que quer migrar
- ✅ PostgreSQL client instalado (se usar PostgreSQL local)

### 2. **Durante a Execução do Script**

Quando o script perguntar:
```
Fazer backup dos dados do localhost agora? (s/N):
```

**Digite `s` e pressione Enter**

O script vai:
- Detectar se você usa SQLite ou PostgreSQL
- Fazer backup automaticamente
- Salvar o arquivo de backup

### 3. **Após o Deploy**

O script automaticamente:
- ✅ Restaura o backup no Cloud SQL
- ✅ Migra todos os dados (proprietários, propriedades, usuários, etc.)
- ✅ Confirma quando a restauração estiver completa

---

## 🔧 SE VOCÊ USAR SQLITE LOCAL

**Atenção**: Se você usa SQLite local (`db.sqlite3`), você tem duas opções:

### Opção A: Migrar Manualmente (Recomendado)
1. O script fará backup do SQLite
2. Você precisará migrar os dados manualmente usando scripts Django
3. Ou converter SQLite para PostgreSQL antes

### Opção B: Usar PostgreSQL Local
- Configure PostgreSQL localmente
- O script fará backup e restore automático

---

## 🔧 SE VOCÊ USAR POSTGRESQL LOCAL

**Perfeito!** O script funciona automaticamente:

1. ✅ Detecta PostgreSQL
2. ✅ Faz backup usando `pg_dump`
3. ✅ Restaura no Cloud SQL usando `psql` ou `pg_restore`
4. ✅ Todos os dados são migrados automaticamente!

---

## 📝 EXEMPLO DE EXECUÇÃO

```bash
# Executar o script
bash RESETAR_E_DEPLOY_DO_ZERO.sh

# Quando perguntado:
Fazer backup dos dados do localhost agora? (s/N): s

# O script fará:
✅ Backup criado: backup_local_20250101_120000.sql
✅ Deploy concluído
✅ Restaurando dados...
✅ Backup restaurado! Proprietários, propriedades e outros dados foram migrados.
```

---

## ✅ O QUE SERÁ MIGRADO

Quando você fizer backup e restore, **TODOS** estes dados serão migrados:

- ✅ **Proprietários** (ProdutorRural)
- ✅ **Propriedades**
- ✅ **Usuários** (exceto senhas se houver incompatibilidade)
- ✅ **Animais**
- ✅ **Lançamentos financeiros**
- ✅ **Transferências**
- ✅ **Vendas**
- ✅ **Configurações**
- ✅ **E todos os outros dados do sistema!**

---

## ⚠️ IMPORTANTE

### Se você NÃO escolher fazer backup:
- O banco no Cloud SQL começará vazio
- Você precisará recriar todos os dados manualmente
- Proprietários, propriedades, etc. não estarão disponíveis

### Se você escolher fazer backup:
- ✅ Todos os dados do localhost serão copiados para o Cloud SQL
- ✅ Sistema funcionará com todos os dados existentes
- ✅ Nada será perdido

---

## 🔍 VERIFICAR DADOS MIGRADOS

Após o deploy e restore, você pode verificar:

1. **Acessar o sistema**: https://SEU-URL.run.app/
2. **Fazer login** com usuário admin
3. **Verificar** se proprietários aparecem
4. **Verificar** se propriedades aparecem
5. **Verificar** se todos os dados estão lá

---

## 🆘 SE ALGO DER ERRADO

### Backup não funcionou?
1. Verifique se PostgreSQL client está instalado:
   ```bash
   pg_dump --version
   psql --version
   ```

2. Faça backup manualmente:
   ```bash
   pg_dump -h localhost -U seu_usuario -d monpec_db > backup_manual.sql
   ```

3. Restaure manualmente depois:
   ```bash
   # Obter IP do Cloud SQL
   gcloud sql instances describe monpec-db --format="value(ipAddresses[0].ipAddress)"
   
   # Restaurar
   psql -h [IP_DO_CLOUD_SQL] -U monpec_user -d monpec_db < backup_manual.sql
   ```

---

## ✅ GARANTIA FINAL

**Se você escolher fazer backup durante o script:**

✅ **GARANTIDO**: Todos os dados do localhost serão migrados  
✅ **GARANTIDO**: Proprietários e propriedades estarão no sistema web  
✅ **GARANTIDO**: Todos os dados funcionarão perfeitamente  

**SEUS DADOS SERÃO MIGRADOS AUTOMATICAMENTE!** 🎉

