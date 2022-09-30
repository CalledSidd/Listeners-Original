from django.contrib import admin
from . models import Cart,CartItem, Coupon, Usedcoupon

# Register your models here.

class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity','is_active' )


admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Coupon)
admin.site.register(Usedcoupon)