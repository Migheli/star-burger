# Generated by Django 3.2.15 on 2023-01-21 05:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0050_orderdata_payment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdata',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='foodcartapp.restaurant', verbose_name='Какой из ресторанов приготовит'),
        ),
    ]
