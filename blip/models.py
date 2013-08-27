# -*- coding: utf-8 -*-

from django.db import models
from django.forms import ModelForm
from django.forms.widgets import TextInput, PasswordInput
# Create your models here.

class Blip (models.Model):
  user = models.ForeignKey('profile.User', null=False, blank=False)
  blip = models.CharField(max_length=64,null=False, blank=False, unique=True)
  password = models.TextField(null=False, blank=False)
  imported = models.BooleanField (default=False)  
  slug = models.SlugField(max_length=64,blank=True, null=True) # security slug
  class Meta:
    app_label = 'blip'


class Info (models.Model):
  status = models.ForeignKey('cockpit.Status')
  blip = models.IntegerField()
  type = models.TextField(null=False, blank=False)
  transport = models.TextField(null=False, blank=False)
  likes = models.IntegerField(default=0)
  liked = models.TextField(null=False, blank=False)    
  def __unicode__(self):
    return ':'.join([ str(i) for i in (self.id, self.blip, self.transport)])

  class Meta:
    app_label = 'blip'
      
#  liked =   userzy

class BlipForm (ModelForm):
  class Meta:
    model = Blip
    fields = ['blip', 'password']
    widgets = {
      'blip': TextInput, 
      'password': PasswordInput(attrs=dict(render_value=True))
    }