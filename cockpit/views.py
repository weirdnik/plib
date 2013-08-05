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

from models import Status, StatusForm, Tag, Like, TAG_RE, MESSAGE_RE, MENTION_RE, STATUS_RE
from profile.models import User

###

def feed_lookup (user, profile, private):
  ''' This is the core function of the service. It takes logged user's profile,
  current displayed user's profile, and private [?] parameter.
  '''
  following = user.watches.all()
  if private:
    result = Status.objects.filter(
      ( Q(owner__exact=user)| Q(recipient__exact=user) ) | # all msgs between displayed and own
       ( Q(owner__in=following) & Q(recipient__exact=None)) | # all followed public statuses
       (Q(owner__exact=profile) | Q(recipient__exact=profile))
       ).order_by('-date')
  else:
     result = Status.objects.filter(
       ( Q(private__exact=False) & 
       ( Q(owner__exact=profile) | Q(recipient__exact=profile) ) ) |
       ( Q(private__exact=True) & 
       ( ( Q(owner__exact=profile) & Q(recipient__exact=user) ) | 
       ( Q(owner__exact=user) & Q(recipient__exact=profile) ) ) )
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
def feed (request, username=None, mobile=False, quote=None, reply=None, private=False):  

  user = get_object_or_404(User, user__id__exact=request.user.id) 
  follow = True
  profile = get_object_or_404 (User, user__username__exact=username) if username else user

  statuses = feed_lookup (user, profile, user==profile)
  last_id = statuses [0].id if statuses else '0'

  if mobile:
    if profile in user.watches.all():
      follow=False
    template = loader.get_template("mobile.html")
    if quote:
      text = '%s ' % reverse('cockpit.views.status', kwargs=dict(object_id=quote))
      form = StatusForm(initial=dict(text=text))
    elif reply:
      if private:
        text = '>>%s: ' % reply
      else:
        text = '>%s: ' % reply      
      form = StatusForm(initial=dict(text=text))    
    else:
      form = StatusForm()
  else:
    template = loader.get_template("feed.html")
    form = None
  return HTTPResponse (template.render(RequestContext(request,
    dict(feed=statuses, profile=profile, form=form, follow=follow, last_id=last_id,
      javascripts=('enter', 'refresh')))))
 
 
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
    
    if request.user in (status.owner.user, 
      status.recipient.user if status.recipient else None):      
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
        
        # message detection
        
        msg = MESSAGE_RE.match(status.text)
        
        if msg:
          recipient = get_object_or_404(DjangoUser, username=msg.groupdict()['recipient'])
          status.recipient = get_object_or_404(User, user=recipient)
          if status.text[1] == '>':
            status.private = True
            
        # tag assignment
        tag_result = TAG_RE.findall(status.text)
        status.tagged = True if tag_result else False
        status.save()        
          
        if status.tagged:
          for tag_text in tag_result:    
            tag, create = Tag.objects.get_or_create(tag=tag_text)
            tag.status.add(status)
            tag.save()          
        
        # mention notification       
        mention_result = MENTION_RE.findall(status.text)
        if mention_result:
          for u in mention_result:
            recipient = User.objects.get(user__username__exact=u)
            action = Status(owner=profile, recipient=recipient, action='mention',
              text=reverse('cockpit.views.status', kwargs=dict(object_id=status.id)))
            action.save()

        # quote notification
        quote_result = STATUS_RE.findall(status.text)        
        for q in quote_result:
          action = Status (owner=profile, recipient=Status.objects.get(pk=q[1]).owner, action='quote', 
            text=reverse('cockpit.views.status', kwargs=dict(object_id=status.id)))
          action.save()
          
      else:
        HTTPResponseBadRequest()
      if mobile:
        return HTTPResponseRedirect(reverse('mobile_dashboard'))      
      else:
        return HTTPResponseRedirect(reverse('cockpit.views.main'))
      
  else:
    return HTTPResponseBadRequest()

def tag(request, text):
  tag_object = get_object_or_404(Tag, tag=text)
  
  statuses = tag_object.status.all().order_by('-date')
  
  template = loader.get_template("feed.html")
  
  return HTTPResponse (template.render(RequestContext(request, dict(feed=statuses))))


@login_required
def like (request, object_id, mobile=False):

  if request.method == 'POST':
    
    user =  get_object_or_404(User, user__id__exact=request.user.id)  
    status =  get_object_or_404(Status, id=object_id)      

    likes, create = Like.objects.get_or_create(user=user)
#    if status not in likes.status.all():
    if True:
      likes.status.add(status)
      likes.save()
    
      action = Status(owner=user, recipient=status.owner, action='like', 
        text=reverse('cockpit.views.status', kwargs=dict(object_id=status.id)))      
      action.save()

    return HTTPResponseRedirect (reverse('mobile_dashboard'))
  else:
    return HTTPResponseNotAllowed ()

@login_required
def unlike (request, object_id, mobile=False):

  if request.method == 'POST':
    
    user =  get_object_or_404(User, user__id__exact=request.user.id)  
    status =  get_object_or_404(Status, id=object_id)      
    
    likes, create = Like.objects.get_or_create(user=user)
    if status in likes.status.all():
      likes.status.remove(status)
      likes.save()
    
#      action = Status(owner=user, recipient=status.owner, action='unlike')
#      action.save()

    return HTTPResponseRedirect (reverse('mobile_dashboard'))
  else:
    return HTTPResponseNotAllowed ()

@login_required
def delete (request, object_id, mobile=False):

  if request.method == 'POST':
    
    user =  get_object_or_404(User, user__id__exact=request.user.id)  
    status =  get_object_or_404(Status, id=object_id)
    
    if user == status.owner or user == status.recipient:
      status.delete()
      return HTTPResponseRedirect (reverse('mobile_dashboard'))
    else:
      return HTTPResponseNotAllowed ()      
  else:
    return HTTPResponseBadRequest()
    
@login_required
def feed_count_since (request, object_id, username=None, private=False):

  user = get_object_or_404(User, user__id__exact=request.user.id) 
  profile = get_object_or_404 (User, user__username__exact=username) if username else user


  if request.method == 'GET':
    query = feed_lookup(user, profile, private)
    try:
      status = Status.objects.get(pk=object_id)
      result = query.filter(date__gt=status.date)
    except Status.DoesNotExist:
      result = query.filter(id__gt=object_id)
    return HTTPResponse(result.count())
  
  return HTTPResponseBadRequest()