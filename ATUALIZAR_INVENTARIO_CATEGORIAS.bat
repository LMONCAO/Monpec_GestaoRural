@echo off
cls
echo ============================================
echo   ATUALIZANDO INVENTARIO E CATEGORIAS
echo ============================================
echo.

echo [1/8] Transferindo categorias padrao...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\gestao_rural\fixtures\categorias_padrao.json root@191.252.225.106:/var/www/monpec.com.br/gestao_rural/fixtures/

echo.
echo [2/8] Transferindo comando de carga...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\gestao_rural\management\commands\carregar_categorias_padrao.py root@191.252.225.106:/var/www/monpec.com.br/gestao_rural/management/commands/

echo.
echo [3/8] Transferindo __init__.py...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\gestao_rural\management\__init__.py root@191.252.225.106:/var/www/monpec.com.br/gestao_rural/management/

echo.
echo [4/8] Transferindo __init__.py commands...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\gestao_rural\management\commands\__init__.py root@191.252.225.106:/var/www/monpec.com.br/gestao_rural/management/commands/

echo.
echo [5/8] Transferindo template de categorias...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\templates\categorias_clean.html root@191.252.225.106:/var/www/monpec.com.br/templates/gestao_rural/categorias_lista.html

echo.
echo [6/8] Transferindo template de inventario...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\templates\inventario_clean.html root@191.252.225.106:/var/www/monpec.com.br/templates/gestao_rural/pecuaria_inventario.html

echo.
echo [7/8] Atualizando propriedades...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\templates\propriedades_corrigido.html root@191.252.225.106:/var/www/monpec.com.br/templates/gestao_rural/propriedades_lista.html

echo.
echo ============================================
echo   ARQUIVOS TRANSFERIDOS COM SUCESSO!
echo ============================================
echo.
echo Agora execute no CONSOLE WEB da Locaweb:
echo.
echo --- BLOCO 1: Criar diretorios ---
echo mkdir -p /var/www/monpec.com.br/gestao_rural/fixtures
echo mkdir -p /var/www/monpec.com.br/gestao_rural/management/commands
echo.
echo --- BLOCO 2: Carregar categorias ---
echo cd /var/www/monpec.com.br
echo source venv/bin/activate
echo python manage.py carregar_categorias_padrao
echo.
echo --- BLOCO 3: Adicionar view de modulos ---
echo echo "" ^>^> gestao_rural/views.py
echo echo "@login_required" ^>^> gestao_rural/views.py
echo echo "def propriedade_modulos(request, propriedade_id):" ^>^> gestao_rural/views.py
echo echo "    propriedade = get_object_or_404(Propriedade, pk=propriedade_id)" ^>^> gestao_rural/views.py
echo echo "    context = {\"propriedade\": propriedade}" ^>^> gestao_rural/views.py
echo echo "    return render(request, \"gestao_rural/propriedade_modulos.html\", context)" ^>^> gestao_rural/views.py
echo.
echo --- BLOCO 4: Adicionar URL de modulos ---
echo sed -i "/name=.propriedade_excluir/a\    path(\"propriedade/^<int:propriedade_id^>/modulos/\", views.propriedade_modulos, name=\"propriedade_modulos\")," gestao_rural/urls.py
echo.
echo --- BLOCO 5: Reiniciar Django ---
echo pkill -9 python
echo sleep 2
echo cd /var/www/monpec.com.br
echo source venv/bin/activate
echo python manage.py runserver 127.0.0.1:8000 ^> /tmp/django.log 2^>^&1 ^&
echo.
pause

