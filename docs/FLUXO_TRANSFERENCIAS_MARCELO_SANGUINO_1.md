# 🔄 FLUXO DE TRANSFERÊNCIAS - MARCELO SANGUINO

## 📋 PROPRIEDADES CONFIGURADAS

1. **Fazenda Canta Galo** (ID: 2) - **MATRIZ**
   - Propriedade principal que transfere gado para outras fazendas
   - Configurada conforme `FLUXO_PROJECAO_COMPLETO.md`

2. **Invernada Grande** (ID: 3)
   - Recebe vacas de descarte da Canta Galo
   - Período: 2022 a 2025

3. **Favo de Mel** (ID: 4)
   - Recebe machos 12-24 meses da Canta Galo
   - Vende 100 cabeças a cada 60 dias (sem saldo negativo)
   - Transfere animais para Girassol após evolução

4. **Girassol** (ID: 5)
   - Recebe animais da Favo de Mel
   - Animais ficam 90 dias e viram boi gordo

---

## 🔄 FLUXO DE TRANSFERÊNCIAS

### 1. Canta Galo → Invernada Grande
- **Categoria**: Vacas de Descarte
- **Frequência**: Anual (janeiro de cada ano)
- **Período**: 2022 a 2025
- **Quantidade**: 100% do estoque inicial de vacas de descarte

### 2. Canta Galo → Favo de Mel
- **Categoria**: Garrotes 12-24 meses
- **Frequência**: Anual (janeiro de cada ano)
- **Quantidade**: 100% do estoque inicial de garrotes 12-24 meses
- **Evolução**: Ao chegar na Favo de Mel, os animais evoluem de categoria

### 3. Favo de Mel - Vendas
- **Categoria**: Boi 24-36 M (após evolução)
- **Frequência**: Bimestral (a cada 60 dias)
- **Quantidade**: 100 cabeças por venda
- **Proteção**: Não vende se saldo ficar negativo
- **Comportamento**: Aguarda próxima transferência se não houver saldo suficiente

### 4. Favo de Mel → Girassol
- **Categoria**: Boi 24-36 M (após evolução na Favo de Mel)
- **Frequência**: Trimestral (a cada 90 dias)
- **Quantidade**: Conforme disponibilidade (sem saldo negativo)
- **Comportamento**: Aguarda próxima transferência se não houver saldo suficiente

### 5. Girassol - Processamento
- **Tempo de permanência**: 90 dias
- **Resultado**: Animais viram "Boi Gordo"
- **Ciclo**: Após saída dos animais, recebe nova transferência da Favo de Mel

---

## ⚙️ CONFIGURAÇÕES TÉCNICAS

### Proteções Implementadas

1. **Saldo Negativo**
   - ✅ Favo de Mel: Não vende se saldo ficar negativo
   - ✅ Girassol: Não recebe se não houver saldo na Favo de Mel
   - ✅ Sistema aguarda próxima transferência quando não há saldo suficiente

2. **Transferências**
   - ✅ Apenas estoque inicial do ano é transferido (não animais criados durante o ano)
   - ✅ Transferências acontecem apenas em janeiro de cada ano
   - ✅ Vacas de descarte e garrotes são transferências, não vendas

3. **Evolução de Categoria**
   - ✅ Garrotes 12-24 M → Boi 24-36 M (na Favo de Mel)
   - ✅ Boi 24-36 M → Boi Gordo (na Girassol, após 90 dias)

---

## 📝 SCRIPTS CRIADOS

1. **`configurar_propriedades_marcelo_sanguino.py`**
   - Cria as 4 propriedades do Marcelo Sanguino

2. **`configurar_fluxo_transferencias_marcelo_sanguino.py`**
   - Configura todas as transferências e vendas entre as propriedades

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ Propriedades criadas
2. ✅ Transferências configuradas
3. ⏳ Configurar inventário inicial na **Fazenda Canta Galo**
4. ⏳ Gerar projeção para testar o fluxo completo

---

## 📊 EXEMPLO DE FLUXO

### Ano 2025 - Janeiro
- **Canta Galo**: Transfere vacas de descarte → Invernada Grande
- **Canta Galo**: Transfere garrotes 12-24 M → Favo de Mel

### Ano 2025 - Março (60 dias após janeiro)
- **Favo de Mel**: Vende 100 cabeças (se tiver saldo suficiente)

### Ano 2025 - Abril (90 dias após janeiro)
- **Favo de Mel**: Transfere animais para Girassol (se tiver saldo)

### Ano 2025 - Julho (90 dias após abril)
- **Girassol**: Animais viram boi gordo e saem
- **Favo de Mel**: Transfere nova leva para Girassol

---

## ⚠️ IMPORTANTE

- As transferências usam apenas o **estoque inicial do ano** (não animais criados durante o ano)
- As vendas na Favo de Mel respeitam o saldo disponível (não ficam negativas)
- O sistema aguarda automaticamente a próxima transferência quando não há saldo suficiente
- Todas as configurações estão ativas e prontas para uso

