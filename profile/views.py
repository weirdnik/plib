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
from django.template import Context, RequestContext, loader, Template
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import django.forms as forms

from models import User

from cockpit.models import Status

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


def blog (request, username):
  if request.method == 'GET':
  
    user =  get_object_or_404(User, user__id=request.user.id)  
    print user    
    statuses = Status.objects.filter(owner__exact=user, recipient__exact=None)

    print statuses    
    template = loader.get_template('blog.html')
    
    return HTTPResponse(template.render(Context(dict(statuses=statuses, profile=user))))


def register (request):

  from django.contrib.auth.models import User as DjangoUser

  class RegistrationForm(UserCreationForm):
    email = forms.EmailField(max_length=128)
        

  if request.method == 'GET':
    template = loader.get_template ('register.html')
    return HTTPResponse (template.render(RequestContext(request, dict(form=UserCreationForm()))))
    
  if request.method == 'POST':

    form = RegistrationForm(request.POST)
    
    if form.is_valid():
    
      print  dir(form['password1']),  form['password2'].data
      if  form['password1'].data == form['password2'].data:
        username = form['username'].data
        password = form['password1'].data
        email = form['email'].data

        # Warning: elsewhere in the code User is profile.models.User instance
        # here it is django.auth USer instance
        
        user = DjangoUser.objects.create_user(username, email, password)
        user.save()
        
        profile = User(user=user)
        profile.save()

        u = authenticate(username, password)        
        login (request, user)
      else:
        print 'bad passwords'
        return HTTPResponseBadRequest()
    else:
    
      return HTTPResponseRedirect(reverse('profile.views.register'))