from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms_usuarios import TenantUsuarioForm, TenantUsuarioUpdateForm
from .models import TenantUsuario, PlanoAssinatura
from .services import tenant_access
from .security_avancado import (
    validar_criacao_usuario_segura,
    criar_verificacao_email,
    enviar_email_verificacao,
    registrar_log_auditoria,
    obter_ip_address,
)


def _validar_habilitacao(request):
    if not tenant_access.usuario_eh_admin(request.user):
        messages.error(request, "Apenas administradores podem gerenciar usuários do sistema.")
        return False
    return True


@login_required
def tenant_usuarios_dashboard(request):
    if not _validar_habilitacao(request):
        # Redirecionar para a página atual (propriedade_modulos) se estiver em uma propriedade
        # ou para dashboard se não estiver
        if hasattr(request, 'resolver_match') and 'propriedade' in request.path:
            # Extrair propriedade_id da URL atual se possível
            try:
                propriedade_id = request.resolver_match.kwargs.get('propriedade_id')
                if propriedade_id:
                    return redirect('propriedade_modulos', propriedade_id=propriedade_id)
            except:
                pass
        return redirect("dashboard")

    assinatura = tenant_access.obter_assinatura_do_usuario(request.user)
    if not assinatura:
        messages.error(request, "Nenhuma assinatura ativa vinculada ao usuário.")
        return redirect("assinaturas_dashboard")

    usuarios = assinatura.usuarios_tenant.select_related("usuario").order_by("nome_exibicao")
    
    # Criar choices dos módulos com labels amigáveis
    modulos_labels = {
        'pecuaria': 'Pecuária',
        'financeiro': 'Financeiro',
        'projetos': 'Projetos',
        'compras': 'Compras',
        'funcionarios': 'Funcionários',
        'rastreabilidade': 'Rastreabilidade',
        'reproducao': 'Reprodução',
        'relatorios': 'Relatórios',
    }
    modulos_choices = [(mod, modulos_labels.get(mod, mod.replace('_', ' ').title())) 
                      for mod in PlanoAssinatura.MODULOS_PADRAO 
                      if mod in assinatura.modulos_disponiveis]
    
    form = TenantUsuarioForm(initial={"modulos": assinatura.modulos_disponiveis}, 
                           modulos_choices=modulos_choices)

    if request.method == "POST":
        form = TenantUsuarioForm(request.POST, modulos_choices=modulos_choices)
        if form.is_valid():
            # Validações de segurança
            ip_address = obter_ip_address(request)
            email = form.cleaned_data["email"]
            
            pode_criar, mensagem = validar_criacao_usuario_segura(
                criado_por=request.user,
                email=email,
                assinatura_id=assinatura.id,
                ip_address=ip_address,
            )
            
            if not pode_criar:
                messages.error(request, mensagem)
                return redirect("tenant_usuarios_dashboard")
            
            try:
                resultado = tenant_access.criar_ou_atualizar_usuario(
                    assinatura=assinatura,
                    nome=form.cleaned_data["nome"],
                    email=email,
                    perfil=form.cleaned_data["perfil"],
                    modulos=form.cleaned_data["modulos"],
                    senha_definida=form.cleaned_data.get("senha") or None,
                    username=form.cleaned_data.get("username") or None,
                    criado_por=request.user,
                )
                
                # Garantir que o usuário esteja ativo (admin cria usuários já ativos)
                if not resultado.usuario.is_active:
                    resultado.usuario.is_active = True
                    resultado.usuario.save()
                
                # Registrar log
                registrar_log_auditoria(
                    tipo_acao='CRIAR_USUARIO',
                    descricao=f"Usuário criado: {resultado.usuario.email}",
                    usuario=request.user,
                    ip_address=ip_address,
                    nivel_severidade='MEDIO',
                    metadata={
                        'usuario_criado_id': resultado.usuario.id,
                        'email': email,
                        'perfil': form.cleaned_data["perfil"],
                    },
                )
                
            except tenant_access.TenantAccessError as exc:
                registrar_log_auditoria(
                    tipo_acao='CRIAR_USUARIO',
                    descricao=f"Erro ao criar usuário: {exc}",
                    usuario=request.user,
                    ip_address=ip_address,
                    nivel_severidade='ALTO',
                    sucesso=False,
                    erro=str(exc),
                )
                messages.error(request, str(exc))
            else:
                msg = f"✅ Usuário <strong>{resultado.usuario.email}</strong> criado com sucesso!"
                msg += f"<br><strong>👤 Username:</strong> <code style='background: #f0f0f0; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 1.1em;'>{resultado.usuario.username}</code>"
                if resultado.senha_temporaria:
                    msg += f"<br><strong>🔑 Senha: <code style='background: #f0f0f0; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 1.1em;'>{resultado.senha_temporaria}</code></strong>"
                    msg += "<br><small class='text-muted'>⚠️ Anote esta senha! Ela será necessária para o primeiro login.</small>"
                messages.success(request, msg)
                return redirect("tenant_usuarios_dashboard")

    contexto = {
        "assinatura": assinatura,
        "usuarios": usuarios,
        "form": form,
        "limite_total": assinatura.plano.max_usuarios if assinatura.plano else None,
        "total_utilizado": assinatura.usuarios_ativos,
    }
    return render(request, "gestao_rural/tenant_usuarios.html", contexto)


