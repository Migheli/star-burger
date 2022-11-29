from django.http import JsonResponse
from django.templatetags.static import static
import json
import phonenumbers

from rest_framework.renderers import JSONRenderer

from rest_framework.decorators import api_view

from .models import Product, OrderProducts, OrderData
from rest_framework.response import Response
from rest_framework import status

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ListField

from django.db import transaction


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


class OrderSerializer(ModelSerializer):

    products = ProductSerializer(many=True, allow_empty=False, write_only=True)
    class Meta:
        model = OrderData
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)  # выкинет ValidationError
    order_validated_data = serializer.validated_data

    print(order_validated_data)
    order = OrderData.objects.create(
        firstname=order_validated_data['firstname'],
        lastname=order_validated_data['lastname'],
        phonenumber=order_validated_data['phonenumber'],
        address=order_validated_data['address'],
    )

    print(order_validated_data['products'][0]['product'].price)

    order_elements = [
        OrderProducts(order=order,
                      product=product['product'],
                      quantity=product['quantity'],
                      price=product['product'].price,
                      )
        for product in order_validated_data['products']
    ]
    OrderProducts.objects.bulk_create(order_elements)

    return Response(OrderSerializer(order).data)
