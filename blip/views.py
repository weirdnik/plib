# Create your views here.
# -*- coding: utf-8 -*-

from models import BlipForm

from django.http import HttpResponse as HTTPResponse
from django.http import HttpResponseRedirect as HTTPResponseRedirect
from django.http import HttpResponseGone as HTTPResponseGone
from django.http import HttpResponseBadRequest as HTTPResponseBadRequest
from django.http import HttpResponseNotAllowed as HTTPResponseNotAllowed
from django.http import HttpResponseForbidden as HTTPResponseForbidden
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.template import RequestContext, loader, Template


@login_required
def importer(request):

  '''This view accepts data from the import blip account form and puts them
  in the database for the importer to use.
  '''

  if request.method == 'GET':
    template = loader.get_template("import.html")
    form = BlipForm()
    return HTTPResponse(template.render(RequestContext(request, dict(form=form))))                                                                                                                                                                                                                            

#  elif request.method == 'POST':
  
    
    

