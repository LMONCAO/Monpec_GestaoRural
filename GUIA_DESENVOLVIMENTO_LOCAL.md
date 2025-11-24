# 💻 Guia de Desenvolvimento Local

## 🚀 Iniciar Servidor

### Método 1: Script Automático
```powershell
.\INICIAR_SERVIDOR_LOCAL.ps1
```

### Método 2: Manual
```powershell
# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Iniciar servidor
python manage.py runserver

# Ou em outra porta
python manage.py runserver 8001
```

### Acessar
- **URL:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/

---

## 🔧 Comandos Úteis

### Criar Migrações
```powershell
python manage.py makemigrations
```

### Aplicar Migrações
```powershell
python manage.py migrate
```

### Criar Superusuário
```powershell
python manage.py createsuperuser
```

### Shell do Django
```powershell
python manage.py shell
```

### Coletar Arquivos Estáticos
```powershell
python manage.py collectstatic
```

### Verificar URLs
```powershell
python manage.py show_urls
```

---

## 🐛 Debug e Desenvolvimento

### Modo Debug
O `settings.py` já tem `DEBUG = True` para desenvolvimento.

### Ver Erros
- Erros aparecem na tela (modo debug)
- Logs no console do terminal

### Hot Reload
O Django recarrega automaticamente quando você salva arquivos!

---

## 📝 Estrutura do Projeto

```
Monpec_GestaoRural/
├── gestao_rural/          # App principal
│   ├── models.py         # Modelos de dados
│   ├── views.py          # Views principais
│   ├── urls.py           # URLs do app
│   └── templates/        # Templates HTML
├── sistema_rural/         # Configurações Django
│   ├── settings.py       # Settings desenvolvimento
│   ├── settings_gcp.py   # Settings produção
│   └── urls.py           # URLs principais
├── templates/            # Templates globais
├── static/              # Arquivos estáticos
├── manage.py            # Script de gerenciamento
└── requirements.txt     # Dependências
```

---

## 🎯 Áreas para Melhorar

### 1. Adicionar Mais Páginas ao Sitemap
Edite `gestao_rural/sitemaps.py`:
```python
def items(self):
    return [
        'landing_page',
        'outra_pagina_publica',  # Adicione aqui
    ]
```

### 2. Melhorar SEO
- Adicionar meta descriptions
- Otimizar títulos
- Adicionar structured data

### 3. Performance
- Otimizar queries do banco
- Adicionar cache
- Otimizar imagens

### 4. Funcionalidades
- Adicionar novas features
- Melhorar UX
- Corrigir bugs

---

## 🔄 Workflow de Desenvolvimento

### 1. Desenvolver Localmente
```powershell
# Iniciar servidor
python manage.py runserver

# Fazer alterações
# Testar no navegador
```

### 2. Testar
- Testar funcionalidades
- Verificar erros
- Testar em diferentes navegadores

### 3. Commit e Push
```powershell
git add .
git commit -m "Descrição das alterações"
git push origin master
```

### 4. Deploy (quando necessário)
```bash
# No Cloud Shell
cd ~/Monpec_GestaoRural
git pull origin master
# ... comandos de deploy
```

---

## 📚 Recursos Úteis

### Documentação Django
- https://docs.djangoproject.com/

### Django Admin
- http://127.0.0.1:8000/admin/

### Logs
- Veja no terminal onde o servidor está rodando

---

## ✅ Checklist de Desenvolvimento

- [ ] Servidor local rodando
- [ ] Fazer alterações
- [ ] Testar no navegador
- [ ] Verificar erros
- [ ] Commit e push
- [ ] Deploy (quando necessário)

---

**Boa sorte com o desenvolvimento!** 💻🚀












