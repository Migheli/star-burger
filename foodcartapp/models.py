from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from django.db.models import Sum, F

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def get_order_sum(self):
        return self.annotate(order_sum=Sum(F('order_products__price') * F('order_products__quantity')))

class Order(models.Model):
    ORDER_STATUSES = [('Принят', 'Принят'), ('Готовится', 'Готовится'),
                      ('Доставка', 'Доставка'), ('Выполнен', 'Выполнен')]

    firstname = models.CharField('Имя', max_length=50, db_index=True)
    lastname = models.CharField('Фамилия', max_length=50, db_index=True)
    phonenumber = PhoneNumberField('Телефон', db_index=True)
    address = models.CharField('Адрес', max_length=250, db_index=True)
    payment_type = models.CharField(
        'Способ оплаты',
        max_length=25,
        null=True,
        blank=True,
        choices=[('Наличными', 'Наличными'), ('Электронно', 'Электронно')],
        default=None,
        db_index=True
    )
    comment = models.TextField('Комментарий', blank=True)
    registered_at = models.DateTimeField('Дата создания', default=timezone.now, db_index=True)
    called_at = models.DateTimeField('Дата звонка', blank=True, null=True, db_index=True)
    delivered_at = models.DateTimeField('Дата доставки', blank=True, null=True, db_index=True)
    cooking_restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='Какой из ресторанов приготовит',
        related_name='orders',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)

    status = models.CharField(
        'Статус',
        max_length=25,
        choices=ORDER_STATUSES,
        default='Принят',
        db_index=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['called_at']

    def is_in_work(self):
        return self.status != 'Выполнен'


class OrderProducts(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='заказ',
        related_name='order_products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)

    product = models.ForeignKey(
        Product,
        verbose_name='продукт',
        related_name='order_products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL)

    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    quantity = models.IntegerField(validators=[MinValueValidator(1)],
                                   verbose_name='количество'
    )

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
