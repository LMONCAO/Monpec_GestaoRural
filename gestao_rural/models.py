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


class Propriedade(models.Model):
    """Modelo para cadastro de propriedades rurais"""
    TIPO_OPERACAO_CHOICES = [
        ('PECUARIA', 'Pecuária'),
        ('AGRICULTURA', 'Agricultura'),
        ('MISTA', 'Mista'),
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
    
    tipo_ciclo_pecuario = models.CharField(
        max_length=20, 
        choices=TIPO_CICLO_PECUARIO_CHOICES, 
        blank=True, 
        null=True,
        verbose_name="Tipo de Ciclo Pecuário"
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
    
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Propriedade"
        verbose_name_plural = "Propriedades"
        ordering = ['nome_propriedade']
    
    def __str__(self):
        return f"{self.nome_propriedade} - {self.produtor.nome}"
    
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
    ]
    
    propriedade = models.ForeignKey(
        Propriedade, 
        on_delete=models.CASCADE, 
        verbose_name="Propriedade"
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
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    
    class Meta:
        verbose_name = "Movimentação Projetada"
        verbose_name_plural = "Movimentações Projetadas"
        ordering = ['data_movimentacao', 'categoria']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.get_tipo_movimentacao_display()}: {self.quantidade} {self.categoria.nome}"


class Cultura(models.Model):
    """Modelo para culturas agrícolas"""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Cultura")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ativo = models.BooleanField(default=True, verbose_name="Ativo")
    
    class Meta:
        verbose_name = "Cultura"
        verbose_name_plural = "Culturas"
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


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


class CicloProducaoAgricola(models.Model):
    """Modelo para ciclos de produção agrícola"""
    propriedade = models.ForeignKey(
        Propriedade, 
        on_delete=models.CASCADE, 
        verbose_name="Propriedade"
    )
    cultura = models.ForeignKey(
        Cultura, 
        on_delete=models.CASCADE, 
        verbose_name="Cultura"
    )
    safra = models.CharField(max_length=20, verbose_name="Safra (ex: 2025/2026)")
    area_plantada_ha = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Área Plantada (ha)"
    )
    produtividade_esperada_sc_ha = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Produtividade Esperada (sc/ha)"
    )
    custo_producao_por_ha = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Custo de Produção por ha (R$)"
    )
    preco_venda_por_sc = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Preço de Venda por sc (R$)"
    )
    data_inicio_plantio = models.DateField(verbose_name="Data de Início do Plantio")
    data_fim_colheita = models.DateField(verbose_name="Data de Fim da Colheita")
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    
    class Meta:
        verbose_name = "Ciclo de Produção Agrícola"
        verbose_name_plural = "Ciclos de Produção Agrícola"
        ordering = ['-data_inicio_plantio']
    
    def __str__(self):
        return f"{self.propriedade.nome_propriedade} - {self.cultura.nome} - {self.safra}"
    
    @property
    def producao_total_esperada_sc(self):
        """Calcula a produção total esperada em sacas"""
        return self.area_plantada_ha * self.produtividade_esperada_sc_ha
    
    @property
    def receita_esperada_total(self):
        """Calcula a receita esperada total"""
        return self.producao_total_esperada_sc * self.preco_venda_por_sc
    
    @property
    def custo_total_producao(self):
        """Calcula o custo total de produção"""
        return self.area_plantada_ha * self.custo_producao_por_ha
    
    @property
    def lucro_esperado(self):
        """Calcula o lucro esperado"""
        return self.receita_esperada_total - self.custo_total_producao


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
