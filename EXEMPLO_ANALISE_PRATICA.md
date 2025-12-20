# Exemplo Prático: Como Analisar e Desenvolver uma Feature

Este documento mostra um exemplo real de como analisar o sistema e desenvolver uma nova funcionalidade profissionalmente.

## 📋 Caso de Uso: Implementar Cadastro de Clientes

### Passo 1: Análise do Problema

**Situação**: O sistema tem o modelo `Cliente` mas não tem interface para gerenciar clientes.

**Objetivo**: Criar CRUD completo de clientes seguindo o padrão do sistema.

---

### Passo 2: Analisar o Código Existente

#### 2.1. Verificar se o Modelo Existe

```bash
# Buscar modelo Cliente
grep -r "class Cliente" gestao_rural/
```

**Resultado**: Encontrado em `gestao_rural/models_cadastros.py`

```python
class Cliente(TimeStampedModel):
    propriedade = models.ForeignKey(Propriedade, ...)
    nome = models.CharField(max_length=200)
    cpf_cnpj = models.CharField(max_length=18, unique=True)
    # ... mais campos
```

**Conclusão**: ✅ Modelo existe, não precisa criar.

#### 2.2. Buscar Padrão Similar (Fornecedores)

```bash
# Ver como Fornecedores está implementado
grep -r "fornecedor_novo\|fornecedores_lista" gestao_rural/
```

**Resultado**: Encontrado em `gestao_rural/views_compras.py` e `gestao_rural/urls.py`

#### 2.3. Analisar Estrutura de Fornecedores

**View**: `gestao_rural/views_compras.py`

```python
@login_required
def fornecedores_lista(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    fornecedores = Fornecedor.objects.filter(
        Q(propriedade=propriedade) | Q(propriedade__isnull=True)
    ).order_by('nome')
    
    return render(request, 'gestao_rural/fornecedores_lista.html', {
        'propriedade': propriedade,
        'fornecedores': fornecedores,
    })

@login_required
def fornecedor_novo(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    # ... código de criação
```

**URL**: `gestao_rural/urls.py`

```python
path('propriedade/<int:propriedade_id>/compras/fornecedores/', 
     views_compras.fornecedores_lista, 
     name='fornecedores_lista'),
path('propriedade/<int:propriedade_id>/compras/fornecedor/novo/', 
     views_compras.fornecedor_novo, 
     name='fornecedor_novo'),
```

**Template**: `templates/gestao_rural/fornecedores_lista.html`

```bash
# Ver estrutura do template
cat templates/gestao_rural/fornecedores_lista.html
```

#### 2.4. Analisar Form

```bash
grep -r "class FornecedorForm" gestao_rural/
```

**Resultado**: Encontrado em `gestao_rural/forms_completos.py`

```python
class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ['nome', 'nome_fantasia', 'cpf_cnpj', ...]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            # ...
        }
```

---

### Passo 3: Planejamento de Desenvolvimento

#### 3.1. Checklist de Implementação

- [ ] Criar `ClienteForm` em `forms_completos.py`
- [ ] Criar view `clientes_lista` em `views.py` ou `views_financeiro.py`
- [ ] Criar view `cliente_novo`
- [ ] Criar view `cliente_editar`
- [ ] Criar view `cliente_excluir`
- [ ] Adicionar URLs em `urls.py`
- [ ] Criar template `clientes_lista.html`
- [ ] Criar template `cliente_form.html`
- [ ] Adicionar link no menu Cadastro
- [ ] Testar funcionalidades

#### 3.2. Decisões de Arquitetura

**Onde colocar as views?**
- `views.py` → Views globais
- `views_financeiro.py` → Se relacionado a financeiro
- `views_compras.py` → Se relacionado a compras

**Decisão**: Como Cliente pode ser usado em múltiplos módulos (vendas, financeiro), vamos colocar em `views.py`.

**Onde colocar URLs?**
- Seguir padrão de Fornecedores
- `/propriedade/<id>/clientes/` → Lista
- `/propriedade/<id>/cliente/novo/` → Criar
- `/propriedade/<id>/cliente/<id>/editar/` → Editar

