# 🔐 SOLUÇÃO - Login e Propriedades

## Problema Identificado

1. **Login não funciona em monpec.com.br** - usuário não encontrado
2. **Nenhuma propriedade criada** - sistema está vazio

## Causa do Problema de Login

O domínio `monpec.com.br` provavelmente está apontando para um serviço/banco de dados DIFERENTE do Cloud Run que acabamos de fazer deploy. O admin foi criado no banco do Cloud Run, mas o domínio pode estar usando outro banco.

## Soluções

### ✅ Solução 1: Usar URL Direta do Cloud Run (Imediato)

**Acesse:** https://monpec-29862706245.us-central1.run.app/login/

**Credenciais:**
- Usuário: `admin` (use apenas "admin", não o email completo)
- Senha: `L6171r12@@`

### ✅ Solução 2: Recriar Admin no Banco Correto

Se você precisa usar `monpec.com.br`, precisamos identificar qual serviço/banco ele está usando e criar o admin lá.

**Execute no Cloud Shell:**

```bash
# Verificar qual serviço o domínio está usando
gcloud run domain-mappings describe monpec.com.br --region us-central1

# Se necessário, recriar admin especificando o banco correto
# (ajuste as variáveis conforme necessário)
```

### ✅ Solução 3: Mapear Domínio para o Serviço Correto

Se o domínio não está mapeado ou está mapeado para serviço errado:

```bash
# Criar mapeamento de domínio
gcloud run domain-mappings create \
  --service monpec \
  --domain monpec.com.br \
  --region us-central1
```

**⚠️ IMPORTANTE:** Depois de criar o mapeamento, você precisa configurar os registros DNS no seu provedor de domínio.

## Sobre Propriedades

**Propriedades NÃO são criadas automaticamente.** Após fazer login como admin, você precisa:

1. **Criar um Produtor** (menu Produtores → Novo Produtor)
2. **Criar uma Propriedade** para esse produtor
3. **Configurar o Inventário** (animais, categorias, etc.)

### Passos Recomendados Após Login:

1. Login como admin
2. Acesse "Produtores" → "Novo Produtor"
3. Preencha os dados do produtor
4. Depois, crie uma propriedade para esse produtor
5. Configure o inventário de animais

## Teste Rápido

1. Acesse: https://monpec-29862706245.us-central1.run.app/login/
2. Login: `admin` / `L6171r12@@`
3. Se funcionar, o problema é apenas o mapeamento do domínio
4. Se não funcionar, o admin precisa ser recriado

## Próximos Passos

1. ✅ Teste o login na URL direta do Cloud Run
2. ✅ Se funcionar, crie propriedades pelo sistema
3. ✅ Configure o domínio personalizado se necessário








