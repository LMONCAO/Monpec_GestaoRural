# 📱 Guia de Uso - Distribuição de Suplementação via WhatsApp

## 🎯 Objetivo

Permitir que o usuário registre distribuições de suplementação (sal, ração, etc.) enviando mensagens de áudio pelo WhatsApp, mesmo quando estiver no campo sem internet. As mensagens serão processadas automaticamente quando houver conexão.

## 📋 Como Funciona

### 1. **Envio da Mensagem**

Quando você distribuir suplementação no campo:

1. Abra o WhatsApp no seu celular
2. Envie uma mensagem de **áudio** para o número configurado do sistema
3. Fale de forma clara e estruturada (veja exemplo abaixo)

### 2. **Processamento Offline/Online**

- Se você estiver **sem internet**: A mensagem ficará salva no WhatsApp e será enviada automaticamente quando houver conexão
- Quando a mensagem chegar ao sistema, ela será processada automaticamente
- O sistema transcreve o áudio e extrai as informações necessárias

### 3. **Registro Automático**

O sistema processa a mensagem e registra a distribuição no sistema automaticamente, atualizando o estoque.

## 🗣️ Formato da Mensagem de Áudio

Fale de forma clara e inclua as seguintes informações:

### **Informações Obrigatórias:**
- ✅ **Tipo de suplementação**: "Sal mineral", "Ração", "Suplemento proteico"
- ✅ **Quantidade**: "2 sacos" ou "2 sacos" (o sistema converte automaticamente conforme cadastro do estoque)
- ✅ **Invernada**: "Invernada 1" ou "Na invernada São João"

### **Informações Opcionais:**
- 🏷️ **Nome do produto**: "Produto Boi Forte" ou "Nome do produto Boi Forte"
- 📅 **Data**: "Hoje" ou "Dia 15/01/2025" (usa hoje se não informado)

## 📝 Exemplos de Mensagens

### Exemplo 1 - Completo:
```
"Olá, acabei de distribuir suplementação. Tipo sal mineral, 
produto Boi Forte, quantidade 2 sacos, na invernada 1. Distribuí hoje."
```

**Nota:** O sistema converte automaticamente de sacos para a unidade do estoque (ex: 2 sacos = 100 kg, se o estoque tiver "50 kg por saco" nas observações).

### Exemplo 2 - Simples:
```
"Distribuí 2 sacos de ração na invernada 2."
```

### Exemplo 3 - Com data específica:
```
"Distribuição registrada. Tipo suplemento proteico, 
quantidade 3 sacos, invernada São João, dia 15 de janeiro."
```

## 📊 Ordem dos Dados Registrados

O sistema registra as informações na seguinte ordem:

1. **Tipo de suplementação**: Sal mineral, Ração, etc.
2. **Produto**: Boi Forte (se informado)
3. **Quantidade**: 2 sacos (100 kg) - mostra sacos e conversão
4. **Invernada**: 1
5. **Data**: 15/01/2025 (ou hoje se não informado)
6. **Observação**: Informações adicionais (se houver)

## 🔄 Conversão de Sacos

O sistema aceita quantidade em **sacos** e faz a conversão automática:

- **Como funciona**: O sistema busca o fator de conversão nas observações do estoque
- **Padrão**: Se não encontrar, usa 50 kg por saco
- **Formato nas observações do estoque**: "50 kg por saco" ou "1 saco = 50kg" ou "50 kg/saco"

**Exemplo:**
- Você informa: "2 sacos"
- Estoque tem: "50 kg por saco" nas observações
- Sistema registra: "2 sacos (100 kg)"

## ⚠️ Requisitos Importantes

### **Estoque Deve Existir**

Antes de distribuir, você precisa ter o **estoque cadastrado** no sistema:

1. Acesse: **Nutrição > Estoques**
2. Cadastre o tipo de suplementação (Sal mineral, Ração, etc.)
3. Informe a quantidade inicial em estoque

**O sistema verifica automaticamente:**
- ✅ Se o estoque existe
- ✅ Se há quantidade suficiente disponível
- ✅ Atualiza o estoque após a distribuição

## 🔧 Validações do Sistema

O sistema valida automaticamente:

- ✅ Se o tipo de suplementação foi informado
- ✅ Se a quantidade foi informada
- ✅ Se a invernada foi informada
- ✅ Se o estoque existe na propriedade
- ✅ Se há quantidade suficiente no estoque

## 🛠️ Solução de Problemas

### Estoque não encontrado

**Erro**: "Estoque de [tipo] não encontrado"

**Solução**: 
1. Cadastre o estoque primeiro em: **Nutrição > Estoques**
2. Informe o tipo exato (ex: "Sal Mineral" ou "Ração")
3. Tente novamente

### Estoque insuficiente

**Erro**: "Estoque insuficiente! Disponível: X kg"

**Solução**:
1. Verifique a quantidade disponível em estoque
2. Reduza a quantidade na mensagem
3. Ou adicione mais ao estoque primeiro

### Tipo não identificado

**Solução**: 
- Fale mais claramente: "Tipo sal mineral" ou "Tipo ração"
- Use palavras-chave: "sal", "ração", "suplemento"

## 📞 Integração com Sistema

Após o registro:
- ✅ A distribuição é registrada automaticamente
- ✅ O estoque é atualizado (quantidade reduzida)
- ✅ O valor total é calculado automaticamente
- ✅ Fica disponível nos relatórios de nutrição

---

**Última atualização**: Janeiro 2025

