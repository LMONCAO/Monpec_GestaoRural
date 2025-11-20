"""Formulários do novo módulo financeiro."""
from django import forms
from django.db.models import Q

from .models_financeiro import (
    CategoriaFinanceira,
    CentroCusto,
    ContaFinanceira,
    LancamentoFinanceiro,
)


class CategoriaFinanceiraForm(forms.ModelForm):
    class Meta:
        model = CategoriaFinanceira
        fields = [
            "propriedade",
            "nome",
            "tipo",
            "categoria_pai",
            "descricao",
            "cor",
            "ativa",
        ]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
            "cor": forms.TextInput(attrs={"type": "color"}),
        }

    def __init__(self, *args, **kwargs):
        propriedade = kwargs.pop("propriedade", None)
        super().__init__(*args, **kwargs)
        self.fields["propriedade"].widget = forms.HiddenInput()
        self.fields["propriedade"].required = False
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            if isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            base_class = "form-select" if isinstance(widget, forms.Select) else "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {base_class}".strip()
        if propriedade:
            self.fields["categoria_pai"].queryset = CategoriaFinanceira.objects.filter(
                Q(propriedade__isnull=True) | Q(propriedade=propriedade)
            ).exclude(id=self.instance.id if self.instance else None)


class CentroCustoFinanceiroForm(forms.ModelForm):
    class Meta:
        model = CentroCusto
        fields = ["propriedade", "nome", "tipo", "descricao", "ativo"]
        widgets = {
            "descricao": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["propriedade"].widget = forms.HiddenInput()
        self.fields["propriedade"].required = False
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            if isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            base_class = "form-select" if isinstance(widget, forms.Select) else "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {base_class}".strip()


class ContaFinanceiraForm(forms.ModelForm):
    class Meta:
        model = ContaFinanceira
        fields = [
            "propriedade",
            "nome",
            "tipo",
            "banco",
            "agencia",
            "numero_conta",
            "saldo_inicial",
            "data_saldo_inicial",
            "permite_negativo",
            "ativa",
        ]
        widgets = {
            "data_saldo_inicial": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["propriedade"].widget = forms.HiddenInput()
        self.fields["propriedade"].required = False
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            if isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            base_class = "form-select" if isinstance(widget, forms.Select) else "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {base_class}".strip()


class LancamentoFinanceiroForm(forms.ModelForm):
    class Meta:
        model = LancamentoFinanceiro
        fields = [
            "propriedade",
            "categoria",
            "centro_custo",
            "conta_origem",
            "conta_destino",
            "descricao",
            "valor",
            "data_competencia",
            "data_vencimento",
            "data_quitacao",
            "forma_pagamento",
            "status",
            "documento_referencia",
            "observacoes",
        ]
        widgets = {
            "data_competencia": forms.DateInput(attrs={"type": "date"}),
            "data_vencimento": forms.DateInput(attrs={"type": "date"}),
            "data_quitacao": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        propriedade = kwargs.pop("propriedade", None)
        super().__init__(*args, **kwargs)
        self.fields["propriedade"].widget = forms.HiddenInput()
        self.fields["propriedade"].required = False
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            if isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            base_class = "form-select" if isinstance(widget, forms.Select) else "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {base_class}".strip()

        if propriedade:
            categorias_qs = CategoriaFinanceira.objects.filter(
                Q(propriedade__isnull=True) | Q(propriedade=propriedade),
                ativa=True,
            ).order_by("tipo", "nome")

            contas_qs = ContaFinanceira.objects.filter(
            propriedade=propriedade,
            ativa=True,
        ).order_by("nome")

            centros_qs = CentroCusto.objects.filter(
                propriedade=propriedade,
                ativo=True,
            ).order_by("nome")

            self.fields["categoria"].queryset = categorias_qs
            self.fields["conta_origem"].queryset = contas_qs
            self.fields["conta_destino"].queryset = contas_qs
            self.fields["centro_custo"].queryset = centros_qs

    def clean(self):
        cleaned = super().clean()
        categoria = cleaned.get("categoria")
        conta_origem = cleaned.get("conta_origem")
        conta_destino = cleaned.get("conta_destino")

        if not categoria:
            return cleaned

        tipo = categoria.tipo

        if tipo == CategoriaFinanceira.TIPO_RECEITA and not conta_destino:
            self.add_error("conta_destino", "Selecione a conta que receberá a receita.")
        elif tipo == CategoriaFinanceira.TIPO_DESPESA and not conta_origem:
            self.add_error("conta_origem", "Selecione a conta de origem da despesa.")
        elif tipo == CategoriaFinanceira.TIPO_TRANSFERENCIA:
            if not conta_origem or not conta_destino:
                self.add_error(
                    None, "Transferências precisam de conta de origem e destino."
                )
            elif conta_origem == conta_destino:
                self.add_error(
                    "conta_destino", "Conta de destino deve ser diferente da origem."
                )

        return cleaned


class ContaPagarForm(forms.ModelForm):
    class Meta:
        from .models_compras_financeiro import ContaPagar
        model = ContaPagar
        fields = [
            "propriedade",
            "fornecedor",
            "ordem_compra",
            "nota_fiscal",
            "descricao",
            "categoria",
            "valor",
            "data_vencimento",
            "data_pagamento",
            "status",
            "forma_pagamento",
            "observacoes",
        ]
        widgets = {
            "data_vencimento": forms.DateInput(attrs={"type": "date"}),
            "data_pagamento": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        propriedade = kwargs.pop("propriedade", None)
        super().__init__(*args, **kwargs)
        self.fields["propriedade"].widget = forms.HiddenInput()
        self.fields["propriedade"].required = False
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            if isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            base_class = "form-select" if isinstance(widget, forms.Select) else "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {base_class}".strip()

        if propriedade:
            from .models_compras_financeiro import Fornecedor, OrdemCompra, NotaFiscal
            self.fields["fornecedor"].queryset = Fornecedor.objects.filter(
                propriedade=propriedade
            ).order_by("nome")
            self.fields["ordem_compra"].queryset = OrdemCompra.objects.filter(
                propriedade=propriedade
            ).order_by("-data_emissao")
            self.fields["nota_fiscal"].queryset = NotaFiscal.objects.filter(
                propriedade=propriedade
            ).order_by("-data_emissao")


class ContaReceberForm(forms.ModelForm):
    class Meta:
        from .models_compras_financeiro import ContaReceber
        model = ContaReceber
        fields = [
            "propriedade",
            "descricao",
            "categoria",
            "cliente",
            "valor",
            "data_vencimento",
            "data_recebimento",
            "status",
            "forma_recebimento",
            "observacoes",
        ]
        widgets = {
            "data_vencimento": forms.DateInput(attrs={"type": "date"}),
            "data_recebimento": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        propriedade = kwargs.pop("propriedade", None)
        super().__init__(*args, **kwargs)
        self.fields["propriedade"].widget = forms.HiddenInput()
        self.fields["propriedade"].required = False
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            if isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} form-check-input".strip()
                continue
            base_class = "form-select" if isinstance(widget, forms.Select) else "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {base_class}".strip()

