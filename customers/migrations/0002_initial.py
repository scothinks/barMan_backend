# Generated by Django 4.2.13 on 2024-07-04 00:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sales', '0001_initial'),
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customertab',
            name='sale',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sales.sale'),
        ),
    ]
