#
# -*- coding: iso-8859-2 -*-
from django.db import models
from django.contrib.auth.models import User as AuthUser

# Create your models here.

class User (models.Model):
  '''
#  active     - konto aktywne - obsolete, auth to ma
#  name       - nazwa usera  -''-
  about      - opis
  icbm       - lokalizacja
  avatar     - obrazek awatara
  background - obrazek t�a
  phone      - nr telefonu
  private    - user prywatny (nie ma bliploga)
  watches    - obserwowanie
  '''
  
  user = models.OneToOneField (AuthUser, related_name='django_user_set')
#  active = models.BooleanField (default=False)
  love = models.BooleanField (default=False)
  premium = models.BooleanField (default=False)
  official = models.BooleanField (default=False)
  slug = models.SlugField ()
  name = models.TextField ()
  about = models.TextField ()
  icbm = models.TextField ()
  sex = models.CharField(max_length=1, choices=(('m','m'), ('f', 'f'), ('o','o'), ('n','n/a')))
  avatar = models.ImageField(upload_to="avatars/%s", blank=True)
  background = models.ImageField (upload_to="backgrounds/%s", blank=True)
  phone = models.TextField ()
  private = models.BooleanField (default=False)
  watches = models.ManyToManyField ('User', related_name='user_watches_set', blank=True)
  ignores = models.ManyToManyField ('User', related_name='user_ignores_set', blank=True)  

  def __unicode__ (self):
  
    return self.user.username
