import django_tables2 as tables
from .models import Income, Costumer


class IncomeTable(tables.Table):
    action = tables.TemplateColumn('''
                                     <div class="btn-group dropright">
                                        <a href='{{ record.get_edit_url }}' class="btn btn-primary"><i class='fa fa-edit'> </i></a>
                                        <button type="button" class="btn btn-secondary dropdown-toggle dropdown-toggle-split" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                                            <span class="sr-only">Toggle Dropright</span>
                                        </button>
                                            <div class="dropdown-menu">
                                                <a class="dropdown-item" href="">---</a>    
                                            </div>
                                        </div>
                                        ''', verbose_name='Eπεξεργασια', orderable=False)

    class Meta:
        model = Income
        template_name = 'django_tables2/bootstrap.html'
        fields = ['date_expired','title', 'costumer', 'total_value', 'action']


class CostumerTable(tables.Table):
    action = tables.TemplateColumn('''
                                         <div class="btn-group dropright">
                                            <a href='{{ record.get_edit_url }}' class="btn btn-primary"><i class='fa fa-edit'> </i></a>
                                            
                                            </div>
                                            ''', verbose_name='Eπεξεργασια', orderable=False)
    tag_balance = tables.Column(verbose_name='ΥΠΟΛΟΙΠΟ', orderable=False)

    class Meta:
        model = Costumer
        template_name = 'django_tables2/bootstrap.html'
        fields = ['title', 'afm', 'cellphone', 'phone', 'tag_balance', 'action']