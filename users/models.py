from django.db import models
from Category . models import Category
import django_extensions
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Account

# Create your models here.
class Products(models.Model):
    product_name   = models.CharField(max_length=200, unique=True)
    slug           = AutoSlugField(populate_from=['product_name'], unique=True)
    description    = models.TextField(max_length=500, blank=True)
    price          = models.IntegerField(validators = [MinValueValidator(0)])
    discount_price = models.IntegerField(validators = [MinValueValidator(0)],null=True,blank=True)
    image1         = models.ImageField(upload_to='photos/Products')
    image2         = models.ImageField(upload_to='photos/Products')
    image3         = models.ImageField(upload_to= 'photos/Products')
    image4         = models.ImageField(upload_to= 'photos/Products')
    stock          = models.IntegerField(validators=[MinValueValidator(0)])
    Is_available   = models.BooleanField(default=True)
    category       = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_date   = models.DateTimeField(auto_now_add=True)
    modified_date  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'products'
        verbose_name_plural = 'products'

    def get_url(self):
        return reverse('product_page',args=[self.category.slug, self.slug])

    def __str__(self):
        return self.product_name


class OfferProduct(models.Model):
    product = models.OneToOneField(Products, related_name='category_offers', on_delete=models.CASCADE)
    discount = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(99)],null=True,default = 0)
    is_active = models.BooleanField(default =True)
    class Meta:
        verbose_name = 'Offer Product'
        verbose_name_plural = 'Offer Products'

    def __str__(self):
        return self.product.product_name

    @property
    def discount_percentage(self):
       return (100 * discount)/product.price


class OfferCategory(models.Model):
    category = models.OneToOneField(Category, related_name='category_offers', on_delete=models.CASCADE)
    discount = models.IntegerField(validators=[MinValueValidator(0),MaxValueValidator(99)],null=True,default = 0)
    is_active = models.BooleanField(default =True)
    class Meta:
        verbose_name = 'OfferCategory'
        verbose_name_plural = 'Offer Categories'

    def __str__(self):
        return self.category.category_name

    @property
    def discount_percentage(self):
       return (100 * discount)/product.price

class Banner(models.Model):
    banner_name    = models.CharField(max_length=200, unique=True)
    image1         = models.ImageField(upload_to='photos/Banners')
    image2         = models.ImageField(upload_to='photos/Banners')
    image3         = models.ImageField(upload_to= 'photos/Banners')
    is_selected    = models.BooleanField(default=False)


    def __str__(self):
        return self.banner_name


class Wishlist(models.Model):
    user           = models.ForeignKey(Account, on_delete=models.CASCADE)
    listed_product = models.ForeignKey(Products, on_delete=models.CASCADE)
    date           = models.DateTimeField(auto_now_add=True)