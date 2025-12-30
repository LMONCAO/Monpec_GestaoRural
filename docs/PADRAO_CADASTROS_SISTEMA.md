# Padrão de Cadastros no Sistema MONPEC

Este documento explica como os desenvolvedores utilizam e integram os cadastros no sistema.

## 📋 Estrutura de Cadastros

Os cadastros no sistema seguem um padrão CRUD consistente e estão organizados em duas categorias:

### 1️⃣ Cadastros Globais (Não vinculados a propriedade)

Estes cadastros são compartilhados entre todas as propriedades do usuário:

#### **Produtor Rural (Proprietário)**
- **Modelo**: `ProdutorRural` (em `gestao_rural/models.py`)
- **Form**: `ProdutorRuralForm` (em `gestao_rural/forms.py`)
- **Views**: `views.py`
  - `produtor_novo()` - Criar
  - `produtor_editar(produtor_id)` - Editar
  - `produtor_excluir(produtor_id)` - Excluir
- **URLs**: 
  - `/produtor/novo/`
  - `/produtor/<id>/editar/`
  - `/produtor/<id>/excluir/`
- **Características**: Vinculado ao `usuario_responsavel` (User)

#### **Categorias de Animais**
- **Modelo**: `CategoriaAnimal` (em `gestao_rural/models.py`)
- **Form**: `CategoriaAnimalForm` (em `gestao_rural/forms.py`)
- **Views**: `views.py`
  - `categoria_nova()` - Criar
  - `categoria_editar(categoria_id)` - Editar
  - `categoria_excluir(categoria_id)` - Excluir
  - `categorias_lista()` - Listar
- **URLs**: 
  - `/categorias/` - Lista
  - `/categorias/nova/` - Criar
  - `/categorias/<id>/editar/` - Editar
  - `/categorias/<id>/excluir/` - Excluir
- **Características**: Global, compartilhado por todos os usuários do sistema

---

### 2️⃣ Cadastros por Propriedade

Estes cadastros são específicos de cada propriedade e requerem `propriedade_id`:

#### **Fazenda/Propriedade**
- **Modelo**: `Propriedade` (em `gestao_rural/models.py`)
- **Form**: `PropriedadeForm` (em `gestao_rural/forms.py`)
- **Views**: `views.py`
  - `propriedade_nova_auto()` - Criar (URL simplificada - encontra produtor automaticamente)
  - `propriedade_nova(produtor_id)` - Criar (com produtor explícito)
  - `propriedade_editar(propriedade_id)` - Editar
  - `propriedade_excluir(propriedade_id)` - Excluir
  - `minhas_propriedades()` - Listar (URL simplificada)
  - `propriedades_lista(produtor_id)` - Listar (com produtor explícito)
- **URLs**: 
  - `/propriedades/` - Lista (simplificada)
  - `/propriedade/nova/` - Criar (simplificada)
  - `/propriedade/<id>/editar/` - Editar
  - `/propriedade/<id>/excluir/` - Excluir
- **Características**: Vinculado a um `ProdutorRural` e requer `propriedade_id`

#### **Fornecedores** (Módulo: Compras)
- **Modelo**: `Fornecedor` (em `gestao_rural/models_compras.py`)
- **Form**: `FornecedorForm` (em `gestao_rural/forms_completos.py`)
- **Views**: `views_compras.py`
  - `fornecedores_lista(propriedade_id)` - Listar
  - `fornecedor_novo(propriedade_id)` - Criar
  - (editar/excluir podem estar implementados)
- **URLs**: 
  - `/propriedade/<id>/compras/fornecedores/` - Lista
  - `/propriedade/<id>/compras/fornecedor/novo/` - Criar
- **Características**: Vinculado a uma `Propriedade`, pode ser compartilhado (`propriedade=None`)

#### **Funcionários** (Módulo: Operações)
- **Modelo**: `Funcionario` (em `gestao_rural/models_funcionarios.py`)
- **Form**: Formulário manual (em `gestao_rural/views_funcionarios.py`)
- **Views**: `views_funcionarios.py`
  - `funcionarios_lista(propriedade_id)` - Listar
  - `funcionario_novo(propriedade_id)` - Criar
  - `funcionarios_dashboard(propriedade_id)` - Dashboard
- **URLs**: 
  - `/propriedade/<id>/operacoes/funcionarios/lista/` - Lista
  - `/propriedade/<id>/operacoes/funcionarios/novo/` - Criar
  - `/propriedade/<id>/operacoes/funcionarios/` - Dashboard
- **Características**: Vinculado a uma `Propriedade`

#### **Clientes** (A ser implementado)
- **Modelo**: `Cliente` (em `gestao_rural/models_cadastros.py`) ✅ Existe
- **Form**: A ser criado
- **Views**: A serem criadas
- **URLs**: A serem definidas
- **Características**: Vinculado a uma `Propriedade`, pode ser compartilhado

---

## 🔧 Padrão de Implementação CRUD

### Estrutura de Views

Todas as views de cadastro seguem este padrão:

