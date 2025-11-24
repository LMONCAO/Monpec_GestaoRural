# 📋 CONFIGURAÇÃO COMPLETA DO SIMULADOR DE PESAGEM E IDENTIFICAÇÃO

## 🎯 OBJETIVO DO SIMULADOR

O simulador foi desenvolvido para automatizar o processo de:
1. **Cadastro de brincos disponíveis no estoque** como animais
2. **Processamento de animais cadastrados** com pesagem e manejo
3. **Geração de log detalhado** de todas as operações realizadas

---

## ⚙️ CONFIGURAÇÕES PRINCIPAIS

### 1. **DELAY INICIAL**
- **Tempo de espera antes de iniciar:** 20 segundos
- **Comportamento:** Contagem regressiva visível na tela (a cada 5 segundos ou nos últimos 5 segundos)
- **Objetivo:** Permitir que o usuário se prepare e o sistema carregue completamente

### 2. **OCULTAÇÃO DO BOTÃO**
- **Comportamento:** O botão "Iniciar Simulador" desaparece automaticamente quando o simulador inicia
- **Retorno:** O botão reaparece quando o simulador finaliza ou é interrompido

### 3. **CRIAÇÃO DE SESSÃO**
- **Tipo de sessão:** Pesagem (COLETA_DADOS)
- **Momento:** Criada automaticamente antes de iniciar o processamento
- **Tratamento de erro:** Se falhar, o simulador continua com aviso

---

## 📊 FASE 1: CADASTRO DE BRINCOS DO ESTOQUE

### **Fonte de Dados**
- **API utilizada:** `/propriedade/{id}/curral/api/dados-simulacao/`
- **Filtro:** Apenas brincos com status `DISPONIVEL`
- **Limite:** Até 500 brincos (configurado no backend)

### **Processo de Cadastro**

Para cada brinco disponível no estoque:

1. **Leitura do Brinco**
   - Campo utilizado: `brincoInputV3`
   - Simula digitação humanizada (80ms por caractere)
   - Delay: 800-1500ms antes de iniciar

2. **Busca no Sistema**
   - Chama `buscarBrincoV3()` para verificar se o animal já existe
   - Aguarda 2000-3000ms para resposta do sistema

3. **Verificação de Existência**
   - Se animal já cadastrado: pula para próximo brinco
   - Se não encontrado: abre modal de cadastro

4. **Preenchimento do Cadastro** (se necessário)
   - **RFID/Chip:** Gera número aleatório no formato `900` + 12 dígitos
   - **Raça:** Aleatória entre:
     - Nelore (código: `NE`)
     - Composto (código: `XX`)
   - **Sexo:** Aleatório (50% Fêmea, 50% Macho)
   - **Idade:** Aleatória entre 6 e 18 meses
   - **Tipo de Registro:** Sempre `DESMAMA`

5. **Confirmação e Atualização**
   - Clica no botão de confirmar cadastro
   - Aguarda 2000-3000ms
   - Fecha modal se ainda estiver aberto
   - Busca novamente o brinco para atualizar o card principal

6. **Delay entre Brincos**
   - 1000-2000ms de pausa humanizada

### **Dados Gerados Aleatoriamente**

| Campo | Valores | Observação |
|-------|---------|------------|
| **Raça** | Nelore, Composto | Apenas estas duas raças |
| **Sexo** | F (Fêmea), M (Macho) | Distribuição 50/50 |
| **Idade** | 6 a 18 meses | Aleatória |
| **RFID** | 900 + 12 dígitos | Formato padrão |
| **Tipo Registro** | DESMAMA | Fixo |

---

## 📊 FASE 2: PROCESSAMENTO DE ANIMAIS CADASTRADOS

### **Fonte de Dados**
- **API utilizada:** `/propriedade/{id}/curral/api/dados-simulacao/`
- **Filtro:** Apenas animais com status `ATIVO`
- **Limite:** Até 500 animais (configurado no backend)

### **Processo de Processamento**

Para cada animal cadastrado:

1. **Leitura do Brinco**
   - Campo utilizado: `brincoInputV3`
   - Usa código SISBOV, número de brinco ou número de manejo
   - Simula digitação humanizada (80ms por caractere)
   - Delay: 800-1500ms antes de iniciar

2. **Busca no Sistema**
   - Chama `buscarBrincoV3()` para localizar o animal
   - Aguarda 2000-3000ms para resposta
   - Verifica se animal foi encontrado (verifica campo `scannerNumeroManejoV3`)

