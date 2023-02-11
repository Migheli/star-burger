from django.contrib import admin
from .models import Location


@admin.register(Location)
class RestaurantAdmin(admin.ModelAdmin):

    search_fields = [
        'address',
        'lon',
        'lat',
    ]
