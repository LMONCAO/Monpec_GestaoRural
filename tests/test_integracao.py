"""
Testes de integração - fluxos completos
"""
import pytest
from django.urls import reverse
from decimal import Decimal

from gestao_rural.models import (
    ProdutorRural, 
    Propriedade, 
    InventarioRebanho, 
    CategoriaAnimal,
    ParametrosProjecaoRebanho
)


@pytest.mark.django_db
class TestFluxoCompleto:
    """Testes de fluxos completos do sistema"""
    
    def test_fluxo_criar_produtor_e_propriedade(self, client_logged_in, user):
        """Testa fluxo completo: criar produtor -> criar propriedade"""
        # 1. Criar produtor
        data_produtor = {
            'nome': 'Novo Produtor',
            'cpf_cnpj': '11111111111',
            'email': 'novo@example.com',
        }
        response = client_logged_in.post(reverse('produtor_novo'), data_produtor)
        assert response.status_code == 302
        
        produtor = ProdutorRural.objects.get(cpf_cnpj='11111111111')
        assert produtor.usuario_responsavel == user
        
        # 2. Criar propriedade
        data_propriedade = {
            'produtor': produtor.id,
            'nome_propriedade': 'Nova Fazenda',
            'municipio': 'Campo Grande',
            'uf': 'MS',
            'area_total_ha': '150.00',
            'tipo_operacao': 'PECUARIA',
            'tipo_ciclo_pecuario': ['CICLO_COMPLETO'],
            'tipo_propriedade': 'PROPRIA',
        }
        response = client_logged_in.post(
            reverse('propriedade_nova', args=[produtor.id]),
            data_propriedade
        )
        assert response.status_code == 302
        
        propriedade = Propriedade.objects.get(nome_propriedade='Nova Fazenda')
        assert propriedade.produtor == produtor
    
    def test_fluxo_pecuaria_completo(self, client_logged_in, propriedade):
        """Testa fluxo completo de pecuária: parâmetros -> inventário"""
        # 1. Configurar parâmetros
        data_parametros = {
            'taxa_natalidade_anual': '85.00',
            'taxa_mortalidade_bezerros_anual': '5.00',
            'taxa_mortalidade_adultos_anual': '2.00',
            'percentual_venda_machos_anual': '90.00',
            'percentual_venda_femeas_anual': '10.00',
            'periodicidade': 'MENSAL',
        }
        response = client_logged_in.post(
            reverse('pecuaria_parametros', args=[propriedade.id]),
            data_parametros
        )
        assert response.status_code == 302
        
        # Verificar parâmetros
        parametros = ParametrosProjecaoRebanho.objects.get(propriedade=propriedade)
        assert parametros.taxa_natalidade_anual == Decimal('85.00')
        
        # 2. Criar categoria e inventário
        categoria = CategoriaAnimal.objects.create(
            nome='Bezerro',
            sexo='M',
            raca='Nelore',
            idade_minima_meses=0,
            ativo=True
        )
        
        from django.utils import timezone
        inventario = InventarioRebanho.objects.create(
            propriedade=propriedade,
            categoria=categoria,
            quantidade=20,
            valor_por_cabeca=Decimal('500.00'),
            data_inventario=timezone.now().date(),
        )
        
        # Verificar inventário
        assert inventario.propriedade == propriedade
        assert inventario.quantidade == 20
    
    def test_fluxo_edicao_completa(self, client_logged_in, produtor, propriedade):
        """Testa fluxo completo de edição: produtor -> propriedade"""
        # 1. Editar produtor
        data_produtor = {
            'nome': 'Produtor Editado',
            'cpf_cnpj': produtor.cpf_cnpj,
            'email': 'editado@example.com',
        }
        response = client_logged_in.post(
            reverse('produtor_editar', args=[produtor.id]),
            data_produtor
        )
        assert response.status_code == 302
        
        produtor.refresh_from_db()
        assert produtor.nome == 'Produtor Editado'
        
        # 2. Editar propriedade
        data_propriedade = {
            'produtor': produtor.id,
            'nome_propriedade': 'Fazenda Editada',
            'municipio': propriedade.municipio,
            'uf': propriedade.uf,
            'area_total_ha': str(propriedade.area_total_ha),
            'tipo_operacao': propriedade.tipo_operacao,
            'tipo_ciclo_pecuario': propriedade.tipo_ciclo_pecuario,
            'tipo_propriedade': propriedade.tipo_propriedade,
        }
        response = client_logged_in.post(
            reverse('propriedade_editar', args=[propriedade.id]),
            data_propriedade
        )
        assert response.status_code == 302
        
        propriedade.refresh_from_db()
        assert propriedade.nome_propriedade == 'Fazenda Editada'


