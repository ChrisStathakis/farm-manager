from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import GeneralExpenseCategory
from .forms import GeneralExpenseForm


@staff_member_required
def validate_generic_expense_create_view(request, pk):
    category = get_object_or_404(GeneralExpenseCategory, id=pk)
    form = GeneralExpenseForm(request.POST or None, initial={
        'category': category
    })
    if form.is_valid():
        form.save()
    return redirect(category.get_card_url())