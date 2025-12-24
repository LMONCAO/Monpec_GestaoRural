# pyright: reportMissingImports=false

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class ProdutorRural(models.Model):
    """Modelo para cadastro de produtores rurais"""
    nome = models.CharField(max_length=200, verbose_name="Nome do Produtor")
    cpf_cnpj = models.CharField(max_length=18, unique=True, verbose_name="CPF/CNPJ")
    documento_identidade = models.CharField(max_length=20, blank=True, null=True, verbose_name="Documento de Identidade (RG)")
    data_nascimento = models.DateField(blank=True, null=True, verbose_name="Data de Nascimento")
    anos_experiencia = models.PositiveIntegerField(blank=True, null=True, verbose_name="Anos de Experiência na Atividade")
    usuario_responsavel = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Usuário Responsável"
    )
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Produtor Rural"
        verbose_name_plural = "Produtores Rurais"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome
    
    @property
    def idade(self):
        """Calcula a idade do produtor baseada na data de nascimento"""
        if self.data_nascimento:
            from datetime import date
            today = date.today()
            return today.year - self.data_nascimento.year - ((today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return None


class PlanoAssinatura(models.Model):
    """Planos de assinatura disponibilizados via Stripe."""
    
    MODULOS_PADRAO = [
        'pecuaria',
        'financeiro',
        'projetos',
        'compras',
        'funcionarios',
        'rastreabilidade',
        'reproducao',
        'relatorios',
    ]
    
    nome = models.CharField(max_length=120, unique=True, verbose_name="Nome do plano")
    slug = models.SlugField(max_length=120, unique=True, verbose_name="Slug")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    stripe_price_id = models.CharField(
        max_length=120, 
        blank=True, 
        verbose_name="Stripe Price ID",
        help_text="ID do preço no Stripe (opcional se usar outro gateway)"
    )
    mercadopago_preapproval_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Mercado Pago Preapproval ID",
        help_text="ID do plano de assinatura no Mercado Pago (opcional)"
    )
    preco_mensal_referencia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Preço mensal de referência (R$)"
    )
    max_usuarios = models.PositiveIntegerField(
        default=1,
        verbose_name="Máximo de usuários",
        help_text="Número máximo de usuários permitidos neste plano"
    )
    modulos_disponiveis = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Módulos disponíveis",
        help_text="Lista de módulos liberados para este plano"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Plano de Assinatura"
        verbose_name_plural = "Planos de Assinatura"
        ordering = ['nome']

    def __str__(self):
        return self.nome
    
    def get_modulos_disponiveis(self):
        """Retorna lista de módulos disponíveis ou padrão se vazio"""
        return self.modulos_disponiveis if self.modulos_disponiveis else self.MODULOS_PADRAO


class AssinaturaCliente(models.Model):
    """Assinaturas dos usuários integradas com a Stripe."""

    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        ATIVA = 'ATIVA', 'Ativa'
        SUSPENSA = 'SUSPENSA', 'Suspensa'
        CANCELADA = 'CANCELADA', 'Cancelada'
        INADIMPLENTE = 'INADIMPLENTE', 'Inadimplente'

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='assinatura',
        verbose_name="Usuário"
    )
    produtor = models.ForeignKey(
        ProdutorRural,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assinaturas',
        verbose_name="Produtor vinculado"
    )
    plano = models.ForeignKey(
        PlanoAssinatura,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assinaturas',
        verbose_name="Plano"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
        verbose_name="Status"
    )
    stripe_customer_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Stripe Customer ID"
    )
    stripe_subscription_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Stripe Subscription ID"
    )
    mercadopago_customer_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Mercado Pago Customer ID"
    )
    mercadopago_subscription_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Mercado Pago Subscription ID"
    )
    gateway_pagamento = models.CharField(
        max_length=50,
        default='stripe',
        choices=[
            ('stripe', 'Stripe'),
            ('mercadopago', 'Mercado Pago'),
            ('asaas', 'Asaas'),
            ('gerencianet', 'Gerencianet'),
        ],
        verbose_name="Gateway de Pagamento",
        help_text="Gateway usado para esta assinatura"
    )
    ultimo_checkout_id = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Último Checkout Session ID"
    )
    current_period_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fim do período atual"
    )
    cancelamento_agendado = models.BooleanField(
        default=False,
        verbose_name="Cancelamento ao término do período"
    )
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadados adicionais")
    data_liberacao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Liberação",
        help_text="Data a partir da qual o usuário terá acesso ao sistema. Se não definida, o acesso será imediato após pagamento confirmado."
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Assinatura de Cliente"
        verbose_name_plural = "Assinaturas de Clientes"
        ordering = ['-atualizado_em']
        indexes = [
            models.Index(fields=['stripe_customer_id']),
            models.Index(fields=['stripe_subscription_id']),
            models.Index(fields=['mercadopago_customer_id']),
            models.Index(fields=['mercadopago_subscription_id']),
            models.Index(fields=['gateway_pagamento']),
        ]

    def __str__(self):
        return f"{self.usuario} - {self.get_status_display()}"

    @property
    def acesso_liberado(self) -> bool:
        """
        Verifica se o acesso está liberado baseado na data de liberação.
        Se não houver data_liberacao definida, considera liberado se status for ATIVA.
        """
        if not self.data_liberacao:
            # Se não há data de liberação, acesso é imediato após pagamento
            return self.status == self.Status.ATIVA
        
        from django.utils import timezone
        hoje = timezone.now().date()
        return self.status == self.Status.ATIVA and hoje >= self.data_liberacao
    
    @property
    def ativa(self):
        return self.status == self.Status.ATIVA

    def atualizar_status(self, status):
        if status in self.Status.values:
            self.status = status
            self.save(update_fields=['status', 'atualizado_em'])

    @property
    def alias_tenant(self) -> str:
        return f"tenant_{self.pk}"
    
    @property
    def usuarios_ativos(self):
        """Retorna o número de usuários ativos do tenant"""
        return self.usuarios_tenant.filter(ativo=True).count()
    
    @property
    def modulos_disponiveis(self):
        """Retorna os módulos disponíveis do plano"""
        if self.plano:
            return self.plano.get_modulos_disponiveis()
        return PlanoAssinatura.MODULOS_PADRAO


class TenantWorkspace(models.Model):
    """Gerencia os bancos de dados dedicados de cada assinatura."""

    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        PROVISIONANDO = 'PROVISIONANDO', 'Provisionando'
        ATIVO = 'ATIVO', 'Ativo'
        ERRO = 'ERRO', 'Erro'
        DESATIVADO = 'DESATIVADO', 'Desativado'

    assinatura = models.OneToOneField(
        AssinaturaCliente,
        on_delete=models.CASCADE,
        related_name='workspace',
        verbose_name="Assinatura"
    )
    alias = models.CharField(max_length=60, unique=True, verbose_name="Alias do banco")
    caminho_banco = models.CharField(max_length=255, verbose_name="Caminho do banco")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE,
        verbose_name="Status"
    )
    provisionado_em = models.DateTimeField(null=True, blank=True, verbose_name="Provisionado em")
    ultimo_erro = models.TextField(blank=True, verbose_name="Último erro conhecido")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadados")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Workspace de Cliente"
        verbose_name_plural = "Workspaces de Clientes"
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.assinatura.usuario} - {self.alias} ({self.get_status_display()})"

    @property
    def caminho_path(self):
        from pathlib import Path

        return Path(self.caminho_banco)

    def marcar_erro(self, mensagem: str):
        self.status = self.Status.ERRO
        self.ultimo_erro = mensagem[:2000]
        self.save(update_fields=['status', 'ultimo_erro', 'atualizado_em'])


class TenantUsuario(models.Model):
    """Usuários dentro de um tenant (assinatura)."""
    
    class Perfil(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        OPERADOR = 'OPERADOR', 'Operador'
        VISUALIZADOR = 'VISUALIZADOR', 'Visualizador'
    
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='tenant_profile',
        verbose_name="Usuário"
    )
    assinatura = models.ForeignKey(
        AssinaturaCliente,
        on_delete=models.CASCADE,
        related_name='usuarios_tenant',
        verbose_name="Assinatura"
    )
    nome_exibicao = models.CharField(max_length=150, verbose_name="Nome de exibição")
    email = models.EmailField(verbose_name="E-mail")
    perfil = models.CharField(
        max_length=20,
        choices=Perfil.choices,
        default=Perfil.OPERADOR,
        verbose_name="Perfil"
    )
    modulos = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Módulos liberados",
        help_text="Lista de módulos que este usuário pode acessar"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios_criados',
        verbose_name="Criado por"
    )
    ultimo_login = models.DateTimeField(null=True, blank=True, verbose_name="Último login")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Usuário do Tenant"
        verbose_name_plural = "Usuários do Tenant"
        ordering = ['nome_exibicao']
        unique_together = [['usuario', 'assinatura']]
    
    def __str__(self):
        return f"{self.nome_exibicao} ({self.assinatura.usuario.username})"
    
    def atualizar_modulos(self, modulos):
        """Atualiza os módulos liberados para o usuário"""
        self.modulos = modulos
        self.save(update_fields=['modulos', 'atualizado_em'])
    
    def tem_acesso_modulo(self, modulo):
        """Verifica se o usuário tem acesso a um módulo específico"""
        return modulo in self.modulos or self.perfil == self.Perfil.ADMIN


class Propriedade(models.Model):
    """Modelo para cadastro de propriedades rurais"""
    TIPO_OPERACAO_CHOICES = [
        ('PECUARIA', 'Pecuária'),
    ]
    
    TIPO_CICLO_PECUARIO_CHOICES = [
        ('CRIA', 'Cria'),
        ('RECRIA', 'Recria'),
        ('ENGORDA', 'Engorda'),
        ('CICLO_COMPLETO', 'Ciclo Completo'),
    ]
    
    TIPO_PROPRIEDADE_CHOICES = [
        ('PROPRIA', 'Própria'),
        ('ARRENDAMENTO', 'Arrendamento'),
    ]
    
    nome_propriedade = models.CharField(max_length=200, verbose_name="Nome da Propriedade")
    produtor = models.ForeignKey(
        ProdutorRural, 
        on_delete=models.CASCADE, 
        verbose_name="Produtor"
    )
    municipio = models.CharField(max_length=100, verbose_name="Município")
    uf = models.CharField(max_length=2, verbose_name="UF")
    
    # Campos de localização detalhada
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    cep = models.CharField(max_length=10, blank=True, null=True, verbose_name="CEP")
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro/Distrito")
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        blank=True, 
        null=True,
        verbose_name="Latitude"
    )
    longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8, 
        blank=True, 
        null=True,
        verbose_name="Longitude"
    )
    ponto_referencia = models.TextField(blank=True, null=True, verbose_name="Ponto de Referência")
    
    area_total_ha = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Área Total (ha)"
    )
    tipo_operacao = models.CharField(
        max_length=20, 
        choices=TIPO_OPERACAO_CHOICES, 
        verbose_name="Tipo de Operação"
    )
    
    tipo_ciclo_pecuario = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Tipos de Ciclo Pecuário"
    )
    
    # Novos campos para tipo de propriedade
    tipo_propriedade = models.CharField(
        max_length=20, 
        choices=TIPO_PROPRIEDADE_CHOICES, 
        default='PROPRIA',
        verbose_name="Tipo de Propriedade"
    )
    
    # Campos para propriedade própria
    valor_hectare_proprio = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valor por Hectare (R$)"
    )
    
    # Campos para arrendamento
    valor_mensal_hectare_arrendamento = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valor Mensal por Hectare (R$)"
    )
    
    # Campos de localização e documentação
    nirf = models.CharField(max_length=50, blank=True, null=True, verbose_name="NIRF")
    incra = models.CharField(max_length=50, blank=True, null=True, verbose_name="INCRA")
    car = models.CharField(max_length=50, blank=True, null=True, verbose_name="CAR")
    inscricao_estadual = models.CharField(max_length=50, blank=True, null=True, verbose_name="Inscrição Estadual")
    
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Propriedade"
        verbose_name_plural = "Propriedades"
        ordering = ['nome_propriedade']
    
    def __str__(self):
        return f"{self.nome_propriedade} - {self.produtor.nome}"
    
    def ciclos_pecuarios_list(self):
        """Retorna a lista normalizada de códigos de ciclo pecuário."""
        valor = self.tipo_ciclo_pecuario or []
        if isinstance(valor, str):
            valor = [item.strip() for item in valor.split(',') if item.strip()]
        return list(valor)

    def get_ciclos_pecuarios_display(self):
        """Retorna a descrição legível dos ciclos pecuários selecionados."""
        mapa = dict(self.TIPO_CICLO_PECUARIO_CHOICES)
        ciclos = self.ciclos_pecuarios_list()
        if not ciclos:
            return mapa.get('CICLO_COMPLETO', 'Ciclo Completo')
        return ', '.join(mapa.get(codigo, codigo) for codigo in ciclos)

    def get_tipo_ciclo_pecuario_display(self):
        """Compatibilidade com templates que utilizam o método padrão do Django."""
        return self.get_ciclos_pecuarios_display()
    
    @property
    def valor_total_propriedade(self):
        """Calcula o valor total da propriedade se for própria"""
        if self.tipo_propriedade == 'PROPRIA' and self.valor_hectare_proprio:
            return self.area_total_ha * self.valor_hectare_proprio
        return None
    
    @property
    def valor_mensal_total_arrendamento(self):
        """Calcula o valor mensal total do arrendamento"""
        if self.tipo_propriedade == 'ARRENDAMENTO' and self.valor_mensal_hectare_arrendamento:
            return self.area_total_ha * self.valor_mensal_hectare_arrendamento
        return None

    def save(self, *args, **kwargs):
        ciclos = self.tipo_ciclo_pecuario or []
        if isinstance(ciclos, str):
            ciclos = [item.strip() for item in ciclos.split(',') if item.strip()]
        self.tipo_ciclo_pecuario = list(ciclos)
        super().save(*args, **kwargs)


