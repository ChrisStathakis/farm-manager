from django.db.models import Sum, FloatField, F
from django.db.models.functions import TruncMonth
from django.shortcuts import  reverse

from django.views.generic import ListView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings


from operator import attrgetter
from itertools import chain

from incomes.models import Income, Costumer, CostumerPayment
from products.models import Product, ProductVendor
from payroll.models import Bill, Payroll
from vendors.models import Payment, Invoice
from general_expenses.models import GeneralExpense
from .tools import sort_months


@method_decorator(staff_member_required, name='dispatch')
class AnalysisHomepage(TemplateView):
    template_name = 'analysis/homepage.html'


@method_decorator(staff_member_required, name='dispatch')
class AnalysisIncomeView(ListView):
    model = Income
    template_name = 'analysis/analysis_incomes.html'
    paginate_by = 100

    def get_queryset(self):
        qs = Income.objects.all()
        qs = Income.filters_data(self.request, qs)
        return qs

    def get_context_data(self,  **kwargs):
        context = super().get_context_data(**kwargs)
        date_filter, currency = True, settings.CURRENCY
        back_url = reverse('analysis:homepage')
        total_value = round(self.object_list.aggregate(Sum('total_value'))['total_value__sum'] if self.object_list.exists() else 0, 2)
        taxes = round(self.object_list.aggregate(Sum('taxes'))['taxes__sum'] if self.object_list.exists() else 0, 2)
        clean_value = round(self.object_list.aggregate(Sum('value'))['value__sum'] if self.object_list.exists() else 0, 2)
        context['costumer_filter'] = True
        context['costumers'] = Costumer.objects.all()
        #     total=Sum('final_value')).values('month', 'total').order_by('month')
        analysis_per_month = self.object_list.annotate(month=TruncMonth('date_expired')).values('month').annotate(
            total=Sum('value')).values('month', 'total').order_by('month')

        analysis_value_per_month = self.object_list.annotate(month=TruncMonth('date_expired')).values('month').annotate(
            total=Sum('value')).values('month', 'total').order_by('month')
        analysis_taxes_per_month = self.object_list.annotate(month=TruncMonth('date_expired')).values('month').annotate(
            total=Sum('taxes')).values('month', 'total').order_by('month')
        analysis_total_value_per_month = self.object_list.annotate(month=TruncMonth('date_expired')).values('month').annotate(
            total=Sum('total_value')).values('month', 'total').order_by('month')
        total_incomes = self.object_list.aggregate(Sum('total_value'))['total_value__sum']

        context.update(locals())
        return context
    

