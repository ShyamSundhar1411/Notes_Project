from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save
from ckeditor_uploader.fields import RichTextUploadingField
from autoslug import AutoSlugField
import uuid

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
class Profile(models.Model):
    GENDER = [
        ('None', 'None'),
        ('Male', 'Male'),
        ('Female', 'Female')
    ]
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    avatar = models.ImageField(blank = True,upload_to = 'avatars/')
    gender = models.CharField(blank = True,max_length = 6, choices = GENDER, default = 'None')
    slug = models.SlugField(blank = True,unique= True)
    
    def __str__(self):
        return self.user.username
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(uuid.uuid4())
        super(Profile,self).save(*args,**kwargs)
@receiver(post_save,sender = User)
def create_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user = instance)
        instance.profile.save()
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()