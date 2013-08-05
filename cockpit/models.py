# /usr/bin/env python
# -*- coding: utf-8 -*-

import re, os

from django.core.urlresolvers import reverse
from django.db import models
from django.forms import ModelForm, Textarea

# RE-s

TAG_RE = re.compile('#(?P<tag>\w+)')
MENTION_RE = re.compile('\^(?P<username>\w+)')
YOUTUBE_RE = re.compile ('https?://(www.)?youtube.com/watch\?v=(?P<video>[\w\d-]+)')
VIMEO_RE = re.compile ('https?://(www.)?vimeo.com/(?P<video>[\w\d]+)')
INSTAGRAM_RE = re.compile('https?://instagram.com/p/(?P<image>[\w\d]+)/?')
MESSAGE_RE = re.compile('^\>\>?(?P<recipient>\w+):?')
MSG_PREFIX_RE = re.compile('^\>')
STATUS_RE = re.compile('(?P<status>/status/(?P<object_id>\d+)/?)')

# Create your models here.

class Status (models.Model):

  date = models.DateTimeField (auto_now_add=True)
  owner = models.ForeignKey ('profile.User', related_name="sender_set")
  recipient = models.ForeignKey ('profile.User', related_name="recipient_set",
    blank=True, null=True)
  private = models.BooleanField (default=False)
