@echo off
echo ============================================
echo   APLICANDO DESIGN CLEAN NO SERVIDOR
echo ============================================
echo.

echo [1/5] Transferindo base template...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\templates\base_clean.html root@191.252.225.106:/var/www/monpec.com.br/templates/

echo.
echo [2/5] Transferindo propriedades template...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\templates\propriedades_lista_clean.html root@191.252.225.106:/var/www/monpec.com.br/templates/gestao_rural/propriedades_lista.html

echo.
echo [3/5] Transferindo pecuaria dashboard...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\templates\pecuaria_dashboard_clean.html root@191.252.225.106:/var/www/monpec.com.br/templates/gestao_rural/pecuaria_dashboard.html

echo.
echo [4/5] Transferindo login...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\templates\login_clean.html root@191.252.225.106:/var/www/monpec.com.br/templates/gestao_rural/login.html

echo.
echo [5/5] Reiniciando Django...
ssh -i "C:\Users\lmonc\Downloads\monpecprojetista.key" root@191.252.225.106 "pkill -9 python && cd /var/www/monpec.com.br && source venv/bin/activate && nohup python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &"

timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo   DESIGN CLEAN APLICADO COM SUCESSO!
echo ============================================
echo.
echo Acesse: http://191.252.225.106
echo.
echo CARACTERISTICAS DO NOVO DESIGN:
echo - Visual limpo e elegante
echo - SEM icones ou figuras
echo - Tipografia profissional
echo - Cores: Azul Marinho + Cinza + Marrom Terra
echo - Layout minimalista
echo.
pause

