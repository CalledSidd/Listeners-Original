from django.shortcuts import render,redirect,reverse
from cart.models import CartItem
import datetime
from datetime import date
from django.core.exceptions import ObjectDoesNotExist
from users.models import Products
from . models import Orders,Payment,OrderProduct
from cart.views import *
from accounts.models import Address
from django.conf import settings
import random
import razorpay
import json
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required 
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
# Create your views here.


def addaddress(request):
    if request.method == 'POST':
        firstname    = request.POST.get('first_name')
        lastname     = request.POST.get('last_name')
        phonenumber  = request.POST.get('phone_number')
        email        = request.POST.get('email')
        address      = request.POST.get('address')
        state        = request.POST.get('state')
        town         = request.POST.get('town')
        pincode      = request.POST.get('zip_code')
        address = Address(firstname = firstname, lastname=lastname, phonenumber= phonenumber, address=address, email=email,town=town, state=state, pincode=pincode, user=request.user)
        address.save()
        return redirect(checkout)
    return render(request, 'home/address.html')




def checkout(request):
    total = 0
    quantity = 0
    cart_items = None
    tax = 0
    grand_total = 0
    global theaddress
    theaddress = request.POST.get('address') #address object in the address as we passed address in it
    if request.user.is_authenticated:
        if 'coupon_code' in request.session:
            coupon_code = request.session['coupon_code']
            print(coupon_code)
            coupon = Coupon.objects.get(coupon_code= coupon_code)
            reduction = coupon.discount
        else:
            reduction = 0
        cart_item_count = CartItem.objects.filter(user = request.user, is_active = True).count()
        if cart_item_count > 0:
            try:
                details = Address.objects.filter(user = request.user)
                cart_items = CartItem.objects.filter(user = request.user, is_active =True)
                if CartItem.objects.filter(user = request.user):
                    cart_items = CartItem.objects.filter(user = request.user)
                for cart_item in cart_items :
                    if cart_item.product.discount_price:
                        total       += (cart_item.product.discount_price * cart_item.quantity)
                    else:
                        total       += (cart_item.product.price * cart_item.quantity)
                    quantity += cart_item.quantity
                tax = (2*total)/100
                grand_total = total + tax - reduction*total/100
            except ObjectDoesNotExist:
                pass
        else:
            return redirect('home') 
# /////////////////////////RazorpayCLient//////////////////////////
        client = razorpay.Client(auth=(settings.RAZOR_KEY_ID , settings.RAZOR_KEY_SECRET ))
        global payments
        payments = client.order.create({'amount': (grand_total)*100, 'currency':'INR', 'payment_capture':1})
        payment_id = payments['id']
        raztotal = grand_total*100
#//////////////////////////////////////////////////////////////////
        context = {
            'total' : total,
            'quantity': quantity,
            'cart_items':cart_items,
            'tax' : tax,
            'grand_total': grand_total,
            'details' : details,
            'raztotal' : raztotal
        }
    else:
        return redirect('login')
    return render(request, 'home/checkout.html' , context)

@login_required(login_url='login')
def paycod(request):
    total       = 0
    cart_items  = None
    quantity    = 0
    tax         = 0
    grand_total = 0
    if request.user.is_authenticated:
        try:
            if 'coupon_code' in request.session:
                coupon_code = request.session['coupon_code']
                print(coupon_code)
                coupon = Coupon.objects.get(coupon_code= coupon_code)
                reduction = coupon.discount
            else:
                reduction = 0
            details  = Address.objects.get(user = request.user)
            order_id = str(int(datetime.datetime.now().strftime('%Y%m%d%H%H%S')))

            if CartItem.objects.filter(user = request.user):
                cart_items = CartItem.objects.filter(user = request.user)
            for cart_item in cart_items:
                if cart_item.product.discount_price:
                      total       += (cart_item.product.discount_price * cart_item.quantity)
                else:
                     total       += (cart_item.product.price * cart_item.quantity)
            tax         = (2*total)/100
            grand_total = total + tax - reduction*total/100
            payment_method  = 'COD'
            pay = Payment(user = request.user, payment_method = payment_method, amount_paid=grand_total, status='Pending')
            pay.save()
            order = Orders(user = request.user,address=details, payment=pay, order_total=total, order_id=order_id, date=date)
            order.is_ordered = True
            order.save()
            # this is where the problem is it is not iteraing through properly
            for item in cart_items:
                orderpro = OrderProduct(
                    order   = order,
                    payment = pay,
                    user    = request.user,
                    quantity= item.quantity,
                    product = item.product,
                    product_price = item.product.price,
                    ordered=True
                )
                orderpro.save() 
                for item in cart_items:
                    product = Products.objects.get(id = item.product.id)
                    product.stock -= item.quantity
                    product.save()
                for item in cart_items:
                    item.delete()
        except Exception as e:
            print(e)
            print("In except for try block inside COD")
            render(request, 'home/404.html')
    else:
        return redirect('cart')
    if 'coupon_code' in request.session:
        try:
            coupon_used = Usedcoupon(coupon= coupon, user = request.user)
            coupon_used.save()
        except Exception as e:
            print(e, "In except for deleting coupon")
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
    context = {
        'total'       : total,
        'quantity'    : quantity,
        'tax'         : tax,
        'grand_total' : grand_total,
        'details'     : details
    }
    return render(request, 'home/orderplaced.html')

def cancelled(request):
    return render(request, 'home/404.html')

