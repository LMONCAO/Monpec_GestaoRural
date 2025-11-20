@echo off
echo Executando migracao para criar tabela de Mensagens WhatsApp...
python manage.py migrate gestao_rural 0046_add_whatsapp_mensagens
echo.
echo Migracao concluida! Pressione qualquer tecla para continuar...
pause




