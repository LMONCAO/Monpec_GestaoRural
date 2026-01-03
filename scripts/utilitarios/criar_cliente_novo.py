"""
Script para criar um novo cliente com banco de dados vazio
Uso: python311\python.exe criar_cliente_novo.py
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
    if created:
        print(f"✓ Plano padrão criado: {plano.nome}")
    else:
        print(f"✓ Usando plano existente: {plano.nome}")
    return plano


def criar_cliente_novo():
    """Cria um novo cliente com banco de dados vazio"""
    print("=" * 70)
    print("CRIAÇÃO DE CLIENTE NOVO - SISTEMA MONPEC")
    print("=" * 70)
    print()
    
    # Coletar informações do usuário
    print("Informe os dados do novo cliente:")
    print()
    
    nome_completo = input("Nome completo: ").strip()
    if not nome_completo:
        print("ERRO: Nome completo é obrigatório!")
        return False
    
    email = input("E-mail: ").strip().lower()
    if not email:
        print("ERRO: E-mail é obrigatório!")
        return False
    
    # Verificar se email já existe
    if User.objects.filter(email__iexact=email).exists():
        print(f"ERRO: O e-mail '{email}' já está cadastrado!")
        return False
    
    username = input(f"Username (deixe em branco para usar '{email.split('@')[0]}'): ").strip()
    if not username:
        username = email.split('@')[0]
    
    # Verificar se username já existe
    if User.objects.filter(username=username).exists():
        print(f"ERRO: O username '{username}' já está em uso!")
        return False
    
    senha = input("Senha: ").strip()
    if not senha:
        print("ERRO: Senha é obrigatória!")
        return False
    
    # Validar senha
    try:
        validar_senha_forte(senha)
    except Exception as e:
        print(f"ERRO na senha: {e}")
        return False
    
    # Dados do produtor rural
    print()
    print("Dados do Produtor Rural:")
    cpf_cnpj = input("CPF/CNPJ: ").strip()
    if not cpf_cnpj:
        print("ERRO: CPF/CNPJ é obrigatório!")
        return False
    
    # Verificar se CPF/CNPJ já existe
    if ProdutorRural.objects.filter(cpf_cnpj=cpf_cnpj).exists():
        print(f"ERRO: O CPF/CNPJ '{cpf_cnpj}' já está cadastrado!")
        return False
    
    telefone = input("Telefone (opcional): ").strip() or None
    endereco_produtor = input("Endereço do produtor (opcional): ").strip() or None
    
    # Dados da propriedade
    print()
    print("Dados da Propriedade:")
    nome_propriedade = input("Nome da propriedade: ").strip()
    if not nome_propriedade:
        print("ERRO: Nome da propriedade é obrigatório!")
        return False
    
    municipio = input("Município: ").strip()
    if not municipio:
        print("ERRO: Município é obrigatório!")
        return False
    
    uf = input("UF (2 letras): ").strip().upper()
    if not uf or len(uf) != 2:
        print("ERRO: UF deve ter 2 letras!")
        return False
    
    area_total = input("Área total (hectares): ").strip()
    try:
        area_total_decimal = Decimal(area_total)
        if area_total_decimal <= 0:
            raise ValueError("Área deve ser maior que zero")
    except (ValueError, Exception) as e:
        print(f"ERRO: Área inválida: {e}")
        return False
    
    tipo_ciclo = input("Tipo de ciclo pecuário (CRIA/RECRIA/ENGORDA/CICLO_COMPLETO) [CICLO_COMPLETO]: ").strip().upper()
    if not tipo_ciclo:
        tipo_ciclo = 'CICLO_COMPLETO'
    if tipo_ciclo not in ['CRIA', 'RECRIA', 'ENGORDA', 'CICLO_COMPLETO']:
        tipo_ciclo = 'CICLO_COMPLETO'
    
    tipo_propriedade = input("Tipo de propriedade (PROPRIA/ARRENDAMENTO) [PROPRIA]: ").strip().upper()
    if not tipo_propriedade:
        tipo_propriedade = 'PROPRIA'
    if tipo_propriedade not in ['PROPRIA', 'ARRENDAMENTO']:
        tipo_propriedade = 'PROPRIA'
    
    # Confirmar criação
    print()
    print("=" * 70)
    print("RESUMO DOS DADOS:")
    print("=" * 70)
    print(f"Nome: {nome_completo}")
    print(f"E-mail: {email}")
    print(f"Username: {username}")
    print(f"CPF/CNPJ: {cpf_cnpj}")
    print(f"Propriedade: {nome_propriedade}")
    print(f"Localização: {municipio}/{uf}")
    print(f"Área: {area_total} ha")
    print("=" * 70)
    print()
    
    confirmar = input("Confirmar criação? (s/N): ").strip().lower()
    if confirmar not in ['s', 'sim', 'y', 'yes']:
        print("Operação cancelada.")
        return False
    
    # Criar tudo em uma transação
    try:
        with transaction.atomic():
            # 1. Criar usuário
            print("\n[1/5] Criando usuário...")
            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=senha,
                first_name=nome_completo.split(' ')[0] if nome_completo else '',
                last_name=' '.join(nome_completo.split(' ')[1:]) if len(nome_completo.split(' ')) > 1 else '',
                is_active=True,
            )
            print(f"   ✓ Usuário criado: {usuario.username}")
            
            # 2. Obter ou criar plano
            print("\n[2/5] Configurando plano...")
            plano = obter_ou_criar_plano_padrao()
            
            # 3. Criar assinatura
            print("\n[3/5] Criando assinatura...")
            assinatura = AssinaturaCliente.objects.create(
                usuario=usuario,
                plano=plano,
                status=AssinaturaCliente.Status.ATIVA,
            )
            print(f"   ✓ Assinatura criada (ID: {assinatura.id})")
            
            # 4. Criar produtor rural
            print("\n[4/5] Criando produtor rural...")
            produtor = ProdutorRural.objects.create(
                nome=nome_completo,
                cpf_cnpj=cpf_cnpj,
                usuario_responsavel=usuario,
                telefone=telefone,
                endereco=endereco_produtor,
            )
            print(f"   ✓ Produtor criado: {produtor.nome}")
            
            # Vincular produtor à assinatura
            assinatura.produtor = produtor
            assinatura.save(update_fields=['produtor'])
            
            # 5. Criar propriedade
            print("\n[5/5] Criando propriedade...")
            propriedade = Propriedade.objects.create(
                nome_propriedade=nome_propriedade,
                produtor=produtor,
                municipio=municipio,
                uf=uf,
                area_total_ha=area_total_decimal,
                tipo_operacao='PECUARIA',
                tipo_ciclo_pecuario=[tipo_ciclo],
                tipo_propriedade=tipo_propriedade,
            )
            print(f"   ✓ Propriedade criada: {propriedade.nome_propriedade}")
            
            # O TenantUsuario será criado automaticamente pelo signal
            # Mas vamos garantir que existe
            tenant_usuario, created = TenantUsuario.objects.get_or_create(
                usuario=usuario,
                defaults={
                    'assinatura': assinatura,
                    'nome_exibicao': nome_completo,
                    'email': email,
                    'perfil': TenantUsuario.Perfil.ADMIN,
                    'ativo': True,
                }
            )
            if created:
                print(f"   ✓ Perfil de tenant criado")
            else:
                print(f"   ✓ Perfil de tenant já existe")
        
        print()
        print("=" * 70)
        print("✓ CLIENTE CRIADO COM SUCESSO!")
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
        criar_cliente_novo()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()