3. **Registro de Pesagem**
   - Campo utilizado: `pesoValorV3`
   - **Peso gerado:**
     - **Fêmeas:** 185 a 210 kg (aleatório)
     - **Machos:** 195 a 220 kg (aleatório)
   - Dispara eventos `input` e `change` para atualizar o sistema
   - Delay: 500-1000ms após preencher

4. **Seleção de Manejo**
   - Campo utilizado: `manejoSelectV3` (select dropdown)
   - **Manejo selecionado:** Sempre "Desmama"
   - Busca a opção que contém "desmama" no texto ou valor
   - Dispara evento `change`
   - Delay: 500-1000ms após selecionar

5. **Finalização e Gravação**
   - Botão utilizado: `btnFinalizarGravarV3` ou `pesoGravarBtnV3`
   - Clica no botão para gravar
   - Aguarda 2000-3000ms para processamento

6. **Limpeza de Campos**
   - Limpa campo de brinco para próximo animal
   - Delay: 1000-2000ms entre animais

### **Pesos Gerados**

| Sexo | Faixa de Peso | Observação |
|------|---------------|------------|
| **Fêmea (F)** | 185 a 210 kg | Aleatório dentro da faixa |
| **Macho (M)** | 195 a 220 kg | Aleatório dentro da faixa |

---

## 📝 SISTEMA DE LOG DETALHADO

### **Estrutura do Log**

O simulador registra **TODAS** as operações realizadas com:

- **Timestamp:** Data e hora exata da operação (ISO 8601)
- **Operação:** Descrição da ação realizada
- **Status:** 
  - `OK` - Operação concluída com sucesso
  - `ERRO` - Operação falhou
  - `INFO` - Informação geral
- **Detalhes:** Objeto JSON com informações específicas da operação

### **Exemplos de Operações Registradas**

```javascript
{
  timestamp: "2024-01-15T10:30:45.123Z",
  operacao: "Cadastrar brinco 1/50",
  status: "INFO",
  detalhes: {
    numero_brinco: "105500376195129",
    codigo_rfid: "900123456789012"
  }
}
```

```javascript
{
  timestamp: "2024-01-15T10:31:20.456Z",
  operacao: "Brinco 1/50 cadastrado",
  status: "OK",
  detalhes: {
    numero_brinco: "105500376195129"
  }
}
```

```javascript
{
  timestamp: "2024-01-15T10:32:10.789Z",
  operacao: "Erro ao cadastrar brinco 5/50",
  status: "ERRO",
  detalhes: {
    numero_brinco: "105500376195133",
    mensagem: "Campo de brinco não encontrado"
  }
}
```

### **Relatório Final**

O relatório é gerado automaticamente ao final da simulação e contém:

1. **Informações Gerais**
   - Data/hora de início
   - Data/hora de fim
   - Duração total
   - Fase final

2. **Estatísticas da Fase 1**
   - Total de brincos cadastrados com sucesso
   - Total de brincos com erro
   - Taxa de sucesso (%)

3. **Estatísticas da Fase 2**
   - Total de animais processados com sucesso
   - Total de animais com erro
   - Taxa de sucesso (%)

4. **Estatísticas de Operações**
   - Total de operações realizadas
   - Operações OK
   - Operações com ERRO
   - Operações INFO

5. **Lista de Erros**
   - Fase onde ocorreu
   - Tipo de erro
   - Código do brinco/animal
   - Mensagem de erro
   - Timestamp

6. **Log Detalhado Completo**
   - Todas as operações em ordem cronológica
   - Status de cada operação
   - Detalhes completos de cada operação

### **Formato de Saída**

- **Console do navegador:** Relatório formatado em texto
- **Arquivo TXT:** Download automático com nome `relatorio_simulador_YYYY-MM-DDTHH-MM-SS.txt`
- **Modal na tela:** Exibição do relatório completo em modal

---

## 🎨 INTERFACE DO USUÁRIO

### **Mensagens na Tela**

Durante a execução, o simulador exibe mensagens explicativas em toast notifications:

- **Tipo INFO (azul):** Informações gerais do processo
- **Tipo SUCCESS (verde):** Operações concluídas com sucesso
- **Tipo WARNING (amarelo):** Avisos e interrupções
- **Tipo ERROR (vermelho):** Erros encontrados

### **Exemplos de Mensagens**

