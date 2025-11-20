#!/usr/bin/env python3
"""
Script para adicionar a view e URL de módulos da propriedade
"""

# Código da view para adicionar
VIEW_CODE = '''
@login_required
def propriedade_modulos(request, propriedade_id):
    """Exibe os módulos disponíveis para uma propriedade"""
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    context = {
        'propriedade': propriedade,
    }
    
    return render(request, 'gestao_rural/propriedade_modulos.html', context)
'''

# URL para adicionar
URL_LINE = "    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),\n"

# Adicionar ao views.py
print("=" * 60)
print("ADICIONAR NO ARQUIVO: gestao_rural/views.py")
print("=" * 60)
print("\nAdicione esta função (após propriedade_excluir):\n")
print(VIEW_CODE)

# Adicionar ao urls.py
print("\n" + "=" * 60)
print("ADICIONAR NO ARQUIVO: gestao_rural/urls.py")
print("=" * 60)
print("\nAdicione esta linha (após propriedade_excluir):\n")
print(URL_LINE)

print("\n" + "=" * 60)
print("COMANDOS NO CONSOLE WEB:")
print("=" * 60)
print("""
# Adicionar view
cd /var/www/monpec.com.br
cat >> gestao_rural/views.py << 'EOF'

@login_required
def propriedade_modulos(request, propriedade_id):
    \"\"\"Exibe os módulos disponíveis para uma propriedade\"\"\"
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    
    context = {
        'propriedade': propriedade,
    }
    
    return render(request, 'gestao_rural/propriedade_modulos.html', context)
EOF

# Reiniciar Django
pkill -9 python
sleep 2
cd /var/www/monpec.com.br
source venv/bin/activate
python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &
""")

