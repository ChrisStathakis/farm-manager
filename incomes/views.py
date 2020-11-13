from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView, TemplateView, DetailView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from django_tables2 import RequestConfig

from .models import Income, Costumer
from .tables import IncomeTable, CostumerTable
from .forms import IncomeForm, CostumerForm, CostumerPayment, CostumerPaymentFromCostumerForm


@method_decorator(staff_member_required, name='dispatch')
class IncomeListView(ListView):
    template_name = 'incomes/list_view.html'
    model = Income
    paginate_by = 50

    def get_queryset(self):
        qs = Income.objects.all()
        qs = Income.filters_data(self.request, qs)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['queryset_table'] = IncomeTable(self.object_list)
        context['create_url'] = reverse('incomes:create')
        context['date_filter'] = True
        context['search_filter'], context['costumer_filter'] = 2*[True]
        context['costumers'] = Costumer.objects.all()
        return context


@method_decorator(staff_member_required, name='dispatch')
class InvoiceCreateView(CreateView):
    template_name = 'incomes/form_view.html'
    model = Income
    form_class = IncomeForm
    success_url = reverse_lazy('incomes:list')

    def get_initial(self):
        initial = super().get_initial()
        initial['sum_z'] = 0
        initial['pos'] = 0
        initial['order_cost'] = 0
        initial['extra'] = 0
        initial['sum_z'] = 0
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["back_url"] = self.success_url
        context['form_title'] = "Δημιουργια Εσοδου" 
        return context
    
    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Νεο εσοδο δημιουργηθηκε.')
        return super().form_valid(form)


@method_decorator(staff_member_required, name='dispatch')
class IncomeUpdateView(UpdateView):
    model = Income
    form_class = IncomeForm
    template_name = 'incomes/form_view.html'
    success_url = reverse_lazy('incomes:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.success_url
        context['delete_url'] = self.object.get_delete_url()
        context['form_title'] = f'Επεξεργασια {self.object}'
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'το Εσοδο Ανανεωθηκε')
        return super().form_valid(form)


@staff_member_required
def income_delete_view(request, pk):
    instance = get_object_or_404(Income, id=pk)
    instance.delete()
    messages.warning(request, 'το Εσοδο διαγραφηκε.')
    return redirect(reverse('incomes:list'))


@method_decorator(staff_member_required, name='dispatch')
class CostumerListView(ListView):
    model = Costumer
    template_name = 'list_view.html'
    paginate_by = 50

    def get_queryset(self):
        return Costumer.filters_data(self.request, Costumer.objects.all())

    def get_context_data(self, **kwargs):
        context = super(CostumerListView, self).get_context_data(**kwargs)
        context['create_url'] = reverse('incomes:costumer_create')
        qs_table = CostumerTable(self.object_list)
        RequestConfig(self.request, {'per_page': self.paginate_by}).configure(qs_table)
        context['queryset_table'] = qs_table

        return context


@method_decorator(staff_member_required, name='dispatch')
class CostumerCreateView(CreateView):
    model = Costumer
    template_name = 'form_view.html'
    form_class = CostumerForm

    def get_success_url(self):
        return self.obj.get_edit_url()

    def form_valid(self, form):
        self.obj = form.save()
        return super(CostumerCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CostumerCreateView, self).get_context_data(**kwargs)
        context['back_url'] = reverse('incomes:costumer_list')
        context['form_title'] = 'ΔΗΜΙΟΥΡΓΙΑ ΠΕΛΑΤΗ'
        # context['incomes'] = Income.filters_data(self.request, self.object.incomes.all())
        # context['payments'] = CostumerPayment.filters_data(self.request, self.object.payments.all())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CostumerUpdateView(UpdateView):
    form_class = CostumerForm
    template_name = 'incomes/costumer_card.html'
    model = Costumer

    def get_success_url(self):
        return self.object.get_edit_url()

    def form_valid(self, form):
        form.save()
        return super(CostumerUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CostumerUpdateView, self).get_context_data(**kwargs)
        context['payment_form'] = CostumerPaymentFromCostumerForm(self.request.POST or None, initial={
            'customer': self.object
        })
        context['date_filter'] = True
        context['incomes'] = Income.filters_data(self.request, self.object.incomes.all())
        context['payments'] = CostumerPayment.filters_data(self.request, self.object.payments.all())
        return context


@staff_member_required
def costumer_delete_view(request, pk):
    obj = get_object_or_404(Costumer, id=pk)
    try:
        obj.delete()
    except:
        messages.warning(request, 'ΔΕ ΜΠΟΡΕΙ ΝΑ ΔΙΑΓΡΑΦΕΙ Ο ΥΠΑΡΧΩΝ ΠΕΛΑΤΗΣ')

