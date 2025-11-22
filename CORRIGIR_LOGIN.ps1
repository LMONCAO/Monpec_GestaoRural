# Script para corrigir problemas de login
# Este script ajuda a diagnosticar e corrigir problemas com login e senha

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CORREÇÃO DE PROBLEMAS DE LOGIN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$username = Read-Host "Digite o nome de usuário que está com problema"

if (-not $username) {
    Write-Host "❌ Nome de usuário não informado!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Verificando usuário no banco de dados..." -ForegroundColor Yellow

# Criar script Python temporário para diagnóstico
$scriptPython = @"
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.cache import cache
from gestao_rural.models_auditoria import VerificacaoEmail
from django.db import OperationalError

username = '$username'

print(f'\n{"="*60}')
print(f'DIAGNÓSTICO DO USUÁRIO: {username}')
print(f'{"="*60}\n')

# Verificar se usuário existe
try:
    user = User.objects.get(username=username)
    print(f'✅ Usuário encontrado!')
    print(f'   - Nome completo: {user.get_full_name() or "Não informado"}')
    print(f'   - E-mail: {user.email or "Não informado"}')
    print(f'   - Ativo: {"SIM" if user.is_active else "NÃO (❌ BLOQUEADO)"}')
    print(f'   - Staff: {"SIM" if user.is_staff else "NÃO"}')
    print(f'   - Superuser: {"SIM" if user.is_superuser else "NÃO"}')
    print(f'   - Data de criação: {user.date_joined}')
    print(f'   - Último login: {user.last_login or "Nunca"}')
    
    # Verificar bloqueio por tentativas
    chave_usuario = f'login_attempts_user_{username}'
    tentativas_usuario = cache.get(chave_usuario, 0)
    ttl_usuario = cache.ttl(chave_usuario)
    
    if tentativas_usuario > 0:
        if ttl_usuario:
            minutos = int(ttl_usuario / 60)
            segundos = int(ttl_usuario % 60)
            print(f'\n⚠️ BLOQUEIO POR TENTATIVAS:')
            print(f'   - Tentativas falhas: {tentativas_usuario}/5')
            print(f'   - Tempo restante: {minutos}min {segundos}s')
        else:
            print(f'\n⚠️ BLOQUEIO POR TENTATIVAS:')
            print(f'   - Tentativas falhas: {tentativas_usuario}/5')
            print(f'   - Tempo restante: Desconhecido')
    else:
        print(f'\n✅ Nenhum bloqueio por tentativas')
    
    # Verificar verificação de e-mail
    try:
        verificacao = VerificacaoEmail.objects.get(usuario=user)
        if not verificacao.email_verificado:
            print(f'\n⚠️ VERIFICAÇÃO DE E-MAIL PENDENTE:')
            print(f'   - E-mail não foi verificado')
            print(f'   - Token expira em: {verificacao.token_expira_em}')
            print(f'   - Tentativas: {verificacao.tentativas_verificacao}/5')
        else:
            print(f'\n✅ E-mail verificado')
    except VerificacaoEmail.DoesNotExist:
        print(f'\n✅ Nenhuma verificação de e-mail obrigatória (usuário antigo)')
    except OperationalError as e:
        print(f'\n⚠️ Erro ao verificar e-mail (tabela pode não existir): {e}')
    
    print(f'\n{"="*60}')
    print(f'OPÇÕES DE CORREÇÃO:')
    print(f'{"="*60}')
    print(f'1. Limpar bloqueio por tentativas')
    print(f'2. Marcar e-mail como verificado (se houver)')
    print(f'3. Ativar usuário (se estiver desabilitado)')
    print(f'4. Redefinir senha')
    print(f'5. Todas as correções acima')
    
except User.DoesNotExist:
    print(f'\n❌ Usuário "{username}" não encontrado!')
    print(f'\nVerifique se o nome de usuário está correto.')
    exit(1)
except Exception as e:
    print(f'\n❌ Erro ao verificar usuário: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"@

$scriptPython | Out-File -FilePath "diagnostico_login_temp.py" -Encoding UTF8

# Executar diagnóstico
python311\python.exe diagnostico_login_temp.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Deseja aplicar correções? (S/N): " -ForegroundColor Yellow -NoNewline
    $aplicar = Read-Host
    
    if ($aplicar -eq "S" -or $aplicar -eq "s") {
        Write-Host ""
        Write-Host "Escolha a correção:" -ForegroundColor Yellow
        Write-Host "1. Limpar bloqueio por tentativas"
        Write-Host "2. Marcar e-mail como verificado"
        Write-Host "3. Ativar usuário"
        Write-Host "4. Redefinir senha"
        Write-Host "5. Todas as correções"
        Write-Host ""
        $opcao = Read-Host "Digite o número da opção (1-5)"
        
        $scriptCorrecao = @"
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User
from django.core.cache import cache
from gestao_rural.models_auditoria import VerificacaoEmail
from django.db import OperationalError
from django.utils import timezone
from django.contrib.auth.hashers import make_password

username = '$username'
opcao = '$opcao'

try:
    user = User.objects.get(username=username)
    print(f'\nAplicando correções para: {username}\n')
    
    # Limpar bloqueio por tentativas
    if opcao in ['1', '5']:
        chave_usuario = f'login_attempts_user_{username}'
        cache.delete(chave_usuario)
        print('✅ Bloqueio por tentativas limpo')
    
    # Marcar e-mail como verificado
    if opcao in ['2', '5']:
        try:
            verificacao = VerificacaoEmail.objects.get(usuario=user)
            if not verificacao.email_verificado:
                verificacao.email_verificado = True
                verificacao.verificado_em = timezone.now()
                verificacao.save()
                print('✅ E-mail marcado como verificado')
            else:
                print('ℹ️  E-mail já estava verificado')
        except VerificacaoEmail.DoesNotExist:
            print('ℹ️  Nenhuma verificação de e-mail para este usuário')
        except OperationalError as e:
            print(f'⚠️  Erro ao verificar e-mail: {e}')
    
    # Ativar usuário
    if opcao in ['3', '5']:
        if not user.is_active:
            user.is_active = True
            user.save()
            print('✅ Usuário ativado')
        else:
            print('ℹ️  Usuário já estava ativo')
    
    # Redefinir senha
    if opcao in ['4', '5']:
        import getpass
        senha_nova = input('Digite a nova senha: ')
        if senha_nova:
            user.set_password(senha_nova)
            user.save()
            print('✅ Senha redefinida com sucesso')
        else:
            print('⚠️  Senha não foi alterada (campo vazio)')
    
    print(f'\n✅ Correções aplicadas com sucesso!')
    print(f'\nAgora você pode tentar fazer login novamente.')
    
except User.DoesNotExist:
    print(f'❌ Usuário não encontrado!')
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
"@
        
        $scriptCorrecao | Out-File -FilePath "corrigir_login_temp.py" -Encoding UTF8
        python311\python.exe corrigir_login_temp.py
    }
}

# Limpar arquivos temporários
if (Test-Path "diagnostico_login_temp.py") { Remove-Item "diagnostico_login_temp.py" }
if (Test-Path "corrigir_login_temp.py") { Remove-Item "corrigir_login_temp.py" }

Write-Host ""
Write-Host "Pressione qualquer tecla para sair..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
