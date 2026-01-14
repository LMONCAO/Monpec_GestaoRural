from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, F, Case, When, IntegerField, Count, Min, Value
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .decorators import bloquear_demo_cadastro
import logging
import os
from datetime import datetime, timedelta, date
from decimal import Decimal, InvalidOperation
import json
import urllib.parse

logger = logging.getLogger(__name__)


def _is_usuario_assinante(user):
    """
    Verifica se o usuário é assinante (superusuário ou tem assinatura ativa).
    Retorna True se:
    - É superusuário ou staff
    - Tem assinatura ativa com acesso liberado
    
    NOTA: Esta função mantida para compatibilidade.
    Use helpers_acesso.is_usuario_assinante() em novos códigos.
    """
    from .helpers_acesso import is_usuario_assinante
    return is_usuario_assinante(user)


def _obter_todas_propriedades(user):
    """
    Retorna todas as propriedades disponíveis para o usuário.
    - Administradores/assinantes: todas as propriedades
    - Usuários normais: apenas propriedades dos seus produtores
    """
    from .models import Propriedade
    
    if _is_usuario_assinante(user):
        # Administrador/assinante: ver todas as propriedades
        return Propriedade.objects.select_related('produtor').all().order_by('produtor__nome', 'nome_propriedade')
    else:
        # Usuário normal: apenas propriedades dos seus produtores
        return Propriedade.objects.filter(
            produtor__usuario_responsavel=user
        ).select_related('produtor').order_by('produtor__nome', 'nome_propriedade')


def _garantir_produtor_e_propriedade_padrao(user):
    """
    Garante que o usuário tenha um produtor e uma propriedade padrão.
    Se não existirem, cria automaticamente.
    Retorna a propriedade padrão (criada ou existente).
    """
    from .models import ProdutorRural, Propriedade
    from django.db import ProgrammingError, transaction
    
    try:
        # Verificar se já existe alguma propriedade para o usuário
        propriedades = Propriedade.objects.filter(
            produtor__usuario_responsavel=user
        )
        
        if propriedades.exists():
            # Retornar a primeira propriedade encontrada
            return propriedades.first()
        
        # Se não há propriedades, verificar se existe produtor
        produtores = ProdutorRural.objects.filter(usuario_responsavel=user)
        
        if not produtores.exists():
            # Criar produtor padrão
            nome_produtor = user.get_full_name() or user.username or 'Meu Produtor'
            email_produtor = user.email or f'{user.username}@monpec.com.br'
            
            # Gerar CPF/CNPJ único baseado no ID do usuário
            cpf_cnpj_base = f'{user.id:011d}' if user.id else '00000000000'
            
            # Verificar se já existe esse CPF/CNPJ
            while ProdutorRural.objects.filter(cpf_cnpj=cpf_cnpj_base).exists():
                cpf_cnpj_base = f'{int(cpf_cnpj_base) + 1:011d}'
            
            try:
                with transaction.atomic():
                    produtor = ProdutorRural.objects.create(
                        nome=nome_produtor,
                        cpf_cnpj=cpf_cnpj_base,
                        usuario_responsavel=user,
                        email=email_produtor,
                        telefone='',
                        anos_experiencia=0,
                    )
                    logger.info(f'Produtor padrão criado automaticamente para usuário {user.username}: {produtor.nome}')
            except ProgrammingError as e:
                # Se houver erro (coluna não existe), criar apenas com campos básicos
                logger.warning(f'Erro ao criar produtor (coluna faltando): {e}. Criando apenas com campos básicos.')
                campos_basicos = {
                    'nome': nome_produtor,
                    'cpf_cnpj': cpf_cnpj_base,
                    'usuario_responsavel': user,
                }
                try:
                    produtor = ProdutorRural.objects.create(**campos_basicos, email=email_produtor)
                except ProgrammingError:
                    produtor = ProdutorRural.objects.create(**campos_basicos)
        else:
            produtor = produtores.first()
        
        # Agora garantir que existe uma propriedade
        propriedade = Propriedade.objects.filter(produtor=produtor).first()
        
        if not propriedade:
            # Criar propriedade padrão
            nome_propriedade = 'Minha Propriedade'
            
            # Verificar se já existe propriedade com esse nome para o produtor
            contador = 1
            while Propriedade.objects.filter(produtor=produtor, nome_propriedade=nome_propriedade).exists():
                nome_propriedade = f'Minha Propriedade {contador}'
                contador += 1
            
            try:
                with transaction.atomic():
                    propriedade = Propriedade.objects.create(
                        produtor=produtor,
                        nome_propriedade=nome_propriedade,
                        municipio='Campo Grande',
                        uf='MS',
                        area_total_ha=Decimal('100.00'),
                        tipo_operacao='PECUARIA',
                        tipo_ciclo_pecuario=['CICLO_COMPLETO'],
                        tipo_propriedade='PROPRIA',
                        valor_hectare_proprio=Decimal('5000.00'),
                    )
                    logger.info(f'Propriedade padrão criada automaticamente para usuário {user.username}: {propriedade.nome_propriedade}')
            except ProgrammingError as e:
                logger.warning(f'Erro ao criar propriedade (coluna faltando): {e}. Tentando criar apenas com campos básicos.')
                campos_basicos = {
                    'produtor': produtor,
                    'nome_propriedade': nome_propriedade,
                    'municipio': 'Campo Grande',
                    'uf': 'MS',
                    'area_total_ha': Decimal('100.00'),
                }
                try:
                    propriedade = Propriedade.objects.create(**campos_basicos, tipo_operacao='PECUARIA')
                except ProgrammingError:
                    propriedade = Propriedade.objects.create(**campos_basicos)
        
        return propriedade
        
    except Exception as e:
        logger.error(f'Erro ao garantir produtor e propriedade padrão para usuário {user.username}: {e}')
        return None


def google_search_console_verification(request):
    """
    Serve o arquivo HTML de verificação do Google Search Console.
    Arquivo: google40933139f3b0d469.html
    O conteúdo deste arquivo é fornecido pelo Google Search Console quando você
    seleciona o método de verificação via arquivo HTML.
    """
    # Conteúdo do arquivo de verificação do Google Search Console
    # O Google espera que o arquivo contenha exatamente: google-site-verification: google40933139f3b0d469.html
    content = "google-site-verification: google40933139f3b0d469.html"
    return HttpResponse(content, content_type='text/html; charset=utf-8')




def health_check(request):
    """
    Endpoint de health check robusto para monitoramento do Google Cloud Run.
    Verifica banco de dados, cache e outras dependências críticas.
    """
    from django.db import connection
    from django.core.cache import cache
    from django.conf import settings
    import time
    import json

    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {},
        'version': '1.0.0'
    }

    # Verificar banco de dados
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            health_status['checks']['database'] = {
                'status': 'healthy',
                'response_time': time.time(),
                'details': 'Connection successful'
            }
    except Exception as e:
        health_status['status'] = 'unhealthy'
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'error': str(e),
            'response_time': time.time()
        }

    # Verificar cache
    try:
        cache_key = f'health_check_{int(time.time())}'
        cache.set(cache_key, 'test_value', 10)
        retrieved_value = cache.get(cache_key)
        if retrieved_value == 'test_value':
            health_status['checks']['cache'] = {
                'status': 'healthy',
                'response_time': time.time(),
                'details': 'Cache read/write successful'
            }
        else:
            health_status['checks']['cache'] = {
                'status': 'unhealthy',
                'error': 'Cache read/write failed',
                'response_time': time.time()
            }
    except Exception as e:
        health_status['checks']['cache'] = {
            'status': 'unhealthy',
            'error': str(e),
            'response_time': time.time()
        }

    # Verificar configurações críticas
    try:
        critical_settings = [
            'SECRET_KEY',
            'DATABASES',
            'ALLOWED_HOSTS'
        ]
        missing_settings = []
        for setting in critical_settings:
            if hasattr(settings, setting):
                if setting == 'SECRET_KEY' and not getattr(settings, setting):
                    missing_settings.append(setting)
                elif setting == 'DATABASES' and not getattr(settings, setting):
                    missing_settings.append(setting)
                elif setting == 'ALLOWED_HOSTS' and not getattr(settings, setting):
                    missing_settings.append(setting)
            else:
                missing_settings.append(setting)

        if missing_settings:
            health_status['checks']['settings'] = {
                'status': 'warning',
                'details': f'Missing critical settings: {", ".join(missing_settings)}',
                'response_time': time.time()
            }
        else:
            health_status['checks']['settings'] = {
                'status': 'healthy',
                'details': 'All critical settings configured',
                'response_time': time.time()
            }
    except Exception as e:
        health_status['checks']['settings'] = {
            'status': 'unhealthy',
            'error': str(e),
            'response_time': time.time()
        }

    # Verificar espaço em disco (se aplicável)
    try:
        import os
        if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
            stat = os.statvfs(settings.MEDIA_ROOT)
            free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            health_status['checks']['disk_space'] = {
                'status': 'healthy' if free_space_gb > 1 else 'warning',
                'details': '.2f',
                'response_time': time.time()
            }
    except Exception as e:
        health_status['checks']['disk_space'] = {
            'status': 'warning',
            'error': f'Could not check disk space: {str(e)}',
            'response_time': time.time()
        }

    # Determinar status geral
    unhealthy_checks = [check for check in health_status['checks'].values()
                       if check.get('status') == 'unhealthy']

    if unhealthy_checks:
        status_code = 503  # Service Unavailable
        health_status['status'] = 'unhealthy'
    else:
        status_code = 200  # OK

    # Retornar resposta JSON detalhada ou simples dependendo do parâmetro
    if request.GET.get('format') == 'json':
        return JsonResponse(health_status, status=status_code)
    else:
        # Resposta simples para compatibilidade com Google Cloud Run health checks
        return HttpResponse(
            health_status['status'].upper(),
            content_type="text/plain",
            status=status_code
        )


def landing_page(request):
    """Página pública do sistema antes do login."""
    # Se o usuário já estiver autenticado, redirecionar para o dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Limpar mensagens antigas que não sejam relacionadas a um envio recente
    # Verificar se há um parâmetro indicando que acabamos de processar um formulário
    if 'form_submitted' not in request.GET:
        # Se não foi um submit recente, limpar todas as mensagens antigas da sessão
        # Isso evita que mensagens de sucesso apareçam quando o usuário apenas acessa a página
        storage = messages.get_messages(request)
        # Consumir todas as mensagens para limpar a sessão
        list(storage)
        # Marcar como usado para garantir limpeza
        storage.used = True

    # Adicionar contexto para indicar se é um logout
    # Isso pode ser usado no template para evitar redirecionamentos automáticos
    context = {
        'is_logout': 'logout' in request.GET,
    }

    # Renderizar a landing page normalmente
    return render(request, 'site/landing_page.html', context)


@csrf_exempt
def criar_usuario_demonstracao(request):
    """Cria usuário para demonstração a partir do popup - VERSÃO SIMPLIFICADA"""
    from django.contrib.auth.models import User
    from django.contrib.auth import login
    from django.urls import reverse
    import urllib.parse
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f'[DEMO_CADASTRO] Iniciando - IP: {request.META.get("REMOTE_ADDR")}')

    # Se for GET, redirecionar para o formulário
    if request.method == 'GET':
        logger.info('[DEMO_CADASTRO] Redirecionando para formulário de criação de usuário')
        return redirect('criando_usuario_demo')

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

    try:
        nome_completo = request.POST.get('nome_completo', '').strip()
        email = request.POST.get('email', '').strip().lower()
        telefone = request.POST.get('telefone', '').strip()

        logger.info(f'[DEMO_CADASTRO] Dados recebidos: nome={nome_completo[:50]}, email={email}')

        # Validação
        if not nome_completo or not email:
            return JsonResponse({
                'success': False,
                'message': 'Por favor, preencha todos os campos obrigatórios.'
            }, status=400)

        # Validar formato de email
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({
                'success': False,
                'message': 'Por favor, informe um e-mail válido.'
            }, status=400)

        # 1. Verificar se usuário existe (case-insensitive)
        # Adicionar tratamento de erro para problemas de conexão com banco
        try:
            user = User.objects.filter(email__iexact=email).first()
        except Exception as db_error:
            logger.error(f'[DEMO_CADASTRO] Erro de conexão com banco de dados: {type(db_error).__name__}: {db_error}', exc_info=True)
            return JsonResponse({
                'success': False,
                'message': 'Erro ao conectar com o banco de dados. Por favor, tente novamente em alguns instantes.'
            }, status=503)
        
        usuario_existente = False
        
        if user:
            # Usu??rio existe - apenas atualizar senha e ativar
            logger.info(f'[DEMO_CADASTRO] Usu??rio existente encontrado: {user.username}')
            user.set_password('monpec')  # Senha padr??o para demo
            user.is_active = True
            user.save()
            usuario_existente = True

            # IMPORTANTE: Criar registro UsuarioAtivo para identificar como usuário demo
            from .models_auditoria import UsuarioAtivo
            try:
                usuario_ativo, created = UsuarioAtivo.objects.get_or_create(
                    usuario=user,
                    defaults={
                        'nome_completo': nome_completo,
                        'email': email,
                        'telefone': telefone or '',
                    }
                )
                logger.info(f'[DEMO_CADASTRO] UsuarioAtivo criado/atualizado: {usuario_ativo.usuario.username} (criado: {created})')
            except Exception as e:
                logger.warning(f'[DEMO_CADASTRO] Erro ao criar UsuarioAtivo para usuário existente: {e}')
        else:
            # Criar novo usu??rio
            logger.info(f'[DEMO_CADASTRO] Criando novo usu??rio...')
            import os
            try:
                username = email.split('@')[0]
                # Garantir username ??nico
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                demo_password = os.getenv('DEMO_USER_PASSWORD', 'monpec')
                user = User.objects.create_user(
                    username=username,
                    email=email.lower(),
                    password=demo_password,
                    first_name=nome_completo.split()[0] if nome_completo else '',
                    last_name=' '.join(nome_completo.split()[1:]) if len(nome_completo.split()) > 1 else '',
                    is_active=True,
                )
                logger.info(f'[DEMO_CADASTRO] Usu??rio criado: {user.username} (ID: {user.id})')
            except Exception as db_error:
                logger.error(f'[DEMO_CADASTRO] Erro ao criar usu??rio no banco: {type(db_error).__name__}: {db_error}', exc_info=True)
                return JsonResponse({
                    'success': False,
                    'message': 'Erro ao criar usu??rio. Por favor, tente novamente em alguns instantes.'
                }, status=503)
        
        # 2. Criar registro UsuarioAtivo para identificar como usuário demo
        from .models_auditoria import UsuarioAtivo
        try:
            logger.info(f'[DEMO_CADASTRO] Criando UsuarioAtivo para usuário: {user.username} (email: {email})')
            usuario_ativo, created = UsuarioAtivo.objects.get_or_create(
                usuario=user,
                defaults={
                    'nome_completo': nome_completo,
                    'email': email,
                    'telefone': telefone or '',
                }
            )
            logger.info(f'[DEMO_CADASTRO] UsuarioAtivo criado para novo usuário: {usuario_ativo.usuario.username} (ID: {usuario_ativo.id}, criado: {created})')


        except Exception as e:
            logger.error(f'[DEMO_CADASTRO] Erro ao criar UsuarioAtivo para novo usuário: {e}', exc_info=True)

        # 3. NÃO criar dados aqui - deixar para o demo_setup fazer isso
        # Isso evita deadlock no banco de dados
        logger.info(f'[DEMO_CADASTRO] Usuário criado. Dados serão criados pelo demo_setup.')

        # 3.1. ENVIAR NOTIFICAÇÕES PARA ADMIN (EMAIL E WHATSAPP)
        try:
            from .services_notificacoes_demo import notificar_cadastro_demo
            ip_address = request.META.get('REMOTE_ADDR')
            notificar_cadastro_demo(
                nome_completo=nome_completo,
                email=email,
                telefone=telefone,
                ip_address=ip_address
            )
            logger.info(f'[DEMO_CADASTRO] Notificações enviadas para admin sobre lead: {email}')
        except Exception as e:
            logger.error(f'[DEMO_CADASTRO] Erro ao enviar notificações: {e}')
            # Não falhar o cadastro por causa das notificações

        # 4. Fazer login automático
        try:
            login(request, user)
            logger.info(f'[DEMO_CADASTRO] Login autom??tico realizado')
        except Exception as e:
            logger.error(f'[DEMO_CADASTRO] Erro no login automático: {e}')

        # 5. Retornar sucesso - SEMPRE redirecionar para demo_loading
        mensagem = 'Demonstração criada com sucesso! Preparando ambiente...'
        demo_loading_url = reverse('demo_loading')
        logger.info(f'[DEMO_CADASTRO] SEMPRE redirecionando para demo_loading: {demo_loading_url}')
        return JsonResponse({
            'success': True,
            'message': mensagem,
            'redirect_url': demo_loading_url
        })
        
    except Exception as e:
        logger.error(f'[DEMO_CADASTRO] Erro inesperado: {type(e).__name__}: {e}', exc_info=True)
        return JsonResponse({
            'success': False,
            'message': 'Erro ao criar usu??rio. Por favor, tente novamente ou entre em contato com o suporte.'
        }, status=500)


def criando_usuario_demo(request):
    """
    Página de formulário para criação de usuário de demonstração
    """
    return render(request, 'gestao_rural/demo/criando_usuario_demo.html')


def contato_submit(request):
    """Processa o formulário de contato e envia email e WhatsApp"""
    from django.core.cache import cache
    
    if request.method == 'POST':
        tipo_formulario = request.POST.get('tipo_formulario', 'contato').strip()
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        empresa = request.POST.get('empresa', '').strip()
        mensagem = request.POST.get('mensagem', '').strip()
        
        # Validação básica
        if not nome or not email:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            url_redirect = reverse('landing_page') + '#contato'
            return redirect(url_redirect)
        
        # Se for formulário de demonstração, verificar se o email já foi usado
        if tipo_formulario == 'demonstracao':
            cache_key = f'demo_email_{email.lower()}'
            if cache.get(cache_key):
                # Email já foi usado - mostrar popup e redirecionar após 5 segundos
                context = {
                    'email': email,
                    'login_url': reverse('login') + '?demo=true',
                }
                return render(request, 'site/email_duplicado_popup.html', context)
            
            # Adicionar email ao cache (30 dias)
            cache.set(cache_key, True, 60 * 60 * 24 * 30)
            
            # DESABILITADO: Envio de email para demonstrações
            # O envio de email foi desabilitado para evitar spam quando usuários criam contas de demonstração
            # Se precisar reativar, descomente o código abaixo
            # 
            # Enviar email ANTES de mostrar a página de cadastro
            # try:
            #     assunto = f'Nova solicitação de demonstração - MONPEC'
            #     corpo_email = f"""
            # Nova solicitação de demonstração recebida através do formulário do site MONPEC:
            # 
            # Nome: {nome}
            # Email: {email}
            # Telefone: {telefone}
            # Empresa/Fazenda: {empresa or 'Não informado'}
            # 
            # ---
            # Esta mensagem foi enviada automaticamente através do formulário de demonstração do site MONPEC.
            # """
            #     send_mail(
            #         subject=assunto,
            #         message=corpo_email,
            #         from_email=settings.DEFAULT_FROM_EMAIL,
            #         recipient_list=['monpecnfe@gmail.com'],
            #         fail_silently=True,  # Não bloquear se houver erro
            #     )
            #     logger.info(f'Email de demonstração enviado com sucesso de {email}')
            # except Exception as e:
            #     logger.error(f'Erro ao enviar email de demonstração: {str(e)}')
            
            logger.info(f'Solicitação de demonstração recebida de {email} (email de notificação desabilitado)')
            
            # Mostrar página de cadastro realizado com os dados
            context = {
                'nome': nome,
                'email': email,
                'telefone': telefone,
                'empresa': empresa,
                'login_url': reverse('login') + f'?demo=true&email={urllib.parse.quote(email)}&nome={urllib.parse.quote(nome)}',
            }
            return render(request, 'site/formulario_cadastro_sucesso.html', context)
        
        # Preparar mensagem para email
        assunto = f'Nova mensagem de contato - MONPEC' if tipo_formulario == 'contato' else f'Nova solicitação de demonstração - MONPEC'
        corpo_email = f"""
Nova mensagem recebida através do formulário de contato do site MONPEC:

Nome: {nome}
Email: {email}
Telefone: {telefone}
Empresa/Fazenda: {empresa or 'Não informado'}

Mensagem:
{mensagem or 'Solicitação de demonstração'}

---
Esta mensagem foi enviada automaticamente através do formulário de contato do site MONPEC.
"""
        
        # Enviar email
        try:
            send_mail(
                subject=assunto,
                message=corpo_email,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['monpecnfe@gmail.com'],
                fail_silently=False,
            )
            logger.info(f'Email de contato enviado com sucesso de {email}')
        except Exception as e:
            logger.error(f'Erro ao enviar email de contato: {str(e)}')
            messages.error(request, 'Erro ao enviar mensagem. Por favor, tente novamente.')
            url_redirect = reverse('landing_page') + '#contato'
            return redirect(url_redirect)
        
        # Preparar mensagem para WhatsApp
        # Formatar telefone (remover caracteres não numéricos)
        telefone_whatsapp = ''.join(filter(str.isdigit, '67999688561'))
        if not telefone_whatsapp.startswith('55'):
            telefone_whatsapp = '55' + telefone_whatsapp
        
        # Criar mensagem formatada para WhatsApp
        mensagem_whatsapp = f"""*Nova mensagem de contato - MONPEC*

*Nome:* {nome}
*Email:* {email}
*Telefone:* {telefone}
*Empresa/Fazenda:* {empresa or 'Não informado'}

*Mensagem:*
{mensagem or 'Solicitação de demonstração'}

---
Enviado automaticamente através do formulário de contato do site MONPEC."""
        
        # Tentar enviar via WhatsApp usando pywhatkit
        try:
            import pywhatkit as pwk
            
            # Calcular horário de envio (1 minuto a partir de agora)
            agora = datetime.now()
            horario_envio = agora + timedelta(minutes=1)
            
            # Enviar mensagem via WhatsApp
            pwk.sendwhatmsg(
                phone_no=telefone_whatsapp,
                message=mensagem_whatsapp,
                time_hour=horario_envio.hour,
                time_min=horario_envio.minute,
                wait_time=15,
                tab_close=True
            )
            logger.info(f'Mensagem de contato enviada via WhatsApp para {telefone_whatsapp}')
        except ImportError:
            # Se pywhatkit não estiver instalado, criar link direto
            mensagem_encoded = urllib.parse.quote(mensagem_whatsapp)
            url_whatsapp = f'https://wa.me/{telefone_whatsapp}?text={mensagem_encoded}'
            logger.info(f'Link WhatsApp criado (pywhatkit não disponível): {url_whatsapp}')
            logger.warning('Para envio automático via WhatsApp, instale: pip install pywhatkit')
        except Exception as e:
            # Se houver erro, criar link direto como fallback
            mensagem_encoded = urllib.parse.quote(mensagem_whatsapp)
            url_whatsapp = f'https://wa.me/{telefone_whatsapp}?text={mensagem_encoded}'
            logger.error(f'Erro ao enviar WhatsApp: {str(e)}. Link criado: {url_whatsapp}')
        
        # Se for contato normal, redirecionar para landing page com mensagem de sucesso
        messages.success(request, 'Mensagem enviada com sucesso! Logo um dos nossos consultores retornará sua solicitação.')
        # Usar redirect com hash e query parameter para garantir que a mensagem apareça
        return redirect(reverse('landing_page') + '#contato?form_submitted=1&success=1')
    
    # Se não for POST, redirecionar para landing page
    return redirect('landing_page')

from .models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho, AnimalIndividual,
    ParametrosProjecaoRebanho, MovimentacaoProjetada,
    ConfiguracaoVenda, TransferenciaPropriedade, PoliticaVendasCategoria,
    SCRBancoCentral, DividaBanco, ContratoDivida, AmortizacaoContrato,
    ProjetoBancario, DocumentoProjeto, PlanejamentoAnual
)
from .forms import (
    ProdutorRuralForm, PropriedadeForm, InventarioRebanhoForm,
    ParametrosProjecaoForm, MovimentacaoProjetadaForm, CategoriaAnimalForm
)


