"""
Configuração global para testes pytest
"""
import pytest
from django.contrib.auth.models import User
from decimal import Decimal

from gestao_rural.models import ProdutorRural, Propriedade


@pytest.fixture
def user(db):
    """Cria um usuário de teste"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def admin_user(db):
    """Cria um usuário admin de teste"""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )


@pytest.fixture
def produtor(db, user):
    """Cria um produtor de teste"""
    return ProdutorRural.objects.create(
        nome='Teste Produtor',
        cpf_cnpj='12345678900',
        usuario_responsavel=user,
        email='produtor@example.com',
        telefone='(67) 99999-9999'
    )


@pytest.fixture
def propriedade(db, produtor):
    """Cria uma propriedade de teste"""
    return Propriedade.objects.create(
        produtor=produtor,
        nome_propriedade='Fazenda Teste',
        municipio='Campo Grande',
        uf='MS',
        area_total_ha=Decimal('100.00'),
        tipo_operacao='PECUARIA',
        tipo_ciclo_pecuario=['CICLO_COMPLETO'],
        tipo_propriedade='PROPRIA',
        valor_hectare_proprio=Decimal('5000.00'),
    )


@pytest.fixture
def client_logged_in(client, user):
    """Cliente de teste autenticado"""
    client.force_login(user)
    return client

