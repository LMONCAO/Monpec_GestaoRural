from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
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
import logging
from datetime import datetime, timedelta, date
from decimal import Decimal, InvalidOperation
import json
import urllib.parse

logger = logging.getLogger(__name__)


def landing_page(request):
    """Página pública do sistema antes do login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    # Limpar mensagens de warning/error que não são relacionadas ao formulário de contato
    # Isso evita que mensagens internas do sistema (como erros de brincos/lotes) apareçam na landing page
    from django.contrib.messages import get_messages
    storage = get_messages(request)
    mensagens_validas = []
    
    # Filtrar mensagens: remover mensagens internas do sistema que não fazem sentido na landing page
    for message in storage:
        mensagem_texto = str(message).lower()
        
        # Remover mensagens sobre brincos, lotes, animais, etc. que são do sistema interno
        if any(palavra in mensagem_texto for palavra in [
            'brinco', 'lote', 'localizado para o', 'animal', 'propriedade', 
            'cadastro', 'editar', 'excluir', 'salvo', 'atualizado'
        ]):
            continue  # Não adicionar essas mensagens
        
        # Manter apenas mensagens relacionadas ao formulário de contato
        if any(palavra in mensagem_texto for palavra in ['contato', 'enviar', 'mensagem', 'preencha', 'tente novamente']):
            mensagens_validas.append((message.level, message.message, message.tags))
    
    # Consumir todas as mensagens antigas
    list(storage)  # Isso consome as mensagens do storage
    
    # Recriar apenas as mensagens válidas (relacionadas ao contato)
    for level, msg, tags in mensagens_validas:
        messages.add_message(request, level, msg, extra_tags=tags)

    features = [
        {
            'icone': 'bi-speedometer2',
            'titulo': 'Dashboard integrado',
            'descricao': 'Indicadores completos para tomada de decisão em tempo real para propriedades rurais.',
        },
        {
            'icone': 'bi-diagram-3',
            'titulo': 'Planejamento pecuário',
            'descricao': 'Cenários, planejamento nutricional e reprodução com projeções automáticas.',
        },
        {
            'icone': 'bi-cash-coin',
            'titulo': 'Controle financeiro',
            'descricao': 'Gestão de custos, vendas, dívidas e fluxo de caixa em um único lugar.',
        },
        {
            'icone': 'bi-shield-check',
            'titulo': 'Rastreabilidade completa',
            'descricao': 'Registro individual dos animais, movimentações e relatórios oficiais PNIB.',
        },
    ]

    depoimentos = [
        {
            'nome': 'André Souza',
            'cargo': 'Produtor de corte em Goiás',
            'texto': '“Centralizamos toda a gestão do rebanho em um único painel e reduzimos custos em 18% no primeiro ano.”',
        },
        {
            'nome': 'Carla Menezes',
            'cargo': 'Consultora agropecuária',
            'texto': '“Com o MONPEC conseguimos acompanhar os indicadores dos clientes em tempo real e otimizar decisões estratégicas.”',
        },
    ]

    context = {
        'features': features,
        'depoimentos': depoimentos,
    }
    return render(request, 'site/landing_page.html', context)


def contato_submit(request):
    """Processa o formulário de contato e envia email e WhatsApp"""
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        empresa = request.POST.get('empresa', '').strip()
        mensagem = request.POST.get('mensagem', '').strip()
        
        # Validação básica
        if not nome or not email or not mensagem:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            url_redirect = reverse('landing_page') + '#contato'
            return redirect(url_redirect)
        
        # Preparar mensagem para email
        assunto = f'Nova mensagem de contato - MONPEC'
        corpo_email = f"""
Nova mensagem recebida através do formulário de contato do site MONPEC:

Nome: {nome}
Email: {email}
Telefone: {telefone}
Empresa/Fazenda: {empresa or 'Não informado'}

Mensagem:
{mensagem}

