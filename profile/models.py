#
# -*- coding: iso-8859-2 -*-


from django.db import models
from django.forms import ModelForm
from django.contrib.auth.models import User as AuthUser
from django.core.urlresolvers import reverse

# Create your models here.

class User (models.Model):
  '''
  about      - opis
  icbm       - lokalizacja
  avatar     - obrazek awatara
  background - obrazek tla
  phone      - nr telefonu
  private    - user prywatny (nie ma bliploga)
  watches    - obserwowanie
  '''
  
  user = models.OneToOneField (AuthUser, related_name='django_user_set')
  love = models.BooleanField (default=False)
  premium = models.BooleanField (default=False)
  official = models.BooleanField (default=False)
  slug = models.SlugField (blank=True, null=True)
  name = models.TextField (blank=True, null=True)
  about = models.TextField (blank=True, null=True)
  icbm = models.TextField (blank=True, null=True)
  sex = models.CharField(max_length=1, 
                         choices=(('m','m'), 
                                  ('f', 'f'), 
                                  ('o','o'), ('n','nie dotyczy')),
                         default='o')
  avatar = models.ImageField(upload_to="avatars/%s", blank=True, null=True)
  background = models.ImageField (upload_to="backgrounds/%s",
                                  blank=True, null=True,
                                  height_field='background_height',
                                  width_field='background_width')
  background_height = models.IntegerField(blank=True, null=True)
  background_width = models.IntegerField(blank=True, null=True)
  phone = models.TextField (blank=True, null=True)
  private = models.BooleanField (default=False)
  watches = models.ManyToManyField ('User', related_name='watched_users_set',
                                    blank=True, null=True)
  ignores = models.ManyToManyField ('User', related_name='ignored_users_set',
                                    blank=True, null=True)  
  watches_tags = models.ManyToManyField ('cockpit.Tag', related_name='watched_tag_set',
                                         blank=True, null=True)
  ignores_tags = models.ManyToManyField ('cockpit.Tag', related_name='ignored_tag_set',
                                         blank=True, null=True)  
  
  def __unicode__ (self):
  
    return self.user.username
    
  def cockpit (self,view='mobile_user'):
    'returns HTML link to user cockpit'
        
    template = '<a href="%s">^%s</a>'
    cockpit = reverse(view, kwargs=dict(username=self.user.username))
    return template % ( cockpit, self.user.username)
                         

class UserForm (ModelForm):
  class Meta:
    model = User
    fields = ['name', 'about', 'icbm', 'sex', 'avatar', 'background']
          