@login_required
def tenant_usuario_toggle(request, usuario_id: int, acao: str):
    if request.method != "POST":
        return redirect("tenant_usuarios_dashboard")
    if not _validar_habilitacao(request):
        return redirect("dashboard")

    assinatura = tenant_access.obter_assinatura_do_usuario(request.user)
    tenant_usuario = get_object_or_404(TenantUsuario, id=usuario_id, assinatura=assinatura)

    try:
        if acao == "desativar":
            tenant_access.desativar_usuario(tenant_usuario)
            messages.info(request, f"{tenant_usuario.nome_exibicao} desativado.")
        elif acao == "reativar":
            tenant_access.reativar_usuario(tenant_usuario)
            messages.success(request, f"{tenant_usuario.nome_exibicao} reativado.")
        else:
            messages.warning(request, "Ação inválida.")
    except tenant_access.TenantAccessError as exc:
        messages.error(request, str(exc))

    return redirect("tenant_usuarios_dashboard")


@login_required
def tenant_usuario_configurar_modulos(request, usuario_id: int):
    """View para configurar módulos de um usuário específico"""
    if not _validar_habilitacao(request):
        return redirect("dashboard")
    
    assinatura = tenant_access.obter_assinatura_do_usuario(request.user)
    tenant_usuario = get_object_or_404(TenantUsuario, id=usuario_id, assinatura=assinatura)
    
    # Obter módulos disponíveis no plano
    modulos_disponiveis = assinatura.modulos_disponiveis
    # Criar lista de módulos com labels mais amigáveis
    modulos_labels = {
        'pecuaria': 'Pecuária',
        'financeiro': 'Financeiro',
        'projetos': 'Projetos',
        'compras': 'Compras',
        'funcionarios': 'Funcionários',
        'rastreabilidade': 'Rastreabilidade',
        'reproducao': 'Reprodução',
        'relatorios': 'Relatórios',
    }
    modulos_choices = [(mod, modulos_labels.get(mod, mod.replace('_', ' ').title())) for mod in PlanoAssinatura.MODULOS_PADRAO if mod in modulos_disponiveis]
    
    if request.method == "POST":
        modulos_selecionados = request.POST.getlist('modulos')
        
        try:
            tenant_usuario.atualizar_modulos(modulos_selecionados)
            
            # Registrar log
            registrar_log_auditoria(
                tipo_acao='CONFIGURAR_MODULOS_USUARIO',
                descricao=f"Módulos configurados para {tenant_usuario.nome_exibicao}: {', '.join(modulos_selecionados)}",
                usuario=request.user,
                ip_address=obter_ip_address(request),
                nivel_severidade='MEDIO',
                metadata={
                    'usuario_configurado_id': tenant_usuario.id,
                    'modulos': modulos_selecionados,
                },
            )
            
            messages.success(request, f"Módulos de {tenant_usuario.nome_exibicao} atualizados com sucesso.")
            return redirect("tenant_usuarios_dashboard")
        except Exception as e:
            messages.error(request, f"Erro ao atualizar módulos: {str(e)}")
    
    contexto = {
        "tenant_usuario": tenant_usuario,
        "modulos_choices": modulos_choices,
        "modulos_selecionados": tenant_usuario.modulos if tenant_usuario.perfil != TenantUsuario.Perfil.ADMIN else modulos_disponiveis,
        "eh_admin": tenant_usuario.perfil == TenantUsuario.Perfil.ADMIN,
    }
    return render(request, "gestao_rural/tenant_usuario_configurar_modulos.html", contexto)