class CategoriaAnimal(models.Model):
    """Modelo para categorias de animais do rebanho"""
    SEXO_CHOICES = [
        ('F', 'Fêmea'),
        ('M', 'Macho'),
        ('I', 'Indefinido'),
    ]
    
    RACA_CHOICES = [
        ('NELORE', 'Nelore'),
        ('ANGUS', 'Angus'),
        ('HEREFORD', 'Hereford'),
        ('BRAHMAN', 'Brahman'),
        ('SIMENTAL', 'Simental'),
        ('GIR', 'Gir'),
        ('GUZERA', 'Guzerá'),
        ('CANCHIM', 'Canchim'),
        ('SENEPOL', 'Senepol'),
        ('OUTROS', 'Outros'),
    ]
    
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='I', verbose_name="Sexo")
    raca = models.CharField(max_length=20, choices=RACA_CHOICES, default='NELORE', verbose_name="Raça")
    idade_minima_meses = models.PositiveIntegerField(null=True, blank=True, verbose_name="Idade Mínima (meses)")
    idade_maxima_meses = models.PositiveIntegerField(null=True, blank=True, verbose_name="Idade Máxima (meses)")
    peso_medio_kg = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="Peso Médio (kg)",
        help_text="Peso médio do animal nesta categoria em quilogramas"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Categoria de Animal"
        verbose_name_plural = "Categorias de Animais"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class InventarioRebanho(models.Model):
    """Modelo para inventário inicial do rebanho"""
    propriedade = models.ForeignKey(
        Propriedade, 
        on_delete=models.CASCADE, 
        verbose_name="Propriedade"
    )
    categoria = models.ForeignKey(
        CategoriaAnimal, 
        on_delete=models.CASCADE, 
        verbose_name="Categoria"
    )
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade")
    valor_por_cabeca = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Valor por Cabeça (R$)"
    )
    data_inventario = models.DateField(verbose_name="Data do Inventário")
    
    @property
    def valor_total(self):
        """Calcula o valor total da categoria"""
        return self.quantidade * self.valor_por_cabeca
    
    class Meta:
        verbose_name = "Inventário do Rebanho"
        verbose_name_plural = "Inventários do Rebanho"
        unique_together = ['propriedade', 'categoria', 'data_inventario']
        ordering = ['-data_inventario', 'categoria']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.categoria.nome}: {self.quantidade}"


class PlanejamentoAnual(models.Model):
    """Planejamento estratégico anual da pecuária"""
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('EM_ANDAMENTO', 'Em andamento'),
        ('APROVADO', 'Aprovado'),
        ('CONCLUIDO', 'Concluído'),
        ('ARQUIVADO', 'Arquivado'),
    ]

    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='planejamentos_pecuarios',
        verbose_name="Propriedade",
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Código da Projeção",
        help_text="Código único identificador da projeção (gerado automaticamente)"
    )
    ano = models.PositiveIntegerField(verbose_name="Ano do Planejamento")
    descricao = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Descrição resumida",
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='RASCUNHO',
        verbose_name="Status",
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de criação")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Última atualização")

    class Meta:
        verbose_name = "Planejamento Anual Pecuário"
        verbose_name_plural = "Planejamentos Anuais Pecuários"
        ordering = ['-data_criacao', '-ano', 'propriedade']
        # Removido unique_together para permitir múltiplos planejamentos no mesmo ano
        # Cada planejamento terá um código único gerado automaticamente
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['ano', 'propriedade']),
            models.Index(fields=['data_criacao']),
        ]

    def gerar_codigo_unico(self):
        """Gera um código único para a projeção no formato PROJ-YYYY-NNNN"""
        if self.codigo:
            return self.codigo
        
        # Buscar o último código do mesmo ano
        ano_atual = self.ano
        queryset = PlanejamentoAnual.objects.filter(
            ano=ano_atual,
            codigo__isnull=False
        )
        
        # Excluir o próprio objeto se já tiver ID
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        
        ultimo_planejamento = queryset.order_by('-codigo').first()
        
        if ultimo_planejamento and ultimo_planejamento.codigo:
            # Extrair o número sequencial do último código
            try:
                partes = ultimo_planejamento.codigo.split('-')
                if len(partes) == 3 and partes[0] == 'PROJ':
                    sequencial = int(partes[2])
                    novo_sequencial = sequencial + 1
                else:
                    novo_sequencial = 1
            except (ValueError, IndexError):
                novo_sequencial = 1
        else:
            novo_sequencial = 1
        
        # Gerar código no formato PROJ-YYYY-NNNN e verificar unicidade
        max_tentativas = 100
        tentativa = 0
        while tentativa < max_tentativas:
            self.codigo = f"PROJ-{ano_atual}-{novo_sequencial:04d}"
            
            # Verificar se o código já existe
            if not PlanejamentoAnual.objects.filter(codigo=self.codigo).exclude(pk=self.pk if self.pk else None).exists():
                return self.codigo
            
            novo_sequencial += 1
            tentativa += 1
        
        # Se não conseguiu após 100 tentativas, usar timestamp
        from django.utils import timezone
        timestamp = int(timezone.now().timestamp() % 10000)
        self.codigo = f"PROJ-{ano_atual}-{timestamp:04d}"
        return self.codigo

    def save(self, *args, **kwargs):
        """Override save para gerar código automaticamente se não existir"""
        if not self.codigo:
            self.gerar_codigo_unico()
        super().save(*args, **kwargs)

    def __str__(self):
        codigo_display = f"[{self.codigo}] " if self.codigo else ""
        return f"{codigo_display}{self.propriedade.nome_propriedade} - {self.ano}"


class AtividadePlanejada(models.Model):
    """Cronograma de atividades operacionais previstas"""
    STATUS_CHOICES = [
        ('AGENDADA', 'Agendada'),
        ('EM_EXECUCAO', 'Em execução'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),
        ('ATRASADA', 'Atrasada'),
    ]

    planejamento = models.ForeignKey(
        PlanejamentoAnual,
        on_delete=models.CASCADE,
        related_name='atividades',
        verbose_name="Planejamento",
    )
    categoria = models.ForeignKey(
        CategoriaAnimal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoria envolvida",
    )
    tipo_atividade = models.CharField(max_length=120, verbose_name="Tipo de atividade")
    descricao = models.TextField(blank=True, verbose_name="Descrição / Observações")
    data_inicio_prevista = models.DateField(verbose_name="Data de início prevista")
    data_fim_prevista = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de término prevista",
    )
    responsavel = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Responsável",
    )
    custo_previsto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Custo previsto (R$)",
    )
    indicador_alvo = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Indicador alvo (ex: taxa prenhez)",
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='AGENDADA',
        verbose_name="Status da atividade",
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Atividade Planejada"
        verbose_name_plural = "Atividades Planejadas"
        ordering = ['data_inicio_prevista', 'tipo_atividade']

    def __str__(self):
        return f"{self.tipo_atividade} ({self.planejamento.ano})"


class MetaComercialPlanejada(models.Model):
    """Metas comerciais (vendas/compras) previstas para o ano"""
    planejamento = models.ForeignKey(
        PlanejamentoAnual,
        on_delete=models.CASCADE,
        related_name='metas_comerciais',
        verbose_name="Planejamento",
    )
    categoria = models.ForeignKey(
        CategoriaAnimal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoria",
    )
    quantidade_animais = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantidade de animais",
    )
    arrobas_totais = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Arrobas totais",
    )
    preco_medio_esperado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Preço médio esperado (R$/@ ou cabeça)",
    )
    canal_venda = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Canal de venda",
    )
    percentual_impostos = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Impostos e taxas (%)",
    )
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Meta Comercial Planejada"
        verbose_name_plural = "Metas Comerciais Planejadas"
        ordering = ['categoria__nome']

    def __str__(self):
        return f"Meta Comercial {self.planejamento.ano} - {self.categoria or 'Geral'}"


class MetaFinanceiraPlanejada(models.Model):
    """Metas de custos/investimentos planejados para o ano"""
    TIPO_CUSTO_CHOICES = [
        ('FIXO', 'Custo fixo'),
        ('VARIAVEL', 'Custo variável'),
        ('INVESTIMENTO', 'Investimento'),
        ('TAXA', 'Taxas e encargos'),
        ('OUTROS', 'Outros'),
    ]

    planejamento = models.ForeignKey(
        PlanejamentoAnual,
        on_delete=models.CASCADE,
        related_name='metas_financeiras',
        verbose_name="Planejamento",
    )
    descricao = models.CharField(max_length=180, verbose_name="Descrição")
    tipo_custo = models.CharField(
        max_length=15,
        choices=TIPO_CUSTO_CHOICES,
        default='VARIAVEL',
        verbose_name="Tipo de custo",
    )
    valor_anual_previsto = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Valor anual previsto (R$)",
    )
    indice_correcao = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Índice de correção",
    )
    percentual_correcao = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Percentual de correção (%)",
    )
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Meta Financeira Planejada"
        verbose_name_plural = "Metas Financeiras Planejadas"
        ordering = ['tipo_custo', 'descricao']

    def __str__(self):
        return f"{self.descricao} ({self.planejamento.ano})"


class IndicadorPlanejado(models.Model):
    """Indicadores estratégicos meta para o ano"""

    EIXO_CHOICES = [
        ('REPRODUCAO', 'Reprodução'),
        ('ENGORDA', 'Engorda'),
        ('FINANCEIRO', 'Financeiro'),
        ('SANIDADE', 'Sanidade'),
        ('OPERACIONAL', 'Operacional'),
        ('SUSTENTABILIDADE', 'Sustentabilidade'),
    ]

    DIRECAO_META_CHOICES = [
        ('MAIOR', 'Maior é melhor'),
        ('MENOR', 'Menor é melhor'),
        ('ALVO', 'Alcançar valor específico'),
    ]

    planejamento = models.ForeignKey(
        PlanejamentoAnual,
        on_delete=models.CASCADE,
        related_name='indicadores_planejados',
        verbose_name="Planejamento",
    )
    codigo = models.CharField(
        max_length=60,
        blank=True,
        verbose_name="Código do indicador",
        help_text=(
            "Identificador para cálculo automático (ex: TAXA_PRENHEZ, "
            "ARROBAS_VENDIDAS, CUSTO_ARROBA)."
        ),
    )
    eixo_estrategico = models.CharField(
        max_length=20,
        choices=EIXO_CHOICES,
        default='OPERACIONAL',
        verbose_name="Eixo estratégico",
    )
    nome = models.CharField(max_length=120, verbose_name="Nome do indicador")
    unidade = models.CharField(
        max_length=30,
        default='%',
        verbose_name="Unidade",
    )
    valor_meta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Meta planejada",
    )
    valor_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor base (realizado atual)",
        help_text="Valor de referência já alcançado, útil para comparar evolução.",
    )
    direcao_meta = models.CharField(
        max_length=10,
        choices=DIRECAO_META_CHOICES,
        default='MAIOR',
        verbose_name="Direção desejada",
    )
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    prioridade = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="Prioridade (1-5)",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Indicador Planejado"
        verbose_name_plural = "Indicadores Planejados"
        ordering = ['prioridade', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.planejamento.ano})"


