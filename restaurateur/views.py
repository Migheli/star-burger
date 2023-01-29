from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from itertools import chain

from foodcartapp.models import Product, Restaurant, OrderData, RestaurantMenuItem
from geodata.models import Location
import requests

from star_burger.settings import YANDEX_GEOCODER_KEY
from geopy import distance as dist
from django.utils import timezone

from requests.exceptions import RequestException

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



def get_address_coordinates(locations, address):

    location, created = locations.get_or_create(
        address=address,
        defaults={'lon': None, 'lat': None}
    )

    if any([created, location.is_expired(), location.is_blank()]):
        try:
            location.lon, location.lat = fetch_coordinates(address)
        except RequestException:
            location.lon, location.lat = None, None

    return location.lon, location.lat


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    order_items = list(OrderData.objects.prefetch_related('products'))
    orders_with_allowed_restaurants = []
    locations = Location.objects.all()

    for order_item in order_items:

        if order_item.status == 'Принят' and order_item.restaurant:
            OrderData.objects.filter(pk=order_item.id).update(status='Готовится')
            order_item.status = 'Готовится'

        restaurants_with_product_availability= [] # находим все рестораны с доступным нужным нам продуктом
        for order_product in order_item.products.all():
            product = order_product.product
            menu_items = list(RestaurantMenuItem.objects.filter(product_id=product.id, availability=True))
            restaurant_with_available_product = [menu_item.restaurant for menu_item in menu_items]

            restaurants_with_product_availability.append(restaurant_with_available_product)


        restaurants_with_available_products = set(chain.from_iterable(restaurants_with_product_availability)) # делаем из рестранов - сет без дублирующих

        allowed_restaurants = set()

        for restaurant in restaurants_with_available_products:
            if list(chain.from_iterable(restaurants_with_product_availability)).count(restaurant) == order_item.products.count():
                allowed_restaurants.add(restaurant)

        allowed_restaurants_with_distance = []

        for allowed_restaurant in allowed_restaurants:
            allowed_restaurant_coordinates = []
            customer_coordinates = []
            customer_coordinates = get_address_coordinates(locations, order_item.address)
            allowed_restaurant_coordinates = get_address_coordinates(locations, allowed_restaurant.address)

            if None in customer_coordinates or None in allowed_restaurant_coordinates:
                distance_to_customer = -1
            else:
                distance_to_customer = round(dist.distance(customer_coordinates, allowed_restaurant_coordinates).km, 2)

            allowed_restaurants_with_distance.append((allowed_restaurant, distance_to_customer))

        print(f'РЕСТОРАНЫ С ДИСТАНЦИЯМИ ДО НИХ --- {allowed_restaurants_with_distance}')

        sorted_allowed_restaurants_with_distance = sorted(allowed_restaurants_with_distance, key=lambda distance: distance[1])

        new_sorted_allowed_restaurants_with_distance = []
        for restaurant, distance in sorted_allowed_restaurants_with_distance:
            if distance < 0:
               distance = 'Ошибка определения координат - расстояние неизвестно'
            new_sorted_allowed_restaurants_with_distance.append((restaurant, distance))

        orders_with_allowed_restaurants.append((order_item, new_sorted_allowed_restaurants_with_distance))

    return render(request, template_name='order_items.html', context={
        'orders_with_allowed_restaurants': orders_with_allowed_restaurants,
    })
