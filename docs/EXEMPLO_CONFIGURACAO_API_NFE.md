# Configuração da API de Nota Fiscal Eletrônica

Este documento explica como configurar a integração com APIs de NF-e no sistema.

## APIs Suportadas

O sistema suporta integração com:
- **Focus NFe** (https://doc.focusnfe.com.br/)
- **NFe.io** (https://nfe.io/)

## Configuração

Adicione as seguintes configurações no arquivo `settings.py`:

### Focus NFe

```python
API_NFE = {
    'TIPO': 'FOCUS_NFE',
    'TOKEN': 'seu_token_aqui',
    'AMBIENTE': 'homologacao',  # ou 'producao'
}
```

### NFe.io

```python
API_NFE = {
    'TIPO': 'NFE_IO',
    'TOKEN': 'seu_token_aqui',
    'COMPANY_ID': 'id_da_empresa',
    'AMBIENTE': 'homologacao',  # ou 'producao'
}
```

## Como Obter Credenciais

### Focus NFe

1. Acesse https://www.focusnfe.com.br/
2. Crie uma conta
3. Obtenha seu token na área de configurações
4. Use o ambiente de homologação para testes

### NFe.io

1. Acesse https://nfe.io/
2. Crie uma conta
3. Obtenha seu token e Company ID na área de configurações
4. Use o ambiente de homologação para testes

## Notas Importantes

- **Ambiente de Homologação**: Use para testes. As NF-e emitidas não têm validade fiscal.
- **Ambiente de Produção**: Use apenas após testar completamente. As NF-e emitidas têm validade fiscal.
- Mantenha suas credenciais seguras e nunca as compartilhe.
- O sistema tentará emitir a NF-e automaticamente quando você criar uma nova nota fiscal de saída.

## Sem Configuração

Se a API não estiver configurada, o sistema ainda permitirá criar notas fiscais, mas elas ficarão com status "PENDENTE" e você precisará emitir manualmente através da API ou importar o XML posteriormente.