```python
@login_required
def entidade_nova(request, propriedade_id=None):  # propriedade_id opcional
    """Cadastrar nova entidade"""
    # Se requer propriedade, buscar e validar
    if propriedade_id:
        propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    if request.method == 'POST':
        # Processar formulário
        form = EntidadeForm(request.POST)
        if form.is_valid():
            entidade = form.save(commit=False)
            # Associar à propriedade se necessário
            if propriedade_id:
                entidade.propriedade = propriedade
            # Outras associações (ex: usuario_responsavel)
            entidade.save()
            messages.success(request, 'Entidade cadastrada com sucesso!')
            return redirect('entidades_lista', propriedade_id=propriedade.id)
    else:
        form = EntidadeForm()
    
    context = {
        'form': form,
        'propriedade': propriedade if propriedade_id else None,
    }
    return render(request, 'gestao_rural/entidade_form.html', context)
```

### Estrutura de URLs

```python
# Em gestao_rural/urls.py

# Cadastros globais
path('entidade/novo/', views.entidade_novo, name='entidade_novo'),
path('entidade/<int:entidade_id>/editar/', views.entidade_editar, name='entidade_editar'),

# Cadastros por propriedade
path('propriedade/<int:propriedade_id>/entidade/novo/', views.entidade_novo, name='entidade_novo'),
path('propriedade/<int:propriedade_id>/entidades/', views.entidades_lista, name='entidades_lista'),
```

### Estrutura de Templates

Templates seguem o padrão:
- `gestao_rural/entidade_form.html` - Formulário de criar/editar
- `gestao_rural/entidades_lista.html` - Lista de entidades

---

## 📍 Como Integrar um Novo Cadastro

### Passo 1: Definir o Modelo

Em `gestao_rural/models.py` ou arquivo específico:

```python
class NovaEntidade(models.Model):
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        null=True,  # Se for compartilhado
        blank=True
    )
    nome = models.CharField(max_length=200)
    # ... outros campos
    
    class Meta:
        verbose_name = "Nova Entidade"
        verbose_name_plural = "Novas Entidades"
```

### Passo 2: Criar o Form

Em `gestao_rural/forms.py` ou arquivo específico:

```python
class NovaEntidadeForm(forms.ModelForm):
    class Meta:
        model = NovaEntidade
        fields = ['nome', 'outro_campo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
        }
```

### Passo 3: Criar as Views

Em `views.py` ou arquivo específico do módulo:

```python
@login_required
def novas_entidades_lista(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    entidades = NovaEntidade.objects.filter(propriedade=propriedade)
    return render(request, 'gestao_rural/novas_entidades_lista.html', {
        'propriedade': propriedade,
        'entidades': entidades,
    })

@login_required
def nova_entidade_novo(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    if request.method == 'POST':
        form = NovaEntidadeForm(request.POST)
        if form.is_valid():
            entidade = form.save(commit=False)
            entidade.propriedade = propriedade
            entidade.save()
            messages.success(request, 'Entidade cadastrada com sucesso!')
            return redirect('novas_entidades_lista', propriedade_id=propriedade.id)
    else:
        form = NovaEntidadeForm()
    return render(request, 'gestao_rural/nova_entidade_form.html', {
        'form': form,
        'propriedade': propriedade,
    })
```

### Passo 4: Registrar URLs

Em `gestao_rural/urls.py`:

```python
path('propriedade/<int:propriedade_id>/novas-entidades/', views.novas_entidades_lista, name='novas_entidades_lista'),
path('propriedade/<int:propriedade_id>/nova-entidade/novo/', views.nova_entidade_novo, name='nova_entidade_novo'),
```

### Passo 5: Adicionar ao Menu

Em `templates/base_modulos_unificado.html`, no menu "Cadastro":

```html
<a href="{% url 'novas_entidades_lista' propriedade.id %}" 
   class="nav-link nav-link-submenu">
    <i class="bi bi-icon-name"></i> Novas Entidades
</a>
```

---

## 🎯 Boas Práticas

1. **Sempre usar `@login_required`** nas views
2. **Validar propriedade** com `get_object_or_404(Propriedade, id=propriedade_id)`
3. **Verificar permissões** quando necessário
4. **Usar `messages.success/error`** para feedback
5. **Seguir convenção de nomes**: `{entidade}_nova`, `{entidade}_editar`, etc.
6. **Redirecionar após salvar** para a lista ou detalhes
7. **Usar forms Django** quando possível
8. **Adicionar docstrings** nas views

---

## 🔍 Localização dos Cadastros no Código

- **Models**: `gestao_rural/models.py` (ou arquivos específicos)
- **Forms**: `gestao_rural/forms.py` (ou arquivos específicos)
- **Views Globais**: `gestao_rural/views.py`
- **Views por Módulo**: 
  - `views_compras.py` - Fornecedores, Ordens de Compra
  - `views_funcionarios.py` - Funcionários
  - `views_financeiro.py` - Contas, Categorias Financeiras
  - etc.
- **Templates**: `templates/gestao_rural/{entidade}_*.html`
- **URLs**: `gestao_rural/urls.py`

---

## 📝 Menu de Cadastros

O menu "Cadastro" está localizado em:
- **Template**: `templates/base_modulos_unificado.html`
- **Posição**: Primeiro item após "Voltar aos Módulos"
- **Estrutura**: Menu expansível (accordion) com submenus

Para adicionar um novo cadastro ao menu, edite o template e adicione um link no submenu de "Cadastro".