#  visible = models.BooleanField (default=False)  
  tagged = models.BooleanField (default=False)
  text = models.TextField (blank=True, null=True, help_text=None)
  image = models.ImageField(upload_to="upload/images/%s.%N", blank=True, null=True,
     height_field='image_height', width_field='image_width')  
  image_height = models.IntegerField(blank=True, null=True)
  image_width = models.IntegerField(blank=True, null=True)  
  preview = models.ImageField(upload_to="images/%s.%N", blank=True, null=True)
  icon = models.ImageField(upload_to="images/%s.%N", blank=True, null=True)
  action = models.CharField (max_length=16, choices=(('like', 'like'), 
   ('follow', u'dodał/a Cię do obserwowanych'), 
   ('unfollow', u'przestal/a cie obserwować'),
   ('mention', u'o Tobie mówi'),
   ('quote', u'Cię cytuje') ), blank=True, null=True)


  def likes (self):
    # .distinct().count()
    
    return Like.objects.filter(status__exact=self)
    

  def liking (self):

    l = self.likes()
    return [ f.user.user.username for f in l ] if l else []
    
    
  def render (self):
    '''rendering of status' text to displayable HTML, it involves
 * interpretation of status' action and presentation with appropriate text or
 
 * mention and quote parsing and presentation
 * hashtags parsing and presentation
 * embedded media URL-s parsing and presentation
    '''  
    def user_cockpit(user, view='mobile_user'):
      template = '<a href="%s">^%s</a>'
      cockpit = reverse(view, kwargs=dict(username=user.user.username))
      return template % ( cockpit, user.user.username)
      

    def insert_embeds (result):
      'run the status text through embeds parsing'
      
      EMBEDS = ( 
        ( YOUTUBE_RE, 
          lambda g: '<iframe width="480" height="270" src="http://www.youtube.com/embed/%s" frameborder="0" allowfullscreen></iframe>' % g.groupdict()['video'] ),
        ( VIMEO_RE, 
          lambda g: '<iframe src="http://player.vimeo.com/video/%s" width="480" height="270" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>' % g.groupdict()['video'] ),
        ( INSTAGRAM_RE, 
          lambda g: '<iframe src="//instagram.com/p/%s/embed/" width="612" height="710" frameborder="0" scrolling="no" allowtransparency="true"></iframe>' % g.groupdict()['image'] ),
      )

      for e in EMBEDS:
       result = e[0].sub(e[1], result)
      
      return result

                   
    if self.action == 'follow':
      result = u'%s zaczął obserwować %s' % (user_cockpit(self.recipient),
        user_cockpit(self.owner)) 
    elif self.action == 'unfollow':
      result = u'%s już nie obserwuje %s' % (user_cockpit(self.recipient),
        user_cockpit(self.owner))
    elif self.action == 'like':
      match = STATUS_RE.match(self.text).groups() if self.text else None        
      if match:
        status_id = match[1]
        status = Status.objects.get(pk=status_id)
        result = u'%s lubi <a href="%s" title="%s" >status</a> %s' % ( user_cockpit(self.owner),
          reverse('cockpit.views.status', kwargs=dict(object_id=status_id)),
          status.text,
          user_cockpit(self.recipient))        
      else:
        result = u'%s lubi status %s' % ( user_cockpit(self.owner),
          user_cockpit(self.recipient))        

    # mention & quoting
    elif self.action in ('mention', 'quote'):    
      u = self.owner.user.username
      d = dict(user=u, 
        profile=reverse('mobile_user', kwargs=dict(username=u, mobile=True)), 
        url=self.text)
      if self.action == 'mention':
        result = u'<a href="%(profile)s">^%(user)s</a> o Tobie mówi: <a href="%(url)s">[^%(user)s]</a>' % d
      else:
        result = u'<a href="%(profile)s">^%(user)s</a> Cię cytuje: <a href="%(url)s">[^%(user)s]</a>' % d      

      # WARNING: depends on status.text format, which depends on urls.py
      object_id = int(self.text.strip('/').split('/')[-1])
      msg = Status.objects.get(pk=object_id)
      if msg: 
        result = result + ': %s <a href="%s">[cytuj]</a> <a href="%s">[odpowiedz]</a>' % ( msg.render(),
          reverse('mobile_dashboard', kwargs=dict(mobile=True, quote=object_id)),
          reverse('mobile_dashboard', kwargs=dict(mobile=True, reply=msg.owner.user.username)))
    else:
      # mentions and quotes
      result = MENTION_RE.sub ( lambda g: u'<a href="%s" target="_top">%s</a>' % (reverse('cockpit.views.main',
        kwargs=dict(username=g.group().strip('^'))), g.group()), self.text)
      # TODO add flat_render for onmouseover display
      result = STATUS_RE.sub( lambda g: u'<a title="%s" href="%s">[%s]</a>' % (Status.objects.get(pk=g.groupdict()['object_id']).text,
        reverse('cockpit.views.status', kwargs=dict(object_id=g.groupdict()['object_id'])),
        Status.objects.get(pk=g.groupdict()['object_id']).owner.user.username),
        result)

      # message prefix display mangling        
      if self.recipient:
        result = MESSAGE_RE.sub ( u'> <a href="%s" target="_top">%s</a>:' % ( reverse('cockpit.views.main',
          kwargs=dict(username=self.recipient)), self.recipient), result)
        if self.private:
          result = MSG_PREFIX_RE.sub('&raquo;', result)
        else:
          result = MSG_PREFIX_RE.sub('&rsaquo;', result)
              
      # embedding stuff from other sites    
      result = insert_embeds(result)

      # hashtags detected
      if self.tagged:
        result = TAG_RE.sub ( lambda g: '<a target="_top" href="%s">%s</a>' % (reverse('cockpit.views.tag', kwargs=dict(text=g.group().strip('#'))) ,g.group()), result)

      # image handling
      if self.image:
        if os.path.exists(self.image.path):
          path = self.image.url + '_preview.jpg'
#         '/'+'/'.join(path.split('/')[-5:]) # dirty hack, no time to fuck with django path handling        
          result = result + '<div class="status-image"><img src="%s" /></div>' % path

    return result

  
class StatusForm (ModelForm):
  class Meta:
    model = Status
    fields = ['text', 'image']
    widgets = {
      'text': Textarea(attrs={'cols': 60, 'rows': 2, 'onkeydown': 'pressed(event)'}),
    }


class Tag (models.Model):

  tag = models.TextField ()
  status = models.ManyToManyField (Status)


class Like (models.Model):

  user = models.OneToOneField ('profile.User')
  status = models.ManyToManyField (Status)
