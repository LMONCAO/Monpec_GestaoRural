# 🎨 DOCUMENTAÇÃO VISUAL - PREENCHIMENTO DOS CARDS

## 📋 ÍNDICE
1. [Estrutura HTML](#estrutura-html)
2. [Estilos CSS](#estilos-css)
3. [JavaScript de Preenchimento](#javascript-de-preenchimento)
4. [Fluxo Completo](#fluxo-completo)
5. [Exemplos Visuais](#exemplos-visuais)

---

## 1. ESTRUTURA HTML

### Card de Identificação do Animal
```html
<!-- Container principal do card -->
<div class="animal-info" id="animalInfo" style="display: none;">
    
    <!-- Cabeçalho do card -->
    <div class="animal-header">
        <div class="animal-id">
            Brinco: <span id="animalBrinco">—</span>
        </div>
        <span class="animal-status" id="animalStatus">Ativo</span>
    </div>
    
    <!-- Detalhes do animal -->
    <div class="animal-details">
        <div class="animal-detail">
            <span>Raça:</span> 
            <span id="animalRaca">—</span>
        </div>
        <div class="animal-detail">
            <span>Idade:</span> 
            <span id="animalIdade">—</span>
        </div>
        <div class="animal-detail">
            <span>Sexo:</span> 
            <span id="animalSexo">—</span>
        </div>
        <div class="animal-detail">
            <span>Última pesagem:</span> 
            <span id="animalUltimoPeso">—</span>
        </div>
        <div class="animal-detail">
            <span>Data Nasc.:</span> 
            <span id="animalNascimento">—</span>
        </div>
        <div class="animal-detail">
            <span>Lote:</span> 
            <span id="animalLote">—</span>
        </div>
    </div>
</div>
```

### Card de Pesagem
```html
<!-- Display de peso -->
<div class="peso-display" id="pesoDisplay">
    <p class="peso-value" id="pesoValue">
        0<span class="peso-unit">kg</span>
    </p>
    <div class="peso-pending-indicator" id="pesoPendingIndicator" style="display: none;">
        <i class="fas fa-microphone"></i>
    </div>
</div>

<!-- Data da pesagem -->
<div class="peso-date">
    <i class="fas fa-calendar-alt"></i> 
    <span id="pesoDate">--/--/---- --:--</span>
</div>
```

---

## 2. ESTILOS CSS

### Estilos do Card de Animal
```css
/* Container principal */
.animal-info {
    display: none;                    /* Inicialmente escondido */
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 15px;
    margin-top: 15px;
    transition: all 0.3s ease;        /* Animação suave */
}

/* Cabeçalho */
.animal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.animal-id {
    font-weight: 600;
    font-size: 1rem;
}

.animal-status {
    background: #4caf50;
    color: white;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
}

/* Detalhes */
.animal-details {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.animal-detail {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    font-size: 0.9rem;
}

.animal-detail span:first-child {
    font-weight: 500;
    color: rgba(255, 255, 255, 0.8);
}

.animal-detail span:last-child {
    font-weight: 600;
    color: white;
}
```

### Estilos do Display de Peso
```css
/* Container do peso */
.peso-display {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
}

/* Estado: Ativo (peso confirmado) */
.peso-display.active {
    background: linear-gradient(135deg, #4caf50, #2e7d32);
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

/* Estado: Pendente (aguardando confirmação) */
.peso-display.pending {
    background: linear-gradient(135deg, #ff9800, #f57c00);
    box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
}

/* Valor do peso */
.peso-value {
    font-size: 3rem;
    font-weight: bold;
    color: white;
    margin: 0;
}

.peso-unit {
    font-size: 1.5rem;
    font-weight: normal;
    opacity: 0.9;
}

/* Data */
.peso-date {
    margin-top: 10px;
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.8);
}
```

---

## 3. JAVASCRIPT DE PREENCHIMENTO

### Função Principal: `atualizarEstadoBrinco()`

```javascript
async function atualizarEstadoBrinco() {
    // 1. Verifica se há brinco digitado
    const temBrinco = brincoInput.value && brincoInput.value.length > 3;
    
    // 2. Habilita/desabilita controles
    const controles = [simularPesoBtn, limparPesoBtn, toggleManualBtn];
    controles.forEach(btn => btn.disabled = !temBrinco);
    manualPesoInput.disabled = !temBrinco;

    if (temBrinco) {
        // 3. Extrai propriedade_id da URL
        const urlMatch = window.location.pathname.match(/propriedade\/(\d+)/);
        const propriedadeId = urlMatch ? urlMatch[1] : null;
        
        if (propriedadeId) {
            try {
                // 4. Busca o animal no backend
                const response = await fetch(
                    `/propriedade/${propriedadeId}/curral/api/identificar/?codigo=${encodeURIComponent(brincoInput.value.trim())}`
                );
                
                if (response.ok) {
                    const data = await response.json();
                    
                    if (data.status === 'animal' && data.dados) {
                        // 5. Armazena no workState
                        workState.animalId = data.dados.id;
                        workState.animalAtual = data.dados;
                        
                        // 6. PREENCHE OS CARDS VISUALMENTE
                        
                        // Mostra o card (estava escondido)
                        animalInfo.style.display = 'block';
                        
                        // Preenche cada campo individualmente
                        animalBrinco.textContent = data.dados.numero_brinco || brincoInput.value;
                        
                        if (animalRaca) {
                            animalRaca.textContent = data.dados.raca || '—';
                        }
                        
                        if (animalSexo) {
                            // Converte F/M para texto
                            const sexoTexto = data.dados.sexo === 'F' ? 'Fêmea' : 
                                            data.dados.sexo === 'M' ? 'Macho' : '—';
                            animalSexo.textContent = sexoTexto;
                        }
                        
                        if (animalNascimento) {
                            animalNascimento.textContent = data.dados.data_nascimento || '—';
                        }
                        
                        // Último peso (com formatação)
                        const ultimoPeso = data.dados.peso_atual || 
                                         data.dados.ultimo_peso || 
                                         data.dados.pesagem_atual?.peso;
                        
                        if (ultimoPeso) {
                            animalUltimoPeso.textContent = `${parseFloat(ultimoPeso).toFixed(1)} kg`;
                        } else {
                            animalUltimoPeso.textContent = '—';
                        }
                        
                        // Feedback de voz (se ativado)
                        if (workState.voicePrompts) {
                            falarMensagem('Informar pesagem');
                        }
                        
                        return;
                    }
                }
            } catch (error) {
                console.error('Erro ao buscar animal:', error);
            }
        }
        
        // Fallback: mostra informações básicas mesmo sem backend
        animalInfo.style.display = 'block';
        animalBrinco.textContent = brincoInput.value;
        animalUltimoPeso.textContent = '—';
        
    } else {
        // Esconde o card se não tem brinco
        animalInfo.style.display = 'none';
        atualizarPeso(0);
        workState.animalId = null;
        workState.animalAtual = null;
    }
}
```

### Função de Atualização de Peso: `atualizarPeso()`

```javascript
function atualizarPeso(peso, pendente = false) {
    console.log('⚖️ atualizarPeso chamado:', { peso, pendente });
    
    // 1. Atualiza o workState
    workState.pesoAtual = peso;
    
    // 2. PREENCHE O DISPLAY VISUALMENTE
    pesoValue.innerHTML = peso.toFixed(1) + '<span class="peso-unit">kg</span>';
    
    // 3. Aplica estados visuais
    if (peso > 0) {
        if (pendente) {
            // Estado: Pendente (laranja)
            pesoDisplay.classList.remove('active');
            pesoDisplay.classList.add('pending');
            pesoPendingIndicator.style.display = 'flex';
        } else {
            // Estado: Ativo (verde)
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
        // Estado: Vazio
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

## 4. FLUXO COMPLETO

### Sequência de Eventos:

```
1. Usuário digita brinco
   ↓
2. Event listener dispara: brincoInput.addEventListener('input', atualizarEstadoBrinco)
   ↓
3. atualizarEstadoBrinco() é chamada
   ↓
4. Faz requisição: fetch('/propriedade/2/curral/api/identificar/?codigo=...')
   ↓
5. Recebe resposta JSON com dados do animal
   ↓
6. Preenche workState: workState.animalId = data.dados.id
   ↓
7. PREENCHE CARDS VISUALMENTE:
   - animalInfo.style.display = 'block'        (mostra card)
   - animalBrinco.textContent = "105500..."    (preenche brinco)
   - animalRaca.textContent = "NELORE"        (preenche raça)
   - animalSexo.textContent = "Fêmea"          (preenche sexo)
   - animalUltimoPeso.textContent = "380.0 kg" (preenche peso)
   ↓
8. Card aparece na tela com todas as informações
```

---

## 5. EXEMPLOS VISUAIS

### Estado Inicial (Antes de digitar brinco):
```
┌─────────────────────────────────────┐
│  IDENTIFICAÇÃO DO ANIMAL            │
│  [Campo brinco vazio]               │
│                                     │
│  [Card escondido - display: none]   │
└─────────────────────────────────────┘
```

### Estado Após Digitar Brinco:
```
┌─────────────────────────────────────┐
│  IDENTIFICAÇÃO DO ANIMAL            │
│  [105500376195129]                  │
│                                     │
│  ┌─────────────────────────────┐  │
│  │ Brinco: 105500376195129  [Ativo]│
│  ├─────────────────────────────┤  │
│  │ Raça:        NELORE         │  │
│  │ Idade:       8 meses         │  │
│  │ Sexo:        Fêmea           │  │
│  │ Última pesagem: 380.0 kg     │  │
│  │ Data Nasc.:  16/03/2025      │  │
│  │ Lote:        Lote A          │  │
│  └─────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Display de Peso - Estado Vazio:
```
┌─────────────────┐
│      0 kg       │
│  --/--/---- --:--│
└─────────────────┘
```

### Display de Peso - Estado Ativo (Verde):
```
┌─────────────────┐
│   395.0 kg     │  ← Verde (peso confirmado)
│  20/11/2025 04:30│
└─────────────────┘
```

### Display de Peso - Estado Pendente (Laranja):
```
┌─────────────────┐
│   395.0 kg     │  ← Laranja (aguardando confirmação)
│   [🎤]          │
└─────────────────┘
```

---

## 🔍 VERIFICAÇÃO NO CONSOLE

### Verificar se o card está visível:
```javascript
document.getElementById('animalInfo').style.display
// Retorna: "block" (visível) ou "none" (escondido)
```

### Verificar conteúdo dos campos:
```javascript
// Brinco
document.getElementById('animalBrinco').textContent
// Retorna: "105500376195129" ou "—"

// Raça
document.getElementById('animalRaca').textContent
// Retorna: "NELORE" ou "—"

// Peso
document.getElementById('animalUltimoPeso').textContent
// Retorna: "380.0 kg" ou "—"
```

### Verificar estado do peso:
```javascript
// Valor do peso
document.getElementById('pesoValue').textContent
// Retorna: "395.0kg"

// Classes aplicadas
document.getElementById('pesoDisplay').classList
// Retorna: ["peso-display", "active"] ou ["peso-display", "pending"]
```

---

## 📊 RESUMO TÉCNICO

### Métodos de Preenchimento:
1. **textContent** → Para texto simples (mais seguro)
2. **innerHTML** → Para HTML (usado no peso com `<span>`)
3. **style.display** → Para mostrar/esconder elementos
4. **classList.add/remove** → Para estados visuais (active/pending)

### Elementos Principais:
- **animalInfo** → Container do card (mostra/esconde)
- **animalBrinco, animalRaca, etc.** → Campos individuais (preenche texto)
- **pesoValue** → Display de peso (preenche HTML)
- **pesoDisplay** → Container do peso (aplica classes CSS)

### Estados Visuais:
- **display: none** → Card escondido
- **display: block** → Card visível
- **class: active** → Peso confirmado (verde)
- **class: pending** → Peso pendente (laranja)

---

## ✅ CONCLUSÃO

Os cards são preenchidos através de:
1. **Busca de dados** via API (`/curral/api/identificar/`)
2. **Atualização do DOM** via JavaScript (`textContent`, `innerHTML`)
3. **Aplicação de estilos** via CSS (`display`, `classList`)
4. **Feedback visual** através de cores e animações

**Tudo acontece na função `atualizarEstadoBrinco()` quando o brinco é digitado!**




