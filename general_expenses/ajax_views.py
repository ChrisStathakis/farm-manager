from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, reverse

from .forms import GeneralFormFromCategory
from .models import GeneralExpense


@staff_member_required
def ajax_generic_expense_modal_view(request, pk):
    instance = get_object_or_404(GeneralExpense, id=pk)
    form = GeneralFormFromCategory(request.POST or None, instance=instance)
    data = dict()
    data['result'] = render_to_string(
        template_name='payroll/ajax/form_modal.html',
        request=request,
        context={
            'form': form,
            'bill': instance,
            'page_title': instance.title,
            'copy_url': reverse('payroll_bills:copy_bill_view', kwargs={'pk': instance.id}),
            'success_url': reverse('payroll_bills:validate_bill_edit_form', kwargs={'pk': instance.id}),
            'delete_url': instance.get_delete_url()
        }
    )
    return JsonResponse(data)