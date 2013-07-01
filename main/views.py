# Create your views here.

from django.http import HttpResponseRedirect as HTTPResponseRedirect
from django.http import HttpResponse as HTTPResponse
from django.core.urlresolvers import reverse
from django.template import Context, loader

def front(request):

  if request.user:
    return HTTPResponseRedirect(reverse('cockpit.views.main'))
  else:
    template = loader.get_template('front.html')
    return HTTPResponse(template.render(Context({})))
      