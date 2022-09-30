from django.contrib import admin
from . models import *

# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id',  'is_ordered' , 'user']
    list_filter  = ['status', 'is_ordered']
    list_per_page= 30   



admin.site.register(Payment) 
admin.site.register(Orders, OrderAdmin)
admin.site.register(OrderProduct)