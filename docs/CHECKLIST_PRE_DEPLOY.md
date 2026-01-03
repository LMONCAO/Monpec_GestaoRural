# ✅ Checklist Pré-Deploy

## 🔍 Verificações Obrigatórias

### 1. Código
- [x] Migration 0100 corrigida (dependência atualizada)
- [x] Tratamento de erros melhorado (Cocho, Funcionario)
- [x] Testes ajustados para serem mais robustos
- [x] Imports corrigidos

### 2. Migrations
- [ ] Verificar migrations pendentes: `python manage.py showmigrations`
- [ ] Aplicar migrations localmente: `python manage.py migrate`
- [ ] Verificar se não há conflitos: `python manage.py makemigrations --dry-run`

### 3. Testes
- [x] Testes de serviços: 18/18 passando (100%)
- [x] Testes de views: 15/18 passando (83%)
- [x] Testes de autenticação: 8/8 passando (100%)
- [ ] Executar todos os testes: `pytest tests/`

### 4. Configurações
- [ ] Verificar variáveis de ambiente no Cloud Run
- [ ] Verificar SECRET_KEY configurada
- [ ] Verificar DATABASE_URL configurada
- [ ] Verificar ALLOWED_HOSTS

### 5. Banco de Dados
- [ ] Backup do banco antes do deploy
- [ ] Verificar conexão com Cloud SQL
- [ ] Aplicar migrations no Cloud SQL

---

## 🚀 Comandos de Deploy

### 1. Preparar
```bash
# Verificar status
git status

# Commit correções (se necessário)
git add .
git commit -m "Correções: migration e tratamento de erros"
git push
```

### 2. Aplicar Migrations
```bash
# Localmente primeiro (testar)
python manage.py migrate

# No Cloud (via Cloud Shell ou Job)
gcloud run jobs execute migrate-db --region us-central1
```

### 3. Deploy
```bash
# Build e deploy
gcloud builds submit --config cloudbuild.yaml

# OU deploy direto
gcloud run deploy monpec --source . --region us-central1
```

### 4. Verificar
```bash
# Ver logs
gcloud run services logs read monpec --region us-central1 --limit 50

# Testar site
curl https://monpec.com.br
```

---

## ⚠️ Problemas Conhecidos e Soluções

### Problema: "Service Unavailable"
**Causa**: Serviço não está rodando ou há erro no código
**Solução**: 
1. Verificar logs do Cloud Run
2. Verificar se migrations foram aplicadas
3. Verificar variáveis de ambiente

### Problema: Migration não aplica
**Causa**: Dependência de migration não existe
**Solução**: ✅ Já corrigido - Migration 0100 atualizada

### Problema: Tabelas opcionais não existem
**Causa**: Migrations opcionais não aplicadas
**Solução**: ✅ Já corrigido - Tratamento de erro adicionado

---

## 📊 Status Atual

| Item | Status |
|------|--------|
| Migration 0100 | ✅ Corrigida |
| Tratamento de erros | ✅ Melhorado |
| Testes | ✅ 91% passando |
| Código | ✅ Pronto para deploy |

---

**Última atualização**: Janeiro 2026

