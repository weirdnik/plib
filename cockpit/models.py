from django.db import models
from profile.models import User
from django.forms import ModelForm

# Create your models here.

class Status (models.Model):

  date = models.DateTimeField (auto_now_add=True)
  owner = models.ForeignKey (User, related_name="sender_set")
  recipient = models.ForeignKey (User, related_name="recipient_set")
  private = models.BooleanField ()
  text = models.TextField ()
  image = models.ImageField(upload_to="images/%s.%N")
  
class StatusForm (ModelForm):
  class Meta:
    model = Status

class Tag (models.Model):

  tag = models.TextField ()
  status = models.ManyToManyField (Status)
  
class Like (models.Model):

  user = models.OneToOneField (User)
  status = models.ManyToManyField (Status)