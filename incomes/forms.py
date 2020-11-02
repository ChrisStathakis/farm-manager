from django import forms

from .models import Income, Costumer, CostumerPayment
from vendors.forms import BaseForm


class IncomeForm(BaseForm, forms.ModelForm):
    date_expired = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}), label='Ημερομηνια')
    
    class Meta:
        model = Income
        fields = ['date_expired', 'title', 'costumer', 'value', 'taxes_modifier', ]


class CostumerForm(BaseForm, forms.ModelForm):


    class Meta:
        model = Costumer
        fields = ['active', 'title', 'afm', 'doy', 'cellphone', 'phone', 'notes']


class CostumerPaymentForm(BaseForm, forms.ModelForm):
    date = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}), label='Ημερομηνια')

    class Meta:
        model = CostumerPayment
        fields = ['is_paid', 'customer', 'date', 'payment_method', 'title', 'description', 'value']


class CostumerPaymentFromCostumerForm(CostumerPaymentForm):
    customer = forms.ModelChoiceField(queryset=Costumer.objects.filter(active=True), widget=forms.HiddenInput())


class InvoiceFormFromCostumer(IncomeForm):
    customer = forms.ModelChoiceField(queryset=Income.objects.all(), widget=forms.HiddenInput())