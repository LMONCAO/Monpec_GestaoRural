#!/usr/bin/env python3
"""
Script para adicionar automaticamente a URL e View de propriedade_modulos
"""

VIEW_CODE = """

@login_required
def propriedade_modulos(request, propriedade_id):
    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)
    context = {'propriedade': propriedade}
    return render(request, 'gestao_rural/propriedade_modulos.html', context)
"""

URL_CODE = "    path('propriedade/<int:propriedade_id>/modulos/', views.propriedade_modulos, name='propriedade_modulos'),\n"

print("="*70)
print("COMANDOS PARA EXECUTAR NO CONSOLE WEB DA LOCAWEB")
print("="*70)
print("\n### 1. ADICIONAR VIEW ###\n")
print("cd /var/www/monpec.com.br")
print('echo "" >> gestao_rural/views.py')
print('echo "@login_required" >> gestao_rural/views.py')
print('echo "def propriedade_modulos(request, propriedade_id):" >> gestao_rural/views.py')
print('echo "    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)" >> gestao_rural/views.py')
print('echo "    context = {\\"propriedade\\": propriedade}" >> gestao_rural/views.py')
print('echo "    return render(request, \\"gestao_rural/propriedade_modulos.html\\", context)" >> gestao_rural/views.py')

print("\n### 2. ADICIONAR URL ###\n")
print('sed -i "/name=.propriedade_excluir/a\\    path(\\"propriedade/<int:propriedade_id>/modulos/\\", views.propriedade_modulos, name=\\"propriedade_modulos\\")," gestao_rural/urls.py')

print("\n### 3. VERIFICAR ###\n")
print("tail -10 gestao_rural/views.py")
print("grep propriedade_modulos gestao_rural/urls.py")

print("\n### 4. REINICIAR DJANGO ###\n")
print("pkill -9 python")
print("sleep 2")
print("cd /var/www/monpec.com.br")
print("source venv/bin/activate")
print("python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &")
print("sleep 3")
print("ps aux | grep manage")

print("\n" + "="*70)
print("COPIE E COLE CADA COMANDO ACIMA NO CONSOLE WEB!")
print("="*70)

