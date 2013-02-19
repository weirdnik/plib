from django.db import models
from django.forms import ModelForm

from profile.models import User

# Create your models here.

class URL(models.Model):
  
  active = models.BooleanField(default=True)
  owner = models.ForeignKey(User)  
  url = models.URLField(verify_exists=True)   
  slug = models.SlugField(unique=True)
  public = models.BooleanField()
  description = models.TextField(blank=True)
  created = models.DateTimeField(auto_now_add=True)

class URLForm (ModelForm):
  class Meta:
    model = URL
    fields = ('url')
    
class Click (models.Model):

  date = models.DateTimeField(auto_now_add=True)
  ip = models.IPAddressField()
  info = models.TextField()
  user = models.ManyToManyField(User)


# TODO tags            