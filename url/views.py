# Create your views here.

import JSON

from models import URLForm

def api_shorten(request):

  if request.method == 'POST':
  
     url = URLForm(request.POST):
     # TODO liczenie sluga
     
     if url.is_valid():
     
       url.save(commit=False)
       
       url.slug = ''
       
       url.save())
       
       return JSON.
