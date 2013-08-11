# -*- coding: utf-8 -*-

from django.db import models
from django.forms import ModelForm

# Create your models here.

class Blip (models.Model):
  user = models.ForeignKey('profile.User', null=False, blank=False)
  blip = models.TextField(null=False, blank=False)
  password = models.TextField(null=False, blank=False)
  imported = models.BooleanField (default=False)  

class Info (models.Model):
  type = models.TextField(null=False, blank=False)
  transport = models.TextField(null=False, blank=False)
  likes = models.IntegerField(default=0)
#  liked =   userzy

class BlipForm (ModelForm):
  class Meta:
    model = Blip
    fields = ['blip', 'password']
                        