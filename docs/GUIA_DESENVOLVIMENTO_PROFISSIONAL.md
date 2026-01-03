# Guia de Desenvolvimento Profissional - Sistema MONPEC

Este documento estabelece as práticas e padrões profissionais para desenvolvimento no sistema MONPEC.

## 📊 1. Análise e Planejamento

### 1.1. Análise de Requisitos

Antes de começar a desenvolver, siga este processo:

#### Checklist de Análise:
- [ ] **Entender o Problema**: Qual problema estamos resolvendo?
- [ ] **Definir Escopo**: O que está incluído e o que não está?
- [ ] **Identificar Stakeholders**: Quem será impactado?
- [ ] **Mapear Dependências**: O que já existe no sistema?
- [ ] **Verificar Padrões**: Como outros módulos similares foram implementados?
- [ ] **Definir Critérios de Sucesso**: Como sabemos que está funcionando?

#### Exemplo de Documentação de Requisitos:

```markdown
## Requisito: Cadastro de Clientes

### Problema
Os usuários precisam cadastrar clientes para vincular às vendas, mas atualmente só podem digitar o nome manualmente.

### Solução Proposta
Criar CRUD completo de clientes seguindo o padrão existente de Fornecedores.

### Escopo
- Modelo Cliente já existe (models_cadastros.py)
- Criar views: lista, novo, editar, excluir
- Criar forms: ClienteForm
- Criar templates
- Adicionar ao menu Cadastro

### Dependências
- Modelo: Cliente (existente)
- Módulo Financeiro (já referencia clientes)
- Módulo Vendas (já usa cliente_nome)

### Critérios de Sucesso
- Usuário consegue cadastrar cliente
- Cliente aparece em listagem
- Cliente pode ser editado/excluído
- Cliente aparece em selects de vendas
```

---

## 🔍 2. Análise de Código Existente

### 2.1. Como Analisar o Sistema

#### Passo 1: Entender a Estrutura
```bash
# Estrutura do projeto
gestao_rural/
├── models.py           # Modelos principais
├── models_*.py        # Modelos por módulo
├── views.py           # Views globais
├── views_*.py         # Views por módulo
├── forms.py           # Formulários
├── urls.py            # Rotas
└── migrations/        # Migrações do banco
```

#### Passo 2: Buscar Padrões Similares
```python
# Exemplo: Quer criar cadastro de Clientes?
# Busque cadastros similares como Fornecedores:

# 1. Ver modelo
grep -r "class Fornecedor" gestao_rural/

# 2. Ver views
grep -r "def fornecedor" gestao_rural/views*.py

# 3. Ver forms
grep -r "FornecedorForm" gestao_rural/forms*.py

# 4. Ver URLs
grep -r "fornecedor" gestao_rural/urls.py

# 5. Ver templates
find templates/ -name "*fornecedor*"
```

#### Passo 3: Analisar Relações
```python
# Entender relacionamentos
# - Cliente tem propriedade? (ForeignKey)
# - É compartilhado? (null=True, blank=True)
# - Tem campos únicos? (unique=True)
# - Tem choices? (choices=...)
```

---

## 🏗️ 3. Desenvolvimento Estruturado

### 3.1. Processo de Desenvolvimento (TDD - Test Driven Development)

#### Fase 1: Planejamento
1. **Criar Issue/Branch**: `feature/cadastro-clientes`
2. **Documentar**: Adicionar ao PADRAO_CADASTROS_SISTEMA.md
3. **Planejar Testes**: O que precisa funcionar?

#### Fase 2: Modelo (se necessário)
```python
# Se o modelo não existe, criar primeiro
# gestao_rural/models_cadastros.py

class Cliente(TimeStampedModel):
    # Seguir padrão do sistema
    propriedade = models.ForeignKey(...)
    nome = models.CharField(...)
    # ... campos
    
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
```

#### Fase 3: Formulário
```python
# gestao_rural/forms_completos.py

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'cpf_cnpj', ...]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            # ... seguir padrão visual do sistema
        }
```

