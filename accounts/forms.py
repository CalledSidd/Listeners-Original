from django import forms
from . models import Account


# forms here

class RegistrationForm(forms.ModelForm):
    class Meta:
        model  = Account
        fields = ['username','first_name','last_name','phone_number','email','password']