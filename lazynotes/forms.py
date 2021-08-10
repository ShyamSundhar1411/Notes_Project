from django import forms
from django.contrib.auth.models import User
from . models import Note,Profile
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name']
class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(label= ('Avatar'),required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = Profile
        fields = ['avatar','gender']