---
Esta mensagem foi enviada automaticamente através do formulário de contato do site MONPEC.
"""
        
        # Enviar email
        try:
            send_mail(
                subject=assunto,
                message=corpo_email,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['l.moncaosilva@gmail.com'],
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
{mensagem}

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
        
        messages.success(request, 'Mensagem enviada com sucesso! Redirecionando para a página de pagamento...')
        # Redirecionar para a página de pagamento da Hotmart
        return redirect('https://pay.hotmart.com/O102944551F')
    
    # Se não for POST, redirecionar para landing page
    return redirect('landing_page')

from .models import (
    ProdutorRural, Propriedade, CategoriaAnimal, InventarioRebanho, AnimalIndividual,
    ParametrosProjecaoRebanho, MovimentacaoProjetada,
    ConfiguracaoVenda, TransferenciaPropriedade, PoliticaVendasCategoria,
    SCRBancoCentral, DividaBanco, ContratoDivida, AmortizacaoContrato,
    ProjetoBancario, DocumentoProjeto
)
from .forms import (
    ProdutorRuralForm, PropriedadeForm, InventarioRebanhoForm,
    ParametrosProjecaoForm, MovimentacaoProjetadaForm, CategoriaAnimalForm
)


def login_view(request):
    """View para login do usuário com proteções de segurança"""
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
                f'⚠️ <strong>Bloqueio por tentativas:</strong> Após 5 tentativas falhas, o sistema bloqueia por 1 minuto. '
                f'Aguarde {minutos}min {segundos}s antes de tentar novamente. '
                f'Possíveis causas: senha incorreta, conta desativada ou e-mail não verificado.'
            )
            return render(request, 'gestao_rural/login_clean.html', {'mostrar_info_ajuda': True})
        
        # Verifica se o usuário existe antes de autenticar
        from django.contrib.auth.models import User
        try:
            usuario_existe = User.objects.filter(username=username).exists()
        except Exception as e:
            logger.error(f'Erro ao verificar usuário: {e}')
            messages.error(
                request, 
                '❌ Erro ao verificar credenciais. Por favor, tente novamente ou entre em contato com o suporte.'
            )
            return render(request, 'gestao_rural/login_clean.html')
        
        if not usuario_existe:
            registrar_tentativa_login_falha(username, ip_address)
            messages.error(
                request, 
                f'❌ <strong>Usuário não encontrado:</strong> O usuário "{username}" não existe no sistema. '
                f'Verifique se o nome de usuário está correto. <strong>Após 5 tentativas falhas, o sistema bloqueia por 1 minuto.</strong>'
            )
            registrar_log_auditoria(
                tipo_acao='LOGIN_FALHA',
                descricao=f"Tentativa de login com usuário inexistente: {username}",
                usuario=None,
                ip_address=ip_address,
                user_agent=user_agent,
                nivel_severidade='MEDIO',
                sucesso=False,
            )
            return render(request, 'gestao_rural/login_clean.html')
        
        # Tenta autenticar
        try:
            user = authenticate(request, username=username, password=password)
        except Exception as e:
            logger.error(f'Erro na autenticação: {e}')
            messages.error(
                request, 
                '❌ Erro ao processar autenticação. Por favor, tente novamente ou entre em contato com o suporte.'
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
                from .models_auditoria import VerificacaoEmail
                from django.db import OperationalError
                try:
                    verificacao = VerificacaoEmail.objects.get(usuario=user)
                    if not verificacao.email_verificado:
                        messages.warning(
                            request,
                            '⚠️ <strong>Verificação de e-mail pendente:</strong> Por favor, verifique seu e-mail antes de fazer login. '
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
                    
                    # Registrar sessão segura
                    registrar_sessao_segura(user, request.session.session_key, ip_address, user_agent)
                    
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
                    
                    # Redirecionar para a URL original (next) ou para o dashboard
                    next_url = request.GET.get('next') or request.POST.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('dashboard')
                except Exception as e:
                    logger.error(f'Erro após autenticação bem-sucedida: {e}')
                    messages.error(
                        request,
                        '⚠️ Login realizado, mas houve um erro ao iniciar a sessão. Por favor, tente novamente.'
                    )
                    return render(request, 'gestao_rural/login_clean.html')
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
    
    # Adicionar informações de ajuda no contexto
    from django.conf import settings
    context = {
        'mostrar_info_ajuda': True,
        'hotmart_checkout_url': getattr(settings, 'HOTMART_CHECKOUT_URL', 'https://pay.hotmart.com/SEU_CODIGO_AQUI'),
    }
    return render(request, 'gestao_rural/login_clean.html', context)


def logout_view(request):
    """View para logout do usuário - redireciona para landing page"""
    from .security_avancado import (
        registrar_log_auditoria,
        invalidar_sessao_segura,
        obter_ip_address,
    )
    
    usuario = request.user if request.user.is_authenticated else None
    ip_address = obter_ip_address(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Invalidar sessão segura
    if request.session.session_key:
        invalidar_sessao_segura(request.session.session_key)
    
    # Registrar log
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
    
    logout(request)
    messages.success(request, 'Você saiu do sistema com sucesso.')
    return redirect('landing_page')


@login_required
def dashboard(request):
    """Dashboard principal - lista de produtores"""
    produtores = ProdutorRural.objects.filter(usuario_responsavel=request.user)

    busca = request.GET.get('busca', '').strip()
    ordenar_por = request.GET.get('ordenar', 'nome')
    direcao = request.GET.get('direcao', 'asc')

    if busca:
        produtores = produtores.filter(
            Q(nome__icontains=busca) |
            Q(cpf_cnpj__icontains=busca) |
            Q(telefone__icontains=busca) |
            Q(email__icontains=busca) |
            Q(propriedade__nome_propriedade__icontains=busca) |
            Q(propriedade__municipio__icontains=busca) |
            Q(propriedade__uf__icontains=busca)
        ).distinct()

    produtores = produtores.annotate(
        total_propriedades=Count('propriedade', distinct=True),
        cidade_principal=Coalesce(Min('propriedade__municipio'), Value('')),
        estado_principal=Coalesce(Min('propriedade__uf'), Value('')),
        total_animais_produtor=Count(
            'propriedade__animais_individuais',
            filter=Q(
                propriedade__animais_individuais__numero_brinco__isnull=False,
            ) & ~Q(propriedade__animais_individuais__numero_brinco=''),
            distinct=True,
        ),
    )

    order_map = {
        'nome': 'nome',
        'cidade': 'cidade_principal',
        'estado': 'estado_principal',
        'propriedades': 'total_propriedades',
        'animais': 'total_animais_produtor',
        'data_cadastro': 'data_cadastro',
    }

    ordem = order_map.get(ordenar_por, 'nome')
    if direcao == 'desc':
        ordem = f'-{ordem}'

    produtores_ordenados = produtores.order_by(ordem, 'nome')

    total_produtores = produtores.count()
    total_propriedades = Propriedade.objects.filter(produtor__in=produtores.values('id')).count()
    total_animais = (
        AnimalIndividual.objects.filter(
            propriedade__produtor__in=produtores.values('id'),
            numero_brinco__isnull=False,
        )
        .exclude(numero_brinco='')
        .count()
    )

    paginator = Paginator(produtores_ordenados, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'produtores': page_obj.object_list,
        'page_obj': page_obj,
        'busca': busca,
        'ordenar_por': ordenar_por,
        'direcao': direcao,
        'total_produtores': total_produtores,
        'total_propriedades': total_propriedades,
        'total_animais': total_animais,
    }
    return render(request, 'gestao_rural/dashboard.html', context)


@login_required
def produtor_novo(request):
    """Cadastro de novo produtor rural"""
    if request.method == 'POST':
        form = ProdutorRuralForm(request.POST)
        if form.is_valid():
            produtor = form.save(commit=False)
            produtor.usuario_responsavel = request.user
            produtor.save()
            messages.success(request, 'Produtor cadastrado com sucesso!')
            return redirect('dashboard')
    else:
        form = ProdutorRuralForm()
    
    return render(request, 'gestao_rural/produtor_novo.html', {'form': form})


@login_required
def produtor_editar(request, produtor_id):
    """Edição de produtor rural"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = ProdutorRuralForm(request.POST, instance=produtor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produtor atualizado com sucesso!')
            return redirect('dashboard')
    else:
        form = ProdutorRuralForm(instance=produtor)
    
    return render(request, 'gestao_rural/produtor_editar.html', {'form': form, 'produtor': produtor})