@login_required
def tenant_usuario_editar(request, usuario_id: int):
    """View para editar um usuário existente"""
    if not _validar_habilitacao(request):
        return redirect("dashboard")
    
    assinatura = tenant_access.obter_assinatura_do_usuario(request.user)
    tenant_usuario = get_object_or_404(TenantUsuario, id=usuario_id, assinatura=assinatura)
    
    # Criar choices dos módulos
    modulos_labels = {
        'pecuaria': 'Pecuária',
        'financeiro': 'Financeiro',
        'projetos': 'Projetos',
        'compras': 'Compras',
        'funcionarios': 'Funcionários',
        'rastreabilidade': 'Rastreabilidade',
        'reproducao': 'Reprodução',
        'relatorios': 'Relatórios',
    }
    modulos_choices = [(mod, modulos_labels.get(mod, mod.replace('_', ' ').title())) 
                      for mod in PlanoAssinatura.MODULOS_PADRAO 
                      if mod in assinatura.modulos_disponiveis]
    
    if request.method == "POST":
        form = TenantUsuarioForm(request.POST, modulos_choices=modulos_choices)
        if form.is_valid():
            try:
                # Atualizar dados do usuário
                tenant_usuario.usuario.first_name = form.cleaned_data["nome"].split(" ")[0][:30]
                tenant_usuario.usuario.last_name = " ".join(form.cleaned_data["nome"].split(" ")[1:])[:150]
                tenant_usuario.usuario.email = form.cleaned_data["email"]
                
                # Atualizar username se fornecido
                username = form.cleaned_data.get("username")
                if username and username != tenant_usuario.usuario.username:
                    if User.objects.filter(username=username).exclude(id=tenant_usuario.usuario.id).exists():
                        messages.error(request, f"O username '{username}' já está em uso.")
                        return redirect("tenant_usuario_editar", usuario_id=usuario_id)
                    tenant_usuario.usuario.username = username
                
                # Atualizar senha se fornecida
                senha = form.cleaned_data.get("senha")
                if senha:
                    tenant_usuario.usuario.set_password(senha)
                
                tenant_usuario.usuario.save()
                
                # Atualizar perfil
                tenant_usuario.perfil = form.cleaned_data["perfil"]
                tenant_usuario.nome_exibicao = form.cleaned_data["nome"]
                tenant_usuario.email = form.cleaned_data["email"]
                
                # Atualizar módulos (exceto se for admin)
                if tenant_usuario.perfil != TenantUsuario.Perfil.ADMIN:
                    tenant_usuario.modulos = form.cleaned_data["modulos"]
                
                tenant_usuario.save()
                
                # Registrar log
                registrar_log_auditoria(
                    tipo_acao='EDITAR_USUARIO',
                    descricao=f"Usuário editado: {tenant_usuario.usuario.email}",
                    usuario=request.user,
                    ip_address=obter_ip_address(request),
                    nivel_severidade='MEDIO',
                    metadata={
                        'usuario_editado_id': tenant_usuario.id,
                        'email': form.cleaned_data["email"],
                        'perfil': form.cleaned_data["perfil"],
                    },
                )
                
                messages.success(request, f"Usuário <strong>{tenant_usuario.nome_exibicao}</strong> atualizado com sucesso!")
                return redirect("tenant_usuarios_dashboard")
            except Exception as e:
                messages.error(request, f"Erro ao atualizar usuário: {str(e)}")
    else:
        # Preencher form com dados atuais
        form = TenantUsuarioForm(
            initial={
                "nome": tenant_usuario.nome_exibicao,
                "username": tenant_usuario.usuario.username,
                "email": tenant_usuario.email,
                "perfil": tenant_usuario.perfil,
                "modulos": tenant_usuario.modulos if tenant_usuario.perfil != TenantUsuario.Perfil.ADMIN else assinatura.modulos_disponiveis,
            },
            modulos_choices=modulos_choices
        )
    
    contexto = {
        "tenant_usuario": tenant_usuario,
        "form": form,
        "assinatura": assinatura,
        "modulos_disponiveis": assinatura.modulos_disponiveis,
    }
    return render(request, "gestao_rural/tenant_usuario_editar.html", contexto)


