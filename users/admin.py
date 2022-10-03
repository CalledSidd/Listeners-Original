from django.contrib import admin
from . models import Products,OfferProduct,OfferCategory,Banner,Wishlist

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    pass
admin.site.register(Products)
admin.site.register(OfferProduct)
admin.site.register(OfferCategory)
admin.site.register(Banner)
admin.site.register(Wishlist)