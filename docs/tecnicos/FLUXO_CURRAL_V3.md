# Fluxo da Página Curral Inteligente 3.0

## Visão Geral

O **Curral Inteligente 3.0** é uma aplicação web para gerenciamento de manejo bovino em tempo real. A página permite identificar animais, registrar pesagens, cadastrar manejos e gerenciar sessões de trabalho no curral.

---

## 1. INÍCIO DO FLUXO

### 1.1. Carregamento da Página
- **Rota**: `/propriedade/<id>/curral/v3/`
- **View**: `curral_dashboard_v3()` em `gestao_rural/views_curral.py`
- **Template**: `templates/gestao_rural/curral_dashboard_v3.html`

### 1.2. Inicialização
- Verifica se existe uma **sessão ativa** (CurralSessao com status 'ABERTA')
- Carrega estatísticas gerais (total de animais, pesagens do dia, manejos do dia)
- Configura URLs das APIs necessárias
- Carrega catálogo de manejos disponíveis

---

## 2. IDENTIFICAÇÃO DO ANIMAL

### 2.1. Entrada do Código
O usuário pode inserir o código do animal de três formas:
- **SISBOV** (ID principal - 15 dígitos)
- **Número de Manejo** (6 dígitos)
- **Brinco/Botton RFID - CHIP** (código eletrônico)

**Campo**: `brincoInputV3` (input de busca)

### 2.2. Busca do Animal
**Função**: `buscarBrincoV3()`

**Fluxo**:
1. Captura o código do campo de entrada
2. Limpa o código (remove espaços, traços, pontos)
3. Valida se o código não está vazio
4. Faz requisição para a API:
   - **URL**: `/propriedade/<id>/curral/api/identificar/`
   - **Métodos**: Tenta GET primeiro, se falhar tenta POST
   - **Payload**: `{ codigo: brinco }`
   - **View**: `curral_identificar_codigo()` em `views_curral.py`

### 2.3. Respostas Possíveis da API

#### **A) Animal Encontrado** (`status: 'animal'`)
- Preenche os campos de identificação:
  - Número de Manejo
  - SISBOV
  - Brinco/Botton RFID
  - Raça / Sexo (editáveis)
  - Data de Nascimento (editável, calcula idade automaticamente)
  - Último Peso
  - Categoria (editável)
  - Pasto/Lote (editável)
- Habilita o campo de peso (`pesoValorV3`)
- Habilita botões de gravação
- Armazena dados em `animalAtualV3` e `brincoAtualV3`

#### **B) Brinco em Estoque** (`status: 'estoque'`)
- Abre modal de cadastro de novo animal
- Permite preencher dados do animal
- Após cadastro, retorna ao fluxo normal

#### **C) Animal Não Encontrado**
- Mostra mensagem de erro
- Sugere cadastrar novo animal
- Permite tentar novamente com outro código

### 2.4. Atualização Automática de Dados
Quando o usuário edita campos (Raça, Sexo, Nascimento, etc.), os dados são salvos automaticamente via:
- **URL**: `/propriedade/<id>/curral/api/animal/atualizar/`
- **Método**: POST
- **Payload**: `{ animal_id, campo: valor }`

---

## 3. REGISTRO DE PESAGEM

### 3.1. Entrada do Peso
O usuário pode inserir o peso de duas formas:
- **Manual**: Digita no campo `pesoValorV3`
- **Automático**: Recebe da balança conectada via API

### 3.2. Integração com Balança
**Endpoint**: `/propriedade/<id>/curral/api/balanca/peso/`
- Recebe peso automaticamente quando a balança está conectada
- Preenche o campo de peso automaticamente

### 3.3. Gravação da Pesagem
**Função**: `gravarPesagemV3()`

**Fluxo**:
1. Valida se há animal identificado
2. Valida se o peso foi informado
3. Prepara payload:
   ```json
   {
     "animal_id": animal.id,
     "brinco": codigo,
     "peso": peso
   }
   ```
4. Envia para API:
   - **URL**: `/propriedade/<id>/curral/api/pesagem/`
   - **Método**: POST
   - **View**: `curral_salvar_pesagem_api()` em `views_curral.py`

### 3.4. Pós-Gravação

#### **A) Apartação Automática** (se configurado)
- Se o tipo de manejo for `PESAGEM_APARTE` e houver configuração de apartações:
  1. Calcula a faixa de peso
  2. Mostra popup de apartação com:
     - Nome do animal
     - Peso registrado
     - Faixa de apartação (ex: "200 kg a 250 kg")
     - Timer de 5 segundos
  3. Após timer, continua o fluxo

#### **B) Atualização de Informações**
Após gravar com sucesso:
- Atualiza campo "Peso Registrado"
- Calcula e exibe:
  - Data da última pesagem
  - Dias desde a última pesagem
  - Ganho total (diferença do peso anterior)
  - Ganho diário médio
- Atualiza gráfico de eficiência de ganho de peso
- Adiciona animal à tabela de animais processados
- Atualiza estatísticas da sessão

### 3.5. Limpeza e Preparação para Próximo Animal
- Limpa apenas o campo de peso (mantém animal identificado)
- Foca no campo de busca para facilitar próxima entrada
- **NÃO** busca automaticamente o próximo brinco (usuário controla)

---

## 4. REGISTRO DE MANEJOS

### 4.1. Seleção de Manejos
O usuário pode selecionar manejos adicionais:
- Vacinação
- Tratamento Sanitário
- Reprodução
- Outros manejos do catálogo

### 4.2. Gravação de Manejos
**Função**: `finalizarEGravarV3()`

