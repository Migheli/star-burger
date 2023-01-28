# Generated by Django 3.2.15 on 2023-01-28 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_orderdata_restaurant'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderdata',
            options={'ordering': ['called_at'], 'verbose_name': 'Заказ', 'verbose_name_plural': 'Заказы'},
        ),
        migrations.AlterField(
            model_name='orderdata',
            name='status',
            field=models.CharField(choices=[('Принят', 'Принят'), ('Принят', 'Принят'), ('Доставка', 'Доставка'), ('Выполнен', 'Выполнен')], db_index=True, default='Принят', max_length=25, verbose_name='Статус'),
        ),
    ]