class CenarioPlanejamento(models.Model):
    """Cenários comparativos do planejamento anual"""
    planejamento = models.ForeignKey(
        PlanejamentoAnual,
        on_delete=models.CASCADE,
        related_name='cenarios',
        verbose_name="Planejamento",
    )
    nome = models.CharField(max_length=120, verbose_name="Nome do cenário")
    descricao = models.TextField(blank=True, verbose_name="Descrição")
    is_baseline = models.BooleanField(
        default=False,
        verbose_name="É cenário base?",
    )
    ajuste_preco_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Ajuste de preço (%)",
    )
    ajuste_custo_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Ajuste de custo (%)",
    )
    ajuste_producao_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Ajuste de produção (%)",
    )
    ajuste_taxas_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Ajuste de taxas (%)",
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cenário de Planejamento"
        verbose_name_plural = "Cenários de Planejamento"
        ordering = ['-is_baseline', 'nome']

    def __str__(self):
        status = "Baseline" if self.is_baseline else "Cenário"
        return f"{status} {self.nome} ({self.planejamento.ano})"


class PoliticaVendasCategoria(models.Model):
    """Modelo para política de vendas por categoria"""
    REPOSICAO_CHOICES = [
        ('NAO_REP', 'Não repor'),
        ('TRANSFERENCIA', 'Transferência'),
        ('COMPRA', 'Compra'),
        ('AMBOS', 'Transferência + Compra'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade, 
        on_delete=models.CASCADE,
        verbose_name="Propriedade"
    )
    categoria = models.ForeignKey(
        CategoriaAnimal,
        on_delete=models.CASCADE,
        verbose_name="Categoria"
    )
    percentual_venda = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Percentual de Venda (%)"
    )
    quantidade_venda = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantidade de Venda"
    )
    reposicao_tipo = models.CharField(
        max_length=20,
        choices=REPOSICAO_CHOICES,
        default='NAO_REP',
        verbose_name="Tipo de Reposição"
    )
    origem_fazenda = models.ForeignKey(
        Propriedade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='politicas_vendas_origem',
        verbose_name="Fazenda de Origem"
    )
    quantidade_transferir = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantidade para Transferir"
    )
    quantidade_comprar = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantidade para Comprar"
    )
    valor_por_cabeca_personalizado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor por Cabeça Personalizado (R$)"
    )
    usar_valor_personalizado = models.BooleanField(
        default=False,
        verbose_name="Usar Valor Personalizado"
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['propriedade', 'categoria']
        verbose_name = "Política de Vendas por Categoria"
        verbose_name_plural = "Políticas de Vendas por Categoria"
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.categoria.nome}: {self.percentual_venda}%"


class ParametrosProjecaoRebanho(models.Model):
    """Modelo para parâmetros de projeção do rebanho"""
    PERIODICIDADE_CHOICES = [
        ('MENSAL', 'Mensal'),
        ('TRIMESTRAL', 'Trimestral'),
        ('SEMESTRAL', 'Semestral'),
        ('ANUAL', 'Anual'),
    ]
    
    propriedade = models.OneToOneField(
        Propriedade, 
        on_delete=models.CASCADE, 
        verbose_name="Propriedade"
    )
    taxa_natalidade_anual = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('85.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Taxa de Natalidade Anual (%)"
    )
    taxa_mortalidade_bezerros_anual = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('5.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Taxa de Mortalidade de Bezerros Anual (%)"
    )
    taxa_mortalidade_adultos_anual = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('2.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Taxa de Mortalidade de Adultos Anual (%)"
    )
    percentual_venda_machos_anual = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('90.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Percentual de Venda de Machos Anual (%)"
    )
    percentual_venda_femeas_anual = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('10.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Percentual de Venda de Fêmeas Anual (%)"
    )
    periodicidade = models.CharField(
        max_length=20, 
        choices=PERIODICIDADE_CHOICES, 
        default='MENSAL',
        verbose_name="Periodicidade"
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Parâmetros de Projeção do Rebanho"
        verbose_name_plural = "Parâmetros de Projeção do Rebanho"
    
    def __str__(self):
        return f"Parâmetros - {self.propriedade.nome_propriedade}"


class ParametrosVendaPorCategoria(models.Model):
    """Modelo para parâmetros de venda por categoria de animal"""
    propriedade = models.ForeignKey(
        Propriedade, 
        on_delete=models.CASCADE, 
        verbose_name="Propriedade"
    )
    categoria = models.ForeignKey(
        CategoriaAnimal, 
        on_delete=models.CASCADE, 
        verbose_name="Categoria"
    )
    percentual_venda_anual = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0')), MaxValueValidator(Decimal('100'))],
        verbose_name="Percentual de Venda Anual (%)"
    )
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    
    class Meta:
        verbose_name = "Parâmetro de Venda por Categoria"
        verbose_name_plural = "Parâmetros de Venda por Categoria"
        unique_together = ['propriedade', 'categoria']
        ordering = ['categoria']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.categoria.nome}: {self.percentual_venda_anual}%"


class MovimentacaoProjetada(models.Model):
    """Modelo para movimentações projetadas do rebanho"""
    TIPO_MOVIMENTACAO_CHOICES = [
        ('NASCIMENTO', 'Nascimento'),
        ('VENDA', 'Venda'),
        ('COMPRA', 'Compra'),
        ('MORTE', 'Morte'),
        ('TRANSFERENCIA_ENTRADA', 'Transferência de Entrada'),
        ('TRANSFERENCIA_SAIDA', 'Transferência de Saída'),
        ('PROMOCAO_ENTRADA', 'Promoção de Entrada (Evolução de Idade)'),
        ('PROMOCAO_SAIDA', 'Promoção de Saída (Evolução de Idade)'),
    ]
    
    propriedade = models.ForeignKey(
        Propriedade, 
        on_delete=models.CASCADE, 
        verbose_name="Propriedade"
    )
    planejamento = models.ForeignKey(
        PlanejamentoAnual,
        on_delete=models.CASCADE,
        related_name='movimentacoes_planejadas',
        null=True,
        blank=True,
        verbose_name="Planejamento anual",
    )
    cenario = models.ForeignKey(
        CenarioPlanejamento,
        on_delete=models.CASCADE,
        related_name='movimentacoes_planejadas',
        null=True,
        blank=True,
        verbose_name="Cenário",
    )
    data_movimentacao = models.DateField(verbose_name="Data da Movimentação")
    tipo_movimentacao = models.CharField(
        max_length=25, 
        choices=TIPO_MOVIMENTACAO_CHOICES, 
        verbose_name="Tipo de Movimentação"
    )
    categoria = models.ForeignKey(
        CategoriaAnimal, 
        on_delete=models.CASCADE, 
        verbose_name="Categoria"
    )
    quantidade = models.IntegerField(verbose_name="Quantidade")
    valor_por_cabeca = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Valor por Cabeça (R$)"
    )
    valor_total = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Valor Total (R$)"
    )
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    
    class Meta:
        verbose_name = "Movimentação Projetada"
        verbose_name_plural = "Movimentações Projetadas"
        ordering = ['data_movimentacao', 'categoria']
    
    def __str__(self):
        nome_cenario = f" [{self.cenario.nome}]" if self.cenario else ""
        return (
            f"{self.propriedade.nome_propriedade}{nome_cenario} - "
            f"{self.get_tipo_movimentacao_display()}: {self.quantidade} {self.categoria.nome}"
        )


class VendaProjetada(models.Model):
    """Modelo para vendas projetadas a partir das projeções de cenários"""
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='vendas_projetadas',
        verbose_name="Propriedade"
    )
    planejamento = models.ForeignKey(
        PlanejamentoAnual,
        on_delete=models.CASCADE,
        related_name='vendas_projetadas',
        null=True,
        blank=True,
        verbose_name="Planejamento Anual"
    )
    cenario = models.ForeignKey(
        CenarioPlanejamento,
        on_delete=models.CASCADE,
        related_name='vendas_projetadas',
        null=True,
        blank=True,
        verbose_name="Cenário"
    )
    movimentacao_projetada = models.ForeignKey(
        MovimentacaoProjetada,
        on_delete=models.CASCADE,
        related_name='vendas_geradas',
        null=True,
        blank=True,
        verbose_name="Movimentação Projetada Origem"
    )
    data_venda = models.DateField(verbose_name="Data da Venda")
    categoria = models.ForeignKey(
        CategoriaAnimal,
        on_delete=models.CASCADE,
        verbose_name="Categoria"
    )
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade")
    # Cliente será referenciado usando lazy reference
    # Nota: O modelo Cliente está em models_cadastros.py mas será resolvido no momento da migração
    cliente_nome = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Nome do Cliente",
        help_text="Nome do cliente da venda (será vinculado ao cadastro quando disponível)"
    )
    peso_total_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso Total (kg)"
    )
    peso_medio_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso Médio por Animal (kg)"
    )
    valor_por_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor por KG (R$)"
    )
    valor_por_animal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor por Animal (R$)"
    )
    valor_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Valor Total (R$)"
    )
    data_recebimento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Recebimento"
    )
    prazo_pagamento_dias = models.PositiveIntegerField(
        default=30,
        verbose_name="Prazo de Pagamento (dias)"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Venda Projetada"
        verbose_name_plural = "Vendas Projetadas"
        ordering = ['-data_venda', 'categoria']
        indexes = [
            models.Index(fields=['propriedade', 'data_venda']),
            models.Index(fields=['cenario', 'data_venda']),
            models.Index(fields=['cliente_nome', 'data_venda']),
        ]
    
    def __str__(self):
        cliente_nome = self.cliente_nome or "Cliente não definido"
        return (
            f"Venda {self.data_venda.strftime('%d/%m/%Y')} - "
            f"{self.quantidade} {self.categoria.nome} - {cliente_nome}"
        )
    
    def calcular_valor_total(self):
        """Calcula o valor total baseado no método de precificação"""
        if self.valor_por_animal and self.quantidade:
            self.valor_total = self.valor_por_animal * self.quantidade
        elif self.valor_por_kg and self.peso_total_kg:
            self.valor_total = self.valor_por_kg * self.peso_total_kg
        elif self.valor_por_animal:
            self.valor_total = self.valor_por_animal * self.quantidade
        return self.valor_total
    
    def calcular_data_recebimento(self):
        """Calcula a data de recebimento baseada no prazo de pagamento"""
        if self.data_venda and not self.data_recebimento:
            from datetime import timedelta
            self.data_recebimento = self.data_venda + timedelta(days=self.prazo_pagamento_dias)
        return self.data_recebimento
    
    def save(self, *args, **kwargs):
        """Sobrescreve save para calcular valores automaticamente"""
        if not self.valor_total or self.valor_total == 0:
            self.valor_total = self.calcular_valor_total() or Decimal('0.00')
        if not self.data_recebimento:
            self.calcular_data_recebimento()
        super().save(*args, **kwargs)


class RegraPromocaoCategoria(models.Model):
    """Modelo para definir regras de promoção de categoria dos animais"""
    categoria_origem = models.ForeignKey(
        CategoriaAnimal, 
        on_delete=models.CASCADE, 
        related_name='promocoes_origem',
        verbose_name="Categoria de Origem"
    )
    categoria_destino = models.ForeignKey(
        CategoriaAnimal, 
        on_delete=models.CASCADE, 
        related_name='promocoes_destino',
        verbose_name="Categoria de Destino"
    )
    idade_minima_meses = models.PositiveIntegerField(verbose_name="Idade Mínima (meses)")
    idade_maxima_meses = models.PositiveIntegerField(verbose_name="Idade Máxima (meses)")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Regra de Promoção de Categoria"
        verbose_name_plural = "Regras de Promoção de Categoria"
        unique_together = ['categoria_origem', 'categoria_destino']
    
    def __str__(self):
        return f"{self.categoria_origem.nome} → {self.categoria_destino.nome}"


class TransferenciaPropriedade(models.Model):
    """Modelo para transferências de animais entre propriedades"""
    TIPO_TRANSFERENCIA_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
    ]
    
    STATUS_CHOICES = [
        ('AGENDADA', 'Agendada'),
        ('REALIZADA', 'Realizada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    propriedade_origem = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='transferencias_origem',
        verbose_name="Propriedade de Origem",
        null=True,
        blank=True
    )
    propriedade_destino = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='transferencias_destino',
        verbose_name="Propriedade de Destino",
        null=True,
        blank=True
    )
    categoria = models.ForeignKey(
        CategoriaAnimal,
        on_delete=models.CASCADE,
        verbose_name="Categoria"
    )
    quantidade = models.PositiveIntegerField(verbose_name="Quantidade")
    data_transferencia = models.DateField(verbose_name="Data da Transferência")
    tipo_transferencia = models.CharField(
        max_length=10,
        choices=TIPO_TRANSFERENCIA_CHOICES,
        verbose_name="Tipo de Transferência"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='AGENDADA',
        verbose_name="Status"
    )
    observacao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observação"
    )
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Transferência entre Propriedades"
        verbose_name_plural = "Transferências entre Propriedades"
        ordering = ['-data_transferencia']
    
    def __str__(self):
        if self.tipo_transferencia == 'ENTRADA':
            return f"{self.propriedade_destino.nome_propriedade} ← {self.quantidade} {self.categoria.nome}"
        else:
            return f"{self.propriedade_origem.nome_propriedade} → {self.quantidade} {self.categoria.nome}"
    
    @property
    def propriedade_relacionada(self):
        """Retorna a propriedade relacionada baseada no tipo de transferência"""
        if self.tipo_transferencia == 'ENTRADA':
            return self.propriedade_destino
        else:
            return self.propriedade_origem


