import django_tables2 as tables

from .models import GeneralExpenseCategory, GeneralExpense


class GeneralExpenseInfoTable(tables.Table):

    class Meta:
        model = GeneralExpense


class GeneralExpenseTable(tables.Table):
    action = tables.TemplateColumn('''
                                         <div class="btn-group dropright">
                                            <a href='{{ record.get_edit_url }}' class="btn btn-primary"><i class='fa fa-edit'> </i></a>
                                           
                                            </div>
                                            ''', verbose_name='Eπεξεργασια', orderable=False)

    tag_value = tables.Column(orderable=False, verbose_name='Αξια')

    class Meta:
        model = GeneralExpense
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date', 'title', 'category', 'is_paid', 'tag_value']


class GeneralExpenseCategoryTable(tables.Table):
    action = tables.TemplateColumn('''
                                    <div class="btn-group dropright">
                                        <a href='{{ record.get_edit_url }}' class="btn btn-primary"><i class='fa fa-edit'> </i></a>  
                                    </div>
                                    ''', verbose_name='Eπεξεργασια', orderable=False)
    card = tables.TemplateColumn(
        '''
            <div class="btn-group dropright">
                <a href='{{ record.get_card_url }}' class="btn btn-primary"><i class='fa fa-eye'> </i></a>  
            </div>
        ''', verbose_name='ΚΑΡΤΕΛΑ', orderable=False
    )

    class Meta:
        model = GeneralExpenseCategory
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title']


class GeneralExpenseTableFromCategory(tables.Table):
    action = tables.TemplateColumn('''
                                         <div class="btn-group dropright">
                                            <a href='{{ record.get_edit_category_url }}' class="btn btn-primary"><i class='fa fa-edit'> </i></a>

                                            </div>
                                            ''', verbose_name='Eπεξεργασια', orderable=False)

    tag_value = tables.Column(orderable=False, verbose_name='Αξια')

    class Meta:
        model = GeneralExpense
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date', 'title', 'category', 'is_paid', 'tag_value']