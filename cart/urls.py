from django.urls import path
from . import views

urlpatterns = [
    path('',views.cart,name='cart'),
    path('addtocart/<int:id>/',views.addtocart, name='addtocart'),
    path('removefromcart/<int:id>/',views.removefromcart, name='removefromcart'),
    path('removecartitem/<int:id>/',views.removecartitem, name='removecartitem'),
    path('redirect_failed/',views.redirectFailed,name='redirectFailed'),
    path('Coupon_apply/',views.coupon,name='couponApply'),
    path('wishlist/',views.wishlist,name='wishlist'),
    
]