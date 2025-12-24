@echo off
echo ========================================
echo CORRIGINDO SENHA DO USUARIO ADMIN
echo ========================================
echo.

python manage.py shell -c "from django.contrib.auth import get_user_model, authenticate; User = get_user_model(); username='admin'; password='L6171r12@@'; user, created = User.objects.get_or_create(username=username, defaults={'email': 'admin@monpec.com.br', 'is_staff': True, 'is_superuser': True, 'is_active': True}); user.set_password(password); user.is_staff=True; user.is_superuser=True; user.is_active=True; user.save(); print('✅ Usuario admin atualizado!' if not created else '✅ Usuario admin criado!'); print(f'Username: {username}'); print(f'Password: {password}'); auth_test = authenticate(username=username, password=password); print(f'✅ Autenticacao teste: {'SUCESSO' if auth_test else 'FALHOU'}')"

echo.
echo ========================================
echo Processo concluido!
echo ========================================
pause

















