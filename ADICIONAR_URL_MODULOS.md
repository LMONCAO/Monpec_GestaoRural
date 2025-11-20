# 🔧 ADICIONAR URL E VIEW PARA MÓDULOS DA PROPRIEDADE

## 📋 O QUE FAZER:

Adicionar no servidor a URL e view para mostrar os módulos de uma propriedade.

---

## 1️⃣ ADICIONAR NO `gestao_rural/urls.py`

Adicione esta linha após a linha de propriedades:

```python
path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),
```

**Localização:** Após a linha:
```python
path('propriedade/<int:propriedade_id>/excluir/', views.propriedade_excluir, name='propriedade_excluir'),
```

---

## 2️⃣ ADICIONAR NO `gestao_rural/views.py`

Adicione esta função:

```python
@login_required
def propriedade_modulos(request, propriedade_id):
    """Exibe os módulos disponíveis para uma propriedade"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    context = {
        'propriedade': propriedade,
    }
    
    return render(request, 'gestao_rural/propriedade_modulos.html', context)
```

**Localização:** Após a função `propriedade_excluir` ou junto com as outras views de propriedade.

---

## 3️⃣ COMANDOS PARA EXECUTAR NO CONSOLE WEB:

```bash
# 1. Editar urls.py
cd /var/www/monpec.com.br
nano gestao_rural/urls.py

# Adicione a linha após propriedade_excluir:
# path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),

# Salvar: Ctrl+O, Enter, Ctrl+X

# 2. Editar views.py
nano gestao_rural/views.py

# Adicione a função propriedade_modulos (código acima)

# Salvar: Ctrl+O, Enter, Ctrl+X

# 3. Reiniciar Django
pkill -9 python
sleep 2
cd /var/www/monpec.com.br
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &
```

---

## ✅ RESULTADO:

Após adicionar:

1. Dashboard → **Propriedades**
2. Clica em "Acessar" → **Módulos da Propriedade** (NOVO!)
3. Escolhe o módulo → Pecuária / Agricultura / Relatórios

---

## 📌 ESTRUTURA COMPLETA:

```
Dashboard
  └─ Propriedades
       └─ [Clica em "Acessar"]
            └─ MÓDULOS DA PROPRIEDADE ← NOVA PÁGINA!
                 ├─ Pecuária
                 ├─ Agricultura
                 ├─ Financeiro (em desenvolvimento)
                 ├─ Relatórios
                 ├─ Configurações
                 └─ Categorias
```

