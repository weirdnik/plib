# Create your views here.

import datetime

from django.http import HttpResponseRedirect as HTTPResponseRedirect
from django.http import HttpResponse as HTTPResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.db.models import Count

import datetime

from cockpit.models import Status, Like

from settings import APP_NAME

def front(request):

  if request.method == 'GET':

    now = datetime.datetime.now()
    week = datetime.timedelta(days=7)
    
    likes = Status.objects.filter(date__gte=(now-week)).annotate(likes_count=Count('likes')).order_by('-likes_count')[:16]
  
    statuses = Status.objects.filter(private__exact=False, recipient__exact=None,
      action__exact=None).order_by('-date')
    feed = statuses[:20] if statuses else None

    template = loader.get_template('front.html')
    return HTTPResponse(template.render(RequestContext(request,
      dict(feed=feed, likes=likes, app_name=APP_NAME))))
      
def health(request):

  return HTTPResponse('OK')