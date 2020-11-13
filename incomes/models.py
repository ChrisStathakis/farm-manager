from django.db import models
from django.shortcuts import reverse
from django.db.models import Sum, Q
from django.db.models.signals import post_delete
from django.conf import settings
from django.dispatch import receiver
from vendors.models import TAXES_CHOICES
from django.utils import timezone

from tinymce.models import HTMLField
from decimal import Decimal

from frontend.tools import initial_date
from frontend.models import PaymentMethod


CURRENCY = settings.CURRENCY


class Costumer(models.Model):
    title = models.CharField(null=True, max_length=240, verbose_name='Επωνυμια')
    afm = models.CharField(blank=True, null=True, max_length=10, verbose_name='ΑΦΜ')
    doy = models.CharField(blank=True, null=True, max_length=240, default='Σπαρτη', verbose_name='ΔΟΥ')
    notes = models.CharField(max_length=200, blank=True, verbose_name='Σημειώσεις')
    cellphone = models.CharField(max_length=20, blank=True, verbose_name='Κινητό')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Τηλέφωνο')
    active = models.BooleanField(default=True, verbose_name='Ενεργός')
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    paid_value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)
    balance = models.DecimalField(decimal_places=2, max_digits=20, default=0.00)

    class Meta:
        ordering = ['title', 'afm']

    def save(self, *args, **kwargs):
        incomes = self.incomes.all()
        payments = self.payments.all()
        self.value = incomes.aggregate(Sum('total_value'))['total_value__sum'] if incomes.exists() else 0
        self.paid_value = payments.aggregate(Sum('value'))['value__sum'] if payments.exists() else 0
        self.balance = self.value - self.paid_value
        super(Costumer, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def tag_balance(self):
        return f'{self.balance} {CURRENCY}'

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    def tag_paid_value(self):
        return f'{self.paid_value} {CURRENCY}'

    def phones(self):
        return f'{self.cellphone} {self.phone}'

    def get_edit_url(self):
        return reverse('incomes:costumers_update', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, queryset):
        q = request.GET.get('q', None)
        balance_name = request.GET.get('balance_name', None)
        status_name = request.GET.get('active_name', None)
        queryset = queryset.filter(active=True) if status_name else queryset
        queryset = queryset.filter(balance__gt=Decimal('0.00')) if balance_name else queryset
        queryset = queryset.filter(Q(first_name__startswith=q.capitalize()) |
                                   Q(last_name__startswith=q.capitalize()) |
                                   Q(eponimia__icontains=q) |
                                   Q(amka__icontains=q) |
                                   Q(afm__icontains=q) |
                                   Q(cellphone__icontains=q) |
                                   Q(phone__icontains=q)
                                   ).distinct() if q else queryset
        return queryset


class CostumerPayment(models.Model):
    is_paid = models.BooleanField(default=True, verbose_name='Πληρωμενο')
    timestamp = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Costumer, on_delete=models.CASCADE, related_name='payments', verbose_name='Πελάτης')
    payment_method = models.ForeignKey(PaymentMethod, null=True, on_delete=models.SET_NULL, verbose_name='Επιταγη')
    date = models.DateField(verbose_name='Ημερομηνία')
    title = models.CharField(max_length=200, blank=True, verbose_name='Τίτλος')
    description = models.TextField(blank=True, verbose_name='Περιγραφή')
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0.00, verbose_name='Ποσό')

    class Meta:
        ordering = ['-date']

    def tag_order_type(self):
        return 'Πληρωμή'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.id:
            self.title = f'Πληρωμή {self.id}' if len(self.title) == 0 else self.title
        super().save(*args, **kwargs)
        self.customer.save()

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    def tag_final_value(self):
        return self.tag_value()

    def get_edit_url(self):
        return reverse('costumers:payment_update', kwargs={'pk': self.id})

    def get_edit_costumer_url(self):
        return reverse('edit_payment_from_costumer', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('costumers:payment_delete', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, qs):
        q = request.GET.get('q', None)
        paid_name = request.GET.getlist('paid_name', None)
        date_start, date_end, date_range = initial_date(request, months=12)
        if q:
            qs = qs.filter(Q(customer__first_name__icontains=q) |
                           Q(customer__last_name__icontains=q) |
                           Q(customer__amka__icontains=q) |
                           Q(customer__cellphone__icontains=q) |
                           Q(customer__phone__icontains=q)
                       ).distinct()
        qs = qs.filter(is_paid=True) if 'have_' in paid_name else qs.filter(is_paid=False) if 'not_' in paid_name else qs
        if date_range:
            qs = qs.filter(date__range=[date_start, date_end])
        return qs


@receiver(post_delete, sender=CostumerPayment)
def update_costumer_payment_value(sender, instance, **kwargs):
    customer = instance.customer
    customer.save()


class Income(models.Model):
    ORDER_TYPE_STATUS = (
        ('a', 'ΤΙΜΟΛΟΓΙΟ'),
        ('b', 'ΑΠΟΔΕΙΞΗ'),
        ('c', 'ΑΛΛΟ')
    )
    payment_method = models.ForeignKey(PaymentMethod, null=True, verbose_name='ΤΡΟΠΟΣ ΠΛΗΡΩΜΗΣ', on_delete=models.SET_NULL)
    costumer = models.ForeignKey(Costumer, on_delete=models.CASCADE, null=True, related_name='incomes', verbose_name='ΠΕΛΑΤΗΣ')
    date_expired = models.DateField(verbose_name='Ημερομηνια')
    title = models.CharField(blank=True, null=True, verbose_name='Σημειωσεις', max_length=240)
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='ΚΑΘΑΡΗ ΑΞΙΑ')
    taxes_modifier = models.CharField(max_length=1, choices=TAXES_CHOICES, default='a')
    taxes = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='ΦΟΡΟΣ')
    order_type = models.CharField(default='a', choices=ORDER_TYPE_STATUS, max_length=1, verbose_name='ΕΙΔΟΣ ΠΑΡΑΣΤΑΤΙΚΟΥ')
    total_value = models.DecimalField(decimal_places=2, max_digits=20, verbose_name='ΑΞΙΑ')

    class Meta:
        ordering = ['-date_expired']

    def __str__(self):
        return f'{self.date_expired}'

    def save(self, *args, **kwargs):
        self.taxes = self.total_value * Decimal(self.get_taxes_modifier_display()/100)
        self.value = self.total_value - self.taxes

        super().save(*args, **kwargs)
        self.costumer.save()

    def tag_value(self):
        return f'{self.value} {CURRENCY}'

    def tag_total_value(self):
        return f'{self.total_value} {CURRENCY}'

    def tag_taxes(self):
        return f'{self.taxes} {CURRENCY}'

    def get_edit_url(self):
        return reverse('incomes:update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('incomes:delete', kwargs={'pk': self.id})

    @staticmethod
    def filters_data(request, qs):
        search_name = request.GET.get('search_name', None)
        date_start, date_end, date_range = initial_date(request, 6)
        qs = qs.filter(notes__icontains=search_name) if search_name else qs
        print(date_start, date_end)
        if date_start and date_end:
            print('her!')
            qs = qs.filter(date_expired__range=[date_start, date_end])
        return qs

