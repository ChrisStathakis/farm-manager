from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import GeneralExpense

@receiver(post_delete, sender=GeneralExpense)
def update_category_on_delete(sender, instance, **kwargs):
    instance.category.save()