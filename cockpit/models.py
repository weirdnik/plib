# /usr/bin/env python
# -*- coding: utf-8 -*-

import re, os

from django.core.urlresolvers import reverse
from django.db import models
from django.forms import ModelForm, Textarea

# constants

STATUS_LENGTH = 160

# RE-s

TAG_RE = re.compile(ur'(?:\s|\A)#(?P<tag>\w+)', re.UNICODE)
MENTION_RE = re.compile('\^(?P<username>\w+)')

YOUTUBE_RE = re.compile ('https?://(www.)?(youtu.be/|youtube.com/watch(?:feature=player_embedded&)\?v=)(?P<video>[\w\d-]+)')
VIMEO_RE = re.compile ('https?://(www.)?vimeo.com/(?P<video>[\w\d]+)')
INSTAGRAM_RE = re.compile('https?://instagram.com/p/(?P<image>[\w\d]+)/?')

# the URL clause finds urls not preceded by iframe call to not fuck embeds - FUGLY

PROCESS_RE = re.compile('(?P<YT>https?://(www.)?(youtu.be/|youtube.com/watch(?:feature=player_embedded&)\?v=)(?P<YT_id>[\w\d-]+))|(?P<Vimeo>https?://(www.)?vimeo.com/(?P<V_ID>[\w\d]+))|(?P<Instagram>https?://instagram.com/p/(?P<I_ID>[\w\d]+)/?)|(?<!(<iframe src=")|(t="270" src="))(?P<url>https?://[\w-]+(\.[\w-]+)*(/[\w\?=,.\-%&;]*)*)')

MESSAGE_RE = re.compile('^(\>|&gt;)(\>|&gt;)?(?P<recipient>\w+):?')
MSG_PREFIX_RE = re.compile('^\>')
STATUS_RE = re.compile(ur'(?P<space>\s|\A)(?:https?://(?:plum\.me|plib\.hell\.pl))?(?P<status>/s(?:tatus)?/(?P<object_id>\d+)/?)')
APO_RE = re.compile(ur'(&#39;)')
URL_RE = None



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
  preview = models.ImageField(upload_to="images/%s", blank=True, null=True)
  icon = models.ImageField(upload_to="images/%s", blank=True, null=True)
  action = models.CharField (max_length=16, choices=(('like', 'like'), 
    ('follow', u'dodał/a cię do obserwowanych'), 
    ('unfollow', u'przestał/a cię obserwować'),
    ('mention', u'mówi o tobie'),
    ('quote', u'cytuje cię'),
    ('watch', 'subskrybuje tag'),
    ('unwatch', 'już nie subskrybuje tagu' )), blank=True, null=True)
  likes = models.ManyToManyField ('profile.User', through='Like')
#  blip = models.ForeignKey('blip.Info', null=True)


  class Meta:
    app_label = 'cockpit'  
    

  def num_likes (self):
    'number of likes on the status'
    
    # .distinct().count()
#    return 0   
    return Like.objects.filter(status__exact=self)
    

  def liking (self):
    'list of users that like this status'

    l = self.likes()
    return [ f.user.user.username for f in l ] if l else []

  def show(self):
    '''Wrapper method to make simplified render(simple=True) avaliable in templates.'''
    return self.render(simple=True)
    
  def render (self, simple=False):
  
    '''rendering of status' text to displayable HTML, it involves
    * interpretation of status' action and presentation with appropriate text or
 
    * mention and quote parsing and presentation
    * hashtags parsing and presentation
    * embedded media URL-s parsing and presentation
    '''

    ### utility functions
      
    def user_cockpit(user, view='mobile_user'):
      template = '<a href="%s">^%s</a>'
      cockpit = reverse(view, kwargs=dict(username=user.user.username))
      return template % ( cockpit, user.user.username)

    def insert_embeds (result):
      'run the status text through embeds parsing'
      
      EMBEDS = ( 
        ( YOUTUBE_RE, 
          lambda g: ' <img src="/static/img/movie.png" />' if simple else '<br /><iframe width="480" height="270" src="http://www.youtube.com/embed/%s" frameborder="0" allowfullscreen></iframe>' % g.groupdict()['video'] ),
        ( VIMEO_RE, 
          lambda g: ' <img src="/static/img/movie.png" />' if simple else '<br /><iframe src="http://player.vimeo.com/video/%s" width="480" height="270" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>' % g.groupdict()['video'] ),
        ( INSTAGRAM_RE, 
          lambda g: ' <img src="/static/img/movie.png" />' if simple else '<br /><iframe src="//instagram.com/p/%s/embed/" width="612" height="710" frameborder="0" scrolling="no" allowtransparency="true"></iframe>' % g.groupdict()['image'] ),
      )

      for e in EMBEDS:
       result = e[0].sub(e[1], result)
      
      return result

    def clickable_url(text):
      match = PROCESS_RE.search(text)
      if match:
        url = match.groupdict().get('url')
        if url:
          result = text.replace(url, '<a href="%s" target="_blank">%s</a>' % ( url, url ) )
          return result    
      return text

    def tag_cockpit(text, view='cockpit.views.tag'):
      template = '<a href="%s">%s</a>'
      cockpit = reverse(view, kwargs=dict(text=text))
      return template % (cockpit, text)
      
    
    ###
                   
    
    if self.action == 'follow':
      result = u'%s obserwuje %s' % (user_cockpit(self.recipient),
        user_cockpit(self.owner)) 
    elif self.action == 'unfollow':
      result = u'%s już nie obserwuje %s' % (user_cockpit(self.recipient),
        user_cockpit(self.owner))
    elif self.action == 'like':
      match = STATUS_RE.match(self.text) if self.text else None        
      if match:
        status_id = match.groupdict().get('object_id')
        try:
          status = Status.objects.get(pk=status_id)
          result = u'%s lubi <a href="%s" title="%s" >status</a> %s' % ( user_cockpit(self.owner),
            reverse('cockpit.views.status', kwargs=dict(object_id=status_id)),
            status.text,
            user_cockpit(self.recipient))        
        except Status.DoesNotExist:
          result = u'%s lubi [usunięty]' % user_cockpit(self.owner)
      else:
        result = u'%s lubi status %s' % ( user_cockpit(self.owner),
          user_cockpit(self.recipient))        
    elif self.action == 'watch':
      result = '%s subskrybuje tag #%s' % (self.owner.cockpit(), tag_cockpit(self.text))
      
    # mention & quoting
    elif self.action in ('mention', 'quote'):    
      u = self.owner.user.username
      d = dict( user=user_cockpit (self.owner),
        username=u,
        profile=user_cockpit (self.recipient),
        url=self.text)

      if self.action == 'mention':
        result = u'%(user)s mówi o %(profile)s: <a href="%(url)s">[^%(username)s]</a>' % d
      else:
        result = u'%(user)s cytuje %(profile)s: <a href="%(url)s">[^%(username)s]</a>' % d      

      # WARNING: depends on status.text format, which depends on urls.py
      object_id = int(self.text.strip('/').split('/')[-1])
      try:
        msg = Status.objects.get(pk=object_id)
      except Status.DoesNotExist:
        msg = None
      if msg: 
        result = result + ': %s <a href="%s">[cytuj]</a> <a href="%s">[odpowiedz]</a>' % ( msg.render(),
          reverse('mobile_dashboard', kwargs=dict(mobile=True, quote=object_id)),
          reverse('reply_dashboard', kwargs=dict(mobile=True, reply=msg.owner.user.username)))

    else:
      # size limit
      
      text = self.text[:STATUS_LENGTH] if len(self.text) > STATUS_LENGTH else self.text
      result = APO_RE.sub("'", text)

      # replacing http://.../status links with /status links
      # FUCK THIS SHIT    

