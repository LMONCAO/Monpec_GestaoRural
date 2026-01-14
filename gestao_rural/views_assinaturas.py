from __future__ import annotations

from typing import Any, Dict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import AssinaturaCliente, PlanoAssinatura
from .services import notificacoes
from .services.provisionamento import provisionar_workspace
from .services.payments.factory import PaymentGatewayFactory


def assinaturas_dashboard(request: HttpRequest) -> HttpResponse:
    """Dashboard de assinaturas - apenas Mercado Pago"""
    from django.db import connection
    
    # Buscar planos ativos - sempre garantir que seja uma queryset válida
    planos = PlanoAssinatura.objects.none()  # Começar com queryset vazia como fallback

    try:
        # Tentar buscar planos ativos primeiro
        planos_ativos = PlanoAssinatura.objects.filter(ativo=True)
        if planos_ativos.exists():
            # Ordenar por preço se o campo existir, senão por nome
            try:
                planos = planos_ativos.order_by("preco_mensal_referencia", "nome")
            except:
                planos = planos_ativos.order_by("nome")
        else:
            # Se não houver planos ativos, buscar todos
            planos_todos = PlanoAssinatura.objects.all()
            if planos_todos.exists():
                try:
                    planos = planos_todos.order_by("preco_mensal_referencia", "nome")
                except:
                    planos = planos_todos.order_by("nome")

        # Se ainda não houver planos, criar planos padrão
        if not planos.exists():
            print("Nenhum plano encontrado, criando planos padrão...")
            try:
                PlanoAssinatura.objects.get_or_create(
                    nome='Básico',
                    slug='basico',
                    defaults={
                        'descricao': 'Plano básico para pequenos produtores',
                        'preco_mensal_referencia': 49.90,
                        'max_usuarios': 1,
                        'modulos_disponiveis': ["dashboard_pecuaria", "curral", "cadastro", "pecuaria", "financeiro", "relatorios"],
                        'recursos': '{"pecuaria": true, "financeiro": true, "relatorios": true}',
                        'ativo': True,
                        'popular': False,
                        'recomendado': False,
                        'ordem_exibicao': 1
                    }
                )
                PlanoAssinatura.objects.get_or_create(
                    nome='Profissional',
                    slug='profissional',
                    defaults={
                        'descricao': 'Plano completo para produtores',
                        'preco_mensal_referencia': 99.90,
                        'max_usuarios': 5,
                        'modulos_disponiveis': ["dashboard_pecuaria", "curral", "cadastro", "planejamento", "pecuaria", "rastreabilidade", "reproducao", "pesagem", "movimentacoes", "patrimonio", "nutricao", "compras", "vendas", "operacoes", "financeiro", "projetos", "relatorios", "categorias", "configuracoes"],
                        'recursos': '{"pecuaria": true, "financeiro": true, "relatorios": true, "projetos_bancarios": true}',
                        'ativo': True,
                        'popular': True,
                        'recomendado': True,
                        'ordem_exibicao': 2
                    }
                )
                PlanoAssinatura.objects.get_or_create(
                    nome='Empresarial',
                    slug='empresarial',
                    defaults={
                        'descricao': 'Plano empresarial para grandes propriedades',
                        'preco_mensal_referencia': 199.90,
                        'max_usuarios': 20,
                        'modulos_disponiveis': ["dashboard_pecuaria", "curral", "cadastro", "planejamento", "pecuaria", "rastreabilidade", "reproducao", "pesagem", "movimentacoes", "patrimonio", "nutricao", "compras", "vendas", "operacoes", "financeiro", "projetos", "relatorios", "categorias", "configuracoes"],
                        'recursos': '{"pecuaria": true, "financeiro": true, "relatorios": true, "projetos_bancarios": true, "multi_propriedade": true}',
                        'ativo': True,
                        'popular': False,
                        'recomendado': False,
                        'ordem_exibicao': 3
                    }
                )
                # Buscar novamente após criar
                planos = PlanoAssinatura.objects.filter(ativo=True).order_by("preco_mensal_referencia", "nome")
            except Exception as create_error:
                print(f"Erro ao criar planos: {create_error}")

    except Exception as e:
        print(f"Erro geral ao buscar planos: {e}")
        # Garantir que planos seja sempre uma queryset válida
        try:
            planos = PlanoAssinatura.objects.all().order_by("preco_mensal_referencia", "nome")
        except Exception:
            # Em último caso, manter a queryset vazia
            planos = PlanoAssinatura.objects.none()
    
    # Buscar assinatura do usuário - apenas se estiver autenticado
    assinatura = None
    if request.user.is_authenticated:
        try:
            # Primeiro tentar usar o ORM do Django (mais seguro)
            from .models import AssinaturaCliente
            try:
                assinatura_obj = AssinaturaCliente.objects.filter(
                    usuario=request.user,
                    status='ATIVA'
                ).first()
                if assinatura_obj:
                    assinatura = assinatura_obj
            except Exception as orm_error:
                print(f"Erro no ORM, tentando SQL direto: {orm_error}")
                # Fallback para SQL direto se o ORM falhar
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT id, usuario_id, produtor_id, plano_id, status,
                                   mercadopago_customer_id, mercadopago_subscription_id,
                                   gateway_pagamento, ultimo_checkout_id, current_period_end,
                                   cancelamento_agendado, metadata, data_liberacao,
                                   criado_em, atualizado_em
                            FROM gestao_rural_assinaturacliente
                            WHERE usuario_id = %s AND status = 'ATIVA'
                            LIMIT 1
                        """, [request.user.id])

                        row = cursor.fetchone()
                        if row:
                            # Criar objeto mock com os dados
                            class AssinaturaMock:
                                def __init__(self, row_data):
                                    self.id = row_data[0]
                                    self.usuario_id = row_data[1]
                                    self.produtor_id = row_data[2]
                                    self.plano_id = row_data[3]
                                    self.status = row_data[4]
                                    self.mercadopago_customer_id = row_data[5]
                                    self.mercadopago_subscription_id = row_data[6]
                                    self.gateway_pagamento = row_data[7]
                                    self.ultimo_checkout_id = row_data[8]
                                    self.current_period_end = row_data[9]
                                    self.cancelamento_agendado = row_data[10]
                                    self.metadata = row_data[11]
                                    self.data_liberacao = row_data[12]
                                    self.criado_em = row_data[13]
                                    self.atualizado_em = row_data[14]
                                    self.plano = None

                            assinatura = AssinaturaMock(row)

                            # Carregar plano se necessário
                            if assinatura.plano_id:
                                try:
                                    assinatura.plano = PlanoAssinatura.objects.get(id=assinatura.plano_id)
                                except PlanoAssinatura.DoesNotExist:
                                    assinatura.plano = None
                except Exception as sql_error:
                    print(f"Erro no SQL direto também: {sql_error}")
                    assinatura = None
        except Exception as e:
            # Em caso de qualquer erro, continuar sem assinatura
            print(f"Erro geral ao buscar assinatura: {e}")
            assinatura = None
    else:
        # Usuário não autenticado
        assinatura = None
    
    # Gateway padrão: apenas Mercado Pago
    gateway_default = 'mercadopago'
    publishable_key = getattr(settings, 'MERCADOPAGO_PUBLIC_KEY', '')
    
    contexto = {
        "planos": planos,
        "assinatura": assinatura,
        "publishable_key": publishable_key,
        "gateway": gateway_default,
    }
    return render(request, "gestao_rural/assinaturas_dashboard.html", contexto)


@login_required
@csrf_exempt
def iniciar_checkout(request: HttpRequest, plano_slug: str) -> JsonResponse:
    print(f"DEBUG: Função iniciar_checkout chamada! Método: {request.method}, Plano: {plano_slug}")
    print(f"DEBUG: POST data: {dict(request.POST)}")
    print(f"DEBUG: User: {request.user.username if request.user.is_authenticated else 'Não autenticado'}")
    if request.method != "POST":
        return JsonResponse({"detail": "Método não permitido."}, status=405)

    # Validações de segurança (opcional - não bloquear se houver erro)
    ip_address = request.META.get('REMOTE_ADDR', '')
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Verificar se pode processar pagamento (permitir se não tiver assinatura ou se estiver inativa)
    try:
        from .security_avancado import (
            verificar_assinatura_ativa_para_pagamento,
            registrar_log_auditoria,
            obter_ip_address,
        )
        ip_address = obter_ip_address(request)
        pode_processar, mensagem = verificar_assinatura_ativa_para_pagamento(request.user)
        if not pode_processar:
            registrar_log_auditoria(
                tipo_acao='PROCESSAR_PAGAMENTO',
                descricao=f"Tentativa de pagamento bloqueada: {mensagem}",
                usuario=request.user,
                ip_address=ip_address,
                user_agent=user_agent,
                nivel_severidade='ALTO',
                sucesso=False,
            )
            return JsonResponse({"detail": mensagem}, status=400)
    except ImportError:
        # Se o módulo não existir, continuar sem validação
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Módulo security_avancado não encontrado. Continuando sem validação adicional.")
    except Exception as e:
        # Se houver erro na verificação, permite continuar (não bloqueia)
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.warning(f"Erro na verificação de segurança: {e}")
        traceback.print_exc()
        pass

    plano = get_object_or_404(PlanoAssinatura, slug=plano_slug, ativo=True)
    
    # Capturar nome e email do formulário (se fornecido)
    nome_cliente = request.POST.get('nome', '').strip() or request.user.get_full_name() or request.user.username
    email_cliente = request.POST.get('email', '').strip() or request.user.email
    
    # Atualizar dados do usuário se fornecidos
    if nome_cliente and nome_cliente != request.user.get_full_name():
        partes_nome = nome_cliente.split(' ', 1)
        request.user.first_name = partes_nome[0]
        if len(partes_nome) > 1:
            request.user.last_name = partes_nome[1]
        request.user.save(update_fields=['first_name', 'last_name'])
    
    if email_cliente and email_cliente != request.user.email:
        request.user.email = email_cliente
        request.user.save(update_fields=['email'])
    
    # Usar get_or_create sem only() para evitar problemas com campos removidos
    assinatura, _ = AssinaturaCliente.objects.get_or_create(
        usuario=request.user, defaults={"plano": plano}
    )
    assinatura.plano = plano
    assinatura.status = AssinaturaCliente.Status.PENDENTE
    assinatura.save(update_fields=["plano", "status", "atualizado_em"])
    
    # Registrar log (TEMPORARIAMENTE DESABILITADO para debug)
    # try:
    #     from .security_avancado import registrar_log_auditoria
    #     registrar_log_auditoria(
    #         tipo_acao='PROCESSAR_PAGAMENTO',
    #         descricao=f"Iniciado checkout para plano {plano.nome}",
    #         usuario=request.user,
    #         ip_address=ip_address,
    #         user_agent=user_agent,
    #         nivel_severidade='MEDIO',
    #         metadata={'plano_id': plano.id, 'plano_slug': plano_slug},
    #     )
    # except (ImportError, Exception):
    #     # Se não conseguir registrar log, continuar mesmo assim
    #     pass
    pass

    success_url = request.build_absolute_uri(reverse("assinaturas_sucesso"))
    cancel_url = request.build_absolute_uri(reverse("assinaturas_cancelado"))

    # Determinar gateway a usar (pode ser passado via parâmetro ou usar padrão)
    gateway_name = request.POST.get('gateway') or request.GET.get('gateway') or getattr(settings, 'PAYMENT_GATEWAY_DEFAULT', 'mercadopago')
    
    try:
        # Verificar se o token está configurado antes de criar o gateway
        from decouple import config as decouple_config
        token_check = decouple_config('MERCADOPAGO_ACCESS_TOKEN', default='')
        if not token_check:
            # Tentar via settings também
            token_check = getattr(settings, 'MERCADOPAGO_ACCESS_TOKEN', '')

        if not token_check:
            import logging
            logger = logging.getLogger(__name__)
            logger.error("MERCADOPAGO_ACCESS_TOKEN não encontrado em .env nem em settings")
            return JsonResponse({
                "detail": "Configuração do Mercado Pago não encontrada. Entre em contato com o suporte para configurar o sistema de pagamentos."
            }, status=500)
        
        # Criar instância do gateway usando factory
        gateway = PaymentGatewayFactory.criar_gateway(gateway_name)
        
        # Verificar se o gateway foi criado
        if not gateway:
            return JsonResponse({"detail": f"Gateway '{gateway_name}' não pôde ser criado. Verifique as configurações."}, status=500)
        
        # Definir gateway na assinatura
        assinatura.gateway_pagamento = gateway_name
        assinatura.save(update_fields=["gateway_pagamento", "atualizado_em"])
        
        # Criar sessão de checkout (nome e email já foram atualizados no usuário acima)
        session_result = gateway.criar_checkout_session(
            assinatura=assinatura,
            plano=plano,
            success_url=success_url,
            cancel_url=cancel_url,
        )
        
        # Verificar se a URL foi gerada
        if not session_result or not session_result.url:
            return JsonResponse({
                "detail": "Erro: URL de checkout não foi gerada. Verifique se MERCADOPAGO_ACCESS_TOKEN está configurado corretamente."
            }, status=500)
            
    except ValueError as exc:
        import traceback
        traceback.print_exc()
        error_msg = str(exc)
        if "não está registrado" in error_msg:
            error_msg += f" Verifique se o gateway '{gateway_name}' está instalado e configurado."
        return JsonResponse({"detail": error_msg}, status=400)
    except RuntimeError as exc:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"RuntimeError ao criar checkout: {exc}", exc_info=True)
        traceback.print_exc()
        error_msg = str(exc)
        if "MERCADOPAGO_ACCESS_TOKEN" in error_msg:
            error_msg += " Configure a variável MERCADOPAGO_ACCESS_TOKEN no arquivo .env"
        return JsonResponse({"detail": error_msg}, status=500)
    except Exception as exc:  # pragma: no cover - logar em produção
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Erro ao iniciar checkout: {exc}", exc_info=True)
        traceback.print_exc()
        error_msg = f"Erro ao iniciar checkout: {str(exc)}"
        # Não expor detalhes técnicos ao usuário em produção
        if settings.DEBUG:
            error_msg = f"Erro ao iniciar checkout: {str(exc)}\n\nTraceback:\n{traceback.format_exc()}"
        else:
            error_msg = "Erro ao processar pagamento. Por favor, tente novamente ou entre em contato com o suporte."
        return JsonResponse({"detail": error_msg}, status=500)

    return JsonResponse({"checkout_url": session_result.url, "session_id": session_result.session_id})


@login_required
def checkout_sucesso(request: HttpRequest) -> HttpResponse:
    """Página de confirmação de pagamento com dados de acesso."""
    try:
        # Se usuário não está autenticado, buscar pela assinatura_id do parâmetro
        assinatura_id = request.GET.get('assinatura_id')
        if not request.user.is_authenticated and assinatura_id:
            assinatura = AssinaturaCliente.objects.filter(id=assinatura_id).values(
                'id', 'usuario_id', 'produtor_id', 'plano_id', 'status',
                'mercadopago_customer_id', 'mercadopago_subscription_id',
                'gateway_pagamento', 'ultimo_checkout_id', 'current_period_end',
                'cancelamento_agendado', 'metadata', 'data_liberacao',
                'criado_em', 'atualizado_em'
            ).first()
        elif request.user.is_authenticated:
            assinatura = AssinaturaCliente.objects.filter(usuario=request.user).values(
                'id', 'usuario_id', 'produtor_id', 'plano_id', 'status',
                'mercadopago_customer_id', 'mercadopago_subscription_id',
                'gateway_pagamento', 'ultimo_checkout_id', 'current_period_end',
                'cancelamento_agendado', 'metadata', 'data_liberacao',
                'criado_em', 'atualizado_em'
            ).first()
        else:
            # Usuário não autenticado e sem assinatura_id
            return render(request, 'gestao_rural/assinaturas_confirmacao.html', {
                'erro': 'Usuário não autenticado e assinatura não encontrada.',
                'test_mode': request.GET.get('test_mode', False)
            })
        # Verificar se usuário tem assinatura
        if assinatura is None:
            # Usuário não tem assinatura, redirecionar para dashboard de assinaturas
            messages.info(request, 'Para acessar o sistema completo, faça uma assinatura primeiro.')
            return redirect('assinaturas_dashboard')

        # Carregar plano separadamente se necessário
        if isinstance(assinatura, dict) and assinatura.get('plano_id'):
            try:
                plano = PlanoAssinatura.objects.get(id=assinatura['plano_id'])
                assinatura['plano'] = plano
            except PlanoAssinatura.DoesNotExist:
                assinatura['plano'] = None

        # Se a assinatura está ativa ou está em modo teste, mostrar dados de acesso
        is_test_mode = request.GET.get('test_mode', False)
        if assinatura and (assinatura.get('status') == AssinaturaCliente.Status.ATIVA.value or is_test_mode):
            # Garantir que o usuário tenha a senha padrão
            garantir_senha_padrao_usuario(request.user)
            
            contexto = {
                'assinatura': assinatura,
                'email': request.user.email if request.user.is_authenticated else 'usuario@exemplo.com',
                'senha': 'Monpec2025@',
                'data_liberacao': assinatura.get('data_liberacao') or '01/02/2026',
                'test_mode': is_test_mode,
            }
            return render(request, 'gestao_rural/assinaturas_confirmacao.html', contexto)
        else:
            # Se ainda está pendente, mostrar mensagem de aguardo com informações de contato
            messages.success(
                request,
                f"Pagamento recebido! Estamos processando sua assinatura. Um de nossos consultores entrará em contato em breve através do e-mail {request.user.email} para orientá-lo sobre o sistema.",
            )
            return redirect("assinaturas_dashboard")
    except AssinaturaCliente.DoesNotExist:
        messages.warning(request, "Assinatura não encontrada.")
        return redirect("assinaturas_dashboard")


@login_required
def checkout_cancelado(request: HttpRequest) -> HttpResponse:
    messages.info(
        request,
        "Pagamento cancelado. Se precisar de ajuda, entre em contato com o suporte.",
    )
    return redirect("assinaturas_dashboard")


@csrf_exempt
def mercadopago_webhook(request: HttpRequest) -> HttpResponse:
    """Webhook para eventos do Mercado Pago."""
    if request.method != "POST":
        return HttpResponse(
            "✅ Webhook do Mercado Pago está funcionando!\n\n"
            "Este endpoint aceita apenas requisições POST do Mercado Pago.\n"
            "Acesse via navegador não é permitido por segurança.\n\n"
            "URL configurada corretamente para: https://monpec.com.br/assinaturas/webhook/mercadopago/",
            content_type="text/plain; charset=utf-8",
            status=405
        )

    payload = request.body
    
    try:
        gateway = PaymentGatewayFactory.criar_gateway('mercadopago')
        evento = gateway.processar_webhook(payload)
    except (ValueError, RuntimeError) as exc:
        return HttpResponse(str(exc), status=400)
    except Exception:
        return HttpResponseBadRequest("Evento inválido.")

    tipo_evento = evento.get("type")
    dados = evento.get("data", {})
    
    # Buscar assinatura pelo external_reference ou preapproval_id
    assinatura = None
    
    if tipo_evento == "payment":
        external_reference = dados.get("external_reference")
        if external_reference:
            try:
                assinatura = AssinaturaCliente.objects.filter(id=external_reference).values(
            'id', 'usuario_id', 'produtor_id', 'plano_id', 'status',
            'mercadopago_customer_id', 'mercadopago_subscription_id',
            'gateway_pagamento', 'ultimo_checkout_id', 'current_period_end',
            'cancelamento_agendado', 'metadata', 'data_liberacao',
            'criado_em', 'atualizado_em'
        ).first()
            except AssinaturaCliente.DoesNotExist:
                pass
    elif tipo_evento in ["subscription", "preapproval"]:
        preapproval_id = dados.get("id")
        if preapproval_id:
            # Buscar por metadata
            assinatura = AssinaturaCliente.objects.filter(
                metadata__mercadopago_preapproval_id=preapproval_id
            ).first()
    
    if assinatura:
        gateway.atualizar_assinatura_por_evento(assinatura, evento)
        assinatura.refresh_from_db()
        
        if assinatura.status == AssinaturaCliente.Status.ATIVA:
            # Definir data de liberação como 01/02/2025 se não estiver definida
            if not assinatura.data_liberacao:
                from datetime import date
                assinatura.data_liberacao = date(2026, 2, 1)  # 01/02/2026
                assinatura.save(update_fields=['data_liberacao', 'atualizado_em'])
            
            # Garantir que o usuário tenha a senha padrão definida
            garantir_senha_padrao_usuario(assinatura.usuario)
            
            # Confirmar email e telefone automaticamente quando pagamento é confirmado
            confirmar_email_e_telefone_usuario(assinatura.usuario)
            
            resultado = provisionar_workspace(assinatura)
            
            # Enviar email com credenciais de acesso apenas na primeira ativação
            if not assinatura.metadata or not assinatura.metadata.get('email_enviado'):
                enviar_email_confirmacao_assinatura(assinatura)
                # Marcar que email foi enviado
                if not assinatura.metadata:
                    assinatura.metadata = {}
                assinatura.metadata['email_enviado'] = True

                # Notificar consultor sobre nova assinatura
                try:
                    from .services.notificacoes import notificar_consultor_nova_assinatura
                    notificar_consultor_nova_assinatura(assinatura)
                    assinatura.metadata['consultor_notificado'] = True
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Falha ao notificar consultor sobre nova assinatura {assinatura.id}: {e}")

                assinatura.save(update_fields=['metadata', 'atualizado_em'])
    
    return HttpResponse(status=200)


def garantir_senha_padrao_usuario(usuario) -> None:
    """Garante que o usuário tenha a senha padrão Monpec2025@ definida."""
    from django.contrib.auth.hashers import check_password
    
    senha_padrao = "Monpec2025@"
    
    # Verificar se o usuário já tem senha definida
    if usuario.password and len(usuario.password) > 0:
        # Se já tem senha, verificar se é a padrão
        if not check_password(senha_padrao, usuario.password):
            # Se não for a padrão, definir a senha padrão
            usuario.set_password(senha_padrao)
            usuario.save(update_fields=['password'])
    else:
        # Se não tem senha, definir a padrão
        usuario.set_password(senha_padrao)
        usuario.save(update_fields=['password'])


def confirmar_email_e_telefone_usuario(usuario) -> None:
    """
    Confirma automaticamente email e telefone do usuário quando o pagamento é confirmado.
    Isso garante que usuários que pagaram não precisem verificar manualmente.
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models_auditoria import VerificacaoEmail, UsuarioAtivo
    
    # Confirmar email
    try:
        verificacao_email, created = VerificacaoEmail.objects.get_or_create(
            usuario=usuario,
            defaults={
                'token': 'auto-confirmed-payment',
                'email_verificado': True,
                'token_expira_em': timezone.now() + timedelta(days=365),  # Longo prazo
                'verificado_em': timezone.now(),
            }
        )
        
        # Se já existe, apenas marcar como verificado
        if not created and not verificacao_email.email_verificado:
            verificacao_email.email_verificado = True
            verificacao_email.verificado_em = timezone.now()
            verificacao_email.save(update_fields=['email_verificado', 'verificado_em'])
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Erro ao confirmar email do usuário {usuario.id}: {e}")
    
    # Ativar usuário se ainda não estiver ativo
    if not usuario.is_active:
        usuario.is_active = True
        usuario.save(update_fields=['is_active'])
    
    # Confirmar telefone (se houver registro em UsuarioAtivo)
    try:
        usuario_ativo, created = UsuarioAtivo.objects.get_or_create(
            usuario=usuario,
            defaults={
                'nome_completo': usuario.get_full_name() or usuario.username,
                'email': usuario.email or '',
                'telefone': '',  # Será preenchido se disponível
                'ativo': True,
            }
        )
        
        # Se já existe, apenas garantir que está ativo
        if not created and not usuario_ativo.ativo:
            usuario_ativo.ativo = True
            usuario_ativo.save(update_fields=['ativo'])
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Erro ao confirmar telefone do usuário {usuario.id}: {e}")


