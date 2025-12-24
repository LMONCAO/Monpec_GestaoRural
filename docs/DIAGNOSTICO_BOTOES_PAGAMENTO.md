# Diagnóstico - Botões de Pagamento Não Funcionam

## Passos para Diagnosticar

### 1. Abrir o Console do Navegador

1. Pressione **F12** no navegador
2. Vá na aba **Console**
3. Recarregue a página (`Ctrl + R` ou `F5`)
4. Clique no botão novamente
5. Veja as mensagens no console

### 2. Verificar Mensagens no Console

**Se aparecer:**
- `"Inicializando script de checkout..."` → Script está carregando
- `"Botões encontrados: X"` → X deve ser maior que 0
- `"Botão clicado!"` → O clique está sendo detectado
- `"Erro: ..."` → Veja a mensagem de erro específica

### 3. Verificar se o Botão Está Desabilitado

**Sintoma:** Botão aparece cinza e não clicável

**Causa:** `MERCADOPAGO_PUBLIC_KEY` não está configurado

**Solução:**
1. Adicione no arquivo `.env`:
   ```env
   MERCADOPAGO_PUBLIC_KEY=sua_chave_aqui
   ```
2. Reinicie o servidor Django

### 4. Verificar se Há Planos no Banco

**Sintoma:** Mensagem "Nenhum plano disponível"

**Solução:**
1. Acesse o admin do Django: `http://localhost:8000/admin/`
2. Vá em **Gestão Rural > Planos de Assinatura**
3. Verifique se há pelo menos um plano **ativo**
4. Se não houver, crie um plano

### 5. Verificar Erros no Backend

**No terminal onde o servidor Django está rodando, veja se aparecem erros quando você clica no botão.**

**Erros comuns:**
- `MERCADOPAGO_ACCESS_TOKEN não configurado` → Adicione no `.env`
- `Plano não encontrado` → Verifique se o plano existe e está ativo
- `Gateway não pôde ser criado` → Verifique as credenciais

### 6. Verificar Requisição HTTP

1. No console do navegador, vá na aba **Network** (Rede)
2. Clique no botão
3. Procure por uma requisição para `/assinaturas/plano/.../checkout/`
4. Clique nela e veja:
   - **Status:** Deve ser 200 (sucesso) ou outro código de erro
   - **Response:** Veja a resposta do servidor

### 7. Verificar CSRF Token

**Sintoma:** Erro 403 Forbidden

**Solução:**
- O CSRF token é gerado automaticamente
- Se houver erro 403, limpe os cookies e tente novamente

## Problemas Comuns e Soluções

### Problema 1: Botão Não Faz Nada

**Possíveis causas:**
1. JavaScript não está carregando
2. Botão está desabilitado
3. Erro silencioso no JavaScript

**Solução:**
- Abra o console (F12) e veja as mensagens
- Verifique se o botão não está com `disabled`

### Problema 2: Erro "Plano não identificado"

**Causa:** O atributo `data-plano` não está sendo definido corretamente

**Solução:**
- Verifique se há planos no banco de dados
- Verifique se o plano tem um `slug` válido

### Problema 3: Erro 500 no Servidor

**Causa:** Erro no backend ao criar checkout

**Solução:**
- Verifique os logs do servidor Django
- Verifique se `MERCADOPAGO_ACCESS_TOKEN` está configurado
- Verifique se o plano existe no banco

### Problema 4: Redireciona mas Mercado Pago Mostra Erro

**Causa:** Credenciais do Mercado Pago inválidas

**Solução:**
- Verifique se as credenciais estão corretas no `.env`
- Use credenciais de teste (sandbox) para desenvolvimento
- Verifique se não há espaços extras nas credenciais

## Checklist Rápido

- [ ] `MERCADOPAGO_ACCESS_TOKEN` configurado no `.env`
- [ ] `MERCADOPAGO_PUBLIC_KEY` configurado no `.env`
- [ ] Servidor Django reiniciado após adicionar variáveis
- [ ] Pelo menos um plano ativo no banco de dados
- [ ] Console do navegador aberto (F12)
- [ ] Botão não está desabilitado (cinza)
- [ ] Usuário está logado no sistema

## Próximos Passos

Se após seguir este guia o problema persistir:

1. Copie todas as mensagens do console do navegador
2. Copie os erros do terminal do servidor Django
3. Verifique se as credenciais do Mercado Pago estão corretas
4. Teste com um plano simples criado no admin



