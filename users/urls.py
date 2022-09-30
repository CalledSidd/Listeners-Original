from django.urls import path
from . import views

urlpatterns = [
    path('add_to_wishlist/<int:id>',views.add_wishlist, name='add_to_wishlist'),
    path('',views.view_wishlist,name='wishlist'),
    path('remove_from_wishlist/<int:id>',views.remove_wishlist,name='remove_from_wishlist')
]