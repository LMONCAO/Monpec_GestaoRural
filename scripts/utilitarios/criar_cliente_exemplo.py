"""
Script de exemplo para criar um cliente novo rapidamente
Modifique os dados abaixo e execute: python311\python.exe criar_cliente_exemplo.py
"""
import os
import sys
import django
from decimal import Decimal

# Configura o Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistema_rural.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from gestao_rural.models import (
    PlanoAssinatura,
    AssinaturaCliente,
    ProdutorRural,
    Propriedade,
    TenantUsuario
)
from gestao_rural.security import validar_senha_forte


def obter_ou_criar_plano_padrao():
    """Obtém ou cria um plano padrão para novos clientes"""
    plano, created = PlanoAssinatura.objects.get_or_create(
        slug='plano-basico',
        defaults={
            'nome': 'Plano Básico',
            'descricao': 'Plano básico para novos clientes',
            'stripe_price_id': 'plano_basico_local',
            'preco_mensal_referencia': Decimal('0.00'),
            'max_usuarios': 5,
            'modulos_disponiveis': PlanoAssinatura.MODULOS_PADRAO,
            'ativo': True,
        }
    )
    return plano


def criar_cliente_exemplo():
    """Cria um cliente de exemplo - MODIFIQUE OS DADOS AQUI"""
    
    # ============================================
    # MODIFIQUE ESTES DADOS CONFORME NECESSÁRIO
    # ============================================
    nome_completo = "Cliente Novo Exemplo"
    email = "monpec@exemplo.com"
    senha = "monpec123"
    username = "monpec"
    cpf_cnpj = "98765432100"
    telefone = "(11) 99999-9999"
    endereco_produtor = "Rua Exemplo, 123 - Centro"
    
    nome_propriedade = "Fazenda Exemplo"
    municipio = "São Paulo"
    uf = "SP"
    area_total = Decimal("1000.00")
    tipo_ciclo = "CICLO_COMPLETO"
    tipo_propriedade = "PROPRIA"
    # ============================================
    
    print("=" * 70)
    print("CRIAÇÃO DE CLIENTE NOVO - SISTEMA MONPEC")
    print("=" * 70)
    print()
    print("DADOS QUE SERÃO CRIADOS:")
    print(f"  Nome: {nome_completo}")
    print(f"  E-mail: {email}")
    print(f"  Username: {username}")
    print(f"  CPF/CNPJ: {cpf_cnpj}")
    print(f"  Propriedade: {nome_propriedade}")
    print(f"  Localização: {municipio}/{uf}")
    print(f"  Área: {area_total} ha")
    print()
    
    # Validações
    if User.objects.filter(email__iexact=email).exists():
        print(f"ERRO: O e-mail '{email}' já está cadastrado!")
        print("Por favor, modifique o e-mail no script.")
        return False
    
    if User.objects.filter(username=username).exists():
        print(f"ERRO: O username '{username}' já está em uso!")
        print("Por favor, modifique o username no script.")
        return False
    
    if ProdutorRural.objects.filter(cpf_cnpj=cpf_cnpj).exists():
        print(f"ERRO: O CPF/CNPJ '{cpf_cnpj}' já está cadastrado!")
        print("Por favor, modifique o CPF/CNPJ no script.")
        return False
    
    # Validar senha (permitir senha monpec123 para este caso específico)
    try:
        if senha.lower() != "monpec123":
            validar_senha_forte(senha)
        else:
            print("Aviso: Usando senha simplificada 'monpec123' (apenas para desenvolvimento/teste)")
    except Exception as e:
        print(f"ERRO na senha: {e}")
        print("Por favor, use uma senha mais forte.")
        return False
    
    print("Criando cliente...")
    print()
    
    # Criar tudo em uma transação
    try:
        with transaction.atomic():
            # 1. Criar usuário
            print("[1/5] Criando usuário...")
            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=nome_completo.split(' ')[0] if nome_completo else '',
                last_name=' '.join(nome_completo.split(' ')[1:]) if len(nome_completo.split(' ')) > 1 else '',
                is_active=True,
            )
            print(f"   [OK] Usuario criado: {usuario.username}")
            
            # 2. Obter ou criar plano
            print("[2/5] Configurando plano...")
            plano = obter_ou_criar_plano_padrao()
            print(f"   [OK] Plano: {plano.nome}")
            
            # 3. Criar assinatura
            print("[3/5] Criando assinatura...")
            assinatura = AssinaturaCliente.objects.create(
                usuario=usuario,
                plano=plano,
                status=AssinaturaCliente.Status.ATIVA,
            )
            print(f"   [OK] Assinatura criada (ID: {assinatura.id})")
            
            # 4. Criar produtor rural
            print("[4/5] Criando produtor rural...")
            produtor = ProdutorRural.objects.create(
                nome=nome_completo,
                cpf_cnpj=cpf_cnpj,
                usuario_responsavel=usuario,
                telefone=telefone,
                endereco=endereco_produtor,
            )
            print(f"   [OK] Produtor criado: {produtor.nome}")
            
            # Vincular produtor à assinatura
            assinatura.produtor = produtor
            assinatura.save(update_fields=['produtor'])
            
            # 5. Criar propriedade
            print("[5/5] Criando propriedade...")
            propriedade = Propriedade.objects.create(
                nome_propriedade=nome_propriedade,
                produtor=produtor,
                municipio=municipio,
                uf=uf,
                area_total_ha=area_total,
                tipo_operacao='PECUARIA',
                tipo_ciclo_pecuario=[tipo_ciclo],
                tipo_propriedade=tipo_propriedade,
            )
            print(f"   [OK] Propriedade criada: {propriedade.nome_propriedade}")
            
            # Garantir que TenantUsuario existe
            TenantUsuario.objects.get_or_create(
                usuario=usuario,
                defaults={
                    'assinatura': assinatura,
                    'nome_exibicao': nome_completo,
                    'email': email,
                    'perfil': TenantUsuario.Perfil.ADMIN,
                    'ativo': True,
                }
            )
            print(f"   [OK] Perfil de tenant criado")
        
        print()
        print("=" * 70)
        print("[SUCESSO] CLIENTE CRIADO COM SUCESSO!")
        print("=" * 70)
        print()
        print("DADOS DE ACESSO:")
        print(f"  Username: {username}")
        print(f"  E-mail: {email}")
        print(f"  Senha: {senha}")
        print()
        print("ESTRUTURA CRIADA:")
        print(f"  • Usuário: {usuario.get_full_name() or usuario.username}")
        print(f"  • Assinatura: {assinatura.id} ({assinatura.get_status_display()})")
        print(f"  • Produtor: {produtor.nome}")
        print(f"  • Propriedade: {propriedade.nome_propriedade}")
        print()
        print("O banco de dados está vazio (sem animais, movimentações, etc.)")
        print("O cliente pode começar a usar o sistema normalmente.")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 70)
        print("ERRO ao criar cliente:")
        print("=" * 70)
        print(str(e))
        print()
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    try:
        criar_cliente_exemplo()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()