class ConfiguracaoVenda(models.Model):
    """Modelo para configurações avançadas de vendas"""
    FREQUENCIA_CHOICES = [
        ('MENSAL', 'Mensal'),
        ('BIMESTRAL', 'Bimestral'),
        ('TRIMESTRAL', 'Trimestral'),
        ('SEMESTRAL', 'Semestral'),
        ('ANUAL', 'Anual'),
    ]
    
    TIPO_REPOSICAO_CHOICES = [
        ('TRANSFERENCIA', 'Transferência'),
        ('COMPRA', 'Compra'),
        ('VENDA', 'Venda'),
    ]
    
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='configuracoes_venda')
    categoria_venda = models.ForeignKey(CategoriaAnimal, on_delete=models.CASCADE, related_name='configuracoes_venda')
    frequencia_venda = models.CharField(max_length=20, choices=FREQUENCIA_CHOICES)
    quantidade_venda = models.PositiveIntegerField()
    tipo_reposicao = models.CharField(max_length=20, choices=TIPO_REPOSICAO_CHOICES)
    
    # Configurações de Transferência
    fazenda_origem = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='transferencias_origem_config', blank=True, null=True)
    fazenda_destino = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='transferencias_destino_config', blank=True, null=True)
    quantidade_transferencia = models.PositiveIntegerField(blank=True, null=True)
    
    # Configurações de Compra
    categoria_compra = models.ForeignKey(CategoriaAnimal, on_delete=models.CASCADE, related_name='configuracoes_compra', blank=True, null=True)
    quantidade_compra = models.PositiveIntegerField(blank=True, null=True)
    valor_animal_venda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    percentual_desconto = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    valor_animal_compra = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.categoria_venda.nome} ({self.frequencia_venda})"


class CustoFixo(models.Model):
    """Modelo para custos fixos da propriedade"""
    TIPO_CUSTO_CHOICES = [
        ('MAQUINARIO', 'Maquinário e Equipamentos'),
        ('INFRAESTRUTURA', 'Infraestrutura'),
        ('PESSOAL', 'Pessoal'),
        ('ADMINISTRATIVO', 'Administrativo'),
        ('FINANCEIRO', 'Financeiro'),
        ('OUTROS', 'Outros'),
    ]
    TIPO_PERIODO_CHOICES = [
        ('MENSAL', 'Mensal (todos os meses)'),
        ('PERIODO_ESPECIFICO', 'Período específico'),
        ('MESES_ESPECIFICOS', 'Meses específicos'),
    ]
    
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='custos_fixos')
    nome_custo = models.CharField(max_length=200, verbose_name="Nome do Custo")
    tipo_custo = models.CharField(max_length=20, choices=TIPO_CUSTO_CHOICES, verbose_name="Tipo de Custo")
    valor_mensal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Mensal (R$)")
    tipo_periodo = models.CharField(max_length=20, choices=TIPO_PERIODO_CHOICES, default='MENSAL', verbose_name="Tipo de Período")
    meses_aplicaveis = models.JSONField(default=list, null=True, blank=True, verbose_name="Meses Aplicáveis")
    data_inicio = models.DateField(blank=True, null=True, verbose_name="Data de Início")
    data_fim = models.DateField(blank=True, null=True, verbose_name="Data de Fim")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Custo Fixo"
        verbose_name_plural = "Custos Fixos"
        ordering = ['tipo_custo', 'nome_custo']
    
    def __str__(self):
        return f"{self.nome_custo} - R$ {self.valor_mensal}/mês"
    
    @property
    def custo_anual(self):
        if self.tipo_periodo == 'MENSAL':
            return self.valor_mensal * 12
        elif self.tipo_periodo == 'MESES_ESPECIFICOS':
            return self.valor_mensal * len(self.meses_aplicaveis)
        elif self.tipo_periodo == 'PERIODO_ESPECIFICO' and self.data_inicio and self.data_fim:
            from dateutil.relativedelta import relativedelta
            months = (self.data_fim.year - self.data_inicio.year) * 12 + (self.data_fim.month - self.data_inicio.month) + 1
            return self.valor_mensal * months
        return self.valor_mensal * 12
    
    def get_meses_nomes(self):
        """Retorna os nomes dos meses aplicáveis"""
        meses_nomes = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        if self.tipo_periodo == 'MESES_ESPECIFICOS':
            return [meses_nomes.get(mes, f'Mês {mes}') for mes in self.meses_aplicaveis]
        return []
    
    def get_custo_por_mes(self, mes):
        """Retorna o custo para um mês específico"""
        if self.tipo_periodo == 'MENSAL':
            return self.valor_mensal
        elif self.tipo_periodo == 'MESES_ESPECIFICOS':
            return self.valor_mensal if mes in self.meses_aplicaveis else 0
        elif self.tipo_periodo == 'PERIODO_ESPECIFICO' and self.data_inicio and self.data_fim:
            from datetime import date
            data_mes = date(2024, mes, 1)  # Usando 2024 como referência
            return self.valor_mensal if self.data_inicio <= data_mes <= self.data_fim else 0
        return 0


class CustoVariavel(models.Model):
    """Modelo para custos variáveis da propriedade"""
    TIPO_CUSTO_CHOICES = [
        ('ALIMENTACAO', 'Alimentação'),
        ('SANEAMENTO', 'Sanidade'),
        ('REPRODUCAO', 'Reprodução'),
        ('MANEJO', 'Manejo'),
        ('TRANSPORTE', 'Transporte'),
        ('ENERGIA', 'Energia e Combustível'),
        ('OUTROS', 'Outros'),
    ]
    TIPO_PERIODO_CHOICES = [
        ('MENSAL', 'Mensal (todos os meses)'),
        ('PERIODO_ESPECIFICO', 'Período específico'),
        ('MESES_ESPECIFICOS', 'Meses específicos'),
    ]
    
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='custos_variaveis')
    nome_custo = models.CharField(max_length=200, verbose_name="Nome do Custo")
    tipo_custo = models.CharField(max_length=20, choices=TIPO_CUSTO_CHOICES, verbose_name="Tipo de Custo")
    valor_por_cabeca = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor por Cabeça (R$)")
    tipo_periodo = models.CharField(max_length=20, choices=TIPO_PERIODO_CHOICES, default='MENSAL', verbose_name="Tipo de Período")
    meses_aplicaveis = models.JSONField(default=list, null=True, blank=True, verbose_name="Meses Aplicáveis")
    data_inicio = models.DateField(blank=True, null=True, verbose_name="Data de Início")
    data_fim = models.DateField(blank=True, null=True, verbose_name="Data de Fim")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Custo Variável"
        verbose_name_plural = "Custos Variáveis"
        ordering = ['tipo_custo', 'nome_custo']
    
    def __str__(self):
        return f"{self.nome_custo} - R$ {self.valor_por_cabeca}/cabeça"
    
    @property
    def impacto_total(self):
        # Este método será calculado na view baseado no inventário
        return self.valor_por_cabeca
    
    @property
    def custo_anual_por_cabeca(self):
        """Calcula o custo anual por cabeça baseado no período"""
        if self.tipo_periodo == 'MENSAL':
            return self.valor_por_cabeca * 12
        elif self.tipo_periodo == 'MESES_ESPECIFICOS':
            return self.valor_por_cabeca * len(self.meses_aplicaveis)
        elif self.tipo_periodo == 'PERIODO_ESPECIFICO' and self.data_inicio and self.data_fim:
            from dateutil.relativedelta import relativedelta
            months = (self.data_fim.year - self.data_inicio.year) * 12 + (self.data_fim.month - self.data_inicio.month) + 1
            return self.valor_por_cabeca * months
        return self.valor_por_cabeca * 12
    
    def get_meses_nomes(self):
        """Retorna os nomes dos meses aplicáveis"""
        meses_nomes = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        if self.tipo_periodo == 'MESES_ESPECIFICOS':
            return [meses_nomes.get(mes, f'Mês {mes}') for mes in self.meses_aplicaveis]
        return []
    
    def get_custo_por_mes(self, mes):
        """Retorna o custo para um mês específico"""
        if self.tipo_periodo == 'MENSAL':
            return self.valor_por_cabeca
        elif self.tipo_periodo == 'MESES_ESPECIFICOS':
            return self.valor_por_cabeca if mes in self.meses_aplicaveis else 0
        elif self.tipo_periodo == 'PERIODO_ESPECIFICO' and self.data_inicio and self.data_fim:
            from datetime import date
            data_mes = date(2024, mes, 1)  # Usando 2024 como referência
            return self.valor_por_cabeca if self.data_inicio <= data_mes <= self.data_fim else 0
        return 0


# ==================== MÓDULO IMOBILIZADO ====================

class CategoriaImobilizado(models.Model):
    """Modelo para categorias de bens imobilizados"""
    nome = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    vida_util_anos = models.IntegerField(verbose_name="Vida Útil (anos)")
    taxa_depreciacao = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taxa de Depreciação (%)")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    class Meta:
        verbose_name = "Categoria de Imobilizado"
        verbose_name_plural = "Categorias de Imobilizados"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - {self.vida_util_anos} anos"


class BemImobilizado(models.Model):
    """Modelo para bens imobilizados da propriedade"""
    TIPO_AQUISICAO_CHOICES = [
        ('COMPRA', 'Compra'),
        ('DOACAO', 'Doação'),
        ('HERANCA', 'Herança'),
        ('CONSTRUCAO', 'Construção Própria'),
        ('OUTROS', 'Outros'),
    ]
    
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='bens_imobilizados')
    categoria = models.ForeignKey(CategoriaImobilizado, on_delete=models.CASCADE, verbose_name="Categoria")
    nome = models.CharField(max_length=200, verbose_name="Nome do Bem")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marca")
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    numero_serie = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Série")
    
    # Valores
    valor_aquisicao = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor de Aquisição (R$)")
    valor_residual = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Valor Residual (R$)")
    
    # Datas
    data_aquisicao = models.DateField(verbose_name="Data de Aquisição")
    data_inicio_depreciacao = models.DateField(verbose_name="Data de Início da Depreciação")
    
    # Método de aquisição
    tipo_aquisicao = models.CharField(max_length=20, choices=TIPO_AQUISICAO_CHOICES, default='COMPRA', verbose_name="Tipo de Aquisição")
    
    # Status
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Bem Imobilizado"
        verbose_name_plural = "Bens Imobilizados"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.valor_aquisicao}"
    
    @property
    def valor_depreciavel(self):
        """Valor depreciável (aquisição - residual)"""
        return self.valor_aquisicao - self.valor_residual
    
    @property
    def depreciacao_mensal(self):
        """Depreciação mensal"""
        if self.categoria.vida_util_anos > 0:
            return self.valor_depreciavel / (self.categoria.vida_util_anos * 12)
        return 0
    
    @property
    def depreciacao_acumulada(self):
        """Depreciação acumulada até hoje"""
        from datetime import date
        if self.data_inicio_depreciacao:
            meses_depreciacao = max(0, (date.today() - self.data_inicio_depreciacao).days // 30)
            return min(self.depreciacao_mensal * meses_depreciacao, self.valor_depreciavel)
        return 0
    
    @property
    def valor_atual(self):
        """Valor atual (aquisição - depreciacao_acumulada)"""
        return self.valor_aquisicao - self.depreciacao_acumulada


# ==================== MÓDULO ENDIVIDAMENTO ====================

class TipoFinanciamento(models.Model):
    """Modelo para tipos de financiamento"""
    nome = models.CharField(max_length=100, verbose_name="Nome do Tipo")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    class Meta:
        verbose_name = "Tipo de Financiamento"
        verbose_name_plural = "Tipos de Financiamento"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Financiamento(models.Model):
    """Modelo para financiamentos e empréstimos"""
    TIPO_TAXA_CHOICES = [
        ('FIXA', 'Taxa Fixa'),
        ('VARIAVEL', 'Taxa Variável'),
        ('MISTA', 'Taxa Mista'),
    ]
    
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='financiamentos')
    tipo = models.ForeignKey(TipoFinanciamento, on_delete=models.CASCADE, verbose_name="Tipo de Financiamento")
    nome = models.CharField(max_length=200, verbose_name="Nome do Financiamento")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    
    # Valores
    valor_principal = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor Principal (R$)")
    taxa_juros_anual = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taxa de Juros Anual (%)")
    tipo_taxa = models.CharField(max_length=20, choices=TIPO_TAXA_CHOICES, default='FIXA', verbose_name="Tipo de Taxa")
    
    # Datas
    data_contratacao = models.DateField(verbose_name="Data de Contratação")
    data_primeiro_vencimento = models.DateField(verbose_name="Data do Primeiro Vencimento")
    data_ultimo_vencimento = models.DateField(verbose_name="Data do Último Vencimento")
    
    # Características
    numero_parcelas = models.IntegerField(verbose_name="Número de Parcelas")
    valor_parcela = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Valor da Parcela (R$)")
    
    # Status
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Financiamento"
        verbose_name_plural = "Financiamentos"
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} - R$ {self.valor_principal}"


