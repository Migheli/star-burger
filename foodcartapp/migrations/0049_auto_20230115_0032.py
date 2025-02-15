# Generated by Django 3.2.15 on 2023-01-14 21:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20230115_0030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdata',
            name='called_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата звонка'),
        ),
        migrations.AlterField(
            model_name='orderdata',
            name='delivered_at',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата доставки'),
        ),
    ]
