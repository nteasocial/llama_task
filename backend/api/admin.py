from django.contrib import admin
from .models import CryptoCurrency


@admin.register(CryptoCurrency)
class CryptoCurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'defillama_id', 'price', 'last_updated')
    search_fields = ('name', 'symbol', 'defillama_id')
    list_filter = ('last_updated',)
