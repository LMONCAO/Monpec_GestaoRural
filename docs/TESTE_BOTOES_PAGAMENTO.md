# Guia de Teste - Botões de Pagamento

## Checklist para Fazer os Botões Funcionarem

### 1. Configurar Credenciais do Mercado Pago

**No arquivo `.env` (na raiz do projeto):**

```env
MERCADOPAGO_ACCESS_TOKEN=seu_access_token_aqui
MERCADOPAGO_PUBLIC_KEY=sua_public_key_aqui
```

**Como obter:**
1. Acesse: https://www.mercadopago.com.br/developers
2. Faça login
3. Vá em "Suas integrações"
4. Copie o **Access Token** e a **Public Key**

### 2. Reiniciar o Servidor Django

Após adicionar as credenciais no `.env`, **reinicie o servidor Django**:

```bash
# Pare o servidor (Ctrl+C) e inicie novamente
python manage.py runserver
```

### 3. Verificar se Há Planos no Banco

**Via Admin:**
1. Acesse: `http://localhost:8000/admin/`
2. Vá em **Gestão Rural > Planos de Assinatura**
3. Verifique se há pelo menos um plano **ativo**
4. Se não houver, crie um plano:
   - Nome: "Plano Monpec" (ou qualquer nome)
   - Slug: será gerado automaticamente
   - Preço mensal de referência: 137.90
   - Ativo: ✓ (marcado)

### 4. Testar os Botões

1. **Abra o Console do Navegador (F12)**
2. Vá na aba **Console**
3. Acesse: `http://localhost:8000/assinaturas/`
4. Clique em qualquer botão ("Aproveitar Oferta Agora" ou "Assinar Agora")
5. **Observe as mensagens no console:**
   - Deve aparecer: "Botão clicado!"
   - Deve aparecer: "URL de checkout: ..."
   - Deve aparecer: "Enviando requisição..."
   - Deve aparecer: "Resposta recebida: 200 OK"
   - Deve aparecer: "Redirecionando para: https://..."

### 5. Problemas Comuns e Soluções

#### Problema: Botão não faz nada quando clicado

**Solução:**
- Abra o console (F12) e veja se há erros
- Verifique se o botão não está desabilitado (cinza)
- Verifique se `MERCADOPAGO_PUBLIC_KEY` está configurado

#### Problema: Erro "MERCADOPAGO_ACCESS_TOKEN não configurado"

**Solução:**
- Adicione `MERCADOPAGO_ACCESS_TOKEN` no arquivo `.env`
- Reinicie o servidor Django

#### Problema: Erro "Plano não encontrado"

**Solução:**
- Verifique se há planos ativos no banco de dados
- Acesse o admin e crie um plano se necessário

#### Problema: Erro "Gateway não está registrado"

**Solução:**
- Verifique se o pacote `mercadopago` está instalado:
  ```bash
  pip install mercadopago
  ```
- Reinicie o servidor

#### Problema: Erro 403 Forbidden

**Solução:**
- Limpe os cookies do navegador
- Faça login novamente
- O CSRF token será gerado automaticamente

### 6. Fluxo Esperado

1. ✅ Usuário clica no botão
2. ✅ Botão mostra "Processando..."
3. ✅ JavaScript envia requisição POST para `/assinaturas/plano/{slug}/checkout/`
4. ✅ Backend cria checkout no Mercado Pago
5. ✅ Backend retorna URL do checkout
6. ✅ JavaScript redireciona para Mercado Pago
7. ✅ Usuário insere dados do cartão no Mercado Pago
8. ✅ Após pagamento, usuário retorna para o sistema

### 7. Testar com Cartão de Teste

**Cartão Aprovado:**
- Número: `5031 4332 1540 6351`
- CVV: `123`
- Nome: Qualquer nome
- Data: Qualquer data futura

### 8. Verificar Logs

**No terminal do servidor Django**, você verá:
- Requisições recebidas
- Erros (se houver)
- URLs geradas

**No console do navegador (F12)**, você verá:
- Logs de debug do JavaScript
- Requisições HTTP na aba Network
- Respostas do servidor

## Próximos Passos

Se tudo estiver configurado corretamente:
1. Os botões devem estar habilitados (não cinza)
2. Ao clicar, deve redirecionar para Mercado Pago
3. Após pagamento, deve retornar para o sistema

Se ainda não funcionar, verifique os logs no console do navegador e no terminal do servidor para identificar o problema específico.
































