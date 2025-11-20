# ⚖️ DOCUMENTAÇÃO VISUAL - SISTEMA DE PESAGEM

## 📋 ÍNDICE
1. [Estrutura Visual da Pesagem](#estrutura-visual)
2. [Estados Visuais do Peso](#estados-visuais)
3. [Como o Peso é Preenchido](#como-preenchido)
4. [Fluxo Completo](#fluxo-completo)
5. [Exemplos Visuais Detalhados](#exemplos-visuais)

---

## 1. ESTRUTURA VISUAL DA PESAGEM

### HTML do Display de Peso:
```html
<!-- Container principal -->
<div class="peso-section">
    
    <!-- Display do peso -->
    <div class="peso-display" id="pesoDisplay">
        <p class="peso-value" id="pesoValue">
            0<span class="peso-unit">kg</span>
        </p>
        <div class="peso-pending-indicator" id="pesoPendingIndicator" style="display: none;">
            <i class="fas fa-microphone"></i>
        </div>
    </div>
    
    <!-- Controles de peso -->
    <div class="peso-controls">
        <button id="simularPesoBtn">Simular</button>
        <button id="limparPesoBtn">Limpar</button>
        <button id="toggleManualBtn">Manual</button>
    </div>
    
    <!-- Input manual (inicialmente escondido) -->
    <div class="peso-manual-input" id="pesoManualInput">
        <input type="number" id="manualPesoInput" placeholder="Digite o peso">
        <button id="confirmarPesoBtn">Confirmar peso</button>
    </div>
    
    <!-- Data da pesagem -->
    <div class="peso-date">
        <i class="fas fa-calendar-alt"></i>
        <span id="pesoDate">--/--/---- --:--</span>
    </div>
</div>
```

---

## 2. ESTADOS VISUAIS DO PESO

### Estado 1: VAZIO (Inicial)
```
┌─────────────────────────┐
│                         │
│        0 kg            │  ← Cinza/Transparente
│                         │
│  --/--/---- --:--      │
│                         │
└─────────────────────────┘

CSS: .peso-display (sem classes)
Cor: rgba(255, 255, 255, 0.1)
```

### Estado 2: PENDENTE (Aguardando confirmação)
```
┌─────────────────────────┐
│                         │
│      395.0 kg          │  ← LARANJA
│        [🎤]            │  ← Indicador de voz
│                         │
│  20/11/2025 04:30      │
│                         │
└─────────────────────────┘

CSS: .peso-display.pending
Cor: linear-gradient(135deg, #ff9800, #f57c00)
```

### Estado 3: ATIVO (Peso confirmado)
```
┌─────────────────────────┐
│                         │
│      395.0 kg          │  ← VERDE
│                         │
│  20/11/2025 04:30      │
│                         │
└─────────────────────────┘

CSS: .peso-display.active
Cor: linear-gradient(135deg, #4caf50, #2e7d32)
```

---

## 3. COMO O PESO É PREENCHIDO

### Função Principal: `atualizarPeso()`

```javascript
function atualizarPeso(peso, pendente = false) {
    console.log('⚖️ atualizarPeso chamado:', { peso, pendente });
    
    // 1. ATUALIZA O WORKSTATE (dados internos)
    workState.pesoAtual = peso;
    
    // 2. PREENCHE O DISPLAY VISUALMENTE
    pesoValue.innerHTML = peso.toFixed(1) + '<span class="peso-unit">kg</span>';
    
    // 3. APLICA ESTADOS VISUAIS
    if (peso > 0) {
        if (pendente) {
            // ESTADO PENDENTE (LARANJA)
            pesoDisplay.classList.remove('active');
            pesoDisplay.classList.add('pending');
            pesoPendingIndicator.style.display = 'flex';
        } else {
            // ESTADO ATIVO (VERDE)
            pesoDisplay.classList.remove('pending');
            pesoDisplay.classList.add('active');
            pesoPendingIndicator.style.display = 'none';
            aguardandoConfirmacao = false;
            
            // Calcula aparte e ganhos
            calcularAparteEGanhos(peso);
            
            // Atualiza data
            atualizarDataPesagem();
        }
    } else {
        // ESTADO VAZIO
        pesoDisplay.classList.remove('active', 'pending');
        pesoPendingIndicator.style.display = 'none';
    }
}
```

### Função de Atualização de Data: `atualizarDataPesagem()`

```javascript
function atualizarDataPesagem() {
    const agora = new Date();
    const dia = String(agora.getDate()).padStart(2, '0');
    const mes = String(agora.getMonth() + 1).padStart(2, '0');
    const ano = agora.getFullYear();
    const hora = String(agora.getHours()).padStart(2, '0');
    const minuto = String(agora.getMinutes()).padStart(2, '0');
    
    const dateString = `${dia}/${mes}/${ano} ${hora}:${minuto}`;
    pesoDate.textContent = dateString;
}
```

---

## 4. FLUXO COMPLETO DE PESAGEM

### Cenário 1: Peso Digitado Manualmente

```
1. Usuário clica em "Manual"
   ↓
2. Input manual aparece
   ↓
3. Usuário digita: 395
   ↓
4. Usuário clica em "Confirmar peso"
   ↓
5. confirmarPesoManual() é chamada
   ↓
6. atualizarPeso(395) é chamada
   ↓
7. Display muda para VERDE (ativo)
   ↓
8. Mostra: "395.0 kg" + data/hora
```

### Cenário 2: Peso Simulado

```
1. Usuário clica em "Simular"
   ↓
2. simularPeso() gera peso aleatório
   ↓
3. atualizarPeso(pesoAleatorio) é chamada
   ↓
4. Display muda para VERDE (ativo)
   ↓
5. Mostra peso + data/hora
```

### Cenário 3: Peso por Voz

```
1. Usuário clica no microfone
   ↓
2. Sistema escuta o peso falado
   ↓
3. atualizarPeso(peso, true) é chamada (pendente=true)
   ↓
4. Display muda para LARANJA (pendente)
   ↓
5. Mostra: "395.0 kg" + ícone de microfone
   ↓
6. Usuário confirma: "OK"
   ↓
7. atualizarPeso(peso, false) é chamada
   ↓
8. Display muda para VERDE (ativo)
```

### Cenário 4: Peso da Balança

```
1. Sistema detecta peso da balança
   ↓
2. atualizarPeso(pesoBalança) é chamada
   ↓
3. Display muda para VERDE (ativo)
   ↓
4. Mostra peso + data/hora automaticamente
```

---

## 5. EXEMPLOS VISUAIS DETALHADOS

### ANTES: Estado Inicial (Sem peso)

```
┌─────────────────────────────────────┐
│  REGISTRO DE PESAGEM                │
│                                     │
│  ┌─────────────────────────────┐  │
│  │                             │  │
│  │         0 kg                │  │  ← Cinza
│  │                             │  │
│  └─────────────────────────────┘  │
│                                     │
│  [Simular] [Limpar] [Manual]       │
│                                     │
│  📅 --/--/---- --:--               │
└─────────────────────────────────────┘

Estado: Vazio
workState.pesoAtual: 0
```

### DURANTE: Digitando Peso Manualmente

```
┌─────────────────────────────────────┐
│  REGISTRO DE PESAGEM                │
│                                     │
│  ┌─────────────────────────────┐  │
│  │                             │  │
│  │         0 kg                │  │  ← Ainda cinza
│  │                             │  │
│  └─────────────────────────────┘  │
│                                     │
│  ┌─────────────────────────────┐  │
│  │ [395]  [🎤]                 │  │  ← Input manual aberto
│  │ [Confirmar peso]             │  │
│  └─────────────────────────────┘  │
│                                     │
│  📅 --/--/---- --:--               │
└─────────────────────────────────────┘

Estado: Digitando
workState.pesoAtual: 0 (ainda não confirmado)
```

### DEPOIS: Peso Confirmado

```
┌─────────────────────────────────────┐
│  REGISTRO DE PESAGEM                │
│                                     │
│  ┌─────────────────────────────┐  │
│  │                             │  │
│  │      395.0 kg              │  │  ← VERDE (ativo)
│  │                             │  │
│  └─────────────────────────────┘  │
│                                     │
│  [Simular] [Limpar] [Manual]       │
│                                     │
│  📅 20/11/2025 04:30               │
└─────────────────────────────────────┘

Estado: Ativo
workState.pesoAtual: 395
CSS: .peso-display.active
```

### PENDENTE: Aguardando Confirmação (Voz)

```
┌─────────────────────────────────────┐
│  REGISTRO DE PESAGEM                │
│                                     │
│  ┌─────────────────────────────┐  │
│  │                             │  │
│  │      395.0 kg              │  │  ← LARANJA (pendente)
│  │        [🎤]                 │  │  ← Indicador de voz
│  │                             │  │
│  └─────────────────────────────┘  │
│                                     │
│  Diga "OK" para gravar...          │
│                                     │
│  📅 20/11/2025 04:30               │
└─────────────────────────────────────┘

Estado: Pendente
workState.pesoAtual: 395
CSS: .peso-display.pending
```

---

## 6. ESTILOS CSS APLICADOS

### Estado Vazio:
```css
.peso-display {
    background: rgba(255, 255, 255, 0.1);
    /* Sem classes adicionais */
}
```

### Estado Pendente (Laranja):
```css
.peso-display.pending {
    background: linear-gradient(135deg, #ff9800, #f57c00);
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
    animation: pulse 2s infinite;
}

.peso-pending-indicator {
    display: flex;
    color: white;
    font-size: 1.5rem;
}
```

### Estado Ativo (Verde):
```css
.peso-display.active {
    background: linear-gradient(135deg, #4caf50, #2e7d32);
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    transform: scale(1.02);
    transition: all 0.3s ease;
}
```

### Valor do Peso:
```css
.peso-value {
    font-size: 3rem;
    font-weight: bold;
    color: white;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.peso-unit {
    font-size: 1.5rem;
    font-weight: normal;
    opacity: 0.9;
}
```

---

## 7. VERIFICAÇÃO NO CONSOLE

### Verificar valor atual do peso:
```javascript
// Valor no display
document.getElementById('pesoValue').textContent
// Retorna: "395.0kg"

// Valor no workState
workState.pesoAtual
// Retorna: 395

// Data da pesagem
document.getElementById('pesoDate').textContent
// Retorna: "20/11/2025 04:30"
```

### Verificar estado visual:
```javascript
// Classes aplicadas
document.getElementById('pesoDisplay').classList
// Retorna: ["peso-display", "active"] ou ["peso-display", "pending"]

// Verificar se está pendente
document.getElementById('pesoDisplay').classList.contains('pending')
// Retorna: true ou false

// Verificar se está ativo
document.getElementById('pesoDisplay').classList.contains('active')
// Retorna: true ou false
```

### Verificar indicador de voz:
```javascript
// Se o indicador está visível
document.getElementById('pesoPendingIndicator').style.display
// Retorna: "flex" (visível) ou "none" (escondido)
```

---

## 8. FLUXO DE SALVAMENTO

### Quando o usuário clica em "Gravar":

```
1. Botão "Gravar" é clicado
   ↓
2. salvarPesagemBackend() é chamada
   ↓
3. Validações:
   - Verifica se há brinco: ✅
   - Verifica se há peso: ✅ (workState.pesoAtual > 0)
   ↓
4. Prepara dados:
   {
     animal_id: workState.animalId,
     peso: workState.pesoAtual,
     data: new Date().toISOString()
   }
   ↓
5. Envia para API:
   POST /propriedade/2/curral/api/pesagem/
   ↓
6. Se sucesso:
   - Mostra mensagem: "Pesagem salva com sucesso!"
   - Atualiza animalUltimoPeso: "395.0 kg"
   - Botão muda para: "Salvo!" (verde)
   - Limpa o peso (se auto-próximo ativado)
   ↓
7. Se erro:
   - Mostra alerta com mensagem de erro
```

---

## 9. EXEMPLO COMPLETO: DO ZERO AO SALVAMENTO

### Passo 1: Estado Inicial
```
Brinco: [           ]  ← Vazio
Peso:   0 kg         ← Cinza
Card:   [Escondido]
```

### Passo 2: Digita Brinco
```
Brinco: [105500376195129]  ← Preenchido
Peso:   0 kg               ← Ainda cinza
Card:   ┌─────────────────┐
        │ Brinco: 105500...│
        │ Raça: NELORE     │
        │ Peso: 380.0 kg   │  ← Último peso
        └─────────────────┘
```

### Passo 3: Digita Peso
```
Brinco: [105500376195129]
Peso:   395.0 kg      ← VERDE (ativo)
Card:   [Mesmo de antes]
```

### Passo 4: Clica em "Gravar"
```
Brinco: [105500376195129]
Peso:   395.0 kg      ← VERDE
Card:   ┌─────────────────┐
        │ Brinco: 105500...│
        │ Raça: NELORE     │
        │ Peso: 395.0 kg   │  ← ATUALIZADO!
        └─────────────────┘
Botão:  [Salvo!]      ← Verde, temporário
```

### Passo 5: Após Salvar (se auto-próximo)
```
Brinco: [           ]  ← Limpo
Peso:   0 kg         ← Cinza novamente
Card:   [Escondido]
```

---

## 10. RESUMO TÉCNICO

### Elementos Principais:
- **pesoValue** → Display do valor (ex: "395.0 kg")
- **pesoDisplay** → Container (aplica classes: active/pending)
- **pesoDate** → Data/hora da pesagem
- **pesoPendingIndicator** → Ícone de microfone (quando pendente)

### Métodos de Preenchimento:
1. **innerHTML** → Para o valor do peso (com `<span>`)
2. **textContent** → Para a data
3. **classList.add/remove** → Para estados visuais
4. **style.display** → Para mostrar/esconder indicador

### Estados:
- **Vazio** → `peso = 0`, sem classes
- **Pendente** → `class: pending`, cor laranja
- **Ativo** → `class: active`, cor verde

### Funções Principais:
- `atualizarPeso(peso, pendente)` → Atualiza display
- `atualizarDataPesagem()` → Atualiza data/hora
- `salvarPesagemBackend()` → Salva no backend

---

## ✅ CONCLUSÃO

O sistema de pesagem funciona através de:
1. **Atualização do DOM** → `pesoValue.innerHTML`
2. **Aplicação de classes CSS** → `active` ou `pending`
3. **Feedback visual** → Cores verde/laranja
4. **Armazenamento interno** → `workState.pesoAtual`
5. **Salvamento no backend** → API `/curral/api/pesagem/`

**Tudo acontece na função `atualizarPeso()` quando o peso é definido!**