# ==================== MÓDULO ANÁLISE ====================

class IndicadorFinanceiro(models.Model):
    """Modelo para indicadores financeiros"""
    TIPO_INDICADOR_CHOICES = [
        ('LIQUIDEZ', 'Liquidez'),
        ('RENTABILIDADE', 'Rentabilidade'),
        ('ENDIVIDAMENTO', 'Endividamento'),
        ('EFICIENCIA', 'Eficiência'),
        ('OUTROS', 'Outros'),
    ]
    
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='indicadores')
    nome = models.CharField(max_length=200, verbose_name="Nome do Indicador")
    tipo = models.CharField(max_length=20, choices=TIPO_INDICADOR_CHOICES, verbose_name="Tipo de Indicador")
    valor = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Valor do Indicador")
    unidade = models.CharField(max_length=50, default='%', verbose_name="Unidade")
    data_referencia = models.DateField(verbose_name="Data de Referência")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    data_calculo = models.DateTimeField(auto_now_add=True, verbose_name="Data do Cálculo")
    
    class Meta:
        verbose_name = "Indicador Financeiro"
        verbose_name_plural = "Indicadores Financeiros"
        ordering = ['-data_referencia']
    
    def __str__(self):
        return f"{self.nome} - {self.valor} {self.unidade}"


class FluxoCaixa(models.Model):
    """Modelo para controle de fluxo de caixa"""
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='fluxos_caixa')
    data_referencia = models.DateField(verbose_name="Data de Referência")
    receita_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Receita Total (R$)")
    custo_fixo_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Custo Fixo Total (R$)")
    custo_variavel_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Custo Variável Total (R$)")
    lucro_bruto = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Lucro Bruto (R$)")
    margem_lucro = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Margem de Lucro (%)")
    data_calculo = models.DateTimeField(auto_now_add=True, verbose_name="Data do Cálculo")
    
    class Meta:
        verbose_name = "Fluxo de Caixa"
        verbose_name_plural = "Fluxos de Caixa"
        ordering = ['-data_referencia']
        unique_together = ['propriedade', 'data_referencia']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.data_referencia} - R$ {self.lucro_bruto}"
    
    def calcular_margem_lucro(self):
        """Calcula a margem de lucro baseada na receita total"""
        if self.receita_total > 0:
            return (self.lucro_bruto / self.receita_total) * 100
        return 0


# ==================== MÓDULO DÍVIDAS FINANCEIRAS ====================

class SCRBancoCentral(models.Model):
    """Modelo para importação do SCR do Banco Central"""
    STATUS_CHOICES = [
        ('IMPORTADO', 'Importado'),
        ('PROCESSADO', 'Processado'),
        ('DISTRIBUIDO', 'Distribuído'),
        ('ERRO', 'Erro'),
    ]
    
    produtor = models.ForeignKey(ProdutorRural, on_delete=models.CASCADE, related_name='scrs')
    arquivo_pdf = models.FileField(upload_to='scr/', verbose_name="Arquivo PDF do SCR")
    data_importacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Importação")
    data_referencia_scr = models.DateField(verbose_name="Data de Referência do SCR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IMPORTADO', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "SCR Banco Central"
        verbose_name_plural = "SCRs Banco Central"
        ordering = ['-data_importacao']
    
    def __str__(self):
        return f"SCR {self.produtor.nome} - {self.data_referencia_scr}"


class DividaBanco(models.Model):
    """Modelo para dívidas por banco extraídas do SCR"""
    STATUS_CHOICES = [
        ('A_VENCER', 'A Vencer'),
        ('VENCIDO', 'Vencido'),
        ('QUITADO', 'Quitado'),
    ]
    
    scr = models.ForeignKey(SCRBancoCentral, on_delete=models.CASCADE, related_name='dividas')
    banco = models.CharField(max_length=200, verbose_name="Nome do Banco")
    status_divida = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Status da Dívida")
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Total (R$)")
    quantidade_contratos = models.PositiveIntegerField(verbose_name="Quantidade de Contratos")
    data_vencimento = models.DateField(blank=True, null=True, verbose_name="Data de Vencimento")
    
    class Meta:
        verbose_name = "Dívida por Banco"
        verbose_name_plural = "Dívidas por Banco"
        ordering = ['banco', 'status_divida']
    
    def __str__(self):
        return f"{self.banco} - {self.status_divida} - R$ {self.valor_total}"


class ContratoDivida(models.Model):
    """Modelo para contratos individuais de dívida"""
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('QUITADO', 'Quitado'),
        ('VENCIDO', 'Vencido'),
        ('RENEGOCIADO', 'Renegociado'),
    ]
    
    divida_banco = models.ForeignKey(DividaBanco, on_delete=models.CASCADE, related_name='contratos')
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='contratos_divida')
    numero_contrato = models.CharField(max_length=100, verbose_name="Número do Contrato")
    valor_contrato = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor do Contrato (R$)")
    taxa_juros_anual = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taxa de Juros Anual (%)")
    quantidade_parcelas = models.PositiveIntegerField(verbose_name="Quantidade de Parcelas")
    valor_parcela = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor da Parcela (R$)")
    data_inicio = models.DateField(verbose_name="Data de Início")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ATIVO', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Contrato de Dívida"
        verbose_name_plural = "Contratos de Dívida"
        ordering = ['propriedade', 'data_vencimento']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.numero_contrato} - R$ {self.valor_contrato}"


class AmortizacaoContrato(models.Model):
    """Modelo para amortização de contratos"""
    contrato = models.ForeignKey(ContratoDivida, on_delete=models.CASCADE, related_name='amortizacoes')
    numero_parcela = models.PositiveIntegerField(verbose_name="Número da Parcela")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    valor_principal = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Principal (R$)")
    valor_juros = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor dos Juros (R$)")
    valor_total = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Total (R$)")
    saldo_devedor = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Saldo Devedor (R$)")
    data_pagamento = models.DateField(blank=True, null=True, verbose_name="Data de Pagamento")
    valor_pago = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Valor Pago (R$)")
    status_pagamento = models.CharField(max_length=20, choices=[
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('ATRASADO', 'Atrasado'),
    ], default='PENDENTE', verbose_name="Status do Pagamento")
    
    class Meta:
        verbose_name = "Amortização de Contrato"
        verbose_name_plural = "Amortizações de Contratos"
        ordering = ['contrato', 'numero_parcela']
        unique_together = ['contrato', 'numero_parcela']
    
    def __str__(self):
        return f"{self.contrato.numero_contrato} - Parcela {self.numero_parcela} - R$ {self.valor_total}"


# ==================== MÓDULO PROJETO BANCÁRIO ====================

