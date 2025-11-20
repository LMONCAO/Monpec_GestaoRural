# 🧪 INSTRUÇÕES PARA TESTAR O SISTEMA DE PESAGEM

## 📋 Como Executar o Teste

### Passo 1: Abrir a página do Curral
1. Acesse: `http://localhost:8000/propriedade/2/curral/painel/`
2. Abra o Console do Navegador (F12 → Console)

### Passo 2: Executar o script de teste
1. Abra o arquivo `teste_pesagem_curral.js` neste projeto
2. **Copie TODO o conteúdo** do arquivo
3. **Cole no console do navegador** e pressione Enter
4. Aguarde o teste terminar (cerca de 2-3 segundos)

### Passo 3: Verificar o relatório
O script vai mostrar:
- ✅ Testes que passaram
- ⚠️ Avisos (não críticos)
- ❌ Erros encontrados
- 📊 Relatório completo em JSON

## 🔍 O que o teste verifica:

1. **Elementos do DOM**: Verifica se todos os elementos necessários existem
2. **Variáveis globais**: Verifica se `workState` e `window.salvarPesagemBackend` estão definidos
3. **Listeners do botão**: Verifica se o botão "Gravar" tem listeners anexados
4. **Função de salvamento**: Verifica se a função tem o código necessário
5. **Estado atual**: Verifica se há brinco e peso preenchidos
6. **Simulação de clique**: Testa se o evento de clique funciona
7. **API endpoint**: Verifica se a rota da API existe e responde
8. **CSRF token**: Verifica se o token CSRF está disponível

## 📊 Interpretando os Resultados

### ✅ Todos os testes passaram
- O sistema está configurado corretamente
- Você pode testar manualmente digitando um peso e clicando em "Gravar"

### ⚠️ Apenas avisos
- O sistema deve funcionar, mas alguns elementos podem não estar preenchidos
- Exemplo: Se não houver brinco/peso, é normal mostrar aviso

### ❌ Erros encontrados
- Verifique quais erros aparecem
- Os erros mais comuns:
  - `window.salvarPesagemBackend não está definido` → O código não foi carregado
  - `Elemento saveBtn não encontrado` → O botão não existe no DOM
  - `CSRF token não encontrado` → Problema de autenticação

## 🛠️ Soluções para Problemas Comuns

### Erro: "window.salvarPesagemBackend não está definido"
**Solução**: 
1. Recarregue a página (Ctrl+F5)
2. Verifique se há erros de JavaScript no console
3. Verifique se o arquivo `curral_dashboard.html` foi salvo corretamente

### Erro: "Elemento saveBtn não encontrado"
**Solução**:
1. Verifique se você está na página correta (`/curral/painel/`)
2. Verifique se o HTML foi renderizado corretamente
3. Tente encontrar o botão manualmente: `document.getElementById('saveBtn')`

### Erro: "CSRF token não encontrado"
**Solução**:
1. Faça login novamente
2. Verifique se você está autenticado
3. Verifique os cookies do navegador

## 📝 Teste Manual Após o Script

Depois de executar o script de teste, faça um teste manual:

1. **Digite um brinco** (ex: `105500376195129`)
2. **Aguarde o animal ser identificado**
3. **Digite um peso** (ex: `395`)
4. **Clique no botão "Gravar"**
5. **Verifique no console** se aparecem os logs:
   - `🔘 BOTÃO GRAVAR CLICADO!`
   - `💾 Função salvarPesagemBackend chamada`
   - `📊 Estado atual: {...}`

## 💾 Relatório Salvo

O relatório completo é salvo no `localStorage` com a chave `teste_pesagem_relatorio`.

Para ver o relatório novamente:
```javascript
JSON.parse(localStorage.getItem('teste_pesagem_relatorio'))
```

## 🆘 Precisa de Ajuda?

Se o teste mostrar erros, envie:
1. O relatório completo do teste
2. Screenshot do console
3. Qualquer mensagem de erro específica




