import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from gestao_rural.views_vendas import vendas_nota_fiscal_emitir
from gestao_rural.models import Propriedade

def test_nfe_view():
    """Testar a view de emissão de NFE diretamente"""

    # Criar request factory
    factory = RequestFactory()

    # Buscar propriedade e usuário
    try:
        propriedade = Propriedade.objects.first()
        user = User.objects.filter(username='admin').first()

        if not propriedade:
            print("ERRO: Nenhuma propriedade encontrada")
            return

        if not user:
            print("ERRO: Usuário admin não encontrado")
            return

        print(f"Testando com propriedade: {propriedade.id} - {propriedade.nome_propriedade}")
        print(f"Usuário: {user.username}")

        # Criar request GET
        request = factory.get(f'/gestao-rural/propriedade/{propriedade.id}/vendas/nota-fiscal/emitir/')
        request.user = user

        # Adicionar middleware de sessão
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

        # Adicionar middleware de mensagens
        messages_middleware = MessageMiddleware()
        messages_middleware.process_request(request)
        request.session.save()

        # Chamar a view diretamente
        try:
            response = vendas_nota_fiscal_emitir(request, propriedade.id)
            print(f"Status da resposta: {response.status_code}")

            if hasattr(response, 'content'):
                print(f"Tamanho da resposta: {len(response.content)} bytes")

            return response

        except Exception as e:
            print(f"ERRO na view: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    except Exception as e:
        print(f"ERRO geral: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_nfe_view()