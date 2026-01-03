from __future__ import annotations

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import AssinaturaCliente, TenantUsuario, TenantWorkspace
from .services.provisionamento import provisionar_workspace

logger = logging.getLogger(__name__)


@receiver(post_save, sender=AssinaturaCliente)
def garantir_usuario_master_no_tenant(sender, instance: AssinaturaCliente, created: bool, **kwargs):
    """Garante que o usuário principal tenha perfil de tenant"""
    if not instance.usuario:
        return
    nome = instance.usuario.get_full_name() or instance.usuario.username
    email = instance.usuario.email or f"{instance.usuario.username}@monpec.local"
    TenantUsuario.objects.get_or_create(
        usuario=instance.usuario,
        defaults={
            "assinatura": instance,
            "nome_exibicao": nome,
            "email": email,
            "perfil": TenantUsuario.Perfil.ADMIN,
            "ativo": True,
        },
    )


@receiver(post_save, sender=AssinaturaCliente)
def provisionar_workspace_automatico(sender, instance: AssinaturaCliente, created: bool, **kwargs):
    """Provisiona workspace automaticamente quando assinatura é ativada"""
    # Só provisiona se a assinatura estiver ativa e não tiver workspace ainda
    if instance.status == AssinaturaCliente.Status.ATIVA:
        if not hasattr(instance, 'workspace') or instance.workspace.status != TenantWorkspace.Status.ATIVO:
            try:
                resultado = provisionar_workspace(instance)
                if resultado.sucesso:
                    logger.info(f"Workspace provisionado automaticamente para assinatura {instance.pk}")
                else:
                    logger.warning(f"Falha ao provisionar workspace: {resultado.mensagem}")
            except Exception as e:
                logger.error(f"Erro ao provisionar workspace automaticamente: {e}")



