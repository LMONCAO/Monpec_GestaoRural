# -*- coding: utf-8 -*-
"""
Formulários Django Completos para Todos os Módulos
"""

from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.db.models import Q
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date

from .models import Propriedade, CategoriaAnimal, AnimalIndividual, CurralSessao, CurralEvento, CurralLote
from .models_financeiro import CentroCusto, PlanoConta
UserModel = get_user_model()

try:
    from .models_reproducao import Touro, EstacaoMonta, IATF, MontaNatural, Nascimento
    from .models_funcionarios import Funcionario, FolhaPagamento, Holerite, DescontoFuncionario
    from .models_operacional import (
        TanqueCombustivel, AbastecimentoCombustivel, ConsumoCombustivel,
        EstoqueSuplementacao, CompraSuplementacao, DistribuicaoSuplementacao,
        Empreiteiro, ServicoEmpreiteiro, Equipamento, ManutencaoEquipamento
    )
    from .models_compras_financeiro import (
        Fornecedor, NotaFiscal, OrdemCompra, ItemOrdemCompra,
        ContaPagar, ContaReceber,
        RequisicaoCompra, ItemRequisicaoCompra,
        AprovacaoRequisicaoCompra, CotacaoFornecedor,
        ItemCotacaoFornecedor, RecebimentoCompra, ItemRecebimentoCompra,
        SetorPropriedade, ConviteCotacaoFornecedor,
        OrcamentoCompraMensal, AjusteOrcamentoCompra,
    )
    from .models_iatf_completo import (
        ProtocoloIATF, TouroSemen, LoteSemen, LoteIATF, EtapaLoteIATF, IATFIndividual
    )
except ImportError:
    pass


# ============================================================================
# FORMAS DE REPRODUÇÃO
# ============================================================================

