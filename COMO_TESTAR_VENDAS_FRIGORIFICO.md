# Como Testar a Geração Automática de Relatório de Saídas

## Funcionalidade Implementada

Quando você encerra uma sessão de curral com tipo de trabalho **"Venda para Frigorífico"**, o sistema automaticamente:
1. Cria movimentações de venda para todos os animais trabalhados na sessão
2. Atualiza o status dos animais para "Vendido"
3. Gera o relatório de saídas automaticamente

## Como Testar

### Passo 1: Criar uma Sessão de Venda para Frigorífico

1. Acesse o Curral Inteligente da propriedade
2. Crie uma nova sessão de trabalho
3. **IMPORTANTE**: Selecione o tipo de trabalho como **"Venda para Frigorífico"**
4. Adicione animais à sessão (identifique animais no curral)

### Passo 2: Trabalhar com os Animais

1. Identifique e pesquise os animais na sessão
2. Registre eventos (pesagem, etc.) para os animais
3. Certifique-se de que há pelo menos um animal com evento registrado

### Passo 3: Encerrar a Sessão

1. Encerre a sessão de trabalho
2. O sistema deve:
   - Criar movimentações de venda automaticamente
   - Mostrar uma mensagem de sucesso com link para o relatório
   - Atualizar o status dos animais para "Vendido"

### Passo 4: Verificar o Relatório

1. Acesse: `/propriedade/<id>/rastreabilidade/relatorio/saidas/`
2. Ou clique no link na mensagem de sucesso
3. Verifique se os animais vendidos aparecem no relatório

## Verificações de Debug

Se não estiver funcionando, verifique:

1. **Tipo de Trabalho**: A sessão deve ter `tipo_trabalho = 'VENDA_FRIGORIFICO'`
2. **Animais na Sessão**: Deve haver eventos com animais associados
3. **Logs**: Verifique os logs do Django para mensagens de debug

## Logs de Debug

A função adiciona logs detalhados:
- Quantos eventos foram encontrados
- Quantas movimentações foram criadas
- Quais animais foram processados
- Erros, se houver

Verifique os logs do Django para mais informações.