class ProjetoBancario(models.Model):
    """Modelo para projetos de crédito rural"""
    STATUS_CHOICES = [
        ('RASCUNHO', 'Rascunho'),
        ('EM_ANALISE', 'Em Análise'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
        ('CONTRATADO', 'Contratado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    TIPO_PROJETO_CHOICES = [
        ('CUSTEIO', 'Custeio'),
        ('INVESTIMENTO', 'Investimento'),
        ('COMERCIALIZACAO', 'Comercialização'),
        ('REFINANCIAMENTO', 'Refinanciamento'),
    ]
    
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='projetos_bancarios')
    planejamento = models.ForeignKey(
        PlanejamentoAnual,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='projetos_bancarios',
        verbose_name="Planejamento de Projeção",
        help_text="Vincule a um planejamento anual para avaliar cenários de projeção no projeto bancário"
    )
    nome_projeto = models.CharField(max_length=200, verbose_name="Nome do Projeto")
    tipo_projeto = models.CharField(max_length=20, choices=TIPO_PROJETO_CHOICES, verbose_name="Tipo de Projeto")
    banco_solicitado = models.CharField(max_length=200, verbose_name="Banco Solicitado")
    valor_solicitado = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor Solicitado (R$)")
    prazo_pagamento = models.PositiveIntegerField(verbose_name="Prazo de Pagamento (meses)")
    taxa_juros = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taxa de Juros (%)")
    data_solicitacao = models.DateField(verbose_name="Data de Solicitação")
    data_aprovacao = models.DateField(blank=True, null=True, verbose_name="Data de Aprovação")
    valor_aprovado = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name="Valor Aprovado (R$)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RASCUNHO', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    arquivo_projeto = models.FileField(upload_to='projetos/', blank=True, null=True, verbose_name="Arquivo do Projeto")
    
    class Meta:
        verbose_name = "Projeto Bancário"
        verbose_name_plural = "Projetos Bancários"
        ordering = ['-data_solicitacao']
    
    def __str__(self):
        return f"{self.nome_projeto} - {self.propriedade.nome_propriedade} - R$ {self.valor_solicitado}"


class DocumentoProjeto(models.Model):
    """Modelo para documentos de projetos bancários"""
    TIPO_DOCUMENTO_CHOICES = [
        ('PROJETO_TECNICO', 'Projeto Técnico'),
        ('LAUDO_AVALIACAO', 'Laudo de Avaliação'),
        ('CONTRATO', 'Contrato'),
        ('COMPROVANTE_RENDA', 'Comprovante de Renda'),
        ('DOCUMENTO_PROPRIEDADE', 'Documento da Propriedade'),
        ('OUTROS', 'Outros'),
    ]
    
    projeto = models.ForeignKey(ProjetoBancario, on_delete=models.CASCADE, related_name='documentos')
    tipo_documento = models.CharField(max_length=30, choices=TIPO_DOCUMENTO_CHOICES, verbose_name="Tipo de Documento")
    nome_documento = models.CharField(max_length=200, verbose_name="Nome do Documento")
    arquivo = models.FileField(upload_to='projetos/documentos/', verbose_name="Arquivo")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data de Upload")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    class Meta:
        verbose_name = "Documento de Projeto"
        verbose_name_plural = "Documentos de Projetos"
        ordering = ['projeto', 'tipo_documento']
    
    def __str__(self):
        return f"{self.projeto.nome_projeto} - {self.nome_documento}"


# ============================================================================
# SISTEMA DE RASTREABILIDADE BOVINA - PNIB
# ============================================================================

class AnimalIndividual(models.Model):
    """Modelo para identificação individual de animais conforme PNIB"""
    
    TIPO_BRINCO_CHOICES = [
        ('VISUAL', 'Brinco Visual'),
        ('ELETRONICO', 'Brinco Eletrônico (RFID)'),
        ('BOTTON', 'Brinco Botton'),
        ('BOLINHA', 'Brinco Bolinha'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('VENDIDO', 'Vendido'),
        ('MORTO', 'Morto'),
        ('TRANSFERIDO', 'Transferido'),
        ('DESAPARECIDO', 'Desaparecido'),
    ]
    
    STATUS_SANITARIO_CHOICES = [
        ('APTO', 'Apto'),
        ('QUARENTENA', 'Quarentena'),
        ('SUSPEITO', 'Suspeito'),
        ('POSITIVO', 'Positivo'),
        ('INDEFINIDO', 'Indefinido'),
    ]
    
    STATUS_REPRODUTIVO_CHOICES = [
        ('INDEFINIDO', 'Indefinido'),
        ('VAZIA', 'Vazia'),
        ('PRENHE', 'Prenhe'),
        ('LACTACAO', 'Lactação'),
        ('SECAGEM', 'Secagem'),
        ('DESCARTE', 'Descarte'),
    ]

    TIPO_ORIGEM_CHOICES = [
        ('NASCIMENTO', 'Nascimento na propriedade'),
        ('COMPRA', 'Compra'),
        ('TRANSFERENCIA', 'Transferência'),
        ('AJUSTE', 'Ajuste de cadastro'),
    ]

    SISTEMA_CRIACAO_CHOICES = [
        ('PASTO', 'Pasto'),
        ('SEMICONFINADO', 'Semi-confinado'),
        ('CONFINADO', 'Confinado'),
        ('INTEGRADO', 'Sistema integrado'),
    ]

    NIVEL_CONFINAMENTO_CHOICES = [
        ('BAIXO', 'Baixo'),
        ('MEDIO', 'Médio'),
        ('ALTO', 'Alto'),
    ]
    
    # Número único do brinco (formato: BR123456789 ou similar)
    numero_brinco = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Número do Brinco",
        help_text="Número único de identificação do animal"
    )
    
    # Código SISBOV oficial
    codigo_sisbov = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código SISBOV",
        help_text="Código oficial do SISBOV/PNIB"
    )
    
    # Número de manejo extraído do código SISBOV
    numero_manejo = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="Número de Manejo",
        help_text="Número de manejo extraído do código SISBOV (6 dígitos para códigos de 15 dígitos)"
    )
    
    # Código eletrônico (RFID/EID)
    codigo_eletronico = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código Eletrônico",
        help_text="Identificador eletrônico (RFID/EID)"
    )
    
    # Tipo de brinco
    tipo_brinco = models.CharField(
        max_length=20,
        choices=TIPO_BRINCO_CHOICES,
        default='VISUAL',
        verbose_name="Tipo de Brinco"
    )

    apelido = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        verbose_name="Apelido / Nome curto"
    )

    foto = models.ImageField(
        upload_to='animais/fotos/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Foto do Animal"
    )
    
    # Propriedade atual do animal
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='animais_individuais',
        verbose_name="Propriedade"
    )

    mae = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filhos_como_mae',
        verbose_name="Mãe"
    )

    pai = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='filhos_como_pai',
        verbose_name="Pai"
    )
    
    # Categoria do animal
    categoria = models.ForeignKey(
        CategoriaAnimal,
        on_delete=models.CASCADE,
        verbose_name="Categoria"
    )
    
    # Data de nascimento (se conhecida)
    data_nascimento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Nascimento"
    )
    
    # Data de identificação (aplicação do brinco)
    data_identificacao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Identificação"
    )
    
    # Propriedade de origem (onde nasceu ou foi comprado)
    propriedade_origem = models.ForeignKey(
        Propriedade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='animais_nascidos',
        verbose_name="Propriedade de Origem"
    )
    
    # Sexo do animal
    sexo = models.CharField(
        max_length=1,
        choices=[('F', 'Fêmea'), ('M', 'Macho')],
        verbose_name="Sexo"
    )
    
    # Raça (se diferente da categoria)
    raca = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Raça"
    )

    classificacao_zootecnica = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        verbose_name="Classificação zootécnica"
    )

    cota_hilton = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        verbose_name="Cota Hilton",
        help_text="Classificação automática baseada na categoria e características do animal"
    )

    grupo_producao = models.CharField(
        max_length=80,
        blank=True,
        null=True,
        verbose_name="Grupo / linha de produção"
    )

    sistema_criacao = models.CharField(
        max_length=20,
        choices=SISTEMA_CRIACAO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Sistema de criação"
    )

    nivel_confinamento = models.CharField(
        max_length=10,
        choices=NIVEL_CONFINAMENTO_CHOICES,
        blank=True,
        null=True,
        verbose_name="Nível de confinamento"
    )
    
    # Peso atual (em kg)
    peso_atual_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso Atual (kg)"
    )

    produtividade_leite_dia = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Produção diária de leite (L)"
    )
    
    # Lote atual (curral/pasto)
    lote_atual = models.ForeignKey(
        'CurralLote',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='animais_lote',
        verbose_name="Lote Atual"
    )
    
    # Status do animal
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='ATIVO',
        verbose_name="Status"
    )
    
    # Situação sanitária
    status_sanitario = models.CharField(
        max_length=20,
        choices=STATUS_SANITARIO_CHOICES,
        default='INDEFINIDO',
        verbose_name="Status Sanitário"
    )

    status_reprodutivo = models.CharField(
        max_length=20,
        choices=STATUS_REPRODUTIVO_CHOICES,
        default='INDEFINIDO',
        verbose_name="Status Reprodutivo"
    )

    STATUS_BND_CHOICES = [
        ('CONFORME', 'Conforme BND'),
        ('DIVERGENTE', 'Divergente BND'),
        ('NAO_CONFORME', 'Não Conforme'),
    ]

    status_bnd = models.CharField(
        max_length=20,
        choices=STATUS_BND_CHOICES,
        blank=True,
        null=True,
        verbose_name="Status BND",
        help_text="Status de conformidade com o Banco Nacional de Dados (BND)"
    )

    data_ultima_cobertura = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da última cobertura / IATF"
    )

    data_prevista_parto = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data prevista de parto"
    )

    data_ultima_diagnostico = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data do último diagnóstico reprodutivo"
    )

    registro_vacinal_em_dia = models.BooleanField(
        default=True,
        verbose_name="Vacinação em dia"
    )

    proxima_vacinacao_obrigatoria = models.DateField(
        null=True,
        blank=True,
        verbose_name="Próxima vacinação obrigatória"
    )

    carencia_produtos_ate = models.DateField(
        null=True,
        blank=True,
        verbose_name="Carência de produtos até"
    )

    custo_aquisicao = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Custo de aquisição (R$)"
    )

    data_aquisicao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de aquisição"
    )

    valor_atual_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor estimado atual (R$)"
    )

    tipo_origem = models.CharField(
        max_length=20,
        choices=TIPO_ORIGEM_CHOICES,
        default='NASCIMENTO',
        verbose_name="Tipo de origem"
    )

    reprodutor_origem = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        verbose_name="Origem genética / reprodutor"
    )
    
    # Data de cadastro
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    
    # Data de última atualização
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    
    # Data e motivo de saída
    data_saida = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Saída"
    )
    
    motivo_saida = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Motivo da Saída"
    )

    documento_saida = models.CharField(
        max_length=120,
        null=True,
        blank=True,
        verbose_name="Documento de Saída"
    )

    data_ultima_movimentacao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da última movimentação"
    )
    
    # Responsável técnico pela última atualização sanitária
    responsavel_tecnico = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='animais_responsavel',
        verbose_name="Responsável Técnico"
    )
    
    class Meta:
        verbose_name = "Animal Individual"
        verbose_name_plural = "Animais Individuais"
        ordering = ['numero_brinco']
        indexes = [
            models.Index(fields=['numero_brinco']),
            models.Index(fields=['propriedade', 'status']),
        ]
    
    def calcular_cota_hilton(self):
        """Calcula automaticamente a Cota Hilton baseada na categoria e características do animal"""
        if not self.categoria:
            return None
        
        nome_categoria = self.categoria.nome.lower()
        sexo = self.sexo.upper() if self.sexo else ''
        
        # Mapeamento de categorias para Cota Hilton
        # Baseado no nome da categoria e sexo do animal
        if 'bezerro' in nome_categoria and sexo == 'M':
            return 'Bezerro'
        elif 'bezerra' in nome_categoria or ('bezerro' in nome_categoria and sexo == 'F'):
            return 'Bezerra'
        elif 'garrote' in nome_categoria:
            return 'Garrote'
        elif 'novilha' in nome_categoria:
            return 'Novilha'
        elif 'boi' in nome_categoria and 'magro' in nome_categoria:
            return 'Boi Magro'
        elif 'boi' in nome_categoria:
            return 'Boi'
        elif 'primípara' in nome_categoria or 'primipara' in nome_categoria:
            return 'Primípara'
        elif 'multípara' in nome_categoria or 'multipara' in nome_categoria:
            return 'Multípara'
        elif 'vaca' in nome_categoria and 'descarte' in nome_categoria:
            return 'Vaca Descarte'
        elif 'touro' in nome_categoria:
            return 'Touro'
        elif 'matriz' in nome_categoria:
            return 'Matriz'
        else:
            # Se não encontrar correspondência, usa a classificação zootécnica ou nome da categoria
            if self.classificacao_zootecnica:
                return self.classificacao_zootecnica
            return self.categoria.nome
    
    def save(self, *args, **kwargs):
        """Calcula automaticamente o número de manejo e cota_hilton quando o código SISBOV é salvo"""
        import re
        
        # Função auxiliar para extrair número de manejo
        def extrair_numero_manejo(codigo_sisbov):
            if not codigo_sisbov:
                return ''
            codigo_limpo = re.sub(r'\D', '', str(codigo_sisbov))
            if len(codigo_limpo) == 15:
                # Código SISBOV completo: extrair posições 8-13 (6 dígitos)
                return codigo_limpo[8:14]
            elif len(codigo_limpo) >= 8:
                # Lógica anterior para códigos menores
                return codigo_limpo[:-1][-7:]
            return ''
        
        # Calcula o número de manejo se houver código SISBOV
        if self.codigo_sisbov and not self.numero_manejo:
            self.numero_manejo = extrair_numero_manejo(self.codigo_sisbov)
        elif self.codigo_sisbov:
            # Recalcula se o código SISBOV mudou
            novo_manejo = extrair_numero_manejo(self.codigo_sisbov)
            if novo_manejo != self.numero_manejo:
                self.numero_manejo = novo_manejo
        
        # Calcula cota_hilton automaticamente se não estiver preenchido ou se categoria/sexo mudou
        # Verifica se o campo existe no banco de dados (migração pode não ter sido aplicada)
        if hasattr(self, 'cota_hilton'):
            if not self.cota_hilton or (self.categoria and self.cota_hilton != self.calcular_cota_hilton()):
                self.cota_hilton = self.calcular_cota_hilton()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.numero_brinco} - {self.get_status_display()}"
    
    @property
    def idade_meses(self):
        """Calcula a idade do animal em meses"""
        if self.data_nascimento:
            from datetime import date
            today = date.today()
            anos = today.year - self.data_nascimento.year
            meses = today.month - self.data_nascimento.month
            return anos * 12 + meses
        return None
    
    @property
    def idade_anos(self):
        """Calcula a idade do animal em anos"""
        if self.data_nascimento:
            from datetime import date
            today = date.today()
            return today.year - self.data_nascimento.year - (
                (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
            )
        return None


class MovimentacaoIndividual(models.Model):
    """Modelo para histórico de movimentações individuais de animais"""
    
    TIPO_MOVIMENTACAO_CHOICES = [
        ('NASCIMENTO', 'Nascimento'),
        ('COMPRA', 'Compra'),
        ('VENDA', 'Venda'),
        ('TRANSFERENCIA_ENTRADA', 'Transferência de Entrada'),
        ('TRANSFERENCIA_SAIDA', 'Transferência de Saída'),
        ('MORTE', 'Morte'),
        ('MUDANCA_CATEGORIA', 'Mudança de Categoria'),
        ('PESAGEM', 'Pesagem'),
        ('VACINACAO', 'Vacinação'),
        ('TRATAMENTO', 'Tratamento'),
        ('OUTROS', 'Outros'),
    ]
    
    # Animal relacionado
    animal = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        related_name='movimentacoes',
        verbose_name="Animal"
    )
    
    # Tipo de movimentação
    tipo_movimentacao = models.CharField(
        max_length=30,
        choices=TIPO_MOVIMENTACAO_CHOICES,
        verbose_name="Tipo de Movimentação"
    )
    
    # Data da movimentação
    data_movimentacao = models.DateField(
        verbose_name="Data da Movimentação"
    )
    
    # Propriedade de origem (para compras, transferências)
    propriedade_origem = models.ForeignKey(
        Propriedade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_origem',
        verbose_name="Propriedade de Origem"
    )
    
    # Propriedade de destino (para vendas, transferências)
    propriedade_destino = models.ForeignKey(
        Propriedade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_destino',
        verbose_name="Propriedade de Destino"
    )
    
    # Categoria anterior (para mudanças de categoria)
    categoria_anterior = models.ForeignKey(
        CategoriaAnimal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_categoria_anterior',
        verbose_name="Categoria Anterior"
    )
    
    # Categoria nova (para mudanças de categoria)
    categoria_nova = models.ForeignKey(
        CategoriaAnimal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_categoria_nova',
        verbose_name="Categoria Nova"
    )
    
    # Peso no momento da movimentação
    peso_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso (kg)"
    )
    
    # Valor (para compras/vendas)
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor (R$)"
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    
    # Dados do documento (GTA, nota fiscal, etc.)
    numero_documento = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Número do Documento"
    )
    
    DOCUMENTO_TIPO_CHOICES = [
        ('GTA', 'GTA'),
        ('NFE', 'Nota Fiscal'),
        ('PROTOCOLO_SANITARIO', 'Protocolo Sanitário'),
        ('OUTROS', 'Outros'),
    ]
    
    documento_tipo = models.CharField(
        max_length=30,
        choices=DOCUMENTO_TIPO_CHOICES,
        default='OUTROS',
        verbose_name="Tipo do Documento"
    )
    
    documento_emissor = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Emissor do Documento"
    )
    
    data_documento = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data do Documento"
    )
    
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimentacoes_registradas',
        verbose_name="Responsável pelo Registro"
    )
    
    quantidade_animais = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade de Animais Envolvidos"
    )
    
    motivo_detalhado = models.TextField(
        null=True,
        blank=True,
        verbose_name="Motivo Detalhado"
    )
    
    # Data de cadastro
    data_cadastro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Data de Cadastro"
    )
    
    class Meta:
        verbose_name = "Movimentação Individual"
        verbose_name_plural = "Movimentações Individuais"
        ordering = ['-data_movimentacao', '-data_cadastro']
        indexes = [
            models.Index(fields=['animal', 'data_movimentacao']),
            models.Index(fields=['tipo_movimentacao', 'data_movimentacao']),
        ]
    
    def __str__(self):
        return f"{self.animal.numero_brinco} - {self.get_tipo_movimentacao_display()} - {self.data_movimentacao}"