#### Fase 4: Views (CRUD)
```python
# gestao_rural/views.py ou views_financeiro.py

@login_required
def clientes_lista(request, propriedade_id):
    """Lista de clientes"""
    propriedade = get_object_or_404(
        Propriedade, 
        id=propriedade_id,
        produtor__usuario_responsavel=request.user  # Segurança
    )
    clientes = Cliente.objects.filter(
        Q(propriedade=propriedade) | Q(propriedade__isnull=True)
    ).order_by('nome')
    
    return render(request, 'gestao_rural/clientes_lista.html', {
        'propriedade': propriedade,
        'clientes': clientes,
    })
```

#### Fase 5: URLs
```python
# gestao_rural/urls.py

path('propriedade/<int:propriedade_id>/clientes/', 
     views.clientes_lista, 
     name='clientes_lista'),
path('propriedade/<int:propriedade_id>/cliente/novo/', 
     views.cliente_novo, 
     name='cliente_novo'),
```

#### Fase 6: Templates
```html
<!-- templates/gestao_rural/clientes_lista.html -->
{% extends 'base_modulos_unificado.html' %}

{% block title %}Clientes - {{ propriedade.nome_propriedade }}{% endblock %}

<!-- Seguir padrão visual do sistema -->
```

#### Fase 7: Menu
```html
<!-- templates/base_modulos_unificado.html -->
<a href="{% url 'clientes_lista' propriedade.id %}">Clientes</a>
```

---

## 📐 4. Padrões de Código

### 4.1. Nomenclatura

```python
# Modelos: PascalCase, singular
class Cliente(models.Model):
    pass

# Views: snake_case, verbo_nome
def cliente_novo(request, propriedade_id):
    pass

# URLs: kebab-case
path('cliente/novo/', ...)

# Templates: snake_case
clientes_lista.html

# Variáveis: snake_case
cliente_novo = Cliente()
```

### 4.2. Estrutura de Views

```python
@login_required  # Sempre usar decorator
def minha_view(request, propriedade_id):
    """
    Docstring explicativa
    Descreve o que a view faz
    """
    # 1. Validação de acesso
    propriedade = get_object_or_404(
        Propriedade,
        id=propriedade_id,
        produtor__usuario_responsavel=request.user
    )
    
    # 2. Processamento POST
    if request.method == 'POST':
        form = MeuForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.propriedade = propriedade
            obj.save()
            messages.success(request, 'Salvo com sucesso!')
            return redirect('minha_lista', propriedade_id=propriedade.id)
    else:
        form = MeuForm()
    
    # 3. Context
    context = {
        'propriedade': propriedade,
        'form': form,
    }
    
    # 4. Render
    return render(request, 'gestao_rural/minha_view.html', context)
```

### 4.3. Tratamento de Erros

```python
from django.db import transaction
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

@login_required
def minha_view(request, propriedade_id):
    try:
        propriedade = get_object_or_404(Propriedade, id=propriedade_id)
        
        with transaction.atomic():
            # Operações no banco
            objeto = MeuModelo.objects.create(...)
            
        messages.success(request, 'Operação realizada com sucesso!')
        return redirect('minha_lista', propriedade_id=propriedade.id)
        
    except IntegrityError as e:
        logger.error(f'Erro de integridade: {e}')
        messages.error(request, 'Erro: Dados duplicados ou inválidos.')
        return redirect('minha_lista', propriedade_id=propriedade.id)
        
    except Exception as e:
        logger.exception('Erro inesperado')
        messages.error(request, 'Erro ao processar. Tente novamente.')
        return redirect('minha_lista', propriedade_id=propriedade.id)
```

---

## 🧪 5. Testes

### 5.1. Testes Manuais (Checklist)

Para cada funcionalidade:

```markdown
## Teste: Cadastro de Cliente

### Teste 1: Criar Cliente
- [ ] Acessar página de novo cliente
- [ ] Preencher formulário completo
- [ ] Salvar com sucesso
- [ ] Verificar mensagem de sucesso
- [ ] Cliente aparece na listagem
- [ ] Dados corretos salvos no banco

### Teste 2: Editar Cliente
- [ ] Acessar cliente existente
- [ ] Editar campos
- [ ] Salvar alterações
- [ ] Verificar que alterações foram salvas

### Teste 3: Excluir Cliente
- [ ] Excluir cliente
- [ ] Confirmar exclusão
- [ ] Verificar que foi removido da lista
- [ ] Verificar que foi removido do banco

### Teste 4: Validações
- [ ] Tentar salvar sem campos obrigatórios
- [ ] Verificar mensagens de erro
- [ ] Tentar salvar CPF/CNPJ duplicado
- [ ] Verificar validação de formato

### Teste 5: Integração
- [ ] Cliente aparece em selects de vendas
- [ ] Cliente pode ser vinculado a vendas
- [ ] Relatórios incluem cliente
```

