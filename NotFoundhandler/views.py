from django.shortcuts import render,redirect
from myadmin.views import adminlogin
# Create your views here.
def error_404(request, exception):
    user = request.user
    try:
        if user.is_admin:
            return redirect('adminlogin')
    except AttributeError:
        pass
    return render(request, 'home/404.html')