class AnimalPesagem(models.Model):
    """Histórico de pesagens dos animais"""

    animal = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        related_name='pesagens',
        verbose_name="Animal"
    )
    data_pesagem = models.DateField(verbose_name="Data da pesagem")
    peso_kg = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Peso (kg)")
    local = models.CharField(max_length=120, blank=True, null=True, verbose_name="Local da pesagem")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pesagens_registradas',
        verbose_name="Responsável"
    )
    tipo_racao = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        verbose_name="Tipo de ração"
    )
    consumo_racao_kg_dia = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Consumo diário de ração (kg)"
    )
    origem_registro = models.CharField(max_length=60, blank=True, null=True, verbose_name="Origem do registro")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Pesagem de Animal"
        verbose_name_plural = "Pesagens de Animais"
        ordering = ['-data_pesagem', '-criado_em']
        indexes = [
            models.Index(fields=['animal', 'data_pesagem']),
        ]

    def __str__(self):
        return f"{self.animal.numero_brinco} - {self.data_pesagem} - {self.peso_kg} kg"


class AnimalVacinaAplicada(models.Model):
    """Vacinas aplicadas individualmente"""

    animal = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        related_name='vacinas',
        verbose_name="Animal"
    )
    vacina = models.CharField(max_length=120, verbose_name="Vacina")
    data_aplicacao = models.DateField(verbose_name="Data de aplicação")
    dose = models.CharField(max_length=60, blank=True, null=True, verbose_name="Dose")
    lote_produto = models.CharField(max_length=80, blank=True, null=True, verbose_name="Lote do produto")
    validade_produto = models.DateField(blank=True, null=True, verbose_name="Validade do produto")
    proxima_dose = models.DateField(blank=True, null=True, verbose_name="Próxima dose")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vacinas_registradas',
        verbose_name="Responsável"
    )
    carencia_ate = models.DateField(blank=True, null=True, verbose_name="Carência até")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Registrado em")

    class Meta:
        verbose_name = "Vacina aplicada"
        verbose_name_plural = "Vacinas aplicadas"
        ordering = ['-data_aplicacao', '-criado_em']
        indexes = [
            models.Index(fields=['animal', 'data_aplicacao']),
            models.Index(fields=['vacina']),
        ]

    def __str__(self):
        return f"{self.animal.numero_brinco} - {self.vacina} ({self.data_aplicacao})"


class AnimalTratamento(models.Model):
    """Tratamentos sanitários aplicados ao animal"""

    animal = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        related_name='tratamentos',
        verbose_name="Animal"
    )
    produto = models.CharField(max_length=150, verbose_name="Produto / Medicamento")
    dosagem = models.CharField(max_length=120, blank=True, null=True, verbose_name="Dosagem")
    data_inicio = models.DateField(verbose_name="Data de início")
    data_fim = models.DateField(blank=True, null=True, verbose_name="Data de término")
    carencia_ate = models.DateField(blank=True, null=True, verbose_name="Carência até")
    motivo = models.CharField(max_length=200, blank=True, null=True, verbose_name="Motivo do tratamento")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tratamentos_registrados',
        verbose_name="Responsável"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Registrado em")

    class Meta:
        verbose_name = "Tratamento de Animal"
        verbose_name_plural = "Tratamentos de Animais"
        ordering = ['-data_inicio', '-criado_em']
        indexes = [
            models.Index(fields=['animal', 'data_inicio']),
        ]

    def __str__(self):
        return f"{self.animal.numero_brinco} - {self.produto}"


class AnimalReproducaoEvento(models.Model):
    """Eventos reprodutivos relevantes"""

    TIPO_EVENTO_CHOICES = [
        ('COBERTURA', 'Cobertura natural'),
        ('INSEMINACAO', 'Inseminação'),
        ('DIAGNOSTICO', 'Diagnóstico de prenhez'),
        ('PARTO', 'Parto'),
        ('ABORTO', 'Aborto'),
        ('SECAGEM', 'Secagem'),
        ('OUTROS', 'Outros'),
    ]

    animal = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        related_name='eventos_reproducao',
        verbose_name="Animal"
    )
    tipo_evento = models.CharField(max_length=20, choices=TIPO_EVENTO_CHOICES, verbose_name="Tipo de evento")
    data_evento = models.DateField(verbose_name="Data do evento")
    resultado = models.CharField(max_length=120, blank=True, null=True, verbose_name="Resultado")
    touro_reprodutor = models.CharField(max_length=120, blank=True, null=True, verbose_name="Touro / Sêmen utilizado")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_reproducao_registrados',
        verbose_name="Responsável"
    )
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Registrado em")

    class Meta:
        verbose_name = "Evento reprodutivo"
        verbose_name_plural = "Eventos reprodutivos"
        ordering = ['-data_evento', '-criado_em']
        indexes = [
            models.Index(fields=['animal', 'data_evento']),
            models.Index(fields=['tipo_evento']),
        ]

    def __str__(self):
        return f"{self.animal.numero_brinco} - {self.get_tipo_evento_display()} ({self.data_evento})"


class AnimalHistoricoEvento(models.Model):
    """Eventos gerais do animal (trocas de brinco, movimentações internas, observações)"""

    animal = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        related_name='eventos_historico',
        verbose_name="Animal"
    )
    tipo_evento = models.CharField(max_length=60, blank=True, null=True, verbose_name="Tipo de evento")
    descricao = models.TextField(verbose_name="Descrição do evento")
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_animais_registrados',
        verbose_name="Usuário"
    )
    data_evento = models.DateTimeField(auto_now_add=True, verbose_name="Data do registro")
    origem = models.CharField(max_length=60, blank=True, null=True, verbose_name="Origem do registro")

    class Meta:
        verbose_name = "Evento de animal"
        verbose_name_plural = "Eventos de animais"
        ordering = ['-data_evento']
        indexes = [
            models.Index(fields=['animal', 'data_evento']),
        ]

    def __str__(self):
        return f"{self.animal.numero_brinco} - {self.tipo_evento or 'Evento'}"


class AnimalDocumento(models.Model):
    """Documentos anexados ao cadastro do animal"""

    animal = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name="Animal"
    )
    tipo_documento = models.CharField(max_length=60, verbose_name="Tipo de documento")
    descricao = models.CharField(max_length=200, blank=True, null=True, verbose_name="Descrição")
    arquivo = models.FileField(upload_to='animais/documentos/%Y/%m/', verbose_name="Arquivo")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data de upload")
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_animais',
        verbose_name="Usuário"
    )

    class Meta:
        verbose_name = "Documento de animal"
        verbose_name_plural = "Documentos de animais"
        ordering = ['-data_upload']

    def __str__(self):
        return f"{self.animal.numero_brinco} - {self.tipo_documento}"


class BrincoAnimal(models.Model):
    """Modelo para gerenciar brincos disponíveis e utilizados"""
    
    TIPO_BRINCO_CHOICES = [
        ('VISUAL', 'Brinco Visual'),
        ('ELETRONICO', 'Brinco Eletrônico (RFID)'),
        ('BOTTON', 'Brinco Botton'),
        ('BOLINHA', 'Brinco Bolinha'),
    ]
    
    STATUS_CHOICES = [
        ('DISPONIVEL', 'Disponível'),
        ('EM_USO', 'Em Uso'),
        ('DANIFICADO', 'Danificado'),
        ('PERDIDO', 'Perdido'),
    ]
    
    # Número do brinco
    numero_brinco = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Número do Brinco"
    )
    
    codigo_rfid = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Código RFID/EID"
    )
    
    # Tipo de brinco
    tipo_brinco = models.CharField(
        max_length=20,
        choices=TIPO_BRINCO_CHOICES,
        default='VISUAL',
        verbose_name="Tipo de Brinco"
    )
    
    # Status do brinco
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DISPONIVEL',
        verbose_name="Status"
    )
    
    # Animal que está usando (se em uso)
    animal = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='brincos',
        verbose_name="Animal"
    )
    
    # Propriedade que possui o brinco
    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='brincos_propriedade',
        verbose_name="Propriedade"
    )
    
    codigo_lote = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Código do Lote de Brincos"
    )
    
    fornecedor = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Fornecedor"
    )
    
    # Data de aquisição
    data_aquisicao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Aquisição"
    )
    
    # Data de utilização
    data_utilizacao = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Utilização"
    )
    
    data_descarte = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Descarte"
    )
    
    status_motivo = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        verbose_name="Motivo do Status"
    )
    
    valor_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Valor Unitário (R$)"
    )
    
    # Observações
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    
    class Meta:
        verbose_name = "Brinco"
        verbose_name_plural = "Brincos"
        ordering = ['numero_brinco']
        indexes = [
            models.Index(fields=['numero_brinco']),
            models.Index(fields=['status', 'propriedade']),
        ]
    
    def __str__(self):
        return f"{self.numero_brinco} - {self.get_status_display()}"


class CurralSessao(models.Model):
    """Sessão de manejo de curral - agrupa todas as ações do período"""

    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('ENCERRADA', 'Encerrada'),
    ]
    
    TIPO_TRABALHO_CHOICES = [
        ('PESAGEM_ROTINA', 'Pesagem de Rotina'),
        ('VENDA_FRIGORIFICO', 'Venda para Frigorífico'),
        ('VENDA_TERCEIROS', 'Venda Para Terceiros'),
        ('IATF', 'IATF'),
        ('INVENTARIO', 'Inventário de Animais'),
        ('CONFERENCIA', 'Conferência'),
        ('ENTRADA', 'Entrada'),
        ('SAIDA', 'Saída'),
        ('COLETA_DADOS', 'Coleta de Dados'),
        ('OUTROS', 'Outros'),
    ]

    propriedade = models.ForeignKey(
        Propriedade,
        on_delete=models.CASCADE,
        related_name='sessoes_curral',
        verbose_name="Propriedade"
    )
    nome = models.CharField(
        max_length=150,
        verbose_name="Nome da Sessão",
        help_text="Identificação amigável da sessão de curral"
    )
    tipo_trabalho = models.CharField(
        max_length=20,
        choices=TIPO_TRABALHO_CHOICES,
        default='COLETA_DADOS',
        verbose_name="Tipo de Trabalho",
        help_text="Tipo de trabalho que será realizado nesta sessão"
    )
    quantidade_esperada = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Quantidade Esperada",
        help_text="Quantidade de animais esperada para este trabalho"
    )
    nome_lote = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nome do Lote",
        help_text="Nome do lote que será trabalhado"
    )
    pasto_origem = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Pasto de Origem",
        help_text="Pasto de origem dos animais"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descrição / Observações"
    )
    data_inicio = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Início da Sessão"
    )
    data_fim = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Término da Sessão"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ABERTA',
        verbose_name="Status"
    )
    criado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessoes_curral_criadas',
        verbose_name="Responsável"
    )

    class Meta:
        verbose_name = "Sessão de Curral"
        verbose_name_plural = "Sessões de Curral"
        ordering = ['-data_inicio']

    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.nome} ({self.get_status_display()})"

    @property
    def eventos_total(self):
        return self.eventos.count()

    @property
    def animais_manejados(self):
        return self.eventos.exclude(animal__isnull=True).values_list('animal_id', flat=True).distinct().count()


