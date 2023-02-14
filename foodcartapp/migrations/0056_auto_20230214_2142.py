# Generated by Django 3.2.15 on 2023-02-14 18:42

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0055_rename_restaurant_orderdata_cooking_restaurant'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(db_index=True, max_length=50, verbose_name='Имя')),
                ('lastname', models.CharField(db_index=True, max_length=50, verbose_name='Фамилия')),
                ('phonenumber', phonenumber_field.modelfields.PhoneNumberField(db_index=True, max_length=128, region=None, verbose_name='Телефон')),
                ('address', models.CharField(db_index=True, max_length=250, verbose_name='Адрес')),
                ('payment_type', models.CharField(choices=[('Наличными', 'Наличными'), ('Электронно', 'Электронно')], db_index=True, default='Электронно', max_length=25, verbose_name='Способ оплаты')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('registered_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='Дата создания')),
                ('called_at', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата звонка')),
                ('delivered_at', models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='Дата доставки')),
                ('status', models.CharField(choices=[('Принят', 'Принят'), ('Готовится', 'Готовится'), ('Доставка', 'Доставка'), ('Выполнен', 'Выполнен')], db_index=True, default='Принят', max_length=25, verbose_name='Статус')),
                ('cooking_restaurant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='foodcartapp.restaurant', verbose_name='Какой из ресторанов приготовит')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
                'ordering': ['called_at'],
            },
        ),
        migrations.AlterField(
            model_name='orderproducts',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_product', to='foodcartapp.order', verbose_name='заказ'),
        ),
        migrations.DeleteModel(
            name='OrderData',
        ),
    ]
