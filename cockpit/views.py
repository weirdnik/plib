# Create your views here.
# -*- coding: utf-8 -*-

import re
import logging 

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
from django.utils.html import escape
from django.http import Http404 as HTTP404

from models import Status, StatusForm, Tag, Like, TAG_RE, MESSAGE_RE, MENTION_RE, STATUS_RE, STATUS_LENGTH
from profile.models import User

###

MESSAGES = { '0': '',
             'IOImage': u'Nie można zamieścić statusu: niedobry obrazek.',
             'UEImage': u'Nie można zamieścić statusu: niedobra nazwa obrazka.',
             'TOOLarge': u'Zbyt duży status.',
             'TOOLong': u'Zbyt długi status.' }

###

def feed_lookup (user, profile, private):
  ''' This is the core function of the service. It takes logged user's profile,
  current displayed user's profile, and private [?] parameter.
  '''
  
  following = user.watches.all()
  tags_watched = user.watches_tags.all()
  tags_ignored = user.ignores_tags.all()
  
  tag_statuses = None
  for t in tags_watched:
    if tag_statuses:
      tag_statuses = tag_statuses | t.status.all()
    else:
      tag_statuses = t.status.all()
  
  if private:
    result = Status.objects.filter(
      ( Q(owner__exact=user)| Q(recipient__exact=user) ) | # all msgs between displayed and own
       ( Q(owner__in=following) & Q(recipient__exact=None) ) | # all followed public statuses
       ( Q(owner__exact=profile) | Q(recipient__exact=profile) )#| # mesgi do i od
#       ( Q) ) # tags subscribed 
       ).order_by('-date')
       
    if tag_statuses:
      result = result | tag_statuses
  else:
     result = Status.objects.filter(
       ( Q(private__exact=False) & 
       ( Q(owner__exact=profile) | Q(recipient__exact=profile) ) ) |
       ( Q(private__exact=True) & 
       ( ( Q(owner__exact=profile) & Q(recipient__exact=user) ) | 
       ( Q(owner__exact=user) & Q(recipient__exact=profile) ) ) )
       ).order_by('-date')
 
  return result.distinct()


def notify(recipient, message, sender='blip'):
 
   '''sends a private message from user blip to given user '''
   blip = get_object_or_404(User, user__username__exact=sender)      
   rcpt = get_object_or_404(User, user__username__exact=recipient)
   body = '>>%s %s' % (recipient, message)
   status = Status(owner=blip, recipient=rcpt, text=body, private=True)
   status.save()      
        
###
# views start here

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
def feed (request, username=None, mobile=False, quote=None, reply=None,
          private=False, slug=None, skip=0):  
  logging.basicConfig(filename='/var/log/plum/logfile', level=logging.INFO)
  #logger = logging.getLogger('plum.cockpit.feed')

  user = get_object_or_404(User, user__id__exact=request.user.id) 
  logging.info('cockpit: %s',user.user.username)
  follow = True
  profile = get_object_or_404 (User, user__username__exact=username) if username else user

  if skip:
    skip = int(skip)
    statuses = feed_lookup (user, profile, user==profile)
    last_id = statuses [0].id if statuses else '0'    
    statuses = statuses [skip:skip+33]
  else:
    statuses = feed_lookup (user, profile, user==profile)[:32]
    last_id = statuses [0].id if statuses else '0'
    
  watched = profile.watches.all()
  watchers = profile.watched_users_set.all()
  
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
    
  result = dict(feed=statuses, profile=profile, form=form, follow=follow, last_id=last_id,
    watches=watched, watchers=watchers, 
    javascripts=('enter', 'refresh'))

  if skip:
    result['skip_prev'] = skip-32 if skip-32 > 0 else 0
  result['skip_next'] = skip+33

  if slug:
    if slug in MESSAGES.keys():
      result['message'] = MESSAGES[slug]
      
  return HTTPResponse (template.render(RequestContext(request,result)))
 
 
@login_required  
def status (request, object_id=None, mobile=False):

  def process_image(**kwargs):
    instance = kwargs.get('instance', None)
    if kwargs.get('created', False):
      if instance:
        if instance.image:
          try:
            image = Image.open(instance.image.path)
            image.thumbnail((640,480), Image.ANTIALIAS)
#        icon = image.thumbnail((256,256), Image.ANTIALIAS)
            image.save(instance.image.path + '_preview' + '.jpg', 'JPEG')
