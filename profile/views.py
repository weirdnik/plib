# Create your views here.

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

from models import User

@login_required
def follow (request, username):

  if request.method == 'POST':
  
    user =  get_object_or_404(User, pk=request.user.id)  
    follow = get_object_or_404 (User, user__username__exact=username)
  
    user.watches.add(follow)
    user.save()
  
    return HTTPResponseRedirect (reverse('cockpit.views.main'))
  else:
    return HTTPResponseNotAllowed ()

@login_required
def unfollow (request, username):

  if request.method == 'POST':
  
    user =  get_object_or_404(User, pk=request.user.id)  
    follow = get_object_or_404 (User, user__username__exact=username)

    if follow in user.watches.all():
      user.watches.remove(follow)
  
      user.save()
  
    return HTTPResponseRedirect (reverse('cockpit.views.main'))
  else:
    return HTTPResponseNotAllowed ()

