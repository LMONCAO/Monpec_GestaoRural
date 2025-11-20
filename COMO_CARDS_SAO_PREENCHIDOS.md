# 📊 COMO OS CARDS SÃO PREENCHIDOS VISUALMENTE

## 🎨 ESTRUTURA VISUAL DOS CARDS

### 1. **CARD DE IDENTIFICAÇÃO DO ANIMAL**

#### HTML (Estrutura):
```html
<div class="animal-info" id="animalInfo">
    <div class="animal-header">
        <div class="animal-id">Brinco: <span id="animalBrinco">—</span></div>
        <span class="animal-status" id="animalStatus">Ativo</span>
    </div>
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

#### JavaScript (Preenchimento):
```javascript
// Função que preenche os cards quando um brinco é digitado
async function atualizarEstadoBrinco() {
    const temBrinco = brincoInput.value && brincoInput.value.length > 3;
    
    if (temBrinco) {
        // 1. Busca o animal no backend
        const response = await fetch(`/propriedade/${propriedadeId}/curral/api/identificar/?codigo=${brincoInput.value}`);
        const data = await response.json();
        
        if (data.status === 'animal' && data.dados) {
            // 2. Armazena no workState
            workState.animalId = data.dados.id;
            workState.animalAtual = data.dados;
            
            // 3. PREENCHE OS CARDS VISUALMENTE:
            
            // Mostra o card (estava escondido)
            animalInfo.style.display = 'block';
            
            // Preenche cada campo:
            animalBrinco.textContent = data.dados.numero_brinco || brincoInput.value;
            animalRaca.textContent = data.dados.raca || '—';
            animalSexo.textContent = data.dados.sexo || '—';
            animalNascimento.textContent = data.dados.data_nascimento || '—';
            
            // Último peso (formatação especial)
            const ultimoPeso = data.dados.peso_atual || data.dados.ultimo_peso;
            if (ultimoPeso) {
                animalUltimoPeso.textContent = `${parseFloat(ultimoPeso).toFixed(1)} kg`;
            } else {
                animalUltimoPeso.textContent = '—';
            }
        }
    } else {
        // Esconde o card se não tem brinco
        animalInfo.style.display = 'none';
    }
}
```

---

### 2. **CARD DE PESAGEM**

#### HTML (Estrutura):
```html
<div class="peso-section">
    <div class="peso-display" id="pesoDisplay">
        <p class="peso-value" id="pesoValue">0<span class="peso-unit">kg</span></p>
    </div>
    <div class="peso-date">
        <i class="fas fa-calendar-alt"></i> 
        <span id="pesoDate">--/--/---- --:--</span>
    </div>
</div>
```

#### JavaScript (Preenchimento):
```javascript
// Função que atualiza o display de peso
function atualizarPeso(peso, pendente = false) {
    // Atualiza o workState
    workState.pesoAtual = peso;
    
    // PREENCHE VISUALMENTE:
    pesoValue.innerHTML = peso.toFixed(1) + '<span class="peso-unit">kg</span>';
    
    // Atualiza a data
    atualizarDataPesagem();
    
    // Muda o estilo visual (ativo/pendente)
    if (peso > 0) {
        if (pendente) {
            pesoDisplay.classList.add('pending');
        } else {
            pesoDisplay.classList.add('active');
        }
    }
}
```

---

## 🔄 FLUXO COMPLETO DE PREENCHIMENTO

### Passo 1: Usuário digita o brinco
```javascript
// Event listener no campo brinco
brincoInput.addEventListener('input', atualizarEstadoBrinco);
```

### Passo 2: Sistema busca o animal
```javascript
// Faz requisição para API
fetch(`/propriedade/${propriedadeId}/curral/api/identificar/?codigo=${brinco}`)
```

### Passo 3: Recebe os dados
```json
{
    "status": "animal",
    "dados": {
        "id": 11,
        "numero_brinco": "105500376195129",
        "raca": "NELORE",
        "sexo": "F",
        "data_nascimento": "16/03/2025",
        "peso_atual": 380.0
    }
}
```

### Passo 4: Preenche os cards
```javascript
// Para cada campo do card:
animalBrinco.textContent = "105500376195129";      // ✅ Preenche
animalRaca.textContent = "NELORE";                  // ✅ Preenche
animalSexo.textContent = "F";                      // ✅ Preenche
animalNascimento.textContent = "16/03/2025";        // ✅ Preenche
animalUltimoPeso.textContent = "380.0 kg";          // ✅ Preenche
```

### Passo 5: Mostra o card
```javascript
animalInfo.style.display = 'block';  // Torna visível
```

---

## 🎨 ESTILOS CSS APLICADOS

### Card de Animal:
```css
.animal-info {
    display: none;  /* Inicialmente escondido */
    background: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 15px;
    margin-top: 15px;
}

.animal-detail {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Display de Peso:
```css
.peso-value {
    font-size: 3rem;
    font-weight: bold;
    color: white;
}

.peso-display.active {
    background: linear-gradient(135deg, #4caf50, #2e7d32);
}

.peso-display.pending {
    background: linear-gradient(135deg, #ff9800, #f57c00);
}
```

---

## 📝 ELEMENTOS QUE SÃO PREENCHIDOS

### ✅ Campos do Card de Animal:
1. **animalBrinco** → `textContent = "105500376195129"`
2. **animalRaca** → `textContent = "NELORE"`
3. **animalSexo** → `textContent = "F"` ou `"M"`
4. **animalNascimento** → `textContent = "16/03/2025"`
5. **animalUltimoPeso** → `textContent = "380.0 kg"`
6. **animalIdade** → Calculado automaticamente
7. **animalLote** → Nome do lote atual

### ✅ Display de Peso:
1. **pesoValue** → `innerHTML = "395.0<span>kg</span>"`
2. **pesoDate** → `textContent = "20/11/2025 04:30"`

---

## 🔍 COMO VERIFICAR SE ESTÁ FUNCIONANDO

### No Console (F12):
```javascript
// Ver se o card está visível
document.getElementById('animalInfo').style.display
// Deve retornar: "block" (se animal identificado) ou "none" (se não)

// Ver o conteúdo dos campos
document.getElementById('animalBrinco').textContent
document.getElementById('animalRaca').textContent
document.getElementById('animalUltimoPeso').textContent

// Ver o peso atual
document.getElementById('pesoValue').textContent
```

---

## 🐛 PROBLEMAS COMUNS

### ❌ Card não aparece:
- **Causa**: `animalInfo.style.display` está como `'none'`
- **Solução**: Verificar se `atualizarEstadoBrinco()` está sendo chamada

### ❌ Campos ficam com "—":
- **Causa**: API não retornou os dados ou dados estão vazios
- **Solução**: Verificar resposta da API no console

### ❌ Peso não atualiza:
- **Causa**: Função `atualizarPeso()` não está sendo chamada
- **Solução**: Verificar se o evento está disparando

---

## 📊 RESUMO

1. **HTML** define a estrutura dos cards
2. **CSS** define a aparência visual
3. **JavaScript** preenche os dados dinamicamente:
   - Busca dados da API
   - Atualiza `textContent` ou `innerHTML` dos elementos
   - Mostra/esconde cards com `style.display`
   - Aplica classes CSS para estados visuais

**Tudo acontece na função `atualizarEstadoBrinco()` quando o brinco é digitado!**




