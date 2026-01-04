"""
Testes para autenticação e autorização
"""
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal

from gestao_rural.models import ProdutorRural, Propriedade


@pytest.mark.django_db
class TestAutenticacao:
    """Testes de autenticação"""
    
    def test_login_view_get(self, client):
        """Testa acesso à página de login"""
        response = client.get(reverse('login'))
        assert response.status_code == 200
    
    def test_login_view_post_sucesso(self, client, user):
        """Testa login bem-sucedido"""
        response = client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        assert response.status_code == 302  # Redirect após login
    
    def test_login_view_post_erro(self, client):
        """Testa login com credenciais inválidas"""
        response = client.post(reverse('login'), {
            'username': 'inexistente',
            'password': 'senhaerrada',
        })
        assert response.status_code == 200  # Permanece na página
        # Verificar mensagem de erro (se implementada)
    
    def test_logout_view(self, client_logged_in):
        """Testa logout"""
        response = client_logged_in.get(reverse('logout'))
        assert response.status_code == 302  # Redirect após logout
    
    def test_dashboard_requer_login(self, client):
        """Testa que dashboard requer autenticação"""
        response = client.get(reverse('dashboard'))
        assert response.status_code == 302  # Redirect para login
    
    def test_dashboard_com_login(self, client_logged_in):
        """Testa acesso ao dashboard com login"""
        response = client_logged_in.get(reverse('dashboard'))
        assert response.status_code in [200, 302]  # 200 ou redirect para propriedade


@pytest.mark.django_db
class TestAutorizacao:
    """Testes de autorização"""
    
    def test_produtor_apenas_do_usuario(self, client, user, produtor):
        """Testa que usuário só vê seus próprios produtores"""
        # Criar outro usuário
        outro_user = User.objects.create_user(
            username='outro',
            email='outro@example.com',
            password='pass123'
        )
        outro_produtor = ProdutorRural.objects.create(
            nome='Outro Produtor',
            cpf_cnpj='99999999999',
            usuario_responsavel=outro_user
        )
        
        client.force_login(user)
        url = reverse('produtor_editar', args=[outro_produtor.id])
        response = client.get(url)
        # Deve dar erro 404 ou redirect (sem permissão)
        assert response.status_code in [302, 403, 404]
    
    def test_propriedade_apenas_do_usuario(self, client, user, propriedade):
        """Testa que usuário só acessa propriedades dos seus produtores"""
        # Criar outro usuário e propriedade
        outro_user = User.objects.create_user(
            username='outro',
            email='outro@example.com',
            password='pass123'
        )
        outro_produtor = ProdutorRural.objects.create(
            nome='Outro Produtor',
            cpf_cnpj='99999999999',
            usuario_responsavel=outro_user
        )
        outra_propriedade = Propriedade.objects.create(
            produtor=outro_produtor,
            nome_propriedade='Outra Fazenda',
            municipio='Dourados',
            uf='MS',
            area_total_ha=Decimal('200.00'),
            tipo_operacao='PECUARIA',
        )
        
        client.force_login(user)
        url = reverse('propriedade_editar', args=[outra_propriedade.id])
        response = client.get(url)
        # Deve dar erro 404 ou redirect (sem permissão)
        assert response.status_code in [302, 403, 404]


