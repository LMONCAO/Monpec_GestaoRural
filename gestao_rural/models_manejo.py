from django.conf import settings
from django.db import models
from django.utils import timezone


class ManejoTipo(models.Model):
    """Catálogo de tipos de manejo disponíveis no sistema."""

    CATEGORIA_CHOICES = [
        ("REPRODUTIVO", "Reprodutivo"),
        ("SANITARIO", "Sanitário"),
        ("NUTRICIONAL", "Nutricional"),
        ("OPERACIONAL", "Operacional"),
        ("COMERCIAL", "Comercial"),
        ("OUTROS", "Outros"),
    ]

    slug = models.SlugField(
        "Identificador",
        max_length=120,
        unique=True,
        null=True,
        blank=True,
        help_text="Identificador único para integrações (ex.: rep_programar_iatf).",
    )
    nome = models.CharField("Nome", max_length=120)
    categoria = models.CharField(
        "Categoria",
        max_length=20,
        choices=CATEGORIA_CHOICES,
        default="OUTROS",
    )
    descricao = models.TextField("Descrição", blank=True)
    instrucoes = models.TextField(
        "Instruções Gerais",
        blank=True,
        help_text="Orientações padrão para execução deste manejo.",
    )
    metadados = models.JSONField(
        "Metadados",
        default=dict,
        blank=True,
        help_text="Configurações adicionais (tags, botões, cores específicas).",
    )
    exige_registro_financeiro = models.BooleanField(
        "Exige vínculo financeiro",
        default=False,
        help_text="Quando marcado, o manejo solicitará lançamento financeiro relacionado.",
    )
    cor_identificacao = models.CharField(
        "Cor de identificação",
        max_length=20,
        default="#0d6efd",
        help_text="Cor hexadecimal utilizada em etiquetas e cards.",
    )
    tempo_estimado_horas = models.DecimalField(
        "Tempo estimado (horas)",
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )
    ativo = models.BooleanField("Ativo", default=True)
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Tipo de Manejo"
        verbose_name_plural = "Tipos de Manejo"
        ordering = ["categoria", "nome"]
        unique_together = [("nome", "categoria")]

    def __str__(self):
        return f"{self.nome} ({self.get_categoria_display()})"


class Manejo(models.Model):
    """Registro operacional de um manejo aplicado a um animal ou lote."""

    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"),
        ("EM_ANDAMENTO", "Em andamento"),
        ("CONCLUIDO", "Concluído"),
        ("CANCELADO", "Cancelado"),
    ]

    PRIORIDADE_CHOICES = [
        ("BAIXA", "Baixa"),
        ("MEDIA", "Média"),
        ("ALTA", "Alta"),
        ("URGENTE", "Urgente"),
    ]

    propriedade = models.ForeignKey(
        "Propriedade",
        on_delete=models.CASCADE,
        related_name="manejos",
        verbose_name="Propriedade",
    )
    animal = models.ForeignKey(
        "AnimalIndividual",
        on_delete=models.CASCADE,
        related_name="manejos",
        verbose_name="Animal",
        blank=True,
        null=True,
        help_text="Opcional. Utilize quando o manejo é específico para um animal.",
    )
    tipo = models.ForeignKey(
        ManejoTipo,
        on_delete=models.PROTECT,
        related_name="manejos",
        verbose_name="Tipo de Manejo",
    )
    titulo = models.CharField(
        "Título",
        max_length=150,
        blank=True,
        help_text="Nome curto para identificar o manejo na agenda.",
    )
    descricao = models.TextField("Descrição detalhada", blank=True)
    status = models.CharField(
        "Status",
        max_length=15,
        choices=STATUS_CHOICES,
        default="PENDENTE",
    )
    prioridade = models.CharField(
        "Prioridade",
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default="MEDIA",
    )
    data_prevista = models.DateField(
        "Data prevista",
        null=True,
        blank=True,
        help_text="Data sugerida para execução do manejo.",
    )
    data_inicio = models.DateTimeField("Iniciado em", null=True, blank=True)
    data_conclusao = models.DateTimeField("Concluído em", null=True, blank=True)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="manejos_responsavel",
        null=True,
        blank=True,
        verbose_name="Responsável",
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="manejos_criados",
        null=True,
        blank=True,
        verbose_name="Criado por",
    )
    observacoes = models.TextField("Observações", blank=True)
    metadados = models.JSONField(
        "Metadados",
        blank=True,
        default=dict,
        help_text="Informações extras específicas do manejo.",
    )
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Manejo"
        verbose_name_plural = "Manejos"
        ordering = ["-data_prevista", "-criado_em"]

    def __str__(self):
        referencia = self.titulo or self.tipo.nome
        if self.animal:
            return f"{referencia} - {self.animal.numero_brinco}"
        return referencia

    @property
    def atrasado(self):
        return (
            self.status in {"PENDENTE", "EM_ANDAMENTO"}
            and self.data_prevista
            and self.data_prevista < timezone.localdate()
        )

    def registrar_transicao(self, novo_status, usuario=None, observacao=None):
        """Atualiza o status e cria histórico da transição."""
        status_anterior = self.status
        if status_anterior == novo_status:
            return

        self.status = novo_status
        if novo_status == "EM_ANDAMENTO" and not self.data_inicio:
            self.data_inicio = timezone.now()
        if novo_status == "CONCLUIDO":
            self.data_conclusao = timezone.now()
        if novo_status in {"PENDENTE", "CANCELADO"}:
            self.data_conclusao = None

        self.save(update_fields=["status", "data_inicio", "data_conclusao", "atualizado_em"])

        ManejoHistorico.objects.create(
            manejo=self,
            status_anterior=status_anterior,
            status_novo=novo_status,
            observacao=observacao or "",
            responsavel=usuario,
        )


