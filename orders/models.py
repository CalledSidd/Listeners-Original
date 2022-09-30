from django.db import models
from accounts.models import Account
from users.models import Products
from accounts.models import Address

# Create your models here.
class Payment(models.Model):
    user            = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    payment_id      = models.CharField(max_length=100, null=True)
    payment_method  = models.CharField(max_length=100)
    amount_paid     = models.CharField(max_length=100)
    status          = models.CharField(max_length=100)
    created_at      = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.payment_method

# New Orders Model because the previous one was not properly working 
class Orders(models.Model):
    STATUS = (
        ('Processing','Processing'),
        ('Confirmed', 'Confirmed'),
        ('Accepted', 'Accepted'),
        ('Out For Delivery', 'Out For Delivery'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user        = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    payment     = models.ForeignKey(Payment, on_delete=models.CASCADE, blank=True, null=True)
    address     = models.ForeignKey(Address, on_delete=models.CASCADE, null=True)
    order_total = models.FloatField(max_length=50, null=True)
    order_id    = models.CharField(max_length=50, null=True)
    date        = models.DateField(auto_now_add=True)
    status      = models.CharField(max_length=30, choices=STATUS, default='Confirmed')
    is_ordered  = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name
    

class OrderProduct(models.Model):
    STATUS = (
        ('Processing','Processing'),
        ('Confirmed', 'Confirmed'),
        ('Accepted', 'Accepted'),
        ('Out For Delivery', 'Out For Delivery'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Return Pending','Return Pending' ),
        ('Return Accepted', 'Return Accepted'),
        ('Returned', 'Returned'),
    )
    order         = models.ForeignKey(Orders, on_delete=models.CASCADE, null=True)
    payment       = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user          = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product       = models.ForeignKey(Products, on_delete=models.CASCADE, null=True)
    status        = models.CharField(max_length=30, choices=STATUS, default='Confirmed', null=True)
    quantity      = models.IntegerField(null=True)
    product_price = models.FloatField(null=True)
    ordered       = models.BooleanField(default=False, null=True)
    created_at    = models.DateTimeField(auto_now_add=True,null=True)
    updated_at    = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.product.product_name