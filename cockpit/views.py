# Create your views here.

from django.db.models import Q
from django.http import HttpResponse as HTTPResponse
from django.http import   HttpResponseRedirect as HTTPResponseRedirect
from django.http import   HttpResponseGone as HTTPResponseGone
from django.http import   HttpResponseBadRequest as HTTPResponseBadRequest
from django.http import   HttpResponseNotAllowed as HTTPResponseNotAllowed
from django.http import   HttpResponseForbidden as HTTPResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template import RequestContext, loader, Template

from models import Status, StatusForm
from profile.models import User

@login_required
def main (request, username=None):

  'main cockpit view for logged in user'
  
  user = get_object_or_404(User, pk=request.user.id)
  profile = get_object_or_404 (User, user__username__exact=username) if username else user
  
  # profile - the profile displayed
  # user - the logged user's profile
  
  template = loader.get_template('cockpit.html')
  result = dict(profile=profile, form=StatusForm())
  
  following = user.watches.all()

  if username:    
    result['statuses'] = Status.objects.filter(owner__exact=profile).order_by('-date')

    if profile in following:
      result['follow'] = False
      result['unfollow'] = True
    else:
      result['follow'] = True
      result['unfollow'] = False
  else:
    statuses = Status.objects.filter(Q(owner__in=following)|Q(owner__exact=profile))
    result['statuses'] = statuses
    result['watch'] = False

  context = RequestContext (request, result)
  return HTTPResponse (template.render(context))
  

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
        status.save()
      else:
        HTTPResponseBadRequest()
      return HTTPResponseRedirect(reverse('cockpit.views.main'))
      
  else:
    return HTTPResponseBadRequest()
    