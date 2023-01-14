# Generated by Django 3.2.15 on 2023-01-14 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0044_orderproducts_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdata',
            name='status',
            field=models.CharField(choices=[('Принят', 'Принят'), ('Готовится', 'Готовится'), ('Доставка', 'Доставка'), ('Выполнен', 'Выполнен')], db_index=True, default='Принят', max_length=25),
        ),
    ]