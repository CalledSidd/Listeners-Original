from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.decorators.cache import cache_control
from accounts.models import Account
from Category.models import Category
from users.models import Products,OfferProduct,OfferCategory
from orders.models import Orders,OrderProduct,Payment
from django.core.paginator import Paginator
from datetime import date
from .models import Todolist
from cart.models import Coupon
import datetime

# Create your views here.
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminlogin(request):
    if 'username' in request.session:
        return redirect(adminHome)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username = username, password = password)
        if user is not None:
            if user.is_superadmin:
                request.session['username'] = username
                login(request, user)
                return redirect(adminHome)
            else:
                messages.error(request, "Invalid Credentials")
                return redirect(adminHome)
        else:
            messages.error(request, "Invalid Credentials")
            print("User is none")
    return render(request, 'myadmin/signin.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def adminlogout(request):
    if 'username' in request.session:
        request.session.flush()
    logout(request)
    return redirect(adminlogin)

def adminHome(request):
    order = Payment.objects.filter(payment_method='COD')
    cod_total = 0
    cod       = 0
    for o in order:
        cod_total = cod_total+float(o.amount_paid)
        cod+=1
    order = Payment.objects.filter(payment_method='paypal')
    pay       = 0
    pay_total = 0
    for r in order:
        pay_total = pay_total+float(r.amount_paid)
        pay += 1
    order   = Payment.objects.filter(payment_method='Razorpay')
    raz     = 0
    raz_total = 0
    for d in order:
        raz_total = raz_total + float(d.amount_paid)
        raz += 1
    total_revenue = pay_total + raz_total + cod_total
    salesreport   = Orders.objects.all().order_by('date')
    todo          = Todolist.objects.all().order_by('-id')[:5]
    context = {
        'pay_total':pay_total,
        'pay':pay,
        'cod_total':cod_total,
        'cod':cod,
        'raz_total' : raz_total,
        'raz' : raz,
        'total' : total_revenue,
        'salesreport' : salesreport,
        'todo' : todo,
    }
    if 'username' in request.session:
        return render(request, 'myadmin/indexchart.html', context)
    else:
        return redirect(adminlogin)


def listuser(request):
    theusers = Account.objects.all()
    context = {
        'theusers' : theusers
    }
    return render(request, 'myadmin/userlist.html',context)

def blockuser(request, id):
    user = Account.objects.get(id =id)
    if user.is_active:
        user.is_active = False   
    else:
        user.is_active = True 
    user.save()
    return redirect(listuser)

def productlist(request):
    products      = Products.objects.all()
    paginator     = Paginator(products, 8)
    page          = request.GET.get('page')
    productsfinal = paginator.get_page(page)
    context = {
        'products': productsfinal,
    }
    return render(request, 'myadmin/productlist.html',context)

def deleteproduct(request, id):
    deleteproduct = Products.objects.get(id=id)
    deleteproduct.delete()
    return redirect(productlist)

def addproduct(request):
    values = Category.objects.all()
    if request.method == 'POST':
        name        = request.POST.get('name')
        description = request.POST.get('description')
        price       = request.POST.get('price')
        stock       = request.POST.get('stock')
        category    = request.POST.get('category')
        image1      = request.FILES.get('image1')
        image2      = request.FILES.get('image2')
        image4      = request.FILES.get('image4')
        image3      = request.FILES.get('image3')
        cat         = Category.objects.get(id=category)
        if name == '' or  description == '' or  price == '' or stock ==  '' or  image1 == '' or  image2 == '' or image3 == '' or  image4 == '':
            messages.error(request, "Fill All Fields Properly")
            return redirect(addproduct)
        else:
            productss   = Products(product_name=name, category=cat, description=description, price=price, stock=stock, image1=image1, image2=image2, image3=image3,image4=image4)
            productss.save()
        return redirect(productlist)
    context = {
        'values' : values
    }
    return render(request, 'myadmin/addproduct.html', context)


def editproduct(request, id):
    product = Products.objects.get(id=id)
    values    = Category.objects.all()
    if request.method == 'POST':
        product_name        = request.POST.get('name')
        product_description = request.POST.get('description')
        product_price       = request.POST.get('price')
        product_stock       = request.POST.get('stock')
        product_image1      = request.FILES.get('image1')
        product_image2      = request.FILES.get('image2')
        product_image3      = request.FILES.get('image3')
        product_image4      =  request.FILES.get('image4')
        obj                 = Products.objects.get(id=id)
        obj.name            = product_name
        obj.description     = product_description
        obj.price           = product_price
        obj.stock           = product_stock
        obj.image1          = product_image1
        obj.image2          = product_image2
        obj.image3          = product_image3
        obj.image4          = product_image4
        if product_name == '' or  product_description == '' or  product_price == '' or product_stock ==  '' or  product_image1 == '' or  product_image2 == '' or product_image3 == '' or  product_image4 == '':
            messages.error(request, "Fill All Fields Properly")
            return render(request, 'myadmin/editproduct.html')
        else:
            obj.save()
        return redirect(productlist)
    context = {
        'product': product,
        'values'     : values
    }
    return render(request, 'myadmin/editproduct.html', context)

def listcategory(request):
    if 'username' in request.session:
        values = Category.objects.all()
        context = {
            'values':values
        }
        return render(request, 'myadmin/categorylist.html',context)
    return redirect(adminlogin)

def addcategory(request):
    if request.method == 'POST':
        category_name = request.POST.get('name')
        description   = request.POST.get('description')
        cat_image     = request.POST.get('image1')
        if category_name == '' or description == '' or cat_image == '':
            messages.error(request, "Please fill all fields properly") 
        elif Category.objects.filter(category_name__iexact=category_name).exists():
            messages.error(request,"category Already Exists")
        else:
            catsss = Category(category_name=category_name, description=description, cat_image=cat_image)
            catsss.save()
            return redirect(listcategory)
    return render(request, 'myadmin/addcategory.html')


def deletecategory(request,id):
    cat = Category.objects.get(id=id)
    cat.delete()
    return redirect(listcategory)

def editcategory(request,id):
    cat  = Category.objects.get(id=id)
    if request.method == 'POST':
        category_name = request.POST.get('name')
        description   = request.POST.get('description')
        cat_image     = request.POST.get('image1')
        if category_name == '' or description == '' or cat_image == '':
            messages.error(request, "Please fill all fields properly") 
        elif category_name.exists():
            messages.error(request,"category Already Exists")
        else:
            catsss = Category(category_name=category_name, description=description, cat_image=cat_image)
            catsss.save()
            return redirect(listcategory)
    return render(request, 'myadmin/editcategory.html' , {'cat' : cat})



def orderlist(request):
    order = Orders.objects.all().order_by('date')
    context = {
            'order' : order,
        }
    return render(request, 'myadmin/orderlist.html', context)


def vieworder(request, id):
    orders = Orders.objects.get(id = id)
    orderproduct = OrderProduct.objects.filter(order = orders)
    return render(request, 'myadmin/vieworder.html',{'orders' : orders, 'orderproduct':orderproduct})

def changeorderstatus(request, id):
    status = request.POST.get("status")
    print(status)
    op = OrderProduct.objects.get(id=id)
    op.status = status
    op.save()
    return redirect(orderlist) 


# def salesReport(request):
#     frmdate = date
#     fm = [2022, frmdate, 1]
#     todt = [2022, frmdate, 28]
#     return redirect(adminHome)

def ViewCoupon(request):
    c = Coupon.objects.all()
    context = {
        'c' : c
    }
    return render(request, 'myadmin/couponlist.html', context)


def AddCoupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        discount    = request.POST.get('discount')
        if coupon_code == '':
            messages.error(request, 'You have not entered a coupon code')
        else:
            coupon = Coupon(coupon_code= coupon_code, discount = discount)
            coupon.save()
            return redirect('couponlist')
    return render(request, 'myadmin/addcoupon.html')


def DeleteCoupon(request, id):
    coupon = Coupon.objects.get(id=id)
    coupon.delete()
    return redirect(ViewCoupon)


# ////////////////////////////////////////
def ListOffer(request):
    CategOffer = OfferCategory.objects.all()
    ProdOffer  = OfferProduct.objects.all()
    context = {
        'OfferC' : CategOffer,
        'OfferP' : ProdOffer,
    }
    return render(request, 'myadmin/offerlist.html', context)

def AddCategoryOffer(request):
    category = Category.objects.all()
    if request.method == 'POST' : 
        discount = request.POST.get('discount')
        chosencategory = request.POST.get('category')
        discount = int(discount)
        if OfferCategory.objects.filter(category = chosencategory).exists():
            messages.error(request, 'Offer is already applied for this category')
            return redirect('listoffer')
        if discount > 0:
            if discount < 90:
                categoryOffer = OfferCategory(discount = discount, category= Category.objects.get(id = chosencategory))
                categoryOffer.save()
                messages.success(request, "New Category Offer Has Been Added")
                return redirect('listoffer')
            else:
                messages.error(request, 'Offer for a category cannot be more than 90%')
                return redirect(AddCategoryOffer)
        else:
            messages.error(request, 'Offer must be greater than 0')
            return redirect(AddCategoryOffer)
    return render(request, 'myadmin/addcategoryoffer.html', {'category' : category})


def AddProductOffer(request):
    products = Products.objects.all()
    if request.method == 'POST':
        discount = request.POST.get('discount')
        chosenproduct  = request.POST.get('product')
        discount = int(discount)
        if OfferProduct.objects.filter(product=chosenproduct).exists():
            messages.error(request, 'Offer is already applied for this category')
            return redirect('listoffer')
        if discount > 0:
            if discount < 90:
                productOffer = OfferProduct()
                productOffer.discount = discount
                product = Products.objects.get(id = chosenproduct)
                product.discount_price = (product.price - (product.price * discount/100))
                product.save()
                productOffer.product = Products.objects.get(id = chosenproduct)
                productOffer.save()
                return redirect('listoffer')
            else:
                messages.error(request, "Discount must be less than 90%")
                return redirect(AddProductOffer)
        else:
            messages.error(request, "Discount must be greater than 0%")
            return redirect(AddProductOffer)
    return render(request, 'myadmin/addproductoffer.html', {'product' : products})

def DeleteProductOffer(request, id):
    delProductOffer = OfferProduct.objects.get(id = id)
    delProductOffer.delete()
    messages.success(request, 'Offer Deleted Succesfully')
    return redirect('listoffer')


def DeleteCategoryOffer(request, id):
    delCategoryOffer = OfferCategory.objects.get( id = id)
    delCategoryOffer.delete()
    messages.success(request, 'Offer Deleted Succesfully')
    return redirect('listoffer')


def salesReport(request):
    salesreport   = Orders.objects.all().order_by('id')
    context = {
        'salesreport' : salesreport,
    }
    return render(request, 'myadmin/salesreport.html' , context)


def date_range(request):
    fromdate = request.POST.get('from')
    todate   = request.POST.get('to')
    if len(fromdate) > 0 and len(todate) > 0:
        frm = fromdate.split('-')
        tod = todate.split('-')

        fm   = [int(x) for x in frm ]
        todt = [int(x) for x in tod ]

        salesreport = Orders.objects.filter(date_gte = datetime.date(fm[0], fm[1], fm[2]),
                                            date_lte = datetime.date(todt[0], todt[1], todt[2]))
    else :
        salesreport = Orders.objects.all()
    context = {
            'salesreport' : salesreport
        }
    return render(request, 'myadmin/salesreport.html' , context)


def monthlyreport(request, date):
    fromdate = date
    fm = [2022, fromdate , 1]
    todt = [2022, fromdate , 28 ]
    salesreport = Orders.objects.filter(date__gte = datetime.date(fm[0], fm[1], fm[2]),
                                        date__lte = datetime.date(todt[0], todt[1], todt[2]))
    if len(salesreport) > 0:
        context = {
            'salesreport' : salesreport,
        }
        return render(request, 'myadmin/salesreport.html' , context)
    else:
        messages.info(request, 'No Orders')
        return render(request, 'myadmin/salesreport.html')


def yearlyreport(request, date) :
    fromdate = date 
    fm = [fromdate, 1 , 1]
    todt = [fromdate, 12, 31 ]
    salesreport = Orders.objects.filter(date__gte = datetime.date(fm[0], fm[1], fm[2]),
                                        date__lte = datetime.date(todt[0], todt[1], todt[2]))
    if len(salesreport) > 0:
        context = {
            'salesreport' : salesreport,
        }
        return render(request, 'myadmin/salesreport.html' , context)
    else:
        messages.info(request, 'No Orders')
        return render(request, 'myadmin/salesreport.html')

def todolist(request):
    todolist = Todolist.objects.all()
    todo = request.POST.get('todo')
    todolist = Todolist.objects.create(todolist = todo )
    return redirect(adminHome)


def todo_delete(request, id):
    todo = Todolist.objects.filter(id = id)
    todo.delete()
    return redirect(adminHome)



# import tempfile
# from django.template.loader import render_to_string
# from urllib import response



# def download_pdf(request):
#     response = HttpResponse(content_type = 'application.pdf')
#     response['Content-Disposition'] = 'inline; attachement; filename=SalesReport' +str(datetime.datetime.now())+'.pdf'
#     response['Content-Transfer-Encoding'] = 'binary'

#     salesreport = Orders.objects.all()
#     total       = salesreport.aggregate(Su,('order_total'))
#     html_string = render_to_string('admin/pdf_output.html', {'salesreport':salesreport, 'total':total})
#     html        = HTML(string=html_string)
#     result      = html.write_pdf()

#     with tempfile.NamedTemporaryFile(delete=True) as output:
#         output.write(result)
#         output.flush()

#         output = open(output.name,'rb')
#         response.write(output.read())

#     return response 

import csv
from django.http import HttpResponse
def download_csv(request):
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename=SalesReport' + str(datetime.datetime.now())+'.csv'
    writer  = csv.writer(response)
    writer.writerow(['order ','name ','amount ','date'])
    salesreport = Orders.objects.all()

    for sale in salesreport:
        writer.writerow([sale.order_id, sale.user.username, sale.order_total, sale.date ])
    return response








import xlwt
from urllib import response

def download_excel(request):
    response = HttpResponse(content_type = 'application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=SalesReport' + str(datetime.datetime.now())+'.xls'
    wb       = xlwt.Workbook(encoding = 'utf-8')
    ws       = wb.add_sheet('SalesReport')
    row_num  = 0
    font_style= xlwt.XFStyle()
    font_style.font.bold = True
    columns   = ['order ','name ','amount ','date ']


    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()

    rows = Orders.objects.all().values_list('order_id','user','order_total','date')

    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num,col_num, str(row[col_num]),font_style)

    wb.save(response)

    return response
