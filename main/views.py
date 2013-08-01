# Create your views here.

import datetime

from django.http import HttpResponseRedirect as HTTPResponseRedirect
from django.http import HttpResponse as HTTPResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.db.models import Count

from cockpit.models import Status, Like

from settings import APP_NAME

def front(request):

  if request.method == 'GET':
  
    statuses = Status.objects.filter(private__exact=False, recipient__exact=None).order_by('-date')    
    feed = statuses[:20] if statuses else None
    
    now = datetime.date.today()
    week = datetime.timedelta(weeks=1)
    since = now-week
    
    liked = Like.objects.filter(status__private__exact=False, 
      status__recipient__exact=None, 
      status__date__gte=since).annotate(likes=Count('user')).order_by('likes')
    likes = liked[:10] if liked else None

    template = loader.get_template('front.html')
    return HTTPResponse(template.render(RequestContext(request, dict(feed=feed,likes=likes,app_name=APP_NAME))))
      