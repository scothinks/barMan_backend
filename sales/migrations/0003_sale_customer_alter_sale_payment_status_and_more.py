# Generated by Django 4.2.13 on 2024-07-06 14:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0002_initial'),
        ('sales', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sale',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='customers.customer'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='payment_status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('DONE', 'Done')], default='PENDING', max_length=10),
        ),
        migrations.AlterField(
            model_name='sale',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
    ]
