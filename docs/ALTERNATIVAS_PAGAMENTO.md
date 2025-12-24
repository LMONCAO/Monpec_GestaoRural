# Alternativas de Pagamento - Integração com Sistema de Assinaturas

## Visão Geral

Este documento descreve as principais alternativas de plataformas de pagamento que podem ser integradas ao sistema além da Stripe, com foco no mercado brasileiro.

## Plataformas Recomendadas

### 1. Mercado Pago ⭐ (Recomendado)

**Vantagens:**
- Maior aceitação no Brasil
- Suporte completo a PIX, boleto e cartão
- Assinaturas recorrentes (Preapproval)
- Excelente documentação e SDK
- Dashboard completo

**Taxas:**
- Cartão de crédito: 4,99% + R$ 0,39
- PIX: 0,99% + R$ 0,39
- Boleto: R$ 3,50

**SDK Python:**
```bash
pip install mercadopago
```

**Documentação:** https://www.mercadopago.com.br/developers/pt/docs

---

### 2. Asaas ⭐ (Melhor para Assinaturas)

**Vantagens:**
- Especializado em assinaturas recorrentes
- Taxas competitivas
- Suporte a PIX, boleto e cartão
- API simples e direta
- Cobrança automática eficiente

**Taxas:**
- PIX: 0,99%
- Boleto: R$ 3,00
- Cartão de crédito: 2,99% + R$ 0,39

**SDK Python:**
```bash
# Não há SDK oficial, usar requests
pip install requests
```

**Documentação:** https://asaas.com/api-doc/

---

### 3. Gerencianet (Efí)

**Vantagens:**
- Forte em PIX e boleto
- Boa para assinaturas
- API robusta
- Suporte técnico bom

**Taxas:**
- PIX: 0,99%
- Boleto: R$ 2,50
- Cartão: 2,99% + R$ 0,39

**SDK Python:**
```bash
pip install gerencianet-sdk-python
```

**Documentação:** https://dev.gerencianet.com.br/

---

### 4. Iugu

**Vantagens:**
- Focado em assinaturas recorrentes
- Suporte a PIX, boleto e cartão
- API simples
- Dashboard intuitivo

**Taxas:**
- PIX: 0,99%
- Boleto: R$ 2,50
- Cartão: 2,99% + R$ 0,39

**SDK Python:**
```bash
pip install iugu-python
```

**Documentação:** https://dev.iugu.com/

---

### 5. PagSeguro

**Vantagens:**
- Amplamente conhecido no Brasil
- Múltiplas formas de pagamento
- Boa aceitação

**Taxas:**
- Cartão: ~4,99% + R$ 0,40
- PIX: 0,99% + R$ 0,40

**SDK Python:**
```bash
pip install pagseguro-python
```

**Documentação:** https://dev.pagseguro.uol.com.br/

---

## Comparação Rápida

| Plataforma | Assinaturas | PIX | Taxa PIX | Facilidade | Recomendação |
|------------|-------------|-----|----------|------------|--------------|
| Mercado Pago | ✅ | ✅ | 0,99% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Asaas | ✅✅ | ✅ | 0,99% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Gerencianet | ✅ | ✅ | 0,99% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Iugu | ✅✅ | ✅ | 0,99% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| PagSeguro | ✅ | ✅ | 0,99% | ⭐⭐⭐ | ⭐⭐⭐ |

---

## Estrutura de Integração Sugerida

Para manter a flexibilidade e permitir múltiplos gateways, sugere-se criar uma estrutura abstrata:

```
gestao_rural/
  services/
    payments/
      __init__.py
      base.py          # Classe abstrata para gateways
      stripe_client.py # (já existe)
      mercado_pago.py  # Nova integração
      asaas_client.py  # Nova integração
      gerencianet_client.py # Nova integração
      factory.py       # Factory para escolher gateway
```

---

## Próximos Passos

1. Escolher a plataforma (recomendado: Mercado Pago ou Asaas)
2. Criar estrutura abstrata de pagamento
3. Implementar cliente específico
4. Atualizar views para suportar múltiplos gateways
5. Adicionar configurações no settings.py
6. Implementar webhooks
7. Testar integração

---

## Notas Importantes

- **PIX**: Todas as plataformas suportam PIX, que é essencial no Brasil
- **Assinaturas**: Asaas e Iugu são especializados, mas Mercado Pago também oferece
- **Taxas**: Considere negociar taxas com volume maior
- **Webhooks**: Todas as plataformas oferecem webhooks para notificações
- **Ambiente de Teste**: Todas oferecem sandbox para testes