class TouroForm(forms.ModelForm):
    class Meta:
        model = Touro
        fields = [
            'numero_brinco', 'nome', 'raca', 'data_nascimento',
            'status', 'propriedade_touro', 'data_primeiro_servico',
            'data_ultima_avaliacao', 'resultado_avaliacao',
            'valor_aquisicao', 'valor_aluguel_mensal', 'observacoes'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_primeiro_servico': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_ultima_avaliacao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class EstacaoMontaForm(forms.ModelForm):
    class Meta:
        model = EstacaoMonta
        fields = [
            'nome', 'tipo', 'data_inicio', 'data_fim',
            'numero_vacas_objetivo', 'taxa_prenhez_objetivo', 'observacoes'
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


# ============================================================================
# FORMAS DE IATF COMPLETO
# ============================================================================

class ProtocoloIATFForm(forms.ModelForm):
    class Meta:
        model = ProtocoloIATF
        fields = [
            'nome', 'tipo', 'descricao',
            'dia_gnrh', 'dia_cidr', 'dia_pgf2a', 'dia_retirada_cidr',
            'dia_gnrh_final', 'dia_iatf',
            'taxa_prenhez_esperada', 'custo_protocolo'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class TouroSemenForm(forms.ModelForm):
    class Meta:
        model = TouroSemen
        fields = [
            'numero_touro', 'nome_touro', 'raca', 'registro',
            'tipo_semen', 'deposito_genetico', 'avaliacao_genetica',
            'preco_dose', 'observacoes'
        ]
        widgets = {
            'avaliacao_genetica': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class LoteSemenForm(forms.ModelForm):
    class Meta:
        model = LoteSemen
        fields = [
            'touro', 'numero_lote', 'numero_doses',
            'data_aquisicao', 'data_validade',
            'preco_unitario', 'localizacao', 'temperatura_armazenamento',
            'fornecedor', 'observacoes'
        ]
        widgets = {
            'data_aquisicao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_validade': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class LoteIATFForm(forms.ModelForm):
    class Meta:
        model = LoteIATF
        fields = [
            'nome_lote', 'protocolo', 'estacao_monta',
            'data_inicio', 'touro_semen', 'lote_semen',
            'categoria_animais', 'score_reprodutivo',
            'inseminador_padrao',
            'custo_medicamentos', 'custo_mao_obra', 'observacoes'
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'categoria_animais': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'score_reprodutivo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
        }


class EtapaLoteIATFForm(forms.ModelForm):
    class Meta:
        model = EtapaLoteIATF
        fields = [
            'nome_etapa', 'codigo_etapa', 'dia_relativo',
            'data_prevista', 'hora_prevista',
            'medicamento_planejado', 'descricao_planejada',
            'responsavel_planejado', 'status',
            'data_execucao', 'hora_execucao',
            'responsavel_execucao', 'inseminador',
            'touro_semen', 'observacoes'
        ]
        widgets = {
            'data_prevista': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_prevista': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'data_execucao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_execucao': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'descricao_planejada': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class IATFIndividualForm(forms.ModelForm):
    class Meta:
        model = IATFIndividual
        fields = [
            'animal_individual', 'lote_iatf', 'estacao_monta', 'protocolo',
            'data_inicio_protocolo', 'touro_semen', 'lote_semen', 'numero_dose',
            'condicao_corporal', 'peso_kg', 'dias_vazia',
            'custo_protocolo', 'custo_semen', 'custo_inseminacao',
            'inseminador', 'veterinario', 'observacoes'
        ]
        widgets = {
            'data_inicio_protocolo': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


# ============================================================================
# FORMAS DE FUNCIONÁRIOS
# ============================================================================

class FuncionarioForm(forms.ModelForm):
    class Meta:
        model = Funcionario
        fields = [
            'nome', 'cpf', 'rg', 'data_nascimento', 'sexo',
            'telefone', 'celular', 'email', 'endereco',
            'cidade', 'estado', 'cep',
            'tipo_contrato', 'cargo', 'data_admissao',
            'salario_base', 'jornada_trabalho',
            'banco', 'agencia', 'conta', 'tipo_conta',
            'observacoes'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_admissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'endereco': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class DescontoFuncionarioForm(forms.ModelForm):
    class Meta:
        model = DescontoFuncionario
        fields = [
            'tipo_desconto', 'descricao', 'valor', 'percentual',
            'data_inicio', 'data_fim', 'numero_parcelas', 'status', 'observacoes'
        ]
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


# ============================================================================
# FORMAS DE SUPLEMENTAÇÃO
# ============================================================================

class EstoqueSuplementacaoForm(forms.ModelForm):
    class Meta:
        model = EstoqueSuplementacao
        fields = [
            'tipo_suplemento', 'unidade_medida',
            'quantidade_atual', 'quantidade_minima',
            'valor_unitario_medio', 'localizacao', 'observacoes'
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class CompraSuplementacaoForm(forms.ModelForm):
    class Meta:
        model = CompraSuplementacao
        fields = [
            'estoque', 'data', 'fornecedor', 'numero_nota_fiscal',
            'quantidade', 'preco_unitario', 'observacoes'
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class DistribuicaoSuplementacaoForm(forms.ModelForm):
    class Meta:
        model = DistribuicaoSuplementacao
        fields = [
            'estoque', 'data', 'pastagem',
            'quantidade', 'numero_animais', 'observacoes'
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


# ============================================================================
# FORMAS DE COMBUSTÍVEL
# ============================================================================

class TanqueCombustivelForm(forms.ModelForm):
    class Meta:
        model = TanqueCombustivel
        fields = [
            'nome', 'capacidade_litros', 'estoque_minimo',
            'localizacao', 'observacoes'
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class ConsumoCombustivelForm(forms.ModelForm):
    class Meta:
        model = ConsumoCombustivel
        fields = [
            'tanque', 'data', 'tipo_equipamento', 'identificacao',
            'quantidade_litros', 'valor_unitario', 'finalidade', 'observacoes'
        ]
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


# ============================================================================
# FORMAS DE COMPRAS
# ============================================================================


class SetorPropriedadeForm(forms.ModelForm):
    responsavel = forms.ModelChoiceField(
        queryset=UserModel.objects.none(),
        required=False,
        label="Responsável",
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Usuário responsável por autorizar ordens relacionadas a este setor."
    )

    class Meta:
        model = SetorPropriedade
        fields = ['nome', 'codigo', 'descricao', 'responsavel', 'ativo']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Oficina, Suprimentos, Pecuária...'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código curto para relatórios'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Resumo das responsabilidades deste setor'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, propriedade=None, **kwargs):
        super().__init__(*args, **kwargs)
        responsaveis_queryset = UserModel.objects.filter(is_active=True).order_by('first_name', 'last_name', 'username')
        self.fields['responsavel'].queryset = responsaveis_queryset
        self.fields['responsavel'].empty_label = "Selecione um responsável"
        self.propriedade_context = propriedade


class ConviteCotacaoFornecedorForm(forms.ModelForm):
    data_expiracao = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label='Data de expiração'
    )

    class Meta:
        model = ConviteCotacaoFornecedor
        fields = ['fornecedor', 'email_destinatario', 'data_expiracao']
        widgets = {
            'fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'email_destinatario': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, requisicao=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Fornecedor.objects.all()
        if requisicao:
            queryset = queryset.filter(
                Q(propriedade=requisicao.propriedade) | Q(propriedade__isnull=True)
            )
        self.fields['fornecedor'].queryset = queryset.order_by('nome')
        self.fields['fornecedor'].empty_label = "Selecione um fornecedor"


class RespostaCotacaoFornecedorCabecalhoForm(forms.ModelForm):
    class Meta:
        model = CotacaoFornecedor
        fields = ['prazo_entrega_estimado', 'condicoes_pagamento', 'valor_frete', 'valor_total', 'observacoes', 'anexo_proposta']
        widgets = {
            'prazo_entrega_estimado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prazo de entrega (ex.: 15 dias)'}),
            'condicoes_pagamento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Condições de pagamento'}),
            'valor_frete': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'readonly': True}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'anexo_proposta': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class RespostaItemCotacaoFornecedorForm(forms.ModelForm):
    class Meta:
        model = ItemCotacaoFornecedor
        fields = ['valor_unitario']
        widgets = {
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


class RequisicaoCompraForm(forms.ModelForm):
    setor = forms.ModelChoiceField(
        queryset=SetorPropriedade.objects.none(),
        required=False,
        label="Setor solicitante",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    equipamento = forms.ModelChoiceField(
        queryset=Equipamento.objects.none(),
        required=False,
        label="Máquina ou equipamento",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    centro_custo = forms.ModelChoiceField(
        queryset=CentroCusto.objects.none(),
        required=False,
        label="Centro de custo",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    plano_conta = forms.ModelChoiceField(
        queryset=PlanoConta.objects.none(),
        required=False,
        label="Plano de contas",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = RequisicaoCompra
        fields = [
            'titulo',
            'justificativa',
            'prioridade',
            'data_necessidade',
            'setor',
            'equipamento',
            'centro_custo',
            'centro_custo_descricao',
            'plano_conta',
            'observacoes',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Compra de insumos para confinamento'}),
            'justificativa': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'data_necessidade': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'centro_custo_descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição livre quando centro de custo não existir'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, propriedade=None, **kwargs):
        super().__init__(*args, **kwargs)

        setores_queryset = SetorPropriedade.objects.all()
        equipamentos_queryset = Equipamento.objects.all()
        centros_custo_queryset = CentroCusto.objects.all()
        planos_conta_queryset = PlanoConta.objects.all()

        if propriedade:
            setor_pk = self.instance.setor_id if self.instance.pk else None
            equipamento_pk = self.instance.equipamento_id if self.instance.pk else None
            centro_custo_pk = self.instance.centro_custo_id if self.instance.pk else None

            setores_queryset = setores_queryset.filter(
                Q(propriedade=propriedade, ativo=True)
                | Q(pk=setor_pk) if setor_pk else Q(propriedade=propriedade, ativo=True)
            )
            equipamentos_queryset = equipamentos_queryset.filter(
                Q(propriedade=propriedade, ativo=True)
                | Q(pk=equipamento_pk) if equipamento_pk else Q(propriedade=propriedade, ativo=True)
            )
            centros_custo_queryset = centros_custo_queryset.filter(
                Q(propriedade=propriedade, ativo=True)
                | Q(pk=centro_custo_pk) if centro_custo_pk else Q(propriedade=propriedade, ativo=True)
            )
            planos_conta_queryset = planos_conta_queryset.filter(
                Q(propriedade=propriedade) | Q(propriedade__isnull=True)
            )

        self.fields['setor'].queryset = setores_queryset.order_by('nome')
        self.fields['equipamento'].queryset = equipamentos_queryset.order_by('nome')
        self.fields['centro_custo'].queryset = centros_custo_queryset.order_by('nome')
        self.fields['plano_conta'].queryset = planos_conta_queryset.filter(ativo=True).order_by('nome')

        self.fields['setor'].empty_label = "Selecione um setor"
        self.fields['equipamento'].empty_label = "Selecione um equipamento"
        self.fields['centro_custo'].empty_label = "Selecione um centro de custo"
        self.fields['plano_conta'].empty_label = "Selecione um plano de contas"

        if not self.instance or not self.instance.centro_custo_descricao:
            self.fields['centro_custo_descricao'].help_text = "Preencha somente quando o centro de custo não estiver cadastrado."


class ItemRequisicaoCompraForm(forms.ModelForm):
    class Meta:
        model = ItemRequisicaoCompra
        fields = [
            'descricao', 'unidade_medida', 'quantidade',
            'valor_estimado_unitario', 'fornecedor_preferencial',
            'observacoes'
        ]
        widgets = {
            'descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Produto ou serviço necessário'}),
            'unidade_medida': forms.Select(attrs={'class': 'form-select'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0'}),
            'valor_estimado_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'fornecedor_preferencial': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class AprovacaoRequisicaoCompraForm(forms.ModelForm):
    class Meta:
        model = AprovacaoRequisicaoCompra
        fields = ['comentario']
        widgets = {
            'comentario': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class CotacaoFornecedorForm(forms.ModelForm):
    class Meta:
        model = CotacaoFornecedor
        fields = [
            'fornecedor', 'status', 'prazo_entrega_estimado',
            'validade_proposta', 'condicoes_pagamento',
            'valor_frete', 'valor_total', 'observacoes', 'anexo_proposta'
        ]
        widgets = {
            'fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'prazo_entrega_estimado': forms.TextInput(attrs={'class': 'form-control'}),
            'validade_proposta': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'condicoes_pagamento': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_frete': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'valor_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'anexo_proposta': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ItemCotacaoFornecedorForm(forms.ModelForm):
    class Meta:
        model = ItemCotacaoFornecedor
        fields = [
            'item_requisicao', 'descricao', 'unidade_medida',
            'quantidade', 'valor_unitario'
        ]
        widgets = {
            'item_requisicao': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'unidade_medida': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0'}),
            'valor_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }


class RecebimentoCompraForm(forms.ModelForm):
    class Meta:
        model = RecebimentoCompra
        fields = [
            'status', 'data_prevista', 'data_recebimento',
            'observacoes', 'comprovante_assinado'
        ]
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'data_prevista': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_recebimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'comprovante_assinado': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class ItemRecebimentoCompraForm(forms.ModelForm):
    class Meta:
        model = ItemRecebimentoCompra
        fields = ['item_ordem', 'quantidade_recebida', 'divergencia', 'justificativa_divergencia']
        widgets = {
            'item_ordem': forms.Select(attrs={'class': 'form-select'}),
            'quantidade_recebida': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'min': '0'}),
            'divergencia': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'justificativa_divergencia': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = [
            'nome', 'nome_fantasia', 'cpf_cnpj', 'tipo',
            'telefone', 'celular', 'email', 'website',
            'endereco', 'cidade', 'estado', 'cep',
            'banco', 'agencia', 'conta', 'observacoes'
        ]
        widgets = {
            'endereco': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class OrdemCompraForm(forms.ModelForm):
    fornecedor = forms.ModelChoiceField(
        queryset=Fornecedor.objects.none(),
        label="Fornecedor",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    setor = forms.ModelChoiceField(
        queryset=SetorPropriedade.objects.none(),
        required=False,
        label="Setor responsável",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    plano_conta = forms.ModelChoiceField(
        queryset=PlanoConta.objects.none(),
        required=False,
        label="Plano de contas",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    centro_custo = forms.ModelChoiceField(
        queryset=CentroCusto.objects.none(),
        required=False,
        label="Centro de custo",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = OrdemCompra
        fields = [
            'fornecedor',
            'numero_ordem',
            'data_emissao',
            'data_entrega_prevista',
            'valor_produtos',
            'valor_frete',
            'setor',
            'plano_conta',
            'centro_custo',
            'centro_custo_descricao',
            'condicoes_pagamento',
            'forma_pagamento',
            'observacoes'
        ]
        widgets = {
            'data_emissao': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_entrega_prevista': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'valor_produtos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'valor_frete': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'centro_custo_descricao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição livre quando o centro de custo não existir'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, propriedade=None, requisicao=None, **kwargs):
        super().__init__(*args, **kwargs)

        fornecedores_qs = Fornecedor.objects.filter(ativo=True)
        setores_qs = SetorPropriedade.objects.filter(ativo=True)
        centros_qs = CentroCusto.objects.all()
        planos_qs = PlanoConta.objects.filter(ativo=True)

        for campo in ['numero_ordem', 'condicoes_pagamento', 'forma_pagamento']:
            if campo in self.fields:
                self.fields[campo].widget.attrs.setdefault('class', 'form-control')

        if propriedade:
            fornecedores_qs = fornecedores_qs.filter(
                Q(propriedade=propriedade) | Q(propriedade__isnull=True)
            ).order_by('nome')
            setores_qs = setores_qs.filter(propriedade=propriedade).order_by('nome')
        
        centros_qs = centros_qs.order_by('nome')
        planos_qs = planos_qs.order_by('nome')

        self.fields['fornecedor'].queryset = fornecedores_qs
        self.fields['setor'].queryset = setores_qs
        self.fields['centro_custo'].queryset = centros_qs
        self.fields['plano_conta'].queryset = planos_qs

        self.fields['fornecedor'].empty_label = "Selecione um fornecedor"
        self.fields['setor'].empty_label = "Selecione um setor"
        self.fields['centro_custo'].empty_label = "Selecione um centro de custo"
        self.fields['plano_conta'].empty_label = "Selecione um plano de contas"

        if requisicao:
            if requisicao.setor_id:
                self.initial.setdefault('setor', requisicao.setor_id)
            if requisicao.plano_conta_id:
                self.initial.setdefault('plano_conta', requisicao.plano_conta_id)
            if requisicao.centro_custo_id:
                self.initial.setdefault('centro_custo', requisicao.centro_custo_id)
            if requisicao.centro_custo_descricao:
                self.initial.setdefault('centro_custo_descricao', requisicao.centro_custo_descricao)


class OrdemCompraAutorizacaoForm(forms.Form):
    DECISAO_CHOICES = [
        ('AUTORIZADA', 'Autorizar aquisição'),
        ('NEGADA', 'Negar/solicitar ajustes'),
    ]

    decisao = forms.ChoiceField(
        choices=DECISAO_CHOICES,
        label="Decisão",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    observacoes = forms.CharField(
        label="Observações",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Informe justificativas, ajustes ou anexos necessários.'}),
    )


class OrcamentoCompraMensalForm(forms.ModelForm):
    class Meta:
        model = OrcamentoCompraMensal
        fields = ['setor', 'mes', 'ano', 'valor_limite', 'observacoes']
        widgets = {
            'setor': forms.Select(attrs={'class': 'form-select'}),
            'mes': forms.Select(attrs={'class': 'form-select'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'valor_limite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'observacoes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, propriedade=None, **kwargs):
        super().__init__(*args, **kwargs)
        setores_qs = SetorPropriedade.objects.filter(ativo=True)
        if propriedade:
            setores_qs = setores_qs.filter(propriedade=propriedade).order_by('nome')
        self.fields['setor'].queryset = setores_qs
        self.fields['setor'].required = False
        self.fields['setor'].empty_label = "Orçamento geral da propriedade"
        self.fields['valor_limite'].label = "Limite mensal (R$)"


class AjusteOrcamentoCompraForm(forms.ModelForm):
    class Meta:
        model = AjusteOrcamentoCompra
        fields = ['valor', 'justificativa']
        widgets = {
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'}),
            'justificativa': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Descreva o motivo do limite extra emergencial.'}),
        }


# ============================================================================
# FORMULÁRIOS - SUPER TELA CURRAL
# ============================================================================

class CurralSessaoForm(forms.ModelForm):
    class Meta:
        model = CurralSessao
        fields = ['nome', 'descricao']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Curral 01 - 05/08 (Lote Novilhas)'}),
            'descricao': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Observações gerais da sessão'}),
        }


class CurralLoteForm(forms.ModelForm):
    class Meta:
        model = CurralLote
        fields = ['nome', 'finalidade', 'observacoes']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lote de destino'}),
            'finalidade': forms.Select(attrs={'class': 'form-select'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class CurralEventoForm(forms.ModelForm):
    class Meta:
        model = CurralEvento
        fields = [
            'animal', 'tipo_evento', 'peso_kg', 'prenhez_status',
            'data_previsao_parto', 'brinco_novo', 'lote_destino',
            'observacoes'
        ]
        widgets = {
            'animal': forms.Select(attrs={
                'class': 'form-select form-select-sm select2',
                'data-placeholder': 'Selecione o animal pelo número do brinco',
            }),
            'tipo_evento': forms.Select(attrs={'class': 'form-select form-select-sm', 'data-placeholder': 'Tipo de manejo realizado'}),
            'peso_kg': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Informe o peso aferido em kg',
            }),
            'prenhez_status': forms.Select(attrs={'class': 'form-select form-select-sm', 'data-placeholder': 'Status reprodutivo atual'}),
            'data_previsao_parto': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'brinco_novo': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Novo brinco, caso tenha ocorrido troca'}),
            'lote_destino': forms.Select(attrs={'class': 'form-select form-select-sm', 'data-placeholder': 'Selecione o lote destino'}),
            'observacoes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control form-control-sm', 'placeholder': 'Descreva detalhes relevantes deste evento'}),
        }

    def __init__(self, *args, **kwargs):
        propriedade = kwargs.pop('propriedade', None)
        sessao = kwargs.pop('sessao', None)
        super().__init__(*args, **kwargs)

        if propriedade:
            self.fields['animal'].queryset = AnimalIndividual.objects.filter(propriedade=propriedade).order_by('numero_brinco')

        if sessao:
            self.fields['lote_destino'].queryset = sessao.lotes.all()
        else:
            self.fields['lote_destino'].queryset = CurralLote.objects.none()

        self.fields['animal'].required = False
        self.fields['peso_kg'].required = False
        self.fields['brinco_novo'].required = False
        self.fields['data_previsao_parto'].required = False
