#!/usr/bin/env python
"""
SCRIPT PARA POPULAR DADOS NA PRODUÇÃO
Executa automaticamente após deploy no Google Cloud
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from gestao_rural.models import Propriedade, AnimalIndividual, CategoriaAnimal, InventarioRebanho
from gestao_rural.models_compras_financeiro import Fornecedor
from gestao_rural.models_funcionarios import Funcionario
from gestao_rural.models_controles_operacionais import Pastagem, Cocho
from gestao_rural.models_patrimonio import TipoBem, BemPatrimonial
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, datetime, timedelta
import random

User = get_user_model()

def criar_dados_producao_seguros():
    """Cria dados de produção de forma segura"""

    print("🔧 Populando dados na produção...")

    # 1. Verificar/Criar propriedade demo
    propriedade, created = Propriedade.objects.get_or_create(
        nome_propriedade='Fazenda Demonstracao',
        defaults={
            'area_total_ha': 1500.00,
            'municipio': 'Campo Grande',
            'uf': 'MS',
            'produtor': None  # Será definido depois
        }
    )

    if created:
        print("✅ Propriedade criada")
    else:
        print("✅ Propriedade já existe")

    # 2. Verificar/Criar usuário demo se necessário
    try:
        usuario_demo = User.objects.filter(username='demo_user').first()
        if not usuario_demo:
            usuario_demo = User.objects.create_user(
                username='demo_user',
                email='demo@monpec.com.br',
                password='demo123456',
                first_name='Usuário',
                last_name='Demonstração'
            )
            print("✅ Usuário demo criado")

        # Associar usuário à propriedade
        from gestao_rural.models import ProdutorRural
        produtor, created = ProdutorRural.objects.get_or_create(
            usuario_responsavel=usuario_demo,
            defaults={
                'cpf_cnpj': 'DEMO-000001',
                'nome_propriedade': 'Fazenda Demonstracao'
            }
        )

        propriedade.produtor = produtor
        propriedade.save()
        print("✅ Produtor associado à propriedade")

    except Exception as e:
        print(f"⚠️ Erro ao criar usuário: {e}")

    # 3. Criar animais (sempre, pois são muitos)
    try:
        # Criar categoria básica
        categoria, created = CategoriaAnimal.objects.get_or_create(
            nome='Vaca',
            sexo='F',
            defaults={'idade_minima_meses': 24, 'raca': 'NELORE', 'ativo': True}
        )

        # Contar animais existentes
        existentes = AnimalIndividual.objects.filter(propriedade=propriedade).count()
        print(f"Animais existentes: {existentes}")

        if existentes < 50:  # Se tem menos que 50, completar
            animais_a_criar = 50 - existentes

            for i in range(animais_a_criar):
                numero_brinco = f"DEMO{(existentes + i + 1):03d}"

                try:
                    AnimalIndividual.objects.get_or_create(
                        numero_brinco=numero_brinco,
                        propriedade=propriedade,
                        defaults={
                            'categoria': categoria,
                            'peso_atual_kg': 400 + random.randint(-50, 50),
                            'sexo': 'F',
                            'raca': 'NELORE',
                            'data_nascimento': date.today() - timedelta(days=random.randint(730, 1825)),
                            'data_aquisicao': date.today() - timedelta(days=random.randint(30, 365)),
                            'status': 'ATIVO',
                        }
                    )
                except Exception as e:
                    print(f"Erro animal {numero_brinco}: {e}")
                    continue

            print(f"✅ Criados {animais_a_criar} animais")
        else:
            print("✅ Animais já suficientes")

    except Exception as e:
        print(f"⚠️ Erro ao criar animais: {e}")

    # 4. Criar fornecedores básicos
    fornecedores_base = [
        {'nome': 'Nutripec MS', 'cpf_cnpj': '12.345.678/0001-90'},
        {'nome': 'Agropecuarista Silva', 'cpf_cnpj': '23.456.789/0001-80'},
        {'nome': 'Veterinaria Campo Grande', 'cpf_cnpj': '34.567.890/0001-70'},
        {'nome': 'Posto Rural', 'cpf_cnpj': '45.678.901/0001-60'},
        {'nome': 'Loja de Maquinas', 'cpf_cnpj': '56.789.012/0001-50'},
    ]

    for forn_data in fornecedores_base:
        try:
            fornecedor, created = Fornecedor.objects.get_or_create(
                nome=forn_data['nome'],
                propriedade=propriedade,
                defaults={'cpf_cnpj': forn_data['cpf_cnpj']}
            )
            if created:
                print(f"✅ Fornecedor criado: {forn_data['nome']}")
        except Exception as e:
            print(f"⚠️ Erro fornecedor {forn_data['nome']}: {e}")

    # 5. Criar funcionários básicos
    funcionarios_base = [
        {'nome': 'Joao Gerente', 'cpf': '123.456.789-01', 'cargo': 'Gerente'},
        {'nome': 'Maria Vaqueira', 'cpf': '234.567.890-12', 'cargo': 'Vaqueira'},
        {'nome': 'Pedro Capataz', 'cpf': '345.678.901-23', 'cargo': 'Capataz'},
        {'nome': 'Ana Veterinaria', 'cpf': '456.789.012-34', 'cargo': 'Veterinaria'},
        {'nome': 'Carlos Mecanico', 'cpf': '567.890.123-45', 'cargo': 'Mecanico'},
        {'nome': 'Roberto Tratador', 'cpf': '678.901.234-56', 'cargo': 'Tratador'},
    ]

    for func_data in funcionarios_base:
        try:
            Funcionario.objects.get_or_create(
                nome=func_data['nome'],
                propriedade=propriedade,
                defaults={
                    'cpf': func_data['cpf'],
                    'cargo': func_data['cargo'],
                    'salario_base': Decimal('2500.00'),
                    'situacao': 'ATIVO',
                    'data_admissao': date.today() - timedelta(days=random.randint(30, 365)),
                }
            )
        except Exception as e:
            print(f"⚠️ Erro funcionario {func_data['nome']}: {e}")

    # 6. Criar pastagens básicas
    pastagens_base = [
        {'nome': 'Pastagem Norte', 'area_ha': 300.0},
        {'nome': 'Pastagem Sul', 'area_ha': 250.0},
        {'nome': 'Pastagem Leste', 'area_ha': 200.0},
        {'nome': 'Pastagem Oeste', 'area_ha': 180.0},
        {'nome': 'Pastagem Central', 'area_ha': 400.0},
    ]

    for past_data in pastagens_base:
        try:
            Pastagem.objects.get_or_create(
                nome=past_data['nome'],
                propriedade=propriedade,
                defaults={'area_ha': Decimal(str(past_data['area_ha']))}
            )
        except Exception as e:
            print(f"⚠️ Erro pastagem {past_data['nome']}: {e}")

    # 7. Criar cochos
    cochos_base = [
        {'nome': 'Cocho 01', 'capacidade': 120},
        {'nome': 'Cocho 02', 'capacidade': 120},
        {'nome': 'Cocho 03', 'capacidade': 100},
        {'nome': 'Cocho Mineral 01', 'capacidade': 80},
        {'nome': 'Cocho Mineral 02', 'capacidade': 80},
    ]

    for cocho_data in cochos_base:
        try:
            Cocho.objects.get_or_create(
                nome=cocho_data['nome'],
                propriedade=propriedade,
                defaults={'capacidade_kg': cocho_data['capacidade']}
            )
        except Exception as e:
            print(f"⚠️ Erro cocho {cocho_data['nome']}: {e}")

    # 8. Criar bens patrimoniais básicos
    try:
        tipo_maquina, created = TipoBem.objects.get_or_create(
            nome='Maquinas Agricolas',
            categoria='MAQUINA',
            defaults={'taxa_depreciacao': Decimal('10.00')}
        )

        bens_base = [
            {'descricao': 'Trator Principal', 'valor': 350000.00},
            {'descricao': 'Caminhao', 'valor': 200000.00},
            {'descricao': 'Curral', 'valor': 150000.00},
            {'descricao': 'Pulverizador', 'valor': 80000.00},
        ]

        for bem_data in bens_base:
            try:
                BemPatrimonial.objects.get_or_create(
                    propriedade=propriedade,
                    descricao=bem_data['descricao'],
                    tipo_bem=tipo_maquina,
                    defaults={
                        'valor_aquisicao': Decimal(str(bem_data['valor'])),
                        'data_aquisicao': date.today() - timedelta(days=random.randint(365, 1825)),
                    }
                )
            except Exception as e:
                print(f"⚠️ Erro bem {bem_data['descricao']}: {e}")

    except Exception as e:
        print(f"⚠️ Erro ao criar bens patrimoniais: {e}")

    # 9. Estatísticas finais
    try:
        animais_final = AnimalIndividual.objects.filter(propriedade=propriedade).count()
        fornecedores_final = propriedade.fornecedores.count()
        funcionarios_final = propriedade.funcionarios.count()
        pastagens_final = Pastagem.objects.filter(propriedade=propriedade).count()
        bens_final = BemPatrimonial.objects.filter(propriedade=propriedade).count()

        print("\n📊 DADOS POPULADOS NA PRODUÇÃO:")
        print(f"   🐄 Animais: {animais_final}")
        print(f"   🛒 Fornecedores: {fornecedores_final}")
        print(f"   👥 Funcionários: {funcionarios_final}")
        print(f"   🌾 Pastagens: {pastagens_final}")
        print(f"   🏢 Bens Patrimoniais: {bens_final}")

    except Exception as e:
        print(f"⚠️ Erro ao contar dados finais: {e}")

    print("\n✅ POPULAÇÃO DE DADOS CONCLUÍDA!")
    print("Sistema pronto para uso em produção!")

if __name__ == '__main__':
    criar_dados_producao_seguros()


