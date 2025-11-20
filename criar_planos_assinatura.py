"""
Script para criar planos de assinatura no sistema MONPEC
Execute: python311\python.exe criar_planos_assinatura.py
"""
import os
import sys
import django

# Configura o Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.utils.text import slugify
from gestao_rural.models import PlanoAssinatura

def criar_planos():
    print("=" * 60)
    print("CRIANDO PLANOS DE ASSINATURA - SISTEMA MONPEC")
    print("=" * 60)
    print()
    
    planos = [
        {
            'nome': 'Plano Básico',
            'descricao': 'Ideal para pequenos produtores rurais. Acesso completo aos módulos principais.',
            'preco_mensal': 99.00,
            'max_usuarios': 1,
            'modulos': ['pecuaria', 'financeiro', 'projetos', 'relatorios'],
            'stripe_price_id': 'price_basico_placeholder',  # Substituir pelo ID real do Stripe
        },
        {
            'nome': 'Plano Intermediário',
            'descricao': 'Para produtores que precisam de mais usuários e módulos adicionais.',
            'preco_mensal': 199.00,
            'max_usuarios': 3,
            'modulos': ['pecuaria', 'financeiro', 'projetos', 'compras', 'rastreabilidade', 'relatorios'],
            'stripe_price_id': 'price_intermediario_placeholder',  # Substituir pelo ID real do Stripe
        },
        {
            'nome': 'Plano Avançado',
            'descricao': 'Solução completa para fazendas maiores com múltiplos usuários.',
            'preco_mensal': 299.00,
            'max_usuarios': 10,
            'modulos': ['pecuaria', 'financeiro', 'projetos', 'compras', 'funcionarios', 'rastreabilidade', 'reproducao', 'relatorios'],
            'stripe_price_id': 'price_avancado_placeholder',  # Substituir pelo ID real do Stripe
        },
        {
            'nome': 'Plano Empresarial',
            'descricao': 'Para grandes empresas e consultorias. Usuários ilimitados e todos os módulos.',
            'preco_mensal': 499.00,
            'max_usuarios': 999,  # Praticamente ilimitado
            'modulos': ['pecuaria', 'financeiro', 'projetos', 'compras', 'funcionarios', 'rastreabilidade', 'reproducao', 'relatorios'],
            'stripe_price_id': 'price_empresarial_placeholder',  # Substituir pelo ID real do Stripe
        },
    ]
    
    criados = 0
    atualizados = 0
    
    for plano_data in planos:
        slug = slugify(plano_data['nome'])
        
        plano, created = PlanoAssinatura.objects.update_or_create(
            slug=slug,
            defaults={
                'nome': plano_data['nome'],
                'descricao': plano_data['descricao'],
                'stripe_price_id': plano_data['stripe_price_id'],
                'preco_mensal_referencia': plano_data['preco_mensal'],
                'max_usuarios': plano_data['max_usuarios'],
                'modulos_disponiveis': plano_data['modulos'],
                'ativo': True,
            }
        )
        
        if created:
            print(f"[OK] CRIADO: {plano.nome}")
            print(f"   - Preco: R$ {plano.preco_mensal_referencia:.2f}/mes")
            print(f"   - Maximo de usuarios: {plano.max_usuarios}")
            print(f"   - Modulos: {', '.join(plano.modulos_disponiveis)}")
            print(f"   - Stripe Price ID: {plano.stripe_price_id}")
            print(f"   [ATENCAO] IMPORTANTE: Atualize o Stripe Price ID no admin!")
            criados += 1
        else:
            print(f"[ATUALIZADO] {plano.nome}")
            print(f"   - Preco: R$ {plano.preco_mensal_referencia:.2f}/mes")
            print(f"   - Maximo de usuarios: {plano.max_usuarios}")
            print(f"   - Modulos: {', '.join(plano.modulos_disponiveis)}")
            atualizados += 1
        print()
    
    print("=" * 60)
    print(f"RESUMO:")
    print(f"  [OK] {criados} plano(s) criado(s)")
    print(f"  [ATUALIZADO] {atualizados} plano(s) atualizado(s)")
    print("=" * 60)
    print()
    print("[ATENCAO] PROXIMOS PASSOS:")
    print()
    print("1. Acesse o Admin Django: /admin/gestao_rural/planoassinatura/")
    print("2. Para cada plano, atualize o 'Stripe Price ID' com o ID real do Stripe")
    print("3. Para criar produtos no Stripe:")
    print("   - Acesse: https://dashboard.stripe.com/products")
    print("   - Crie um produto para cada plano")
    print("   - Configure preço recorrente mensal")
    print("   - Copie o Price ID (começa com 'price_')")
    print("   - Cole no campo 'Stripe Price ID' no admin")
    print()
    print("=" * 60)

if __name__ == '__main__':
    criar_planos()

