from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User,auth
from orders.models import Orders,OrderProduct
from accounts.models import Account,Address
from cart.models import Cart,CartItem
from . forms import RegistrationForm
from django.http import HttpResponse
from django.contrib import messages
from users.models import Products,OfferCategory,OfferProduct,Banner
from django.conf import settings
from cart.views import _cart_id
from twilio.rest import Client
from django.db.models import Q
from Category.models import *
from myadmin import views
from ast import Return
import email

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    products = Products.objects.all().order_by('-created_date')
    banner   = Banner.objects.all()
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
            if not Prod:
                r.discount_price = None
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save() 
    context = {
        'products':products,
        'banner' : banner,
    }
    return render(request,'home/index.html',context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userlogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email = email, password = password)
        if user is not None: 
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                currentcart = CartItem.objects.filter(user=request.user)
                if is_cart_item_exists:
                    cart_item =  CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        # if item in currentcart:
                        #     item.quantity += 1
                        item.user = user
                        item.save()
            except:
                pass
            login(request, user)
            request.session['email'] = email
            return redirect(home)
        else:
            messages.error(request,"Invalid Credentials ")
    return render(request, 'home/login.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def signup(request):
    if request.method == 'POST':
        first_name   = request.POST.get('first_name')
        last_name    = request.POST.get('last_name')
        username     = request.POST.get('username')
        email        = request.POST.get('mail')
        phone_number = request.POST.get('phone_number')
        password     = request.POST.get('password')
        password2    = request.POST.get('password2')
        if password == password2:
            if Account.objects.filter(username = username).exists():
                messages.error(request,"User Already Exists")
                return redirect(userlogin)
            elif email == '' or username == '' or first_name == '' or last_name == '' or password == '' or password2 == '':
                messages.error(request, "Please Fill the all Fields")
            else:
                user = Account.objects.create_user(email = email, first_name=first_name, last_name = last_name, username = username, password = password, phone_number = phone_number)
                user.save();
                return redirect(userlogin)
        else:
            messages.error(request,"Passwords do not match")
            return render(request, 'home/signup.html')
    return render(request, 'home/signup.html')

def number_login(request):
    if request.method == 'POST':
        phone_number    = request.POST['phone_number']
        phone_no        ="+91" + phone_number
        print(phone_number)
        if Account.objects.filter(phone_number=phone_number).exists():
            print("Phone number exists")
            user = Account.objects.get(phone_number = phone_number)
            account_sid  = settings.ACCOUNT_SID
            auth_token   = settings.AUTH_TOKEN
            client       = Client(account_sid,auth_token)
            verification = client.verify \
                .services(settings.SERVICES) \
                .verifications \
                .create(to=phone_no ,channel='sms')
            context = {
                'phone_number' : phone_number
            }
            return render(request,'home/otp.html',context)
        else:
            messages.error(request,'invalid Mobile number')
            return redirect(number_login)
    return render(request,"home/otp-phone.html")


def otp(request, phone_number):
    if request.method == 'POST':
        if Account.objects.filter(phone_number= phone_number):
            user           = Account.objects.get(phone_number= phone_number)
            phone_no       = "+91" + str(phone_number)
            otp_input      = request.POST.get('otp')
            if len(otp_input)>0:
                account_sid        = settings.ACCOUNT_SID
                auth_token         = settings.AUTH_TOKEN
                client             = Client(account_sid, auth_token)
                verification_check = client.verify \
                                    .services(settings.SERVICES) \
                                    .verification_checks \
                                    .create(to= phone_no, code= otp_input)
                if verification_check.status == "approved":
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect(home)
                else:
                    messages.error(request,'Invalid OTP')
                    return render(request,'home/otp.html',{'phone_number':phone_number}) 
            else:
                messages.error(request,'Invalid OTP')
                return render(request,'home/otp.html',{'phone_number':phone_number})
        else:
            messages.success(request,'Invalid Phone number')
            return redirect(otp)
    return render(request,"home/otp.html")

def userlogout(request):
    if 'username' in request.session:
        request.session.flush()
    logout(request)
    return redirect(home)


def shop(request):
    products       = Products.objects.all().filter(Is_available=True)
    products_count = products.count()
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
            if not Prod:
                r.discount_price = None
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save()  
    context    = {
                'products': products,
                'Prod' : Prod,
            }
    return render(request,'home/product.html',context)


# Category Sorting  Banner Start 
def iem(request):
    cat      = Category.objects.get(category_name='IEM')
    products = Products.objects.filter(category=cat)
    Prod     = 0
    Cat      = 0
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save()
        try:
            Coffer = OfferCategory.objects.get(category = r.category )
            Cat    = Coffer.discount
            if Coffer:
                r.discount_price = int(r.price - (r.price*(Cat/100)))
                r.save()
        except Exception as e :
            r.discount_price = None
            r.save()
        try:
            if Poffer and Coffer:
                if Prod > Cat:
                    r.discount_price = int(r.price - (r.price * (Prod/100)))
                    r.save()
                else:
                    r.discount_price = int(r.price - (r.price * (Cat/100)))
        except Exception as e:
            pass
        try:
            if not Poffer and Coffer:
                r.discount_price = None
                r.save()
            if not Prod and Coffer:
                r.discount_price = None
                r.save()
        except Exception as e:
            pass
    context  = {
        'products' : products,
        'Prod' : Prod,
        'Cat'  : Cat
    }
    return render(request,'home/iem.html',context)

def overtheear(request):
    cat      = Category.objects.get(category_name='Over The Ear')
    products = Products.objects.filter(category=cat)
    Prod     = 0
    Cat      = 0
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save()
        try:
            Coffer = OfferCategory.objects.get(category = r.category )
            Cat    = Coffer.discount
            if Coffer:
                r.discount_price = int(r.price - (r.price*(Cat/100)))
                r.save()
        except Exception as e :
            r.discount_price = None
            r.save()
        try:
            if Poffer and Coffer:
                if Prod > Cat:
                    r.discount_price = int(r.price - (r.price * (Prod/100)))
                    r.save()
                else:
                    r.discount_price = int(r.price - (r.price * (Cat/100)))
        except Exception as e:
            pass
        try:
            if not Poffer and Coffer:
                r.discount_price = None
                r.save()
            if not Prod and Coffer:
                r.discount_price = None
                r.save()
        except Exception as e:
            pass
    context  = {
        'products' : products,
        'Prod' : Prod,
        'Cat'  : Cat
    }
    return render(request,'home/overtheear.html',context)

def TWS(request):
    cat      = Category.objects.get(category_name='True Wireless')
    products = Products.objects.filter(category=cat)
    Prod     = 0
    Cat      = 0
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save()
        try:
            Coffer = OfferCategory.objects.get(category = r.category )
            Cat    = Coffer.discount
            if Coffer:
                r.discount_price = int(r.price - (r.price*(Cat/100)))
                r.save()
        except Exception as e :
            r.discount_price = None
            r.save()
        try:
            if Poffer and Coffer:
                if Prod > Cat:
                    r.discount_price = int(r.price - (r.price * (Prod/100)))
                    r.save()
                else:
                    r.discount_price = int(r.price - (r.price * (Cat/100)))
        except Exception as e:
            pass
        try:
            if not Poffer and Coffer:
                r.discount_price = None
                r.save()
            if not Prod and Coffer:
                r.discount_price = None
                r.save()
        except Exception as e:
            pass
    context  = {
        'products' : products,
        'Prod' : Prod,
        'Cat'  : Cat
    }
    return render(request,'home/tws.html', context)
# Category sorting  banner end

# category sorting in html product display
def truewireless(request):
    cat      = Category.objects.get(category_name='True Wireless')
    products = Products.objects.filter(category=cat)
    Prod     = 0
    Cat      = 0
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save()
        try:
            Coffer = OfferCategory.objects.get(category = r.category )
            Cat    = Coffer.discount
            if Coffer:
                r.discount_price = int(r.price - (r.price*(Cat/100)))
                r.save()
        except Exception as e :
            r.discount_price = None
            r.save()
        try:
            if Poffer and Coffer:
                if Prod > Cat:
                    r.discount_price = int(r.price - (r.price * (Prod/100)))
                    r.save()
                else:
                    r.discount_price = int(r.price - (r.price * (Cat/100)))
        except Exception as e:
            pass
        try:
            if not Poffer and Coffer:
                r.discount_price = None
                r.save()
            if not Prod and Coffer:
                r.discount_price = None
                r.save()
        except Exception as e:
            pass
    context  = {
        'products' : products,
        'Prod' : Prod,
        'Cat'  : Cat
    }
    return render(request, 'home/product.html' , context)

def OverEar(request):
    cat      = Category.objects.get(category_name='Over The Ear')
    products = Products.objects.filter(category=cat)
    Prod     = 0
    Cat      = 0
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save()
        try:
            Coffer = OfferCategory.objects.get(category = r.category )
            Cat    = Coffer.discount
            if Coffer:
                r.discount_price = int(r.price - (r.price*(Cat/100)))
                r.save()
        except Exception as e :
            # r.discount_price = None
            # r.save()
            pass
        try:
            if Poffer and Coffer:
                if Prod > Cat:
                    r.discount_price = int(r.price - (r.price * (Prod/100)))
                    r.save()
                else:
                    r.discount_price = int(r.price - (r.price * (Cat/100)))
        except Exception as e:
            pass
        try:
            if not Poffer and Coffer:
                r.discount_price = None
                r.save()
            if not Prod and Coffer:
                r.discount_price = None
                r.save()
        except Exception as e:
            pass
    context  = {
        'products' : products,
        'Prod' : Prod,
        'Cat'  : Cat
    }
    return render(request,'home/product.html',context)

def inearmonitor(request):
    cat      = Category.objects.get(category_name='IEM')
    products = Products.objects.filter(category=cat)
    Prod     = 0
    Cat      = 0
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save()
        try:
            Coffer = OfferCategory.objects.get(category = r.category )
            Cat    = Coffer.discount
            if Coffer:
                r.discount_price = int(r.price - (r.price*(Cat/100)))
                r.save()
        except Exception as e :
            pass
        try:
            if Poffer and Coffer:
                if Prod > Cat:
                    r.discount_price = int(r.price - (r.price * (Prod/100)))
                    r.save()
                else:
                    r.discount_price = int(r.price - (r.price * (Cat/100)))
        except Exception as e:
            pass
        try:
            if not Poffer and Coffer:
                r.discount_price = None
                r.save()
            if not Prod and Coffer:
                r.discount_price = None
                r.save()
        except Exception as e:
            pass
    context  = {
        'products' : products,
        'Prod' : Prod,
        'Cat'  : Cat
    }
    return render(request,'home/product.html',context)


def userprofile(request):
    address = Address.objects.filter(user = request.user)
    context = {
        'address' : address,
    }
    return render(request,'home/userprofilebase.html', context)

def edituserprofile(request):
    return render(request, 'home/userprofileedit.html')

def productdetail(request,id):
    value = Products.objects.get(id=id)
    context = {
        'value':value
    }
    return render(request, 'home/product-detail.html',context)

def listorder(request):
    orders = OrderProduct.objects.all().filter(user = request.user).order_by('-created_at')
    context = {
        'orders' : orders
    }
    return render(request, 'home/orderlist.html' , context)

def cancelorder(request,id):
    orders = OrderProduct.objects.get(id=id)
    orders.status = 'Cancelled'
    orders.save()
    return redirect(listorder)


def changepassword(request):
    if request.method == 'POST':
        current_pass = request.POST.get('current_pass')
        new_pass     = request.POST.get('new_pass')
        confirm_pass     = request.POST.get('confirm_pass')

        account = Account.objects.get(email = request.user)
        password = account.check_password(current_pass)

        if new_pass == confirm_pass:
            if password : 
                account.set_password(new_pass)
                account.save()
                login(request, account)

                messages.success(request, "Your password has been changed")
                return redirect('userprofile')
            else:
                messages.error(request, "Password does not exist")
                return redirect('changepassword')
    return render(request, "home/changepassword.html")


def search(request):
    if 'search' in request.GET:
        keyword = request.GET['search']
        if keyword :
            products = Products.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
        context = {
            'products' : products,
        }
    return render(request,'home/product.html', context)


def invoice(request, id):
    address = Address.objects.filter(user = request.user)
    order   = OrderProduct.objects.filter(id = id)
    context = {
        'address':address,
        'order': order,
        
    }
    return render(request, 'home/invoice.html', context)


def flush(request):
    request.session.flush()
    return render(request, 'home/404.html')


def returnOrder(request, id):
    orders = OrderProduct.objects.get(id=id)
    orders.status = 'Returned'
    orders.save()
    return redirect(listorder)

def WhatsNew(request):
    products = Products.objects.all().order_by('-created_date')
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save()
        try:
            Coffer = OfferCategory.objects.get(category = r.category )
            Cat    = Coffer.discount
            if Coffer:
                r.discount_price = int(r.price - (r.price*(Cat/100)))
                r.save()
        except Exception as e :
            # r.discount_price = None
            # r.save()
            pass
        try:
            if Poffer and Coffer:
                if Prod > Cat:
                    r.discount_price = int(r.price - (r.price * (Prod/100)))
                    r.save()
                else:
                    r.discount_price = int(r.price - (r.price * (Cat/100)))
        except Exception as e:
            pass
        try:
            if not Poffer and Coffer:
                r.discount_price = None
                r.save()
            if not Prod and Coffer:
                r.discount_price = None
                r.save()
        except Exception as e:
            pass
    context  = {
        'products' : products
    }
    return render(request,'home/product.html',context)

def LowtoHigh(request):
    products = Products.objects.all().order_by('price')
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save()
        try:
            Coffer = OfferCategory.objects.get(category = r.category )
            Cat    = Coffer.discount
            if Coffer:
                r.discount_price = int(r.price - (r.price*(Cat/100)))
                r.save()
        except Exception as e :
            r.discount_price = None
            r.save()
        try:
            if Poffer and Coffer:
                if Prod > Cat:
                    r.discount_price = int(r.price - (r.price * (Prod/100)))
                    r.save()
                else:
                    r.discount_price = int(r.price - (r.price * (Cat/100)))
        except Exception as e:
            pass
        try:
            if not Poffer and Coffer:
                r.discount_price = None
                r.save()
            if not Prod and Coffer:
                r.discount_price = None
                r.save()
        except Exception as e:
            pass
    context  = {
        'products' : products
    }
    return render(request,'home/product.html',context)


def HightoLow(request):
    products = Products.objects.all().order_by('-price')
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save()
        try:
            Coffer = OfferCategory.objects.get(category = r.category )
            Cat    = Coffer.discount
            if Coffer:
                r.discount_price = int(r.price - (r.price*(Cat/100)))
                r.save()
        except Exception as e :
            r.discount_price = None
            r.save()
        try:
            if Poffer and Coffer:
                if Prod > Cat:
                    r.discount_price = int(r.price - (r.price * (Prod/100)))
                    r.save()
                else:
                    r.discount_price = int(r.price - (r.price * (Cat/100)))
        except Exception as e:
            pass
        try:
            if not Poffer and Coffer:
                r.discount_price = None
                r.save()
            if not Prod and Coffer:
                r.discount_price = None
                r.save()
        except Exception as e:
            pass
    context  = {
        'products' : products
    }
    return render(request,'home/product.html',context)


def Popularity(request):
    products = Products.objects.all().order_by('-price')
    for r in products:
        try:
            Poffer = OfferProduct.objects.get(product= r.id)
            Prod   = Poffer.discount
            if Poffer:
                r.discount_price = int(r.price - (r.price*(Prod/100)))
                r.save()
        except Exception as e : 
            r.discount_price = None
            r.save()
        try:
            Coffer = OfferCategory.objects.get(category = r.category )
            Cat    = Coffer.discount
            if Coffer:
                r.discount_price = int(r.price - (r.price*(Cat/100)))
                r.save()
        except Exception as e :
            r.discount_price = None
            r.save()
        try:
            if Poffer and Coffer:
                if Prod > Cat:
                    r.discount_price = int(r.price - (r.price * (Prod/100)))
                    r.save()
                else:
                    r.discount_price = int(r.price - (r.price * (Cat/100)))
        except Exception as e:
            pass
        try:
            if not Poffer and Coffer:
                r.discount_price = None
                r.save()
            if not Prod and Coffer:
                r.discount_price = None
                r.save()
        except Exception as e:
            pass
    context  = {
        'products' : products
    }
    return render(request,'home/product.html',context)


def loginsignup(request):
    return render(request, 'home/loginsignup.html')

def deleteAddress(request):
    if request.method == 'POST':
        address = Address.objects.get(user = request.user, id = id)
        address.delete()
        address.save()
        return redirect(userprofile)
