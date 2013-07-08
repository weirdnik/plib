# Create your views here.
# -*- coding: iso-8859-2 -*-

import re

from PIL import Image

from django.db.models import Q
from django.http import HttpResponse as HTTPResponse
from django.http import HttpResponseRedirect as HTTPResponseRedirect
from django.http import HttpResponseGone as HTTPResponseGone
from django.http import HttpResponseBadRequest as HTTPResponseBadRequest
from django.http import HttpResponseNotAllowed as HTTPResponseNotAllowed
from django.http import HttpResponseForbidden as HTTPResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template import RequestContext, loader, Template
from django.contrib.auth.models import User as DjangoUser
from django.db.models.signals import post_save

from models import Status, StatusForm, Tag, TAG_RE
from profile.models import User

MESSAGE_RE = re.compile('^>>?(?P<recipient>\w+)')
MENTION_RE = re.compile('\^(?P<nickname>\w+)')

###

def feed_lookup (user, profile, private):
  ''' This is the core function of the service. It takes logged user's profile,
  current displayed user's profile, and private [?] parameter.
  '''
  following = user.watches.all()
  if private:
    result = Status.objects.filter(
      (Q(owner__in=following) & Q(recipient__exact=None)) |
      Q(owner__exact=profile) | Q(recipient__exact=profile)).order_by('-date')      
  else:
     result = Status.objects.filter(
       ( Q(owner__exact=user)| Q(recipient__exact=user) ) | # all msgs between displayed and own
       ( ( Q(owner__in=following) & Q(private__exact=False) ) & Q(recipient__exact=None) )| # all followed public statuses
       ( (Q(owner__exact=profile) | Q(recipient__exact=profile)) & Q(private__exact=False) )
       ).order_by('-date')
 
  return result

###
@login_required
def main (request, username=None):

  'main cockpit view for logged in user'
  
  user = get_object_or_404(DjangoUser, pk=request.user.id)	
  user_profile = get_object_or_404 (User, user__exact=user)
  profile = get_object_or_404 (User, user__username__exact=username) if username else user_profile
  
  # profile - the profile displayed
  # user - the logged user's profile
   
  template = loader.get_template('cockpit.html')
  result = dict(profile=profile, form=StatusForm())
  
  following = user_profile.watches.all()

  if username:    
    result['statuses'] = feed_lookup (user_profile, profile, False)

    if profile in following:
      result['follow'] = False
      result['unfollow'] = True
    else:
      result['follow'] = True
      result['unfollow'] = False
  else: # profile = user
    statuses = feed_lookup (user_profile, profile, True)
  
    result['statuses'] = statuses
    result['watch'] = False
    result['profile'] = profile
  context = RequestContext (request, result)
  return HTTPResponse (template.render(context))


@login_required
def feed (request, username=None, mobile=False):  

  user = get_object_or_404(User, user__id__exact=request.user.id) 
  follow = True
#  if username: 
#    profile = get_object_or_404(User, user__username__exact=username)
#  else:
#    profile = user  ## FIXME
#  user = get_object_or_404(DjangoUser, pk=request.user.id)
#  user_profile = get_object_or_404 (User, user__exact=user)

  profile = get_object_or_404 (User, user__username__exact=username) if username else user

  statuses = feed_lookup (user, profile, user==profile)  
  if mobile:
    if profile in user.watches.all():
      follow=False
    template = loader.get_template("mobile.html")
    form = StatusForm()
  else:
    template = loader.get_template("feed.html")
    form = None
  return HTTPResponse (template.render(RequestContext(request,
     dict(feed=statuses, profile=profile, form=form, javascripts=('enter',), follow=follow))))
 
 
@login_required  
def status (request, object_id=None, mobile=False):

  def process_image(**kwargs):
    instance = kwargs.get('instance', None)
    if kwargs.get('created', False):
      if instance:
        if instance.image:
          image = Image.open(instance.image.path)
          image.thumbnail((640,480), Image.ANTIALIAS)
#        icon = image.thumbnail((256,256), Image.ANTIALIAS)
          image.save(instance.image.path + '_preview' + '.jpg', 'JPEG')
#        icon.save(instance.image.path + '.preview.', 'JPEG')
        
  post_save.connect(process_image, sender=Status)
  
  user = get_object_or_404(DjangoUser, pk=request.user.id)
  profile = get_object_or_404 (User, user__exact=user)
  
  if request.method == 'GET':
    if not object_id:
      return HTTPResponseNotAllowed ()
      
    status = get_object_or_404 (Status, pk=object_id)
    
    if request.user in (status.owner.user, status.recipient.user):
      
      return HTTPResponse (status)
    else:
      return HTTPResponseForbidden () 
     
  elif request.method == 'POST':
    if object_id:
      return HTTPResponseNotAllowed ()
    else:
    
      form = StatusForm (request.POST, request.FILES)
      if form.is_valid():
        status=form.save(commit=False)
        status.owner=profile

        #ESCAPE CONTENT - CRITICAL  XXX
        
        # tag assignment
        
        msg = MESSAGE_RE.match(status.text)
        
        if msg:
          recipient = get_object_or_404(DjangoUser, username=msg.groupdict()['recipient'])
          status.recipient = get_object_or_404(User, user=recipient)
          if status.text[1] == '>':
            status.private = True
        status.save()
        
        tag_result = TAG_RE.search(status.text)
        if tag_result:
          status.tagged = True
          tag_text = tag_result.group().strip('#').strip()
          
          tag, create = Tag.objects.get_or_create(tag__exact=tag_text)
          tag.status.add(status)
          tag.save()          
        else:
          status.tagged = True            
        
      else:
        HTTPResponseBadRequest()
      if mobile:
        return HTTPResponseRedirect(reverse('mobile_dashboard'))      
      else:
        return HTTPResponseRedirect(reverse('cockpit.views.main'))
      
  else:
    return HTTPResponseBadRequest()

def tag(request, text):
  tag_object = get_object_or_404(Tag, tag__exact=text)
  
  statuses = tag_object.status.all().order_by('-date')
  
  template = loader.get_template("tag.html")
  
  return HTTPResponse (RequestContext(request, dict(feed=statuses)))
