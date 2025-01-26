from django.contrib import admin
from .models import Product

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display=['id','name','price','cat','pdetails','is_active']
    list_filter=['cat','is_active']

admin.site.register(Product,ProductAdmin)

