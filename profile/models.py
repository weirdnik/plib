from django.db import models
from django.contrib.auth.models import User as AuthUser

# Create your models here.

class User (models.Model):

  user = models.OneToOneField (AuthUser, related_name='django_user_set')
  active = models.BooleanField (default=False)  
  name = models.TextField()
  about = models.TextField()
  icbm = models.TextField()
  avatar = models.ImageField(upload_to="avatars/%s", blank=True)
  background = models.ImageField (upload_to="backgrounds/%s", blank=True)
  phone = models.TextField ()
  private = models.BooleanField (default = False)
  watches = models.ManyToManyField ('User', related_name='user_watches_set', blank=True)
#  sex

  def __unicode__ (self):
  
    return self.user.username