- "Simulador iniciado. Aguardando 20 segundos antes de começar..."
- "Iniciando em 15 segundos..."
- "FASE 1: Cadastrando brincos disponíveis do estoque..."
- "Brinco 1/50: Cadastrando 105500376195129..."
- "Brinco 1/50: Preenchendo dados (Raça: Nelore, Sexo: Fêmea)..."
- "Animal 1/100: Lendo brinco 105500376195129..."
- "Animal 1/100: Registrando pesagem (195.5 kg)..."
- "Animal 1/100: Selecionando manejo (Desmama)..."
- "Simulação concluída! Verifique o relatório no console e arquivo TXT."

---

## ⚡ VELOCIDADE E TIMING

### **Delays Humanizados**

O simulador utiliza delays aleatórios para simular comportamento humano:

| Ação | Delay Mínimo | Delay Máximo | Observação |
|------|--------------|--------------|------------|
| Antes de iniciar leitura | 800ms | 1500ms | Simula tempo de preparação |
| Após digitar brinco | 500ms | 1000ms | Simula verificação |
| Após buscar no sistema | 2000ms | 3000ms | Aguarda resposta do backend |
| Após preencher campo | 200-500ms | 400-1000ms | Varia por tipo de campo |
| Entre animais/brincos | 1000ms | 2000ms | Pausa entre processamentos |
| Após confirmar cadastro | 2000ms | 3000ms | Aguarda processamento |

### **Velocidade de Digitação**

- **Taxa:** 80ms por caractere
- **Simulação:** Digitação caractere por caractere (não cola o texto completo)

---

## 🔧 CONFIGURAÇÕES TÉCNICAS

### **APIs Utilizadas**

1. **Buscar Brincos/Animais:**
   - Endpoint: `/propriedade/{propriedade_id}/curral/api/dados-simulacao/`
   - Método: GET
   - Retorna: Lista de brincos disponíveis e animais cadastrados

2. **Identificar Código:**
   - Endpoint: `/propriedade/{propriedade_id}/curral/api/identificar/`
   - Método: GET
   - Parâmetro: `codigo` (número do brinco/SISBOV)

3. **Registrar Manejo:**
   - Endpoint: `/propriedade/{propriedade_id}/curral/api/registrar/`
   - Método: POST
   - Body: Dados do animal e manejo

4. **Criar Sessão:**
   - Endpoint: `/propriedade/{propriedade_id}/curral/api/sessao/criar/`
   - Método: POST
   - Body: Dados da sessão

### **Elementos DOM Utilizados**

#### **Campos de Entrada:**
- `brincoInputV3` - Campo de leitura do brinco
- `pesoValorV3` - Campo de peso
- `cadastroRfidV3` - Campo de RFID no modal de cadastro
- `cadastroRacaV3` - Select de raça no modal
- `cadastroSexoV3` - Select de sexo no modal
- `cadastroIdadeV3` - Campo de idade no modal
- `cadastroTipoRegistroV3` - Select de tipo de registro no modal
- `manejoSelectV3` - Select de manejo

#### **Botões:**
- `btnSimulador` - Botão para iniciar o simulador
- `btnConfirmarCadastroV3` - Botão de confirmar cadastro no modal
- `btnFinalizarGravarV3` - Botão de finalizar e gravar
- `pesoGravarBtnV3` - Botão alternativo de gravar pesagem

#### **Modais:**
- `modalCadastroEstoque` - Modal de cadastro de animal

#### **Elementos de Exibição:**
- `scannerNumeroManejoV3` - Exibe número de manejo do animal encontrado
- `scannerSisbovV3` - Exibe SISBOV do animal encontrado
- `scannerCodigoEletronicoV3` - Exibe código eletrônico do animal encontrado

---

## 🚨 TRATAMENTO DE ERROS

### **Tipos de Erros Capturados**

1. **Erro de Campo Não Encontrado**
   - Exemplo: "Campo de brinco não encontrado"
   - Ação: Registra no log e continua com próximo item

2. **Erro de Modal Não Encontrado**
   - Exemplo: "Modal de cadastro não encontrado"
   - Ação: Registra no log e continua com próximo item

3. **Erro de Animal Não Encontrado**
   - Exemplo: "Animal não encontrado após busca"
   - Ação: Registra no log e continua com próximo item

4. **Erro de API**
   - Exemplo: "Erro HTTP 500"
   - Ação: Registra no log com detalhes e continua

5. **Erro de Sessão**
   - Exemplo: "Erro ao criar sessão de pesagem"
   - Ação: Registra no log mas continua a simulação

### **Estrutura de Erro no Log**

