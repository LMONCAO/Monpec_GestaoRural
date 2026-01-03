"""
Script simplificado para criar um novo cliente com banco de dados vazio
Uso: python311\python.exe criar_cliente_novo_simples.py nome email senha cpf_cnpj propriedade municipio uf area

Exemplo:
python311\python.exe criar_cliente_novo_simples.py "João Silva" joao@email.com senha123 12345678900 "Fazenda Teste" "São Paulo" SP 1000
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


def criar_cliente_novo(
    nome_completo,
    email,
    senha,
    cpf_cnpj,
    nome_propriedade,
    municipio,
    uf,
    area_total,
    username=None,
    telefone=None,
    endereco_produtor=None,
    tipo_ciclo='CICLO_COMPLETO',
    tipo_propriedade='PROPRIA'
):
    """Cria um novo cliente com banco de dados vazio"""
    
    # Validações básicas
    if not nome_completo or not email or not senha or not cpf_cnpj:
        raise ValueError("Nome, e-mail, senha e CPF/CNPJ são obrigatórios")
    
    if not nome_propriedade or not municipio or not uf or not area_total:
        raise ValueError("Dados da propriedade são obrigatórios")
    
    # Normalizar email
    email = email.lower().strip()
    
    # Verificar se email já existe
    if User.objects.filter(email__iexact=email).exists():
        raise ValueError(f"O e-mail '{email}' já está cadastrado")
    
    # Gerar username se não fornecido
    if not username:
        username = email.split('@')[0]
    
    # Verificar se username já existe
    if User.objects.filter(username=username).exists():
        # Tentar adicionar sufixo
        sufixo = 1
        username_base = username
        while User.objects.filter(username=username).exists():
            username = f"{username_base}{sufixo}"
            sufixo += 1
    
    # Validar senha
    try:
        validar_senha_forte(senha)
    except Exception as e:
        raise ValueError(f"Senha inválida: {e}")
    
    # Verificar se CPF/CNPJ já existe
    if ProdutorRural.objects.filter(cpf_cnpj=cpf_cnpj).exists():
        raise ValueError(f"O CPF/CNPJ '{cpf_cnpj}' já está cadastrado")
    
    # Converter área
    try:
        area_total_decimal = Decimal(str(area_total))
        if area_total_decimal <= 0:
            raise ValueError("Área deve ser maior que zero")
    except (ValueError, Exception) as e:
        raise ValueError(f"Área inválida: {e}")
    
    # Normalizar UF
    uf = uf.upper().strip()
    if len(uf) != 2:
        raise ValueError("UF deve ter 2 letras")
    
    # Normalizar tipo de ciclo
    tipo_ciclo = tipo_ciclo.upper().strip()
    if tipo_ciclo not in ['CRIA', 'RECRIA', 'ENGORDA', 'CICLO_COMPLETO']:
        tipo_ciclo = 'CICLO_COMPLETO'
    
    # Normalizar tipo de propriedade
    tipo_propriedade = tipo_propriedade.upper().strip()
    if tipo_propriedade not in ['PROPRIA', 'ARRENDAMENTO']:
        tipo_propriedade = 'PROPRIA'
    
    # Criar tudo em uma transação
    with transaction.atomic():
        # 1. Criar usuário
        usuario = User.objects.create_user(
            username=username,
            email=email,
            password=senha,
            first_name=nome_completo.split(' ')[0] if nome_completo else '',
            last_name=' '.join(nome_completo.split(' ')[1:]) if len(nome_completo.split(' ')) > 1 else '',
            is_active=True,
        )
        
        # 2. Obter ou criar plano
        plano = obter_ou_criar_plano_padrao()
        
        # 3. Criar assinatura
        assinatura = AssinaturaCliente.objects.create(
            usuario=usuario,
            plano=plano,
            status=AssinaturaCliente.Status.ATIVA,
        )
        
        # 4. Criar produtor rural
        produtor = ProdutorRural.objects.create(
            nome=nome_completo,
            cpf_cnpj=cpf_cnpj,
            usuario_responsavel=usuario,
            telefone=telefone,
            endereco=endereco_produtor,
        )
        
        # Vincular produtor à assinatura
        assinatura.produtor = produtor
        assinatura.save(update_fields=['produtor'])
        
        # 5. Criar propriedade
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
        
        return {
            'usuario': usuario,
            'assinatura': assinatura,
            'produtor': produtor,
            'propriedade': propriedade,
        }


if __name__ == '__main__':
    print("=" * 70)
    print("CRIAÇÃO DE CLIENTE NOVO - SISTEMA MONPEC")
    print("=" * 70)
    print()
    
    # Verificar argumentos
    if len(sys.argv) < 9:
        print("Uso: python311\\python.exe criar_cliente_novo_simples.py")
        print("     nome email senha cpf_cnpj propriedade municipio uf area")
        print()
        print("Exemplo:")
        print('  python311\\python.exe criar_cliente_novo_simples.py')
        print('    "João Silva" joao@email.com senha123 12345678900')
        print('    "Fazenda Teste" "São Paulo" SP 1000')
        print()
        print("Parâmetros opcionais (após os obrigatórios):")
        print("  username telefone endereco tipo_ciclo tipo_propriedade")
        sys.exit(1)
    
    try:
        nome_completo = sys.argv[1]
        email = sys.argv[2]
        senha = sys.argv[3]
        cpf_cnpj = sys.argv[4]
        nome_propriedade = sys.argv[5]
        municipio = sys.argv[6]
        uf = sys.argv[7]
        area_total = sys.argv[8]
        
        username = sys.argv[9] if len(sys.argv) > 9 else None
        telefone = sys.argv[10] if len(sys.argv) > 10 else None
        endereco_produtor = sys.argv[11] if len(sys.argv) > 11 else None
        tipo_ciclo = sys.argv[12] if len(sys.argv) > 12 else 'CICLO_COMPLETO'
        tipo_propriedade = sys.argv[13] if len(sys.argv) > 13 else 'PROPRIA'
        
        resultado = criar_cliente_novo(
            nome_completo=nome_completo,
            email=email,
            senha=senha,
            cpf_cnpj=cpf_cnpj,
            nome_propriedade=nome_propriedade,
            municipio=municipio,
            uf=uf,
            area_total=area_total,
            username=username,
            telefone=telefone,
            endereco_produtor=endereco_produtor,
            tipo_ciclo=tipo_ciclo,
            tipo_propriedade=tipo_propriedade,
        )
        
        print()
        print("=" * 70)
        print("✓ CLIENTE CRIADO COM SUCESSO!")
        print("=" * 70)
        print()
        print("DADOS DE ACESSO:")
        print(f"  Username: {resultado['usuario'].username}")
        print(f"  E-mail: {resultado['usuario'].email}")
        print(f"  Senha: {senha}")
        print()
        print("ESTRUTURA CRIADA:")
        print(f"  • Usuário: {resultado['usuario'].get_full_name() or resultado['usuario'].username}")
        print(f"  • Assinatura: {resultado['assinatura'].id} ({resultado['assinatura'].get_status_display()})")
        print(f"  • Produtor: {resultado['produtor'].nome}")
        print(f"  • Propriedade: {resultado['propriedade'].nome_propriedade}")
        print()
        print("O banco de dados está vazio (sem animais, movimentações, etc.)")
        print("O cliente pode começar a usar o sistema normalmente.")
        print("=" * 70)
        
    except Exception as e:
        print()
        print("=" * 70)
        print("ERRO ao criar cliente:")
        print("=" * 70)
        print(str(e))
        print()
        import traceback
        traceback.print_exc()
        sys.exit(1)


