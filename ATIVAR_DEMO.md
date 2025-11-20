# 🎯 COMO ATIVAR A VERSÃO DE DEMONSTRAÇÃO RESTRITA

## 📋 **O QUE FOI IMPLEMENTADO**

A versão de demonstração restrita permite acesso apenas a:
- ✅ `/propriedade/2/pecuaria/dashboard/`
- ✅ `/propriedade/2/curral/painel/`

Todas as outras páginas são bloqueadas e redirecionam para a página de compra.

## 🔧 **COMO ATIVAR**

### **Opção 1: Variável de Ambiente (Recomendado)**

```powershell
# No PowerShell, antes de iniciar o servidor:
$env:DEMO_MODE = "true"
$env:DEMO_LINK_PAGAMENTO = "http://localhost:8000/assinaturas/"
python manage.py runserver
```

### **Opção 2: Modificar settings.py diretamente**

Edite `sistema_rural/settings.py`:

```python
# Linha ~197
DEMO_MODE = True  # Mudar de False para True
DEMO_LINK_PAGAMENTO = 'http://localhost:8000/assinaturas/'  # Seu link de pagamento
```

### **Opção 3: Criar arquivo .env**

Crie um arquivo `.env` na raiz do projeto:

```
DEMO_MODE=true
DEMO_LINK_PAGAMENTO=http://localhost:8000/assinaturas/
```

## 🎨 **FUNCIONALIDADES**

### **1. Bloqueio de Rotas**
- ✅ Middleware bloqueia todas as rotas exceto as permitidas
- ✅ Redireciona automaticamente para `/comprar-sistema/`

### **2. Menu Lateral Oculto**
- ✅ Sidebar completamente escondido em modo demo
- ✅ Botão de menu mobile também escondido
- ✅ Layout ajustado para ocupar 100% da largura

### **3. Página de Compra**
- ✅ Página bonita com mensagem de demonstração
- ✅ Contador regressivo de 4 segundos
- ✅ Redirecionamento automático para link de pagamento
- ✅ Botão para comprar imediatamente

## 📝 **ARQUIVOS CRIADOS/MODIFICADOS**

### **Novos Arquivos:**
- `gestao_rural/middleware_demo.py` - Middleware de restrição
- `gestao_rural/views_demo.py` - View da página de compra
- `gestao_rural/context_processors.py` - Context processor para DEMO_MODE
- `templates/gestao_rural/demo/comprar_sistema.html` - Template da página de compra

### **Arquivos Modificados:**
- `sistema_rural/settings.py` - Adicionado configurações de demo e middleware
- `gestao_rural/urls.py` - Adicionado rota `/comprar-sistema/`
- `templates/base_modulos_unificado.html` - Esconder sidebar em modo demo

## 🚀 **TESTAR**

1. Ative o modo demo (veja opções acima)
2. Inicie o servidor: `python manage.py runserver`
3. Tente acessar:
   - ✅ `http://localhost:8000/propriedade/2/pecuaria/dashboard/` - Deve funcionar
   - ✅ `http://localhost:8000/propriedade/2/curral/painel/` - Deve funcionar
   - ❌ `http://localhost:8000/dashboard/` - Deve redirecionar para compra
   - ❌ `http://localhost:8000/propriedade/2/agricultura/` - Deve redirecionar para compra

## 🔄 **DESATIVAR MODO DEMO**

### **Opção 1: Variável de Ambiente**
```powershell
$env:DEMO_MODE = "false"
```

### **Opção 2: settings.py**
```python
DEMO_MODE = False
```

## ⚙️ **CONFIGURAÇÕES AVANÇADAS**

### **Alterar Link de Pagamento:**
```python
DEMO_LINK_PAGAMENTO = 'https://seu-site.com/assinaturas/'
```

### **Alterar Tempo de Redirecionamento:**
Edite `templates/gestao_rural/demo/comprar_sistema.html`:
```html
'tempo_redirecionamento': 4,  # Mudar para o tempo desejado (em segundos)
```

### **Adicionar Mais Rotas Permitidas:**
Edite `gestao_rural/middleware_demo.py`:
```python
self.allowed_paths = [
    r'^/propriedade/2/pecuaria/dashboard/',
    r'^/propriedade/2/curral/painel/',
    r'^/propriedade/2/nova-rota/',  # Adicionar aqui
]
```

## ✅ **CHECKLIST**

- [ ] Modo demo ativado
- [ ] Link de pagamento configurado
- [ ] Servidor iniciado
- [ ] Rotas permitidas funcionando
- [ ] Outras rotas redirecionando para compra
- [ ] Menu lateral escondido
- [ ] Página de compra funcionando

---

**🎉 Pronto! Sua versão de demonstração restrita está configurada!**