@method_decorator(staff_member_required, name='dispatch')
class AnalysisOutcomeView(TemplateView):
    template_name = 'analysis/analysis_outcome.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currency = settings.CURRENCY
        back_url = reverse('analysis:homepage')
        date_filter = True

        # grab the data
        bills = Bill.filters_data(self.request, Bill.objects.all())
        payrolls = Payroll.filters_data(self.request, Payroll.objects.all())
        invoices = Invoice.filters_data(self.request, Invoice.objects.all())
        generic_expenses = GeneralExpense.filters_data(self.request, GeneralExpense.objects.all())

        # calculate the total taxes
        total_taxes = 0
        total_taxes += invoices.aggregate(Sum('total_taxes'))['total_taxes__sum'] if invoices.exists() else 0
        total_taxes += generic_expenses.aggregate(Sum('total_taxes'))['total_taxes__sum'] if generic_expenses.exists() else 0
        total_taxes += bills.aggregate(Sum('total_taxes'))['total_taxes__sum'] if bills.exists() else 0

        generic_expenses_analysis = generic_expenses.values('category__title').annotate(total=Sum('value')).order_by('-total')
        generic_expenses_analysis_per_month = generic_expenses.annotate(month=TruncMonth('date')).values('month'). \
            annotate(total=Sum('value')).values('month', 'total').order_by('month')

        total_bills = bills.aggregate(Sum('final_value'))['final_value__sum'] if bills else 0
        analysis_bills = bills.values('category__title').annotate(total=Sum('final_value')).order_by('-total')
        analysis_bills_per_month = bills.annotate(month=TruncMonth('date_expired')).values('month').annotate(
            total=Sum('final_value')).values('month', 'total').order_by('month')

        total_payroll = payrolls.aggregate(Sum('final_value'))['final_value__sum'] if payrolls else 0
        total_invoices = invoices.aggregate(Sum('final_value'))['final_value__sum'] if invoices else 0
        total_generic = generic_expenses.aggregate(Sum('value'))['value__sum'] if generic_expenses else 0
        total_expenses = total_bills + total_payroll + total_invoices + total_generic
        analysis_invoices = invoices.values('vendor__title').annotate(total=Sum('final_value')).order_by('-total')
        analysis_invoices_per_month = invoices.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('final_value')).values('month', 'total').order_by('month')
        payroll_analysis = payrolls.values('person__title').annotate(total=Sum('final_value')).order_by('-total')
        payroll_analysis_per_month = payrolls.annotate(month=TruncMonth('date_expired')).values('month').\
            annotate(total=Sum('final_value')).values('month', 'total').order_by('month')

        # get unique months
        months = sort_months([analysis_invoices_per_month, analysis_bills_per_month, payroll_analysis_per_month, generic_expenses_analysis_per_month])

        result_per_months = []
        for month in months:
            data = {
                'month': month,
                'total': 0
            }
            # data['invoice'] = ele['total'] for ele in analysis_invoices_per_month if ele['month'] == month else 0
            for ele in analysis_invoices_per_month:
                if ele['month'] == month:
                    data['invoice'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in analysis_bills_per_month:
                if ele['month'] == month:
                    data['bills'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in payroll_analysis_per_month:
                if ele['month'] == month:
                    data['payroll'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in generic_expenses_analysis_per_month:
                if ele['month'] == month:
                    data['generic'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            data['invoice'] = data['invoice'] if 'invoice' in data.keys() else 0
            data['bills'] = data['bills'] if 'bills' in data.keys() else 0
            data['payroll'] = data['payroll'] if 'payroll' in data.keys() else 0
            data['generic'] = data['generic'] if 'generic' in data.keys() else 0
            result_per_months.append(data)

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class CashRowView(TemplateView):
    template_name = 'analysis/cash_row.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        currency = settings.CURRENCY
        back_url = reverse('analysis:homepage')
        incomes = Income.filters_data(self.request, Income.objects.all()).order_by('date_expired')
        income_clean_value, income_taxes, income_value = 0, 0, 0
        if incomes.exists():
            income_clean_value = incomes.aggregate(Sum('clean_value'))['clean_value__sum']
            income_taxes = incomes.aggregate(Sum('taxes'))['taxes__sum']
            income_value = incomes.aggregate(Sum('final_value'))['final_value__sum']

        total_z = incomes.aggregate(Sum('sum_z'))['sum_z__sum'] if incomes.exists() else 0
        total_pos = incomes.aggregate(Sum('pos'))['pos__sum'] if incomes.exists() else 0
        total_cash = total_z - total_pos
        total_order = incomes.aggregate(Sum('order_cost'))['order_cost__sum'] if incomes.exists() else 0
        total = incomes.aggregate(Sum('value'))['value__sum'] if incomes.exists() else 0

        date_filter = True

        # outcomes
        vendor_payments = Payment.filters_data(self.request, Payment.objects.all())
        vendor_payments_total = vendor_payments.aggregate(Sum('value'))['value__sum'] if vendor_payments.exists() else 0

        payrolls = Payroll.filters_data(self.request, Payroll.objects.filter(is_paid=True))
        payrolls_total = payrolls.aggregate(Sum('final_value'))['final_value__sum'] if payrolls.exists() else 0

        bills = Bill.filters_data(self.request, Bill.objects.filter(is_paid=True))
        bills_total = bills.aggregate(Sum('final_value'))['final_value__sum'] if bills.exists() else 0

        generic_expenses = GeneralExpense.filters_data(self.request, GeneralExpense.objects.filter(is_paid=True))
        generic_expenses_total = generic_expenses.aggregate(Sum('value'))['value__sum'] if generic_expenses.exists() else 0

        total_expenses = vendor_payments_total + bills_total + payrolls_total + generic_expenses_total
        expenses_query = sorted(
                chain(bills, vendor_payments, payrolls, generic_expenses),
                key=attrgetter('report_date'))
        diff = round(total - total_expenses, 2)
        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class BalanceSheetView(TemplateView):
    template_name = 'analysis/balance_sheet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_filter, currency = True, settings.CURRENCY

        # incomes
        incomes = Income.filters_data(self.request, Income.objects.all())
        paid_incomes = CostumerPayment.filters_data(self.request, CostumerPayment.objects.all())
        income_clean_value, income_taxes, income_value = 0, 0, 0
        paid_incomes = paid_incomes.aggregate(Sum('value'))['value__sum'] if paid_incomes.exists() else 0
        if incomes.exists():
            income_clean_value = round(incomes.aggregate(Sum('value'))['value__sum'], 2)
            income_taxes = round(incomes.aggregate(Sum('taxes'))['taxes__sum'], 2)
            income_value = round(incomes.aggregate(Sum('total_value'))['total_value__sum'], 2)
        remaining_incomes = income_value - paid_incomes

        incomes_per_month = incomes.annotate(month=TruncMonth('date_expired')).values('month', 'total_value').annotate(
            total=Sum('total_value')).values('month', 'total').order_by('month')
        incomes_per_month_table = incomes.annotate(month=TruncMonth('date_expired')).values('month')\
            .annotate(
                      total_taxes=Sum('taxes'),
                      total_value=Sum('value'),
                      # totalk=Sum('total_value')
                      ).order_by('month')



        # vendors data

        invoices = Invoice.filters_data(self.request, Invoice.objects.all())
        invoices_per_month = invoices.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('final_value')).values('month', 'total').order_by('month')
        invoices_total = invoices.aggregate(Sum('final_value'))['final_value__sum'] if invoices.exists() else 0
        invoices_taxes = invoices.aggregate(Sum('total_taxes'))['total_taxes__sum'] if invoices.exists() else 0
        vendors = invoices.values('vendor__title', 'vendor__balance').annotate(total=Sum('final_value')).order_by('-total')[:15]

        # payments
        payments = Payment.filters_data(self.request, Payment.objects.all())
        payments_total = payments.aggregate(Sum('value'))['value__sum'] if payments.exists() else 0
        # payments_taxes = payments.aggregate(Sum('total_taxes'))['total_taxes__sum'] if payments.exists() else 0
        vendors_remaining = invoices_total - payments_total

        # bills
        bills = Bill.filters_data(self.request, Bill.objects.all())
        bills_per_month = bills.annotate(month=TruncMonth('date_expired')).values('month').annotate(total=Sum('final_value')).values('month', 'total').order_by('month')
        bills_total = bills.aggregate(Sum('final_value'))['final_value__sum'] if bills.exists() else 0
        bills_taxes = bills.aggregate(Sum('total_taxes'))['total_taxes__sum'] if bills.exists() else 0
        bills_paid_total = bills.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] if bills.filter(is_paid=True).exists() else 0
        bills_per_bill = bills.values('category__title').annotate(total_pay=Sum('final_value'),
                                                                  paid_value=Sum('paid_value'))\
            .order_by('category__title')

        # payrolls
        payrolls = Payroll.filters_data(self.request, Payroll.objects.all())
        payroll_per_month = payrolls.annotate(month=TruncMonth('date_expired')).values('month').annotate(total=Sum('final_value')).values('month', 'total').order_by('month')
        payrolls_total = payrolls.aggregate(Sum('final_value'))['final_value__sum'] if payrolls.exists() else 0
        payrolls_paid_total = payrolls.filter(is_paid=True).aggregate(Sum('final_value'))['final_value__sum'] if payrolls.filter(is_paid=True).exists() else 0
        payroll_per_person = payrolls.values('person__title').annotate(total_pay=Sum('final_value'),
                                                                       paid_value=Sum('paid_value'))\
            .order_by('person__title')

        # general Expenses
        general_expenses = GeneralExpense.filters_data(self.request, GeneralExpense.objects.all())
        general_per_month = general_expenses.annotate(month=TruncMonth('date')).values('month')\
            .annotate(total=Sum('value')).values('month', 'total').order_by('month')
        general_total = general_expenses.aggregate(Sum('value'))['value__sum'] if general_expenses.exists() else 0
        general_taxes = general_expenses.aggregate(Sum('total_taxes'))['total_taxes__sum'] if general_expenses.exists() else 0
        general_paid_qs = general_expenses.filter(is_paid=True)
        general_paid_total = general_paid_qs.aggregate(Sum('value'))['value__sum'] if general_paid_qs.exists() else 0
        expenses_per_category = general_expenses.values('category__title').annotate(total_pay=Sum('value'),
                                                                                    paid_value=Sum('paid_value'))\
            .order_by('category__title')

        # diffs
        totals = bills_total + payrolls_total + invoices_total + general_total
        paid_totals = bills_paid_total + payrolls_paid_total + payments_total + general_paid_total
        total_taxes = bills_taxes + general_taxes + general_taxes + invoices_taxes
        taxes_diff = income_taxes - total_taxes
        income_expenses_diff = income_value - payrolls_total - bills_total - general_total - invoices_total
        income_expenses_diff_paid = paid_incomes - payments_total - payrolls_paid_total - bills_paid_total - general_paid_total

        # chart analysis
        months = sort_months([incomes_per_month, invoices_per_month, payroll_per_month, bills_per_month, general_per_month])

        result_per_months = []
        for month in months:
            data = {
                'month': month,
                'total': 0
            }
            for ele in incomes_per_month:
                if ele['month'] == month:
                    data['income'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in invoices_per_month:
                if ele['month'] == month:
                    data['invoice'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in bills_per_month:
                if ele['month'] == month:
                    data['bills'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in payroll_per_month:
                if ele['month'] == month:
                    data['payroll'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            for ele in general_per_month:
                if ele['month'] == month:
                    data['generic'] = ele['total']
                    data['total'] = data['total'] + ele['total']
            data['invoice'] = data['invoice'] if 'invoice' in data.keys() else 0
            data['bills'] = data['bills'] if 'bills' in data.keys() else 0
            data['payroll'] = data['payroll'] if 'payroll' in data.keys() else 0
            data['generic'] = data['generic'] if 'generic' in data.keys() else 0
            result_per_months.append(data)

        context.update(locals())
        return context


@method_decorator(staff_member_required, name='dispatch')
class LogisticRowView(TemplateView):
    template_name = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[""] = ''
        return context


@method_decorator(staff_member_required, name='dispatch')
class StoreInventoryView(TemplateView):
    model = Product
    template_name = 'analysis/store_inventory.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.all()
        vendor_products = ProductVendor.objects.all()
        products_total = products.aggregate(total=Sum(F('price_buy')*F('qty'), output_field=FloatField()))\
            if products.exists() else 0
        vendor_products = vendor_products.values('taxes_modifier').annotate(total=Sum(F('product__qty')*F('product__price_buy'), output_field=FloatField())).values('taxes_modifier', 'total').order_by('taxes_modifier')
        context.update(locals())
        return context