import itertools
import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from gestao_rural.models import (
    AnimalIndividual,
    CategoriaAnimal,
    ProdutorRural,
    Propriedade,
)


class Command(BaseCommand):
    help = "Gera uma carga masiva de produtores, propriedades e animais para testes."

    def add_arguments(self, parser):
        parser.add_argument('--total', type=int, default=999_000,
                            help='Total de animais a serem gerados (padrão: 999000).')
        parser.add_argument('--produtores', type=int, default=20,
                            help='Quantidade de produtores rurais (padrão: 20).')
        parser.add_argument('--propriedades', type=int, default=50,
                            help='Quantidade de propriedades (padrão: 50).')
        parser.add_argument('--chunk-size', type=int, default=10_000,
                            help='Tamanho dos lotes de bulk_create (padrão: 10000).')
        parser.add_argument('--purge', action='store_true',
                            help='Remove animais das propriedades criadas antes de gerar novos.')

    def handle(self, *args, **options):
        total_animais = options['total']
        total_produtores = options['produtores']
        total_propriedades = options['propriedades']
        chunk_size = options['chunk_size']
        purge = options['purge']

        if total_propriedades < total_produtores:
            raise CommandError('A quantidade de propriedades deve ser maior ou igual à de produtores.')

        categorias = list(CategoriaAnimal.objects.all())
        if not categorias:
            raise CommandError('Nenhuma CategoriaAnimal encontrada. Execute a rotina de criação de categorias padrão antes.')

        categorias_por_sexo = {
            'F': [c for c in categorias if c.sexo == 'F'],
            'M': [c for c in categorias if c.sexo == 'M'],
            'I': [c for c in categorias if c.sexo not in {'F', 'M'}],
        }

        def categoria_para_sexo(sexo):
            lista = categorias_por_sexo.get(sexo) or categorias_por_sexo['I'] or categorias
            return random.choice(lista)

        User = get_user_model()
        usuarios = list(User.objects.all())
        if not usuarios:
            raise CommandError('Nenhum usuário encontrado. Crie pelo menos um usuário para ser responsável pelos produtores.')

        usuario_iterator = itertools.cycle(usuarios)
        produtores = []
        self.stdout.write(self.style.NOTICE(f'Criando {total_produtores} produtores...'))

        for idx in range(total_produtores):
            cpf = f'{idx + 1:011d}'
            produtor, _created = ProdutorRural.objects.get_or_create(
                cpf_cnpj=cpf,
                defaults={
                    'nome': f'Produtor {idx + 1:02d}',
                    'usuario_responsavel': next(usuario_iterator),
                    'anos_experiencia': random.randint(1, 30),
                    'telefone': f'(11) 9{random.randint(4000, 9999)}-{random.randint(1000, 9999)}',
                    'email': f'produtor{idx + 1:02d}@monpec.test',
                    'endereco': 'Endereço gerado automaticamente para testes de carga.'
                }
            )
            produtores.append(produtor)

        self.stdout.write(self.style.NOTICE(f'Criando {total_propriedades} propriedades...'))
        propriedades = []
        municipios = ['Cidade Modelo', 'Nova Canãa', 'Vale Verde', 'Serra Azul']
        for idx in range(total_propriedades):
            produtor = produtores[idx % len(produtores)]
            nome = f'Fazenda {idx + 1:03d}'
            defaults = {
                'municipio': random.choice(municipios),
                'uf': 'SP',
                'area_total_ha': Decimal(random.randint(500, 2000)),
                'tipo_operacao': 'PECUARIA',
                'tipo_ciclo_pecuario': ['CICLO_COMPLETO'],
                'tipo_propriedade': 'PROPRIA',
                'valor_hectare_proprio': Decimal('5000.00'),
            }
            propriedade, _created = Propriedade.objects.get_or_create(
                nome_propriedade=nome,
                produtor=produtor,
                defaults=defaults,
            )
            propriedades.append(propriedade)

        if not propriedades:
            raise CommandError('Falha ao criar propriedades.')

        if purge:
            self.stdout.write(self.style.WARNING('Removendo animais existentes das propriedades geradas...'))
            AnimalIndividual.objects.filter(propriedade__in=propriedades).delete()

        base_por_propriedade = total_animais // len(propriedades)
        sobra = total_animais % len(propriedades)
        inicio_brinco = 100_000_000_000_000  # 15 dígitos base SISBOV

        total_criado = 0
        sexo_ciclo = ['F', 'M']
        status_pool = ['ATIVO'] * 6 + ['VENDIDO', 'TRANSFERIDO', 'DESAPARECIDO', 'MORTO']
        racas = ['NELORE', 'ANGUS', 'HEREFORD', 'BRAHMAN', 'GIROLANDO']
        agora = timezone.now()
        sequencial = 0

        self.stdout.write(self.style.NOTICE(
            f'Gerando {total_animais:,} animais distribuídos entre {len(propriedades)} propriedades...'
        ))

        for idx, propriedade in enumerate(propriedades):
            quota = base_por_propriedade + (1 if idx < sobra else 0)
            if quota == 0:
                continue

            registros = []
            for j in range(quota):
                sequencial += 1
                numero_brinco = inicio_brinco + sequencial
                sexo = sexo_ciclo[(sequencial + idx) % len(sexo_ciclo)]
                categoria = categoria_para_sexo(sexo)
                nascimento = date.today() - timedelta(days=random.randint(90, 1825))
                peso = round(random.uniform(180, 620), 2)
                peso_decimal = Decimal(f'{peso:.2f}')
                status = random.choice(status_pool)
                raca = categoria.raca if getattr(categoria, 'raca', None) else random.choice(racas)

                registros.append(AnimalIndividual(
                    numero_brinco=f'{numero_brinco:015d}',
                    tipo_brinco='VISUAL',
                    propriedade=propriedade,
                    categoria=categoria,
                    data_nascimento=nascimento,
                    sexo=sexo,
                    raca=raca,
                    peso_atual_kg=peso_decimal,
                    status=status,
                    observacoes='Carga massiva para testes de performance.',
                    data_cadastro=agora,
                ))

                if len(registros) >= chunk_size:
                    AnimalIndividual.objects.bulk_create(registros, batch_size=chunk_size)
                    total_criado += len(registros)
                    registros.clear()
                    if total_criado % 50_000 == 0:
                        self.stdout.write(self.style.NOTICE(f'- {total_criado:,} animais gerados...'))

            if registros:
                AnimalIndividual.objects.bulk_create(registros, batch_size=chunk_size)
                total_criado += len(registros)
                if total_criado % 50_000 == 0 or total_criado == total_animais:
                    self.stdout.write(self.style.NOTICE(f'- {total_criado:,} animais gerados...'))

        self.stdout.write(self.style.SUCCESS(
            f'Processo concluído! {total_criado:,} animais cadastrados para testes.'
        ))


