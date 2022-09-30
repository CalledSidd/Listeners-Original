from django.shortcuts import render,redirect
from users.models import Products
from . models import Cart, CartItem, Coupon , Usedcoupon
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages

#  Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



def updatecart(request, id):
    current_user = request.user
    if current_user.is_authenticated:
        cart_id = id
        cart_item = CartItem.objects.get(id = cart_id)
        cart_item.quantity += 1 
        cart_item.save()
        cart_q  = cart_item.quantity
        return HttpResponse(cart_q)
    else:
        pass



@login_required(login_url='login')
def addtocart(request,id):
    current_user = request.user
    product = Products.objects.get(id=id) 
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request)) #get cart using the cart id present in the session
            cart.save()
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
            cart_id = _cart_id(request))
            cart.save()
        try:
            cart_item = CartItem.objects.get(product = product, cart = cart, user= request.user)
            cart_item.quantity += 1 
            cart_item.save()
        except CartItem.DoesNotExist:
                cart_item   = CartItem.objects.create(
            product = product,
            quantity= 1,
            cart    = cart,
            user= request.user
        )
        cart_item.save()
        
    else:
        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id = _cart_id(request))   
            cart.save() 
        try:
            cart_item = CartItem.objects.get(product = product, cart = cart)
            cart_item.quantity += 1 
            cart_item.save()

        except CartItem.DoesNotExist:
                cart_item   = CartItem.objects.create(
            product = product,
            quantity= 1,
            cart    = cart,
        )
        cart_item.save()
    return redirect('cart')

def removefromcart(request, id):
    if request.user.is_authenticated:
        cart      = Cart.objects.get(cart_id =_cart_id(request))
        product   = get_object_or_404(Products, id=id )
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def removecartitem(request, id):
    product   =  get_object_or_404(Products, id=id)
    cart_item =  CartItem.objects.get(product=product)
    cart_item.delete()
    return redirect('cart')

def cart(request, total = 0, quantity= 0, cart_items=None):
    if 'coupon_code' in request.session:
        coupon_code = request.session['coupon_code']
        coupon = Coupon.objects.get(coupon_code= coupon_code)
        reduction = coupon.discount
    else:
        reduction = 0
    try:
        tax           = 0
        grand_total   = 0
        if request.user.is_authenticated:
            cart_items    = CartItem.objects.filter( user= request.user)
            cart          = Cart.objects.get(cart_id=_cart_id(request))
        else:
            cart          = Cart.objects.get(cart_id=_cart_id(request))
            cart_items    = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            if cart_item.product.discount_price:
                    total       += (cart_item.product.discount_price * cart_item.quantity)
            else:
                    total       += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = ( 2* total)/100
        grand_total = total + tax - reduction*total/100
    except ObjectDoesNotExist:
        pass
    context = {
        'total'      : total,
        'quantity'   : quantity,
        'cart_items' : cart_items,
        'tax'        : tax,
        'grand_total': grand_total,
    }
    return render(request, 'home/cart.html', context)

# ///////////////////////////////////////////////////////////////////Coupon////////////////////////////////////////////////////////////////////
def coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            if Coupon.objects.get(coupon_code = coupon_code):
                coupon_exists = Coupon.objects.get(coupon_code = coupon_code)
                print(coupon_exists)
                try:
                    if Usedcoupon.objects.get(user = request.user, coupon = coupon_exists):
                        messages.error(request, "This coupon has been used or has expired")
                        return redirect('cart')
                except:
                    request.session['coupon_code'] = coupon_code
                    messages.success(request, "Your Coupon Has Been Applied")
            else:
                messages.error(request, "The Coupon you entered is Invalid")
                return redirect('cart')
        except:
            messages.error(request, "The Coupon you entered is Invalid")
    return redirect('cart')


def redirectFailed(request):
    return render(request, 'home/404.html')

def wishlist(request):
    return render(request, 'home/wishlist.html')