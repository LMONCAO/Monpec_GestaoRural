"""
Views para o módulo de Marketing - Geração de Posts e Captura de Leads
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
import json

from .models_marketing import (
    TemplatePost, PostGerado, LeadInteressado, CampanhaMarketing, ConfiguracaoMarketing
)
from .gerador_posts import GeradorPosts, popular_templates_iniciais
from .forms_marketing import (
    TemplatePostForm, PostGeradoForm, LeadForm, CampanhaForm, ConfiguracaoMarketingForm,
    GerarPostForm
)


@login_required
def marketing_dashboard(request):
    """Dashboard principal do módulo de marketing"""
    
    # Estatísticas
    total_leads = LeadInteressado.objects.count()
    leads_novos = LeadInteressado.objects.filter(status='novo').count()
    total_posts = PostGerado.objects.count()
    posts_pendentes = PostGerado.objects.filter(status='rascunho').count()
    
    # Posts recentes
    posts_recentes = PostGerado.objects.order_by('-criado_em')[:5]
    
    # Leads recentes
    leads_recentes = LeadInteressado.objects.order_by('-criado_em')[:5]
    
    # Templates disponíveis
    total_templates = TemplatePost.objects.filter(ativo=True).count()
    
    # Verificar se precisa popular templates
    if total_templates == 0:
        messages.info(request, "Nenhum template encontrado. Clique em 'Popular Templates' para criar templates iniciais.")
    
    context = {
        'total_leads': total_leads,
        'leads_novos': leads_novos,
        'total_posts': total_posts,
        'posts_pendentes': posts_pendentes,
        'posts_recentes': posts_recentes,
        'leads_recentes': leads_recentes,
        'total_templates': total_templates,
    }
    
    return render(request, 'gestao_rural/marketing/dashboard.html', context)


@login_required
def templates_list(request):
    """Lista de templates de posts"""
    templates = TemplatePost.objects.all().order_by('-criado_em')
    
    # Filtros
    tipo_post = request.GET.get('tipo_post')
    rede_social = request.GET.get('rede_social')
    ativo = request.GET.get('ativo')
    
    if tipo_post:
        templates = templates.filter(tipo_post=tipo_post)
    if rede_social:
        templates = templates.filter(rede_social=rede_social)
    if ativo:
        templates = templates.filter(ativo=ativo == 'true')
    
    context = {
        'templates': templates,
        'tipos_post': TemplatePost.TIPO_POST_CHOICES,
        'redes_sociais': TemplatePost.REDE_SOCIAL_CHOICES,
    }
    
    return render(request, 'gestao_rural/marketing/templates_list.html', context)


@login_required
def template_create(request):
    """Criar novo template"""
    if request.method == 'POST':
        form = TemplatePostForm(request.POST)
        if form.is_valid():
            template = form.save()
            messages.success(request, f'Template "{template.nome}" criado com sucesso!')
            return redirect('marketing_template_edit', template_id=template.id)
    else:
        form = TemplatePostForm()
    
    return render(request, 'gestao_rural/marketing/template_form.html', {'form': form})


@login_required
def template_edit(request, template_id):
    """Editar template"""
    template = get_object_or_404(TemplatePost, id=template_id)
    
    if request.method == 'POST':
        form = TemplatePostForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, 'Template atualizado com sucesso!')
            return redirect('marketing_templates')
    else:
        form = TemplatePostForm(instance=template)
    
    context = {
        'form': form,
        'template': template,
        'variaveis_disponiveis': GeradorPosts.VARIAVEIS_PADRAO,
    }
    
    return render(request, 'gestao_rural/marketing/template_form.html', context)


@login_required
@require_POST
def template_delete(request, template_id):
    """Deletar template"""
    template = get_object_or_404(TemplatePost, id=template_id)
    template.delete()
    messages.success(request, 'Template deletado com sucesso!')
    return redirect('marketing_templates')


@login_required
@require_POST
def popular_templates(request):
    """Popular templates iniciais"""
    try:
        criados = popular_templates_iniciais()
        messages.success(request, f'{criados} templates iniciais criados com sucesso!')
    except Exception as e:
        messages.error(request, f'Erro ao popular templates: {str(e)}')
    
    return redirect('marketing_templates')


@login_required
def posts_list(request):
    """Lista de posts gerados"""
    posts = PostGerado.objects.all().order_by('-criado_em')
    
    # Filtros
    status = request.GET.get('status')
    tipo_post = request.GET.get('tipo_post')
    rede_social = request.GET.get('rede_social')
    
    if status:
        posts = posts.filter(status=status)
    if tipo_post:
        posts = posts.filter(tipo_post=tipo_post)
    if rede_social:
        posts = posts.filter(rede_social=rede_social)
    
    context = {
        'posts': posts,
        'status_choices': PostGerado.STATUS_CHOICES,
        'tipos_post': TemplatePost.TIPO_POST_CHOICES,
        'redes_sociais': TemplatePost.REDE_SOCIAL_CHOICES,
    }
    
    return render(request, 'gestao_rural/marketing/posts_list.html', context)


@login_required
def gerar_post(request):
    """Gerar novo post"""
    if request.method == 'POST':
        form = GerarPostForm(request.POST)
        if form.is_valid():
            try:
                gerador = GeradorPosts()
                
                template_id = form.cleaned_data.get('template')
                variaveis_extras = form.cleaned_data.get('variaveis_extras')
                rede_social = form.cleaned_data.get('rede_social', 'geral')
                
                if template_id:
                    post = gerador.gerar_post(
                        template_id=template_id.id,
                        variaveis_extras=variaveis_extras,
                        rede_social=rede_social,
                        usuario=request.user
                    )
                else:
                    tipo_post = form.cleaned_data.get('tipo_post')
                    post = gerador.gerar_post_aleatorio(
                        tipo_post=tipo_post,
                        rede_social=rede_social,
                        usuario=request.user
                    )
                
                messages.success(request, 'Post gerado com sucesso!')
                return redirect('marketing_post_edit', post_id=post.id)
            except Exception as e:
                messages.error(request, f'Erro ao gerar post: {str(e)}')
    else:
        form = GerarPostForm()
    
    context = {
        'form': form,
        'templates': TemplatePost.objects.filter(ativo=True),
    }
    
    return render(request, 'gestao_rural/marketing/gerar_post.html', context)


@login_required
def post_edit(request, post_id):
    """Editar post gerado"""
    post = get_object_or_404(PostGerado, id=post_id)
    
    if request.method == 'POST':
        form = PostGeradoForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post atualizado com sucesso!')
            
            # Se mudou status para publicado, atualizar data
            if post.status == 'publicado' and not post.publicado_em:
                post.publicado_em = timezone.now()
                post.save()
            
            return redirect('marketing_posts')
    else:
        form = PostGeradoForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
    }
    
    return render(request, 'gestao_rural/marketing/post_form.html', context)


@login_required
@require_POST
def post_delete(request, post_id):
    """Deletar post"""
    post = get_object_or_404(PostGerado, id=post_id)
    post.delete()
    messages.success(request, 'Post deletado com sucesso!')
    return redirect('marketing_posts')


@login_required
def gerar_posts_semana(request):
    """Gerar posts para a semana"""
    if request.method == 'POST':
        try:
            gerador = GeradorPosts()
            posts = gerador.gerar_posts_semana(usuario=request.user)
            messages.success(request, f'{len(posts)} posts gerados para a semana!')
            return redirect('marketing_posts')
        except Exception as e:
            messages.error(request, f'Erro ao gerar posts: {str(e)}')
    
    return render(request, 'gestao_rural/marketing/gerar_posts_semana.html')


# ========== LANDING PAGE E LEADS ==========

def landing_page_gratuita(request):
    """Landing page para captura de leads - Acesso gratuito"""
    config = ConfiguracaoMarketing.get_config()
    
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            
            # Capturar IP e User Agent
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                lead.ip_address = x_forwarded_for.split(',')[0]
            else:
                lead.ip_address = request.META.get('REMOTE_ADDR')
            
            lead.user_agent = request.META.get('HTTP_USER_AGENT', '')
            lead.origem = 'landing_page_gratuita'
            lead.save()
            
            # Criar usuário com acesso gratuito (se configurado)
            if config.ativar_acesso_gratuito:
                try:
                    # Verificar se usuário já existe
                    usuario, criado = User.objects.get_or_create(
                        email=lead.email,
                        defaults={
                            'username': lead.email,
                            'first_name': lead.nome.split()[0] if lead.nome.split() else '',
                            'last_name': ' '.join(lead.nome.split()[1:]) if len(lead.nome.split()) > 1 else '',
                            'is_active': True,
                        }
                    )
                    
                    if criado:
                        # Gerar senha temporária
                        senha_temporaria = User.objects.make_random_password(length=12)
                        usuario.set_password(senha_temporaria)
                        usuario.save()
                        
                        # Enviar email com credenciais
                        enviar_credenciais_gratuitas(lead, usuario, senha_temporaria)
                        lead.credenciais_enviadas = True
                        lead.credenciais_enviadas_em = timezone.now()
                        lead.save()
                except Exception as e:
                    # Log erro mas não impede o cadastro do lead
                    print(f"Erro ao criar usuário: {e}")
            
            messages.success(
                request,
                'Cadastro realizado com sucesso! Verifique seu email para acessar o sistema gratuitamente.'
            )
            return redirect('landing_page_sucesso')
    else:
        form = LeadForm()
    
    context = {
        'form': form,
        'config': config,
        'beneficios': [
            'Gestão completa do rebanho',
            'Controle financeiro (DRE, Fluxo de Caixa)',
            'Projeções inteligentes com IA',
            'Relatórios profissionais',
            'Rastreabilidade completa (PNIB)',
        ]
    }
    
    return render(request, 'gestao_rural/marketing/landing_page_gratuita.html', context)


def landing_page_sucesso(request):
    """Página de sucesso após cadastro"""
    config = ConfiguracaoMarketing.get_config()
    
    return render(request, 'gestao_rural/marketing/landing_page_sucesso.html', {
        'config': config,
    })


def enviar_credenciais_gratuitas(lead: LeadInteressado, usuario: User, senha: str):
    """Envia email com credenciais de acesso gratuito"""
    config = ConfiguracaoMarketing.get_config()
    
    assunto = "Acesso Gratuito ao MONPEC - Gestão Rural Inteligente"
    
    mensagem_texto = f"""