def paypal(request):
    total       = 0
    tax         = 0
    grand_total = 0
    quantity    = 0
    rawtotal    = 0
    reduction   = 0
    host = request.get_host()
    cart_items = CartItem.objects.filter(user = request.user)
    for cart_item in cart_items:
        if cart_item.product.discount_price:
            total       += (cart_item.product.discount_price * cart_item.quantity)
        else:
            total       += (cart_item.product.price * cart_item.quantity)
        tax         = (2*total)/100
        grand_total = total + tax - reduction*total/100
    paypal_dict = {
        'business' : settings.PAYPAL_RECEIVER_EMAIL,
        'amount'   : grand_total,
        'currency_code' : 'USD',
        'notify_url'    : 'http://{}{}'.format(host, reverse('paypal-ipn')),
        'return_url'    : 'http://{}{}'.format(host, reverse('payment_done')),
        'cancel_return' : 'http://{}{}'.format(host, reverse('payment_cancelled')),
    }
    form   = PayPalPaymentsForm(initial = paypal_dict)
    return render(request, 'home/paypal.html', {'form':form})


@csrf_exempt
def paypalpaymentDone(request):
    total = 0
    quantity = 0
    cart_items = None
    tax = 0
    grand_total = 0
    if 'coupon_code' in request.session:
        coupon_code = request.session['coupon_code']
        coupon = Coupon.objects.get(coupon_code= coupon_code)
        reduction = coupon.discount
    else:
        reduction = 0
    details  = Address.objects.get(user = request.user)
    order_id = str(int(datetime.datetime.now().strftime('%Y%m%d%H%H%S')))
    user = request.user
    if CartItem.objects.filter(user = request.user):
        cart_items = CartItem.objects.filter(user = request.user)
    for cart_item in cart_items:
        if cart_item.product.discount_price:
            total       += (cart_item.product.discount_price * cart_item.quantity)
        else:
            total       += (cart_item.product.price * cart_item.quantity)
        tax         = (2*total)/100
    grand_total = total + tax - reduction*total/100
    payment_method  = 'paypal'
    payment_id      = str(int(datetime.datetime.now().strftime('%Y%m%d%H%H%S')))
    dates = date.today()
    pay = Payment(user = request.user, payment_method = payment_method, amount_paid=grand_total, payment_id= payment_id, created_at= dates)
    pay.save()
    order = Orders(user = request.user,address=details, payment=pay, order_total=total, order_id=order_id, date=date)
    order.is_ordered = True
    order.save()
    for item in cart_items:
        orderpro = OrderProduct(
            order   = order,
            payment = pay,
            user    = request.user,
            quantity= item.quantity,
            product = item.product,
            product_price = item.product.price,
            ordered=True
        )
        orderpro.save()
        for item in cart_items:
            product = Products.objects.get(id = item.product.id)
            product.stock -= item.quantity
            product.save()

        for item in cart_items:
            item.delete()
        if 'coupon_code' in request.session:
            try:
                coupon_used = Usedcoupon(coupon= coupon, user = request.user)
                coupon_used.save()
            except Exception as e:
                print(e, "In except for deleting coupon")
            if 'coupon_code' in request.session:
                del request.session['coupon_code']
    return render(request, 'home/placedsuccessfully.html')

def RazorPaySuccess(request):
    total = 0
    quantity = 0
    cart_items = None
    tax = 0
    grand_total = 0 
    pay_id = request.GET.get('razorpay_payment_id')
    if 'coupon_code' in request.session:
        coupon_code = request.session['coupon_code']
        print(coupon_code)
        coupon = Coupon.objects.get(coupon_code= coupon_code)
        reduction = coupon.discount
    else:
        reduction = 0
    details  = Address.objects.get(user = request.user)
    order_id = str(int(datetime.datetime.now().strftime('%Y%m%d%H%H%S')))
    user = request.user
    if CartItem.objects.filter(user = request.user):
        cart_items = CartItem.objects.filter(user = request.user)
    for cart_item in cart_items:
        if cart_item.product.discount_price:
            total       += (cart_item.product.discount_price * cart_item.quantity)
        else:
            total       += (cart_item.product.price * cart_item.quantity)
    tax         = (2*total)/100
    grand_total = total + tax - reduction*total/100
    payment_method  = 'Razorpay'
    payment_id      = pay_id
    dates = date.today()
    pay = Payment(user = request.user, payment_method = payment_method, amount_paid=grand_total, payment_id= payment_id, created_at= dates)
    pay.save()
    order = Orders(user = request.user,address=details, payment=pay, order_total=total, order_id=order_id, date=date)
    order.is_ordered = True
    order.save()
    for item in cart_items:
        orderpro = OrderProduct(
            order   = order,
            payment = pay,
            user    = request.user,
            quantity= item.quantity,
            product = item.product,
            product_price = item.product.price,
            ordered=True
        )
        orderpro.save()
    for item in cart_items:
        product = Products.objects.get(id = item.product.id)
        product.stock -= item.quantity
        product.save()

    for item in cart_items:
        item.delete()
    
    if 'coupon_code' in request.session:
        try:
            coupon_used = Usedcoupon(coupon= coupon, user = request.user)
            coupon_used.save()
        except Exception as e:
            print(e, "In except for deleting coupon")
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
    context = {
        'order' : order,
        'details' : details,
        'payment_id'  : payment_id,
        'grand_total' : pay.amount_paid,
        'tax' : tax,
        'total' : total
    }

    return render(request, 'home/placedsuccessfully.html', context)
