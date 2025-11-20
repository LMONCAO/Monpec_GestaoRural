@echo off
cls
echo ================================================
echo   ATUALIZANDO SISTEMA COM NAVEGACAO MELHORADA
echo ================================================
echo.
echo Transferindo templates para o servidor...
echo.

echo [1/4] Base com navegacao...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\templates\base_navegacao.html root@191.252.225.106:/var/www/monpec.com.br/templates/

echo.
echo [2/4] Propriedades...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\templates\propriedades_navegacao.html root@191.252.225.106:/var/www/monpec.com.br/templates/gestao_rural/propriedades_lista.html

echo.
echo [3/4] Dashboard Pecuaria...
scp -i "C:\Users\lmonc\Downloads\monpecprojetista.key" C:\Monpec_projetista\templates\pecuaria_navegacao.html root@191.252.225.106:/var/www/monpec.com.br/templates/gestao_rural/pecuaria_dashboard.html

echo.
echo [4/4] Reiniciando sistema...
ssh -i "C:\Users\lmonc\Downloads\monpecprojetista.key" root@191.252.225.106 "pkill -9 python; sleep 2; cd /var/www/monpec.com.br && source venv/bin/activate && nohup python manage.py runserver 127.0.0.1:8000 > /tmp/django.log 2>&1 &"

timeout /t 3 /nobreak >nul

echo.
echo ================================================
echo   SISTEMA ATUALIZADO COM SUCESSO!
echo ================================================
echo.
echo MELHORIAS APLICADAS:
echo.
echo - Menu lateral elegante
echo - Breadcrumbs (migalhas de pao)
echo - Navegacao intuitiva
echo - Botoes de acao claros
echo - Visual profissional e clean
echo - SEM icones desnecessarios
echo.
echo Acesse: http://191.252.225.106
echo.
echo Usuario: admin
echo Senha: 123456
echo.
pause