def login_view(request):
    """View para login do usuário com proteções de segurança"""
    # Usar o import global de login (linha 4) para evitar conflitos de escopo
    from .security import (
        verificar_tentativas_login, 
        registrar_tentativa_login_falha,
        limpar_tentativas_login
    )
    from .security_avancado import (
        registrar_log_auditoria,
        registrar_sessao_segura,
        obter_ip_address,
    )
    
    # Obtém IP do cliente
    ip_address = obter_ip_address(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Validação básica
        if not username:
            messages.error(request, 'Por favor, informe o nome de usuário.')
            return render(request, 'gestao_rural/login_clean.html')
        
        if not password:
            messages.error(request, 'Por favor, informe a senha.')
            return render(request, 'gestao_rural/login_clean.html')
        
        # Verifica bloqueio por tentativas
        bloqueado, tempo_restante = verificar_tentativas_login(username, ip_address)
        if bloqueado:
            minutos = int(tempo_restante / 60)
            segundos = int(tempo_restante % 60)
            messages.error(
                request, 
                f' <strong>Bloqueio por tentativas:</strong> Após 5 tentativas falhas, o sistema bloqueia por 1 minuto. '
                f'Aguarde {minutos}min {segundos}s antes de tentar novamente. '
                f'Possíveis causas: senha incorreta, conta desativada ou e-mail não verificado.'
            )
            return render(request, 'gestao_rural/login_clean.html', {'mostrar_info_ajuda': True})
        
        # Verificar se é email ou username e autenticar
        from django.contrib.auth.models import User
        user = None
        
        # Tentar autenticar primeiro com username
        try:
            user = authenticate(request, username=username, password=password)
        except Exception as e:
            logger.error(f'Erro na autenticação: {e}')
        
        # Se não funcionar e parecer email, tentar com email (case-insensitive)
        if user is None and '@' in username:
            try:
                email_normalizado = username.lower().strip()
                user_by_email = User.objects.filter(email__iexact=email_normalizado).first()
                if user_by_email:
                    logger.info(f'Usuário encontrado por email: username={user_by_email.username}, email={user_by_email.email}, is_active={user_by_email.is_active}')
                    user = authenticate(request, username=user_by_email.username, password=password)
                    if user:
                        logger.info(f'Autenticação bem-sucedida com username: {user_by_email.username}')
                    else:
                        logger.warning(f' Autenticação falhou para username: {user_by_email.username} (senha incorreta ou usuário inativo)')
                else:
                    logger.warning(f' Nenhum usuário encontrado com email: {email_normalizado}')
            except Exception as e:
                logger.error(f'Erro ao buscar usuário por email: {e}', exc_info=True)
        
        # Verificar se o usuário existe (para mensagem de erro) - case-insensitive
        # IMPORTANTE: Esta verificação só serve para mostrar mensagem de erro apropriada
        # Não deve bloquear a autenticação, pois o authenticate() já faz isso
        if user is None:
            try:
                # Verificar se existe usuário com esse username ou email
                usuario_existe = User.objects.filter(username__iexact=username).exists() or User.objects.filter(email__iexact=username).exists()
                
                logger.info(f'Verificação de usuário: username={username}, usuario_existe={usuario_existe}')
            except Exception as e:
                logger.error(f'Erro ao verificar usuário: {e}', exc_info=True)
                usuario_existe = False  # Se houver erro, assumir que não existe
            
            if not usuario_existe:
                registrar_tentativa_login_falha(username, ip_address)
                messages.error(
                    request, 
                    f'❌ <strong>Usuário não encontrado:</strong> O usuário ou email "{username}" não existe no sistema. '
                    f'Verifique se está correto. <strong>Após 5 tentativas falhas, o sistema bloqueia por 1 minuto.</strong>'
                )
                registrar_log_auditoria(
                    tipo_acao='LOGIN_FALHA',
                    descricao=f"Tentativa de login com usuário/email inexistente: {username}",
                    usuario=None,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    nivel_severidade='MEDIO',
                    sucesso=False,
                )
                return render(request, 'gestao_rural/login_clean.html')
        
        if user is not None:
            if not user.is_active:
                messages.error(
                    request, 
                    '❌ <strong>Conta desativada:</strong> Esta conta está desabilitada. '
                    'Entre em contato com o administrador do sistema para reativar sua conta. '
                    '<strong>Após 5 tentativas falhas, o sistema bloqueia por 1 minuto.</strong>'
                )
                registrar_tentativa_login_falha(username, ip_address)
                registrar_log_auditoria(
                    tipo_acao='LOGIN_FALHA',
                    descricao=f"Tentativa de login com conta desabilitada: {username}",
                    usuario=user,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    nivel_severidade='ALTO',
                    sucesso=False,
                )
                return render(request, 'gestao_rural/login_clean.html')
            else:
                # Verificar se e-mail foi verificado (para novos usuários)
                # EXCETO para usuários de demonstração (do popup)
                from .models_auditoria import VerificacaoEmail
                from .helpers_acesso import is_usuario_demo
                from django.db import OperationalError
                
                # Verificar se é usuário de demonstração usando função centralizada
                is_demo_user_check = is_usuario_demo(user)
                
                # Verificar se veio com parâmetro demo
                is_demo_param_check = request.GET.get('demo') == 'true' or request.POST.get('demo') == 'true'
                
                # Se for usuário de demonstração, pular verificação de email
                if not (is_demo_user_check or is_demo_param_check):
                    try:
                        verificacao = VerificacaoEmail.objects.get(usuario=user)
                        if not verificacao.email_verificado:
                            messages.warning(
                                request,
                                ' <strong>Verificação de e-mail pendente:</strong> Por favor, verifique seu e-mail antes de fazer login. '
                                'Verifique sua caixa de entrada e spam. <strong>Após 5 tentativas falhas, o sistema bloqueia por 1 minuto.</strong>'
                            )
                            registrar_tentativa_login_falha(username, ip_address)
                            registrar_log_auditoria(
                                tipo_acao='LOGIN_FALHA',
                                descricao=f"Tentativa de login sem e-mail verificado: {username}",
                                usuario=user,
                                ip_address=ip_address,
                                user_agent=user_agent,
                                nivel_severidade='MEDIO',
                                sucesso=False,
                            )
                            return render(request, 'gestao_rural/login_clean.html')
                    except (VerificacaoEmail.DoesNotExist, OperationalError):
                        # Usuário antigo ou tabela não existe ainda - não precisa verificar
                        pass
                
                # Login bem-sucedido - limpa tentativas
                try:
                    limpar_tentativas_login(username, ip_address)
                    login(request, user)
                    
                    # IMPORTANTE: Verificar se é demo ANTES de registrar sessão segura
                    # para garantir que o redirecionamento funcione
                    from .helpers_acesso import is_usuario_demo
                    
                    # Verificar se é usuário demo usando função centralizada
                    is_demo_user = is_usuario_demo(user)
                    
                    # Verificar parâmetro demo na URL (GET ou POST) - prioridade máxima
                    demo_get = request.GET.get('demo')
                    demo_post = request.POST.get('demo')
                    is_demo_param = (demo_get and (demo_get.lower() == 'true' or demo_get == '1')) or \
                                   (demo_post and (demo_post.lower() == 'true' or demo_post == '1'))
                    
                    if is_demo_user:
                        logger.info(f'Usuário demo detectado no login: {user.username} (função centralizada)')
                    
                    # Log detalhado para debug
                    logger.info(f'[DEBUG LOGIN] - username={username}, is_demo_user={is_demo_user}, is_demo_param={is_demo_param}, demo_get={demo_get}, demo_post={demo_post}')
                    
                    # Se for demo, redirecionar para tela de loading primeiro
                    if is_demo_user or is_demo_param:
                        logger.info(f'[USUARIO DE DEMONSTRACAO DETECTADO] - is_demo_user={is_demo_user}, is_demo_param={is_demo_param}, demo_get={demo_get}, demo_post={demo_post}, username={username}')
                        logger.info(f'[REDIRECIONANDO PARA DEMO_LOADING]')
                        return redirect('demo_loading')
                    
                    # Registrar sessão segura (apenas se não for demo ou se não redirecionou)
                    registrar_sessao_segura(user, request.session.session_key, ip_address, user_agent)
                    
                    # Atualizar registro de usuário ativo (se existir)
                    from .helpers_db import obter_usuario_ativo_seguro
                    usuario_ativo = obter_usuario_ativo_seguro(user)
                    if usuario_ativo:
                        try:
                            usuario_ativo.ultimo_acesso = timezone.now()
                            usuario_ativo.total_acessos += 1
                            usuario_ativo.save()
                            logger.info(f'UsuarioAtivo atualizado para {user.username}: total_acessos={usuario_ativo.total_acessos}')
                        except Exception as e:
                            logger.warning(f'Erro ao atualizar UsuarioAtivo: {e}')
                    
                    # Se usuario_ativo existe e for primeiro acesso, enviar convite para o grupo do WhatsApp
                    if usuario_ativo and usuario_ativo.total_acessos == 1:
                            try:
                                # Link de convite do grupo do WhatsApp (substitua pelo link real do seu grupo)
                                # Formato: https://chat.whatsapp.com/CODIGO_DO_GRUPO
                                grupo_whatsapp_link = getattr(settings, 'WHATSAPP_GRUPO_DEMO_LINK', 'https://chat.whatsapp.com/SEU_LINK_DO_GRUPO_AQUI')
                                
                                logger.info(f'Usuário {usuario_ativo.nome_completo} ({usuario_ativo.email}) acessou pela primeira vez. Enviando convite para grupo WhatsApp.')
                                
                                # Se tiver telefone, enviar mensagem com link do grupo
                                if usuario_ativo.telefone:
                                    telefone_limpo = ''.join(filter(str.isdigit, usuario_ativo.telefone))
                                    if not telefone_limpo.startswith('55'):
                                        telefone_limpo = '55' + telefone_limpo
                                    
                                    # Criar mensagem de boas-vindas com link do grupo
                                    nome_primeiro = usuario_ativo.nome_completo.split()[0] if usuario_ativo.nome_completo.split() else 'Usuário'
                                    mensagem_whatsapp = f"""Olá {nome_primeiro}! 👋

Bem-vindo(a) à demonstração do sistema MONPEC!

Para acompanhar dicas, atualizações e tirar dúvidas, entre no nosso grupo do WhatsApp:

{grupo_whatsapp_link}

Aproveite a demonstração! 🚀"""
                                    
                                    # Tentar enviar via pywhatkit (se disponível)
                                    try:
                                        import pywhatkit as pwk
                                        agora = datetime.now()
                                        horario_envio = agora + timedelta(minutes=1)
                                        pwk.sendwhatmsg(
                                            phone_no=telefone_limpo,
                                            message=mensagem_whatsapp,
                                            time_hour=horario_envio.hour,
                                            time_min=horario_envio.minute,
                                            wait_time=15,
                                            tab_close=True
                                        )
                                        logger.info(f'Convite do grupo WhatsApp enviado para {telefone_limpo}')
                                    except ImportError:
                                        # Se pywhatkit não estiver instalado, criar link direto
                                        mensagem_encoded = urllib.parse.quote(mensagem_whatsapp)
                                        url_whatsapp = f'https://wa.me/{telefone_limpo}?text={mensagem_encoded}'
                                        logger.info(f'Link WhatsApp criado (pywhatkit não disponível): {url_whatsapp}')
                                    except Exception as e:
                                        logger.error(f'Erro ao enviar WhatsApp: {str(e)}')
                                
                                # Também enviar link do grupo por email
                                try:
                                    assunto_grupo = f'Bem-vindo ao MONPEC - Convite para o Grupo WhatsApp'
                                    corpo_email_grupo = f"""
Olá {usuario_ativo.nome_completo},

Bem-vindo(a) à demonstração do sistema MONPEC!

Para acompanhar dicas, atualizações e tirar dúvidas, entre no nosso grupo do WhatsApp:

{grupo_whatsapp_link}

Aproveite a demonstração!

Equipe MONPEC
"""
                                    send_mail(
                                        subject=assunto_grupo,
                                        message=corpo_email_grupo,
                                        from_email=settings.DEFAULT_FROM_EMAIL,
                                        recipient_list=[usuario_ativo.email],
                                        fail_silently=True,
                                    )
                                    logger.info(f'Email com convite do grupo enviado para {usuario_ativo.email}')
                                except Exception as e:
                                    logger.error(f'Erro ao enviar email com convite do grupo: {str(e)}')
                                    
                            except Exception as e:
                                logger.error(f'Erro ao processar convite para grupo WhatsApp: {str(e)}')
                    
                    # Enviar email informando que o usuário acessou o sistema (apenas se usuario_ativo existir)
                    if usuario_ativo:
                        try:
                            assunto = f'Usuário acessou o sistema - MONPEC'
                            corpo_email = f"""
O usuário acessou o sistema MONPEC:

Nome: {usuario_ativo.nome_completo}
Email: {usuario_ativo.email}
Telefone: {usuario_ativo.telefone or 'Não informado'}
IP: {ip_address}
Data/Hora: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}
Total de Acessos: {usuario_ativo.total_acessos}

---
Esta mensagem foi enviada automaticamente pelo sistema MONPEC.
"""
                            send_mail(
                                subject=assunto,
                                message=corpo_email,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=['l.moncaosilva@google.com'],
                                fail_silently=True,
                            )
                            logger.info(f'Email de acesso enviado para l.moncaosilva@google.com - Usuário: {username}')
                        except Exception as e:
                            logger.error(f'Erro ao enviar email de acesso: {str(e)}')
                    
                    # Registrar log
                    registrar_log_auditoria(
                        tipo_acao='LOGIN',
                        descricao=f"Login bem-sucedido: {username}",
                        usuario=user,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        nivel_severidade='BAIXO',
                        sucesso=True,
                    )
                    
                    logger.info(f'Login bem-sucedido - Usuário: {username}, IP: {ip_address}')
                    
                    # Redirecionar para a URL original (next) ou para o dashboard (apenas se NÃO for demo)
                    next_url = request.GET.get('next') or request.POST.get('next')
                    if next_url:
                        return redirect(next_url)
                    
                    # Para outros usuários, buscar primeira propriedade ou redirecionar para landing page
                    try:
                        from .models import Propriedade
                        propriedade = Propriedade.objects.filter(
                            produtor__usuario_responsavel=user
                        ).first()
                        
                        if propriedade:
                            # Redirecionar direto para a página inicial (módulos)
                            return redirect('propriedade_modulos', propriedade_id=propriedade.id)
                        else:
                            # ✅ NOVO: Se não tem propriedade, redirecionar para landing page
                            logger.info(f'[LOGIN] Usuário {user.username} não tem propriedades. Redirecionando para landing page.')
                            messages.info(request, 'Bem-vindo! Cadastre sua primeira propriedade para começar.')
                            return redirect('landing_page')
                    except Exception as e:
                        logger.error(f'[LOGIN] Erro ao buscar propriedade após login: {e}')
                        # Em caso de erro, redirecionar para dashboard mesmo assim
                        return redirect('dashboard')
                except Exception as e:
                    logger.error(f'Erro após autenticação bem-sucedida: {e}')
                    # Em vez de mostrar erro, redirecionar para dashboard
                    return redirect('dashboard')
        else:
            # Login falhou - registra tentativa e verifica quantas tentativas restam
            from django.core.cache import cache
            chave_usuario = f'login_attempts_user_{username}'
            tentativas_atuais = cache.get(chave_usuario, 0)
            tentativas_restantes = 5 - tentativas_atuais - 1
            
            registrar_tentativa_login_falha(username, ip_address)
            
            if tentativas_restantes > 0:
                mensagem = (
                    f'❌ <strong>Senha incorreta:</strong> Verifique se a senha está digitada corretamente. '
                    f'<strong>Você tem {tentativas_restantes} tentativa(s) restante(s).</strong> '
                    f'Após 5 tentativas falhas, o sistema bloqueia por 1 minuto. '
                    f'Se esqueceu sua senha, use a opção "Esqueceu a senha?".'
                )
            else:
                mensagem = (
                    f'❌ <strong>Senha incorreta:</strong> Você excedeu 5 tentativas falhas. '
                    f'O sistema foi bloqueado por 1 minuto. Aguarde antes de tentar novamente.'
                )
            
            messages.error(request, mensagem)
            registrar_log_auditoria(
                tipo_acao='LOGIN_FALHA',
                descricao=f"Tentativa de login com senha incorreta: {username}",
                usuario=None,
                ip_address=ip_address,
                user_agent=user_agent,
                nivel_severidade='MEDIO',
                sucesso=False,
            )
    
    # Verificar se é modo demonstração
    is_demo = request.GET.get('demo') == 'true' or request.GET.get('demo') == '1'
    email_param = request.GET.get('email', '')
    nome_param = request.GET.get('nome', '')
    
    # Se vier email da demonstração, usar senha "monpec"
    senha_demo = 'monpec' if email_param else 'demo123'
    
    # Se for modo demo, garantir que o usuário demo existe (apenas se não vier email específico)
    if is_demo and not email_param:
        from django.contrib.auth.models import User
        demo_user, created = User.objects.get_or_create(
            username='demo_monpec',
            defaults={
                'email': 'demo@monpec.com.br',
                'is_staff': True,
                'is_superuser': False,
                'is_active': True,
            }
        )
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
            logger.info('Usuário demo_monpec criado automaticamente')
        elif not demo_user.check_password('demo123'):
            # Se o usuário existe mas a senha está diferente, atualizar
            demo_user.set_password('demo123')
            demo_user.save()
            logger.info('Senha do usuário demo_monpec atualizada')
    
    # Adicionar informações de ajuda no contexto
    from django.conf import settings
    context = {
        'mostrar_info_ajuda': True,
        # Removido: Hotmart - usando apenas Mercado Pago
        'is_demo': is_demo,
        'demo_username': email_param if email_param else 'demo_monpec',
        'demo_password': senha_demo,
        'email_param': email_param,
        'nome_param': nome_param,
    }
    return render(request, 'gestao_rural/login_clean.html', context)


def logout_view(request):
    """View para logout do usuário - redireciona para landing page"""
    try:
        # Tentar importar módulos de segurança (se existirem)
        try:
            from .security_avancado import (
                registrar_log_auditoria,
                invalidar_sessao_segura,
                obter_ip_address,
            )

            usuario = request.user if request.user.is_authenticated else None
            ip_address = obter_ip_address(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')

            # Invalidar sessão segura (apenas se a tabela existir)
            try:
                if request.session.session_key:
                    invalidar_sessao_segura(request.session.session_key)
            except Exception as e:
                # Se a tabela SessaoSegura não existir, continuar sem erro
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Tabela SessaoSegura não existe, pulando invalidação: {e}')

            # Registrar log (apenas se conseguir importar)
            try:
                if usuario:
                    registrar_log_auditoria(
                        tipo_acao='LOGOUT',
                        descricao=f"Logout: {usuario.username}",
                        usuario=usuario,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        nivel_severidade='BAIXO',
                        sucesso=True,
                    )
            except Exception as e:
                # Se houver erro no registro de auditoria, continuar
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Erro no registro de auditoria do logout: {e}')
        except ImportError as e:
            # Se o módulo security_avancado não existir, fazer logout básico
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'Módulo security_avancado não encontrado, fazendo logout básico: {e}')

    except Exception as e:
        # Se houver erro geral, continuar com o logout básico
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f'Erro geral no logout avançado, fazendo logout básico: {e}')

    # FAZER LOGOUT COMPLETO - limpar todas as sessões e dados
    logout(request)

    # Limpar sessão completamente para garantir
    request.session.flush()

    # Limpar qualquer dado de sessão relacionado a demo
    keys_to_delete = [key for key in request.session.keys() if 'demo' in key.lower()]
    for key in keys_to_delete:
        del request.session[key]

    # Garantir que não há redirecionamento automático para demo_loading
    # Todos os usuários (incluindo demo) vão para landing_page com parâmetro logout
    messages.success(request, 'Você saiu do sistema com sucesso.')
    return redirect('landing_page')


@login_required
def dashboard(request):
    """Dashboard principal - mostra lista de propriedades (fazendas)"""
    from .services.dashboard_service import DashboardService
    from .helpers_acesso import is_usuario_demo
    from django.db import ProgrammingError
    from .models import Propriedade
    
    try:
        # Obter parâmetros de busca e ordenação
        busca = request.GET.get('busca', '').strip()
        ordenar_por = request.GET.get('ordenar', 'nome_propriedade')
        direcao = request.GET.get('direcao', 'asc')
        
        # Usar serviço para obter dados do dashboard
        dados = DashboardService.obter_dados_dashboard(request.user)
        propriedades = dados['propriedades']
        
        # Aplicar busca se fornecida
        if busca:
            propriedades = propriedades.filter(
                Q(nome_propriedade__icontains=busca) |
                Q(municipio__icontains=busca) |
                Q(uf__icontains=busca) |
                Q(produtor__nome__icontains=busca)
            )
        
        # Anotar com total de animais para ordenação e exibição
        propriedades = propriedades.annotate(
            total_animais_calc=Count('animais_individuais', filter=Q(animais_individuais__status='ATIVO'))
        )
        
        # Aplicar ordenação
        if ordenar_por == 'nome_propriedade':
            propriedades = propriedades.order_by(f'{"" if direcao == "asc" else "-"}nome_propriedade')
        elif ordenar_por == 'municipio':
            propriedades = propriedades.order_by(f'{"" if direcao == "asc" else "-"}municipio')
        elif ordenar_por == 'uf':
            propriedades = propriedades.order_by(f'{"" if direcao == "asc" else "-"}uf')
        elif ordenar_por == 'animais':
            propriedades = propriedades.order_by(f'{"" if direcao == "asc" else "-"}total_animais_calc')
        else:
            propriedades = propriedades.order_by('nome_propriedade')
        
        # Calcular total de animais de todas as propriedades
        total_animais = sum(prop.total_animais_calc for prop in propriedades)
        
        # Paginação
        paginator = Paginator(propriedades, 12)  # 12 propriedades por página
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Adicionar atributo total_animais para cada propriedade (compatibilidade com template)
        for prop in page_obj:
            if not hasattr(prop, 'total_animais'):
                prop.total_animais = getattr(prop, 'total_animais_calc', 0)
        
        # Se não houver propriedades, verificar se é demo
        is_demo_user = is_usuario_demo(request.user)
        logger.info(f'[DASHBOARD] is_demo_user: {is_demo_user}, total_propriedades: {dados["total_propriedades"]}')
        
        if is_demo_user and dados['total_propriedades'] == 0:
            logger.info(f'[DASHBOARD] Usuário demo sem propriedades. Redirecionando para demo_setup.')
            messages.info(request, 'Configurando sua demonstração...')
            return redirect('demo_setup')
        
        # Se não houver propriedades e não for demo, mostrar estado vazio
        if dados['total_propriedades'] == 0:
            logger.info(f'[DASHBOARD] Nenhuma propriedade encontrada.')
            return render(request, 'gestao_rural/dashboard.html', {
                'propriedades': [],
                'total_propriedades': 0,
                'total_animais': 0,
                'busca': busca,
                'ordenar_por': ordenar_por,
                'direcao': direcao,
                'page_obj': None,
            })
        
        # ✅ REDIRECIONAR AUTOMATICAMENTE: Se houver propriedades, redirecionar para a primeira propriedade
        # Buscar propriedade prioritária ou primeira propriedade (usar queryset original antes das anotações)
        propriedade_prioritaria = dados.get('propriedade_prioritaria')
        if propriedade_prioritaria:
            logger.info(f'[DASHBOARD] Redirecionando para módulos da propriedade {propriedade_prioritaria.id}')
            return redirect('propriedade_modulos', propriedade_id=propriedade_prioritaria.id)
        elif dados['total_propriedades'] > 0:
            # Se não houver propriedade prioritária, usar a primeira propriedade do queryset original
            primeira_propriedade = dados['propriedades'].first() if hasattr(dados['propriedades'], 'first') else (dados['propriedades'][0] if dados['propriedades'] else None)
            if primeira_propriedade:
                logger.info(f'[DASHBOARD] Redirecionando para módulos da primeira propriedade {primeira_propriedade.id}')
                return redirect('propriedade_modulos', propriedade_id=primeira_propriedade.id)
        
        # Renderizar dashboard com lista de propriedades (fallback - não deve chegar aqui)
        context = {
            'propriedades': page_obj,
            'total_propriedades': dados['total_propriedades'],
            'total_animais': total_animais,
            'busca': busca,
            'ordenar_por': ordenar_por,
            'direcao': direcao,
            'page_obj': page_obj,
        }
        
        return render(request, 'gestao_rural/dashboard.html', context)
        
    except ProgrammingError as e:
        logger.warning(f'Erro de programação no dashboard: {e}')
        # Fallback para comportamento seguro
        propriedades = Propriedade.objects.filter(
            produtor__usuario_responsavel=request.user
        ).select_related('produtor').order_by('nome_propriedade')
        
        paginator = Paginator(propriedades, 12)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context = {
            'propriedades': page_obj,
            'total_propriedades': propriedades.count(),
            'total_animais': 0,
            'busca': request.GET.get('busca', ''),
            'ordenar_por': request.GET.get('ordenar', 'nome_propriedade'),
            'direcao': request.GET.get('direcao', 'asc'),
            'page_obj': page_obj,
        }
        return render(request, 'gestao_rural/dashboard.html', context)
    except Exception as e:
        logger.error(f'Erro inesperado no dashboard: {e}', exc_info=True)
        # Removendo a mensagem de erro para não mostrar ao usuário
        return render(request, 'gestao_rural/dashboard.html', {
            'propriedades': [],
            'total_propriedades': 0,
            'total_animais': 0,
            'busca': '',
            'ordenar_por': 'nome_propriedade',
            'direcao': 'asc',
            'page_obj': None,
        })


