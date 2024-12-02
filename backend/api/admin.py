from django.contrib import admin
from .models import CryptoCurrency


@admin.register(CryptoCurrency)
class CryptoCurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'price', 'last_updated')
    search_fields = ('name', 'symbol')
    readonly_fields = ('last_updated',)
