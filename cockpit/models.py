import re
from django.core.urlresolvers import reverse

from django.db import models
from profile.models import User
from django.forms import ModelForm

#

TAG_RE = re.compile('#(?P<tag>\w+)')
MENTION_RE = re.compile('^(?P<username>\w+)')

# Create your models here.

class Status (models.Model):

  date = models.DateTimeField (auto_now_add=True)
  owner = models.ForeignKey (User, related_name="sender_set")
  recipient = models.ForeignKey (User, related_name="recipient_set", blank=True, null=True)
  private = models.BooleanField (default=False)
  tagged = models.BooleanField (default=True)
  text = models.TextField (blank=False)
  image = models.ImageField(upload_to="images/%s.%N", blank=True)
  
#  event  

  def render (self):

    result = MENTION_RE.sub( lambda g: '<a href="%s">%s</a>' % (reverse('cockpit.views.main', kwargs=dict(username=g.group().strip('^'))), g.group().strip('^')), self.text))
  
    if self.tagged:

      result = TAG_RE.sub ( lambda g: '<a href="%s">%s</a>' % (reverse('cockpit.views.tag', kwargs=dict(tag=g.group().strip('#'))) ,g.group()),  s))    

      return result

  
class StatusForm (ModelForm):
  class Meta:
    model = Status
    fields = ['text', 'image']


class Tag (models.Model):

  tag = models.TextField ()
  status = models.ManyToManyField (Status)
  

class Like (models.Model):

  user = models.OneToOneField (User)
  status = models.ManyToManyField (Status)