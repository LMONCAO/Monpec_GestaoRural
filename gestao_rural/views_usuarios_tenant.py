from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms_usuarios import TenantUsuarioForm
from .models import TenantUsuario
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
        return redirect("dashboard")

    assinatura = tenant_access.obter_assinatura_do_usuario(request.user)
    if not assinatura:
        messages.error(request, "Nenhuma assinatura ativa vinculada ao usuário.")
        return redirect("assinaturas_dashboard")

    usuarios = assinatura.usuarios_tenant.select_related("usuario").order_by("nome_exibicao")
    form = TenantUsuarioForm(initial={"modulos": assinatura.modulos_disponiveis})

    if request.method == "POST":
        form = TenantUsuarioForm(request.POST)
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
                    senha_definida=form.cleaned_data["senha_temporaria"] or None,
                    criado_por=request.user,
                )
                
                # Criar verificação de e-mail para novo usuário
                if not resultado.usuario.is_active:
                    verificacao = criar_verificacao_email(resultado.usuario)
                    enviar_email_verificacao(resultado.usuario, verificacao)
                    resultado.usuario.is_active = False  # Inativo até verificar e-mail
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
                msg = "Usuário salvo com sucesso."
                if resultado.senha_temporaria:
                    msg += f" Senha temporária: {resultado.senha_temporaria}"
                if not resultado.usuario.is_active:
                    msg += " E-mail de verificação enviado. O usuário precisa verificar o e-mail para ativar a conta."
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



