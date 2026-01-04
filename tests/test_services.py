"""
Testes básicos para os serviços
"""
from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal

from gestao_rural.models import ProdutorRural, Propriedade
from gestao_rural.services.produtor_service import ProdutorService
from gestao_rural.services.propriedade_service import PropriedadeService
from gestao_rural.services.dashboard_service import DashboardService


class ProdutorServiceTest(TestCase):
    """Testes para ProdutorService"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_obter_produtores_do_usuario(self):
        """Testa se retorna apenas produtores do usuário"""
        # Criar produtor para o usuário
        produtor = ProdutorRural.objects.create(
            nome='Teste Produtor',
            cpf_cnpj='12345678900',
            usuario_responsavel=self.user
        )
        
        # Buscar produtores
        produtores = ProdutorService.obter_produtores_do_usuario(self.user)
        
        # Verificar
        self.assertEqual(produtores.count(), 1)
        self.assertEqual(produtores.first().nome, 'Teste Produtor')
    
    def test_pode_acessar_produtor(self):
        """Testa verificação de permissão"""
        # Criar produtor
        produtor = ProdutorRural.objects.create(
            nome='Teste Produtor',
            cpf_cnpj='12345678900',
            usuario_responsavel=self.user
        )
        
        # Verificar permissão
        pode_acessar = ProdutorService.pode_acessar_produtor(self.user, produtor)
        self.assertTrue(pode_acessar)
        
        # Criar outro usuário
        outro_user = User.objects.create_user(
            username='outro_user',
            email='outro@example.com',
            password='testpass123'
        )
        
        # Verificar que não pode acessar
        pode_acessar = ProdutorService.pode_acessar_produtor(outro_user, produtor)
        self.assertFalse(pode_acessar)


class PropriedadeServiceTest(TestCase):
    """Testes para PropriedadeService"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.produtor = ProdutorRural.objects.create(
            nome='Teste Produtor',
            cpf_cnpj='12345678900',
            usuario_responsavel=self.user
        )
    
    def test_obter_propriedades_do_usuario(self):
        """Testa se retorna apenas propriedades do usuário"""
        # Criar propriedade
        propriedade = Propriedade.objects.create(
            produtor=self.produtor,
            nome_propriedade='Teste Propriedade',
            municipio='Campo Grande',
            uf='MS',
            area_total_ha=Decimal('100.00'),
            tipo_operacao='PECUARIA',
        )
        
        # Buscar propriedades
        propriedades = PropriedadeService.obter_propriedades_do_usuario(self.user)
        
        # Verificar
        self.assertGreaterEqual(propriedades.count(), 1)
        self.assertIn(propriedade, propriedades)
    
    def test_pode_acessar_propriedade(self):
        """Testa verificação de permissão"""
        # Criar propriedade
        propriedade = Propriedade.objects.create(
            produtor=self.produtor,
            nome_propriedade='Teste Propriedade',
            municipio='Campo Grande',
            uf='MS',
            area_total_ha=Decimal('100.00'),
            tipo_operacao='PECUARIA',
        )
        
        # Verificar permissão
        pode_acessar = PropriedadeService.pode_acessar_propriedade(self.user, propriedade)
        self.assertTrue(pode_acessar)


class DashboardServiceTest(TestCase):
    """Testes para DashboardService"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.produtor = ProdutorRural.objects.create(
            nome='Teste Produtor',
            cpf_cnpj='12345678900',
            usuario_responsavel=self.user
        )
    
    def test_obter_dados_dashboard(self):
        """Testa obtenção de dados do dashboard"""
        # Criar propriedade
        propriedade = Propriedade.objects.create(
            produtor=self.produtor,
            nome_propriedade='Teste Propriedade',
            municipio='Campo Grande',
            uf='MS',
            area_total_ha=Decimal('100.00'),
            tipo_operacao='PECUARIA',
        )
        
        # Buscar dados
        dados = DashboardService.obter_dados_dashboard(self.user)
        
        # Verificar
        self.assertIn('produtores', dados)
        self.assertIn('propriedades', dados)
        self.assertIn('total_propriedades', dados)
        self.assertIn('total_area', dados)
        self.assertGreaterEqual(dados['total_propriedades'], 1)


