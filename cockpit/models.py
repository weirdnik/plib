#

import re, os

from django.core.urlresolvers import reverse
from django.db import models
from plib.profile.models import User
from django.forms import ModelForm, Textarea

#

TAG_RE = re.compile('#(?P<tag>\w+)')
MENTION_RE = re.compile('\^(?P<username>\w+)')
YOUTUBE_RE = re.compile ('http://(www.)?youtube.com/watch\?v=(?P<video>[\w\d-]+)')

VIMEO_RE = re.compile ('https?://(www.)?vimeo.com/(?P<video>[\w\d]+)')

# Create your models here.

class Status (models.Model):

  date = models.DateTimeField (auto_now_add=True)
  owner = models.ForeignKey (User, related_name="sender_set")
  recipient = models.ForeignKey (User, related_name="recipient_set", blank=True, null=True)
  private = models.BooleanField (default=False)
  tagged = models.BooleanField (default=True)
  text = models.TextField (blank=False)
  image = models.ImageField(upload_to="upload/images/%s.%N", blank=True)
  tags_watched = models.ManyToManyField (aTag)
  tags_ignored = models.ManyToManyField (Tag)
  ignored = models.ManyToManyField (User)
  image = models.ImageField(upload_to="upload/images/%s.%N", blank=True, height_field='image_height', width_field='image_width')  
  image_height = models.IntegerField(blank=True)
  image_width = models.IntegerField(blank=True)  
  preview = models.ImageField(upload_to="images/%s.%N", blank=True)
  icon = models.ImageField(upload_to="images/%s.%N", blank=True)
  action = models.CharField (max_length=16, choices=(('like', 'like'), ))

  def render (self):

    result = MENTION_RE.sub( lambda g: '<a href="%s" target="_top">%s</a>' % (reverse('cockpit.views.main', kwargs=dict(username=g.group().strip('^'))), g.group()), self.text)

    # embedding stuff from other sites
    
    result = YOUTUBE_RE.sub ( lambda g: '<iframe width="480" height="270" src="http://www.youtube.com/embed/%s" frameborder="0" allowfullscreen></iframe>' % g.groupdict()['video'], result )
    result = VIMEO_RE.sub  ( lambda g: '<iframe src="http://player.vimeo.com/video/%s" width="480" height="270" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>' % g.groupdict()['video'], result)

    if self.tagged:

      result = TAG_RE.sub ( lambda g: '<a target="_top" href="%s">%s</a>' % (reverse('cockpit.views.tag', kwargs=dict(tag=g.group().strip('#'))) ,g.group()), result)

    # TODO private messages marking

    if self.image:
      if os.path.exists(self.image.path):
        path = self.image.url + '_preview.jpg'
#        '/'+'/'.join(path.split('/')[-5:]) # dirty hack, no time to fuck with django path handling
        
        result = result + '<div class="status-image"><img src="%s"></div>' % path

    return result

  
class StatusForm (ModelForm):
  class Meta:
    model = Status
    fields = ['text', 'image']
    widgets = {
      'text': Textarea(attrs={'cols': 60, 'rows': 2}),
    }

class Tag (models.Model):

  tag = models.TextField ()
  status = models.ManyToManyField (Status)
  

class Like (models.Model):

  user = models.OneToOneField (User)
  status = models.ManyToManyField (Status)