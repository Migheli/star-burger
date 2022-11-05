from django.http import JsonResponse
from django.templatetags.static import static
import json
import phonenumbers

from rest_framework.decorators import api_view

from .models import Product, OrderProducts, OrderData
from rest_framework.response import Response
from rest_framework import status

def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    data = request.data

    if 'firstname' not in data and 'lastname' not in data and 'phonenumber' not in data and 'address' not in data:
        return Response('firstname, lastname, phonenumber, address: Обязательное поле.',
                        status=status.HTTP_400_BAD_REQUEST)

    if 'products' not in data:
        return Response('products: Обязательное поле.',
                        status=status.HTTP_400_BAD_REQUEST)

    if not any([data['firstname'], data['lastname'], data['phonenumber'], data['address']]):
        return Response('firstname, lastname, phonenumber, address: Это поле не может быть пустым.',
                        status=status.HTTP_400_BAD_REQUEST)

    if data['phonenumber'] is "":
        return Response(
            '// phonenumber: Это поле не может быть пустым.',
            status=status.HTTP_400_BAD_REQUEST)

    if not phonenumbers.is_valid_number(phonenumbers.parse(data['phonenumber'], "SG")):
        return Response(
            '// phonenumber: Введен некорректный номер телефона.',
            status=status.HTTP_400_BAD_REQUEST)

    for product in data['products']:
        if product['product'] not in Product.objects.all().values_list('pk', flat=True):
            return Response(
                f'// products: Недопустимый первичный ключ "{product["product"]}',
                status=status.HTTP_400_BAD_REQUEST)

    if isinstance(data['firstname'], list):
        return Response(
            f'// firstname: Not a valid string.',
            status=status.HTTP_400_BAD_REQUEST)


    if data['products'] is None:
        return Response('products: Это поле не может быть пустым.', status=status.HTTP_400_BAD_REQUEST)
    if type(data['products']) == str:
        return Response('products: Ожидался list со значениями, но был получен "str".', status=status.HTTP_400_BAD_REQUEST)
    if len(data['products']) == 0:
        return Response('products: Этот список не может быть пустым.', status=status.HTTP_400_BAD_REQUEST)

    if data['firstname'] is None:
        return Response('// firstname: Это поле не может быть пустым.',
                        status=status.HTTP_400_BAD_REQUEST)



    print(data)
    order = OrderData.objects.create(
        first_name=data['firstname'],
        last_name=data['lastname'],
        phone_number=data['phonenumber'],
        address=data['address'],
    )

    order_elements = []
    for product in data['products']:
        order_element = OrderProducts(
            order=order,
            product=Product.objects.get(id=product['product']),
            quantity=product['quantity']
            )
        order_elements.append(order_element)

    order_elements = OrderProducts.objects.bulk_create(order_elements)

    return JsonResponse({})
