from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.contrib.auth.models import User
from . models import Note,Profile
class NoteCreationForm(forms.ModelForm):
    notes = forms.CharField(widget=CKEditorUploadingWidget)
    class Meta:
        model = Note
        fields = ['title','subject','notes']
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email')
class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(label= ('Avatar'),required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = Profile
        fields = ('avatar','gender')