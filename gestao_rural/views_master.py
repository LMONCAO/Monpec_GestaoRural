from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import AssinaturaCliente, MasterAccessLog, TenantWorkspace, UsuarioMaster

User = get_user_model()


def _registrar_log(master: UsuarioMaster, acao: str, request, assinatura: AssinaturaCliente | None = None):
    workspace = getattr(assinatura, "workspace", None) if assinatura else None
    MasterAccessLog.objects.create(
        master=master,
        assinatura=assinatura,
        workspace=workspace,
        acao=acao,
        ip_origem=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
    )


def _obter_master(request) -> UsuarioMaster | None:
    usuario = request.user
    return getattr(usuario, "master_account", None)


def master_login(request):
    if request.user.is_authenticated and request.session.get("master_mode"):
        return redirect("master_tenants_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        token = request.POST.get("token")

        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, "Credenciais inválidas.")
        else:
            master = getattr(user, "master_account", None)
            if not master:
                messages.error(request, "Usuário não autorizado como master.")
            elif not token or not master.validar_chave(token):
                messages.error(request, "Token master inválido.")
            else:
                login(request, user)
                request.session["master_mode"] = True
                request.session["master_id"] = master.id
                _registrar_log(master, "LOGIN_MASTER", request)
                messages.success(request, "Acesso master liberado.")
                return redirect("master_tenants_dashboard")

    return render(request, "gestao_rural/master_login.html")


@login_required
def master_tenants_dashboard(request):
    master = _obter_master(request)
    if not master or not request.session.get("master_mode"):
        messages.error(request, "Ative o modo master para continuar.")
        return redirect("master_login")

    workspaces = TenantWorkspace.objects.select_related("assinatura", "assinatura__usuario").order_by("-criado_em")
    contexto = {
        "workspaces": workspaces,
    }
    return render(request, "gestao_rural/master_tenants.html", contexto)


@login_required
def master_impersonar(request, assinatura_id: int):
    master = _obter_master(request)
    if not master:
        messages.error(request, "Apenas usuários master podem executar esta ação.")
        return redirect("dashboard")

    assinatura = get_object_or_404(
        AssinaturaCliente.objects.select_related("usuario"), id=assinatura_id
    )
    destino_user = assinatura.usuario
    master_user_id = request.user.id
    master_mode_flag = request.session.get("master_mode")
    master_id = request.session.get("master_id")

    login(request, destino_user)
    if master_mode_flag:
        request.session["master_mode"] = master_mode_flag
    if master_id:
        request.session["master_id"] = master_id
    request.session["master_original_user_id"] = master_user_id
    request.session["impersonado_por_master"] = True
    request.session["master_impersonation_assinatura_id"] = assinatura.id
    _registrar_log(master, "IMPERSONACAO_INICIADA", request, assinatura)
    messages.success(request, f"Acessando como {destino_user.username}.")
    return redirect("dashboard")


@login_required
def master_sair_impersonacao(request):
    if not request.session.get("impersonado_por_master"):
        return redirect("dashboard")

    master_user_id = request.session.get("master_original_user_id")
    master_mode_flag = request.session.get("master_mode")
    master_id = request.session.get("master_id")
    master = None
    if master_user_id:
        master_user = User.objects.filter(id=master_user_id).first()
        if master_user:
            master = getattr(master_user, "master_account", None)
            login(request, master_user)
            if master_mode_flag:
                request.session["master_mode"] = master_mode_flag
            if master_id:
                request.session["master_id"] = master_id
    request.session.pop("impersonado_por_master", None)
    request.session.pop("master_impersonation_assinatura_id", None)
    request.session.pop("master_original_user_id", None)
    if master:
        _registrar_log(master, "IMPERSONACAO_ENCERRADA", request)
    messages.info(request, "Retornou ao modo master.")
    return redirect("master_tenants_dashboard")