class CurralLote(models.Model):
    """Lotes criados durante uma sessão de curral"""

    FINALIDADE_CHOICES = [
        ('ENGORDA', 'Engorda/Cocho'),
        ('PASTO', 'Retorno ao Pasto'),
        ('VENDA', 'Venda/Leilão'),
        ('REPRODUCAO', 'Reprodução'),
        ('ISOLAMENTO', 'Isolamento/Sanidade'),
        ('OUTROS', 'Outros'),
    ]

    sessao = models.ForeignKey(
        CurralSessao,
        on_delete=models.CASCADE,
        related_name='lotes',
        verbose_name="Sessão"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome do Lote")
    finalidade = models.CharField(
        max_length=20,
        choices=FINALIDADE_CHOICES,
        default='ENGORDA',
        verbose_name="Finalidade"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    ordem_exibicao = models.PositiveIntegerField(default=0, verbose_name="Ordem de Exibição")

    class Meta:
        verbose_name = "Lote de Curral"
        verbose_name_plural = "Lotes de Curral"
        ordering = ['sessao', 'ordem_exibicao', 'nome']

    def __str__(self):
        return f"{self.nome} ({self.get_finalidade_display()})"


class CurralEvento(models.Model):
    """Eventos realizados durante o manejo de curral"""

    EVENTO_CHOICES = [
        ('IDENTIFICACAO', 'Identificação / Conferência'),
        ('PESAGEM', 'Pesagem'),
        ('TROCA_BRINCO', 'Troca de Brinco'),
        ('REPRODUCAO', 'Protocolo Reprodutivo / IATF'),
        ('DIAGNOSTICO', 'Diagnóstico de Prenhez'),
        ('SANIDADE', 'Sanidade / Tratamento'),
        ('ENTRADA', 'Movimentação de Entrada'),
        ('SAIDA', 'Movimentação de Saída'),
        ('APARTACAO', 'Apartação / Lote'),
        ('OUTROS', 'Outros'),
    ]

    PRENHEZ_STATUS_CHOICES = [
        ('DESCONHECIDO', 'Desconhecido'),
        ('AGENDADO', 'Diagnóstico Agendado'),
        ('PRENHA', 'Prenha'),
        ('NAO_PRENHA', 'Não Prenha'),
        ('PARTO', 'Pariu Recentemente'),
    ]

    sessao = models.ForeignKey(
        CurralSessao,
        on_delete=models.CASCADE,
        related_name='eventos',
        verbose_name="Sessão"
    )
    animal = models.ForeignKey(
        AnimalIndividual,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='eventos_curral',
        verbose_name="Animal"
    )
    lote_destino = models.ForeignKey(
        CurralLote,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos',
        verbose_name="Lote Destino"
    )
    tipo_evento = models.CharField(
        max_length=20,
        choices=EVENTO_CHOICES,
        verbose_name="Tipo de Evento"
    )
    data_evento = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora")
    peso_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Peso (kg)"
    )
    variacao_peso = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Variação de Peso"
    )
    brinco_anterior = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Brinco Anterior"
    )
    brinco_novo = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Brinco Novo"
    )
    prenhez_status = models.CharField(
        max_length=15,
        choices=PRENHEZ_STATUS_CHOICES,
        default='DESCONHECIDO',
        verbose_name="Status Reprodutivo"
    )
    data_previsao_parto = models.DateField(
        null=True,
        blank=True,
        verbose_name="Previsão de Parto"
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    dados_adicionais = models.JSONField(blank=True, null=True, verbose_name="Dados Adicionais")
    responsavel = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_curral_registrados',
        verbose_name="Responsável"
    )
    movimentacao = models.ForeignKey(
        MovimentacaoIndividual,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='eventos_curral',
        verbose_name="Movimentação Gerada"
    )

    class Meta:
        verbose_name = "Evento de Curral"
        verbose_name_plural = "Eventos de Curral"
        ordering = ['-data_evento']

    def __str__(self):
        return f"{self.get_tipo_evento_display()} - {self.animal or 'Sem animal'}"

    def save(self, *args, **kwargs):
        from django.utils import timezone

        creating = self._state.adding

        if self.animal and self.tipo_evento == 'PESAGEM' and self.peso_kg:
            # Buscar último peso conhecido para cálculo da variação
            ultimo_evento = CurralEvento.objects.filter(
                animal=self.animal,
                tipo_evento='PESAGEM',
                data_evento__lt=self.data_evento if not creating else timezone.now()
            ).order_by('-data_evento').first()
            if ultimo_evento and ultimo_evento.peso_kg:
                self.variacao_peso = self.peso_kg - ultimo_evento.peso_kg
            else:
                movimentacao_anterior = self.animal.movimentacoes.filter(
                    tipo_movimentacao='PESAGEM'
                ).order_by('-data_movimentacao').first()
                if movimentacao_anterior and movimentacao_anterior.peso_kg:
                    self.variacao_peso = self.peso_kg - movimentacao_anterior.peso_kg

        super().save(*args, **kwargs)

        # Atualizações pós-salvamento
        if self.tipo_evento == 'PESAGEM' and self.animal and self.peso_kg:
            # Atualizar peso atual do animal
            self.animal.peso_atual_kg = self.peso_kg
            self.animal.save(update_fields=['peso_atual_kg', 'data_atualizacao'])

            # Criar ou atualizar movimentação associada
            if not self.movimentacao:
                movimentacao = MovimentacaoIndividual.objects.create(
                    animal=self.animal,
                    tipo_movimentacao='PESAGEM',
                    data_movimentacao=self.data_evento.date(),
                    peso_kg=self.peso_kg,
                    observacoes=self.observacoes or 'Registro de pesagem via sessão de curral'
                )
                self.movimentacao = movimentacao
                super().save(update_fields=['movimentacao'])
            else:
                self.movimentacao.peso_kg = self.peso_kg
                self.movimentacao.data_movimentacao = self.data_evento.date()
                self.movimentacao.observacoes = self.observacoes or self.movimentacao.observacoes
                self.movimentacao.save()

        if self.tipo_evento == 'TROCA_BRINCO' and self.animal and self.brinco_novo:
            brinco_original = self.animal.numero_brinco
            if self.brinco_novo != brinco_original:
                self.brinco_anterior = brinco_original
                # Atualiza brincos auxiliares
                from django.db import transaction
                from django.db.models import Q

                with transaction.atomic():
                    # Liberar brinco antigo, se existir
                    BrincoAnimal.objects.filter(numero_brinco=brinco_original).update(
                        status='DISPONIVEL',
                        animal=None,
                        data_utilizacao=None
                    )
                    # Atribuir brinco novo
                    brinco_obj, created = BrincoAnimal.objects.get_or_create(
                        numero_brinco=self.brinco_novo,
                        defaults={
                            'tipo_brinco': 'VISUAL',
                            'status': 'EM_USO',
                            'animal': self.animal,
                            'propriedade': self.animal.propriedade,
                            'data_utilizacao': timezone.now().date(),
                        }
                    )
                    if not created:
                        brinco_obj.status = 'EM_USO'
                        brinco_obj.animal = self.animal
                        brinco_obj.propriedade = self.animal.propriedade
                        brinco_obj.data_utilizacao = timezone.now().date()
                        brinco_obj.save()

                    # Atualizar animal
                    self.animal.numero_brinco = self.brinco_novo
                    self.animal.save(update_fields=['numero_brinco', 'data_atualizacao'])

                super().save(update_fields=['brinco_anterior'])

        if self.tipo_evento in {'REPRODUCAO', 'DIAGNOSTICO'} and self.animal:
            # Atualizar observações do animal com status reprodutivo mais recente
            info = self.animal.observacoes or ''
            registro = f"\n{self.data_evento.strftime('%d/%m/%Y')} - {self.get_tipo_evento_display()} - {self.get_prenhez_status_display()}"
            if registro.strip() not in info:
                self.animal.observacoes = (info + registro).strip()
                self.animal.save(update_fields=['observacoes', 'data_atualizacao'])


# ============================================================================
# INTEGRAÇÃO WHATSAPP - REGISTRO DE NASCIMENTOS
# ============================================================================

class MensagemWhatsApp(models.Model):
    """Armazena mensagens de WhatsApp recebidas para processamento"""
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente de Processamento'),
        ('PROCESSANDO', 'Processando'),
        ('PROCESSADO', 'Processado com Sucesso'),
        ('ERRO', 'Erro no Processamento'),
        ('AGUARDANDO_CONFIRMACAO', 'Aguardando Confirmação'),
    ]
    
    # Dados da mensagem
    numero_whatsapp = models.CharField(max_length=20, verbose_name="Número do WhatsApp")
    tipo_mensagem = models.CharField(max_length=20, default='audio', verbose_name="Tipo de Mensagem")
    tipo_registro = models.CharField(
        max_length=30,
        choices=[
            ('NASCIMENTO', 'Nascimento'),
            ('SUPLEMENTACAO', 'Distribuição de Suplementação'),
            ('OUTROS', 'Outros'),
        ],
        default='NASCIMENTO',
        verbose_name="Tipo de Registro"
    )
    conteudo_audio_url = models.URLField(blank=True, null=True, verbose_name="URL do Áudio")
    conteudo_texto = models.TextField(blank=True, null=True, verbose_name="Texto Transcrito")
    
    # Dados extraídos
    dados_extraidos = models.JSONField(default=dict, blank=True, verbose_name="Dados Extraídos")
    
    # Status e processamento
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")
    propriedade = models.ForeignKey(
        'Propriedade',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mensagens_whatsapp',
        verbose_name="Propriedade"
    )
    
    # Erros e observações
    erro_processamento = models.TextField(blank=True, null=True, verbose_name="Erro no Processamento")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    
    # Timestamps
    data_recebimento = models.DateTimeField(auto_now_add=True, verbose_name="Data de Recebimento")
    data_processamento = models.DateTimeField(blank=True, null=True, verbose_name="Data de Processamento")
    
    class Meta:
        verbose_name = "Mensagem WhatsApp"
        verbose_name_plural = "Mensagens WhatsApp"
        ordering = ['-data_recebimento']
    
    def __str__(self):
        return f"Mensagem de {self.numero_whatsapp} - {self.get_status_display()}"


class PrecoCEPEA(models.Model):
    """Modelo para armazenar preços médios CEPEA por estado, ano e categoria de animal"""
    
    TIPO_CATEGORIA_CHOICES = [
        ('BEZERRO', 'Bezerro (0-12 meses)'),
        ('BEZERRA', 'Bezerra (0-12 meses)'),
        ('GARROTE', 'Garrote (12-24 meses)'),
        ('NOVILHA', 'Novilha (12-24 meses)'),
        ('BOI', 'Boi (24-36 meses)'),
        ('BOI_MAGRO', 'Boi Magro (24-36 meses)'),
        ('PRIMIPARA', 'Primípara (24-36 meses)'),
        ('MULTIPARA', 'Multípara (>36 meses)'),
        ('VACA_DESCARTE', 'Vaca Descarte (>36 meses)'),
        ('TOURO', 'Touro (>36 meses)'),
    ]
    
    uf = models.CharField(max_length=2, verbose_name="UF", db_index=True)
    ano = models.PositiveIntegerField(verbose_name="Ano", db_index=True)
    tipo_categoria = models.CharField(
        max_length=20,
        choices=TIPO_CATEGORIA_CHOICES,
        verbose_name="Tipo de Categoria",
        db_index=True
    )
    preco_medio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Preço Médio (R$/cabeça)",
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    preco_minimo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Preço Mínimo (R$/cabeça)",
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    preco_maximo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Preço Máximo (R$/cabeça)",
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    fonte = models.CharField(
        max_length=100,
        default='CEPEA',
        verbose_name="Fonte dos Dados"
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name="Data de Atualização"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Observações"
    )
    
    class Meta:
        verbose_name = "Preço CEPEA"
        verbose_name_plural = "Preços CEPEA"
        unique_together = [['uf', 'ano', 'tipo_categoria']]
        ordering = ['-ano', 'uf', 'tipo_categoria']
        indexes = [
            models.Index(fields=['uf', 'ano']),
            models.Index(fields=['tipo_categoria', 'ano']),
        ]
    
    def __str__(self):
        return f"{self.get_tipo_categoria_display()} - {self.uf} ({self.ano}): R$ {self.preco_medio}"


from .models_manejo import (  # noqa: E402,F401
    Manejo,
    ManejoChecklistExecucao,
    ManejoChecklistItem,
    ManejoHistorico,
    ManejoTipo,
)

# Importar modelos de cadastros para garantir que sejam registrados
try:
    from .models_cadastros import (  # noqa: E402,F401
        Cliente,
        Frigorifico,
        UnidadeMedida,
    )
except ImportError:
    # Se houver erro de importação, ignorar
    pass
