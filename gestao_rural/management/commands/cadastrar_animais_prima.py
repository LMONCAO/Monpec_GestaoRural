"""
Django management command para cadastrar animais da Prima com dados completos.
Inclui pesagens, vacinas, movimentações e dados reprodutivos.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import date, timedelta, datetime
from decimal import Decimal
import random
import os

from gestao_rural.models import (
    Propriedade, AnimalIndividual, CategoriaAnimal,
    AnimalPesagem, AnimalVacinaAplicada, MovimentacaoIndividual,
    CurralEvento, CurralSessao, BrincoAnimal
)
from django.db.models import Q


def extrair_numero_manejo(codigo):
    """Extrai número de manejo do código SISBOV (6 dígitos das posições 8-13)"""
    codigo_str = str(codigo).strip()
    if len(codigo_str) >= 13:
        return codigo_str[7:13]  # Posições 8-13 (índices 7-12)
    return codigo_str[-6:] if len(codigo_str) >= 6 else codigo_str


def normalizar_codigo(codigo):
    """Remove asteriscos e espaços do código"""
    return str(codigo).strip().rstrip('*').strip()


def categoria_padrao_para(sexo, idade_meses=None):
    """Retorna categoria padrão baseada no sexo e idade"""
    sexo = sexo.upper()
    
    if idade_meses is None:
        idade_meses = random.randint(12, 60)
    
    if sexo == 'F':
        if idade_meses < 12:
            return CategoriaAnimal.objects.filter(
                nome__icontains='bezerro',
                sexo='F',
                ativo=True
            ).first()
        elif idade_meses < 24:
            return CategoriaAnimal.objects.filter(
                nome__icontains='novilha',
                sexo='F',
                ativo=True
            ).first()
        else:
            return CategoriaAnimal.objects.filter(
                nome__icontains='vaca',
                sexo='F',
                ativo=True
            ).first()
    else:  # M
        if idade_meses < 12:
            return CategoriaAnimal.objects.filter(
                nome__icontains='bezerro',
                sexo='M',
                ativo=True
            ).first()
        elif idade_meses < 24:
            return CategoriaAnimal.objects.filter(
                nome__icontains='novilho',
                sexo='M',
                ativo=True
            ).first()
        else:
            return CategoriaAnimal.objects.filter(
                nome__icontains='touro',
                sexo='M',
                ativo=True
            ).first()


def ler_codigos_arquivo(caminho_arquivo):
    """Lê códigos do arquivo"""
    codigos = []
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            for linha in f:
                codigo = normalizar_codigo(linha)
                if codigo:
                    codigos.append(codigo)
        return codigos
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return []


def criar_dados_animal(codigo, propriedade, usuario):
    """Cria um animal com dados variados e realistas"""
    
    codigo_limpo = normalizar_codigo(codigo)
    numero_manejo = extrair_numero_manejo(codigo_limpo)
    
    # Verificar se animal já existe em outras propriedades
    animais_existentes = AnimalIndividual.objects.filter(
        Q(codigo_eletronico=codigo_limpo) |
        Q(numero_brinco=codigo_limpo) |
        Q(codigo_sisbov=codigo_limpo) |
        Q(numero_manejo=numero_manejo)
    ).exclude(propriedade=propriedade)
    
    # Excluir animais de outras propriedades
    if animais_existentes.exists():
        print(f"Encontrado {animais_existentes.count()} animal(is) em outras propriedades. Excluindo...")
        for animal in animais_existentes:
            # Excluir registros relacionados
            AnimalPesagem.objects.filter(animal=animal).delete()
            AnimalVacinaAplicada.objects.filter(animal=animal).delete()
            MovimentacaoIndividual.objects.filter(animal=animal).delete()
            CurralEvento.objects.filter(animal=animal).delete()
            animal.delete()
        print(f"Animais de outras propriedades excluidos.")
    
    # Verificar se já existe nesta propriedade
    animal_existente = AnimalIndividual.objects.filter(
        propriedade=propriedade
    ).filter(
        Q(codigo_eletronico=codigo_limpo) |
        Q(numero_brinco=codigo_limpo) |
        Q(codigo_sisbov=codigo_limpo) |
        Q(numero_manejo=numero_manejo)
    ).first()
    
    if animal_existente:
        print(f"ℹ️  Animal {codigo_limpo} já existe nesta propriedade. Atualizando...")
        animal = animal_existente
    else:
        # Dados variados para criar animais realistas
        sexo = random.choice(['M', 'F'])
        idade_meses = random.randint(6, 72)  # Idade variada
        data_nascimento = date.today() - timedelta(days=idade_meses * 30)
        
        # Raças comuns
        racas = ['Nelore', 'Angus', 'Brahman', 'Gir', 'Guzerá', 'Canchim', 'Simental']
        raca = random.choice(racas)
        
        # Categoria baseada em sexo e idade
        categoria = categoria_padrao_para(sexo, idade_meses)
        if not categoria:
            # Se não encontrou categoria, usar primeira disponível
            categoria = CategoriaAnimal.objects.filter(ativo=True, sexo=sexo).first()
            if not categoria:
                print(f"Erro: Nenhuma categoria encontrada para sexo {sexo}")
                return None
        
        # Peso baseado na idade e sexo
        if sexo == 'M':
            peso_base = 200 + (idade_meses * 8)  # Machos mais pesados
        else:
            peso_base = 180 + (idade_meses * 7)  # Fêmeas
        
        peso_atual = Decimal(str(round(peso_base + random.uniform(-30, 50), 1)))
        
        # Buscar ou criar brinco no estoque
        # BrincoAnimal.numero_brinco é unique globalmente, então busca primeiro
        brinco = BrincoAnimal.objects.filter(numero_brinco=codigo_limpo).first()
        
        if not brinco:
            # Criar novo brinco
            try:
                brinco = BrincoAnimal.objects.create(
                    propriedade=propriedade,
                    numero_brinco=codigo_limpo,
                    tipo_brinco='ELETRONICO',
                    status='DISPONIVEL',
                    codigo_rfid=codigo_limpo,
                )
            except Exception as e:
                print(f"Erro ao criar brinco {codigo_limpo}: {e}")
                return None
        else:
            # Brinco já existe - atualizar propriedade se necessário
            if brinco.propriedade != propriedade:
                # Se está em uso por outro animal, não pode mudar
                if brinco.status == 'EM_USO' and brinco.animal and brinco.animal.propriedade != propriedade:
                    print(f"Brinco {codigo_limpo} ja esta em uso em outra propriedade")
                    return None
                # Atualizar propriedade
                brinco.propriedade = propriedade
                brinco.save()
        
        # Se brinco está em uso por outro animal, liberar
        if brinco.status == 'EM_USO' and brinco.animal != animal_existente:
            if brinco.animal and brinco.animal.propriedade != propriedade:
                # Liberar brinco se animal está em outra propriedade
                brinco.status = 'DISPONIVEL'
                brinco.animal = None
                brinco.save()
        
        # Criar animal
        animal = AnimalIndividual.objects.create(
            numero_brinco=codigo_limpo,
            codigo_sisbov=codigo_limpo,
            codigo_eletronico=codigo_limpo,
            numero_manejo=numero_manejo,
            tipo_brinco='ELETRONICO',
            propriedade=propriedade,
            categoria=categoria,
            data_nascimento=data_nascimento,
            data_identificacao=date.today(),
            sexo=sexo,
            raca=raca,
            peso_atual_kg=peso_atual,
            status='ATIVO',
            status_sanitario='APTO',
            status_reprodutivo='INDEFINIDO' if sexo == 'M' else 'VAZIA',
            responsavel_tecnico=usuario,
            observacoes=f'Cadastrado via script de importação - {date.today().strftime("%d/%m/%Y")}'
        )
        
        # Atualizar brinco
        brinco.status = 'EM_USO'
        brinco.animal = animal
        brinco.data_utilizacao = date.today()
        brinco.save()
        
        print(f"Animal criado: {codigo_limpo} - {sexo} - {idade_meses} meses - {peso_atual} kg")
    
    return animal


def criar_pesagens_historicas(animal, usuario):
    """Cria pesagens históricas para o animal"""
    if animal.data_nascimento:
        idade_meses = (date.today() - animal.data_nascimento).days // 30
        
        # Criar 3-6 pesagens históricas
        num_pesagens = random.randint(3, 6)
        
        for i in range(num_pesagens):
            # Data da pesagem (mais antiga = mais recente)
            dias_atras = random.randint(30, idade_meses * 30)
            data_pesagem = date.today() - timedelta(days=dias_atras)
            
            # Peso baseado na idade na época
            idade_na_epoca = max(1, idade_meses - (dias_atras // 30))
            if animal.sexo == 'M':
                peso = Decimal(str(round(150 + (idade_na_epoca * 7) + random.uniform(-20, 30), 1)))
            else:
                peso = Decimal(str(round(130 + (idade_na_epoca * 6) + random.uniform(-20, 30), 1)))
            
            # Criar pesagem
            AnimalPesagem.objects.get_or_create(
                animal=animal,
                data_pesagem=data_pesagem,
                defaults={
                    'peso_kg': peso,
                    'responsavel': usuario,
                    'observacoes': f'Pesagem histórica - {data_pesagem.strftime("%d/%m/%Y")}',
                    'origem_registro': 'IMPORTACAO'
                }
            )
        
        # Atualizar peso atual com a última pesagem
        ultima_pesagem = AnimalPesagem.objects.filter(animal=animal).order_by('-data_pesagem').first()
        if ultima_pesagem:
            animal.peso_atual_kg = ultima_pesagem.peso_kg
            animal.save(update_fields=['peso_atual_kg'])
        
        print(f"  {num_pesagens} pesagens historicas criadas")


def criar_vacinas(animal, usuario):
    """Cria registros de vacinação"""
    vacinas_comuns = [
        'Aftosa',
        'Brucelose',
        'Raiva',
        'Clostridioses',
        'IBR/BVD',
    ]
    
    # Criar 2-4 vacinas
    num_vacinas = random.randint(2, 4)
    vacinas_aplicar = random.sample(vacinas_comuns, min(num_vacinas, len(vacinas_comuns)))
    
    for vacina_nome in vacinas_aplicar:
        # Data de aplicação (últimos 12 meses)
        dias_atras = random.randint(30, 365)
        data_aplicacao = date.today() - timedelta(days=dias_atras)
        
        # Próxima dose (se aplicável)
        proxima_dose = None
        if vacina_nome == 'Aftosa':
            proxima_dose = data_aplicacao + timedelta(days=180)  # 6 meses
        
        AnimalVacinaAplicada.objects.get_or_create(
            animal=animal,
            vacina=vacina_nome,
            data_aplicacao=data_aplicacao,
            defaults={
                'dose': '1ª dose',
                'lote_produto': f'LOTE-{random.randint(1000, 9999)}',
                'validade_produto': data_aplicacao + timedelta(days=365),
                'proxima_dose': proxima_dose,
                'responsavel': usuario,
            }
        )
    
    print(f"  {len(vacinas_aplicar)} vacinas registradas")


def criar_movimentacoes(animal, usuario):
    """Cria movimentações históricas"""
    if animal.data_nascimento:
        # Movimentação de nascimento
        MovimentacaoIndividual.objects.get_or_create(
            animal=animal,
            tipo_movimentacao='NASCIMENTO',
            data_movimentacao=animal.data_nascimento,
            defaults={
                'propriedade_origem': animal.propriedade,
                'peso_kg': Decimal('35.0'),  # Peso ao nascer
                'observacoes': 'Nascimento registrado via importação',
                'responsavel': usuario,
            }
        )
        
        # Possível mudança de categoria (se animal mais velho)
        idade_meses = (date.today() - animal.data_nascimento).days // 30
        if idade_meses > 12:
            data_mudanca = animal.data_nascimento + timedelta(days=365)
            MovimentacaoIndividual.objects.get_or_create(
                animal=animal,
                tipo_movimentacao='MUDANCA_CATEGORIA',
                data_movimentacao=data_mudanca,
                defaults={
                    'propriedade_origem': animal.propriedade,
                    'peso_kg': Decimal('150.0'),
                    'observacoes': 'Mudança de categoria automática',
                    'responsavel': usuario,
                }
            )
        
        print(f"  Movimentacoes criadas")


def criar_dados_reprodutivos(animal, usuario, propriedade):
    """Cria dados reprodutivos para fêmeas"""
    if animal.sexo != 'F':
        return
    
    idade_meses = (date.today() - animal.data_nascimento).days // 30 if animal.data_nascimento else 24
    
    # Só criar dados reprodutivos para fêmeas com mais de 18 meses
    if idade_meses < 18:
        animal.status_reprodutivo = 'INDEFINIDO'
        animal.save(update_fields=['status_reprodutivo'])
        return
    
    # Criar ou obter sessão de curral
    sessao, _ = CurralSessao.objects.get_or_create(
        propriedade=propriedade,
        status='ABERTA',
        defaults={
            'nome': f'Sessão Importação - {date.today().strftime("%d/%m/%Y")}',
            'data_inicio': timezone.now(),
            'criado_por': usuario,
        }
    )
    
    # Status reprodutivo variado
    status_opcoes = ['VAZIA', 'PRENHE', 'LACTACAO']
    pesos = [0.5, 0.3, 0.2]  # 50% vazia, 30% prenhe, 20% lactação
    status_reprodutivo = random.choices(status_opcoes, weights=pesos)[0]
    animal.status_reprodutivo = status_reprodutivo
    animal.save(update_fields=['status_reprodutivo'])
    
    # Criar evento reprodutivo
    if status_reprodutivo == 'PRENHE':
        # Diagnóstico de prenhez (30-60 dias atrás)
        dias_atras = random.randint(30, 60)
        data_diagnostico = date.today() - timedelta(days=dias_atras)
        
        CurralEvento.objects.get_or_create(
            sessao=sessao,
            animal=animal,
            tipo_evento='DIAGNOSTICO',
            data_evento=timezone.make_aware(
                datetime.combine(data_diagnostico, datetime.min.time())
            ),
            defaults={
                'prenhez_status': 'PRENHA',
                'responsavel': usuario,
                'observacoes': 'Diagnóstico de prenhez positivo',
            }
        )
        
        print(f"  Diagnostico de prenhez registrado")
    
    elif status_reprodutivo == 'LACTACAO':
        # Parto recente (30-120 dias atrás)
        dias_atras = random.randint(30, 120)
        data_parto = date.today() - timedelta(days=dias_atras)
        
        CurralEvento.objects.get_or_create(
            sessao=sessao,
            animal=animal,
            tipo_evento='REPRODUCAO',
            data_evento=timezone.make_aware(
                datetime.combine(data_parto, datetime.min.time())
            ),
            defaults={
                'prenhez_status': 'PRENHA',
                'responsavel': usuario,
                'observacoes': 'Parto registrado',
            }
        )
        
        print(f"  Parto registrado")
    
    print(f"  Status reprodutivo: {status_reprodutivo}")


class Command(BaseCommand):
    help = 'Cadastra animais da Prima com dados completos (pesagens, vacinas, movimentações, reprodutivos)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--arquivo',
            type=str,
            default=r'c:\Users\joaoz\Downloads\animais prima.txt',
            help='Caminho do arquivo com códigos dos animais'
        )
        parser.add_argument(
            '--propriedade',
            type=int,
            help='ID da propriedade onde cadastrar os animais'
        )
        parser.add_argument(
            '--usuario',
            type=int,
            help='ID do usuário responsável'
        )
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Pula confirmação e executa automaticamente'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        arquivo = options['arquivo']
        propriedade_id = options.get('propriedade')
        usuario_id = options.get('usuario')
        
        if not os.path.exists(arquivo):
            self.stdout.write(self.style.ERROR(f'Arquivo nao encontrado: {arquivo}'))
            return
        
        # Ler códigos
        self.stdout.write('Lendo codigos do arquivo...')
        codigos = ler_codigos_arquivo(arquivo)
        
        if not codigos:
            self.stdout.write(self.style.ERROR('Nenhum codigo encontrado no arquivo!'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'{len(codigos)} codigos encontrados'))
        
        # Solicitar propriedade se não fornecida
        if not propriedade_id:
            self.stdout.write('\n📋 Propriedades disponíveis:')
            propriedades = Propriedade.objects.all().order_by('nome_propriedade')
            for prop in propriedades:
                self.stdout.write(f'  {prop.id} - {prop.nome_propriedade}')
            
            try:
                propriedade_id = int(input('\nDigite o ID da propriedade: ').strip())
            except (ValueError, KeyboardInterrupt):
                self.stdout.write(self.style.ERROR('ID invalido ou operacao cancelada!'))
                return
        
        try:
            propriedade = Propriedade.objects.get(id=propriedade_id)
        except Propriedade.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Propriedade {propriedade_id} nao encontrada!'))
            return
        
        # Solicitar usuário se não fornecido
        if not usuario_id:
            self.stdout.write('\nUsuarios disponiveis:')
            usuarios = User.objects.filter(is_staff=True).order_by('username')
            for user in usuarios:
                self.stdout.write(f'  {user.id} - {user.username} ({user.get_full_name() or "Sem nome"})')
            
            try:
                usuario_id = int(input('\nDigite o ID do usuario: ').strip())
            except (ValueError, KeyboardInterrupt):
                self.stdout.write(self.style.ERROR('ID invalido ou operacao cancelada!'))
                return
        
        try:
            usuario = User.objects.get(id=usuario_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Usuario {usuario_id} nao encontrado!'))
            return
        
        # Confirmar (a menos que --yes seja usado)
        if not options.get('yes', False):
            self.stdout.write(f'\nATENCAO: Serao cadastrados {len(codigos)} animais na propriedade {propriedade.nome_propriedade}')
            self.stdout.write('   Animais existentes em outras propriedades serao EXCLUIDOS!')
            try:
                confirmar = input('\nDeseja continuar? (s/N): ').strip().lower()
            except KeyboardInterrupt:
                self.stdout.write(self.style.ERROR('Operacao cancelada.'))
                return
            
            if confirmar != 's':
                self.stdout.write(self.style.ERROR('Operacao cancelada.'))
                return
        
        # Processar
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write(f'CADASTRO DE ANIMAIS - PROPRIEDADE: {propriedade.nome_propriedade}')
        self.stdout.write(f'{"="*60}\n')
        
        total = len(codigos)
        sucesso = 0
        erros = 0
        
        for i, codigo in enumerate(codigos, 1):
            try:
                self.stdout.write(f'\n[{i}/{total}] Processando: {codigo}')
                
                animal = criar_dados_animal(codigo, propriedade, usuario)
                if not animal:
                    erros += 1
                    continue
                
                criar_pesagens_historicas(animal, usuario)
                criar_vacinas(animal, usuario)
                criar_movimentacoes(animal, usuario)
                criar_dados_reprodutivos(animal, usuario, propriedade)
                
                sucesso += 1
                self.stdout.write(self.style.SUCCESS(f'Animal {codigo} processado com sucesso!'))
                
            except Exception as e:
                erros += 1
                self.stdout.write(self.style.ERROR(f'Erro ao processar {codigo}: {e}'))
                import traceback
                traceback.print_exc()
        
        self.stdout.write(f'\n{"="*60}')
        self.stdout.write('RESUMO:')
        self.stdout.write(f'  Total processado: {total}')
        self.stdout.write(self.style.SUCCESS(f'  Sucesso: {sucesso}'))
        self.stdout.write(self.style.ERROR(f'  Erros: {erros}'))
        self.stdout.write(f'{"="*60}\n')

