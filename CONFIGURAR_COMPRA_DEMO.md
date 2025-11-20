# 🛒 CONFIGURAR LINK DE COMPRA PARA DEMO

## 📋 **PROBLEMA**

A página de compra (`/comprar-sistema/`) está aparecendo, mas o link de pagamento precisa ser configurado corretamente.

## 🔧 **SOLUÇÃO**

### **Opção 1: Usar a Página de Assinaturas (Já existe)**

A rota `/assinaturas/` já existe no sistema. Configure assim:

**Edite `sistema_rural/settings.py`:**

```python
# Linha ~202
DEMO_LINK_PAGAMENTO = 'http://localhost:8000/assinaturas/'
```

### **Opção 2: Link Externo (Se tiver página de vendas)**

Se você tem uma página de vendas externa:

```python
DEMO_LINK_PAGAMENTO = 'https://seu-site.com/comprar/'
```

### **Opção 3: Link para Login**

Se quiser redirecionar para login:

```python
DEMO_LINK_PAGAMENTO = 'http://localhost:8000/login/'
```

## ⚙️ **CONFIGURAÇÃO ATUAL**

Verifique o arquivo `sistema_rural/settings.py` na linha ~202:

```python
DEMO_LINK_PAGAMENTO = os.getenv('DEMO_LINK_PAGAMENTO', 'http://localhost:8000/assinaturas/')
```

**O padrão já é `/assinaturas/`**, então deve funcionar!

## 🚀 **COMO TESTAR**

1. **Inicie o servidor:**
   ```powershell
   python manage.py runserver
   ```

2. **Acesse uma rota bloqueada:**
   ```
   http://localhost:8000/dashboard/
   ```

3. **Deve redirecionar para:**
   ```
   http://localhost:8000/comprar-sistema/
   ```

4. **Após 4 segundos (ou clicar no botão), deve ir para:**
   ```
   http://localhost:8000/assinaturas/
   ```

## 🔍 **VERIFICAR SE ESTÁ FUNCIONANDO**

Se a página de compra não redirecionar:

1. **Verifique o console do navegador (F12):**
   - Veja se há erros no JavaScript
   - Veja qual URL está sendo usada

2. **Verifique o settings.py:**
   ```python
   # Deve estar assim:
   DEMO_LINK_PAGAMENTO = 'http://localhost:8000/assinaturas/'
   ```

3. **Teste a rota de assinaturas diretamente:**
   ```
   http://localhost:8000/assinaturas/
   ```
   Deve mostrar a página de planos de assinatura.

## 📝 **ALTERNATIVAS**

### **Desativar Redirecionamento Automático:**

Se quiser que o usuário clique manualmente no botão (sem redirecionar automaticamente):

Edite `gestao_rural/views_demo.py`:

```python
'tempo_redirecionamento': 0,  # 0 = sem redirecionamento automático
```

### **Alterar Tempo de Redirecionamento:**

Edite `gestao_rural/views_demo.py`:

```python
'tempo_redirecionamento': 10,  # 10 segundos ao invés de 4
```

## ✅ **CHECKLIST**

- [ ] Verificar se `DEMO_LINK_PAGAMENTO` está configurado em `settings.py`
- [ ] Verificar se a rota `/assinaturas/` existe e funciona
- [ ] Testar redirecionamento de rotas bloqueadas
- [ ] Testar clique no botão "Comprar Sistema Completo"
- [ ] Verificar redirecionamento automático após 4 segundos

---

**🎉 Configuração concluída!**