#      result = STATUS_RE.sub(lambda g: u'%(space)s/status/%(object_id)s/' % g.groupdict(), result)
      
#      print result
# dict(url=reverse('cockpit.views.status', 
#                                                                             kwargs=dict(object_id=g.groupdict().get('object_id')))),
#                                                                 space=g.groupdict().get('space','')),
 #                            result)
    
      # go on with processing               

#      result = STATUS_RE.sub( lambda g: u'%(space)sxt)s" href="%(url)s">[%(user)s]</a>' % dict(text=Status.objects.get(pk=g.groupdict()['object_id']).text,
#        url=reverse('cockpit.views.status', kwargs=dict(object_id=g.groupdict()['object_id'])),
#        user=Status.objects.get(pk=g.groupdict()['object_id']).owner.user.username,
#        space=g.groupdict().get('space','')), result)

      # mentions 
          
      result = MENTION_RE.sub ( lambda g: u'<a href="%s" target="_top">%s</a>' % (reverse('cockpit.views.main',
        kwargs=dict(username=g.group().strip('^'))), g.group()), result)

      # message prefix display mangling        
      if self.recipient:
        result = MESSAGE_RE.sub ( u'> <a href="%s">%s</a>:' % (
          reverse('mobile_user',kwargs=dict(username=self.recipient.user.username)),
          self.recipient.user.username), 
          result)
        
        if self.private:
          result = MSG_PREFIX_RE.sub('&raquo;', result)
        else:
          result = MSG_PREFIX_RE.sub('&rsaquo;', result)
              
      # embedding stuff from other sites    
      
      result = insert_embeds(result)      
      result = clickable_url(result)      

      # quotes - AFTER EMBEDS      
      # TODO add flat_render for onmouseover display      
      result = STATUS_RE.sub( lambda g: u'%(space)s<a title="%(text)s" href="%(url)s">[%(user)s]</a>' % dict(text=Status.objects.get(pk=g.groupdict()['object_id']).text,
        url=reverse('cockpit.views.status', kwargs=dict(object_id=g.groupdict()['object_id'])),
        user=Status.objects.get(pk=g.groupdict()['object_id']).owner.user.username,
        space=g.groupdict().get('space','')), result)

      # clickable urls


      try:
        if simple:
          if self.image:
            result = result + ' <img src="/static/img/image.png" />'
        elif os.path.exists(self.image.path):
          path = self.image.url + '_preview.jpg'
#           '/'+'/'.join(path.split('/')[-5:]) # dirty hack, no time to fuck with django path handling        
          result = result + '<div class="status-image"><img src="%s" /></div>' % path
      except ValueError:
        pass 

      # hashtags detected
      if self.tagged:
        
        result = TAG_RE.sub ( lambda g: '<a target="_top" href="%s">%s</a>' % (reverse('cockpit.views.tag',
          kwargs=dict(text=g.group().strip().strip('#'))), g.group()), result)

      # image handling

    return result

  
class StatusForm (ModelForm):
  class Meta:
    model = Status
    fields = ['text', 'image']
    widgets = {
      'text': Textarea(attrs={'maxlength': 256, 'size': 160, 'cols': 80, 'rows': 2, 'onkeydown': 'pressed(event)'}),
    }

class Tag (models.Model):

  tag = models.TextField ()
  status = models.ManyToManyField (Status)

  class Meta:
    app_label = 'cockpit'    
    
class Like (models.Model):

  status = models.ForeignKey ('cockpit.Status', null=True)
  user = models.ForeignKey ('profile.User', null=False)
  date = models.DateTimeField (auto_now_add=True,null=True)

  class Meta:
    app_label = 'cockpit'    