---

### Passo 4: Implementação Passo a Passo

#### 4.1. Criar Form (Baseado em FornecedorForm)

```python
# gestao_rural/forms_completos.py

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente  # Importar do models_cadastros
        fields = [
            'nome', 'nome_fantasia', 'tipo_pessoa', 'cpf_cnpj',
            'inscricao_estadual', 'tipo_cliente',
            'telefone', 'celular', 'email', 'website',
            'endereco', 'numero', 'complemento', 'bairro',
            'cidade', 'estado', 'cep',
            'banco', 'agencia', 'conta', 'tipo_conta', 'pix',
            'limite_credito', 'observacoes'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            # ... seguir padrão do sistema
        }
```

#### 4.2. Criar Views

```python
# gestao_rural/views.py

from .models_cadastros import Cliente
from .forms_completos import ClienteForm

@login_required
def clientes_lista(request, propriedade_id):
    """Lista de clientes da propriedade"""
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id,
        produtor__usuario_responsavel=request.user
    )
    
    clientes = Cliente.objects.filter(
        Q(propriedade=propriedade) | Q(propriedade__isnull=True)
    ).order_by('nome')
    
    context = {
        'propriedade': propriedade,
        'clientes': clientes,
    }
    return render(request, 'gestao_rural/clientes_lista.html', context)


@login_required
def cliente_novo(request, propriedade_id):
    """Cadastrar novo cliente"""
    propriedade = get_object_or_404(
        Propriedade,
        id=propriedade_id,
        produtor__usuario_responsavel=request.user
    )
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.propriedade = propriedade
            cliente.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('clientes_lista', propriedade_id=propriedade.id)
    else:
        form = ClienteForm()
    
    context = {
        'propriedade': propriedade,
        'form': form,
        'form_type': 'novo'
    }
    return render(request, 'gestao_rural/cliente_form.html', context)


@login_required
def cliente_editar(request, propriedade_id, cliente_id):
    """Editar cliente existente"""
    propriedade = get_object_or_404(
        Propriedade,
        id=propriedade_id,
        produtor__usuario_responsavel=request.user
    )
    cliente = get_object_or_404(Cliente, id=cliente_id, propriedade=propriedade)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('clientes_lista', propriedade_id=propriedade.id)
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'propriedade': propriedade,
        'cliente': cliente,
        'form': form,
        'form_type': 'editar'
    }
    return render(request, 'gestao_rural/cliente_form.html', context)


@login_required
def cliente_excluir(request, propriedade_id, cliente_id):
    """Excluir cliente"""
    propriedade = get_object_or_404(
        Propriedade,
        id=propriedade_id,
        produtor__usuario_responsavel=request.user
    )
    cliente = get_object_or_404(Cliente, id=cliente_id, propriedade=propriedade)
    
    if request.method == 'POST':
        nome = cliente.nome
        cliente.delete()
        messages.success(request, f'Cliente "{nome}" excluído com sucesso!')
        return redirect('clientes_lista', propriedade_id=propriedade.id)
    
    context = {
        'propriedade': propriedade,
        'cliente': cliente,
    }
    return render(request, 'gestao_rural/cliente_excluir.html', context)
```

#### 4.3. Adicionar URLs

```python
# gestao_rural/urls.py

# Adicionar após outras URLs de cadastros
path('propriedade/<int:propriedade_id>/clientes/', views.clientes_lista, name='clientes_lista'),
path('propriedade/<int:propriedade_id>/cliente/novo/', views.cliente_novo, name='cliente_novo'),
path('propriedade/<int:propriedade_id>/cliente/<int:cliente_id>/editar/', views.cliente_editar, name='cliente_editar'),
path('propriedade/<int:propriedade_id>/cliente/<int:cliente_id>/excluir/', views.cliente_excluir, name='cliente_excluir'),
```

#### 4.4. Criar Templates (Baseados em Fornecedores)

```bash
# Copiar estrutura de fornecedores como base
cp templates/gestao_rural/fornecedores_lista.html templates/gestao_rural/clientes_lista.html
cp templates/gestao_rural/fornecedor_form.html templates/gestao_rural/cliente_form.html

# Ajustar referências no template
# - Trocar "fornecedor" por "cliente"
# - Trocar "Fornecedor" por "Cliente"
# - Ajustar campos específicos
```

