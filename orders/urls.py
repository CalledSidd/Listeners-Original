from django.urls import path
from . import views

urlpatterns = [
    path('placecod/',views.paycod,name='cod'),
    path('checkout/',views.checkout, name='checkout'), 
    path('addaddress',views.addaddress,name='addaddress'),
    path('paypal/',views.paypal,name='paypal'),
    path('payment_failed/',views.cancelled,name='payment_cancelled'),
    path('payment_succesful/',views.paypalpaymentDone,name='payment_done'),
    path('razorpay_successful/',views.RazorPaySuccess,name='razorpaysuccess'),
    
]