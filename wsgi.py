import os,sys
import django.core.handlers.wsgi

local_path = (lambda p:'/'.join(p.split('/')[:-1]))(os.path.abspath(__file__))
super_path = (lambda p:'/'.join(p.split('/')[:-1]))(local_path)

if local_path not in sys.path:
  sys.path.append(local_path)
if super_path not in sys.path:
  sys.path.append(super_path)
            
os.environ['DJANGO_SETTINGS_MODULE'] = 'plib.settings'
application = django.core.handlers.wsgi.WSGIHandler()
            