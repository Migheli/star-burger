from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from itertools import chain

from foodcartapp.models import Product, Restaurant, OrderData, RestaurantMenuItem
import requests


from star_burger.settings import YANDEX_GEOCODER_KEY

class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": YANDEX_GEOCODER_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    order_items = list(OrderData.objects.prefetch_related('products'))
    menu_items = list(RestaurantMenuItem.objects.all())
    orders_with_allowed_restaurants = []

    for order_item in order_items:
        if order_item.restaurant:
            print(f'Адрес Ресторана - {order_item.restaurant.address}')
            print(f'Результат работы функции определения координат - {fetch_coordinates(order_item.restaurant.address)}')
        print(f'статус = {order_item.status} ресторан = {order_item.restaurant}')
        if order_item.status == 'Принят' and order_item.restaurant:
            print(f'статус = {order_item.status} ресторан = {order_item.restaurant}')
            OrderData.objects.filter(pk=order_item.id).update(status='Готовится')
            order_item.status = 'Готовится'

        restaurants_with_product_availability= []
        for order_product in order_item.products.all():
            product = order_product.product
            menu_items = list(RestaurantMenuItem.objects.filter(product_id=product.id, availability=True))
            restaurant_with_available_product = [menu_item.restaurant for menu_item in menu_items]
            restaurants_with_product_availability.append(restaurant_with_available_product)

        restaurants_with_available_products = set(chain.from_iterable(restaurants_with_product_availability))
        allowed_restaurants = set()
        for restaurant_with_available_products in restaurants_with_available_products:
            if all(restaurant for restaurant in restaurants_with_product_availability):
                allowed_restaurants.add(restaurant_with_available_products)

        orders_with_allowed_restaurants.append((order_item, allowed_restaurants))

    print(orders_with_allowed_restaurants)
    return render(request, template_name='order_items.html', context={
        'orders_with_allowed_restaurants': orders_with_allowed_restaurants,
        #'menu_items': RestaurantMenuItem.objects.all(),
        #'allowed_restaurants': allowed_restaurants,
        #'rest_dict': rest_dict
    })
