# Funcionalidade Expandir/Recolher - Movimentações Detalhadas

## 🎯 Funcionalidade Implementada

### **Botão de Expandir/Recolher**
- ✅ **Botão no cabeçalho** da seção de Movimentações Detalhadas
- ✅ **Ícone dinâmico** que muda conforme o estado (chevron-down/up)
- ✅ **Texto dinâmico** que alterna entre "Expandir" e "Recolher"
- ✅ **Animação suave** de transição

## 🛠️ Implementação Técnica

### **1. Estrutura HTML**
```html
<div class="card-header">
    <div class="d-flex justify-content-between align-items-center">
        <div>
            <h5>Movimentações Detalhadas</h5>
            <small>Registro completo de todas as movimentações</small>
        </div>
        <button class="btn btn-sm btn-light" 
                data-bs-toggle="collapse" 
                data-bs-target="#movimentacoes-detalhadas">
            <i class="bi bi-chevron-down"></i> Expandir
        </button>
    </div>
</div>
<div class="collapse" id="movimentacoes-detalhadas">
    <!-- Conteúdo da tabela -->
</div>
```

### **2. JavaScript Dinâmico**
```javascript
// Controle do botão expandir/recolher
collapseElement.addEventListener('show.bs.collapse', function() {
    iconToggle.className = 'bi bi-chevron-up';
    btnToggle.innerHTML = '<i class="bi bi-chevron-up"></i> Recolher';
});

collapseElement.addEventListener('hide.bs.collapse', function() {
    iconToggle.className = 'bi bi-chevron-down';
    btnToggle.innerHTML = '<i class="bi bi-chevron-down"></i> Expandir';
});
```

### **3. Estilos CSS**
```css
#btn-toggle-movimentacoes {
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

#btn-toggle-movimentacoes:hover {
    background-color: rgba(255, 255, 255, 0.2) !important;
    transform: scale(1.05);
}

.collapse {
    transition: height 0.35s ease;
}
```

## 🎨 Interface Visual

### **Estado Recolhido (Padrão)**
- 🔽 **Ícone**: Chevron para baixo
- 📝 **Texto**: "Expandir"
- 👁️ **Conteúdo**: Oculto
- 🎯 **Ação**: Clique para expandir

### **Estado Expandido**
- 🔼 **Ícone**: Chevron para cima
- 📝 **Texto**: "Recolher"
- 👁️ **Conteúdo**: Visível
- 🎯 **Ação**: Clique para recolher

### **Efeitos Visuais**
- ✨ **Hover**: Escala 1.05x e mudança de cor
- 🔄 **Transição**: 0.3s ease para todos os elementos
- 📱 **Responsivo**: Funciona em todos os dispositivos
- 🎨 **Integrado**: Combina com o design existente

## 📊 Benefícios

### **Para o Usuário**
- ✅ **Controle total** sobre a visualização
- ✅ **Interface limpa** sem sobrecarga de informações
- ✅ **Acesso rápido** aos detalhes quando necessário
- ✅ **Experiência personalizada** de navegação

### **Para Performance**
- ✅ **Carregamento otimizado** da página
- ✅ **Redução de scroll** desnecessário
- ✅ **Foco nas informações** mais importantes
- ✅ **Interface mais organizada**

### **Para Usabilidade**
- ✅ **Navegação intuitiva** com botões claros
- ✅ **Feedback visual** imediato
- ✅ **Animações suaves** para melhor UX
- ✅ **Acessibilidade** mantida

## 🚀 Funcionalidades Avançadas

### **Controle Dinâmico**
- ✅ **Ícone automático** que muda conforme estado
- ✅ **Texto contextual** que indica a ação
- ✅ **Eventos Bootstrap** para controle preciso
- ✅ **Estado persistente** durante a sessão

### **Animações Suaves**
- ✅ **Transição de altura** suave (0.35s)
- ✅ **Efeitos hover** responsivos
- ✅ **Escala dinâmica** no hover
- ✅ **Transições CSS** otimizadas

## 🎉 Resultado Final

**✅ FUNCIONALIDADE EXPANDIR/RECOLHER COMPLETAMENTE IMPLEMENTADA**

- **Botão intuitivo** no cabeçalho da seção
- **Controle total** sobre a visualização das movimentações
- **Interface limpa** e organizada
- **Animações suaves** para melhor experiência
- **Performance otimizada** com carregamento sob demanda

**O usuário agora pode escolher quando visualizar as movimentações detalhadas, mantendo a interface limpa e focada!** 📊🎯✨

