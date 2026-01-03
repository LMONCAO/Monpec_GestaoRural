"""
Testes para views de produtores
"""
import pytest
from django.urls import reverse
from django.contrib.auth.models import User

from gestao_rural.models import ProdutorRural


@pytest.mark.django_db
class TestProdutorViews:
    """Testes para views de produtores"""
    
    def test_produtor_novo_get(self, client_logged_in):
        """Testa acesso à página de novo produtor"""
        response = client_logged_in.get(reverse('produtor_novo'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_produtor_novo_post(self, client_logged_in, user):
        """Testa criação de novo produtor"""
        data = {
            'nome': 'Novo Produtor',
            'cpf_cnpj': '98765432100',
            'email': 'novo@example.com',
            'telefone': '(67) 88888-8888',
        }
        response = client_logged_in.post(reverse('produtor_novo'), data)
        assert response.status_code == 302  # Redirect após sucesso
        
        # Verificar se foi criado
        assert ProdutorRural.objects.filter(cpf_cnpj='98765432100').exists()
        produtor = ProdutorRural.objects.get(cpf_cnpj='98765432100')
        assert produtor.usuario_responsavel == user
    
    def test_produtor_editar_get(self, client_logged_in, produtor):
        """Testa acesso à página de edição"""
        url = reverse('produtor_editar', args=[produtor.id])
        response = client_logged_in.get(url)
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['produtor'] == produtor
    
    def test_produtor_editar_post(self, client_logged_in, produtor):
        """Testa edição de produtor"""
        url = reverse('produtor_editar', args=[produtor.id])
        data = {
            'nome': 'Produtor Atualizado',
            'cpf_cnpj': produtor.cpf_cnpj,
            'email': 'atualizado@example.com',
        }
        response = client_logged_in.post(url, data)
        assert response.status_code == 302
        
        # Verificar atualização
        produtor.refresh_from_db()
        assert produtor.nome == 'Produtor Atualizado'
        assert produtor.email == 'atualizado@example.com'
    
    def test_produtor_excluir_get(self, client_logged_in, produtor):
        """Testa acesso à página de exclusão"""
        url = reverse('produtor_excluir', args=[produtor.id])
        response = client_logged_in.get(url)
        assert response.status_code == 200
        assert 'produtor' in response.context
    
    def test_produtor_excluir_post(self, client_logged_in, produtor):
        """Testa exclusão de produtor"""
        produtor_id = produtor.id
        url = reverse('produtor_excluir', args=[produtor_id])
        response = client_logged_in.post(url)
        assert response.status_code == 302
        
        # Verificar exclusão
        assert not ProdutorRural.objects.filter(id=produtor_id).exists()
    
    def test_produtor_editar_sem_permissao(self, client, produtor):
        """Testa que usuário sem permissão não pode editar"""
        # Criar outro usuário
        outro_user = User.objects.create_user(
            username='outro',
            email='outro@example.com',
            password='pass123'
        )
        client.force_login(outro_user)
        
        url = reverse('produtor_editar', args=[produtor.id])
        response = client.get(url)
        # Deve redirecionar ou dar erro 403/404
        assert response.status_code in [302, 403, 404]

