import os
import sys
import django.core.handlers.wsgi

path = (lambda p:'/'.join(p.split('/')[:-1]))(os.path.abspath(__file__))

sys.path.append('/usr/share/pyshared/django/')

if path not in sys.path:
  sys.path.append(path)
            
os.environ['DJANGO_SETTINGS_MODULE'] = 'skandale.settings'
application = django.core.handlers.wsgi.WSGIHandler()
            