#! /usr/bin/env python

'''Blip importer based on Robert Maron's scripts.


class BlipInfo(models.Model):

  

'''

import os
import sys
import re
import json

WORKDIR = '/srv/www/plib.hell.pl/plib'

RE = re.compile('^blip-\w+-(?P<file_id>\d+)-full.txt$')

def update_profile(username):

  '''Feeds the data gathered by the script to the user
  
  transport
  likes_count
  liked_by
  '''

  def datadir():
    return os.path.join(os.path.abspath(WORKDIR), 'DATA')
    
  def avatar(username): 
  
    for suffix in ('jpg', 'png'):
      path = os.path.join(datadir(),'avatar-%s.%s' % (username, suffix))
      if os.path.exists(path):
        return path

  def import_month (year, month):
  
  #  from cockpit.models import Status
  
#    def parse_status(text):
 
#     text =    
 #    date = 
#    from cockpit.models import TAG_RE, MESSAGE_RE
    

#          tag_result = TAG_RE.findall(status.text)
#                    status.tagged = True if tag_result else False
                    
#                              status.text = escape(status.text) # SECURITY !!!!! DO NOT REMOVE!!!
#                                        status.save()
                                        
  #  pass
    
    path = os.path.join(datadir(), str(year), str(month))  
    for f in  [ file(os.path.join(path,f)).read() for f in os.listdir(path) if RE.match(f) ][:2]:
      data = json.loads(f)
      print data    
      
      text = data.get('body', None)
      date = data.get('created_at', None)

#  from django.shortcuts import get_object_or_404
#  from django.contrib.auth.models import User as User
#  
#  from models import User as Profile

#  user = get_object_or_404(User, username__exact=username)
#  profile = get_object_or_404(Profile, user__exact=user)
  
  print avatar(username)  

  print import_month(2009,12)

if __name__ == '__main__':

  print "This file should be run as a part of PLIB."
  update_profile('alex')
  sys.exit(1)