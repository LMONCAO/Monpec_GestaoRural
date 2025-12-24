from __future__ import annotations

import secrets
import string
from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Tuple

from django.contrib.auth.models import User
from django.db import transaction
from django.utils.text import slugify

from ..models import AssinaturaCliente, TenantUsuario


class TenantAccessError(RuntimeError):
    """Erro base para operações de controle de usuários do tenant."""


@dataclass
class NovoUsuarioResultado:
    usuario: User
    tenant_usuario: TenantUsuario
    senha_temporaria: Optional[str] = None


def _gerar_username_base(nome: str) -> str:
    base = slugify(nome) or "usuario"
    return base[:20]


def _gerar_senha_temporaria() -> str:
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(12))


def obter_assinatura_do_usuario(usuario: User) -> Optional[AssinaturaCliente]:
    """Retorna a assinatura vinculada ao usuário autenticado."""
    if hasattr(usuario, "assinatura"):
        return usuario.assinatura
    perfil = getattr(usuario, "tenant_profile", None)
    if perfil:
        return perfil.assinatura
    return None


def contar_usuarios_ativos(assinatura: AssinaturaCliente) -> int:
    return assinatura.usuarios_tenant.filter(ativo=True).count()


def verificar_limite_usuarios(assinatura: AssinaturaCliente) -> None:
    if not assinatura.plano:
        return
    ativos = contar_usuarios_ativos(assinatura)
    if ativos >= assinatura.plano.max_usuarios:
        raise TenantAccessError(
            f"O plano atual permite até {assinatura.plano.max_usuarios} usuários. "
            "Atualize o plano para adicionar mais acessos."
        )


@transaction.atomic
def criar_ou_atualizar_usuario(
    *,
    assinatura: AssinaturaCliente,
    nome: str,
    email: str,
    perfil: str,
    modulos: Optional[Sequence[str]] = None,
    senha_definida: Optional[str] = None,
    username: Optional[str] = None,
    criado_por: Optional[User] = None,
) -> NovoUsuarioResultado:
    """
    Cria ou atualiza um usuário vinculado ao tenant, respeitando o limite do plano.
    """
    email_normalizado = email.lower().strip()
    if not email_normalizado:
        raise TenantAccessError("Informe um e-mail válido para o usuário.")

    verificar_limite_usuarios(assinatura)

    usuario = User.objects.filter(email__iexact=email_normalizado).first()
    senha_temporaria: Optional[str] = None

    if usuario and hasattr(usuario, "tenant_profile"):
        if usuario.tenant_profile.assinatura != assinatura:
            raise TenantAccessError("Este e-mail já está vinculado a outra conta MONPEC.")
    elif not usuario:
        # Usar username fornecido ou gerar automaticamente
        if username:
            # Validar se username já existe
            if User.objects.filter(username=username).exists():
                raise TenantAccessError(f"O username '{username}' já está em uso. Escolha outro.")
            username_final = username
        else:
            # Gerar username automaticamente
            username_base = _gerar_username_base(nome or email_normalizado.split("@")[0])
            username_final = username_base
            sufixo = 1
            while User.objects.filter(username=username_final).exists():
                username_final = f"{username_base[:15]}{sufixo}"
                sufixo += 1
        
        senha_temporaria = senha_definida or _gerar_senha_temporaria()
        usuario = User.objects.create_user(
            username=username_final,
            email=email_normalizado,
            password=senha_temporaria,
            first_name=(nome or "").split(" ")[0][:30],
            last_name=" ".join((nome or "").split(" ")[1:])[:150],
            is_active=True,  # Usuários criados por admin ficam ativos por padrão
        )
    else:
        # Usuário existe, mas ainda não possui perfil de tenant
        if senha_definida:
            usuario.set_password(senha_definida)
            usuario.save(update_fields=["password"])

    tenant_usuario, _ = TenantUsuario.objects.get_or_create(
        usuario=usuario,
        defaults={
            "assinatura": assinatura,
            "nome_exibicao": nome,
            "email": email_normalizado,
            "perfil": perfil,
            "criado_por": criado_por,
        },
    )

    if tenant_usuario.assinatura != assinatura:
        raise TenantAccessError("O usuário informado pertence a outro tenant.")

    tenant_usuario.nome_exibicao = nome
    tenant_usuario.email = email_normalizado
    tenant_usuario.perfil = perfil
    tenant_usuario.criado_por = tenant_usuario.criado_por or criado_por
    tenant_usuario.atualizar_modulos(modulos or assinatura.modulos_disponiveis)
    tenant_usuario.save()

    return NovoUsuarioResultado(
        usuario=usuario,
        tenant_usuario=tenant_usuario,
        senha_temporaria=senha_temporaria,
    )


def desativar_usuario(tenant_usuario: TenantUsuario) -> None:
    tenant_usuario.ativo = False
    tenant_usuario.save(update_fields=["ativo", "atualizado_em"])


def reativar_usuario(tenant_usuario: TenantUsuario) -> None:
    verificar_limite_usuarios(tenant_usuario.assinatura)
    tenant_usuario.ativo = True
    tenant_usuario.save(update_fields=["ativo", "atualizado_em"])


def registrar_login_tenant(usuario: User) -> None:
    perfil = getattr(usuario, "tenant_profile", None)
    if not perfil:
        return
    perfil.ultimo_login = getattr(usuario, "last_login", None)
    perfil.save(update_fields=["ultimo_login"])


def usuario_eh_admin(usuario: User) -> bool:
    """Retorna True se o usuário tiver permissão administrativa no tenant."""
    # Superuser sempre é admin
    if usuario.is_superuser:
        return True
    # Usuário com assinatura (master) é admin
    if hasattr(usuario, "assinatura"):
        return True
    # Verificar perfil de tenant
    perfil = getattr(usuario, "tenant_profile", None)
    if not perfil:
        return False
    return perfil.perfil == TenantUsuario.Perfil.ADMIN

