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

from models import Status, StatusForm
from profile.models import User

def main (request):

  'main cockpit view for logged in user'
  
  user = request.user
  
  if user:
    profile = get_object_or_404(User, pk=user.id)
    result = dict(profile=profile)
    
    result['statuses'] = Status.objects.filter(owner__exact=user, recipient__exact=user).order_by('date')
    
    template = loader.get_template('cockpit.html')
    context = RequestContext (request, result)
    
    return HTTPResponse (template.render(context))
  
  else:
  
    return HTTPResponseRedirect ('/')
    
  
@login_required  
def status (request, object_id=None):

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
        status=form.save()
        
      return HTTPResponseRedirect(reverse('cockpit.views.main'))
      
  else:
    return HTTPResponseBadRequest()
    