@login_required
def produtor_novo(request):
    """Cadastro de novo produtor rural"""
    # Verificar se é usuário de demonstração
    # Verificar se é usuário demo usando função centralizada
    from .helpers_acesso import is_usuario_demo
    is_demo_user = is_usuario_demo(request.user)
    
    # Se for usuário demo, redirecionar IMEDIATAMENTE para setup automático (que cria tudo)
    if is_demo_user:
        logger.info(f'Usuário demo tentou acessar cadastro de produtor. Redirecionando para demo_setup.')
        return redirect('demo_setup')
    
    if request.method == 'POST':
        form = ProdutorRuralForm(request.POST)
        if form.is_valid():
            # Tentar salvar normalmente primeiro
            from django.db import ProgrammingError
            try:
                produtor = form.save(commit=False)
                produtor.usuario_responsavel = request.user
                produtor.save()
            except ProgrammingError as e:
                # Se houver erro (coluna não existe), criar manualmente apenas com campos básicos
                logger.warning(f'Erro ao salvar produtor (coluna faltando): {e}. Criando apenas com campos básicos.')
                from .models import ProdutorRural
                # Obter dados do formulário validado
                dados = form.cleaned_data
                campos_basicos = {
                    'nome': dados.get('nome'),
                    'cpf_cnpj': dados.get('cpf_cnpj'),
                    'usuario_responsavel': request.user,
                    'documento_identidade': dados.get('documento_identidade'),
                    'data_nascimento': dados.get('data_nascimento'),
                    'anos_experiencia': dados.get('anos_experiencia'),
                    'telefone': dados.get('telefone'),
                    'email': dados.get('email'),
                }
                # Tentar adicionar endereco se estiver presente
                if 'endereco' in dados and dados.get('endereco'):
                    try:
                        produtor = ProdutorRural.objects.create(**campos_basicos, endereco=dados.get('endereco'))
                    except ProgrammingError:
                        # Se endereco também não existir, criar sem ele
                        produtor = ProdutorRural.objects.create(**campos_basicos)
                else:
                    produtor = ProdutorRural.objects.create(**campos_basicos)
            
            # Se for usuário de demonstração, criar automaticamente a propriedade Monpec1 (ou Monpec2, Monpec3, etc.)
            if is_demo_user:
                try:
                    from .models import Propriedade
                    from decimal import Decimal
                    import re
                    
                    # Verificar se já existe propriedade com nome "Monpec" para este produtor
                    propriedades_existentes = Propriedade.objects.filter(
                        produtor=produtor,
                        nome_propriedade__iregex=r'^Monpec\d+$'
                    ).order_by('nome_propriedade')
                    
                    # Determinar o próximo número disponível para este produtor
                    if propriedades_existentes.exists():
                        # Encontrar o maior número usado
                        numeros_usados = []
                        for prop in propriedades_existentes:
                            match = re.search(r'Monpec(\d+)', prop.nome_propriedade, re.IGNORECASE)
                            if match:
                                numeros_usados.append(int(match.group(1)))
                        
                        if numeros_usados:
                            proximo_numero = max(numeros_usados) + 1
                        else:
                            proximo_numero = 2
                        
                        nome_propriedade = f'Monpec{proximo_numero}'
                        logger.info(f' Propriedade Monpec1 já existe para este produtor. Usando {nome_propriedade}')
                    else:
                        nome_propriedade = 'Monpec1'
                    
                    propriedade = Propriedade.objects.create(
                        produtor=produtor,
                        nome_propriedade=nome_propriedade,
                        municipio='Campo Grande',
                        uf='MS',
                        area_total_ha=Decimal('1000.00'),
                        tipo_operacao='PECUARIA',
                        tipo_ciclo_pecuario=['CICLO_COMPLETO'],
                        tipo_propriedade='PROPRIA',
                        valor_hectare_proprio=Decimal('10000.00'),
                    )
                    logger.info(f'Propriedade {nome_propriedade} criada automaticamente para usuário de demonstração {request.user.username}')
                    
                    # Redirecionar para a propriedade criada
                    messages.success(request, f'Produtor e propriedade {nome_propriedade} cadastrados com sucesso! Bem-vindo à demonstração!')
                    return redirect('propriedade_modulos', propriedade_id=propriedade.id)
                except Exception as e:
                    logger.error(f'Erro ao criar propriedade Monpec automaticamente: {e}')
                    messages.warning(request, 'Produtor cadastrado, mas houve um erro ao criar a propriedade. Por favor, crie manualmente.')
            
            messages.success(request, 'Produtor cadastrado com sucesso!')
            return redirect('dashboard')
    else:
        # Pré-preencher formulário com dados do usuário de demonstração
        initial_data = {}
        if is_demo_user:
            try:
                from .models_auditoria import UsuarioAtivo
                from django.db import ProgrammingError
                usuario_ativo = UsuarioAtivo.objects.get(usuario=request.user)
                initial_data = {
                    'nome': usuario_ativo.nome_completo,
                    'email': usuario_ativo.email,
                    'telefone': usuario_ativo.telefone,
                }
            except (UsuarioAtivo.DoesNotExist, ProgrammingError):
                pass
            except:
                pass
        
        form = ProdutorRuralForm(initial=initial_data)
    
    # Buscar lista de produtores cadastrados para exibir discretamente
    # Admin: todos os produtores | Assinante/Usuário normal: apenas os que ele cadastrou
    # Incluir contagem de propriedades para otimizar a query
    # Usar only() para buscar apenas colunas básicas que certamente existem (sem certificado_digital)
    from django.db import ProgrammingError, DatabaseError, OperationalError
    produtores = []
    try:
        # Verificar primeiro se é admin
        if request.user.is_superuser or request.user.is_staff:
            # Admin: mostrar TODOS os produtores cadastrados
            produtores = ProdutorRural.objects.annotate(
                propriedades_count=Count('propriedade')
            ).only('id', 'nome', 'cpf_cnpj', 'email', 'telefone', 'usuario_responsavel_id', 'data_cadastro').order_by('nome')
        else:
            # Verificar se é assinante
            try:
                from .models import AssinaturaCliente, TenantUsuario
                
                # Buscar assinatura do usuário
                assinatura = None
                if hasattr(request.user, 'assinatura'):
                    # Sempre usar defer() para evitar campos do Stripe removidos
                    assinatura = AssinaturaCliente.objects.filter(usuario=request.user).first()
                
                if assinatura and assinatura.status == 'ATIVA':
                    # Assinante: buscar todos os usuários da mesma assinatura (equipe)
                    usuarios_tenant = TenantUsuario.objects.filter(
                        assinatura=assinatura,
                        ativo=True
                    ).select_related('usuario')
                    
                    # Obter IDs dos usuários da equipe
                    usuarios_ids = [tu.usuario.id for tu in usuarios_tenant]
                    
                    # Também incluir o próprio usuário
                    usuarios_ids.append(request.user.id)
                    
                    # Filtrar produtores cadastrados por esses usuários (equipe do assinante)
                    produtores = ProdutorRural.objects.filter(
                        usuario_responsavel__id__in=usuarios_ids
                    ).annotate(
                        propriedades_count=Count('propriedade')
                    ).only('id', 'nome', 'cpf_cnpj', 'email', 'telefone', 'usuario_responsavel_id', 'data_cadastro').order_by('nome')
                else:
                    # Usuário normal ou assinante inativo: apenas os produtores que ele cadastrou
                    produtores = ProdutorRural.objects.filter(
                        usuario_responsavel=request.user
                    ).annotate(
                        propriedades_count=Count('propriedade')
                    ).only('id', 'nome', 'cpf_cnpj', 'email', 'telefone', 'usuario_responsavel_id', 'data_cadastro').order_by('nome')
            except Exception:
                # Em caso de erro, comportamento seguro: apenas seus próprios produtores
                produtores = ProdutorRural.objects.filter(
                    usuario_responsavel=request.user
                ).annotate(
                    propriedades_count=Count('propriedade')
                ).only('id', 'nome', 'cpf_cnpj', 'email', 'telefone', 'usuario_responsavel_id', 'data_cadastro').order_by('nome')
    except (ProgrammingError, DatabaseError, OperationalError) as e:
        # Se houver erro (alguma coluna não existe), usar apenas colunas básicas essenciais
        logger.warning(f'Erro ao buscar produtores com annotate: {e}. Tentando query simplificada.')
        try:
            if request.user.is_superuser or request.user.is_staff:
                # Admin: todos os produtores
                produtores = ProdutorRural.objects.only('id', 'nome', 'cpf_cnpj', 'usuario_responsavel_id').order_by('nome')
            else:
                # Assinante ou usuário normal: apenas os que ele cadastrou
                produtores = ProdutorRural.objects.filter(
                    usuario_responsavel=request.user
                ).only('id', 'nome', 'cpf_cnpj', 'usuario_responsavel_id').order_by('nome')
        except Exception as e2:
            logger.error(f'Erro ao buscar produtores mesmo com query simplificada: {e2}')
            produtores = []
    except Exception as e:
        logger.error(f'Erro inesperado ao buscar produtores: {e}', exc_info=True)
        produtores = []
    
    context = {
        'form': form,
        'is_demo_user': is_demo_user,
        'produtores': produtores,
    }
    return render(request, 'gestao_rural/produtor_novo.html', context)


@login_required
@bloquear_demo_cadastro
def produtor_editar(request, produtor_id):
    """Edição de produtor rural"""
    # Se for assinante, pode acessar qualquer produtor
    if _is_usuario_assinante(request.user):
        produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    else:
        produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = ProdutorRuralForm(request.POST, request.FILES, instance=produtor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produtor atualizado com sucesso!')
            return redirect('dashboard')
    else:
        form = ProdutorRuralForm(instance=produtor)
    
    return render(request, 'gestao_rural/produtor_editar.html', {
        'form': form, 
        'produtor': produtor,
        'today': date.today()
    })


@login_required
@bloquear_demo_cadastro
def produtor_excluir(request, produtor_id):
    """Exclusão de produtor rural"""
    # Se for assinante, pode acessar qualquer produtor
    if _is_usuario_assinante(request.user):
        produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    else:
        produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    if request.method == 'POST':
        produtor.delete()
        messages.success(request, 'Produtor excluído com sucesso!')
        return redirect('dashboard')
    
    return render(request, 'gestao_rural/produtor_excluir.html', {'produtor': produtor})


@login_required
def propriedades_lista(request, produtor_id):
    """Lista de propriedades de um produtor"""
    # Se for assinante, pode acessar qualquer produtor
    if _is_usuario_assinante(request.user):
        produtor = get_object_or_404(ProdutorRural, id=produtor_id)
    else:
        produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
    }
    return render(request, 'gestao_rural/propriedades_lista.html', context)


@login_required
def propriedade_nova(request, produtor_id=None):
    """Cadastro de nova propriedade - sempre permite seleção de produtor"""
    produtor = None
    
    # Se produtor_id foi fornecido na URL, buscar o produtor (apenas para pré-selecionar)
    # Mas o campo sempre será exibido para permitir alteração
    if produtor_id:
        # Admin pode acessar qualquer produtor
        if request.user.is_superuser or request.user.is_staff:
            produtor = get_object_or_404(ProdutorRural, id=produtor_id)
        # Se for assinante, pode acessar qualquer produtor
        elif _is_usuario_assinante(request.user):
            produtor = get_object_or_404(ProdutorRural, id=produtor_id)
        else:
            produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = PropriedadeForm(request.POST, user=request.user, produtor_initial=produtor)
        if form.is_valid():
            propriedade = form.save()
            messages.success(request, 'Propriedade cadastrada com sucesso!')
            return redirect('propriedades_lista', produtor_id=propriedade.produtor.id)
    else:
        form = PropriedadeForm(user=request.user, produtor_initial=produtor)
    
    context = {
        'form': form,
        'produtor': produtor,
    }
    return render(request, 'gestao_rural/propriedade_nova.html', context)


@login_required
@bloquear_demo_cadastro
def propriedade_editar(request, propriedade_id):
    """Edição de propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = PropriedadeForm(request.POST, instance=propriedade, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Propriedade atualizada com sucesso!')
            return redirect('propriedades_lista', produtor_id=propriedade.produtor.id)
    else:
        form = PropriedadeForm(instance=propriedade, user=request.user)
    
    context = {
        'form': form,
        'propriedade': propriedade,
    }
    return render(request, 'gestao_rural/propriedade_editar.html', context)


@login_required
@bloquear_demo_cadastro
def propriedade_excluir(request, propriedade_id):
    """Exclusão de propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    if request.method == 'POST':
        produtor_id = propriedade.produtor.id
        propriedade.delete()
        messages.success(request, 'Propriedade excluída com sucesso!')
        return redirect('propriedades_lista', produtor_id=produtor_id)
    
    return render(request, 'gestao_rural/propriedade_excluir.html', {'propriedade': propriedade})


@login_required
def pecuaria_dashboard(request, propriedade_id):
    """Dashboard do módulo pecuária"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Verificar se tem inventário inicial
    inventario = InventarioRebanho.objects.filter(propriedade=propriedade).first()
    
    # Verificar se tem parâmetros configurados
    parametros = ParametrosProjecaoRebanho.objects.filter(propriedade=propriedade).first()
    
    # Contar movimentações projetadas
    movimentacoes_count = MovimentacaoProjetada.objects.filter(propriedade=propriedade).count()
    
    context = {
        'propriedade': propriedade,
        'inventario': inventario,
        'parametros': parametros,
        'movimentacoes_count': movimentacoes_count,
    }
    return render(request, 'gestao_rural/pecuaria_dashboard.html', context)


@login_required
def pecuaria_inventario(request, propriedade_id):
    """Gerenciamento do inventário inicial do rebanho - Versão refeita do zero"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Buscar categorias ativas com sexo e raça definidos
    categorias = CategoriaAnimal.objects.filter(
        ativo=True,
        sexo__in=['F', 'M'],
        raca__isnull=False
    ).exclude(raca='').order_by('sexo', 'raca', 'idade_minima_meses')
    
    if request.method == 'POST':
        try:
            # Excluir inventário se solicitado
            if 'excluir_todos' in request.POST:
                InventarioRebanho.objects.filter(propriedade=propriedade).delete()
                messages.success(request, 'Inventário excluído com sucesso!')
                return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
            
            # Processar salvamento
            data_inventario_str = request.POST.get('data_inventario') or request.POST.get('data_inventario_hidden')
            
            if not data_inventario_str:
                data_inventario = timezone.now().date()
                messages.warning(request, 'Data não informada. Usando data atual.')
            else:
                try:
                    from datetime import datetime
                    data_inventario = datetime.strptime(data_inventario_str, '%Y-%m-%d').date()
                except ValueError:
                    data_inventario = timezone.now().date()
                    messages.warning(request, 'Data inválida. Usando data atual.')
            
            # Processar cada categoria
            itens_salvos = 0
            erros = []
            
            with transaction.atomic():
                # IMPORTANTE: Excluir todos os inventários anteriores desta propriedade
                # para garantir que não haja duplicatas ao salvar várias vezes
                # Isso garante que só existe um inventário por propriedade
                InventarioRebanho.objects.filter(propriedade=propriedade).delete()
                
                for categoria in categorias:
                    quantidade_str = request.POST.get(f'quantidade_{categoria.id}', '').strip()
                    valor_str = request.POST.get(f'valor_por_cabeca_{categoria.id}', '').strip()
                    
                    # Pular se não há dados
                    if not quantidade_str and not valor_str:
                        continue
                    
                    try:
                        quantidade = int(quantidade_str) if quantidade_str else 0
                        valor_por_cabeca = Decimal(valor_str.replace(',', '.')) if valor_str else Decimal('0.00')
                        
                        # Validações
                        if quantidade < 0:
                            erros.append(f'{categoria.nome}: Quantidade não pode ser negativa')
                            continue
                        
                        if valor_por_cabeca < 0:
                            erros.append(f'{categoria.nome}: Valor não pode ser negativo')
                            continue
                        
                        # Criar novo registro (já excluímos os anteriores)
                        InventarioRebanho.objects.create(
                            propriedade=propriedade,
                            categoria=categoria,
                            data_inventario=data_inventario,
                            quantidade=quantidade,
                            valor_por_cabeca=valor_por_cabeca
                        )
                        itens_salvos += 1
                        
                    except (ValueError, InvalidOperation) as e:
                        erros.append(f'{categoria.nome}: {str(e)}')
            
            # Mensagens de feedback
            if erros:
                for erro in erros:
                    messages.error(request, erro)
            
            if itens_salvos > 0:
                messages.success(request, f'{itens_salvos} categoria(s) salva(s) com sucesso!')
            
            return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
            
        except Exception as e:
            logger.error(f'Erro ao processar inventário: {e}', exc_info=True)
            messages.error(request, f'Erro ao processar inventário: {str(e)}')
            return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
    
    # Preparar dados para exibição
    categorias_com_inventario = []
    total_quantidade = 0
    total_valor = Decimal('0.00')
    
    # Verificar se há uma data específica na URL (após salvar)
    data_inventario_filtro = request.GET.get('data_inventario')
    if data_inventario_filtro:
        try:
            from datetime import datetime
            data_filtro = datetime.strptime(data_inventario_filtro, '%Y-%m-%d').date()
        except ValueError:
            data_filtro = None
    else:
        data_filtro = None
    
    # Buscar inventário - usar data específica se fornecida, senão buscar o mais recente de cada categoria
    inventario_dict = {}
    if data_filtro:
        # Buscar inventário da data específica
        inventarios_recentes = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            categoria__in=categorias,
            data_inventario=data_filtro
        ).select_related('categoria').order_by('categoria')
    else:
        # Buscar inventário mais recente de cada categoria
        inventarios_recentes = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            categoria__in=categorias
        ).select_related('categoria').order_by('categoria', '-data_inventario')
    
    # Agrupar por categoria, mantendo apenas o mais recente de cada uma (se não houver data específica)
    for inv in inventarios_recentes:
        if data_filtro:
            # Com data específica, usar todos os itens dessa data
            inventario_dict[inv.categoria_id] = inv
        else:
            # Sem data específica, manter apenas o mais recente de cada categoria
            if inv.categoria_id not in inventario_dict:
                inventario_dict[inv.categoria_id] = inv
    
    for categoria in categorias:
        inventario = inventario_dict.get(categoria.id)
        
        quantidade = inventario.quantidade if inventario else 0
        valor_por_cabeca = inventario.valor_por_cabeca if inventario else Decimal('0.00')
        valor_total = inventario.valor_total if inventario else Decimal('0.00')
        
        total_quantidade += quantidade
        total_valor += valor_total
        
        categorias_com_inventario.append({
            'categoria': categoria,
            'quantidade': quantidade,
            'valor_por_cabeca': valor_por_cabeca,
            'valor_total': valor_total,
            'data_inventario': inventario.data_inventario if inventario else None
        })
    
    # Calcular valor médio por cabeça
    valor_medio = total_valor / total_quantidade if total_quantidade > 0 else Decimal('0.00')
    
    # Determinar a data do inventário a ser exibida
    # Prioridade: 1) Data na URL (após salvar), 2) Data do inventário mais recente
    data_inventario_atual = data_filtro
    
    if not data_inventario_atual:
        # Se não há data específica, buscar a data do inventário mais recente (se existir)
        inventario_mais_recente = InventarioRebanho.objects.filter(
            propriedade=propriedade
        ).order_by('-data_inventario').first()
        
        data_inventario_atual = inventario_mais_recente.data_inventario if inventario_mais_recente else None
    
    context = {
        'propriedade': propriedade,
        'categorias_com_inventario': categorias_com_inventario,
        'total_quantidade': total_quantidade,
        'total_valor': total_valor,
        'valor_medio': valor_medio,
        'tem_inventario': any(item['quantidade'] > 0 for item in categorias_com_inventario),
        'data_inventario_atual': data_inventario_atual,
    }
    
    return render(request, 'gestao_rural/pecuaria_inventario.html', context)


@login_required
def pecuaria_parametros_avancados(request, propriedade_id):
    """Configurações avançadas de vendas e reposição"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Obter categorias e outras propriedades
    categorias = CategoriaAnimal.objects.all().order_by('sexo', 'idade_minima_meses')
    outras_fazendas = Propriedade.objects.filter(produtor__usuario_responsavel=request.user).exclude(id=propriedade_id)
    
    if request.method == 'POST':
        if 'salvar_configuracoes' in request.POST:
            # Processar configurações de venda
            categoria_venda_id = request.POST.get('categoria_venda')
            frequencia_venda = request.POST.get('frequencia_venda')
            quantidade_venda = request.POST.get('quantidade_venda')
            tipo_reposicao = request.POST.get('tipo_reposicao')
            
            if categoria_venda_id and frequencia_venda and quantidade_venda and tipo_reposicao:
                categoria_venda = get_object_or_404(CategoriaAnimal, id=categoria_venda_id)
                
                # Criar configuração de venda
                configuracao = ConfiguracaoVenda.objects.create(
                    propriedade=propriedade,
                    categoria_venda=categoria_venda,
                    frequencia_venda=frequencia_venda,
                    quantidade_venda=int(quantidade_venda),
                    tipo_reposicao=tipo_reposicao
                )
                
                # Configurações de transferência
                if tipo_reposicao == 'TRANSFERENCIA':
                    fazenda_origem_id = request.POST.get('fazenda_origem')
                    quantidade_transferencia = request.POST.get('quantidade_transferencia')
                    
                    if fazenda_origem_id and quantidade_transferencia:
                        fazenda_origem = get_object_or_404(Propriedade, id=fazenda_origem_id)
                        configuracao.fazenda_origem = fazenda_origem
                        configuracao.quantidade_transferencia = int(quantidade_transferencia)
                        configuracao.save()
                
                # Configurações de compra
                elif tipo_reposicao == 'COMPRA':
                    categoria_compra_id = request.POST.get('categoria_compra')
                    quantidade_compra = request.POST.get('quantidade_compra')
                    valor_animal_venda = request.POST.get('valor_animal_venda')
                    percentual_desconto = request.POST.get('percentual_desconto')
                    
                    if categoria_compra_id and quantidade_compra:
                        categoria_compra = get_object_or_404(CategoriaAnimal, id=categoria_compra_id)
                        configuracao.categoria_compra = categoria_compra
                        configuracao.quantidade_compra = int(quantidade_compra)
                        
                        if valor_animal_venda:
                            configuracao.valor_animal_venda = Decimal(valor_animal_venda)
                        
                        if percentual_desconto:
                            configuracao.percentual_desconto = Decimal(percentual_desconto)
                            # Calcular valor da compra
                            if configuracao.valor_animal_venda and configuracao.percentual_desconto:
                                configuracao.valor_animal_compra = configuracao.calcular_valor_compra()
                        
                        configuracao.save()
                
                messages.success(request, 'Configuração de venda salva com sucesso!')
                return redirect('pecuaria_parametros_avancados', propriedade_id=propriedade_id)
    
    # Obter configurações existentes
    configuracoes = ConfiguracaoVenda.objects.filter(propriedade=propriedade, ativo=True).order_by('-data_criacao')
    
    context = {
        'propriedade': propriedade,
        'categorias': categorias,
        'outras_fazendas': outras_fazendas,
        'configuracoes': configuracoes,
    }
    
    return render(request, 'gestao_rural/pecuaria_parametros_avancados.html', context)


@login_required
def pecuaria_parametros(request, propriedade_id):
    """Configuração dos parâmetros de projeção do rebanho"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Buscar ou criar parâmetros
    parametros, created = ParametrosProjecaoRebanho.objects.get_or_create(
        propriedade=propriedade,
        defaults={
            'taxa_natalidade_anual': Decimal('85.00'),
            'taxa_mortalidade_bezerros_anual': Decimal('5.00'),
            'taxa_mortalidade_adultos_anual': Decimal('2.00'),
            'percentual_venda_machos_anual': Decimal('90.00'),
            'percentual_venda_femeas_anual': Decimal('10.00'),
            'periodicidade': 'MENSAL',
        }
    )
    
    if request.method == 'POST':
        # Processar formulário de parâmetros básicos
        form = ParametrosProjecaoForm(request.POST, instance=parametros)
        if form.is_valid():
            parametros = form.save()
            
            # Processar política de vendas por categoria
            politica_vendas_data = request.POST.get('politica_vendas_data')
            if politica_vendas_data:
                try:
                    vendas_data = json.loads(politica_vendas_data)
                    
                    # Limpar políticas existentes
                    PoliticaVendasCategoria.objects.filter(propriedade=propriedade).delete()
                    
                    # Criar novas políticas
                    for item in vendas_data:
                        if item.get('percentual_venda', 0) > 0 or item.get('quantidade_venda', 0) > 0:
                            PoliticaVendasCategoria.objects.create(
                                propriedade=propriedade,
                                categoria_id=item['categoria_id'],
                                percentual_venda=item.get('percentual_venda', 0),
                                quantidade_venda=item.get('quantidade_venda', 0),
                                valor_por_cabeca_personalizado=item.get('valor_por_cabeca_personalizado', 0),
                                usar_valor_personalizado=item.get('usar_valor_personalizado', False),
                                reposicao_tipo=item.get('reposicao_tipo', 'NAO_REP'),
                                origem_fazenda_id=item.get('origem_fazenda') if item.get('origem_fazenda') else None,
                                quantidade_transferir=item.get('quantidade_transferir', 0),
                                quantidade_comprar=item.get('quantidade_comprar', 0)
                            )
                    
                    messages.success(request, 'Parâmetros e políticas de vendas salvos com sucesso!')
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Erro ao processar política de vendas: {e}")
                    messages.warning(request, 'Erro ao processar política de vendas. Parâmetros básicos salvos.')
            else:
                messages.success(request, 'Parâmetros salvos com sucesso!')
            
            # Aplicar parâmetros do tipo de ciclo
            parametros = aplicar_parametros_ciclo(propriedade, parametros)
            return redirect('pecuaria_dashboard', propriedade_id=propriedade.id)
    else:
        form = ParametrosProjecaoForm(instance=parametros)
        # Aplicar parâmetros padrão do tipo de ciclo
        parametros = aplicar_parametros_ciclo(propriedade, parametros)
    
    # Obter categorias ordenadas (Fêmeas primeiro, depois Machos)
    categorias = CategoriaAnimal.objects.filter(ativo=True).annotate(
        ordem_sexo=Case(
            When(sexo='F', then=1),
            When(sexo='M', then=2),
            When(sexo='I', then=3),
            default=4,
            output_field=IntegerField(),
        )
    ).order_by('ordem_sexo', 'idade_minima_meses', 'idade_maxima_meses', 'nome')
    
    # Obter outras fazendas do mesmo produtor
    outras_fazendas = Propriedade.objects.filter(
        produtor=propriedade.produtor
    ).exclude(id=propriedade_id)
    
    # Obter políticas existentes
    politicas_existentes = PoliticaVendasCategoria.objects.filter(propriedade=propriedade).select_related('categoria', 'origem_fazenda')
    
    # Preparar dados das categorias com políticas
    categorias_com_politica = []
    for categoria in categorias:
        politica = politicas_existentes.filter(categoria=categoria).first()
        categorias_com_politica.append({
            'categoria': categoria,
            'politica': politica
        })
    
    context = {
        'propriedade': propriedade,
        'form': form,
        'parametros': parametros,
        'categorias_com_politica': categorias_com_politica,
        'outras_fazendas': outras_fazendas,
    }
    return render(request, 'gestao_rural/pecuaria_parametros.html', context)