class ManejoHistorico(models.Model):
    """Histórico de eventos de um manejo."""

    manejo = models.ForeignKey(
        Manejo,
        on_delete=models.CASCADE,
        related_name="historicos",
        verbose_name="Manejo",
    )
    status_anterior = models.CharField(
        "Status anterior",
        max_length=15,
        choices=Manejo.STATUS_CHOICES,
        blank=True,
        null=True,
    )
    status_novo = models.CharField(
        "Status novo",
        max_length=15,
        choices=Manejo.STATUS_CHOICES,
    )
    observacao = models.TextField("Observação", blank=True)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável",
    )
    data_evento = models.DateTimeField("Data do evento", auto_now_add=True)

    class Meta:
        verbose_name = "Histórico de Manejo"
        verbose_name_plural = "Históricos de Manejo"
        ordering = ["-data_evento"]

    def __str__(self):
        return f"{self.manejo} - {self.get_status_novo_display()}"


class ManejoChecklistItem(models.Model):
    """Itens padrão associados a um tipo de manejo."""

    tipo_manejo = models.ForeignKey(
        ManejoTipo,
        on_delete=models.CASCADE,
        related_name="checklist_itens",
        verbose_name="Tipo de Manejo",
    )
    titulo = models.CharField("Título", max_length=120)
    descricao = models.TextField("Descrição", blank=True)
    ordem = models.PositiveIntegerField("Ordem", default=0)
    exige_anexo = models.BooleanField(
        "Exige anexo",
        default=False,
        help_text="Solicita documento ou foto comprobatória para conclusão.",
    )

    class Meta:
        verbose_name = "Item de Checklist de Manejo"
        verbose_name_plural = "Itens de Checklist de Manejo"
        ordering = ["tipo_manejo", "ordem", "titulo"]

    def __str__(self):
        return f"{self.tipo_manejo.nome} - {self.titulo}"


class ManejoChecklistExecucao(models.Model):
    """Execução dos itens de checklist para um manejo específico."""

    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"),
        ("EM_PROGRESSO", "Em progresso"),
        ("CONCLUIDO", "Concluído"),
    ]

    manejo = models.ForeignKey(
        Manejo,
        on_delete=models.CASCADE,
        related_name="checklist_execucoes",
        verbose_name="Manejo",
    )
    item = models.ForeignKey(
        ManejoChecklistItem,
        on_delete=models.CASCADE,
        related_name="execucoes",
        verbose_name="Item",
    )
    status = models.CharField(
        "Status",
        max_length=15,
        choices=STATUS_CHOICES,
        default="PENDENTE",
    )
    observacao = models.TextField("Observação", blank=True)
    data_conclusao = models.DateTimeField("Concluído em", null=True, blank=True)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Responsável",
    )
    criado_em = models.DateTimeField("Criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Execução de Checklist de Manejo"
        verbose_name_plural = "Execuções de Checklist de Manejo"
        unique_together = [("manejo", "item")]
        ordering = ["manejo", "item__ordem"]

    def __str__(self):
        return f"{self.manejo} - {self.item.titulo}"

    def concluir(self, usuario=None, observacao=None):
        self.status = "CONCLUIDO"
        self.observacao = observacao or self.observacao
        self.responsavel = usuario or self.responsavel
        self.data_conclusao = timezone.now()
        self.save(update_fields=["status", "observacao", "responsavel", "data_conclusao", "atualizado_em"])



