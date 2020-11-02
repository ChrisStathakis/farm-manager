from django.shortcuts import get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.http import JsonResponse



from .models import CostumerPayment
from .forms import CostumerPaymentForm


def ajax_modal_view(request, pk):
    obj = get_object_or_404(CostumerPayment, id=pk)
    form = CostumerPaymentForm(request.POST or None, instance=obj)
    data = {}
    data['result'] = render_to_string('',
                                      request=request,
                                      context={
                                          'form': form,
                                          'form_title': obj,

                                      }
                                      )
    return JsonResponse(data)