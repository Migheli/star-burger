from django.contrib import admin
from django.shortcuts import reverse
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme


from .models import Location

from django.shortcuts import redirect
from star_burger.settings import ALLOWED_HOSTS
from django.utils.encoding import iri_to_uri




@admin.register(Location)
class RestaurantAdmin(admin.ModelAdmin):

    search_fields = [
        'address',
        'lon',
        'lat',
    ]

