from django.http import JsonResponse
from django.templatetags.static import static
import json
import phonenumbers

from rest_framework.decorators import api_view

from .models import Product, OrderProducts, OrderData
from rest_framework.response import Response
from rest_framework import status

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ListField


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


class ProductSerializer(ModelSerializer):
    class Meta:
        model = OrderProducts
        fields = ['product', 'quantity']




class ApplicationSerializer(ModelSerializer):
    #products = ListField(
    #    child=ProductSerializer(many=False)
    #)
    products = ProductSerializer(many=True, allow_empty=False)
    class Meta:
        model = OrderData
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']



@api_view(['POST'])
def register_order(request):
    data = request.data

    serializer = ApplicationSerializer(data=data)
    serializer.is_valid(raise_exception=True)  # выкинет ValidationError

    print(data)
    order = OrderData.objects.create(
        firstname=data['firstname'],
        lastname=data['lastname'],
        phonenumber=data['phonenumber'],
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
