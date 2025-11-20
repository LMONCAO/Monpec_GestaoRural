#!/usr/bin/env python
"""
Script para criar planos de assinatura automaticamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from gestao_rural.models import PlanoAssinatura

def criar_planos():
    """Cria planos de assinatura padrão"""
    print("🛒 Criando planos de assinatura...")
    print("")
    
    planos = [
        {
            'slug': 'basico',
            'nome': 'Básico',
            'descricao': 'Plano ideal para pequenos produtores. Inclui gestão básica de rebanho e relatórios simples.',
            'preco_mensal_referencia': 99.00,
        },
        {
            'slug': 'profissional',
            'nome': 'Profissional',
            'descricao': 'Plano completo para médios produtores. Inclui todas as funcionalidades básicas mais projeções e análises avançadas.',
            'preco_mensal_referencia': 199.00,
        },
        {
            'slug': 'enterprise',
            'nome': 'Enterprise',
            'descricao': 'Plano completo para grandes propriedades. Inclui todas as funcionalidades, suporte prioritário e integrações avançadas.',
            'preco_mensal_referencia': 399.00,
        },
    ]
    
    for plano_data in planos:
        plano, created = PlanoAssinatura.objects.get_or_create(
            slug=plano_data['slug'],
            defaults={
                **plano_data,
                'ativo': True,
            }
        )
        if created:
            print(f"✅ Plano '{plano.nome}' criado com sucesso!")
            print(f"   Preço: R$ {plano.preco_mensal_referencia:.2f}/mês")
        else:
            print(f"ℹ️ Plano '{plano.nome}' já existe")
            # Atualizar se necessário
            plano.ativo = True
            plano.save()
    
    print("")
    print("🎉 Processo concluído!")
    print("")
    print("📋 Planos disponíveis:")
    for plano in PlanoAssinatura.objects.filter(ativo=True):
        print(f"   • {plano.nome} - R$ {plano.preco_mensal_referencia:.2f}/mês")
    print("")
    print("🌐 Acesse: http://localhost:8000/assinaturas/")

if __name__ == '__main__':
    try:
        criar_planos()
    except Exception as e:
        print(f"❌ Erro ao criar planos: {e}")
        import traceback
        traceback.print_exc()




