from django.urls import path
from .views import (
    IncomeListView, InvoiceCreateView, IncomeUpdateView, income_delete_view,
    CostumerListView, CostumerCreateView, CostumerUpdateView, costumer_delete_view
                    )

from .action_views import (
    validate_payment_creation_view, update_or_delete_payment_from_costumer_view,
    update_or_delete_income_view

)

app_name = 'incomes'

urlpatterns = [
    path('list/', IncomeListView.as_view(), name='list'),
    path('create/', InvoiceCreateView.as_view(), name='create'),
    path('update/<int:pk>/', IncomeUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', income_delete_view, name='delete'),

    path('costumer/list/', CostumerListView.as_view(), name='costumer_list'),
    path('costumers/create/', CostumerCreateView.as_view(), name='costumer_create'),
    path('costumers/update/<int:pk>/', CostumerUpdateView.as_view(), name='costumers_update'),
    path('costumers/delete/<int:pk>', costumer_delete_view, name='costumers_delete'),

    path('action/validate-payment-creation/<int:pk>/', validate_payment_creation_view, name='validate_payment_creation'),
    path('action/update-or-delete-payment-view/<int:pk>/<slug:type_>/', update_or_delete_payment_from_costumer_view,
         name='update_or_delete_payment_view'),
    path('action/validate-income/<int:pk>/<slug:type_>/', update_or_delete_income_view, name='update_or_delete_income_view')



   
]