@login_required
def pecuaria_projecao(request, propriedade_id):
    """Visualização e geração da projeção do rebanho - REFATORADO"""
    from django.core.cache import cache
    from django.db.models import Max
    from collections import defaultdict
    from datetime import date
    
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Obter inventário mais recente
    from django.db.models import Max
    data_inventario_recente = InventarioRebanho.objects.filter(
        propriedade=propriedade
    ).aggregate(Max('data_inventario'))['data_inventario__max']
    
    if data_inventario_recente:
        inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario=data_inventario_recente
        ).select_related('categoria').order_by('categoria__nome')
    else:
        inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade
        ).select_related('categoria').order_by('categoria__nome')
    
    # Armazenar data do inventário para usar como início da projeção
    data_inicio_projecao = data_inventario_recente
    
    parametros = ParametrosProjecaoRebanho.objects.filter(propriedade=propriedade).first()
    
    # Se for usuário demo, criar parâmetros automaticamente se não existirem
    # Isso permite que usuários demo pulem a etapa de configuração e vão direto para gerar projeção
    if not parametros:
        # Verificar se é usuário demo
        is_demo_user = False
        if request.user.username in ['demo', 'demo_monpec']:
            is_demo_user = True
        else:
            try:
                from .models_auditoria import UsuarioAtivo
                UsuarioAtivo.objects.get(usuario=request.user)
                is_demo_user = True
            except:
                pass
        
        if is_demo_user:
            # Criar parâmetros automaticamente com valores padrão
            parametros, created = ParametrosProjecaoRebanho.objects.get_or_create(
                propriedade=propriedade,
                defaults={
                    'taxa_natalidade_anual': Decimal('85.00'),
                    'taxa_mortalidade_bezerros_anual': Decimal('5.00'),
                    'taxa_mortalidade_adultos_anual': Decimal('2.00'),
                    'percentual_venda_machos_anual': Decimal('90.00'),
                    'percentual_venda_femeas_anual': Decimal('10.00'),
                    'periodicidade': 'MENSAL',
                }
            )
            logger.info(f'Parâmetros de projeção criados automaticamente para usuário demo: {request.user.username}')
        else:
            # Para usuários não-demo, redirecionar para configurar parâmetros
            messages.error(request, 'É necessário configurar os parâmetros de projeção primeiro.')
            return redirect('pecuaria_parametros', propriedade_id=propriedade.id)
    
    # Validações básicas
    if not inventario.exists():
        messages.error(request, 'É necessário cadastrar o inventário inicial primeiro.')
        return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
    
    # Processar POST - Gerar nova projeção
    if request.method == 'POST':
        try:
            anos_projecao = int(request.POST.get('anos_projecao', 5))
            
            if not (1 <= anos_projecao <= 20):
                messages.error(request, 'Número de anos deve estar entre 1 e 20.')
                return redirect('pecuaria_projecao', propriedade_id=propriedade.id)
            
            logger.info(f"Gerando projeção para {propriedade.nome_propriedade} - {anos_projecao} anos")
            
            # Sempre criar um NOVO planejamento com nova ID para cada geração
            from django.utils import timezone
            from .models import PlanejamentoAnual
            from datetime import datetime
            ano_atual = timezone.now().year
            
            # Criar novo planejamento sempre
            planejamento = PlanejamentoAnual.objects.create(
                propriedade=propriedade,
                ano=ano_atual,
                descricao=f'Planejamento {ano_atual} - Projeção do Rebanho - {datetime.now().strftime("%d/%m/%Y %H:%M")}',
                status='RASCUNHO'
            )
            
            # O código será gerado automaticamente no save()
            logger.info(f"Novo planejamento criado: {planejamento.codigo}")
            
            # Obter data do inventário para iniciar a projeção
            data_inventario = InventarioRebanho.objects.filter(
                propriedade=propriedade
            ).aggregate(Max('data_inventario'))['data_inventario__max']
            
            # Gerar projeção vinculada ao planejamento
            gerar_projecao(propriedade, anos_projecao, data_inventario, planejamento=planejamento)
            
            # Invalidar cache
            cache.delete(f'projecao_{propriedade_id}')
            
            messages.success(
                request, 
                f'✅ Projeção gerada com sucesso para {anos_projecao} anos! '
                f'ID da Projeção: {planejamento.codigo}. '
                f'Use este ID para buscar a projeção na página de Cenários ou vinculá-la a um Projeto Bancário.'
            )
            # Redirecionar para a página de projeção, que vai abrir a planilha em nova aba via JavaScript
            return redirect('pecuaria_projecao', propriedade_id=propriedade.id)
            
        except ValueError as e:
            messages.error(request, f'Erro ao gerar projeção: {str(e)}')
        except Exception as e:
            logger.error(f"Erro ao gerar projeção: {e}", exc_info=True)
            messages.error(request, 'Erro inesperado ao gerar projeção. Tente novamente.')
    
    # Buscar movimentações projetadas
    cache_key = f'projecao_{propriedade_id}'
    movimentacoes = cache.get(cache_key)
    
    if not movimentacoes:
        movimentacoes = list(
            MovimentacaoProjetada.objects
            .filter(propriedade=propriedade)
            .select_related('categoria')
            .order_by('data_movimentacao')
        )
        logger.info(f"Movimentações encontradas no banco: {len(movimentacoes)}")
        if movimentacoes:
            cache.set(cache_key, movimentacoes, 1800)
        else:
            logger.warning(f"Nenhuma movimentação encontrada para propriedade {propriedade_id}")
    
    # Processar dados da projeção
    resumo_projecao_por_ano = {}
    evolucao_detalhada = {}
    
    if movimentacoes:
        try:
            logger.info(f"Processando {len(movimentacoes)} movimentações para resumo por ano")
            logger.info(f"Inventário inicial: {len(inventario)} itens")
            # Converter inventário para lista se necessário
            inventario_lista = list(inventario) if not isinstance(inventario, list) else inventario
            resumo_projecao_por_ano = gerar_resumo_projecao_por_ano(movimentacoes, inventario_lista, propriedade)
            logger.info(f"Resumo gerado com {len(resumo_projecao_por_ano)} anos")
            # Extrair ano da primeira movimentação se disponível
            ano_projecao = movimentacoes[0].data_movimentacao.year if movimentacoes else None
            evolucao_detalhada = gerar_evolucao_detalhada_rebanho(movimentacoes, inventario_lista, propriedade, ano_projecao)
        except Exception as e:
            logger.error(f"Erro ao processar dados de projeção: {e}", exc_info=True)
    
    # Calcular totais do inventário
    total_femeas = sum(
        item.quantidade for item in inventario
        if any(termo in item.categoria.nome.lower() 
               for termo in ['fêmea', 'femea', 'bezerra', 'novilha', 'primípara', 'multípara', 'vaca'])
    )
    
    total_machos = sum(
        item.quantidade for item in inventario
        if any(termo in item.categoria.nome.lower() 
               for termo in ['macho', 'bezerro', 'garrote', 'boi', 'touro'])
    )
    
    # Total geral deve ser a soma de fêmeas + machos para garantir consistência
    total_geral = total_femeas + total_machos
    
    # Calcular estatísticas da projeção
    estatisticas = {
        'total_anos': len(resumo_projecao_por_ano) if resumo_projecao_por_ano else 0,
        'total_movimentacoes': len(movimentacoes),
        'tem_projecao': len(movimentacoes) > 0,
    }
    
    # Calcular evolução total do rebanho
    evolucao_rebanho = []
    saldo_atual = total_geral
    
    # Ordenar anos para exibição ordenada no template
    resumo_projecao_por_ano_ordenado = {}
    if resumo_projecao_por_ano:
        for ano in sorted(resumo_projecao_por_ano.keys()):
            dados = resumo_projecao_por_ano[ano]
            resumo_projecao_por_ano_ordenado[ano] = dados
            
            # Preparar dados para gráfico
            evolucao_rebanho.append({
                'ano': ano,
                'saldo_inicial': dados.get('totais', {}).get('saldo_inicial_total', 0),
                'saldo_final': dados.get('totais', {}).get('saldo_final_total', 0),
                'variacao': dados.get('totais', {}).get('saldo_final_total', 0) - dados.get('totais', {}).get('saldo_inicial_total', 0),
                'receitas': float(dados.get('totais', {}).get('receitas_total', 0)),
                'custos': float(dados.get('totais', {}).get('custos_total', 0)),
            })
    else:
        resumo_projecao_por_ano_ordenado = {}
    
    # Buscar planejamento mais recente para exibir o ID
    from django.utils import timezone
    from .models import PlanejamentoAnual
    ano_atual = timezone.now().year
    planejamento_atual = PlanejamentoAnual.objects.filter(
        propriedade=propriedade
    ).order_by('-ano', '-data_criacao').first()
    
    context = {
        'propriedade': propriedade,
        'inventario': inventario,
        'parametros': parametros,
        'movimentacoes': movimentacoes,
        'resumo_projecao_por_ano': resumo_projecao_por_ano_ordenado,
        'evolucao_detalhada': evolucao_detalhada,
        'total_femeas': total_femeas,
        'total_machos': total_machos,
        'total_geral': total_geral,
        'estatisticas': estatisticas,
        'evolucao_rebanho': evolucao_rebanho,
        'data_inventario_recente': data_inventario_recente,
        'planejamento_atual': planejamento_atual,  # Adicionado para exibir ID
    }
    
    return render(request, 'gestao_rural/pecuaria_projecao.html', context)


@login_required
def pecuaria_projecao_planilha(request, propriedade_id):
    """Visualização da planilha de projeção sem menu lateral (para nova aba)"""
    from django.core.cache import cache
    from django.db.models import Max
    from collections import defaultdict
    from datetime import date
    from .models import Propriedade, InventarioRebanho, MovimentacaoProjetada
    
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Obter inventário mais recente
    data_inventario_recente = InventarioRebanho.objects.filter(
        propriedade=propriedade
    ).aggregate(Max('data_inventario'))['data_inventario__max']
    
    if data_inventario_recente:
        inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario=data_inventario_recente
        ).select_related('categoria').order_by('categoria__nome')
    else:
        inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade
        ).select_related('categoria').order_by('categoria__nome')
    
    # Buscar movimentações projetadas
    cache_key = f'projecao_{propriedade_id}'
    movimentacoes = cache.get(cache_key)
    
    if not movimentacoes:
        movimentacoes = list(
            MovimentacaoProjetada.objects
            .filter(propriedade=propriedade)
            .select_related('categoria')
            .order_by('data_movimentacao')
        )
        if movimentacoes:
            cache.set(cache_key, movimentacoes, 1800)
    
    # Processar dados da projeção
    resumo_projecao_por_ano = {}
    evolucao_detalhada = {}
    
    if movimentacoes:
        try:
            # Converter inventário para lista se necessário
            inventario_lista = list(inventario) if not isinstance(inventario, list) else inventario
            # As funções gerar_resumo_projecao_por_ano e gerar_evolucao_detalhada_rebanho 
            # estão definidas no mesmo arquivo, então podem ser chamadas diretamente
            resumo_projecao_por_ano = gerar_resumo_projecao_por_ano(movimentacoes, inventario_lista, propriedade)
            # Extrair ano da primeira movimentação se disponível
            ano_projecao = movimentacoes[0].data_movimentacao.year if movimentacoes else None
            evolucao_detalhada = gerar_evolucao_detalhada_rebanho(movimentacoes, inventario_lista, propriedade, ano_projecao)
        except Exception as e:
            logger.error(f"Erro ao processar dados de projeção: {e}", exc_info=True)
    
    # Calcular totais do inventário
    total_femeas = sum(
        item.quantidade for item in inventario
        if any(termo in item.categoria.nome.lower() 
               for termo in ['fêmea', 'femea', 'bezerra', 'novilha', 'primípara', 'multípara', 'vaca'])
    )
    
    total_machos = sum(
        item.quantidade for item in inventario
        if any(termo in item.categoria.nome.lower() 
               for termo in ['macho', 'bezerro', 'garrote', 'boi', 'touro'])
    )
    
    total_geral = total_femeas + total_machos
    
    # Calcular estatísticas da projeção
    estatisticas = {
        'total_anos': len(resumo_projecao_por_ano) if resumo_projecao_por_ano else 0,
        'total_movimentacoes': len(movimentacoes),
        'tem_projecao': len(movimentacoes) > 0,
    }
    
    # Calcular evolução total do rebanho
    evolucao_rebanho = []
    saldo_atual = total_geral
    
    # Ordenar anos para exibição ordenada no template
    resumo_projecao_por_ano_ordenado = {}
    if resumo_projecao_por_ano:
        for ano in sorted(resumo_projecao_por_ano.keys()):
            dados = resumo_projecao_por_ano[ano]
            resumo_projecao_por_ano_ordenado[ano] = dados
            
            # Preparar dados para gráfico
            evolucao_rebanho.append({
                'ano': ano,
                'saldo_inicial': dados.get('totais', {}).get('saldo_inicial_total', 0),
                'saldo_final': dados.get('totais', {}).get('saldo_final_total', 0),
                'variacao': dados.get('totais', {}).get('saldo_final_total', 0) - dados.get('totais', {}).get('saldo_inicial_total', 0),
                'receitas': float(dados.get('totais', {}).get('receitas_total', 0)),
            })
            saldo_atual = dados.get('totais', {}).get('saldo_final_total', 0)
    
    # Buscar planejamento atual (mais recente)
    planejamento_atual = None
    if movimentacoes:
        try:
            from .models import PlanejamentoAnual
            planejamento_atual = PlanejamentoAnual.objects.filter(
                propriedade=propriedade
            ).order_by('-data_criacao', '-ano').first()
        except:
            pass
    
    context = {
        'propriedade': propriedade,
        'inventario': inventario,
        'resumo_projecao_por_ano': resumo_projecao_por_ano_ordenado,
        'evolucao_detalhada': evolucao_detalhada,
        'total_femeas': total_femeas,
        'total_machos': total_machos,
        'total_geral': total_geral,
        'estatisticas': estatisticas,
        'evolucao_rebanho': evolucao_rebanho,
        'data_inventario_recente': data_inventario_recente,
        'planejamento_atual': planejamento_atual,
    }
    
    return render(request, 'gestao_rural/pecuaria_projecao_planilha.html', context)


def pecuaria_inventario_dados(request, propriedade_id):
    """View para retornar dados do inventário em JSON para a IA"""
    from datetime import date
    
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    # Obter inventário mais recente
    inventario_data = InventarioRebanho.objects.filter(
        propriedade=propriedade
    ).order_by('-data_inventario').first()
    
    # Calcular saldos atuais considerando movimentações
    data_atual = date.today()
    saldos_atuais = obter_saldo_atual_propriedade(propriedade, data_atual)
    
    # Obter todas as categorias para garantir que todas tenham saldo
    todas_categorias = CategoriaAnimal.objects.filter(ativo=True)
    
    # Converter saldos para formato com nome da categoria como chave
    saldos = {}
    for categoria in todas_categorias:
        # Usar o saldo calculado se existir, senão 0
        quantidade = saldos_atuais.get(categoria, 0)
        saldos[categoria.nome] = int(quantidade)
    
    if not inventario_data:
        # Se não há inventário, retornar apenas saldos
        return JsonResponse({
            'success': True,
            'saldos': saldos,
            'inventario': {},
            'data_inventario': None
        })
    
    # Obter todas as categorias e seus valores
    inventario = {}
    categorias = CategoriaAnimal.objects.all()
    
    for categoria in categorias:
        item = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            categoria=categoria,
            data_inventario=inventario_data.data_inventario
        ).first()
        
        if item:
            inventario[categoria.nome] = {
                'quantidade': item.quantidade,
                'valor_por_cabeca': float(item.valor_por_cabeca),
                'valor_total': float(item.valor_total)
            }
        else:
            inventario[categoria.nome] = {
                'quantidade': 0,
                'valor_por_cabeca': 0.0,
                'valor_total': 0.0
            }
        
        # Garantir que todas as categorias tenham saldo (mesmo que 0)
        if categoria.nome not in saldos:
            saldos[categoria.nome] = 0
    
    return JsonResponse({
        'success': True,
        'saldos': saldos,
        'inventario': inventario,
        'data_inventario': inventario_data.data_inventario.strftime('%d/%m/%Y')
    })


@login_required
def pecuaria_projecao_demo_planilha(request, propriedade_id):
    """View para exibir projeção de demonstração em formato planilha"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Verificar se é usuário demo
    if request.user.username not in ['demo_monpec', 'demo']:
        messages.error(request, 'Esta página é apenas para usuários de demonstração.')
        return redirect('pecuaria_projecao', propriedade_id=propriedade_id)
    
    # Obter número de anos da query string (padrão: 5)
    anos = int(request.GET.get('anos', 5))
    
    # Dados de exemplo para demonstração
    # Ordenar por idade e sexo: fêmeas primeiro (do mais novo para o mais velho), depois machos (do mais novo para o mais velho)
    categorias_ordenadas = [
        # Fêmeas (do mais novo para o mais velho)
        {'nome': 'Bezerras', 'cor': '#ffc107'},
        {'nome': 'Novilhas', 'cor': '#fd7e14'},
        {'nome': 'Primíparas', 'cor': '#e83e8c'},
        {'nome': 'Vacas', 'cor': '#28a745'},
        # Machos (do mais novo para o mais velho)
        {'nome': 'Bezerros', 'cor': '#17a2b8'},
        {'nome': 'Garrotes', 'cor': '#6c757d'},
        {'nome': 'Touros', 'cor': '#007bff'},
    ]
    
    dados_demo = {
        'propriedade': propriedade,
        'anos': anos,
        'anos_lista': list(range(1, anos + 1)),
        'categorias': categorias_ordenadas,
    }
    
    # Gerar dados de exemplo para cada ano e categoria
    projecao_demo = {}
    for ano in dados_demo['anos_lista']:
        ano_atual = datetime.now().year + ano - 1
        projecao_demo[ano_atual] = {}
        
        for categoria in dados_demo['categorias']:
            nome_cat = categoria['nome']
            # Valores de exemplo baseados na categoria
            if nome_cat == 'Vacas':
                saldo_inicial = 500 if ano == 1 else projecao_demo[ano_atual - 1][nome_cat]['saldo_final']
                nascimentos = 350
                compras = 0
                vendas = 100
                mortes = 5
                transferencias_entrada = 0
                transferencias_saida = 0
                evolucao = 0
                saldo_final = saldo_inicial + nascimentos + compras - vendas - mortes + transferencias_entrada - transferencias_saida + evolucao
                peso_medio = 450.0
                valor_unitario = 3500.00
            elif nome_cat == 'Bezerros':
                saldo_inicial = 200 if ano == 1 else projecao_demo[ano_atual - 1][nome_cat]['saldo_final']
                nascimentos = 175
                compras = 0
                vendas = 50
                mortes = 3
                transferencias_entrada = 0
                transferencias_saida = 0
                evolucao = -150  # Evoluem para garrotes
                saldo_final = saldo_inicial + nascimentos + compras - vendas - mortes + transferencias_entrada - transferencias_saida + evolucao
                peso_medio = 180.0
                valor_unitario = 1200.00
            elif nome_cat == 'Bezerras':
                saldo_inicial = 180 if ano == 1 else projecao_demo[ano_atual - 1][nome_cat]['saldo_final']
                nascimentos = 175
                compras = 0
                vendas = 30
                mortes = 2
                transferencias_entrada = 0
                transferencias_saida = 0
                evolucao = -150  # Evoluem para novilhas
                saldo_final = saldo_inicial + nascimentos + compras - vendas - mortes + transferencias_entrada - transferencias_saida + evolucao
                peso_medio = 170.0
                valor_unitario = 1100.00
            elif nome_cat == 'Garrotes':
                saldo_inicial = 150 if ano == 1 else projecao_demo[ano_atual - 1][nome_cat]['saldo_final']
                nascimentos = 0
                compras = 0
                vendas = 80
                mortes = 2
                transferencias_entrada = 150  # Vêm de bezerros
                transferencias_saida = 0
                evolucao = -70  # Evoluem para touros ou vendas
                saldo_final = saldo_inicial + nascimentos + compras - vendas - mortes + transferencias_entrada - transferencias_saida + evolucao
                peso_medio = 320.0
                valor_unitario = 2800.00
            elif nome_cat == 'Novilhas':
                saldo_inicial = 140 if ano == 1 else projecao_demo[ano_atual - 1][nome_cat]['saldo_final']
                nascimentos = 0
                compras = 0
                vendas = 20
                mortes = 1
                transferencias_entrada = 150  # Vêm de bezerras
                transferencias_saida = 0
                evolucao = -120  # Evoluem para primíparas
                saldo_final = saldo_inicial + nascimentos + compras - vendas - mortes + transferencias_entrada - transferencias_saida + evolucao
                peso_medio = 300.0
                valor_unitario = 2500.00
            elif nome_cat == 'Primíparas':
                saldo_inicial = 120 if ano == 1 else projecao_demo[ano_atual - 1][nome_cat]['saldo_final']
                nascimentos = 0
                compras = 0
                vendas = 30
                mortes = 1
                transferencias_entrada = 120  # Vêm de novilhas
                transferencias_saida = 0
                evolucao = -90  # Evoluem para vacas
                saldo_final = saldo_inicial + nascimentos + compras - vendas - mortes + transferencias_entrada - transferencias_saida + evolucao
                peso_medio = 380.0
                valor_unitario = 3200.00
            else:  # Touros
                saldo_inicial = 30 if ano == 1 else projecao_demo[ano_atual - 1][nome_cat]['saldo_final']
                nascimentos = 0
                compras = 5
                vendas = 2
                mortes = 1
                transferencias_entrada = 70  # Vêm de garrotes
                transferencias_saida = 0
                evolucao = 0
                saldo_final = saldo_inicial + nascimentos + compras - vendas - mortes + transferencias_entrada - transferencias_saida + evolucao
                peso_medio = 650.0
                valor_unitario = 4500.00
            
            valor_total = saldo_final * valor_unitario
            
            projecao_demo[ano_atual][nome_cat] = {
                'saldo_inicial': saldo_inicial,
                'nascimentos': nascimentos,
                'compras': compras,
                'vendas': vendas,
                'mortes': mortes,
                'transferencias_entrada': transferencias_entrada,
                'transferencias_saida': transferencias_saida,
                'evolucao': evolucao,
                'saldo_final': saldo_final,
                'peso_medio': peso_medio,
                'valor_unitario': valor_unitario,
                'valor_total': valor_total,
            }
    
    dados_demo['projecao'] = projecao_demo
    
    # Calcular totais e médias para cada ano
    totais_por_ano = {}
    for ano_atual, dados_ano in projecao_demo.items():
        total_saldo_inicial = 0
        total_nascimentos = 0
        total_compras = 0
        total_vendas = 0
        total_mortes = 0
        total_transf_entrada = 0
        total_transf_saida = 0
        total_evolucao = 0
        total_saldo_final = 0
        soma_peso_medio = 0
        soma_valor_unitario = 0
        total_valor_total = 0
        contador = 0
        
        for categoria in categorias_ordenadas:
            nome_cat = categoria['nome']
            if nome_cat in dados_ano:
                dados = dados_ano[nome_cat]
                total_saldo_inicial += dados['saldo_inicial']
                total_nascimentos += dados['nascimentos']
                total_compras += dados['compras']
                total_vendas += dados['vendas']
                total_mortes += dados['mortes']
                total_transf_entrada += dados['transferencias_entrada']
                total_transf_saida += dados['transferencias_saida']
                total_evolucao += dados['evolucao']
                total_saldo_final += dados['saldo_final']
                soma_peso_medio += dados['peso_medio']
                soma_valor_unitario += dados['valor_unitario']
                total_valor_total += dados['valor_total']
                contador += 1
        
        totais_por_ano[ano_atual] = {
            'total_saldo_inicial': total_saldo_inicial,
            'total_nascimentos': total_nascimentos,
            'total_compras': total_compras,
            'total_vendas': total_vendas,
            'total_mortes': total_mortes,
            'total_transf_entrada': total_transf_entrada,
            'total_transf_saida': total_transf_saida,
            'total_evolucao': total_evolucao,
            'total_saldo_final': total_saldo_final,
            'media_peso_medio': soma_peso_medio / contador if contador > 0 else 0,
            'media_valor_unitario': soma_valor_unitario / contador if contador > 0 else 0,
            'total_valor_total': total_valor_total,
        }
    
    dados_demo['totais_por_ano'] = totais_por_ano
    
    return render(request, 'gestao_rural/pecuaria_projecao_demo_planilha.html', dados_demo)


def gerar_projecao(propriedade, anos, data_inicio_projecao=None, planejamento=None, cenario=None):
    """Função para gerar a projeção do rebanho com IA Inteligente
    
    Args:
        propriedade: Propriedade
        anos: Número de anos para projetar
        data_inicio_projecao: Data de início da projeção (opcional)
        planejamento: PlanejamentoAnual para vincular as movimentações (opcional)
        cenario: CenarioPlanejamento para vincular as movimentações (opcional)
    """
    from .ia_movimentacoes_automaticas import sistema_movimentacoes
    from django.db import transaction
    from datetime import date
    
    # Buscar inventário inicial
    inventario_inicial = InventarioRebanho.objects.filter(propriedade=propriedade)
    
    # Validações
    if not inventario_inicial.exists():
        raise ValueError(f"Inventário inicial não cadastrado para {propriedade.nome_propriedade}")
    
    # Se não foi passada data de início, usar a data do inventário mais recente
    from django.db.models import Max
    if not data_inicio_projecao:
        data_inicio_projecao = InventarioRebanho.objects.filter(
            propriedade=propriedade
        ).aggregate(Max('data_inventario'))['data_inventario__max']
    
    # Se ainda não tiver data, usar data atual
    if not data_inicio_projecao:
        data_inicio_projecao = date.today()
    
    try:
        parametros = ParametrosProjecaoRebanho.objects.get(propriedade=propriedade)
    except ParametrosProjecaoRebanho.DoesNotExist:
        raise ValueError(f"Parâmetros de projeção não configurados para {propriedade.nome_propriedade}")
    
    logger.info(f"Iniciando geração de projeção INTELIGENTE para {propriedade.nome_propriedade}")
    logger.info(f"Data de início da projeção: {data_inicio_projecao}")
    logger.info(f"Planejamento: {planejamento.codigo if planejamento else 'Nenhum'}")
    logger.info(f"Cenário: {cenario.nome if cenario else 'Nenhum'}")
    logger.info(f"Parâmetros: Natalidade={parametros.taxa_natalidade_anual}%, Mortalidade Bezerros={parametros.taxa_mortalidade_bezerros_anual}%, Mortalidade Adultos={parametros.taxa_mortalidade_adultos_anual}%")
    logger.info(f"Anos de projeção: {anos}")
    
    # Gerar movimentações com transação atômica
    try:
        with transaction.atomic():
            # Limpar projeções anteriores vinculadas ao planejamento/cenário se especificado
            if planejamento:
                # Limpar apenas movimentações do planejamento
                MovimentacaoProjetada.objects.filter(
                    propriedade=propriedade,
                    planejamento=planejamento
                ).delete()
                logger.info(f"Projeções anteriores do planejamento {planejamento.codigo} limpas")
            else:
                # Limpar todas as projeções da propriedade (comportamento antigo)
                MovimentacaoProjetada.objects.filter(propriedade=propriedade).delete()
                logger.info("Projeções anteriores limpas")
            
            # Usar sistema inteligente para gerar todas as movimentações
            movimentacoes = sistema_movimentacoes.gerar_movimentacoes_completas(
                propriedade, parametros, inventario_inicial, anos, data_inicio_projecao
            )
            logger.info(f"Movimentações geradas: {len(movimentacoes)}")
            
            # Vincular movimentações ao planejamento/cenário
            for movimentacao in movimentacoes:
                if planejamento:
                    movimentacao.planejamento = planejamento
                if cenario:
                    movimentacao.cenario = cenario
            
            # Salvar todas as movimentações no banco
            movimentacoes_salvas = 0
            for movimentacao in movimentacoes:
                try:
                    movimentacao.save()
                    movimentacoes_salvas += 1
                except Exception as e:
                    logger.error(f"Erro ao salvar movimentação {movimentacao}: {e}", exc_info=True)
                    raise  # Re-raise para fazer rollback da transação
            
            logger.info(f"Total de movimentações INTELIGENTES geradas e salvas: {movimentacoes_salvas}/{len(movimentacoes)}")
    except Exception as e:
        logger.error(f"Erro ao gerar projeção: {e}", exc_info=True)
        raise  # Re-raise para que a view possa tratar o erro
    
    return movimentacoes


@login_required
def relatorio_final(request, propriedade_id):
    """Relatório final para análise bancária"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Dados da pecuária
    inventario_pecuaria = InventarioRebanho.objects.filter(propriedade=propriedade)
    parametros_pecuaria = ParametrosProjecaoRebanho.objects.filter(propriedade=propriedade).first()
    movimentacoes_pecuaria = MovimentacaoProjetada.objects.filter(propriedade=propriedade)
    
    # Cálculos de resumo
    total_rebanho_atual = inventario_pecuaria.aggregate(total=Sum('quantidade'))['total'] or 0
    
    context = {
        'propriedade': propriedade,
        'inventario_pecuaria': inventario_pecuaria,
        'parametros_pecuaria': parametros_pecuaria,
        'movimentacoes_pecuaria': movimentacoes_pecuaria,
        'total_rebanho_atual': total_rebanho_atual,
    }
    return render(request, 'gestao_rural/relatorio_final.html', context)


