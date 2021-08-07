from django.db import models
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField
from autoslug import AutoSlugField

# Create your models here.
class Note(models.Model):
    title = models.CharField(max_length = 200)
    subject = models.CharField(max_length = 200)
    notes = RichTextUploadingField()
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    updated_on = models.DateField(auto_now = True)
    slug = AutoSlugField(populate_from = "title",unique=True,blank = True,editable = True)

    def __str__(self):
        return self.title
