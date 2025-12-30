# 🔍 DIAGNÓSTICO - Problema de Login

## Problema Identificado

Você está acessando `monpec.com.br/login/` mas o usuário admin não é encontrado, mesmo tendo sido criado com sucesso no Cloud Run Job.

## Possíveis Causas

1. **Domínio apontando para serviço diferente**: `monpec.com.br` pode estar apontando para outro serviço/instância que usa um banco de dados diferente
2. **Múltiplos serviços Cloud Run**: Pode haver mais de um serviço rodando
3. **Banco de dados diferente**: O domínio pode estar usando um banco diferente do que o job atualizou

## Solução Rápida

### Opção 1: Usar a URL direta do Cloud Run

Acesse: **https://monpec-29862706245.us-central1.run.app/login/**
- Usuário: `admin` (não use email)
- Senha: `L6171r12@@`

### Opção 2: Verificar qual serviço o domínio está usando

Execute no Cloud Shell:

```bash
# Verificar mapeamento do domínio
gcloud run domain-mappings list --region us-central1

# Ver qual serviço o domínio está mapeado
gcloud run domain-mappings describe monpec.com.br --region us-central1
```

### Opção 3: Recriar admin no banco correto

Se o domínio está usando um banco diferente, você precisa criar o admin novamente especificando o banco correto.

## Sobre Propriedades

Propriedades precisam ser criadas manualmente após o login, ou através de scripts de inicialização. O admin sozinho não cria propriedades automaticamente.








