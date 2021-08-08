from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from . models import Note
class NoteCreationForm(forms.ModelForm):
    notes = forms.CharField(widget=CKEditorUploadingWidget)
    class Meta:
        model = Note
        fields = ['title','subject','notes']