from django import forms
from django.forms import inlineformset_factory

from .models import Movimentacao, Item


# =========================
# 📦 MOVIMENTAÇÃO FORM
# =========================
class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = [
            'data',
            'tipo',
            'fornecedor',
            'nf',
            'cfop',
            'div',
            'local',
            'placa',
            'obs',
            'visto_patio',
            'visto_conferente',
            'cartao_patio',
            'cartao_conferente',
        ]

        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'fornecedor': forms.TextInput(attrs={'class': 'form-control'}),
            'nf': forms.TextInput(attrs={'class': 'form-control'}),
            'cfop': forms.TextInput(attrs={'class': 'form-control'}),
            'div': forms.TextInput(attrs={'class': 'form-control'}),
            'local': forms.Select(attrs={'class': 'form-control'}),
            'placa': forms.TextInput(attrs={'class': 'form-control'}),
            'obs': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# =========================
# 📋 ITEM FORM
# =========================
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['material', 'unidade', 'div', 'descricao', 'quantidade']

        widgets = {
            'material': forms.TextInput(attrs={'class': 'form-control'}),
            'unidade': forms.TextInput(attrs={'class': 'form-control'}),
            'div': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.TextInput(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    # 🔥 Validação básica (evita item vazio)
    def clean(self):
        cleaned_data = super().clean()

        material = cleaned_data.get('material')
        quantidade = cleaned_data.get('quantidade')

        # Se todos campos vazios → ignora (formset trata)
        if not material and not quantidade:
            return cleaned_data

        if not material:
            raise forms.ValidationError("Material é obrigatório.")

        if quantidade is None or quantidade <= 0:
            raise forms.ValidationError("Quantidade deve ser maior que zero.")

        return cleaned_data


# =========================
# 📑 FORMSET
# =========================
ItemFormSet = inlineformset_factory(
    Movimentacao,
    Item,
    form=ItemForm,
    extra=1,          # melhor UX
    can_delete=True
)