#### 4.5. Atualizar Menu

```html
<!-- templates/base_modulos_unificado.html -->
<!-- No menu Cadastro, ajustar o link de Clientes: -->

<a href="{% url 'clientes_lista' propriedade.id %}" 
   class="nav-link nav-link-submenu {% if 'cliente' in request.path %}active{% endif %}">
    <i class="bi bi-person-check"></i> Clientes
</a>
```

---

### Passo 5: Testes

#### 5.1. Teste Manual - Checklist

```markdown
## Teste: Cadastro de Clientes

### Criar Cliente
- [ ] Acessar /propriedade/1/clientes/
- [ ] Clicar em "Novo Cliente"
- [ ] Preencher formulário completo
- [ ] Salvar
- [ ] Verificar mensagem de sucesso
- [ ] Verificar que cliente aparece na lista
- [ ] Verificar dados no banco

### Editar Cliente
- [ ] Clicar em "Editar" em um cliente
- [ ] Modificar campos
- [ ] Salvar
- [ ] Verificar alterações salvas

### Excluir Cliente
- [ ] Clicar em "Excluir" em um cliente
- [ ] Confirmar exclusão
- [ ] Verificar que foi removido

### Validações
- [ ] Tentar salvar sem nome (obrigatório)
- [ ] Tentar salvar CPF/CNPJ duplicado
- [ ] Verificar mensagens de erro

### Integração
- [ ] Cliente aparece em selects de vendas?
- [ ] Cliente pode ser vinculado?
```

#### 5.2. Teste de Integração

Verificar se não quebrou nada existente:

```bash
# Rodar servidor
python manage.py runserver

# Testar outras funcionalidades
# - Criar venda
# - Criar receita
# - Outras áreas que usam cliente
```

---

### Passo 6: Documentação

#### 6.1. Atualizar PADRAO_CADASTROS_SISTEMA.md

Adicionar seção de Clientes:

```markdown
#### **Clientes**
- **Modelo**: `Cliente` (em `gestao_rural/models_cadastros.py`)
- **Form**: `ClienteForm` (em `gestao_rural/forms_completos.py`)
- **Views**: `views.py`
  - `clientes_lista(propriedade_id)` - Listar
  - `cliente_novo(propriedade_id)` - Criar
  - `cliente_editar(propriedade_id, cliente_id)` - Editar
  - `cliente_excluir(propriedade_id, cliente_id)` - Excluir
- **URLs**: 
  - `/propriedade/<id>/clientes/` - Lista
  - `/propriedade/<id>/cliente/novo/` - Criar
  - `/propriedade/<id>/cliente/<id>/editar/` - Editar
  - `/propriedade/<id>/cliente/<id>/excluir/` - Excluir
- **Características**: Vinculado a uma `Propriedade`, pode ser compartilhado
```

#### 6.2. Commit no Git

```bash
git add .
git commit -m "feat: implementa CRUD completo de clientes

- Adiciona ClienteForm
- Cria views: lista, novo, editar, excluir
- Adiciona templates
- Atualiza menu Cadastro
- Segue padrão de Fornecedores

Closes #123"
```

---

### Passo 7: Code Review

Antes de fazer merge, revisar:

- [ ] Código segue padrão do sistema?
- [ ] Validações de segurança implementadas?
- [ ] Mensagens de feedback ao usuário?
- [ ] Templates seguem padrão visual?
- [ ] Não quebrou funcionalidades existentes?
- [ ] Documentação atualizada?

---

## 🎯 Resumo do Processo

1. **Análise**: Entender problema e buscar padrões similares
2. **Planejamento**: Checklist e decisões de arquitetura
3. **Implementação**: Forms → Views → URLs → Templates → Menu
4. **Testes**: Manual e integração
5. **Documentação**: Atualizar docs e commitar
6. **Review**: Revisar antes de merge

Seguindo este processo, garantimos código profissional, consistente e manutenível! 🚀