def gerar_resumo_projecao_tabela(movimentacoes, periodicidade):
    """Gera resumo da projeção em formato de tabela por período"""
    from collections import defaultdict
    from datetime import datetime
    
    resumo = defaultdict(lambda: {
        'nascimentos_femeas': 0,
        'nascimentos_machos': 0,
        'vendas_femeas': 0,
        'vendas_machos': 0,
        'mortes_femeas': 0,
        'mortes_machos': 0,
        'total_rebanho': 0
    })
    
    # Agrupar movimentações por período
    for mov in movimentacoes:
        data = mov.data_movimentacao
        if periodicidade == 'MENSAL':
            periodo = f"{data.month:02d}/{data.year}"
        elif periodicidade == 'TRIMESTRAL':
            trimestre = ((data.month - 1) // 3) + 1
            periodo = f"T{trimestre}/{data.year}"
        elif periodicidade == 'SEMESTRAL':
            semestre = 1 if data.month <= 6 else 2
            periodo = f"S{semestre}/{data.year}"
        else:  # ANUAL
            periodo = str(data.year)
        
        # Categorizar por tipo e sexo
        if mov.tipo_movimentacao == 'NASCIMENTO':
            if 'Fêmea' in mov.categoria.nome or 'Vaca' in mov.categoria.nome or 'Bezerra' in mov.categoria.nome:
                resumo[periodo]['nascimentos_femeas'] += mov.quantidade
            else:
                resumo[periodo]['nascimentos_machos'] += mov.quantidade
        elif mov.tipo_movimentacao == 'VENDA':
            if 'Fêmea' in mov.categoria.nome or 'Vaca' in mov.categoria.nome or 'Bezerra' in mov.categoria.nome:
                resumo[periodo]['vendas_femeas'] += mov.quantidade
            else:
                resumo[periodo]['vendas_machos'] += mov.quantidade
        elif mov.tipo_movimentacao == 'MORTE':
            if 'Fêmea' in mov.categoria.nome or 'Vaca' in mov.categoria.nome or 'Bezerra' in mov.categoria.nome:
                resumo[periodo]['mortes_femeas'] += mov.quantidade
            else:
                resumo[periodo]['mortes_machos'] += mov.quantidade
    
    # Calcular total do rebanho por período
    total_inicial = 0
    for periodo in sorted(resumo.keys()):
        resumo[periodo]['total_rebanho'] = (
            total_inicial + 
            resumo[periodo]['nascimentos_femeas'] + 
            resumo[periodo]['nascimentos_machos'] - 
            resumo[periodo]['vendas_femeas'] - 
            resumo[periodo]['vendas_machos'] - 
            resumo[periodo]['mortes_femeas'] - 
            resumo[periodo]['mortes_machos']
        )
        total_inicial = resumo[periodo]['total_rebanho']
    
    return dict(resumo)


def gerar_evolucao_categorias_tabela(movimentacoes, inventario_inicial):
    """Gera evolução das categorias em formato de tabela"""
    from collections import defaultdict
    from datetime import datetime
    
    # Inicializar com inventário inicial
    categorias_inicial = {}
    for item in inventario_inicial:
        categorias_inicial[item.categoria.nome] = item.quantidade
    
    # Agrupar movimentações por período e categoria
    evolucao = defaultdict(lambda: defaultdict(int))
    periodos = set()
    
    for mov in movimentacoes:
        data = mov.data_movimentacao
        periodo = f"{data.month:02d}/{data.year}"
        periodos.add(periodo)
        
        categoria = mov.categoria.nome
        
        if mov.tipo_movimentacao in ['NASCIMENTO', 'TRANSFERENCIA_ENTRADA']:
            evolucao[categoria][periodo] += mov.quantidade
        elif mov.tipo_movimentacao in ['VENDA', 'MORTE', 'TRANSFERENCIA_SAIDA']:
            evolucao[categoria][periodo] -= mov.quantidade
    
    # Ordenar períodos cronologicamente
    periodos_ordenados = sorted(periodos, key=lambda x: (int(x.split('/')[1]), int(x.split('/')[0])))
    
    # Calcular saldo acumulado por categoria
    resultado = {}
    for categoria, movimentacoes_cat in evolucao.items():
        saldo_anterior = categorias_inicial.get(categoria, 0)
        resultado[categoria] = [saldo_anterior]  # Saldo inicial
        
        for periodo in periodos_ordenados:
            saldo_anterior += movimentacoes_cat.get(periodo, 0)
            resultado[categoria].append(saldo_anterior)
    
    return resultado, periodos_ordenados


def gerar_evolucao_detalhada_rebanho(movimentacoes, inventario_inicial, propriedade=None, ano=None):
    """Gera evolução detalhada do rebanho com todas as movimentações do período completo"""
    from collections import defaultdict
    
    # Inicializar com inventário inicial
    categorias_inicial = {}
    for item in inventario_inicial:
        categorias_inicial[item.categoria.nome] = item.quantidade
    
    # Agrupar movimentações por categoria
    movimentacoes_por_categoria = defaultdict(lambda: {
        'nascimentos': 0,
        'compras': 0,
        'vendas': 0,
        'transferencias_entrada': 0,
        'transferencias_saida': 0,
        'promocao_entrada': 0,  # Promoção de categoria (envelhecimento)
        'promocao_saida': 0,    # Promoção de categoria (envelhecimento)
        'mortes': 0,
        'evolucao_categoria': None
    })
    
    # Processar TODAS as movimentações do período completo
    logger.debug(f"Processando {len(movimentacoes)} movimentações para evolução detalhada")
    
    for mov in movimentacoes:
        categoria = mov.categoria.nome
        
        if mov.tipo_movimentacao == 'NASCIMENTO':
            movimentacoes_por_categoria[categoria]['nascimentos'] += mov.quantidade
        elif mov.tipo_movimentacao == 'COMPRA':
            movimentacoes_por_categoria[categoria]['compras'] += mov.quantidade
        elif mov.tipo_movimentacao == 'VENDA':
            movimentacoes_por_categoria[categoria]['vendas'] += mov.quantidade
        elif mov.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA':
            # Distinguir entre transferência entre fazendas e promoção de categoria
            if 'Promoção' in mov.observacao:
                movimentacoes_por_categoria[categoria]['promocao_entrada'] += mov.quantidade
            else:
                movimentacoes_por_categoria[categoria]['transferencias_entrada'] += mov.quantidade
        elif mov.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
            # Distinguir entre transferência entre fazendas e promoção de categoria
            if 'Promoção' in mov.observacao:
                movimentacoes_por_categoria[categoria]['promocao_saida'] += mov.quantidade
            else:
                movimentacoes_por_categoria[categoria]['transferencias_saida'] += mov.quantidade
        elif mov.tipo_movimentacao == 'MORTE':
            movimentacoes_por_categoria[categoria]['mortes'] += mov.quantidade
    
    # Calcular saldo final e evolução de categoria
    resultado = {}
    for categoria, movs in movimentacoes_por_categoria.items():
        saldo_inicial = categorias_inicial.get(categoria, 0)
        
        # Calcular saldo final
        saldo_final = (saldo_inicial + 
                      movs['nascimentos'] + 
                      movs['compras'] + 
                      movs['transferencias_entrada'] + 
                      movs['promocao_entrada'] - 
                      movs['vendas'] - 
                      movs['transferencias_saida'] - 
                      movs['promocao_saida'] - 
                      movs['mortes'])
        
        # Calcular evolução de categoria baseada na promoção (envelhecimento)
        evolucao_categoria = None
        if movs['promocao_entrada'] > 0 or movs['promocao_saida'] > 0:
            # Se houve promoção, mostrar o saldo líquido da promoção
            saldo_promocao = movs['promocao_entrada'] - movs['promocao_saida']
            if saldo_promocao > 0:
                evolucao_categoria = f"+{saldo_promocao}"
            elif saldo_promocao < 0:
                evolucao_categoria = f"{saldo_promocao}"
            else:
                evolucao_categoria = "0"
        else:
            # Se não houve promoção, mostrar "-" para indicar que não evoluiu
            evolucao_categoria = "-"
        
        # Mostrar nascimentos apenas para categorias de 0-12 meses
        nascimentos_display = movs['nascimentos'] if any(termo in categoria.lower() for termo in ['bezerro', 'bezerra', '0-12']) else 0
        
        # Obter peso médio da categoria
        try:
            categoria_obj = CategoriaAnimal.objects.get(nome=categoria)
            peso_medio_kg = categoria_obj.peso_medio_kg or Decimal('0.00')
        except CategoriaAnimal.DoesNotExist:
            peso_medio_kg = Decimal('0.00')
        
        # Calcular valor unitário baseado no inventário inicial
        valor_unitario = Decimal('0.00')
        try:
            logger.debug(f"Buscando inventário para categoria: '{categoria}'")
            logger.debug(f"Inventário disponível: {[f'{item.categoria.nome}: R$ {item.valor_por_cabeca}' for item in inventario_inicial]}")
            
            item_inventario = next((item for item in inventario_inicial if item.categoria.nome == categoria), None)
            if item_inventario and item_inventario.valor_por_cabeca:
                valor_unitario = item_inventario.valor_por_cabeca
                logger.debug(f"{categoria}: Valor unitário encontrado = R$ {valor_unitario}")
            else:
                logger.warning(f"{categoria}: Valor unitário não encontrado no inventário")
                if item_inventario:
                    logger.debug(f"Item encontrado mas sem valor: {item_inventario.valor_por_cabeca}")
                else:
                    logger.debug(f"Nenhum item encontrado para esta categoria")
                
                # Usar valor padrão se não encontrar no inventário
                try:
                    categoria_obj = CategoriaAnimal.objects.get(nome=categoria)
                    # Extrair ano da primeira movimentação se disponível
                    ano_categoria = ano
                    if not ano_categoria and movimentacoes:
                        ano_categoria = movimentacoes[0].data_movimentacao.year
                    valor_unitario = obter_valor_padrao_por_categoria(categoria_obj, propriedade, ano_categoria)
                    logger.debug(f"{categoria}: Usando valor padrão = R$ {valor_unitario}")
                except CategoriaAnimal.DoesNotExist:
                    valor_unitario = Decimal('2000.00')  # Valor padrão genérico
                    logger.debug(f"{categoria}: Usando valor genérico = R$ {valor_unitario}")
        except Exception as e:
            logger.error(f"ERRO {categoria}: Erro ao buscar valor unitário: {e}", exc_info=True)
            valor_unitario = Decimal('0.00')
        
        # Calcular valor total
        valor_total = valor_unitario * Decimal(str(saldo_final))
        
        resultado[categoria] = {
            'saldo_inicial': saldo_inicial,
            'nascimentos': nascimentos_display,
            'compras': movs['compras'],
            'vendas': movs['vendas'],
            'transferencias_entrada': movs['transferencias_entrada'],
            'transferencias_saida': movs['transferencias_saida'],
            'mortes': movs['mortes'],
            'evolucao_categoria': evolucao_categoria,
            'saldo_final': saldo_final,
            'peso_medio_kg': peso_medio_kg,
            'valor_unitario': valor_unitario,
            'valor_total': valor_total
        }
    
    logger.debug(f"Evolução detalhada processada para {len(resultado)} categorias")
    return resultado


def obter_parametros_padrao_ciclo(tipo_ciclo):
    """Retorna parâmetros padrão baseados no tipo de ciclo pecuário"""
    parametros_padrao = {
        'CRIA': {
            'taxa_natalidade_anual': 85.0,
            'taxa_mortalidade_bezerros_anual': 5.0,
            'taxa_mortalidade_adultos_anual': 2.0,
            'percentual_venda_machos_anual': 0.0,  # Não vende machos na cria
            'percentual_venda_femeas_anual': 0.0,  # Não vende fêmeas na cria
            'descricao': 'Foco na reprodução e criação de bezerros'
        },
        'RECRIA': {
            'taxa_natalidade_anual': 0.0,  # Não há reprodução na recria
            'taxa_mortalidade_bezerros_anual': 3.0,
            'taxa_mortalidade_adultos_anual': 1.5,
            'percentual_venda_machos_anual': 0.0,  # Não vende na recria
            'percentual_venda_femeas_anual': 0.0,  # Não vende na recria
            'descricao': 'Foco no desenvolvimento de animais jovens'
        },
        'ENGORDA': {
            'taxa_natalidade_anual': 0.0,  # Não há reprodução na engorda
            'taxa_mortalidade_bezerros_anual': 2.0,
            'taxa_mortalidade_adultos_anual': 1.0,
            'percentual_venda_machos_anual': 100.0,  # Vende todos os machos
            'percentual_venda_femeas_anual': 100.0,  # Vende todas as fêmeas
            'descricao': 'Foco na terminação e venda de animais'
        },
        'CICLO_COMPLETO': {
            'taxa_natalidade_anual': 85.0,
            'taxa_mortalidade_bezerros_anual': 5.0,
            'taxa_mortalidade_adultos_anual': 2.0,
            'percentual_venda_machos_anual': 80.0,  # Vende a maioria dos machos
            'percentual_venda_femeas_anual': 10.0,  # Vende algumas fêmeas
            'descricao': 'Sistema completo: cria, recria e engorda'
        }
    }
    
    return parametros_padrao.get(tipo_ciclo, parametros_padrao['CICLO_COMPLETO'])


def aplicar_parametros_ciclo(propriedade, parametros):
    """Aplica parâmetros específicos baseados no tipo de ciclo da propriedade"""
    ciclos_pecuarios = []
    if hasattr(propriedade, 'ciclos_pecuarios_list'):
        ciclos_pecuarios = propriedade.ciclos_pecuarios_list()
    elif propriedade.tipo_ciclo_pecuario:
        valor = propriedade.tipo_ciclo_pecuario
        if isinstance(valor, str):
            ciclos_pecuarios = [item.strip() for item in valor.split(',') if item.strip()]
        else:
            ciclos_pecuarios = list(valor)

    if ciclos_pecuarios:
        parametros_ciclo = obter_parametros_padrao_ciclo(ciclos_pecuarios[0])
        
        # Atualizar parâmetros se não foram definidos pelo usuário
        if not parametros.taxa_natalidade_anual:
            parametros.taxa_natalidade_anual = parametros_ciclo['taxa_natalidade_anual']
        if not parametros.taxa_mortalidade_bezerros_anual:
            parametros.taxa_mortalidade_bezerros_anual = parametros_ciclo['taxa_mortalidade_bezerros_anual']
        if not parametros.taxa_mortalidade_adultos_anual:
            parametros.taxa_mortalidade_adultos_anual = parametros_ciclo['taxa_mortalidade_adultos_anual']
        if not parametros.percentual_venda_machos_anual:
            parametros.percentual_venda_machos_anual = parametros_ciclo['percentual_venda_machos_anual']
        if not parametros.percentual_venda_femeas_anual:
            parametros.percentual_venda_femeas_anual = parametros_ciclo['percentual_venda_femeas_anual']
        
        parametros.save()
    
    return parametros


# Views para Transferências entre Propriedades
@login_required
def transferencias_lista(request):
    """Lista todas as transferências do usuário"""
    transferencias = TransferenciaPropriedade.objects.filter(
        Q(propriedade_origem__produtor__usuario_responsavel=request.user) |
        Q(propriedade_destino__produtor__usuario_responsavel=request.user)
    ).order_by('-data_transferencia')
    
    context = {
        'transferencias': transferencias,
    }
    return render(request, 'gestao_rural/transferencias_lista.html', context)


@login_required
def transferencia_nova(request):
    """Criar nova transferência entre propriedades"""
    if request.method == 'POST':
        form = TransferenciaPropriedadeForm(request.POST, user=request.user)
        if form.is_valid():
            transferencia = form.save()
            messages.success(request, 'Transferência cadastrada com sucesso!')
            return redirect('transferencias_lista')
    else:
        form = TransferenciaPropriedadeForm(user=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'gestao_rural/transferencia_nova.html', context)


@login_required
def transferencia_editar(request, transferencia_id):
    """Editar transferência existente"""
    transferencia = get_object_or_404(
        TransferenciaPropriedade.objects.filter(
            Q(propriedade_origem__produtor__usuario_responsavel=request.user) |
            Q(propriedade_destino__produtor__usuario_responsavel=request.user)
        ),
        id=transferencia_id
    )
    
    if request.method == 'POST':
        form = TransferenciaPropriedadeForm(request.POST, instance=transferencia, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transferência atualizada com sucesso!')
            return redirect('transferencias_lista')
    else:
        form = TransferenciaPropriedadeForm(instance=transferencia, user=request.user)
    
    context = {
        'form': form,
        'transferencia': transferencia,
    }
    return render(request, 'gestao_rural/transferencia_editar.html', context)


@login_required
def transferencia_excluir(request, transferencia_id):
    """Excluir transferência"""
    transferencia = get_object_or_404(
        TransferenciaPropriedade.objects.filter(
            Q(propriedade_origem__produtor__usuario_responsavel=request.user) |
            Q(propriedade_destino__produtor__usuario_responsavel=request.user)
        ),
        id=transferencia_id
    )
    
    if request.method == 'POST':
        transferencia.delete()
        messages.success(request, 'Transferência excluída com sucesso!')
        return redirect('transferencias_lista')
    
    context = {
        'transferencia': transferencia,
    }
    return render(request, 'gestao_rural/transferencia_excluir.html', context)


def gerar_resumo_projecao_por_ano(movimentacoes, inventario_inicial, propriedade=None):
    """Gera resumo da projeção organizado por ano no mesmo formato da Evolução Detalhada"""
    from collections import defaultdict
    from datetime import datetime
    from .models import CategoriaAnimal
    
    logger.info(f"=== INICIANDO gerar_resumo_projecao_por_ano ===")
    logger.info(f"Total de movimentações recebidas: {len(movimentacoes)}")
    logger.info(f"Total de itens no inventário inicial: {len(inventario_inicial)}")
    
    # Buscar todas as categorias ativas
    todas_categorias = CategoriaAnimal.objects.filter(ativo=True).order_by('sexo', 'idade_minima_meses')
    nomes_categorias = [cat.nome for cat in todas_categorias]
    logger.info(f"Total de categorias ativas: {len(nomes_categorias)}")
    
    # Agrupar movimentações por ano
    movimentacoes_por_ano = defaultdict(list)
    for mov in movimentacoes:
        ano = mov.data_movimentacao.year
        movimentacoes_por_ano[ano].append(mov)
    
    logger.info(f"Movimentações agrupadas por {len(movimentacoes_por_ano)} anos: {list(movimentacoes_por_ano.keys())}")
    
    # Inicializar com inventário inicial
    categorias_inicial = {}
    for item in inventario_inicial:
        categorias_inicial[item.categoria.nome] = item.quantidade
    
    # Gerar resumo detalhado para cada ano
    resumo_por_ano = {}
    saldos_finais_ano_anterior = {}  # Armazenar saldos finais do ano anterior
    
    for ano in sorted(movimentacoes_por_ano.keys()):
        movimentacoes_ano = movimentacoes_por_ano[ano]
        logger.info(f"Processando ano {ano} com {len(movimentacoes_ano)} movimentações")
        
        # Agrupar movimentações por categoria para o ano
        movimentacoes_por_categoria = defaultdict(lambda: {
            'nascimentos': 0,
            'compras': 0,
            'vendas': 0,
            'transferencias_entrada': 0,
            'transferencias_saida': 0,
            'promocao_entrada': 0,
            'promocao_saida': 0,
            'mortes': 0,
            'evolucao_categoria': None
        })
        
        for mov in movimentacoes_ano:
            categoria = mov.categoria.nome
            
            if mov.tipo_movimentacao == 'NASCIMENTO':
                movimentacoes_por_categoria[categoria]['nascimentos'] += mov.quantidade
            elif mov.tipo_movimentacao == 'COMPRA':
                movimentacoes_por_categoria[categoria]['compras'] += mov.quantidade
            elif mov.tipo_movimentacao == 'VENDA':
                movimentacoes_por_categoria[categoria]['vendas'] += mov.quantidade
            elif mov.tipo_movimentacao == 'PROMOCAO_ENTRADA' or (mov.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA' and 'Promoção' in (mov.observacao or '')):
                movimentacoes_por_categoria[categoria]['promocao_entrada'] += mov.quantidade
            elif mov.tipo_movimentacao == 'PROMOCAO_SAIDA' or (mov.tipo_movimentacao == 'TRANSFERENCIA_SAIDA' and 'Promoção' in (mov.observacao or '')):
                movimentacoes_por_categoria[categoria]['promocao_saida'] += mov.quantidade
            elif mov.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA':
                movimentacoes_por_categoria[categoria]['transferencias_entrada'] += mov.quantidade
            elif mov.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
                movimentacoes_por_categoria[categoria]['transferencias_saida'] += mov.quantidade
            elif mov.tipo_movimentacao == 'MORTE':
                movimentacoes_por_categoria[categoria]['mortes'] += mov.quantidade
            else:
                # Log de movimentações não reconhecidas para debug
                logger.warning(f"Tipo de movimentação não reconhecido: {mov.tipo_movimentacao} para categoria {categoria}")
        
        # Calcular resultado para cada categoria do ano
        resultado_ano = {}
        
        # Processar todas as categorias ativas, não apenas as que têm movimentações
        for categoria_nome in nomes_categorias:
            # Obter movimentações para esta categoria (pode estar vazio)
            movs = movimentacoes_por_categoria.get(categoria_nome, {
                'nascimentos': 0,
                'compras': 0,
                'vendas': 0,
                'transferencias_entrada': 0,
                'transferencias_saida': 0,
                'promocao_entrada': 0,
                'promocao_saida': 0,
                'mortes': 0,
                'evolucao_categoria': None
            })
            # Para o primeiro ano, usar inventário inicial
            # Para anos seguintes, usar saldo final do ano anterior
            if ano == min(movimentacoes_por_ano.keys()):
                saldo_inicial = categorias_inicial.get(categoria_nome, 0)
            else:
                saldo_inicial = saldos_finais_ano_anterior.get(categoria_nome, 0)
            
            # Calcular saldo final
            saldo_final = (saldo_inicial + 
                          movs['nascimentos'] + 
                          movs['compras'] + 
                          movs['transferencias_entrada'] + 
                          movs['promocao_entrada'] - 
                          movs['vendas'] - 
                          movs['transferencias_saida'] - 
                          movs['promocao_saida'] - 
                          movs['mortes'])
            
            # Calcular evolução de categoria
            evolucao_categoria = None
            if movs['promocao_entrada'] > 0 or movs['promocao_saida'] > 0:
                saldo_promocao = movs['promocao_entrada'] - movs['promocao_saida']
                if saldo_promocao > 0:
                    evolucao_categoria = f"+{saldo_promocao}"
                elif saldo_promocao < 0:
                    evolucao_categoria = f"{saldo_promocao}"
                else:
                    evolucao_categoria = "0"
            else:
                evolucao_categoria = "-"
            
            # Mostrar nascimentos apenas para categorias de 0-12 meses
            nascimentos_display = movs['nascimentos'] if any(termo in categoria_nome.lower() for termo in ['bezerro', 'bezerra', '0-12']) else 0
            
            # Obter peso médio da categoria
            try:
                categoria_obj = CategoriaAnimal.objects.get(nome=categoria_nome)
                peso_medio_kg = categoria_obj.peso_medio_kg or Decimal('0.00')
            except CategoriaAnimal.DoesNotExist:
                peso_medio_kg = Decimal('0.00')
            
            # Calcular valor unitário baseado no inventário inicial
            valor_unitario = Decimal('0.00')
            try:
                item_inventario = next((item for item in inventario_inicial if item.categoria.nome == categoria_nome), None)
                if item_inventario and item_inventario.valor_por_cabeca:
                    valor_unitario = item_inventario.valor_por_cabeca
                else:
                    # Usar valor padrão se não encontrar no inventário
                    try:
                        categoria_obj = CategoriaAnimal.objects.get(nome=categoria_nome)
                        valor_unitario = obter_valor_padrao_por_categoria(categoria_obj, propriedade, ano)
                    except CategoriaAnimal.DoesNotExist:
                        valor_unitario = Decimal('2000.00')  # Valor padrão genérico
            except (AttributeError, TypeError, ValueError, KeyError) as e:
                logging.warning(f"Erro ao calcular valor unitário para categoria {categoria_nome}: {e}")
                valor_unitario = Decimal('2000.00')  # Valor padrão genérico em caso de erro
            
            # Calcular valor total
            valor_total = valor_unitario * Decimal(str(saldo_final))
            
            # Verificar se a categoria tem dados relevantes antes de incluir
            tem_dados_relevantes = (
                saldo_inicial > 0 or 
                saldo_final > 0 or 
                movs['nascimentos'] > 0 or 
                movs['compras'] > 0 or 
                movs['vendas'] > 0 or 
                movs['mortes'] > 0 or 
                movs['transferencias_entrada'] > 0 or 
                movs['transferencias_saida'] > 0 or 
                movs['promocao_entrada'] > 0 or 
                movs['promocao_saida'] > 0
            )
            
            # Só incluir categoria se tiver dados relevantes
            if tem_dados_relevantes:
                resultado_ano[categoria_nome] = {
                    'saldo_inicial': saldo_inicial,
                    'nascimentos': nascimentos_display,
                    'compras': movs['compras'],
                    'vendas': movs['vendas'],
                    'transferencias_entrada': movs['transferencias_entrada'],
                    'transferencias_saida': movs['transferencias_saida'],
                    'mortes': movs['mortes'],
                    'evolucao_categoria': evolucao_categoria,
                    'saldo_final': saldo_final,
                    'peso_medio_kg': peso_medio_kg,
                    'valor_unitario': valor_unitario,
                    'valor_total': valor_total
                }
            
            # Armazenar saldo final para usar como saldo inicial do próximo ano (sempre, mesmo sem dados)
            saldos_finais_ano_anterior[categoria_nome] = saldo_final
        
        # Calcular totais do ano
        totais_ano = {
            'saldo_inicial_total': 0,
            'nascimentos_total': 0,
            'compras_total': 0,
            'vendas_total': 0,
            'transferencias_entrada_total': 0,
            'transferencias_saida_total': 0,
            'mortes_total': 0,
            'saldo_final_total': 0,
            'valor_total_geral': Decimal('0.00'),
            'receitas_total': Decimal('0.00'),
            'custos_total': Decimal('0.00'),
            'custos_compras': Decimal('0.00'),
            'perdas_mortes': Decimal('0.00'),  # Perdas por mortes (não são custos)
            'total_femeas': 0,
            'total_machos': 0,
        }
        
        for categoria_nome, dados in resultado_ano.items():
            totais_ano['saldo_inicial_total'] += dados['saldo_inicial']
            totais_ano['nascimentos_total'] += dados['nascimentos']
            totais_ano['compras_total'] += dados['compras']
            totais_ano['vendas_total'] += dados['vendas']
            totais_ano['transferencias_entrada_total'] += dados['transferencias_entrada']
            totais_ano['transferencias_saida_total'] += dados['transferencias_saida']
            totais_ano['mortes_total'] += dados['mortes']
            totais_ano['saldo_final_total'] += dados['saldo_final']
            totais_ano['valor_total_geral'] += dados['valor_total']
            
            # Contar fêmeas e machos
            nome_lower = categoria_nome.lower()
            if any(termo in nome_lower for termo in ['fêmea', 'femea', 'bezerra', 'novilha', 'primípara', 'multípara', 'vaca']):
                totais_ano['total_femeas'] += dados['saldo_final']
            elif any(termo in nome_lower for termo in ['macho', 'bezerro', 'garrote', 'boi', 'touro']):
                totais_ano['total_machos'] += dados['saldo_final']
        
        # Calcular receitas e custos do ano baseado nas movimentações
        for mov in movimentacoes_ano:
            # Calcular valor_total manualmente
            quantidade = mov.quantidade if mov.quantidade else 0
            
            # PRIORIDADE 1: Usar valor_por_cabeca já salvo na movimentação (se existir)
            # PRIORIDADE 2: Usar valor_total já salvo na movimentação (se existir)
            # PRIORIDADE 3: Buscar valor_por_cabeca do inventário
            # PRIORIDADE 4: Usar valor padrão da categoria
            
            valor_mov = Decimal('0')
            
            if mov.valor_total:
                # Se já tem valor_total calculado, usar diretamente
                valor_mov = Decimal(str(mov.valor_total))
            elif mov.valor_por_cabeca and quantidade > 0:
                # Se tem valor_por_cabeca, calcular
                valor_mov = Decimal(str(mov.valor_por_cabeca)) * Decimal(str(quantidade))
            else:
                # Buscar do inventário ou usar valor padrão
                try:
                    inventario_item = InventarioRebanho.objects.filter(
                        propriedade=mov.propriedade,
                        categoria=mov.categoria
                    ).first()
                    
                    if inventario_item and inventario_item.valor_por_cabeca:
                        valor_unitario = inventario_item.valor_por_cabeca
                    else:
                        # Usar valor padrão da categoria com CEPEA se disponível
                        try:
                            ano_mov = mov.data_movimentacao.year if mov.data_movimentacao else None
                            valor_unitario = obter_valor_padrao_por_categoria(mov.categoria, mov.propriedade, ano_mov)
                        except Exception as e:
                            logger.warning(f"Erro ao obter valor padrão para categoria {mov.categoria.nome}: {e}")
                            valor_unitario = Decimal('2000.00')  # Valor padrão genérico
                    
                    valor_mov = Decimal(str(quantidade)) * Decimal(str(valor_unitario))
                except Exception as e:
                    logger.warning(f"Erro ao calcular valor para movimentação {mov.id} ({mov.categoria.nome}): {e}")
                    valor_mov = Decimal('0')
            
            if mov.tipo_movimentacao == 'VENDA':
                totais_ano['receitas_total'] += valor_mov
                logger.debug(f"Venda: {mov.categoria.nome} - {quantidade} cabeças - R$ {valor_mov:.2f}")
            elif mov.tipo_movimentacao == 'COMPRA':
                totais_ano['custos_total'] += valor_mov
                totais_ano['custos_compras'] += valor_mov
                logger.debug(f"Compra: {mov.categoria.nome} - {quantidade} cabeças - R$ {valor_mov:.2f}")
            # MORTE não é custo, é perda - não incluir nos custos
        
        logger.info(f"Ano {ano} - Receitas: R$ {totais_ano['receitas_total']:.2f}, Custos: R$ {totais_ano['custos_total']:.2f}, Lucro: R$ {totais_ano['receitas_total'] - totais_ano['custos_total']:.2f}")
        
        # Remover 'TOTAIS' do resultado_ano se existir
        resultado_ano_sem_totais = {k: v for k, v in resultado_ano.items() if k != 'TOTAIS'}
        
        # Ordenar categorias: primeiro fêmeas (por idade), depois machos (por idade)
        categorias_ordenadas = {}
        categorias_para_ordenar = []
        
        for categoria_nome, dados_cat in resultado_ano_sem_totais.items():
            try:
                categoria_obj = CategoriaAnimal.objects.get(nome=categoria_nome)
                # Determinar ordem de sexo: Fêmeas primeiro (1), Machos segundo (2), Indefinidos terceiro (3)
                if categoria_obj.sexo == 'F':
                    ordem_sexo = 1  # Fêmeas primeiro
                elif categoria_obj.sexo == 'M':
                    ordem_sexo = 2  # Machos segundo
                else:
                    ordem_sexo = 3  # Indefinidos
                
                # Idade mínima para ordenação (usar 999 se None para colocar no final)
                idade_minima = categoria_obj.idade_minima_meses if categoria_obj.idade_minima_meses is not None else 999
                idade_maxima = categoria_obj.idade_maxima_meses if categoria_obj.idade_maxima_meses is not None else 999
            except CategoriaAnimal.DoesNotExist:
                # Fallback: tentar determinar pelo nome
                if 'fêmea' in categoria_nome.lower() or 'femea' in categoria_nome.lower() or categoria_nome.endswith(' F'):
                    ordem_sexo = 1  # Fêmeas primeiro
                elif 'macho' in categoria_nome.lower() or categoria_nome.endswith(' M') or 'bezerro(o)' in categoria_nome.lower() or 'garrote' in categoria_nome.lower() or 'boi' in categoria_nome.lower() or 'touro' in categoria_nome.lower():
                    ordem_sexo = 2  # Machos segundo
                else:
                    ordem_sexo = 3  # Indefinidos
                idade_minima = 999
                idade_maxima = 999
            
            categorias_para_ordenar.append((ordem_sexo, idade_minima, idade_maxima, categoria_nome, dados_cat))
        
        # Ordenar: primeiro por sexo, depois por idade mínima, depois por idade máxima, depois por nome
        categorias_para_ordenar.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
        
        # Criar dicionário ordenado (Python 3.7+ mantém ordem de inserção)
        for ordem_sexo, idade_minima, idade_maxima, categoria_nome, dados_cat in categorias_para_ordenar:
            categorias_ordenadas[categoria_nome] = dados_cat
        
        logger.info(f"Ano {ano}: {len(categorias_ordenadas)} categorias processadas, Saldo Final Total: {totais_ano['saldo_final_total']}")
        
        # Calcular saldo final do ano anterior para exibição
        saldo_final_ano_anterior = None
        if ano > min(movimentacoes_por_ano.keys()):
            ano_anterior = ano - 1
            if ano_anterior in resumo_por_ano and 'totais' in resumo_por_ano[ano_anterior]:
                saldo_final_ano_anterior = resumo_por_ano[ano_anterior]['totais']['saldo_final_total']
        
        # Estruturar dados no formato esperado pelo template
        resumo_por_ano[ano] = {
            'categorias': categorias_ordenadas,
            'totais': {
                'saldo_inicial_total': totais_ano['saldo_inicial_total'],
                'nascimentos_total': totais_ano['nascimentos_total'],
                'compras_total': totais_ano['compras_total'],
                'vendas_total': totais_ano['vendas_total'],
                'transferencias_entrada_total': totais_ano['transferencias_entrada_total'],
                'transferencias_saida_total': totais_ano['transferencias_saida_total'],
                'mortes_total': totais_ano['mortes_total'],
                'saldo_final_total': totais_ano['saldo_final_total'],
                'valor_total_geral': totais_ano['valor_total_geral'],
                'receitas_total': totais_ano['receitas_total'],
                'custos_total': totais_ano['custos_total'],
                'custos_compras': totais_ano.get('custos_compras', Decimal('0.00')),
                'perdas_mortes': totais_ano.get('perdas_mortes', Decimal('0.00')),
                'lucro_total': totais_ano['receitas_total'] - totais_ano['custos_total'],
                'total_femeas': totais_ano['total_femeas'],
                'total_machos': totais_ano['total_machos'],
                'total_animais': totais_ano['saldo_final_total'],
            },
            'saldo_final_ano_anterior': saldo_final_ano_anterior,
            'ano_anterior': ano - 1 if ano > min(movimentacoes_por_ano.keys()) else None
        }
    
    logger.info(f"Resumo por ano processado para {len(resumo_por_ano)} anos")
    if resumo_por_ano:
        primeiro_ano = list(resumo_por_ano.keys())[0]
        logger.info(f"Primeiro ano: {primeiro_ano}, tem categorias: {'categorias' in resumo_por_ano[primeiro_ano]}, tem totais: {'totais' in resumo_por_ano[primeiro_ano]}")
        if 'categorias' in resumo_por_ano[primeiro_ano]:
            logger.info(f"Número de categorias no primeiro ano: {len(resumo_por_ano[primeiro_ano]['categorias'])}")
    return resumo_por_ano


# ==================== GESTÃO DE CATEGORIAS ====================

@login_required
def categorias_lista(request):
    """Lista todas as categorias de animais"""
    # Ordenar: primeiro fêmeas (F), depois machos (M), depois indefinidos (I)
    # Dentro de cada grupo de sexo, ordenar por idade mínima (0-12, 12-24, 24-36, 36+)
    categorias = CategoriaAnimal.objects.filter(ativo=True).annotate(
        ordem_sexo=Case(
            When(sexo='F', then=1),  # Fêmeas primeiro
            When(sexo='M', then=2),  # Machos segundo
            When(sexo='I', then=3),  # Indefinidos terceiro
            default=4,
            output_field=IntegerField(),
        )
    ).order_by(
        'ordem_sexo',  # Ordem personalizada do sexo
        'idade_minima_meses',  # Por idade mínima dentro de cada sexo (None vai para o final)
        'nome'  # Por nome como último critério
    )
    return render(request, 'gestao_rural/categorias_lista.html', {'categorias': categorias})


@login_required
@bloquear_demo_cadastro
def categoria_nova(request):
    """Cria uma nova categoria de animal"""
    if request.method == 'POST':
        form = CategoriaAnimalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('categorias_lista')
    else:
        form = CategoriaAnimalForm()
    
    return render(request, 'gestao_rural/categoria_nova.html', {'form': form})


@login_required
@bloquear_demo_cadastro
def categoria_editar(request, categoria_id):
    """Edita uma categoria existente"""
    categoria = get_object_or_404(CategoriaAnimal, id=categoria_id)
    
    if request.method == 'POST':
        form = CategoriaAnimalForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('categorias_lista')
    else:
        form = CategoriaAnimalForm(instance=categoria)
    
    return render(request, 'gestao_rural/categoria_editar.html', {'form': form, 'categoria': categoria})


@login_required
@bloquear_demo_cadastro
def categoria_excluir(request, categoria_id):
    """Exclui uma categoria"""
    categoria = get_object_or_404(CategoriaAnimal, id=categoria_id)
    
    if request.method == 'POST':
        # Verificar todos os lugares onde a categoria pode estar sendo usada
        bloqueios = []
        
        # Verificar inventários
        inventarios_count = InventarioRebanho.objects.filter(categoria=categoria).count()
        if inventarios_count > 0:
            bloqueios.append(f'{inventarios_count} inventário(s)')
        
        # Verificar movimentações projetadas
        movimentacoes_count = MovimentacaoProjetada.objects.filter(categoria=categoria).count()
        if movimentacoes_count > 0:
            bloqueios.append(f'{movimentacoes_count} movimentação(ões) projetada(s)')
        
        # Verificar políticas de vendas
        try:
            from .models import PoliticaVendasCategoria
            politicas_count = PoliticaVendasCategoria.objects.filter(categoria=categoria).count()
            if politicas_count > 0:
                bloqueios.append(f'{politicas_count} política(s) de venda')
        except (ImportError, AttributeError) as e:
            logging.debug(f"Erro ao verificar políticas de venda: {e}")
            pass
        
        # Verificar configurações de venda
        try:
            from .models import ConfiguracaoVenda
            configuracoes_count = ConfiguracaoVenda.objects.filter(categoria_venda=categoria).count()
            if configuracoes_count > 0:
                bloqueios.append(f'{configuracoes_count} configuração(ões) de venda')
        except (ImportError, AttributeError) as e:
            logging.debug(f"Erro ao verificar configurações de venda: {e}")
            pass
        
        if bloqueios:
            mensagem = f'Não é possível excluir a categoria "{categoria.nome}" pois ela está sendo usada em: {", ".join(bloqueios)}.'
            messages.error(request, mensagem)
            return redirect('categorias_lista')
        
        # Se não há bloqueios, pode excluir
        nome_categoria = categoria.nome
        categoria.delete()
        messages.success(request, f'Categoria "{nome_categoria}" excluída com sucesso!')
        return redirect('categorias_lista')
    
    # Para GET, mostrar informações de uso
    inventarios_count = InventarioRebanho.objects.filter(categoria=categoria).count()
    movimentacoes_count = MovimentacaoProjetada.objects.filter(categoria=categoria).count()
    
    politicas_count = 0
    configuracoes_count = 0
    try:
        from .models import PoliticaVendasCategoria, ConfiguracaoVenda
        politicas_count = PoliticaVendasCategoria.objects.filter(categoria=categoria).count()
        configuracoes_count = ConfiguracaoVenda.objects.filter(categoria_venda=categoria).count()
    except (ImportError, AttributeError) as e:
        logging.debug(f"Erro ao verificar políticas e configurações: {e}")
        pass
    
    context = {
        'categoria': categoria,
        'inventarios_count': inventarios_count,
        'movimentacoes_count': movimentacoes_count,
        'politicas_count': politicas_count,
        'configuracoes_count': configuracoes_count,
        'pode_excluir': (inventarios_count + movimentacoes_count + politicas_count + configuracoes_count) == 0
    }
    
    return render(request, 'gestao_rural/categoria_excluir.html', context)


def obter_saldo_atual_propriedade(propriedade, data_referencia):
    """Obtém o saldo atual de uma propriedade em uma data específica"""
    from decimal import Decimal
    
    saldo_por_categoria = {}
    
    # Obter data do inventário mais recente
    inventario_data = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        data_inventario__lte=data_referencia
    ).order_by('-data_inventario').values_list('data_inventario', flat=True).first()
    
    if inventario_data:
        # Obter TODOS os itens do inventário mais recente
        itens_inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            data_inventario=inventario_data
        ).select_related('categoria')
        
        # Inicializar saldos com valores do inventário
        for item in itens_inventario:
            saldo_por_categoria[item.categoria] = item.quantidade
        
        # Calcular movimentações desde o inventário inicial
        movimentacoes = MovimentacaoProjetada.objects.filter(
            propriedade=propriedade,
            data_movimentacao__gt=inventario_data,
            data_movimentacao__lte=data_referencia
        ).select_related('categoria')
        
        for movimentacao in movimentacoes:
            categoria = movimentacao.categoria
            
            if categoria not in saldo_por_categoria:
                saldo_por_categoria[categoria] = 0
            
            if movimentacao.tipo_movimentacao == 'NASCIMENTO':
                saldo_por_categoria[categoria] += movimentacao.quantidade
            elif movimentacao.tipo_movimentacao == 'COMPRA':
                saldo_por_categoria[categoria] += movimentacao.quantidade
            elif movimentacao.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA':
                saldo_por_categoria[categoria] += movimentacao.quantidade
            elif movimentacao.tipo_movimentacao == 'VENDA':
                saldo_por_categoria[categoria] -= movimentacao.quantidade
            elif movimentacao.tipo_movimentacao == 'MORTE':
                saldo_por_categoria[categoria] -= movimentacao.quantidade
            elif movimentacao.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
                saldo_por_categoria[categoria] -= movimentacao.quantidade
    
    return saldo_por_categoria


def obter_valor_padrao_por_categoria(categoria, propriedade=None, ano=None):
    """
    Retorna valores padrão por categoria de animal
    Se propriedade e ano forem fornecidos, tenta buscar preço CEPEA
    
    Args:
        categoria: Objeto CategoriaAnimal
        propriedade: Objeto Propriedade (opcional)
        ano: Ano de referência (opcional, usa ano atual se não fornecido)
    
    Returns:
        Decimal com o valor unitário
    """
    from decimal import Decimal
    from datetime import date
    from gestao_rural.apis_integracao.api_cepea import CEPEAService
    
    # Se propriedade e ano fornecidos, tentar buscar CEPEA
    if propriedade and propriedade.uf:
        if not ano:
            ano = date.today().year
        
        try:
            cepea_service = CEPEAService()
            tipo_cepea = cepea_service.mapear_categoria_para_cepea(categoria.nome)
            
            if tipo_cepea:
                preco_cepea = cepea_service.obter_preco_por_categoria(
                    uf=propriedade.uf,
                    ano=ano,
                    tipo_categoria=tipo_cepea
                )
                
                if preco_cepea:
                    return preco_cepea
        except Exception as e:
            logger.warning(f"Erro ao buscar preço CEPEA para {categoria.nome}: {e}")
    
    # Valores padrão baseados no mercado brasileiro (R$ por cabeça) - fallback
    # IMPORTANTE: Bezerro desmamado é SEMPRE mais caro que bezerra (diferença de ~30-40%)
    # Valores baseados em Scot Consultoria e mercado real
    valores_padrao = {
        'bezerro': Decimal('2200.00'),     # 0-12 meses (desmamado) - MAIS CARO
        # Base: 6,5@ a R$ 390/@ = R$ 2.535 (Scot Consultoria 2024-2025)
        'bezerra': Decimal('1500.00'),     # 0-12 meses - mais barata
        # Base: ~R$ 1.075-1.200 (Scot Consultoria)
        'garrote': Decimal('2800.00'),     # 12-24 meses (8-10@ a R$ 350-380/@)
        'novilha': Decimal('3200.00'),     # 12-24 meses (8-10@ a R$ 400-420/@)
        'boi': Decimal('4200.00'),         # 24-36 meses (15-18@ a R$ 280-300/@)
        'boi_magro': Decimal('3800.00'),   # 24-36 meses (13-15@ a R$ 290/@)
        'primipara': Decimal('4500.00'),   # 24-36 meses (reprodução)
        'multipara': Decimal('5200.00'),   # >36 meses (reprodução)
        'vaca_descarte': Decimal('2800.00'), # vacas de descarte (12-14@ a R$ 230-250/@)
        'touro': Decimal('6500.00')        # reprodutores
    }
    
    nome_categoria = categoria.nome.lower()
    
    # Identificar o tipo de animal baseado no nome da categoria
    if 'bezerro' in nome_categoria and 'bezerra' not in nome_categoria:
        return valores_padrao['bezerro']
    elif 'bezerra' in nome_categoria:
        return valores_padrao['bezerra']
    elif 'garrote' in nome_categoria:
        return valores_padrao['garrote']
    elif 'novilha' in nome_categoria:
        return valores_padrao['novilha']
    elif 'boi' in nome_categoria and 'magro' in nome_categoria:
        return valores_padrao['boi_magro']
    elif 'boi' in nome_categoria:
        return valores_padrao['boi']
    elif 'primípara' in nome_categoria or 'primipara' in nome_categoria:
        return valores_padrao['primipara']
    elif 'multípara' in nome_categoria or 'multipara' in nome_categoria:
        return valores_padrao['multipara']
    elif 'descarte' in nome_categoria:
        return valores_padrao['vaca_descarte']
    elif 'touro' in nome_categoria:
        return valores_padrao['touro']
    else:
        # Valor padrão genérico
        return Decimal('2000.00')


def processar_compras_configuradas(propriedade, data_referencia, fator_inflacao=1.0):
    """Processa compras configuradas para uma propriedade com inflação"""
    from decimal import Decimal
    
    print(f"Processando compras para {propriedade.nome_propriedade} em {data_referencia} (inflação: {fator_inflacao:.2%})")
    
    # Buscar configurações de venda que geram compras
    configuracoes = ConfiguracaoVenda.objects.filter(
        propriedade=propriedade,
        tipo_reposicao='COMPRA',
        ativo=True
    )
    
    print(f"Configurações de compra encontradas: {configuracoes.count()}")
    for config in configuracoes:
        print(f"   - {config.categoria_compra.nome} (Qtd: {config.quantidade_compra})")
    
    compras_processadas = []
    
    for config in configuracoes:
        print(f"Processando compra: {config.categoria_compra.nome}")
        
        # Verificar se é o momento da compra baseado na frequência
        momento_correto = verificar_momento_compra(config, data_referencia)
        print(f"   Momento correto: {momento_correto}")
        
        if momento_correto and config.quantidade_compra > 0:
            # Calcular valor com inflação
            valor_original = config.valor_animal_compra or Decimal('0')
            
            # Se não há valor configurado, usar valor padrão com CEPEA
            if valor_original == 0:
                ano_compra = data_referencia.year if data_referencia else None
                valor_original = obter_valor_padrao_por_categoria(
                    config.categoria_compra, 
                    config.propriedade if hasattr(config, 'propriedade') else None,
                    ano_compra
                )
            
            valor_com_inflacao = valor_original * Decimal(str(fator_inflacao))
            
            # Registrar a compra com valor inflacionado
            MovimentacaoProjetada.objects.create(
                propriedade=propriedade,
                data_movimentacao=data_referencia,
                tipo_movimentacao='COMPRA',
                categoria=config.categoria_compra,
                quantidade=config.quantidade_compra,
                observacao=f'Compra configurada - {config.categoria_compra.nome} - R$ {valor_com_inflacao}/cabeça (Inflação: {fator_inflacao:.1%})'
            )
            
            compras_processadas.append({
                'categoria': config.categoria_compra,
                'quantidade': config.quantidade_compra,
                'valor_unitario': valor_com_inflacao,
                'valor_total': valor_com_inflacao * config.quantidade_compra
            })
            
            print(f"Compra aplicada: {config.categoria_compra.nome} +{config.quantidade_compra} (R$ {valor_com_inflacao:.2f} cada)")
        else:
            print(f"AVISO: Não é o momento da compra ou quantidade zero")
    
    print(f"Total de compras processadas: {len(compras_processadas)}")
    return compras_processadas


def verificar_momento_compra(config, data_referencia):
    """Verifica se é o momento correto para realizar uma compra baseado na frequência"""
    from datetime import datetime, timedelta, date
    
    print(f"Verificando momento da compra:")
    print(f"   Frequência: {config.frequencia_venda}")
    print(f"   Data referência: {data_referencia}")
    print(f"   Data criação: {config.data_criacao}")
    
    # Converter data_referencia para datetime se necessário
    if isinstance(data_referencia, str):
        data_referencia = datetime.strptime(data_referencia, '%Y-%m-%d').date()
    elif hasattr(data_referencia, 'date'):
        data_referencia = data_referencia.date()
    
    # Calcular dias baseado na frequência
    frequencia_dias = {
        'MENSAL': 30,
        'BIMESTRAL': 60,
        'TRIMESTRAL': 90,
        'SEMESTRAL': 180,
        'ANUAL': 365
    }
    
    dias_frequencia = frequencia_dias.get(config.frequencia_venda, 30)
    print(f"   Dias necessários: {dias_frequencia}")
    
    # Verificar se já passou o tempo suficiente desde a última compra
    ultima_compra = MovimentacaoProjetada.objects.filter(
        propriedade=config.propriedade,
        tipo_movimentacao='COMPRA',
        categoria=config.categoria_compra
    ).order_by('-data_movimentacao').first()
    
    if ultima_compra:
        dias_desde_ultima = (data_referencia - ultima_compra.data_movimentacao).days
        print(f"   Última compra: {ultima_compra.data_movimentacao}")
        print(f"   Dias desde última: {dias_desde_ultima}")
        resultado = dias_desde_ultima >= dias_frequencia
    else:
        # Primeira compra - verificar se passou o tempo mínimo
        dias_desde_inicio = (data_referencia - config.data_criacao.date()).days
        print(f"   Primeira compra - dias desde criação: {dias_desde_inicio}")
        resultado = dias_desde_inicio >= dias_frequencia
    
    print(f"   Resultado: {resultado}")
    return resultado


def processar_transferencias_configuradas(propriedade_destino, data_referencia):
    """Processa transferências configuradas para uma propriedade de destino"""
    from decimal import Decimal
    
    print(f"Processando transferências para {propriedade_destino.nome_propriedade} em {data_referencia}")
    
    # Buscar configurações de venda que geram transferências
    configuracoes = ConfiguracaoVenda.objects.filter(
        propriedade=propriedade_destino,
        tipo_reposicao='TRANSFERENCIA',
        ativo=True
    )
    
    print(f"Configurações encontradas: {configuracoes.count()}")
    for config in configuracoes:
        print(f"   - {config.categoria_venda.nome} de {config.fazenda_origem.nome_propriedade} (Qtd: {config.quantidade_transferencia})")
    
    transferencias_processadas = []
    
    for config in configuracoes:
        print(f"Verificando configuração: {config.categoria_venda.nome}")
        
        # Verificar se é o momento da transferência baseado na frequência
        momento_correto = verificar_momento_transferencia(config, data_referencia)
        print(f"   Momento correto: {momento_correto}")
        
        if momento_correto:
            # Obter saldo da propriedade de origem
            saldo_origem = obter_saldo_atual_propriedade(config.fazenda_origem, data_referencia)
            print(f"   Saldo origem: {saldo_origem}")
            
            # Verificar se há saldo suficiente na categoria de origem
            categoria_origem = config.categoria_venda
            saldo_disponivel = saldo_origem.get(categoria_origem, 0)
            print(f"   Saldo disponível: {saldo_disponivel}, Quantidade necessária: {config.quantidade_transferencia}")
            
            if saldo_disponivel >= config.quantidade_transferencia:
                # Criar transferência de saída na origem
                movimentacao_saida = MovimentacaoProjetada.objects.create(
                    propriedade=config.fazenda_origem,
                    data_movimentacao=data_referencia,
                    tipo_movimentacao='TRANSFERENCIA_SAIDA',
                    categoria=categoria_origem,
                    quantidade=config.quantidade_transferencia,
                    observacao=f'Transferência para {propriedade_destino.nome_propriedade}'
                )
                
                # Criar transferência de entrada no destino
                movimentacao_entrada = MovimentacaoProjetada.objects.create(
                    propriedade=propriedade_destino,
                    data_movimentacao=data_referencia,
                    tipo_movimentacao='TRANSFERENCIA_ENTRADA',
                    categoria=categoria_origem,
                    quantidade=config.quantidade_transferencia,
                    observacao=f'Transferência de {config.fazenda_origem.nome_propriedade}'
                )
                
                transferencias_processadas.append({
                    'origem': config.fazenda_origem,
                    'destino': propriedade_destino,
                    'categoria': categoria_origem,
                    'quantidade': config.quantidade_transferencia,
                    'data': data_referencia,
                    'tipo': 'TRANSFERENCIA'
                })
                
                print(f"[OK] Transferencia processada: {config.fazenda_origem.nome_propriedade} -> {propriedade_destino.nome_propriedade}")
                print(f"   Categoria: {categoria_origem.nome}")
                print(f"   Quantidade: {config.quantidade_transferencia}")
                print(f"   Data: {data_referencia}")
            else:
                # Saldo insuficiente: criar compra automática
                print(f"[AVISO] Saldo insuficiente para transferencia: {saldo_disponivel} < {config.quantidade_transferencia}")
                print(f"[INFO] Gerando COMPRA automatica para {propriedade_destino.nome_propriedade}")

                # Criar compra automática
                movimentacao_compra = MovimentacaoProjetada.objects.create(
                    propriedade=propriedade_destino,
                    data_movimentacao=data_referencia,
                    tipo_movimentacao='COMPRA',
                    categoria=categoria_origem,
                    quantidade=config.quantidade_transferencia,
                    valor_unitario=Decimal('0.00'),  # Valor será calculado depois
                    valor_total=Decimal('0.00')
                )
                print(f"[OK] Compra automática criada: {movimentacao_compra}")
                transferencias_processadas.append(movimentacao_compra)
    
    return transferencias_processadas


@login_required
def area_assinante(request):
    """
    Página especial para usuários assinantes que ainda aguardam liberação.
    Mostra informações sobre a assinatura e data de ativação.
    """
    from .helpers_acesso import is_usuario_assinante

    # Verificar se é assinante
    if not is_usuario_assinante(request.user):
        messages.warning(request, 'Esta página é exclusiva para assinantes.')
        return redirect('dashboard')

    # Obter dados da assinatura
    try:
        from .models import AssinaturaCliente
        assinatura = AssinaturaCliente.objects.filter(
            usuario=request.user,
            status='ATIVA'
        ).first()

        context = {
            'assinatura': assinatura,
            'data_liberacao': getattr(assinatura, 'data_liberacao', None) if assinatura else None,
        }
    except Exception:
        context = {
            'assinatura': None,
            'data_liberacao': None,
        }

    return render(request, 'gestao_rural/area_assinante.html', context)


@login_required
def area_assinante(request):
    """
    Página especial para usuários assinantes que ainda aguardam liberação.
    Mostra informações sobre a assinatura e data de ativação.
    """
    from .helpers_acesso import is_usuario_assinante

    # Verificar se é assinante
    if not is_usuario_assinante(request.user):
        messages.warning(request, 'Esta página é exclusiva para assinantes.')
        return redirect('dashboard')

    # Obter dados da assinatura
    try:
        from .models import AssinaturaCliente
        assinatura = AssinaturaCliente.objects.filter(
            usuario=request.user,
            status='ATIVA'
        ).first()

        context = {
            'assinatura': assinatura,
            'data_liberacao': getattr(assinatura, 'data_liberacao', None) if assinatura else None,
        }
    except Exception:
        context = {
            'assinatura': None,
            'data_liberacao': None,
        }

    return render(request, 'gestao_rural/area_assinante.html', context)


def verificar_momento_transferencia(config, data_referencia):
    """Verifica se é o momento de processar uma transferência baseado na frequência"""
    from datetime import datetime, timedelta, date
    
    print(f"Verificando momento da transferência:")
    print(f"   Frequência: {config.frequencia_venda}")
    print(f"   Data referência: {data_referencia}")
    print(f"   Data criação: {config.data_criacao}")
    
    # Converter data_referencia para datetime se necessário
    if isinstance(data_referencia, str):
        data_referencia = datetime.strptime(data_referencia, '%Y-%m-%d').date()
    elif hasattr(data_referencia, 'date'):
        data_referencia = data_referencia.date()
    
    # Calcular dias baseado na frequência
    frequencia_dias = {
        'MENSAL': 30,
        'BIMESTRAL': 60,
        'TRIMESTRAL': 90,
        'SEMESTRAL': 180,
        'ANUAL': 365
    }
    
    dias_frequencia = frequencia_dias.get(config.frequencia_venda, 30)
    print(f"   Dias necessários: {dias_frequencia}")
    
    # Verificar se já passou o tempo suficiente desde a última transferência
    ultima_transferencia = MovimentacaoProjetada.objects.filter(
        propriedade=config.propriedade,
        tipo_movimentacao='TRANSFERENCIA_ENTRADA',
        categoria=config.categoria_venda
    ).order_by('-data_movimentacao').first()
    
    if ultima_transferencia:
        dias_desde_ultima = (data_referencia - ultima_transferencia.data_movimentacao).days
        print(f"   Última transferência: {ultima_transferencia.data_movimentacao}")
        print(f"   Dias desde última: {dias_desde_ultima}")
        resultado = dias_desde_ultima >= dias_frequencia
    else:
        # Primeira transferência - verificar se passou o tempo mínimo
        dias_desde_inicio = (data_referencia - config.data_criacao.date()).days
        print(f"   Primeira transferência - dias desde criação: {dias_desde_inicio}")
        resultado = dias_desde_inicio >= dias_frequencia
    
    print(f"   Resultado: {resultado}")
    return resultado


@login_required
def testar_transferencias(request, propriedade_id):
    """View para testar o sistema de transferências"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Buscar configurações de transferência
    configuracoes = ConfiguracaoVenda.objects.filter(
        propriedade=propriedade,
        tipo_reposicao='TRANSFERENCIA',
        ativo=True
    )
    
    # Simular data atual
    from datetime import date
    data_atual = date.today()
    
    # Processar transferências
    transferencias_processadas = processar_transferencias_configuradas(propriedade, data_atual)
    
    context = {
        'propriedade': propriedade,
        'configuracoes': configuracoes,
        'transferencias_processadas': transferencias_processadas,
        'data_teste': data_atual,
    }
    
    return render(request, 'gestao_rural/testar_transferencias.html', context)


@login_required
def obter_saldo_fazenda_ajax(request, fazenda_id, categoria_id):
    """AJAX endpoint para obter saldo atual de uma fazenda"""
    from datetime import date
    import json
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Buscar fazenda
        fazenda = get_object_or_404(Propriedade, id=fazenda_id)
        
        # Verificar permissões - usuário deve ter acesso à fazenda
        # Permitir se o usuário for responsável pelo produtor da fazenda ou se a fazenda pertencer ao mesmo produtor
        usuario_tem_acesso = False
        
        if fazenda.produtor:
            # Verificar se o usuário é o responsável pelo produtor desta fazenda
            if fazenda.produtor.usuario_responsavel == request.user:
                usuario_tem_acesso = True
            else:
                # Verificar se o usuário é um produtor que possui esta fazenda
                try:
                    usuario_produtor = request.user.produtorrural_set.first()
                    if usuario_produtor and fazenda.produtor.id == usuario_produtor.id:
                        usuario_tem_acesso = True
                except (AttributeError, TypeError) as e:
                    logging.debug(f"Erro ao verificar acesso do usuário: {e}")
                    pass
        
        if not usuario_tem_acesso:
            # Se não encontrou acesso direto, permitir se for superuser ou se a fazenda for do mesmo produtor
            # que a propriedade atual (para transferências entre fazendas do mesmo produtor)
            try:
                usuario_produtor = request.user.produtorrural_set.first()
                if usuario_produtor:
                    # Verificar se há outras fazendas do mesmo produtor acessíveis pelo usuário
                    outras_fazendas = Propriedade.objects.filter(produtor=usuario_produtor)
                    if outras_fazendas.exists() and fazenda.produtor == usuario_produtor:
                        usuario_tem_acesso = True
            except (AttributeError, TypeError) as e:
                logging.debug(f"Erro ao verificar acesso a outras fazendas: {e}")
                pass
        
        if not usuario_tem_acesso and not request.user.is_superuser:
            logger.warning(f'Usuário {request.user.username} tentou acessar fazenda {fazenda_id} sem permissão')
            return JsonResponse({
                'success': False,
                'error': 'Você não tem permissão para acessar esta fazenda'
            }, status=403)
        
        categoria = get_object_or_404(CategoriaAnimal, id=categoria_id)
        
        # Obter saldo atual
        data_atual = date.today()
        saldo_por_categoria = obter_saldo_atual_propriedade(fazenda, data_atual)
        saldo_atual = saldo_por_categoria.get(categoria, 0)
        
        logger.info(f'Saldo consultado: Fazenda={fazenda.nome_propriedade}, Categoria={categoria.nome}, Saldo={saldo_atual}')
        
        return JsonResponse({
            'success': True,
            'saldo': saldo_atual,
            'fazenda': fazenda.nome_propriedade,
            'categoria': categoria.nome,
            'saldo_atual': saldo_atual,
            'data_consulta': data_atual.strftime('%d/%m/%Y')
        })
        
    except Propriedade.DoesNotExist:
        logger.error(f'Fazenda {fazenda_id} não encontrada')
        return JsonResponse({
            'success': False,
            'error': f'Fazenda {fazenda_id} não encontrada'
        }, status=404)
    except CategoriaAnimal.DoesNotExist:
        logger.error(f'Categoria {categoria_id} não encontrada')
        return JsonResponse({
            'success': False,
            'error': f'Categoria {categoria_id} não encontrada'
        }, status=404)
    except Exception as e:
        logger.error(f'Erro ao obter saldo: {str(e)}', exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def buscar_saldo_inventario(request, propriedade_id, categoria_id):
    """View para buscar saldo do inventário de uma categoria específica"""
    try:
        propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
        categoria = get_object_or_404(CategoriaAnimal, id=categoria_id)
        
        # Buscar inventário da categoria
        inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            categoria=categoria
        ).first()
        
        if inventario:
            quantidade = inventario.quantidade
            categoria_nome = categoria.nome
        else:
            quantidade = 0
            categoria_nome = categoria.nome
        
        return JsonResponse({
            'success': True,
            'quantidade': quantidade,
            'categoria_nome': categoria_nome,
            'propriedade_nome': propriedade.nome_propriedade
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao buscar saldo: {str(e)}'
        })


def preparar_dados_graficos(movimentacoes, resumo_por_ano):
    """Prepara dados formatados para gráficos Chart.js"""
    from collections import defaultdict
    from decimal import Decimal
    
    # Inicializar estrutura de dados
    dados = {
        'labels': [],  # Períodos (ex: "2025", "Jan/2025")
        'total_animais': [],
        'femeas': [],
        'machos': [],
        'receitas': [],
        'custos': [],
        'lucro': [],
    }
    
    # Processar por ano - resumo_por_ano tem estrutura: {ano: {categoria: dados, 'TOTAIS': dados}}
    for ano, dados_ano in resumo_por_ano.items():
        # Obter linha de TOTAIS que já contém todos os cálculos corretos
        totais = dados_ano.get('TOTAIS', {})
        
        # Extrair dados dos TOTAIS
        total_animais = totais.get('total_animais', 0)
        total_femeas = totais.get('total_femeas', 0)
        total_machos = totais.get('total_machos', 0)
        receitas = float(totais.get('receitas', 0))
        custos = float(totais.get('custos', 0))
        lucro = receitas - custos
        
        dados['labels'].append(str(ano))
        dados['total_animais'].append(float(total_animais))
        dados['femeas'].append(float(total_femeas))
        dados['machos'].append(float(total_machos))
        dados['receitas'].append(float(receitas))
        dados['custos'].append(float(custos))
        dados['lucro'].append(float(lucro))
    
    return dados


# ==================== MÓDULO DÍVIDAS FINANCEIRAS ====================



@login_required
def importar_scr(request, propriedade_id):
    """Importar SCR do Banco Central - VERSÃO CORRIGIDA"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    if request.method == 'POST':
        arquivo_pdf = request.FILES.get('arquivo_pdf')
        data_referencia = request.POST.get('data_referencia')
        
        # Validações
        if not arquivo_pdf:
            messages.error(request, 'Por favor, selecione um arquivo PDF para importar.')
            return render(request, 'gestao_rural/importar_scr.html', {'propriedade': propriedade})
        
        if not data_referencia:
            messages.error(request, 'Por favor, informe a data de referência do SCR.')
            return render(request, 'gestao_rural/importar_scr.html', {'propriedade': propriedade})
        
        # Validar extensão do arquivo
        nome_arquivo = arquivo_pdf.name.lower()
        if not nome_arquivo.endswith('.pdf'):
            messages.error(request, 'Formato de arquivo inválido. Por favor, envie um arquivo PDF (.pdf).')
            return render(request, 'gestao_rural/importar_scr.html', {'propriedade': propriedade})
        
        # Validar tamanho do arquivo (máximo 10MB)
        if arquivo_pdf.size > 10 * 1024 * 1024:
            messages.error(request, 'Arquivo muito grande. O tamanho máximo permitido é 10MB.')
            return render(request, 'gestao_rural/importar_scr.html', {'propriedade': propriedade})
        
        # Validar data
        try:
            data_referencia_obj = datetime.strptime(data_referencia, '%Y-%m-%d').date()
            if data_referencia_obj > date.today():
                messages.error(request, 'A data de referência não pode ser futura.')
                return render(request, 'gestao_rural/importar_scr.html', {'propriedade': propriedade})
        except ValueError:
            messages.error(request, 'Data de referência inválida. Use o formato YYYY-MM-DD.')
            return render(request, 'gestao_rural/importar_scr.html', {'propriedade': propriedade})
        
        try:
            # Verificar se bibliotecas necessárias estão instaladas
            try:
                import PyPDF2
                import pdfplumber
            except ImportError as e:
                messages.error(request, f'Bibliotecas necessárias não estão instaladas: {str(e)}. Execute: pip install PyPDF2 pdfplumber')
                return render(request, 'gestao_rural/importar_scr.html', {'propriedade': propriedade})
            
            # Criar registro do SCR
            scr = SCRBancoCentral.objects.create(
                produtor=propriedade.produtor,
                arquivo_pdf=arquivo_pdf,
                data_referencia_scr=data_referencia_obj,
                status='IMPORTADO'
            )
            
            # Processar o PDF automaticamente
            from .scr_parser import SCRParser, SCRProcessor
            
            try:
                parser = SCRParser()
                dados_extraidos = parser.extrair_dados_pdf(arquivo_pdf)
                
                if not dados_extraidos or not dados_extraidos.get('dividas_por_banco'):
                    messages.warning(request, 'SCR importado, mas nenhuma dívida foi identificada no PDF. Verifique se o arquivo está correto.')
                    scr.status = 'ERRO'
                    scr.save()
                    return redirect('dividas_dashboard', propriedade_id=propriedade.id)
                
                # Salvar dados extraídos
                processor = SCRProcessor(scr, dados_extraidos)
                estatisticas = processor.processar_e_salvar()
                
                if estatisticas.get('erros'):
                    erros_msg = '; '.join(estatisticas['erros'][:5])  # Limitar a 5 erros
                    if len(estatisticas['erros']) > 5:
                        erros_msg += f'... (mais {len(estatisticas["erros"]) - 5} erros)'
                    messages.warning(request, f'SCR importado com avisos: {erros_msg}')
                else:
                    messages.success(request, f'✅ SCR importado e processado com sucesso! {estatisticas.get("dividas_criadas", 0)} dívidas identificadas.')
                
                scr.status = 'PROCESSADO'
                scr.save()
                
                return redirect('dividas_dashboard', propriedade_id=propriedade.id)
                
            except Exception as e_parser:
                # Erro no parser
                scr.status = 'ERRO'
                scr.save()
                import traceback
                error_detail = traceback.format_exc()
                messages.error(request, f'❌ Erro ao processar PDF do SCR: {str(e_parser)}')
                logging.error(f"Erro ao processar SCR - Propriedade {propriedade_id}: {error_detail}")
                return render(request, 'gestao_rural/importar_scr.html', {'propriedade': propriedade})
                
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            messages.error(request, f'❌ Erro ao importar SCR: {str(e)}')
            logging.error(f"Erro ao importar SCR - Propriedade {propriedade_id}: {error_detail}")
            return render(request, 'gestao_rural/importar_scr.html', {'propriedade': propriedade})
    
    return render(request, 'gestao_rural/importar_scr.html', {'propriedade': propriedade})


@login_required
def reprocessar_scr(request, propriedade_id, scr_id):
    """Reprocessar SCR que falhou"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    scr = get_object_or_404(SCRBancoCentral, id=scr_id, produtor=propriedade.produtor)
    
    try:
        from .scr_parser import SCRParser, SCRProcessor
        
        # Limpar dados anteriores
        scr.dividas.all().delete()
        
        # Reprocessar PDF
        parser = SCRParser()
        dados_extraidos = parser.extrair_dados_pdf(scr.arquivo_pdf)
        
        # Salvar dados extraídos
        processor = SCRProcessor(scr, dados_extraidos)
        estatisticas = processor.processar_e_salvar()
        
        if estatisticas['erros']:
            messages.warning(request, f'SCR reprocessado com avisos: {", ".join(estatisticas["erros"])}')
        else:
            messages.success(request, f'SCR reprocessado com sucesso! {estatisticas["dividas_criadas"]} dívidas identificadas.')
        
    except Exception as e:
        messages.error(request, f'Erro ao reprocessar SCR: {str(e)}')
        logging.error(f"Erro ao reprocessar SCR: {str(e)}")
    
    return redirect('dividas_dashboard', propriedade_id=propriedade.id)


@login_required
def distribuir_dividas_por_fazenda(request, propriedade_id, scr_id):
    """Distribuir dívidas do SCR para fazendas específicas"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    scr = get_object_or_404(SCRBancoCentral, id=scr_id, produtor=propriedade.produtor)
    
    if request.method == 'POST':
        # Processar distribuição
        distribuicoes = []
        
        for key, value in request.POST.items():
            if key.startswith('divida_') and key.endswith('_fazenda'):
                divida_id = key.replace('divida_', '').replace('_fazenda', '')
                fazenda_id = value
                
                if fazenda_id and fazenda_id != '0':
                    distribuicoes.append({
                        'divida_id': divida_id,
                        'fazenda_id': fazenda_id
                    })
        
        # Criar contratos para cada distribuição
        contratos_criados = 0
        
        for distribuicao in distribuicoes:
            try:
                divida = DividaBanco.objects.get(id=distribuicao['divida_id'])
                fazenda = Propriedade.objects.get(id=distribuicao['fazenda_id'])
                
                # Calcular valores do contrato
                valor_por_contrato = divida.valor_total / divida.quantidade_contratos
                
                # Criar contratos individuais
                for i in range(divida.quantidade_contratos):
                    contrato = ContratoDivida.objects.create(
                        divida_banco=divida,
                        propriedade=fazenda,
                        numero_contrato=f"{divida.banco}_{divida.id}_{i+1}",
                        valor_contrato=valor_por_contrato,
                        taxa_juros_anual=Decimal('8.5'),  # Taxa padrão
                        quantidade_parcelas=60,  # 5 anos padrão
                        valor_parcela=valor_por_contrato / 60,
                        data_inicio=scr.data_referencia_scr,
                        data_vencimento=scr.data_referencia_scr.replace(year=scr.data_referencia_scr.year + 5),
                        status='ATIVO'
                    )
                    
                    # Gerar amortização
                    gerar_amortizacao_contrato(contrato)
                    
                    contratos_criados += 1
                
            except Exception as e:
                logging.error(f"Erro ao criar contrato: {str(e)}")
                continue
        
        messages.success(request, f'{contratos_criados} contratos criados e distribuídos para as fazendas!')
        return redirect('dividas_contratos', propriedade_id=propriedade.id)
    
    # Buscar dívidas e fazendas para distribuição
    dividas = DividaBanco.objects.filter(scr=scr)
    fazendas = Propriedade.objects.filter(produtor=propriedade.produtor)
    
    context = {
        'propriedade': propriedade,
        'scr': scr,
        'dividas': dividas,
        'fazendas': fazendas,
    }
    
    return render(request, 'gestao_rural/distribuir_dividas.html', context)


def gerar_amortizacao_contrato(contrato):
    """Gera tabela de amortização para um contrato"""
    from .models import AmortizacaoContrato
    from datetime import timedelta
    
    saldo_devedor = contrato.valor_contrato
    taxa_mensal = contrato.taxa_juros_anual / 100 / 12
    
    for parcela_num in range(1, contrato.quantidade_parcelas + 1):
        # Calcular valores da parcela
        valor_juros = saldo_devedor * taxa_mensal
        valor_principal = contrato.valor_parcela - valor_juros
        valor_total = valor_principal + valor_juros
        
        # Atualizar saldo devedor
        saldo_devedor -= valor_principal
        
        # Data de vencimento
        data_vencimento = contrato.data_inicio + timedelta(days=30 * parcela_num)
        
        # Criar amortização
        AmortizacaoContrato.objects.create(
            contrato=contrato,
            numero_parcela=parcela_num,
            data_vencimento=data_vencimento,
            valor_principal=valor_principal,
            valor_juros=valor_juros,
            valor_total=valor_total,
            saldo_devedor=max(saldo_devedor, Decimal('0'))
        )


@login_required
def dividas_amortizacao(request, propriedade_id):
    """Amortização de contratos"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    contratos = ContratoDivida.objects.filter(propriedade=propriedade)

    # Geração de amortização via POST (PRICE/SAC)
    if request.method == 'POST' and request.POST.get('simular'):
        try:
            contrato_id = int(request.POST.get('contrato_id'))
            metodo = request.POST.get('metodo') or 'PRICE'
            parcelas = int(request.POST.get('parcelas') or 0)
            juros_am = Decimal(str(request.POST.get('juros_am') or '0'))
            primeiro_venc = request.POST.get('primeiro_vencimento')

            contrato = get_object_or_404(ContratoDivida, id=contrato_id, propriedade=propriedade)
            if parcelas < 1 or parcelas > 480:
                raise ValueError('Quantidade de parcelas inválida.')

            if not primeiro_venc:
                raise ValueError('Primeira data de vencimento obrigatória.')

            from datetime import datetime
            data_venc = datetime.strptime(primeiro_venc, '%Y-%m-%d').date()

            # Parâmetros financeiros
            saldo = Decimal(str(contrato.valor_contratado))
            i = (juros_am / Decimal('100'))  # taxa ao mês (decimal)

            # Limpar amortizações anteriores do contrato
            AmortizacaoContrato.objects.filter(contrato=contrato).delete()

            # Cálculo da prestação no PRICE
            prestacao = None
            if metodo == 'PRICE':
                if i == 0:
                    prestacao = saldo / parcelas
                else:
                    fator = (i * (1 + i) ** parcelas) / (((1 + i) ** parcelas) - 1)
                    prestacao = (saldo * fator).quantize(Decimal('0.01'))

            for n in range(1, parcelas + 1):
                juros = (saldo * i).quantize(Decimal('0.01')) if i > 0 else Decimal('0.00')
                if metodo == 'PRICE':
                    principal = (prestacao - juros) if i > 0 else (saldo / parcelas)
                    valor_total = prestacao if i > 0 else (principal + juros)
                else:  # SAC
                    principal = (saldo / (parcelas - n + 1)).quantize(Decimal('0.01')) if (parcelas - n + 1) > 0 else saldo
                    valor_total = (principal + juros).quantize(Decimal('0.01'))

                novo_saldo = (saldo - principal).quantize(Decimal('0.01'))

                AmortizacaoContrato.objects.create(
                    contrato=contrato,
                    numero_parcela=n,
                    data_vencimento=data_venc,
                    valor_principal=max(principal, Decimal('0.00')),
                    valor_juros=max(juros, Decimal('0.00')),
                    valor_total=max(valor_total, Decimal('0.00')),
                    saldo_devedor=max(novo_saldo, Decimal('0.00')),
                )

                saldo = novo_saldo
                # Avançar um mês sem dependências externas
                from calendar import monthrange
                old_day = data_venc.day
                year = data_venc.year
                month = data_venc.month + 1
                if month > 12:
                    month = 1
                    year += 1
                last_day = monthrange(year, month)[1]
                new_day = min(old_day, last_day)
                data_venc = data_venc.replace(year=year, month=month, day=new_day)

            messages.success(request, 'Tabela de amortização gerada com sucesso!')
            return redirect('dividas_amortizacao', propriedade_id=propriedade.id)
        except Exception as e:
            messages.error(request, f'Erro ao simular amortização: {e}')
            return redirect('dividas_amortizacao', propriedade_id=propriedade.id)

    amortizacoes = AmortizacaoContrato.objects.filter(
        contrato__propriedade=propriedade
    ).order_by('data_vencimento')
    
    context = {
        'propriedade': propriedade,
        'contratos': contratos,
        'amortizacoes': amortizacoes,
    }
    
    return render(request, 'gestao_rural/dividas_amortizacao.html', context)


# ==================== MÓDULO PROJETO BANCÁRIO ====================

@login_required
def projeto_bancario_dashboard(request, propriedade_id):
    """Dashboard do módulo Projeto Bancário"""
    from .models import ProjetoBancario
    
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    projetos = ProjetoBancario.objects.filter(propriedade=propriedade).order_by('-data_solicitacao')
    
    # Calcular estatísticas
    total_solicitado = sum(projeto.valor_solicitado for projeto in projetos if projeto.valor_solicitado) or 0
    total_aprovado = sum(projeto.valor_aprovado for projeto in projetos if projeto.valor_aprovado) or 0
    projetos_aprovados = projetos.filter(status='APROVADO').count()
    projetos_em_analise = projetos.filter(status='EM_ANALISE').count()
    projetos_pendentes = projetos.filter(status='PENDENTE').count()
    
    context = {
        'propriedade': propriedade,
        'projetos': projetos,
        'total_solicitado': total_solicitado,
        'total_aprovado': total_aprovado,
        'projetos_aprovados': projetos_aprovados,
        'projetos_em_analise': projetos_em_analise,
        'projetos_pendentes': projetos_pendentes,
        'total_projetos': projetos.count(),
    }
    
    return render(request, 'gestao_rural/projeto_bancario_dashboard.html', context)


@login_required
def projeto_bancario_novo(request, propriedade_id):
    """Criar novo projeto bancário"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    from .forms_projetos import ProjetoBancarioForm
    
    # Verificar se há um planejamento_id na URL (vindo da página de cenários)
    planejamento_id = request.GET.get('planejamento_id')
    planejamento = None
    if planejamento_id:
        try:
            planejamento = PlanejamentoAnual.objects.get(id=planejamento_id, propriedade=propriedade)
            messages.info(request, f'Projeção {planejamento.codigo} será vinculada ao projeto bancário.')
        except PlanejamentoAnual.DoesNotExist:
            messages.warning(request, 'Planejamento não encontrado.')
    
    if request.method == 'POST':
        form = ProjetoBancarioForm(request.POST, request.FILES, propriedade=propriedade)
        if form.is_valid():
            projeto = form.save(commit=False)
            projeto.propriedade = propriedade
            if not projeto.status:
                projeto.status = 'RASCUNHO'
            projeto.save()
            messages.success(request, f'Projeto bancário criado com sucesso!{" A projeção foi vinculada." if projeto.planejamento else ""}')
            return redirect('projeto_bancario_detalhes', propriedade_id=propriedade.id, projeto_id=projeto.id)
        else:
            messages.error(request, 'Corrija os erros do formulário.')
    else:
        form = ProjetoBancarioForm(propriedade=propriedade)
        # Pré-selecionar o planejamento se veio da página de cenários
        if planejamento:
            form.fields['planejamento'].initial = planejamento.id
    
    return render(request, 'gestao_rural/projeto_bancario_novo.html', {
        'propriedade': propriedade, 
        'form': form,
        'planejamento_vinculado': planejamento
    })


@login_required
def projeto_bancario_detalhes(request, propriedade_id, projeto_id):
    """Detalhes do projeto bancário"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    projeto = get_object_or_404(ProjetoBancario, id=projeto_id, propriedade=propriedade)
    
    documentos = DocumentoProjeto.objects.filter(projeto=projeto)
    
    # Análise de cenários se houver planejamento vinculado
    cenarios_analise = None
    if projeto.planejamento:
        from .views_cenarios import calcular_metricas_cenario
        from .models import CenarioPlanejamento
        
        cenarios = CenarioPlanejamento.objects.filter(planejamento=projeto.planejamento).order_by('-is_baseline', 'nome')
        cenarios_analise = []
        
        # Calcular parcela do empréstimo
        valor_financiamento = projeto.valor_solicitado or projeto.valor_aprovado or Decimal('0')
        taxa_juros_mensal = projeto.taxa_juros / 100 / 12 if projeto.taxa_juros else Decimal('0')
        prazo_meses = projeto.prazo_pagamento or 1
        
        if valor_financiamento > 0 and prazo_meses > 0:
            # Cálculo da parcela (Price)
            if taxa_juros_mensal > 0:
                fator = (1 + taxa_juros_mensal) ** prazo_meses
                valor_parcela_mensal = valor_financiamento * (taxa_juros_mensal * fator) / (fator - 1)
            else:
                valor_parcela_mensal = valor_financiamento / prazo_meses
        else:
            valor_parcela_mensal = Decimal('0')
        
        valor_parcela_anual = valor_parcela_mensal * 12
        
        for cenario in cenarios:
            metricas = calcular_metricas_cenario(projeto.planejamento, cenario)
            
            # Calcular capacidade de pagamento
            lucro_anual = Decimal(str(metricas['lucro']))
            capacidade_pagamento = lucro_anual - valor_parcela_anual
            cobertura_parcela = (lucro_anual / valor_parcela_anual * 100) if valor_parcela_anual > 0 else Decimal('0')
            
            # Avaliar viabilidade
            if capacidade_pagamento >= 0 and cobertura_parcela >= 150:
                viabilidade = 'ALTA'
            elif capacidade_pagamento >= 0 and cobertura_parcela >= 120:
                viabilidade = 'MÉDIA'
            elif capacidade_pagamento >= 0:
                viabilidade = 'BAIXA'
            else:
                viabilidade = 'INVIÁVEL'
            
            cenarios_analise.append({
                'cenario': cenario,
                'metricas': metricas,
                'valor_parcela_mensal': float(valor_parcela_mensal),
                'valor_parcela_anual': float(valor_parcela_anual),
                'capacidade_pagamento': float(capacidade_pagamento),
                'cobertura_parcela': float(cobertura_parcela),
                'viabilidade': viabilidade,
            })
    
    context = {
        'propriedade': propriedade,
        'projeto': projeto,
        'documentos': documentos,
        'cenarios_analise': cenarios_analise,
    }
    
    return render(request, 'gestao_rural/projeto_bancario_detalhes.html', context)


@login_required
def projeto_bancario_analise_cenarios(request, propriedade_id, projeto_id):
    """Análise detalhada de cenários para o projeto bancário"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    projeto = get_object_or_404(ProjetoBancario, id=projeto_id, propriedade=propriedade)
    
    if not projeto.planejamento:
        messages.warning(request, 'Este projeto não possui um planejamento vinculado. Vincule um planejamento para analisar cenários.')
        return redirect('projeto_bancario_detalhes', propriedade_id=propriedade.id, projeto_id=projeto.id)
    
    from .views_cenarios import calcular_metricas_cenario
    from .models import CenarioPlanejamento
    
    planejamento = projeto.planejamento
    cenarios = CenarioPlanejamento.objects.filter(planejamento=planejamento).order_by('-is_baseline', 'nome')
    
    # Calcular valores do financiamento
    valor_financiamento = projeto.valor_solicitado or projeto.valor_aprovado or Decimal('0')
    taxa_juros_mensal = projeto.taxa_juros / 100 / 12 if projeto.taxa_juros else Decimal('0')
    prazo_meses = projeto.prazo_pagamento or 1
    
    if valor_financiamento > 0 and prazo_meses > 0:
        # Cálculo da parcela (Price)
        if taxa_juros_mensal > 0:
            fator = (1 + taxa_juros_mensal) ** prazo_meses
            valor_parcela_mensal = valor_financiamento * (taxa_juros_mensal * fator) / (fator - 1)
        else:
            valor_parcela_mensal = valor_financiamento / prazo_meses
    else:
        valor_parcela_mensal = Decimal('0')
    
    valor_parcela_anual = valor_parcela_mensal * 12
    valor_total_pagamento = valor_parcela_mensal * prazo_meses
    valor_total_juros = valor_total_pagamento - valor_financiamento
    
    # Analisar cada cenário
    cenarios_analise = []
    for cenario in cenarios:
        metricas = calcular_metricas_cenario(planejamento, cenario)
        
        # Calcular capacidade de pagamento
        lucro_anual = Decimal(str(metricas['lucro']))
        capacidade_pagamento = lucro_anual - valor_parcela_anual
        cobertura_parcela = (lucro_anual / valor_parcela_anual * 100) if valor_parcela_anual > 0 else Decimal('0')
        
        # Calcular margem de segurança
        margem_seguranca = ((lucro_anual - valor_parcela_anual) / lucro_anual * 100) if lucro_anual > 0 else Decimal('0')
        
        # Calcular prazo de retorno considerando o financiamento
        investimento_liquido = valor_financiamento - valor_total_juros if valor_financiamento > 0 else Decimal('0')
        payback_anos = (investimento_liquido / capacidade_pagamento) if capacidade_pagamento > 0 else Decimal('0')
        
        # Avaliar viabilidade
        if capacidade_pagamento >= 0 and cobertura_parcela >= 150 and margem_seguranca >= 30:
            viabilidade = 'ALTA'
            viabilidade_descricao = 'Excelente capacidade de pagamento e margem de segurança'
        elif capacidade_pagamento >= 0 and cobertura_parcela >= 120 and margem_seguranca >= 20:
            viabilidade = 'MÉDIA'
            viabilidade_descricao = 'Boa capacidade de pagamento, mas margem de segurança moderada'
        elif capacidade_pagamento >= 0 and cobertura_parcela >= 100:
            viabilidade = 'BAIXA'
            viabilidade_descricao = 'Capacidade de pagamento no limite, baixa margem de segurança'
        else:
            viabilidade = 'INVIÁVEL'
            viabilidade_descricao = 'Lucro insuficiente para cobrir as parcelas do financiamento'
        
        cenarios_analise.append({
            'cenario': cenario,
            'metricas': metricas,
            'valor_parcela_mensal': float(valor_parcela_mensal),
            'valor_parcela_anual': float(valor_parcela_anual),
            'capacidade_pagamento': float(capacidade_pagamento),
            'cobertura_parcela': float(cobertura_parcela),
            'margem_seguranca': float(margem_seguranca),
            'payback_anos': float(payback_anos),
            'viabilidade': viabilidade,
            'viabilidade_descricao': viabilidade_descricao,
        })
    
    # Calcular prazo em anos
    prazo_anos = prazo_meses / 12 if prazo_meses > 0 else 0
    
    context = {
        'propriedade': propriedade,
        'projeto': projeto,
        'planejamento': planejamento,
        'cenarios_analise': cenarios_analise,
        'valor_financiamento': float(valor_financiamento),
        'valor_parcela_mensal': float(valor_parcela_mensal),
        'valor_parcela_anual': float(valor_parcela_anual),
        'valor_total_pagamento': float(valor_total_pagamento),
        'valor_total_juros': float(valor_total_juros),
        'prazo_meses': prazo_meses,
        'prazo_anos': float(prazo_anos),
        'taxa_juros': projeto.taxa_juros,
    }
    
    return render(request, 'gestao_rural/projeto_bancario_analise_cenarios.html', context)


@login_required
def projeto_bancario_editar(request, propriedade_id, projeto_id):
    """Editar projeto bancário"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    projeto = get_object_or_404(ProjetoBancario, id=projeto_id, propriedade=propriedade)
    
    from .forms_projetos import ProjetoBancarioForm
    if request.method == 'POST':
        form = ProjetoBancarioForm(request.POST, request.FILES, instance=projeto, propriedade=propriedade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projeto bancário atualizado com sucesso!')
            return redirect('projeto_bancario_detalhes', propriedade_id=propriedade.id, projeto_id=projeto.id)
        else:
            messages.error(request, 'Corrija os erros do formulário.')
    else:
        form = ProjetoBancarioForm(instance=projeto, propriedade=propriedade)
    
    return render(request, 'gestao_rural/projeto_bancario_editar.html', {'propriedade': propriedade, 'projeto': projeto, 'form': form})


@login_required
def dividas_contratos(request, propriedade_id):
    """Lista todos os contratos de dívida de uma propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id)
    
    contratos = ContratoDivida.objects.filter(propriedade=propriedade).order_by('-data_inicio')

    # Filtros simples
    banco = request.GET.get('banco')
    status = request.GET.get('status')
    if banco:
        contratos = contratos.filter(banco__icontains=banco)
    if status:
        contratos = contratos.filter(status=status)

    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(contratos, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'propriedade': propriedade,
        'contratos': page_obj,
        'page_obj': page_obj,
        'filtro_banco': banco,
        'filtro_status': status,
    }
    
    return render(request, 'gestao_rural/dividas_contratos.html', context)