Olá {lead.nome},

Parabéns! Seu cadastro foi realizado com sucesso.

Você agora tem acesso GRATUITO ao MONPEC - Sistema de Gestão Rural Inteligente.

SUAS CREDENCIAIS DE ACESSO:
Email: {usuario.email}
Senha: {senha}

ACESSE AGORA:
{config.url_site}

IMPORTANTE:
- Guarde estas credenciais com segurança
- Recomendamos alterar a senha após o primeiro acesso
- Um de nossos consultores entrará em contato em breve

Explore todas as funcionalidades do sistema e descubra como podemos ajudar você a transformar sua gestão rural!

Atenciosamente,
Equipe MONPEC
"""
    
    mensagem_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f8f9fa;
            padding: 30px;
            border: 1px solid #dee2e6;
        }}
        .credentials {{
            background-color: white;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #28a745;
            border-radius: 5px;
        }}
        .button {{
            display: inline-block;
            background-color: #28a745;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MONPEC - Gestão Rural Inteligente</h1>
        <p>Acesso Gratuito Ativado!</p>
    </div>
    
    <div class="content">
        <p>Olá <strong>{lead.nome}</strong>,</p>
        
        <p>Parabéns! Seu cadastro foi realizado com sucesso.</p>
        
        <p>Você agora tem acesso <strong>GRATUITO</strong> ao MONPEC - Sistema de Gestão Rural Inteligente.</p>
        
        <div class="credentials">
            <h3 style="color: #28a745; margin-top: 0;">🔐 SUAS CREDENCIAIS DE ACESSO</h3>
            <p><strong>Email:</strong> {usuario.email}</p>
            <p><strong>Senha:</strong> {senha}</p>
        </div>
        
        <div style="text-align: center;">
            <a href="{config.url_site}" class="button">Acessar Sistema Agora</a>
        </div>
        
        <p><strong>⚠️ IMPORTANTE:</strong></p>
        <ul>
            <li>Guarde estas credenciais com segurança</li>
            <li>Recomendamos alterar a senha após o primeiro acesso</li>
            <li>Um de nossos consultores entrará em contato em breve</li>
        </ul>
        
        <p>Explore todas as funcionalidades do sistema e descubra como podemos ajudar você a transformar sua gestão rural!</p>
        
        <p>Atenciosamente,<br>
        <strong>Equipe MONPEC</strong></p>
    </div>
</body>
</html>
"""
    
    remetente = getattr(settings, 'DEFAULT_FROM_EMAIL', config.email_contato)
    
    try:
        send_mail(
            subject=assunto,
            message=mensagem_texto,
            from_email=remetente,
            recipient_list=[lead.email],
            html_message=mensagem_html,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erro ao enviar email: {e}")


@login_required
def leads_list(request):
    """Lista de leads"""
    leads = LeadInteressado.objects.all().order_by('-criado_em')
    
    # Filtros
    status = request.GET.get('status')
    origem = request.GET.get('origem')
    busca = request.GET.get('busca')
    
    if status:
        leads = leads.filter(status=status)
    if origem:
        leads = leads.filter(origem=origem)
    if busca:
        leads = leads.filter(
            Q(nome__icontains=busca) |
            Q(email__icontains=busca) |
            Q(propriedade_nome__icontains=busca)
        )
    
    # Estatísticas
    total_leads = LeadInteressado.objects.count()
    por_status = LeadInteressado.objects.values('status').annotate(
        total=Count('id')
    )
    
    context = {
        'leads': leads,
        'status_choices': LeadInteressado.STATUS_CHOICES,
        'total_leads': total_leads,
        'por_status': por_status,
    }
    
    return render(request, 'gestao_rural/marketing/leads_list.html', context)


@login_required
def lead_detail(request, lead_id):
    """Detalhes do lead"""
    lead = get_object_or_404(LeadInteressado, id=lead_id)
    
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead atualizado com sucesso!')
            return redirect('marketing_leads')
    else:
        form = LeadForm(instance=lead)
    
    context = {
        'lead': lead,
        'form': form,
    }
    
    return render(request, 'gestao_rural/marketing/lead_detail.html', context)


@login_required
def configuracao_marketing(request):
    """Configurações gerais de marketing"""
    config = ConfiguracaoMarketing.get_config()
    
    if request.method == 'POST':
        form = ConfiguracaoMarketingForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações atualizadas com sucesso!')
            return redirect('marketing_configuracao')
    else:
        form = ConfiguracaoMarketingForm(instance=config)
    
    context = {
        'form': form,
        'config': config,
    }
    
    return render(request, 'gestao_rural/marketing/configuracao.html', context)



