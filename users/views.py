from django.shortcuts import render,redirect
from . models import Products,Wishlist
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='login')
def add_wishlist(request, id):
    wish = get_object_or_404(Products, id=id)
    Wishlist.objects.get_or_create(listed_product = wish, user = request.user)
    return redirect(view_wishlist)

@login_required(login_url='login')
def view_wishlist(request):
    wishlist = Wishlist.objects.filter(user = request.user)
    return render(request, 'home/wishlist.html', {'wishlist' :wishlist })


@login_required(login_url='login')
def remove_wishlist(request, id):
    wishlist = Wishlist.objects.get(user = request.user, id=id)
    wishlist.delete()
    return redirect(view_wishlist)
