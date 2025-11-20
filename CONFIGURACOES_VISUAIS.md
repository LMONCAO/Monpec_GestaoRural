# Configurações Atuais - Resumo Visual

## 📊 **PARÂMETROS CONFIGURADOS**

```
┌─────────────────────────────────────────────────────────────────┐
│                     TAXA REPRODUTIVA (NATALIDADE)                │
├─────────────────────────────────────────────────────────────────┤
│ Taxa Anual: 85.00%                                               │
│ Taxa Mensal: 7.08% (85% ÷ 12)                                   │
│                                                                   │
│ COMO FUNCIONA:                                                   │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 30 Matrizes × 7.08% = 2 bezerros/mês → 24 bezerros/ano    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│ Baseado em: Multíparas + Primíparas                              │
│ Distribuição: 50% bezerros + 50% bezerras                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       TAXA DE MORTALIDADE                        │
├─────────────────────────────────────────────────────────────────┤
│ BEZERROS (0-12 meses):                                          │
│   Taxa Anual: 5.00%                                              │
│   Taxa Mensal: 0.42% (5% ÷ 12)                                   │
│   Aplicada em: Bezerros, Bezerras                               │
│                                                                   │
│ ADULTOS (>12 meses):                                             │
│   Taxa Anual: 2.00%                                              │
│   Taxa Mensal: 0.17% (2% ÷ 12)                                   │
│   Aplicada em: Garrotes, Novilhas, Primíparas, Multíparas, Bois │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      POLÍTICA DE VENDAS                          │
├─────────────────────────────────────────────────────────────────┤
│ MACHOS: 90.00%  ──────────────────┐                            │
│ FEMEAS: 10.00%  ─────┐             │                            │
│                     │             │                            │
│ EXEMPLO:              │             │                            │
│ ┌─────────────────────┴─────────────┴───────────────────────┐  │
│ │ 50 Novilhos × 90% = 45 vendas/ano                           │  │
│ │ 50 Novilhas × 10% = 5 vendas/ano (mantém matrizes)         │  │
│ └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    EVOLUÇÃO DE IDADE                            │
├─────────────────────────────────────────────────────────────────┤
│ Taxa de Evolução: 8.33% ao mês (100% em 12 meses)              │
│                                                                   │
│ MAPEAMENTO:                                                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Bezerros (0-12m)    → Garrotes (12-24m)                    │ │
│ │ Bezerras (0-12m)    → Novilhas (12-24m)                    │ │
│ │ Garrotes (12-24m)   → Bois (24-36m)                         │ │
│ │ Novilhas (12-24m)   → Primíparas (24-36m)                   │ │
│ │ Primíparas (24-36m) → Multíparas (>36m)                     │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│ IMPORTANTE: Evolução calculada no SALDO FINAL                   │
│              (após todas as movimentações do mês)               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       PERIODICIDADE                              │
├─────────────────────────────────────────────────────────────────┤
│ Padrão: MENSAL                                                  │
│                                                                   │
│ Opções:                                                          │
│ • MENSAL (12 vezes/ano)                                          │
│ • TRIMESTRAL (4 vezes/ano)                                      │
│ • SEMESTRAL (2 vezes/ano)                                        │
│ • ANUAL (1 vez/ano)                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 **FLUXO DE PROJEÇÃO MENSUAL**

```
┌──────────────────────────────────────────────────────────────────┐
│                     PROCESSO DO MÊS                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📅 DIA 15 - MOVIMENTAÇÕES:                                       │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 1. NASCIMENTOS                                             │  │
│  │    30 matrizes × 7.08% = 2 bezerros                        │  │
│  │                                                            │  │
│  │ 2. MORTES                                                  │  │
│  │    100 bezerros × 0.42% = 0.4 mortes                      │  │
│  │    100 adultos × 0.17% = 0.2 mortes                        │  │
│  │                                                            │  │
│  │ 3. VENDAS                                                  │  │
│  │    50 novilhos × 90% = 45 vendas                           │  │
│  │    50 novilhas × 10% = 5 vendas                            │  │
│  │                                                            │  │
│  │ 4. COMPRAS                                                 │  │
│  │    2 novilhas (reposição)                                  │  │
│  │                                                            │  │
│  │ 5. TRANSFERÊNCIAS                                         │  │
│  │    1 bezerro (Fazenda A → Fazenda B)                       │  │
│  │                                                            │  │
│  │ SALDO FINAL: 100 + 2 - 0.6 - 50 - 0 + 2 - 1 = 52.4       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  📅 DIA 28 - EVOLUÇÃO DE IDADE:                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 52.4 Bezerros × 8.33% = 4 animais evoluem                   │  │
│  │                                                            │  │
│  │ PROMOCAO_SAIDA: -4 Bezerros                                │  │
│  │ PROMOCAO_ENTRADA: +4 Garrotes                              │  │
│  │                                                            │  │
│  │ SALDO FINAL AJUSTADO: 48.4 Bezerros + 4 Garrotes          │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📊 **EXEMPLO PRÁTICO (Ano 1)**

```
┌─────────────────────────────────────────────────────────────────┐
│                   PROJEÇÃO ANO 1                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│ SALDO INICIAL: 100 ANIMAIS                                      │
│                                                                  │
│ MOVIMENTAÇÕES:                                                  │
│ ├─ NASCIMENTOS:     +96 bezerros                               │
│ ├─ MORTES:          -7 animais                                │
│ ├─ VENDAS:          -180 animais                              │
│ ├─ COMPRAS:         +50 animais                               │
│ ├─ TRANFERÊNCIAS:   ±5 animais                                │
│ └─ EVOLUÇÃO:        ±85 animais mudaram de categoria          │
│                                                               │
│ SALDO FINAL: 134 ANIMAIS (+34%)                               │
│                                                               │
│ ANÁLISE FINANCEIRA:                                           │
│ ├─ Receitas (Vendas): R$ 450.000,00                          │
│ ├─ Custos (Compras + Mortes): R$ 280.000,00                   │
│ └─ Lucro: R$ 170.000,00                                       │
│                                                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ **SISTEMA PRONTO**

### **Configurações Padrão:**
- ✅ Natalidade: 85% (alto, ideal para cria)
- ✅ Mortalidade Bezerros: 5% (realista)
- ✅ Mortalidade Adultos: 2% (baixo, rebanho saudável)
- ✅ Venda Machos: 90% (maximiza receita)
- ✅ Venda Fêmeas: 10% (conserva matrizes)
- ✅ Evolução: Automática (8.33% mensal)
- ✅ Periodicidade: Mensal

### **Pronto para Usar:**
1. Cadastre o inventário inicial
2. Os parâmetros já estão configurados (ou ajuste se necessário)
3. Clique em "Gerar Projeção"
4. Escolha o período (5 anos recomendado)
5. Visualize os resultados

**Sistema funcional e pronto para projeções realistas!** 🚀

