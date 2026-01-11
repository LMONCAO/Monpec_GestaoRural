#!/usr/bin/env python
"""
SCRIPT PARA POPULAR DADOS COMPLETOS NA PRODUÇÃO
Inclui os 1300 animais, planejamento e todos os dados criados
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings_gcp')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model
from gestao_rural.models import Propriedade, ProdutorRural
from decimal import Decimal

User = get_user_model()

def popular_dados_completos():
    """Popula todos os dados criados no desenvolvimento"""

    print("🚀 Populando dados completos de produção...")

    try:
        # 1. Criar/verificar administrador
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@monpec.com.br',
                'is_superuser': True,
                'is_staff': True
            }
        )
        if created:
            admin_user.set_password('L6171r12@@')
            admin_user.save()
            print("✅ Admin criado")

        # 2. Criar produtor para admin
        produtor_admin, created = ProdutorRural.objects.get_or_create(
            usuario_responsavel=admin_user,
            defaults={
                'nome': 'Produtor Admin',
                'cpf_cnpj': '00000000000',
                'email': 'admin@monpec.com.br'
            }
        )
        print(f"✅ Produtor admin: {'criado' if created else 'já existe'}")

        # 3. Criar propriedade grande para admin (ID 5)
        propriedade_grande, created = Propriedade.objects.get_or_create(
            produtor=produtor_admin,
            nome_propriedade='Fazenda Grande Demonstracao',
            defaults={
                'municipio': 'Campo Grande',
                'uf': 'MS',
                'area_total_ha': Decimal('5000.00'),
                'tipo_operacao': 'PECUARIA',
                'tipo_ciclo_pecuario': ['CICLO_COMPLETO'],
                'tipo_propriedade': 'PROPRIA',
                'valor_hectare_proprio': Decimal('12000.00')
            }
        )
        print(f"✅ Propriedade grande (ID {propriedade_grande.id}): {'criada' if created else 'já existe'}")

        # 4. Executar comando para popular dados completos
        print("📊 Executando popular_fazenda_grande_demo...")
        try:
            call_command('popular_fazenda_grande_demo', propriedade_id=propriedade_grande.id, force=True, verbosity=1)
            print("✅ Dados da fazenda grande populados")
        except Exception as e:
            print(f"⚠️ Erro ao popular fazenda grande: {e}")

        # 5. Executar comando para criar planejamento
        print("📅 Criando planejamento 2026...")
        try:
            call_command('criar_planejamento_2026', propriedade_id=propriedade_grande.id, verbosity=1)
            print("✅ Planejamento 2026 criado")
        except Exception as e:
            print(f"⚠️ Erro ao criar planejamento: {e}")

        # 6. Verificar dados finais
        from gestao_rural.models import AnimalIndividual, InventarioRebanho, PlanejamentoAnual

        animais_count = AnimalIndividual.objects.filter(propriedade=propriedade_grande).count()
        inventario_count = InventarioRebanho.objects.filter(propriedade=propriedade_grande).count()
        planejamento_count = PlanejamentoAnual.objects.filter(propriedade=propriedade_grande).count()

        print("📋 Verificação final:")
        print(f"   🐄 Animais individuais: {animais_count}")
        print(f"   📊 Registros de inventário: {inventario_count}")
        print(f"   📅 Planejamentos: {planejamento_count}")

        if animais_count >= 1300 and planejamento_count >= 1:
            print("✅✅✅ DADOS POPULADOS COM SUCESSO! ✅✅✅")
        else:
            print("⚠️ Alguns dados podem não ter sido populados completamente")

    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    popular_dados_completos()