```javascript
{
  fase: "CADASTRO_BRINCOS" | "PROCESSAMENTO_ANIMAIS",
  brinco: "105500376195129", // ou animal
  indice: 5,
  tipo: "Cadastro de Brinco" | "Processamento de Animal",
  mensagem: "Descrição do erro",
  timestamp: "2024-01-15T10:30:45.123Z"
}
```

---

## 📊 ESTATÍSTICAS COLETADAS

O simulador mantém estatísticas detalhadas durante toda a execução:

### **Variáveis de Controle**

```javascript
simuladorRelatorio = {
  fase: "INICIO" | "CADASTRO_BRINCOS" | "PROCESSAMENTO_ANIMAIS" | "FINALIZADO",
  brincosCadastrados: 0,
  brincosComErro: 0,
  animaisProcessados: 0,
  animaisComErro: 0,
  operacoes: [], // Array de todas as operações
  erros: [], // Array de erros encontrados
  inicio: "2024-01-15T10:30:00.000Z",
  fim: "2024-01-15T11:45:00.000Z"
}
```

---

## 🎯 FLUXO COMPLETO DE EXECUÇÃO

```
1. Usuário clica em "Iniciar Simulador"
   ↓
2. Confirmação de diálogo
   ↓
3. Botão desaparece da tela
   ↓
4. Aguarda 20 segundos (contagem regressiva)
   ↓
5. Cria sessão de pesagem
   ↓
6. FASE 1: Busca brincos disponíveis no estoque
   ↓
7. Para cada brinco:
   - Lê brinco
   - Busca no sistema
   - Se não encontrado: cadastra
   - Registra no log
   ↓
8. FASE 2: Busca animais cadastrados
   ↓
9. Para cada animal:
   - Lê brinco
   - Busca no sistema
   - Registra pesagem
   - Seleciona manejo (Desmama)
   - Grava dados
   - Registra no log
   ↓
10. Gera relatório completo
   ↓
11. Faz download do arquivo TXT
   ↓
12. Exibe modal com relatório
   ↓
13. Botão reaparece na tela
```

---

## 🔍 DEBUGGING E LOGS

### **Logs no Console**

O simulador gera logs detalhados no console do navegador:

- `🔵` - Informações gerais do simulador
- `✅` - Operações bem-sucedidas
- `❌` - Erros encontrados
- `🖱️` - Ações de clique
- `🔍` - Verificações e checagens
- `ℹ️` - Informações adicionais

### **Como Verificar se Está Funcionando**

1. Abra o console do navegador (F12)
2. Procure por mensagens com emojis
3. Verifique se há erros em vermelho
4. Confirme que as operações estão sendo registradas

---

## 📦 ARQUIVO DE LOG GERADO

### **Nome do Arquivo**
`relatorio_simulador_YYYY-MM-DDTHH-MM-SS.txt`

Exemplo: `relatorio_simulador_2024-01-15T10-30-45.txt`

### **Conteúdo do Arquivo**

O arquivo contém:
- Relatório completo formatado
- Todas as estatísticas
- Lista de erros
- Log detalhado de todas as operações
- Timestamps de todas as ações

### **Localização**
O arquivo é baixado automaticamente na pasta de downloads padrão do navegador.

---

## ⚠️ OBSERVAÇÕES IMPORTANTES

1. **Dados Reais:** O simulador trabalha com dados reais do banco de dados
2. **Não Destrutivo:** As operações são reais, então os dados serão realmente cadastrados/atualizados
3. **Performance:** O simulador processa até 500 brincos e 500 animais (limite configurado no backend)
4. **Interrupção:** O simulador pode ser interrompido, mas os dados já processados não serão revertidos
5. **Log Completo:** Todas as operações são registradas, mesmo as que falharam

---

## 🎓 RESUMO DAS SOLICITAÇÕES ATENDIDAS

✅ **Delay de 20 segundos antes de iniciar**  
✅ **Botão desaparece quando inicia**  
✅ **Cria sessão de pesagem automaticamente**  
✅ **Identifica animais como desmama**  
✅ **Cadastra brincos livres do estoque**  
✅ **Processa animais cadastrados com pesagem e manejo**  
✅ **Gera pesos aleatórios (Fêmeas: 185-210kg, Machos: 195-220kg)**  
✅ **Usa apenas raças Nelore e Composto**  
✅ **Gera log detalhado em TXT**  
✅ **Registra erros e status OK**  
✅ **Exibe mensagens explicativas na tela**  
✅ **Velocidade humanizada com delays**  
✅ **Trabalha com dados reais do sistema**

---

**Última atualização:** Janeiro 2024  
**Versão do Simulador:** 3.0






