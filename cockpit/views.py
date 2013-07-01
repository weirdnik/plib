# Create your views here.
# -*- coding: iso-8859-2 -*-
import re

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

from models import Status, StatusForm
from profile.models import User

MESSAGE_RE = re.compile('^>>?(?P<recipient>\w+)')
MENTION_RE = re.compile('\^(?P<nickname>\w+)')

###

def feed_lookup (user, profile, private):
  following = user.watches.all()
  if private:
    result = Status.objects.filter(
      (Q(owner__in=following) & Q(recipient__exact=None)) |
      Q(owner__exact=profile) | Q(recipient__exact=profile)).order_by('-date')
      
  else:
     result = Status.objects.filter(
       ( Q(owner__exact=user)| Q(recipient__exact=user) ) | # all msgs between displayed and own
       ( (Q(owner__exact=profile) | Q(recipient__exact=profile)) & Q(private__exact=False))
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
#    result['statuses'] = Status.objects.filter(
#      ( Q(owner__exact=user)| Q(recipient__exact=user) ) | # all msgs between displayed and owner
#      ( (Q(owner__exact=profile) | Q(recipient__exact=profile)) & Q(private__exact=False))
#      ).order_by('-date')

    if profile in following:
      result['follow'] = False
      result['unfollow'] = True
    else:
      result['follow'] = True
      result['unfollow'] = False
  else: # profile = user
    statuses = feed_lookup (user_profile, profile, True)
#    statuses = Status.objects.filter(
#       (Q(owner__in=following) & Q(recipient__exact=None)) |
#       Q(owner__exact=profile) | Q(recipient__exact=profile))
  
    result['statuses'] = statuses
    result['watch'] = False
    result['profile'] = profile
  context = RequestContext (request, result)
  return HTTPResponse (template.render(context))

@login_required
def feed (request, username=None):  

  user = get_object_or_404(DjangoUser, pk=request.user.id)
  user_profile = get_object_or_404 (User, user__exact=user)
  profile = get_object_or_404 (User, user__username__exact=username) if username else user_profile

  statuses = feed_lookup (user_profile, profile, user==profile)  
  template = loader.get_template("feed.html")
  return HTTPResponse (template.render(RequestContext(request, dict(feed=statuses, profile=profile))))
 
 
@login_required  
def status (request, object_id=None):

  user = get_object_or_404(User, pk=request.user.id)
  
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
    
      form = StatusForm (request.POST)
      if form.is_valid():
        status=form.save(commit=False)
        status.owner=user

        #ESCAPE CONTENT - CRITICAL  XXX
        
        # tag assignment
        
        msg = MESSAGE_RE.match(status.text)
        
        if msg:
          recipient = get_object_or_404(DjangoUser, username=msg.groupdict()['recipient'])
          status.recipient = get_object_or_404(User, user=recipient)
          if status.text[1] == '>':
            status.private = True
        
        status.save()
        
        # convert txt.png -resize 400\> 200.png
        
      else:
        HTTPResponseBadRequest()
      return HTTPResponseRedirect(reverse('cockpit.views.main'))
      
  else:
    return HTTPResponseBadRequest()

def tag(request, tag):
  pass    