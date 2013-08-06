# Create your views here.

import string, random

from Image import Image

import sendmail

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
from django.template import Context, RequestContext, loader, Template
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User as DjangoUser
from django.db.models.signals import post_save

import django.forms as forms

from models import User, UserForm
from cockpit.models import Status

###

HOST_URL = 'http://plib.hell.pl'

###

@login_required
def follow (request, username):

  if request.method == 'POST':
  
	user =	get_object_or_404(User, user__id__exact=request.user.id)  
	follow = get_object_or_404 (User, user__username__exact=username)
  
	user.watches.add(follow)
	user.save()

	action = Status(owner=follow, recipient=user, action='follow')
	action.save()
	
  
	return HTTPResponseRedirect (reverse('mobile_dashboard'))
  else:
	return HTTPResponseNotAllowed ()


@login_required
def unfollow (request, username):

  if request.method == 'POST':
  
	user =	get_object_or_404(User, user__id__exact=request.user.id)
	follow = get_object_or_404 (User, user__username__exact=username)

	if follow in user.watches.all():
	  user.watches.remove(follow)
	  user.save()

	action = Status(owner=follow, recipient=user, action='unfollow')
	action.save()
  
	return HTTPResponseRedirect (reverse('mobile_dashboard'))
  else:
	return HTTPResponseNotAllowed ()


def blog (request, username):
  if request.method == 'GET':
  
	user =	get_object_or_404(User, user__username__exact=username)
	statuses = Status.objects.filter(owner__exact=user, recipient__exact=None)

	template = loader.get_template('blog.html')
	
	return HTTPResponse(template.render(Context(dict(statuses=statuses, profile=user))))


def register (request):

  template = loader.get_template ('register.html')

  class RegistrationForm(UserCreationForm):
#	 pass
	email = forms.EmailField(max_length=128)
	   
  if request.method == 'GET':

	return HTTPResponse (template.render(RequestContext(request, dict(form=RegistrationForm()))))
	
  elif request.method == 'POST':

	form = RegistrationForm(request.POST)
	
	if form.is_valid():
	
	  print	 dir(form['password1']),  form['password2'].data
	  if  form['password1'].data == form['password2'].data:
		username = form['username'].data.strip()
		password = form['password1'].data
		email = form['email'].data
		 
		# Warning: elsewhere in the code user is profile.models.User instance
		# here it is django.auth User instance

		try: 
		  user = DjangoUser.objects.get(username=username)		  
		except DjangoUser.DoesNotExist:
		  user = DjangoUser.objects.create_user(username, email, password)
		  user.is_active = False
		  user.save()
				  
		  profile = User(user=user)
		  slug = ''
		  for i in xrange(16):
			slug = slug + random.choice(string.ascii_letters)
		  profile.slug = slug
		  
		  slug_path = reverse('profile.views.confirm', kwargs=dict(slug=slug))
		  slug_url = request.META.get('HTTP_ORIGIN',HOST_URL) + slug_path
		 
		  profile.save()
		  sendmail.confirm (email, slug_url)		  
		  template = loader.get_template ('confirm.html')
		  return HTTPResponse (template.render(RequestContext(request, dict(email=email))))
	  else:
		print 'bad passwords'
		return HTTPResponseBadRequest()
	else:
	  return HTTPResponse (template.render(RequestContext(request, dict(form=form))))

def confirm (request, slug=None):

  if slug:
	user = get_object_or_404(User, slug__exact=slug)
	if user:
	  user.user.is_active = True
	  user.user.save()
	  user.active = True
	  user.save()
#	   u = authenticate(user.user.username, password)		 
#	   login (request, user.user)
	  template = loader.get_template('confirmed.html')
	  
	  return HTTPResponse(template.render(Context(dict(user=user))))
	  
  return HTTPResponseRedirect(reverse('cockpit.views.main'))


def edit (request):

  def process_images(**kwargs):
	import os
	
	instance = kwargs.get('instance', None)
	if instance.avatar:
	  avatar = Image.open(instance.avatar.path)
	  avatar.thumbnail((256,256), Image.ANTIALIAS)
	  avatar.save(instance.avatar.path + '.jpg', 'JPEG')

  # works but unnecessary
  
#	 if instance.background:
#	   background = Image.open(instance.background.path)
#	   path = os.path.join((lambda p:'/'.join(p.split('/')[:-1]))(instance.background.path), 'background-%s.jpg' % instance.user.username)
#	   background.save(path,'JPEG')
	  
  post_save.connect(process_images, sender=User)
  template = loader.get_template ("account.html")																		   
  user =  get_object_or_404(User, user__id__exact=request.user.id)	

  if request.method == 'GET':
	initial = { 'name': user.name, 'about': user.about, 'icbm': user.icbm }
	result = dict(form=UserForm(initial))
	
  elif request.method == 'POST':
	form = UserForm(request.POST, request.FILES)
	if form.is_valid():
	  save = False
	  for item in ('name', 'about', 'icbm', 'sex', 'avatar', 'background'):
		value = form.cleaned_data.get(item, None)
		if value:
		  setattr(user, item, value)
		  save = True
	  if save:
		user.save()
	result = dict(form=form)
	  
  return HTTPResponse(template.render(RequestContext(request, result)))
  