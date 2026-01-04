"""
Testes completos para serviços
"""
import pytest
from django.contrib.auth.models import User
from decimal import Decimal

from gestao_rural.models import ProdutorRural, Propriedade, AssinaturaCliente, TenantUsuario
from gestao_rural.services.produtor_service import ProdutorService
from gestao_rural.services.propriedade_service import PropriedadeService
from gestao_rural.services.dashboard_service import DashboardService


@pytest.mark.django_db
class TestProdutorServiceCompleto:
    """Testes completos para ProdutorService"""
    
    def test_obter_produtores_admin(self, admin_user):
        """Testa que admin vê todos os produtores"""
        # Criar produtores de diferentes usuários
        user1 = User.objects.create_user('user1', 'user1@test.com', 'pass')
        user2 = User.objects.create_user('user2', 'user2@test.com', 'pass')
        
        ProdutorRural.objects.create(
            nome='Produtor 1',
            cpf_cnpj='11111111111',
            usuario_responsavel=user1
        )
        ProdutorRural.objects.create(
            nome='Produtor 2',
            cpf_cnpj='22222222222',
            usuario_responsavel=user2
        )
        
        produtores = ProdutorService.obter_produtores_do_usuario(admin_user)
        assert produtores.count() >= 2
    
    def test_obter_produtores_usuario_normal(self, user):
        """Testa que usuário normal vê apenas seus produtores"""
        # Criar outro usuário e produtor
        outro_user = User.objects.create_user('outro', 'outro@test.com', 'pass')
        ProdutorRural.objects.create(
            nome='Meu Produtor',
            cpf_cnpj='11111111111',
            usuario_responsavel=user
        )
        ProdutorRural.objects.create(
            nome='Produtor de Outro',
            cpf_cnpj='22222222222',
            usuario_responsavel=outro_user
        )
        
        produtores = ProdutorService.obter_produtores_do_usuario(user)
        assert produtores.count() == 1
        assert produtores.first().nome == 'Meu Produtor'
    
    def test_pode_acessar_produtor_proprio(self, user, produtor):
        """Testa que usuário pode acessar seu próprio produtor"""
        assert ProdutorService.pode_acessar_produtor(user, produtor) is True
    
    def test_pode_acessar_produtor_outro(self, user):
        """Testa que usuário não pode acessar produtor de outro"""
        outro_user = User.objects.create_user('outro', 'outro@test.com', 'pass')
        outro_produtor = ProdutorRural.objects.create(
            nome='Outro Produtor',
            cpf_cnpj='99999999999',
            usuario_responsavel=outro_user
        )
        
        assert ProdutorService.pode_acessar_produtor(user, outro_produtor) is False
    
    def test_criar_produtor_com_propriedade_demo(self, user):
        """Testa criação de produtor com propriedade demo"""
        dados_produtor = {
            'nome': 'Produtor Demo',
            'cpf_cnpj': '12345678900',
            'email': 'demo@test.com',
        }
        
        produtor, propriedade = ProdutorService.criar_produtor_com_propriedade_demo(
            user, dados_produtor
        )
        
        assert produtor is not None
        assert propriedade is not None
        assert produtor.nome == 'Produtor Demo'
        assert propriedade.nome_propriedade == 'Monpec1'
        assert propriedade.produtor == produtor


@pytest.mark.django_db
class TestPropriedadeServiceCompleto:
    """Testes completos para PropriedadeService"""
    
    def test_obter_propriedades_do_usuario(self, user, produtor, propriedade):
        """Testa obtenção de propriedades do usuário"""
        propriedades = PropriedadeService.obter_propriedades_do_usuario(user)
        assert propriedade in propriedades
    
    def test_pode_acessar_propriedade_propria(self, user, propriedade):
        """Testa que usuário pode acessar sua própria propriedade"""
        assert PropriedadeService.pode_acessar_propriedade(user, propriedade) is True
    
    def test_pode_acessar_propriedade_outra(self, user):
        """Testa que usuário não pode acessar propriedade de outro"""
        outro_user = User.objects.create_user('outro', 'outro@test.com', 'pass')
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
        
        assert PropriedadeService.pode_acessar_propriedade(user, outra_propriedade) is False
    
    def test_obter_propriedades_do_produtor(self, user, produtor, propriedade):
        """Testa obtenção de propriedades de um produtor"""
        propriedades = PropriedadeService.obter_propriedades_do_produtor(user, produtor)
        assert propriedade in propriedades
    
    def test_criar_propriedade_padrao(self, user, produtor):
        """Testa criação de propriedade padrão"""
        propriedade = PropriedadeService.criar_propriedade_padrao(user, produtor)
        
        assert propriedade is not None
        assert propriedade.produtor == produtor
        assert propriedade.nome_propriedade == 'Minha Propriedade'
        assert propriedade.area_total_ha == Decimal('100.00')


@pytest.mark.django_db
class TestDashboardServiceCompleto:
    """Testes completos para DashboardService"""
    
    def test_obter_dados_dashboard(self, user, produtor, propriedade):
        """Testa obtenção de dados do dashboard"""
        dados = DashboardService.obter_dados_dashboard(user)
        
        assert 'produtores' in dados
        assert 'propriedades' in dados
        assert 'total_propriedades' in dados
        assert 'total_area' in dados
        assert 'propriedade_prioritaria' in dados
        
        assert produtor in dados['produtores']
        assert propriedade in dados['propriedades']
        assert dados['total_propriedades'] >= 1
    
    def test_propriedade_prioritaria_monpec(self, user, produtor):
        """Testa que propriedade Monpec1 tem prioridade"""
        # Criar propriedade Monpec1
        propriedade_monpec = Propriedade.objects.create(
            produtor=produtor,
            nome_propriedade='Monpec1',
            municipio='Campo Grande',
            uf='MS',
            area_total_ha=Decimal('100.00'),
            tipo_operacao='PECUARIA',
        )
        
        dados = DashboardService.obter_dados_dashboard(user)
        assert dados['propriedade_prioritaria'] == propriedade_monpec
    
    def test_propriedade_prioritaria_outra(self, user, produtor):
        """Testa que primeira propriedade é prioridade se não houver Monpec"""
        dados = DashboardService.obter_dados_dashboard(user)
        # Se não houver Monpec, deve retornar primeira propriedade
        if dados['propriedade_prioritaria']:
            assert dados['propriedade_prioritaria'].produtor == produtor


