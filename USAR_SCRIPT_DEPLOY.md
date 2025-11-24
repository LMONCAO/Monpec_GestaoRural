# 🚀 Deploy Usando Script (Recomendado)

## ⚠️ Problema Resolvido

O erro `event not found` acontece porque o bash interpreta o `!` como comando de histórico.

## ✅ Solução: Usar o Script

Use o arquivo `DEPLOY_PASSO_A_PASSO.sh` que resolve esse problema!

### Como Usar:

1. **Abra o Cloud Shell:** https://console.cloud.google.com/

2. **Copie o conteúdo do arquivo `DEPLOY_PASSO_A_PASSO.sh`**

3. **Cole no Cloud Shell e pressione Enter**

   OU

   **Execute diretamente:**
   ```bash
   curl -s https://raw.githubusercontent.com/LMONCAO/Monpec_GestaoRural/master/DEPLOY_PASSO_A_PASSO.sh | bash
   ```

4. **Aguarde ~15-20 minutos**

5. **A URL será exibida no final**

---

## 🔍 Por que usar o script?

- ✅ Evita problemas com caracteres especiais (`!`)
- ✅ Mostra progresso passo a passo
- ✅ Mais fácil de debugar se houver erro
- ✅ Mais legível e organizado

---

## 📋 O que o script faz:

1. Atualiza código do GitHub
2. Obtém informações do banco
3. Gera SECRET_KEY
4. Faz build da imagem Docker
5. Faz deploy no Cloud Run
6. Mostra a URL final

---

**Dica:** O script mostra mensagens de progresso, então você sabe o que está acontecendo a cada momento!













