#! /usr/bin/env python

'''Blip importer based on Robert Maron's scripts.
'''

import os
import sys
import re
import json

DEBUG = True

WORKDIR = '/srv/www/plib.hell.pl/plib'

RE = re.compile('^blip-\w+-(?P<file_id>\d+)-full.txt$')

YEARS = ('2013', ) # tuple(range(2007,2014))

MONTHS = ('07', ) # tuple(range (1,13))

def update_account(username, blipname):

  '''Feeds the data gathered by the script to the user
  
  transport
  likes_count
  liked_by
  '''

  def datadir():
    return os.path.join(os.path.abspath(WORKDIR), 'DATA')
    
  def avatar(username): 
  
    for suffix in ('jpg', 'png', 'gif'):
      path = os.path.join(datadir(),'avatar-%s.%s' % (username, suffix))
      if os.path.exists(path):
        return path

  def import_month (user, year, month):
    '''Reads single month data dump and puts into the database.'''
    
    from cockpit.models import Status, Tag, TAG_RE, MESSAGE_RE
    from models import Info
      
    path = os.path.join(datadir(), str(year), str(month))  
    if os.path.exists(path):
      print 'Importing %s/%s' % (month, year)
      for f in  [ os.path.join(path,f)
                  for f in os.listdir(path) if RE.match(f) ]:

        blip = json.loads(file(f).read())      
        text = blip.get('body', None)
        date = blip.get('created_at', None)
                      
      # TODO zapisywanie bliplajkow

        blip_id = blip.get('id', None)
        blip_type = blip.get('type', None)
        transport = blip.get('transport_description', '')
        likes = blip.get('likes_count', 0)
        liked = blip.get('likes_user', tuple())
        
        info = Info(blip=blip_id, type=type, transport=transport, likes=likes)
        info.save()        
        if DEBUG:
          print info

        status = Status(owner=user, text=text, date=date, blip=info)
        tag_result = TAG_RE.findall(status.text)
        status.tagged = True if tag_result else False
                    
        status.text = escape(status.text) # SECURITY !!!!! DO NOT REMOVE!!!

        core='-'.join(f.split('-')[:-1])
        for suffix in ('jpg', 'png', 'gif'):
          filename = '.'.join((core, suffix))
          if os.path.exists(filename): # jest obrazek
            if DEBUG:
              print filename
            status.image.save(filename, File(file(filename)))
        
        status.save()       
      
        if status.tagged:
          for tag_text in tag_result:
            tag, create = Tag.objects.get_or_create(tag=tag_text.lower())
            tag.status.add(status)
            tag.save()

  def update_profile(profile,username):
    from cockpit.models import Tag
    # updating the avatar
    
    avatar_filename = avatar(username)
    if avatar_filename:
      profile.avatar.save(avatar_filename, File(file(avatar_filename)))

    subscribed_tags = json.loads(file(os.path.join(datadir(),'tags-%s.txt' % username), 'r').read())
    for t in subscribed_tags:
      tag_path = t.get('tag_path', None)
      if tag_path:
        tag_text = tag_path.split('/')[-1].lower()
        print tag_text
        tag, create = Tag.objects.get_or_create(tag=tag_text)
        if create:
          tag.save()
        profile.watches_tags.add(tag)
    profile.save()

    ignored_tags = json.loads(file(os.path.join(datadir(),'tags-ignored-%s.txt' % username), 'r').read())
    for t in ignored_tags:
      tag_path = t.get('tag_path', None)
      if tag_path:
        tag_text = tag_path.split('/')[-1].lower()
        print tag_text
        tag, create = Tag.objects.get_or_create(tag=tag_text)
        if create:
          tag.save()
        profile.ignores_tags.add(tag)
    profile.save()

  from django.shortcuts import get_object_or_404
  from django.contrib.auth.models import User as User
  from django.utils.html import escape
  from django.core.files import File
    
  from profile.models import User as Profile
  
  user = get_object_or_404(User, username__exact=username)
  profile = get_object_or_404(Profile, user__exact=user)

  update_profile(profile, username)

#  for year in YEARS:
#    for month in MONTHS:
#      import_month(profile, year, month)
  
#  print avatar(username)  

#  print import_month(2009,12)

# TODO puszczanie robmar-skryptu


def check_running():
  '''test if other instances are running'''
  
  RUN = '/var/tmp'
  


  files = [ f for f in os.listdir(RUN) if f.startswith('blip.') ]

  blips = []
  
  for f in files:
    try:
      filename = os.path.join(RUN, f)
      pid = int(file(filename,'r').read())
      os.kill(pid,0)
    except OSError:
      os.remove(filename)
      print 'Stale file %s deleted.' % filename
    except ValueError:
      continue
    else:
      blipname = f.split('.')[1]
      blips.append(blipname)
      
  return blips

if __name__ == '__main__':

  file('/var/tmp/blip.test','w').write(str(os.getpid()))
  print check_running()

  mypid = os.getpid()

  print "This file should be run as a part of PLIB."
#  update_account('alex', 'alex')
  sys.exit(1)