from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import ForeignKey
from django.utils import timezone


from django.db.models import Count, Sum, F

from phonenumber_field.modelfields import PhoneNumberField
from decimal import Decimal


class Location(models.Model):

    address = models.CharField('Адрес локации', max_length=200, unique=True)
    lat = models.FloatField('Широта', null=True)
    lon = models.FloatField('Долгота', null=True)
    updated_at = models.DateTimeField('Дата актуализации', default=timezone.now, db_index=True)

    class Meta:
        verbose_name = 'Локация'
        verbose_name_plural = 'Локации'

    def __str__(self):
        return self.address

    def is_expired(self):
        return (timezone.now() - self.updated_at).days > 180