#        icon.save(instance.image.path + '.preview.', 'JPEG')
          except IOError:
            os.remove(instance.image.path)
            instance.delete()
            return HTTPResponseRedirect(reverse('message_dashboard', 
              kwargs=dict(slug='IOImage')))
        
  post_save.connect(process_image, sender=Status)  
  
  user = get_object_or_404(DjangoUser, pk=request.user.id)
  profile = get_object_or_404 (User, user__exact=user)
  
  if request.method == 'GET':
    if not object_id:
      return HTTPResponseNotAllowed ('No GETting here.')
      
    status = get_object_or_404 (Status, pk=object_id)
    
    if not status.private or request.user in (status.owner.user, 
      status.recipient.user if status.recipient else None):
      template = loader.get_template("status.html")
      return HTTPResponse (template.render(RequestContext(request, dict(status=status))))
    else:
      return HTTPResponseForbidden () 
     
  elif request.method == 'POST':
    if object_id:
      return HTTPResponseNotAllowed ('No editing of the history!')
    else:    
      try:
        form = StatusForm (request.POST, request.FILES)
        if form.is_valid():
          status=form.save(commit=False)
          if len(status.text) > STATUS_LENGTH:
            newform = StatusForm(initial=dict(text=status.text))
            message = u'%s: ...%s' % (MESSAGES.get('TOOLong'),
              status.text[STATUS_LENGTH-16:STATUS_LENGTH])
            template = loader.get_template("mobile.html")
            return HTTPResponse(template.render(RequestContext(request,
              dict(form=newform, message=message, profile=profile))))
          status.owner=profile
        # message detection
          msg = MESSAGE_RE.match(status.text)
        
          if msg:
            recipient = get_object_or_404(DjangoUser, username=msg.groupdict()['recipient'])
            status.recipient = get_object_or_404(User, user=recipient)
            if status.text.startswith('>>'):
              status.private = True
            
        # tag assignment
          tag_result = TAG_RE.findall(status.text)
          status.tagged = True if tag_result else False

          status.text = escape(status.text.strip()) # SECURITY !!!!! DO NOT REMOVE!!!
          status.save()        
      except UnicodeEncodeError:
        return HTTPResponseRedirect(reverse('message_dashboard',
          kwargs=dict(slug='UEImage')))
                           
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
        action = Status	 (owner=profile, recipient=Status.objects.get(pk=q[1]).owner, action='quote', 
          text=reverse('cockpit.views.status', kwargs=dict(object_id=status.id)))
        action.save()
          
  #  else:
  #    HTTPResponseBadRequest()

    if mobile:
      return HTTPResponseRedirect(reverse('mobile_dashboard'))      
    else:
      return HTTPResponseRedirect(reverse('cockpit.views.main'))
      
  else:
    return HTTPResponseBadRequest()

def tag(request, text):

  user =  get_object_or_404(User, user__id__exact=request.user.id)  
  if request.method == 'GET':
  
    tag_object, create = Tag.objects.get_or_create(tag=text)
    if create:
      tag_object.save()   
    form = StatusForm (initial=dict(text='#%s' % text))
    statuses = tag_object.status.filter(private__exact=False, 
      recipient__exact=None).order_by('-date')[:32]
  
    template = loader.get_template("tag.html")
    result = dict(feed=statuses, text=text, 
      follow=tag_object not in user.watches_tags.all(), 
      ignore=tag_object not in user.ignores_tags.all())
  
    return HTTPResponse (template.render(RequestContext(request, result)))


def tag_subscription(request, text, action=None):

  if request.method == 'POST':

    tag_object = get_object_or_404(Tag, tag=text)
    user =  get_object_or_404(User, user__id__exact=request.user.id)  
  
    if action == 'subscribe':
      user.watches_tags.add(tag_object)
      user.save()
  
      notification = Status(owner=user, action='watch', text=text)
      notification.save()
    elif action == 'unsubscribe':
      if tag_object in user.watches_tags.all():
        user.watches_tags.remove(tag_object)
    elif action == 'ignore':
      pass
                          
    return HTTPResponseRedirect (reverse('mobile_dashboard'))
  else:
    return HTTPResponseNotAllowed ()

  
@login_required
def like (request, object_id, mobile=False):

  if request.method == 'POST':
    
    user =  get_object_or_404(User, user__id__exact=request.user.id)  
    status =  get_object_or_404(Status, id=object_id)      

    like, create = Like.objects.get_or_create(user=user, status=status)
    if create:
      like.save()
    
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
    
    like, create = Like.objects.get_or_create(user=user)
    if not create:
      like.delete()    
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
