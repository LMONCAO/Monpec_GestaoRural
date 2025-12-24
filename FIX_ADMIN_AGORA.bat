@echo off
cd /d "%~dp0"
echo ========================================
echo CORRIGINDO SENHA DO ADMIN
echo ========================================
echo.

python manage.py shell -c "from django.contrib.auth import get_user_model, authenticate; User = get_user_model(); username='admin'; password='L6171r12@@'; user, created = User.objects.get_or_create(username=username, defaults={'email': 'admin@monpec.com.br', 'is_staff': True, 'is_superuser': True, 'is_active': True}); user.set_password(password); user.is_staff=True; user.is_superuser=True; user.is_active=True; user.email='admin@monpec.com.br'; user.save(); print('✅ Usuario admin atualizado!' if not created else '✅ Usuario admin criado!'); print('Username: admin'); print('Password: L6171r12@@'); auth_test = authenticate(username=username, password=password); print('✅ Autenticacao: SUCESSO' if auth_test else '❌ Autenticacao: FALHOU')"

echo.
echo ========================================
pause

