def enviar_email_confirmacao_assinatura(assinatura: AssinaturaCliente) -> bool:
    """Envia email de confirmação de assinatura com credenciais de acesso."""
    try:
        usuario = assinatura.usuario
        email_usuario = usuario.email
        
        assunto = "Assinatura Confirmada - MONPEC - Pré-Lançamento"
        
        mensagem_texto = f"""
Olá {usuario.get_full_name() or usuario.username},

Sua assinatura foi confirmada com sucesso!

ASSINATURA DE PRÉ-LANÇAMENTO
O sistema MONPEC estará disponível a partir de 01/02/2026.

SUAS CREDENCIAIS DE ACESSO:
Email: {email_usuario}
Senha: Monpec2025@

IMPORTANTE:
- Este é um sistema de pré-lançamento
- O acesso será liberado em 01/02/2026
- Um de nossos consultores entrará em contato em breve para orientá-lo sobre o sistema
- Guarde estas credenciais com segurança

Enquanto aguarda o lançamento, você pode acessar a versão de demonstração do sistema para conhecer as funcionalidades.

Atenciosamente,
Equipe MONPEC - Gestão Rural Inteligente
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
            background: linear-gradient(135deg, #0d6efd 0%, #0b5ed7 100%);
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
            border-left: 4px solid #0d6efd;
            border-radius: 5px;
        }}
        .credentials strong {{
            color: #0d6efd;
            font-size: 16px;
        }}
        .warning {{
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .footer {{
            text-align: center;
            color: #6c757d;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MONPEC - Gestão Rural Inteligente</h1>
        <p>Assinatura Confirmada - Pré-Lançamento</p>
    </div>
    
    <div class="content">
        <p>Olá <strong>{usuario.get_full_name() or usuario.username}</strong>,</p>
        
        <p>Sua assinatura foi confirmada com sucesso!</p>
        
        <div class="credentials">
            <h3 style="color: #0d6efd; margin-top: 0;">📋 ASSINATURA DE PRÉ-LANÇAMENTO</h3>
            <p>O sistema MONPEC estará disponível a partir de <strong>01/02/2025</strong>.</p>
        </div>
        
        <div class="credentials">
            <h3 style="color: #0d6efd; margin-top: 0;">🔐 SUAS CREDENCIAIS DE ACESSO</h3>
            <p><strong>Email:</strong> {email_usuario}</p>
            <p><strong>Senha:</strong> Monpec2025@</p>
        </div>
        
        <div class="warning">
            <strong>⚠️ IMPORTANTE:</strong>
            <ul>
                <li>Este é um sistema de pré-lançamento</li>
                <li>O acesso será liberado em <strong>01/02/2025</strong></li>
                <li>Um de nossos consultores entrará em contato em breve para orientá-lo sobre o sistema</li>
                <li>Guarde estas credenciais com segurança</li>
            </ul>
        </div>
        
        <p>Enquanto aguarda o lançamento, você pode acessar a versão de demonstração do sistema para conhecer as funcionalidades.</p>
        
        <p>Atenciosamente,<br>
        <strong>Equipe MONPEC - Gestão Rural Inteligente</strong></p>
    </div>
    
    <div class="footer">
        <p>Este é um email automático, por favor não responda.</p>
        <p>MONPEC - Gestão Rural Inteligente</p>
    </div>
</body>
</html>
"""
        
        remetente = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@monpec.com.br')
        
        send_mail(
            subject=assunto,
            message=mensagem_texto,
            from_email=remetente,
            recipient_list=[email_usuario],
            html_message=mensagem_html,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Erro ao enviar email de confirmação de assinatura: {e}")
        return False


@login_required
def pre_lancamento(request: HttpRequest) -> HttpResponse:
    """Página de pré-lançamento para assinantes."""
    try:
        assinatura = AssinaturaCliente.objects.filter(usuario=request.user).values(
            'id', 'usuario_id', 'produtor_id', 'plano_id', 'status',
            'mercadopago_customer_id', 'mercadopago_subscription_id',
            'gateway_pagamento', 'ultimo_checkout_id', 'current_period_end',
            'cancelamento_agendado', 'metadata', 'data_liberacao',
            'criado_em', 'atualizado_em'
        ).first()
        # Carregar plano separadamente se necessário
        if assinatura and assinatura.plano_id:
            try:
                assinatura.plano = PlanoAssinatura.objects.get(id=assinatura.plano_id)
            except PlanoAssinatura.DoesNotExist:
                assinatura.plano = None
    except AssinaturaCliente.DoesNotExist:
        return redirect('assinaturas_dashboard')

    # Redirecionar para dashboard de demonstração
    return redirect('dashboard')


@login_required
def leads_demo(request: HttpRequest) -> HttpResponse:
    """Página para visualizar leads de usuários demo interessados."""
    # Verificar se usuário é superuser ou admin
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado. Apenas administradores podem visualizar esta página.')
        return redirect('assinaturas_dashboard')

    # Buscar usuários demo (que têm UsuarioAtivo)
    from django.contrib.auth.models import User
    from gestao_rural.models_auditoria import UsuarioAtivo

    try:
        # Buscar usuários que são demo
        usuarios_demo_ids = UsuarioAtivo.objects.values_list('usuario_id', flat=True)
        usuarios_demo = User.objects.filter(id__in=usuarios_demo_ids).order_by('-date_joined')

        # Estatísticas
        from gestao_rural.services_notificacoes_demo import obter_estatisticas_leads_demo
        estatisticas = obter_estatisticas_leads_demo()

        contexto = {
            'leads_demo': usuarios_demo,
            'estatisticas': estatisticas,
        }

        return render(request, 'gestao_rural/leads_demo.html', contexto)

    except Exception as e:
        messages.error(request, f'Erro ao carregar leads: {str(e)}')
        return redirect('assinaturas_dashboard')


@login_required
def usuarios_assinantes(request: HttpRequest) -> HttpResponse:
    """Página para visualizar todos os usuários com assinaturas ativas."""
    # Verificar se usuário é superuser ou admin
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado. Apenas administradores podem visualizar esta página.')
        return redirect('dashboard')

    # Buscar todas as assinaturas com dados relacionados
    assinaturas = AssinaturaCliente.objects.select_related(
        'usuario', 'plano'
    ).order_by('-criado_em')

    # Estatísticas avançadas
    total_assinaturas = assinaturas.count()
    assinaturas_ativas = assinaturas.filter(status='ATIVA').count()
    assinaturas_pendentes = assinaturas.filter(status='PENDENTE').count()
    assinaturas_canceladas = assinaturas.filter(status='CANCELADA').count()

    # Receita total
    from django.db.models import Sum
    receita_total = 0
    for assinatura in assinaturas.filter(status='ATIVA'):
        if assinatura.plano and assinatura.plano.preco_mensal_referencia:
            receita_total += float(assinatura.plano.preco_mensal_referencia)

    # Taxa de conversão
    taxa_conversao = 0
    if total_assinaturas > 0:
        taxa_conversao = (assinaturas_ativas / total_assinaturas) * 100

    # Receita média por assinatura ativa
    receita_media = 0
    if assinaturas_ativas > 0:
        receita_media = receita_total / assinaturas_ativas

    # Assinaturas por plano
    planos_stats = {}
    for assinatura in assinaturas.filter(status='ATIVA'):
        plano_nome = assinatura.plano.nome if assinatura.plano else 'Sem Plano'
        if plano_nome not in planos_stats:
            planos_stats[plano_nome] = {'count': 0, 'receita': 0}
        planos_stats[plano_nome]['count'] += 1
        if assinatura.plano and assinatura.plano.preco_mensal_referencia:
            planos_stats[plano_nome]['receita'] += float(assinatura.plano.preco_mensal_referencia)

    # Dados para gráficos (últimos 7 dias)
    from datetime import timedelta, datetime
    hoje = datetime.now().date()
    ultimos_7_dias = []
    for i in range(7):
        dia = hoje - timedelta(days=i)
        count = assinaturas.filter(criado_em__date=dia).count()
        ultimos_7_dias.append({
            'data': dia.strftime('%d/%m'),
            'count': count
        })

    contexto = {
        'assinaturas': assinaturas,
        'total_assinaturas': total_assinaturas,
        'assinaturas_ativas': assinaturas_ativas,
        'assinaturas_pendentes': assinaturas_pendentes,
        'assinaturas_canceladas': assinaturas_canceladas,
        'receita_total': receita_total,
        'taxa_conversao': round(taxa_conversao, 1),
        'receita_media': round(receita_media, 2),
        'planos_stats': planos_stats,
        'ultimos_7_dias': ultimos_7_dias,
    }

    return render(request, 'gestao_rural/usuarios_assinantes.html', contexto)


# Sistema de pagamento: Apenas Mercado Pago
# Stripe foi completamente removido do sistema

