from django.db import migrations

def update_sale_total_amounts(apps, schema_editor):
    Sale = apps.get_model('sales', 'Sale')
    for sale in Sale.objects.all():
        sale.total_amount = sale.item.cost * sale.quantity
        sale.save()

class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_sale_total_amount'),  
    ]

    operations = [
        migrations.RunPython(update_sale_total_amounts),
    ]