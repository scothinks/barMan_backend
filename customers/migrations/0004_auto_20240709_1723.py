from django.db import migrations

def deduplicate_tabs(apps, schema_editor):
    CustomerTab = apps.get_model('customers', 'CustomerTab')
    Customer = apps.get_model('customers', 'Customer')
    for customer in Customer.objects.all():
        tabs = CustomerTab.objects.filter(customer=customer)
        if tabs.count() > 1:
            first_tab = tabs.first()
            tabs.exclude(pk=first_tab.pk).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0003_remove_customertab_sale_customertab_created_at_and_more'),  
    ]

    operations = [
        migrations.RunPython(deduplicate_tabs),
    ]