@login_required
def produtor_excluir(request, produtor_id):
    """Exclusão de produtor rural"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    if request.method == 'POST':
        produtor.delete()
        messages.success(request, 'Produtor excluído com sucesso!')
        return redirect('dashboard')
    
    return render(request, 'gestao_rural/produtor_excluir.html', {'produtor': produtor})


@login_required
def propriedades_lista(request, produtor_id):
    """Lista de propriedades de um produtor"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    propriedades = Propriedade.objects.filter(produtor=produtor)
    
    context = {
        'produtor': produtor,
        'propriedades': propriedades,
    }
    return render(request, 'gestao_rural/propriedades_lista.html', context)


@login_required
def propriedade_nova(request, produtor_id):
    """Cadastro de nova propriedade"""
    produtor = get_object_or_404(ProdutorRural, id=produtor_id, usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = PropriedadeForm(request.POST)
        if form.is_valid():
            propriedade = form.save(commit=False)
            propriedade.produtor = produtor
            propriedade.save()
            messages.success(request, 'Propriedade cadastrada com sucesso!')
            return redirect('propriedades_lista', produtor_id=produtor.id)
    else:
        form = PropriedadeForm()
    
    context = {
        'form': form,
        'produtor': produtor,
    }
    return render(request, 'gestao_rural/propriedade_nova.html', context)


@login_required
def propriedade_editar(request, propriedade_id):
    """Edição de propriedade"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    if request.method == 'POST':
        form = PropriedadeForm(request.POST, instance=propriedade)
        if form.is_valid():
            form.save()
            messages.success(request, 'Propriedade atualizada com sucesso!')
            return redirect('propriedades_lista', produtor_id=propriedade.produtor.id)
    else:
        form = PropriedadeForm(instance=propriedade)
    
    context = {
        'form': form,
        'propriedade': propriedade,
    }
    return render(request, 'gestao_rural/propriedade_editar.html', context)


@login_required
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
                        
                        # Salvar ou atualizar
                        InventarioRebanho.objects.update_or_create(
                            propriedade=propriedade,
                            categoria=categoria,
                            data_inventario=data_inventario,
                            defaults={
                                'quantidade': quantidade,
                                'valor_por_cabeca': valor_por_cabeca
                            }
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
    
    # Buscar inventário mais recente de cada categoria
    inventario_dict = {}
    inventarios_recentes = InventarioRebanho.objects.filter(
        propriedade=propriedade,
        categoria__in=categorias
    ).select_related('categoria').order_by('categoria', '-data_inventario')
    
    # Agrupar por categoria, mantendo apenas o mais recente de cada uma
    for inv in inventarios_recentes:
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
    
    context = {
        'propriedade': propriedade,
        'categorias_com_inventario': categorias_com_inventario,
        'total_quantidade': total_quantidade,
        'total_valor': total_valor,
        'valor_medio': valor_medio,
        'tem_inventario': any(item['quantidade'] > 0 for item in categorias_com_inventario),
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
    
    parametros = ParametrosProjecaoRebanho.objects.filter(propriedade=propriedade).first()
    
    # Validações básicas
    if not inventario.exists():
        messages.error(request, 'É necessário cadastrar o inventário inicial primeiro.')
        return redirect('pecuaria_inventario', propriedade_id=propriedade.id)
    
    if not parametros:
        messages.error(request, 'É necessário configurar os parâmetros de projeção primeiro.')
        return redirect('pecuaria_parametros', propriedade_id=propriedade.id)
    
    # Processar POST - Gerar nova projeção
    if request.method == 'POST':
        try:
            anos_projecao = int(request.POST.get('anos_projecao', 5))
            
            if not (1 <= anos_projecao <= 20):
                messages.error(request, 'Número de anos deve estar entre 1 e 20.')
                return redirect('pecuaria_projecao', propriedade_id=propriedade.id)
            
            logger.info(f"Gerando projeção para {propriedade.nome_propriedade} - {anos_projecao} anos")
            gerar_projecao(propriedade, anos_projecao)
            
            # Invalidar cache
            cache.delete(f'projecao_{propriedade_id}')
            
            messages.success(request, f'Projeção gerada com sucesso para {anos_projecao} anos!')
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
        if movimentacoes:
            cache.set(cache_key, movimentacoes, 1800)
    
    # Processar dados da projeção
    resumo_projecao_por_ano = {}
    evolucao_detalhada = {}
    
    if movimentacoes:
        try:
            resumo_projecao_por_ano = gerar_resumo_projecao_por_ano(movimentacoes, inventario)
            evolucao_detalhada = gerar_evolucao_detalhada_rebanho(movimentacoes, inventario)
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
    
    total_geral = sum(item.quantidade for item in inventario)
    
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
    }
    
    return render(request, 'gestao_rural/pecuaria_projecao.html', context)


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


def gerar_projecao(propriedade, anos):
    """Função para gerar a projeção do rebanho com IA Inteligente"""
    from .ia_movimentacoes_automaticas import sistema_movimentacoes
    from django.db import transaction
    
    # Buscar inventário inicial
    inventario_inicial = InventarioRebanho.objects.filter(propriedade=propriedade)
    
    # Validações
    if not inventario_inicial.exists():
        raise ValueError(f"Inventário inicial não cadastrado para {propriedade.nome_propriedade}")
    
    try:
        parametros = ParametrosProjecaoRebanho.objects.get(propriedade=propriedade)
    except ParametrosProjecaoRebanho.DoesNotExist:
        raise ValueError(f"Parâmetros de projeção não configurados para {propriedade.nome_propriedade}")
    
    logger.info(f"Iniciando geração de projeção INTELIGENTE para {propriedade.nome_propriedade}")
    logger.info(f"Parâmetros: Natalidade={parametros.taxa_natalidade_anual}%, Mortalidade Bezerros={parametros.taxa_mortalidade_bezerros_anual}%, Mortalidade Adultos={parametros.taxa_mortalidade_adultos_anual}%")
    logger.info(f"Anos de projeção: {anos}")
    
    # Gerar movimentações com transação atômica
    with transaction.atomic():
        # Limpar projeções anteriores
        MovimentacaoProjetada.objects.filter(propriedade=propriedade).delete()
        
        # Usar sistema inteligente para gerar todas as movimentações
        movimentacoes = sistema_movimentacoes.gerar_movimentacoes_completas(
            propriedade, parametros, inventario_inicial, anos
        )
        
        # Salvar todas as movimentações no banco
        for movimentacao in movimentacoes:
            movimentacao.save()
    
    logger.info(f"Total de movimentações INTELIGENTES geradas e salvas: {len(movimentacoes)}")
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


def gerar_evolucao_detalhada_rebanho(movimentacoes, inventario_inicial):
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
                    valor_unitario = obter_valor_padrao_por_categoria(categoria_obj)
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


def gerar_resumo_projecao_por_ano(movimentacoes, inventario_inicial):
    """Gera resumo da projeção organizado por ano no mesmo formato da Evolução Detalhada"""
    from collections import defaultdict
    from datetime import datetime
    from .models import CategoriaAnimal
    
    # Buscar todas as categorias ativas
    todas_categorias = CategoriaAnimal.objects.filter(ativo=True).order_by('sexo', 'idade_minima_meses')
    nomes_categorias = [cat.nome for cat in todas_categorias]
    
    # Agrupar movimentações por ano
    movimentacoes_por_ano = defaultdict(list)
    for mov in movimentacoes:
        ano = mov.data_movimentacao.year
        movimentacoes_por_ano[ano].append(mov)
    
    # Inicializar com inventário inicial
    categorias_inicial = {}
    for item in inventario_inicial:
        categorias_inicial[item.categoria.nome] = item.quantidade
    
    # Gerar resumo detalhado para cada ano
    resumo_por_ano = {}
    saldos_finais_ano_anterior = {}  # Armazenar saldos finais do ano anterior
    
    for ano in sorted(movimentacoes_por_ano.keys()):
        movimentacoes_ano = movimentacoes_por_ano[ano]
        
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
            elif mov.tipo_movimentacao == 'TRANSFERENCIA_ENTRADA':
                if 'Promoção' in mov.observacao:
                    movimentacoes_por_categoria[categoria]['promocao_entrada'] += mov.quantidade
                else:
                    movimentacoes_por_categoria[categoria]['transferencias_entrada'] += mov.quantidade
            elif mov.tipo_movimentacao == 'TRANSFERENCIA_SAIDA':
                if 'Promoção' in mov.observacao:
                    movimentacoes_por_categoria[categoria]['promocao_saida'] += mov.quantidade
                else:
                    movimentacoes_por_categoria[categoria]['transferencias_saida'] += mov.quantidade
            elif mov.tipo_movimentacao == 'MORTE':
                movimentacoes_por_categoria[categoria]['mortes'] += mov.quantidade
        
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
                        valor_unitario = obter_valor_padrao_por_categoria(categoria_obj)
                    except CategoriaAnimal.DoesNotExist:
                        valor_unitario = Decimal('2000.00')  # Valor padrão genérico
            except (AttributeError, TypeError, ValueError, KeyError) as e:
                logging.warning(f"Erro ao calcular valor unitário para categoria {categoria_nome}: {e}")
                valor_unitario = Decimal('2000.00')  # Valor padrão genérico em caso de erro
            
            # Calcular valor total
            valor_total = valor_unitario * Decimal(str(saldo_final))
            
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
            
            # Armazenar saldo final para usar como saldo inicial do próximo ano
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
            
            # Buscar valor_por_cabeca do inventário (MovimentacaoProjetada não tem esse campo)
            try:
                inventario_item = InventarioRebanho.objects.filter(
                    propriedade=mov.propriedade,
                    categoria=mov.categoria
                ).first()
                
                valor_unitario = inventario_item.valor_por_cabeca if inventario_item and inventario_item.valor_por_cabeca else Decimal('0')
            except:
                valor_unitario = Decimal('0')
            
            valor_mov = Decimal(str(quantidade)) * Decimal(str(valor_unitario))
            
            if mov.tipo_movimentacao == 'VENDA':
                totais_ano['receitas_total'] += valor_mov
            elif mov.tipo_movimentacao in ['COMPRA', 'MORTE']:
                totais_ano['custos_total'] += valor_mov
        
        # Adicionar linha de totais
        resultado_ano['TOTAIS'] = {
            'saldo_inicial': totais_ano['saldo_inicial_total'],
            'nascimentos': totais_ano['nascimentos_total'],
            'compras': totais_ano['compras_total'],
            'vendas': totais_ano['vendas_total'],
            'transferencias_entrada': totais_ano['transferencias_entrada_total'],
            'transferencias_saida': totais_ano['transferencias_saida_total'],
            'mortes': totais_ano['mortes_total'],
            'evolucao_categoria': '-',
            'saldo_final': totais_ano['saldo_final_total'],
            'peso_medio_kg': Decimal('0.00'),
            'valor_unitario': Decimal('0.00'),
            'valor_total': totais_ano['valor_total_geral'],
            'receitas': totais_ano['receitas_total'],
            'custos': totais_ano['custos_total'],
            'lucro': totais_ano['receitas_total'] - totais_ano['custos_total'],
            'total_femeas': totais_ano['total_femeas'],
            'total_machos': totais_ano['total_machos'],
            'total_animais': totais_ano['saldo_final_total'],
        }
        
        resumo_por_ano[ano] = resultado_ano
    
    logger.debug(f"Resumo por ano processado para {len(resumo_por_ano)} anos")
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


def obter_valor_padrao_por_categoria(categoria):
    """Retorna valores padrão por categoria de animal"""
    from decimal import Decimal
    
    # Valores padrão baseados no mercado brasileiro (R$ por cabeça)
    valores_padrao = {
        'bezerro': Decimal('800.00'),      # 0-12 meses
        'bezerra': Decimal('1200.00'),     # 0-12 meses
        'garrote': Decimal('1800.00'),     # 12-24 meses
        'novilha': Decimal('2200.00'),     # 12-24 meses
        'boi': Decimal('2800.00'),         # 24-36 meses
        'boi_magro': Decimal('2500.00'),   # 24-36 meses (magro)
        'primipara': Decimal('3000.00'),   # 24-36 meses
        'multipara': Decimal('3500.00'),   # >36 meses
        'vaca_descarte': Decimal('2000.00'), # vacas de descarte
        'touro': Decimal('4000.00')        # reprodutores
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
            
            # Se não há valor configurado, usar valor padrão
            if valor_original == 0:
                valor_original = obter_valor_padrao_por_categoria(config.categoria_compra)
            
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
                    observacao=f'Compra automática (transferência cancelada por falta de saldo em {config.fazenda_origem.nome_propriedade})'
                )
                
                transferencias_processadas.append({
                    'origem': None,
                    'destino': propriedade_destino,
                    'categoria': categoria_origem,
                    'quantidade': config.quantidade_transferencia,
                    'data': data_referencia,
                    'tipo': 'COMPRA'
                })
                
                print(f"[OK] Compra automatica criada: {propriedade_destino.nome_propriedade} (+{config.quantidade_transferencia} {categoria_origem.nome})")
        else:
            print(f"AVISO: Não é o momento da transferência")
    
    print(f"Total de transferências processadas: {len(transferencias_processadas)}")
    return transferencias_processadas


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
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    projetos = ProjetoBancario.objects.filter(propriedade=propriedade).order_by('-data_solicitacao')
    
    # Calcular estatísticas
    total_solicitado = sum(projeto.valor_solicitado for projeto in projetos)
    total_aprovado = sum(projeto.valor_aprovado or 0 for projeto in projetos)
    projetos_aprovados = projetos.filter(status='APROVADO').count()
    
    context = {
        'propriedade': propriedade,
        'projetos': projetos,
        'total_solicitado': total_solicitado,
        'total_aprovado': total_aprovado,
        'projetos_aprovados': projetos_aprovados,
    }
    
    return render(request, 'gestao_rural/projeto_bancario_dashboard.html', context)


@login_required
def projeto_bancario_novo(request, propriedade_id):
    """Criar novo projeto bancário"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    from .forms_projetos import ProjetoBancarioForm
    if request.method == 'POST':
        form = ProjetoBancarioForm(request.POST, request.FILES)
        if form.is_valid():
            projeto = form.save(commit=False)
            projeto.propriedade = propriedade
            if not projeto.status:
                projeto.status = 'RASCUNHO'
            projeto.save()
            messages.success(request, 'Projeto bancário criado com sucesso!')
            return redirect('projeto_bancario_dashboard', propriedade_id=propriedade.id)
        else:
            messages.error(request, 'Corrija os erros do formulário.')
    else:
        form = ProjetoBancarioForm()
    
    return render(request, 'gestao_rural/projeto_bancario_novo.html', {'propriedade': propriedade, 'form': form})


@login_required
def projeto_bancario_detalhes(request, propriedade_id, projeto_id):
    """Detalhes do projeto bancário"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    projeto = get_object_or_404(ProjetoBancario, id=projeto_id, propriedade=propriedade)
    
    documentos = DocumentoProjeto.objects.filter(projeto=projeto)
    
    context = {
        'propriedade': propriedade,
        'projeto': projeto,
        'documentos': documentos,
    }
    
    return render(request, 'gestao_rural/projeto_bancario_detalhes.html', context)


@login_required
def projeto_bancario_editar(request, propriedade_id, projeto_id):
    """Editar projeto bancário"""
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    projeto = get_object_or_404(ProjetoBancario, id=projeto_id, propriedade=propriedade)
    
    from .forms_projetos import ProjetoBancarioForm
    if request.method == 'POST':
        form = ProjetoBancarioForm(request.POST, request.FILES, instance=projeto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projeto bancário atualizado com sucesso!')
            return redirect('projeto_bancario_detalhes', propriedade_id=propriedade.id, projeto_id=projeto.id)
        else:
            messages.error(request, 'Corrija os erros do formulário.')
    else:
        form = ProjetoBancarioForm(instance=projeto)
    
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
        return JsonResponse({
            'error': str(e),
            'valor_por_cabeca': 0.0
        }, status=400)


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
    propriedade = get_object_or_404(Propriedade, id=propriedade_id, produtor__usuario_responsavel=request.user)
    
    total_animais = (
        InventarioRebanho.objects
        .filter(propriedade=propriedade)
        .aggregate(total=Sum('quantidade'))
        .get('total') or 0
    )
    
    context = {
        'propriedade': propriedade,
        'total_animais': total_animais,
    }
    
    return render(request, 'propriedade_modulos.html', context)

