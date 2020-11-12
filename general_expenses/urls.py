from django.urls import path

from .views import (GenericExpensesListView, GeneralExpenseCreateView, GeneralExpenseUpdateView, delete_generic_expense_view,
                    GenericExpensesCategoryListView, GeneralExpenseCategoryUpdateView, GeneralExpenseCategoryCreateView, delete_generic_category_expense_view,
                    pay_expense_view, GeneralExpenseCardView, GeneralExpenseUpdateFromDetailView
                    )

from .ajax_views import ajax_generic_expense_modal_view
from .action_views import validate_generic_expense_create_view


app_name = 'generic_expenses'

urlpatterns = [
    path('list/', GenericExpensesListView.as_view(), name='list'),
    path('update/<int:pk>/', GeneralExpenseUpdateView.as_view(), name='update'),
    path('delete/<int:pk>/', delete_generic_expense_view, name='delete'),
    path('create/', GeneralExpenseCreateView.as_view(), name='create'),
    path('pay/<int:pk>/', pay_expense_view, name='pay_expense'),
    path('card/<int:pk>/', GeneralExpenseCardView.as_view(), name='card'),
    path('card-update-invoice/<int:pk>/', GeneralExpenseUpdateFromDetailView.as_view(), name='update_invoice_from_card'),

    path('category/list/', GenericExpensesCategoryListView.as_view(), name='category_list'),
    path('category/update/<int:pk>/', GeneralExpenseCategoryUpdateView.as_view(), name='category_update'),
    path('category/delete/<int:pk>/', delete_generic_category_expense_view, name='category_delete'),
    path('category/create/', GeneralExpenseCategoryCreateView.as_view(), name='category_create'),


    path('ajax/create/<int:pk>/', ajax_generic_expense_modal_view, name='ajax_expense_category_modal'),
    path('validate-create/expense/<int:pk>/', validate_generic_expense_create_view, name='validate_expense_creation'),

]
