# 🔓 DESATIVAR MODO DEMO E CRIAR PLANOS DE ASSINATURA

## ✅ **MODO DEMO DESATIVADO**

O modo demo foi **DESATIVADO** no arquivo `sistema_rural/settings.py`.

Agora você tem acesso à **VERSÃO COMPLETA** do sistema! 🎉

---

## 🛒 **CRIAR PLANOS DE ASSINATURA**

Para que a página de assinaturas mostre os planos disponíveis, você precisa criá-los no banco de dados.

### **Opção 1: Via Admin do Django (Mais Fácil)**

1. **Acesse o admin:**
   ```
   http://localhost:8000/admin/
   ```

2. **Faça login:**
   - Usuário: `admin` (ou seu usuário)
   - Senha: sua senha

3. **Vá em "Planos de Assinatura"** (ou "Plano Assinaturas")

4. **Clique em "Adicionar Plano de Assinatura"**

5. **Preencha os dados:**
   - **Nome:** Ex: "Básico", "Profissional", "Enterprise"
   - **Slug:** Ex: "basico", "profissional", "enterprise" (sem espaços, minúsculas)
   - **Descrição:** Descrição do plano
   - **Preço Mensal Referência:** Ex: 99.00 (em reais)
   - **Ativo:** ✅ Marque como ativo
   - **Stripe Price ID:** (opcional, se usar Stripe)

6. **Salve o plano**

7. **Repita para criar mais planos**

### **Opção 2: Via Shell do Django (Script)**

Execute no terminal:

```python
python manage.py shell
```

Depois cole este código:

```python
from gestao_rural.models import PlanoAssinatura

# Criar plano Básico
plano_basico, created = PlanoAssinatura.objects.get_or_create(
    slug='basico',
    defaults={
        'nome': 'Básico',
        'descricao': 'Plano ideal para pequenos produtores',
        'preco_mensal_referencia': 99.00,
        'ativo': True,
    }
)
if created:
    print('✅ Plano Básico criado!')
else:
    print('ℹ️ Plano Básico já existe')

# Criar plano Profissional
plano_pro, created = PlanoAssinatura.objects.get_or_create(
    slug='profissional',
    defaults={
        'nome': 'Profissional',
        'descricao': 'Plano completo para médios produtores',
        'preco_mensal_referencia': 199.00,
        'ativo': True,
    }
)
if created:
    print('✅ Plano Profissional criado!')
else:
    print('ℹ️ Plano Profissional já existe')

# Criar plano Enterprise
plano_enterprise, created = PlanoAssinatura.objects.get_or_create(
    slug='enterprise',
    defaults={
        'nome': 'Enterprise',
        'descricao': 'Plano completo para grandes propriedades',
        'preco_mensal_referencia': 399.00,
        'ativo': True,
    }
)
if created:
    print('✅ Plano Enterprise criado!')
else:
    print('ℹ️ Plano Enterprise já existe')

print('\n🎉 Planos criados com sucesso!')
```

### **Opção 3: Script Python Automático**

Crie um arquivo `criar_planos.py` na raiz do projeto:

```python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import PlanoAssinatura

planos = [
    {
        'slug': 'basico',
        'nome': 'Básico',
        'descricao': 'Plano ideal para pequenos produtores',
        'preco_mensal_referencia': 99.00,
    },
    {
        'slug': 'profissional',
        'nome': 'Profissional',
        'descricao': 'Plano completo para médios produtores',
        'preco_mensal_referencia': 199.00,
    },
    {
        'slug': 'enterprise',
        'nome': 'Enterprise',
        'descricao': 'Plano completo para grandes propriedades',
        'preco_mensal_referencia': 399.00,
    },
]

for plano_data in planos:
    plano, created = PlanoAssinatura.objects.get_or_create(
        slug=plano_data['slug'],
        defaults={
            **plano_data,
            'ativo': True,
        }
    )
    if created:
        print(f"✅ Plano {plano.nome} criado!")
    else:
        print(f"ℹ️ Plano {plano.nome} já existe")

print('\n🎉 Processo concluído!')
```

Execute:
```bash
python criar_planos.py
```

---

## 🔄 **REINICIAR O SERVIDOR**

Após desativar o modo demo, **reinicie o servidor Django**:

```powershell
# Parar o servidor (Ctrl+C)
# Depois iniciar novamente:
python manage.py runserver
```

---

## ✅ **VERIFICAR SE FUNCIONOU**

1. **Acesse:** `http://localhost:8000/assinaturas/`

2. **Deve mostrar:**
   - ✅ Os planos criados
   - ✅ Botão "Assinar agora" em cada plano
   - ✅ Preços e descrições

3. **Teste acesso completo:**
   - ✅ `http://localhost:8000/dashboard/` - Deve funcionar
   - ✅ `http://localhost:8000/propriedade/2/pecuaria/` - Deve funcionar
   - ✅ Todas as rotas devem estar acessíveis

---

## 🎯 **RESUMO**

### **Para Desativar Demo:**
```python
# Em sistema_rural/settings.py linha 199:
DEMO_MODE = os.getenv('DEMO_MODE', 'False').lower() == 'true'  # DESATIVADO
```

### **Para Criar Planos:**
1. Via Admin: `/admin/` → Planos de Assinatura
2. Via Shell: `python manage.py shell` → Cole o código
3. Via Script: `python criar_planos.py`

### **Reiniciar Servidor:**
```bash
python manage.py runserver
```

---

**🎉 Agora você tem acesso à versão completa do sistema!**





