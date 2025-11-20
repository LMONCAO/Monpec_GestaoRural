# 📱 Guia de Uso - Registro de Nascimentos via WhatsApp

## 🎯 Objetivo

Permitir que o usuário registre nascimentos de bezerros enviando mensagens de áudio pelo WhatsApp, mesmo quando estiver no campo sem internet. As mensagens serão processadas automaticamente quando houver conexão.

> **📌 Nota**: O sistema também suporta registro de **Distribuição de Suplementação** via WhatsApp. Veja o guia específico em `GUIA_WHATSAPP_SUPLEMENTACAO.md`

## 📋 Como Funciona

### 1. **Envio da Mensagem**

Quando você estiver no campo e uma vaca tiver um bezerro:

1. Abra o WhatsApp no seu celular
2. Envie uma mensagem de **áudio** para o número configurado do sistema
3. Fale de forma clara e estruturada (veja exemplo abaixo)

### 2. **Processamento Offline/Online**

- Se você estiver **sem internet**: A mensagem ficará salva no WhatsApp e será enviada automaticamente quando houver conexão
- Quando a mensagem chegar ao sistema, ela será processada automaticamente
- O sistema transcreve o áudio e extrai as informações necessárias

### 3. **Registro Automático**

O sistema processa a mensagem e registra o nascimento no sistema automaticamente.

## 🗣️ Formato da Mensagem de Áudio

Fale de forma clara e inclua as seguintes informações:

### **Informações Obrigatórias:**
- ✅ **Brinco da mãe**: "A vaca com brinco 1234..."
- ✅ **Sexo do bezerro**: "É um macho" ou "É uma fêmea"

### **Informações Opcionais (mas recomendadas):**
- 📅 **Data**: "Nasceu hoje" ou "Nasceu dia 15/01/2025"
- ⏰ **Hora**: Automática (usa hora atual se não informada) ou "Às 14 horas" ou "Às 14:30"
- ⚖️ **Peso**: "Pesou 35 quilos" ou "35 kg"
- 🏷️ **Brinco do bezerro**: "O bezerro tem brinco 5678"
- 🐄 **Tipo de parto**: "Parto normal", "Cesariana" ou "Parto difícil"
- 🐂 **Raça**: "Raça Nelore" ou "É da raça Angus"
- 🎨 **Cor**: "Cor branca" ou "É de cor preta"
- 🏞️ **Invernada**: "Invernada 1" ou "Na invernada São João"

## 📝 Exemplos de Mensagens

### Exemplo 1 - Completo:
```
"Olá, acabei de registrar um nascimento. A vaca com brinco 1234 teve um bezerro. 
O bezerro tem brinco 5678, é um macho, pesou 35 quilos. Nasceu hoje, parto normal. 
Raça Nelore, cor branca, na invernada 1."
```

**Nota:** A hora será registrada automaticamente com a hora atual se não for informada.

### Exemplo 2 - Simples:
```
"A vaca brinco 1234 teve bezerro. É uma fêmea, brinco 5678, nasceu hoje."
```

### Exemplo 3 - Com data específica:
```
"Nascimento registrado. Vaca brinco 1234, bezerro brinco 5678, macho, 
pesou 38 quilos. Nasceu dia 15 de janeiro de 2025, às 10 horas da manhã, 
parto normal. Raça Angus, cor preta, invernada São João."
```

### Exemplo 4 - Sem hora (hora automática):
```
"Vaca brinco 1234 teve bezerro. Brinco 5678, fêmea, 32 quilos, 
raça Nelore, cor branca, invernada 2."
```
A hora será registrada automaticamente com a hora atual do envio da mensagem.

## 🔧 Configuração

### 1. **Configurar Número do WhatsApp**

O sistema precisa estar configurado para receber mensagens. Você pode usar:

- **Twilio WhatsApp API**
- **Evolution API**
- **WhatsApp Business API**
- Ou qualquer serviço que forneça webhook para mensagens

### 2. **Configurar Webhook**

Configure o webhook do seu provedor de WhatsApp para apontar para:
```
https://seu-dominio.com/whatsapp/webhook/
```

### 3. **Associar Número à Propriedade**

Você pode criar um modelo `PropriedadeWhatsApp` para associar números de telefone às propriedades, ou configurar manualmente no sistema.

## 📊 Acompanhamento

### Ver Mensagens Recebidas

Acesse: `Propriedade > Pecuária > Mensagens WhatsApp`

Ou diretamente: `/propriedade/{id}/whatsapp/mensagens/`

### Status das Mensagens

- **Pendente**: Aguardando processamento
- **Processando**: Sendo processada no momento
- **Processado**: Nascimento registrado com sucesso
- **Erro**: Houve algum problema (pode reprocessar)

### Reprocessar Mensagem com Erro

Se uma mensagem falhar, você pode:
1. Verificar o erro na lista de mensagens
2. Clicar em "Reprocessar" para tentar novamente
3. Ou corrigir os dados manualmente no sistema

## ⚠️ Dicas Importantes

1. **Fale claramente**: O sistema usa reconhecimento de voz, então fale pausadamente
2. **Mencione os números**: Sempre mencione "brinco" antes do número para facilitar a identificação
3. **Use palavras-chave**: "macho", "fêmea", "pesou", "nasceu", "parto", "raça", "cor", "invernada"
4. **Hora automática**: Se não informar a hora, o sistema usa automaticamente a hora atual
5. **Verifique depois**: Sempre confira se o nascimento foi registrado corretamente
6. **Mensagens offline**: O WhatsApp salva mensagens offline e envia quando houver internet

## 🔍 Validações do Sistema

O sistema valida automaticamente:

- ✅ Se a mãe (vaca) existe na propriedade
- ✅ Se o sexo foi informado
- ✅ Se a data foi identificada (usa hoje se não informado)
- ✅ Se os dados são suficientes para criar o registro

## 🛠️ Solução de Problemas

### Mensagem não foi processada

1. Verifique se o texto foi transcrito corretamente
2. Veja o erro na lista de mensagens
3. Tente reprocessar ou corrija manualmente

### Dados incorretos extraídos

1. O sistema pode não ter entendido alguma parte do áudio
2. Verifique os dados extraídos na lista
3. Corrija manualmente se necessário
4. Para melhorar, fale mais claramente nas próximas vezes

### Mãe não encontrada

1. Verifique se o brinco da mãe está correto
2. Confirme se a vaca está cadastrada na propriedade
3. Cadastre a vaca primeiro se necessário

## 📞 Suporte

Se tiver dúvidas ou problemas, entre em contato com o suporte do sistema.

---

**Última atualização**: Janeiro 2025