### 5.2. Testes Automatizados (Futuro)

```python
# tests/test_clientes.py
from django.test import TestCase
from django.contrib.auth.models import User
from gestao_rural.models import Propriedade, ProdutorRural

class ClienteTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.com', 'pass')
        self.produtor = ProdutorRural.objects.create(
            nome="Teste",
            cpf_cnpj="12345678900",
            usuario_responsavel=self.user
        )
        self.propriedade = Propriedade.objects.create(
            nome_propriedade="Fazenda Teste",
            produtor=self.produtor,
            municipio="Teste",
            uf="SP",
            area_total_ha=100
        )
    
    def test_criar_cliente(self):
        from gestao_rural.models_cadastros import Cliente
        cliente = Cliente.objects.create(
            propriedade=self.propriedade,
            nome="Cliente Teste",
            cpf_cnpj="98765432100"
        )
        self.assertEqual(cliente.nome, "Cliente Teste")
```

---

## 🔒 6. Segurança

### 6.1. Validação de Acesso

```python
# SEMPRE validar acesso à propriedade
propriedade = get_object_or_404(
    Propriedade,
    id=propriedade_id,
    produtor__usuario_responsavel=request.user  # ⚠️ IMPORTANTE
)

# Para operações que modificam dados
@login_required
@require_http_methods(["POST"])
def excluir_cliente(request, propriedade_id, cliente_id):
    propriedade = get_object_or_404(
        Propriedade,
        id=propriedade_id,
        produtor__usuario_responsavel=request.user
    )
    cliente = get_object_or_404(Cliente, id=cliente_id, propriedade=propriedade)
    # ... resto do código
```

### 6.2. Validação de Dados

```python
# No formulário
class ClienteForm(forms.ModelForm):
    cpf_cnpj = forms.CharField(
        max_length=18,
        validators=[validate_cpf_cnpj]  # Validar formato
    )
    
    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data['cpf_cnpj']
        # Validação customizada
        if Cliente.objects.filter(cpf_cnpj=cpf_cnpj).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('CPF/CNPJ já cadastrado')
        return cpf_cnpj
```

---

## 📝 7. Documentação

### 7.1. Documentar Código

```python
@login_required
def cliente_novo(request, propriedade_id):
    """
    Cadastra um novo cliente para a propriedade.
    
    Args:
        request: HttpRequest com dados do formulário
        propriedade_id: ID da propriedade onde o cliente será cadastrado
    
    Returns:
        HttpResponse renderizando o formulário ou redirecionando para lista
    
    Raises:
        404: Se propriedade não existe ou usuário não tem acesso
    
    Notes:
        - Cliente pode ser compartilhado (propriedade=None) ou específico
        - Valida CPF/CNPJ único no sistema
    """
    # ... código
```

### 7.2. Atualizar Documentação do Sistema

Quando adicionar novo cadastro:

1. Atualizar `PADRAO_CADASTROS_SISTEMA.md`
2. Adicionar ao `README.md` se relevante
3. Documentar API endpoints se houver

---

## 🚀 8. Versionamento (Git)

### 8.1. Workflow Recomendado

```bash
# 1. Criar branch para feature
git checkout -b feature/cadastro-clientes

# 2. Desenvolver e commitar frequentemente
git add .
git commit -m "feat: adiciona cadastro de clientes - lista e formulário"

# 3. Commits descritivos
git commit -m "feat: adiciona validação de CPF/CNPJ em ClienteForm"
git commit -m "fix: corrige erro ao excluir cliente com vendas vinculadas"
git commit -m "docs: atualiza documentação de cadastros"

# 4. Antes de merge, testar
# 5. Criar Pull Request
# 6. Code Review
# 7. Merge para master/main
```

### 8.2. Convenções de Commits

```
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação (não afeta código)
refactor: refatoração
test: testes
chore: manutenção (dependencies, configs)
```

