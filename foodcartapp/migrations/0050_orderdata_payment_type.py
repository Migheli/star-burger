# Generated by Django 3.2.15 on 2023-01-14 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0049_auto_20230115_0032'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdata',
            name='payment_type',
            field=models.CharField(choices=[('Наличными', 'Наличными'), ('Электронно', 'Электронно')], db_index=True, default='Наличными', max_length=25, verbose_name='Способ оплаты'),
        ),
    ]
