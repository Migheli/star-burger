# Generated by Django 3.2.15 on 2022-11-09 19:18

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0041_auto_20221106_1316'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='orderproducts',
            managers=[
                ('element_data', django.db.models.manager.Manager()),
            ],
        ),
    ]