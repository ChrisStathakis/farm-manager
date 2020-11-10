from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.conf import settings
import uuid

CURRENCY = settings.CURRENCY
TAXES_CHOICES = (
    ('a', 0),
    ('b', 13),
    ('c', 24)
)


from frontend.models import PaymentMethod


class DefaultOrderModel(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='Friendly ID')
    title = models.CharField(max_length=150, verbose_name='Τίτλος')
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True, verbose_name='Σημειώσεις')
    payment_method = models.ForeignKey(PaymentMethod,
                                       null=True,
                                       on_delete=models.PROTECT,
                                       verbose_name='Τρόπος Πληρωμής')
    date_expired = models.DateField(default=timezone.now, verbose_name='Ημερομηνία')
    taxes_modifier = models.CharField(max_length=1, choices=TAXES_CHOICES, verbose_name='a')
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Αξία')
    clean_value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='ΚΑΘΑΡΗ ΑΞΙΑ')
    total_taxes = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Φόροι')
    paid_value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Πληρωτέο Ποσό')
    final_value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Τελική Αξίσ')
    discount = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Επιπλέον Έκπτωση')
    is_paid = models.BooleanField(default=False, verbose_name='Πληρωμένο?')
    printed = models.BooleanField(default=False, verbose_name='Εκτυπωμένο')
    objects = models.Manager()

    def save(self, *args, **kwargs):
        self.final_value = self.value - self.discount
        self.total_taxes = self.final_value * self.get_taxes_modifier_display()/100
        self.clean_value = self.final_value - self.total_taxes
        if self.is_paid:
            self.paid_value = self.final_value
        super(DefaultOrderModel, self).save(*args, **kwargs)

    class Meta:
        abstract = True

    def tag_is_paid(self):
        return 'Is Paid' if self.is_paid else 'Not Paid'

    def tag_value(self):
        return f'{self.value} {CURRENCY}'
    tag_value.short_description = 'Αρχική Αξία'

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'
    tag_final_value.short_description = 'Αξία'

    def tag_paid_value(self):
        return f'{self.paid_value} {CURRENCY}'

    def get_remaining_value(self):
        return self.final_value - self.paid_value

    def tag_payment_method(self):
        return f'{self.payment_method} {CURRENCY}'


class DefaultBasicModel(models.Model):
    active = models.BooleanField(default=True, verbose_name='Κατάσταση')
    title = models.CharField(max_length=255, verbose_name='Ονομασία')
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    user_account = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    costum_ordering = models.IntegerField(default=1)

    class Meta:
        abstract = True


class DefaultOrderItemModel(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True, verbose_name='Ημερομηνία Τελευταίας Επεξεργασίας')
    qty = models.PositiveIntegerField(default=1, verbose_name='Ποσότητα')
    value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Άρχικη Αξία')
    discount_value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Ποσοστό Έκτωσης')
    final_value = models.DecimalField(decimal_places=2, max_digits=20, default=0, verbose_name='Αξία')

    class Meta:
        abstract = True

    def tag_final_value(self):
        return f'{self.final_value} {CURRENCY}'
    tag_final_value.short_description = 'Αξία'

    def tag_value(self):
        return f'{self.value} {CURRENCY}'
    tag_value.short_description = 'Αρχική Αξία'


PAYROLL_CHOICES = (
    ('1', 'Μισθός'),
    ('2', 'ΙΚΑ'),
    ('3', 'ΑΣΦΑΛΙΣΤΙΚΕΣ ΕΙΣΦΟΡΕΣ'),
    ('4', 'ΗΜΕΡΟΜΗΣΘΙΟ'),
    ('5', 'ΕΡΓΟΣΗΜΟ'),
    ('6', 'ΔΩΡΟ')
    )