@login_required
def api_valor_inventario(request, propriedade_id, categoria_id):
    """API para buscar valor por cabeça do inventário de uma categoria"""
    from django.http import JsonResponse
    
    try:
        propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
        categoria = get_object_or_404(CategoriaAnimal, id=categoria_id)
        
        # Buscar valor do inventário para esta categoria
        inventario = InventarioRebanho.objects.filter(
            propriedade=propriedade,
            categoria=categoria
        ).first()
        
        if inventario:
            valor_por_cabeca = float(inventario.valor_por_cabeca)
        else:
            valor_por_cabeca = 0.0
        
        return JsonResponse({
            'valor_por_cabeca': valor_por_cabeca,
            'categoria_nome': categoria.nome,
            'propriedade_nome': propriedade.nome_propriedade
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def api_buscar_planejamento_por_codigo(request, propriedade_id):
    """API para buscar planejamento por código"""
    from django.http import JsonResponse
    
    try:
        propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
        codigo = request.GET.get('codigo', '').strip().upper()
        
        if not codigo:
            return JsonResponse({'error': 'Código não fornecido'}, status=400)
        
        try:
            planejamento = PlanejamentoAnual.objects.get(
                codigo=codigo,
                propriedade=propriedade
            )
            
            return JsonResponse({
                'id': planejamento.id,
                'codigo': planejamento.codigo,
                'ano': planejamento.ano,
                'descricao': planejamento.descricao,
                'status': planejamento.status,
                'status_display': planejamento.get_status_display()
            })
        except PlanejamentoAnual.DoesNotExist:
            return JsonResponse({'error': f'Projeção com código {codigo} não encontrada'}, status=404)
        except PlanejamentoAnual.MultipleObjectsReturned:
            planejamento = PlanejamentoAnual.objects.filter(
                codigo=codigo,
                propriedade=propriedade
            ).first()
            return JsonResponse({
                'id': planejamento.id,
                'codigo': planejamento.codigo,
                'ano': planejamento.ano,
                'descricao': planejamento.descricao,
                'status': planejamento.status,
                'status_display': planejamento.get_status_display()
            })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def dividas_dashboard(request, propriedade_id):
    """Dashboard de dívidas financeiras"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Buscar SCRs importados
    scrs = SCRBancoCentral.objects.filter(produtor=propriedade.produtor).order_by('-data_importacao')
    
    # Buscar contratos de dívida da propriedade
    contratos = ContratoDivida.objects.filter(propriedade=propriedade).order_by('-data_inicio')
    
    # Calcular estatísticas
    total_dividas = contratos.aggregate(total=Sum('valor_contrato'))['total'] or Decimal('0.00')
    contratos_ativos = contratos.filter(status='ATIVO').count()
    
    # Calcular parcelas pendentes
    total_parcelas_pendentes = 0
    for contrato in contratos:
        total_parcelas_pendentes += contrato.amortizacoes.filter(status_pagamento='PENDENTE').count()
    
    context = {
        'propriedade': propriedade,
        'scrs': scrs,
        'contratos': contratos,
        'total_dividas': total_dividas,
        'contratos_ativos': contratos_ativos,
        'total_parcelas_pendentes': total_parcelas_pendentes,
    }
    
    return render(request, 'gestao_rural/dividas_dashboard.html', context)


@login_required
def projeto_bancario_dashboard(request, propriedade_id):
    """Dashboard de projetos bancários"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    # Buscar projetos bancários da propriedade
    projetos = ProjetoBancario.objects.filter(propriedade=propriedade).order_by('-data_solicitacao')
    
    # Calcular estatísticas
    total_solicitado = projetos.aggregate(total=Sum('valor_solicitado'))['total'] or 0
    total_aprovado = projetos.filter(status='APROVADO').aggregate(total=Sum('valor_aprovado'))['total'] or 0
    projetos_em_analise = projetos.filter(status='EM_ANALISE').count()
    
    context = {
        'propriedade': propriedade,
        'projetos': projetos,
        'total_solicitado': total_solicitado,
        'total_aprovado': total_aprovado,
        'projetos_em_analise': projetos_em_analise,
    }
    
    return render(request, 'gestao_rural/projeto_bancario_dashboard.html', context)


@login_required
def propriedade_modulos(request, propriedade_id):
    """Exibe os módulos disponíveis para uma propriedade"""
    from .decorators import obter_propriedade_com_permissao
    from .models_auditoria import UsuarioAtivo
    from .models import Propriedade, ProdutorRural
    
    # ========== VERIFICAÇÃO DE USUÁRIO DEMO - PRIMEIRA COISA A FAZER ==========
    is_demo_user = False
    
    # Verificar se é usuário demo padrão
    if request.user.username in ['demo', 'demo_monpec']:
        is_demo_user = True
        logger.info(f'USUÁRIO DEMO PADRÃO: {request.user.username}')
    else:
        # Verificar se é usuário de demonstração (do popup ou formulário)
        try:
            UsuarioAtivo.objects.get(usuario=request.user)
            is_demo_user = True
            logger.info(f'USUÁRIO DEMO (UsuarioAtivo): {request.user.username}')
        except:
            # Verificar se é usuário criado via formulário de demonstração
            try:
                UsuarioAtivo.objects.get(email=request.user.email)
                is_demo_user = True
                logger.info(f'USUÁRIO DEMO (formulário): {request.user.username} ({request.user.email})')
            except:
                logger.info(f'USUÁRIO NÃO É DEMO: {request.user.username}')
                pass
    
    # ========== SE FOR DEMO, SEMPRE USAR PROPRIEDADE COMPARTILHADA ==========
    if is_demo_user:
        # Usuários demo com UsuarioAtivo usam a propriedade compartilhada "Fazenda Demonstracao"
        propriedade_compartilhada = Propriedade.objects.filter(
            nome_propriedade='Fazenda Demonstracao'
        ).first()

        if propriedade_compartilhada:
            # Se o ID solicitado NÃO for a propriedade compartilhada, redirecionar
            if propriedade_id != propriedade_compartilhada.id:
                logger.info(f'🔄 REDIRECIONANDO DEMO: propriedade {propriedade_id} → {propriedade_compartilhada.nome_propriedade} (ID: {propriedade_compartilhada.id})')
                return redirect('propriedade_modulos', propriedade_id=propriedade_compartilhada.id)

            # Se chegou aqui, é a propriedade compartilhada - usar diretamente
            propriedade = propriedade_compartilhada
            logger.info(f'DEMO ACESSANDO PROPRIEDADE COMPARTILHADA {propriedade.nome_propriedade} (ID: {propriedade.id})')
        else:
            # Propriedade compartilhada não existe, redirecionar para setup
            logger.warning(f'Propriedade compartilhada "Fazenda Demonstracao" não encontrada. Redirecionando para demo_setup.')
            return redirect('demo_setup')
    else:
        # Usuário normal - verificar permissão
        try:
            propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
        except Exception as e:
            # Se der erro, verificar novamente se não é demo (pode ter sido criado agora)
            try:
                UsuarioAtivo.objects.get(usuario=request.user)
                # É demo! Redirecionar para propriedade Monpec do produtor
                produtor = ProdutorRural.objects.filter(usuario_responsavel=request.user).first()
                if produtor:
                    try:
                        monpec1 = Propriedade.objects.filter(
                            produtor=produtor,
                            nome_propriedade__iregex=r'^Monpec\d+$'
                        ).order_by('nome_propriedade').first()
                    except ProgrammingError:
                        monpec1 = Propriedade.objects.filter(produtor=produtor).first()
                    if monpec1:
                        logger.info(f'🔄 Usuário identificado como demo após erro. Redirecionando para {monpec1.nome_propriedade}')
                        return redirect('propriedade_modulos', propriedade_id=monpec1.id)
            except:
                pass
            # Se não for demo, re-raise o erro
            raise
    
    total_animais = (
        InventarioRebanho.objects
        .filter(propriedade=propriedade)
        .aggregate(total=Sum('quantidade'))
        .get('total') or 0
    )
    
    # Buscar todas as propriedades disponíveis para o seletor
    todas_propriedades = _obter_todas_propriedades(request.user)
    
    # Buscar preferências de módulos do usuário para esta propriedade
    from .models import PreferenciaModulosUsuario
    try:
        preferencia = PreferenciaModulosUsuario.objects.get(
            usuario=request.user,
            propriedade=propriedade
        )
        configuracao = preferencia.configuracao
    except PreferenciaModulosUsuario.DoesNotExist:
        # Configuração padrão: todos os módulos na ordem original
        configuracao = {
            'modulos': ['curral', 'planejamento', 'pecuaria', 'nutricao', 'patrimonio', 
                       'compras', 'financeiro', 'operacoes', 'projetos', 'relatorios', 
                       'categorias', 'configuracoes'],
            'ordem': list(range(12))
        }
    
    context = {
        'propriedade': propriedade,
        'total_animais': total_animais,
        'todas_propriedades': todas_propriedades,
        'configuracao_modulos': json.dumps(configuracao),
    }
    
    return render(request, 'propriedade_modulos.html', context)


@login_required
def salvar_preferencias_modulos(request, propriedade_id):
    """Salva as preferências de módulos do usuário"""
    from .models import PreferenciaModulosUsuario, Propriedade
    from .decorators import obter_propriedade_com_permissao
    
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    try:
        # Verificar permissão
        propriedade = obter_propriedade_com_permissao(request.user, propriedade_id)
        
        # Obter dados do POST
        data = json.loads(request.body)
        modulos = data.get('modulos', [])
        ordem = data.get('ordem', [])
        
        # Validar que temos exatamente 12 módulos (mantendo o número de cards)
        if len(modulos) != 12:
            return JsonResponse({
                'erro': 'Deve haver exatamente 12 módulos selecionados'
            }, status=400)
        
        # Criar ou atualizar preferência
        preferencia, created = PreferenciaModulosUsuario.objects.update_or_create(
            usuario=request.user,
            propriedade=propriedade,
            defaults={
                'configuracao': {
                    'modulos': modulos,
                    'ordem': ordem
                }
            }
        )
        
        return JsonResponse({
            'sucesso': True,
            'mensagem': 'Preferências salvas com sucesso!',
            'configuracao': preferencia.configuracao
        })
        
    except Exception as e:
        logger.error(f'Erro ao salvar preferências de módulos: {str(e)}')
        return JsonResponse({
            'erro': f'Erro ao salvar preferências: {str(e)}'
        }, status=500)


def robots_txt(request):
    """
    View para servir o arquivo robots.txt
    Permite indexação de páginas públicas mas bloqueia áreas administrativas
    """
    content = """User-agent: *
Allow: /
Allow: /dashboard/
Allow: /demo/
Disallow: /admin/
Disallow: /api/
Disallow: /static/
Disallow: /media/
Disallow: /login/
Disallow: /logout/
Disallow: /recuperar-senha/
Disallow: /alterar-senha/

# Sitemap
Sitemap: https://monpec.com.br/sitemap.xml
"""
    return HttpResponse(content, content_type='text/plain')

def offline_page(request):
    """Página exibida quando não há conexão com internet"""
    return render(request, 'site/offline.html')