**Fluxo**:
1. Verifica se há pesagem ou manejos para gravar
2. Se houver pesagem, grava primeiro
3. Grava manejos selecionados:
   - **URL**: `/propriedade/<id>/curral/api/manejos/registrar/`
   - **Método**: POST
   - **Payload**:
     ```json
     {
       "tipo_fluxo": "animal",
       "codigo": codigo,
       "animal_id": animal.id,
       "manejos": [
         {
           "tipo": "VACINACAO",
           "dados": { ... }
         }
       ]
     }
     ```

---

## 5. GESTÃO DE SESSÃO

### 5.1. Sessão Ativa
A página sempre verifica se há uma sessão ativa:
- **Status**: 'ABERTA'
- **Informações exibidas**:
  - Nome da sessão
  - Data/hora de início
  - Total de eventos
  - Animais processados
  - Total de pesagens

### 5.2. Criar Nova Sessão
**Endpoint**: `/propriedade/<id>/curral/api/sessao/criar/`
- Permite iniciar uma nova sessão de trabalho
- Define nome, tipo de trabalho, pasto/lote

### 5.3. Encerrar Sessão
**Endpoint**: `/propriedade/<id>/curral/api/sessao/encerrar/`
- Finaliza a sessão atual
- Gera relatório final
- Salva estatísticas

### 5.4. Atualização de Estatísticas
As estatísticas são atualizadas automaticamente:
- Total de animais processados
- Total de pesagens
- Média de peso
- Ganho médio diário
- Por categoria

---

## 6. FUNCIONALIDADES AUXILIARES

### 6.1. Busca da Mãe (Opcional)
- Permite buscar informações da mãe do animal
- Mostra informações de IATF se disponível
- Exibe touro utilizado na inseminação

### 6.2. Simulador
- **Botão**: "► INICIAR SIMULADOR"
- Permite simular pesagens em massa
- Útil para testes e demonstrações

### 6.3. Relatórios
- **Botão**: "RELATÓRIOS"
- Gera relatórios da sessão atual
- Exporta dados para análise

---

## 7. FLUXO COMPLETO RESUMIDO

```
1. CARREGAR PÁGINA
   ├─ Verificar sessão ativa
   ├─ Carregar estatísticas
   └─ Inicializar componentes

2. IDENTIFICAR ANIMAL
   ├─ Usuário digita código (SISBOV/Manejo/RFID)
   ├─ Clica em "Buscar" ou pressiona Enter
   ├─ API busca animal
   ├─ Se encontrado: preenche dados
   └─ Se não encontrado: oferece cadastro

3. REGISTRAR PESAGEM
   ├─ Usuário insere peso (manual ou balança)
   ├─ Clica em "Gravar"
   ├─ API salva pesagem
   ├─ Se apartação: mostra popup
   ├─ Calcula ganhos e estatísticas
   └─ Atualiza interface

4. REGISTRAR MANEJOS (Opcional)
   ├─ Usuário seleciona manejos adicionais
   └─ Clica em "Finalizar e Gravar"

5. PRÓXIMO ANIMAL
   ├─ Limpa campo de peso
   ├─ Mantém animal identificado
   └─ Retorna ao passo 2
```

---

## 8. APIs PRINCIPAIS

| Endpoint | Método | Função |
|----------|--------|--------|
| `/propriedade/<id>/curral/api/identificar/` | GET/POST | Identifica animal por código |
| `/propriedade/<id>/curral/api/animal/atualizar/` | POST | Atualiza dados do animal |
| `/propriedade/<id>/curral/api/pesagem/` | POST | Salva pesagem |
| `/propriedade/<id>/curral/api/balanca/peso/` | POST | Recebe peso da balança |
| `/propriedade/<id>/curral/api/manejos/registrar/` | POST | Registra manejos |
| `/propriedade/<id>/curral/api/sessao/criar/` | POST | Cria nova sessão |
| `/propriedade/<id>/curral/api/sessao/encerrar/` | POST | Encerra sessão |
| `/propriedade/<id>/curral/api/stats/` | GET | Obtém estatísticas gerais |
| `/propriedade/<id>/curral/api/sessao/stats/` | GET | Obtém estatísticas da sessão |

---

## 9. VARIÁVEIS JAVASCRIPT IMPORTANTES

- `animalAtualV3`: Objeto com dados do animal atual
- `brincoAtualV3`: Código do animal atual (SISBOV/Manejo/RFID)
- `animaisRegistrados`: Array com animais já processados na sessão
- `manejosSelecionadosV3`: Array com manejos selecionados para gravar
- `propriedadeId`: ID da propriedade atual
- `identificarUrl`: URL da API de identificação
- `registrarUrl`: URL da API de registro
- `sessaoAtiva`: Dados da sessão ativa

---

## 10. OBSERVAÇÕES IMPORTANTES

1. **Campo de Busca**: Nunca é limpo automaticamente após gravar pesagem, apenas recebe foco
2. **Campo de Peso**: É limpo após gravar pesagem
3. **Apartação**: Só acontece se configurado no tipo de manejo
4. **Sessão**: Deve estar ativa para registrar eventos
5. **Offline**: A página suporta modo offline com sincronização posterior
6. **Validações**: Todos os campos são validados antes de enviar para API

---

## 11. PRÓXIMOS PASSOS PARA IMPLEMENTAÇÃO

Se precisar modificar ou estender o fluxo:

1. **Identificação**: Edite `buscarBrincoV3()` no HTML
2. **Pesagem**: Edite `gravarPesagemV3()` no HTML
3. **API Backend**: Edite `views_curral.py`
4. **Validações**: Adicione validações nas funções JavaScript
5. **Novos Campos**: Adicione campos no HTML e atualize as funções de busca/gravação

---

**Última atualização**: Baseado no código atual do sistema Monpec_GestaoRural

