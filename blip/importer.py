#! /usr/bin/env python

'''Blip importer based on Robert Maron's scripts.
'''

import os
import sys
import re
import json

WORKDIR = '/srv/www/plib.hell.pl/plib'

RE = re.compile('^blip-\w+-(?P<file_id>\d+)-full.txt$')

YEARS = tuple(range(2007,2014))
MONTHS = tuple(range (1,13))

def update_account(username, blipname):

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

  def import_month (user, year, month):
    '''Reads single month data dump and puts into the database.'''
    
    from cockpit.models import Status, Tag, TAG_RE, MESSAGE_RE
    from models import Info
      
#  def parse_status(text):

    path = os.path.join(datadir(), str(year), str(month))  
    if os.path.exists(path):
      print 'Importing %s/%s' % (month, year)
      for f in  [ file(os.path.join(path,f)).read()
                  for f in os.listdir(path) if RE.match(f) ]:
        blip = json.loads(f)      
        text = blip.get('body', None)
        date = blip.get('created_at', None)
              
      # TODO robienie blipinfo

        blip_id = blip.get('id', None)
        blip_type = blip.get('type', None)
        transport = blip.get('transport_description', '')
        likes = blip.get('likes_count', 0)
        liked = blip.get('likes_user', tuple())
        
        info = Info(blip=blip_id, type-type, transport=transport, likes=likes)

        status = Status(owner=user, text=text, date=date)
        tag_result = TAG_RE.findall(status.text)
        status.tagged = True if tag_result else False
                    
        status.text = escape(status.text) # SECURITY !!!!! DO NOT REMOVE!!!
        status.save()       
      
        if status.tagged:
          for tag_text in tag_result:
            print tag_text
            tag, create = Tag.objects.get_or_create(tag=tag_text.lower())
            tag.status.add(status)
            tag.save()
                                                            

  from django.shortcuts import get_object_or_404
  from django.contrib.auth.models import User as User
  from django.utils.html import escape
  
  from profile.models import User as Profile
  
  user = get_object_or_404(User, username__exact=username)
  profile = get_object_or_404(Profile, user__exact=user)

  for year in YEARS:
    for month in MONTHS:
      import_month(profile, year, month)
  
#  print avatar(username)  

#  print import_month(2009,12)

# TODO puszczanie robmar-skryptu


if __name__ == '__main__':

  print "This file should be run as a part of PLIB."
  update_account('alex', 'alex')
  sys.exit(1)