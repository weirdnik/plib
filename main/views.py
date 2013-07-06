# Create your views here.

from django.http import HttpResponseRedirect as HTTPResponseRedirect
from django.http import HttpResponse as HTTPResponse
from django.core.urlresolvers import reverse
from django.template import Context, loader

from cockpit.models import Status

def front(request):

  if request.user.id:
    return HTTPResponseRedirect(reverse('cockpit.views.main'))
  else:
    statuses = Status.objects.filter(private__exact=False, recipient__exact=False).order_by('-date')
    
    if statuses:
      feed = statuses[:20] if statuses else None
    
    template = loader.get_template('front.html')
    return HTTPResponse(template.render(Context(dict(feed=feed))))
      