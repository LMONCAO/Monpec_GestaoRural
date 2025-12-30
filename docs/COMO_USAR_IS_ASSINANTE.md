# Como Usar IS_ASSINANTE nos Templates

## Objetivo
Fazer modificações que **só apareçam para assinantes** (usuários que fizeram login com senha de assinante) e **NÃO apareçam para usuários demo** (criados pelo botão demonstração).

## Variáveis Disponíveis

### `IS_ASSINANTE`
- **True**: Usuário é assinante (não é demo e tem acesso liberado)
- **False**: Usuário é demo ou não tem assinatura ativa

### `IS_DEMO_USER`
- **True**: Usuário é demo (criado pelo botão demonstração ou usuário padrão demo/demo_monpec)
- **False**: Usuário não é demo

### `acesso_liberado`
- **True**: Usuário tem assinatura ativa
- **False**: Usuário não tem assinatura ativa

## Exemplos de Uso

### 1. Mostrar conteúdo apenas para assinantes

```django
{% if IS_ASSINANTE %}
    <div class="feature-premium">
        <h3>Recurso Premium</h3>
        <p>Este recurso só está disponível para assinantes.</p>
    </div>
{% endif %}
```

### 2. Mostrar conteúdo diferente para assinantes vs demo

```django
{% if IS_ASSINANTE %}
    <button class="btn btn-primary">Salvar Alterações</button>
{% else %}
    <button class="btn btn-secondary" disabled>Versão Demo - Funcionalidade Limitada</button>
{% endif %}
```

### 3. Aplicar estilos CSS apenas para assinantes

```django
{% if IS_ASSINANTE %}
<style>
    .minha-classe-personalizada {
        background-color: #6495ed;
        color: white;
    }
</style>
{% endif %}
```

### 4. Incluir JavaScript apenas para assinantes

```django
{% if IS_ASSINANTE %}
<script>
    // Seu código JavaScript aqui
    console.log('Usuário assinante detectado');
</script>
{% endif %}
```

### 5. Mostrar/ocultar elementos HTML

```django
<div class="sidebar">
    <a href="/dashboard">Dashboard</a>
    
    {% if IS_ASSINANTE %}
        <a href="/relatorios-avancados">Relatórios Avançados</a>
        <a href="/exportacao-completa">Exportação Completa</a>
    {% endif %}
</div>
```

### 6. Condicionar classes CSS

```django
<div class="card {% if IS_ASSINANTE %}card-premium{% else %}card-demo{% endif %}">
    Conteúdo do card
</div>
```

## Onde Usar

Você pode usar `IS_ASSINANTE` em qualquer template que herda ou inclui o `base_modulos_unificado.html`, incluindo:

- `templates/base_modulos_unificado.html` (template base)
- Templates que estendem este base
- Templates de módulos específicos

## Importante

- ✅ **IS_ASSINANTE = True**: Usuário logado com senha de assinante (ex: admin com senha L6171r12@@)
- ❌ **IS_ASSINANTE = False**: Usuários demo criados pelo botão demonstração ou usuários padrão demo/demo_monpec

## Verificação

Para verificar se está funcionando:

1. Faça login com sua senha de assinante (admin/L6171r12@@)
2. As modificações com `{% if IS_ASSINANTE %}` devem aparecer
3. Faça login com um usuário demo
4. As modificações com `{% if IS_ASSINANTE %}` NÃO devem aparecer
















