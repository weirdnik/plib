# Create your views here.

import JSON

from models import URLForm

from cockpit.models import PROCESS_RE

def shorten(request):

  if request.method == 'POST':
  
     url = URLForm(request.POST):
     # TODO liczenie sluga
     
     if url.is_valid():

       # is URL a freeform URL or something to be left alone to embed?
       
       match = PROCESS_RE.search(url.cleaned_data["url")
       
       if match:
         if 'url' in match.groupdict().keys():

     
         url.save(commit=False)
       
         url.slug = ''   
         url.save())
       
         return JSON.
