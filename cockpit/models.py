from django.db import models
from profile.models import User

# Create your models here.

class Status (models.Model):

  owner = models.ForeignKey (User, related_name="sender_set")
  recipient = models.ForeignKey (User, related_name="recipient_set")
  private = models.BooleanField ()
  text = models.TextField ()
  image = models.ImageField(upload_to="images/%s.%N")
  
class Tag (models.Model):

  tag = models.TextField ()
  status = models.ManyToManyField (Status)
  
class Like (models.Model):

  user = models.OneToOneField (User)
  status = models.ManyToManyField (Status)