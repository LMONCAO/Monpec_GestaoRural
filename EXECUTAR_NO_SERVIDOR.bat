@echo off
echo ============================================================
echo COMANDO PARA EXECUTAR NO SERVIDOR DE PRODUÇÃO
echo ============================================================
echo.
echo Este comando deve ser executado NO SERVIDOR (via SSH),
echo NÃO no seu PC local!
echo.
echo ============================================================
echo COPIE E COLE O COMANDO ABAIXO NO SERVIDOR:
echo ============================================================
echo.
echo python manage.py shell -c "from django.contrib.auth import get_user_model, authenticate; User = get_user_model(); username = 'admin'; password = 'L6171r12@@'; user, created = User.objects.get_or_create(username=username, defaults={'email': 'admin@monpec.com.br', 'is_staff': True, 'is_superuser': True, 'is_active': True}); user.set_password(password); user.is_staff = True; user.is_superuser = True; user.is_active = True; user.email = 'admin@monpec.com.br'; user.save(); print('✅ Admin corrigido!'); print(f'Username: {username}'); print(f'Password: {password}'); auth = authenticate(username=username, password=password); print(f'✅ Autenticacao: {\"SUCESSO\" if auth else \"FALHOU\"}')"
echo.
echo ============================================================
pause