---

## 🔄 9. Code Review Checklist

Antes de fazer merge, verificar:

- [ ] **Segurança**: Validação de acesso implementada?
- [ ] **Padrão**: Segue padrão do sistema?
- [ ] **Performance**: Queries otimizadas (select_related, prefetch_related)?
- [ ] **Validação**: Formulários validam dados?
- [ ] **Erros**: Tratamento de erros implementado?
- [ ] **Mensagens**: Mensagens de feedback ao usuário?
- [ ] **Templates**: Seguem padrão visual do sistema?
- [ ] **URLs**: Nomes descritivos e consistentes?
- [ ] **Documentação**: Código documentado?
- [ ] **Testes**: Funcionalidade testada manualmente?

---

## 📊 10. Performance

### 10.1. Queries Otimizadas

```python
# ❌ RUIM: N+1 queries
clientes = Cliente.objects.all()
for cliente in clientes:
    print(cliente.propriedade.nome)  # Query para cada cliente!

# ✅ BOM: Usar select_related
clientes = Cliente.objects.select_related('propriedade').all()
for cliente in clientes:
    print(cliente.propriedade.nome)  # Sem queries adicionais

# ✅ BOM: Para relações reversas
propriedade = Propriedade.objects.prefetch_related('clientes').get(id=1)
for cliente in propriedade.clientes.all():  # Sem query adicional
    print(cliente.nome)
```

### 10.2. Paginação

```python
from django.core.paginator import Paginator

@login_required
def clientes_lista(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    clientes = Cliente.objects.filter(propriedade=propriedade)
    
    paginator = Paginator(clientes, 50)  # 50 por página
    page = request.GET.get('page')
    clientes_page = paginator.get_page(page)
    
    return render(request, 'gestao_rural/clientes_lista.html', {
        'propriedade': propriedade,
        'clientes': clientes_page,
    })
```

---

## 🎯 11. Checklist Final de Desenvolvimento

Antes de considerar uma funcionalidade completa:

### Funcionalidade
- [ ] Criação funcionando
- [ ] Listagem funcionando
- [ ] Edição funcionando
- [ ] Exclusão funcionando (com validações)
- [ ] Validações de formulário
- [ ] Mensagens de feedback

### Segurança
- [ ] Autenticação requerida (@login_required)
- [ ] Validação de acesso à propriedade
- [ ] Validação de dados (forms)
- [ ] Proteção CSRF ({% csrf_token %})

### Interface
- [ ] Templates seguem padrão visual
- [ ] Responsivo (mobile)
- [ ] Mensagens de erro/sucesso
- [ ] Navegação intuitiva

### Integração
- [ ] Adicionado ao menu (se aplicável)
- [ ] URLs registradas
- [ ] Não quebrou funcionalidades existentes
- [ ] Integra com outros módulos (se necessário)

### Documentação
- [ ] Código documentado
- [ ] Documentação atualizada
- [ ] Comentários explicativos

---

## 📚 12. Recursos de Aprendizado

### Para Desenvolvedores

1. **Entender Django**:
   - Documentação oficial: https://docs.djangoproject.com/
   - Models: https://docs.djangoproject.com/en/stable/topics/db/models/
   - Views: https://docs.djangoproject.com/en/stable/topics/http/views/
   - Forms: https://docs.djangoproject.com/en/stable/topics/forms/

2. **Padrões do Sistema**:
   - Ler código existente (Fornecedores, Funcionários)
   - Consultar PADRAO_CADASTROS_SISTEMA.md
   - Seguir estrutura de arquivos

3. **Ferramentas**:
   - IDE: VS Code, PyCharm
   - Git: Versionamento
   - Django Debug Toolbar: Debug de queries

---

## 🎓 Conclusão

Desenvolvimento profissional requer:

1. ✅ **Análise antes de codificar**
2. ✅ **Seguir padrões estabelecidos**
3. ✅ **Testar antes de entregar**
4. ✅ **Documentar o código**
5. ✅ **Revisar antes de merge**
6. ✅ **Pensar em segurança e performance**

Seguindo estes padrões, garantimos:
- Código consistente e manutenível
- Menos bugs
- Facilidade de onboarding de novos desenvolvedores
- Sistema escalável e robusto


