from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import reverse, redirect, get_object_or_404, render
from .models import CostumerPayment, Costumer, Income
from .forms import CostumerPaymentForm, CostumerPaymentFromCostumerForm, InvoiceFormFromCostumer


@staff_member_required
def validate_payment_creation_view(request, pk):
    costumer = get_object_or_404(Costumer, id=pk)
    form = CostumerPaymentForm(request.POST or None, initial={'customer': costumer})
    if form.is_valid():
        print('is valid')
        form.save()
    else:
        print(form.errors)

    return redirect(costumer.get_edit_url())


@staff_member_required
def validate_update_view(request, pk):
    obj = get_object_or_404(CostumerPayment, id=pk)
    form = CostumerPaymentForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect(obj.customer.get_edit_url())
    return redirect(obj.customer.get_edit_url())


@staff_member_required
def update_or_delete_payment_from_costumer_view(request, pk, type_):
    obj = get_object_or_404(CostumerPayment, id=pk)
    if type_ == 'delete':
        obj.delete()
        return redirect(obj.customer.get_edit_url())
    form = CostumerPaymentFromCostumerForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        return redirect(obj.customer.get_edit_url())

    return render(request, 'incomes/form_view.html', context={
        'form': form,
        'form_title': f'ΕΠΕΞΕΡΓΑΣΙΑ {obj}',
        'back_url': obj.customer.get_edit_url()
    })


@staff_member_required
def update_or_delete_income_view(request, pk, type_):
    obj = get_object_or_404(Income, id=pk)
    if type_ == 'delete':
        obj.delete()
        return redirect(obj.costumer.get_edit_url())
    form = InvoiceFormFromCostumer(request.POST or None, instance=obj, initial={'costumer': obj.costumer})
    if form.is_valid():
        form.save()
        return redirect(obj.costumer.get_edit_url())
    return render(request, 'incomes/form_view.html', context={
        'form': form,
        'form_title': f'{obj}',
        'back_url': obj.costumer.get_edit_url()
    })

