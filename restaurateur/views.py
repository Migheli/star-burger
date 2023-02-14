from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, OrderData, RestaurantMenuItem
from geodata.models import Location
import requests

from django.conf import settings
from geopy import distance as dist

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
        'poducts_with_restaurant_availability': products_with_restaurant_availability,
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
        "apikey": settings.YANDEX_GEOCODER_KEY,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if found_places:
        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        return lon, lat


def get_coordinates(locations, address):
    lon, lat = None, None
    is_expired = True

    if locations.get(address):
        lon, lat, is_expired = locations.get(address)

    if all([not is_expired, lon, lat]):
        return lon, lat

    else:
        try:
            coordinates = fetch_coordinates(address)
            if coordinates:
                lon, lat = coordinates
                Location.objects.update_or_create(address=address, lon=lon, lat=lat)
                return lon, lat
        except RequestException:
            return None


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = OrderData.objects.prefetch_related('order_product')
    menu_items = RestaurantMenuItem.objects.all()
    restaurants = Restaurant.objects.all()
    required_addresses = [order.address for order in orders] + [restaurant.address for restaurant in restaurants]
    locations = Location.objects.filter(address__in=required_addresses)

    menu_items_availability = {(menu_item.product_id, menu_item.restaurant_id) : menu_item.availability
    for menu_item in menu_items}

    orders_with_allowed_restaurants = []
    for order in orders:

        if order.status == 'Принят' and order.cooking_restaurant:
            OrderData.objects.filter(pk=order.id).update(status='Готовится')
            order.status = 'Готовится'

        restaurants_with_product_availability = [
            restaurant for order_product in order.order_product.all()
            for restaurant in restaurants if menu_items_availability.get((order_product.product_id, restaurant.id))
        ]

        allowed_restaurants = set([restaurant for restaurant in restaurants_with_product_availability
                                   if restaurants_with_product_availability.count(restaurant) == order.order_product.count()]) # если количество вхождений ресторана в список равно количеству элементов заказа, добавляем ресторан в неповторяющийся сет искомых ресторанов

        preloaded_locations = {location.address : (location.lon, location.lat, location.is_expired()) for location in locations}
        restaurants_with_distances = []

        for allowed_restaurant in allowed_restaurants:
            customer_coordinates = get_coordinates(preloaded_locations, order.address)
            restaurant_coordinates = get_coordinates(preloaded_locations, allowed_restaurant.address)

            if customer_coordinates and restaurant_coordinates:
                distance_to_customer = round(dist.distance(customer_coordinates, restaurant_coordinates).km, 2)
            else:
                distance_to_customer = -1   # отрицательное значение переменной является индикатором того, что дистанцию вычислить не удалось и произошла ошибка
            restaurants_with_distances.append((allowed_restaurant, distance_to_customer))

        sorted_restaurants_with_distances = sorted(restaurants_with_distances, key=lambda distance: distance[1])

        orders_with_allowed_restaurants.append((order, sorted_restaurants_with_distances))

    return render(request, template_name='order_items.html', context={
        'orders_with_allowed_restaurants': orders_with_allowed_restaurants,
    })
