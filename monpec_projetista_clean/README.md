# MONPEC PROJETISTA - Sistema de Gestão Rural

Sistema completo para elaboração de projetos bancários rurais.

## Instalação

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Ativar ambiente (Linux/Mac)
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar banco de dados
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver
```

## Estrutura do Projeto

- `gestao_rural/` - App principal com todos os módulos
- `monpec_project/` - Configurações do Django
- `static/` - Arquivos estáticos (CSS, JS, imagens)
- `templates/` - Templates HTML

## Módulos

1. **Produtores e Propriedades** - Cadastro base
2. **Pecuária** - Gestão de rebanho com IA
3. **Agricultura** - Ciclos produtivos
4. **Bens e Patrimônio** - Gestão patrimonial
5. **Financeiro** - Custos e dívidas
6. **Projetos Bancários** - Consolidação e relatórios

## Desenvolvido com

- Django 4.2.7
- Python 3.11+
- Bootstrap 5
- ReportLab (PDF)
- OpenPyXL (Excel)
