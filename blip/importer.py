#! /usr/bin/env python

'''Blip importer based on Robert Maron's scripts.
'''

import os
import sys
import re
import json
import subprocess

global WORKDIR

DEBUG = True
RUN = '/var/tmp'
WORKDIR = '/srv/www/plib.hell.pl/plib'
SRC_DIR = (lambda p:'/'.join(p.split('/')[:-1]))(os.path.abspath(__file__))

JOBS = 2

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
  
    tags_filename =  os.path.join(datadir(),'tags-%s.txt' % username)
    print tags_filename   
    if os.path.exists(tags_filename):
      subscribed_tags = json.loads(file(tags_filename, 'r').read())
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

    tags_filename = os.path.join(datadir(),'tags-ignored-%s.txt' % username)
    print tags_filename   
    if os.path.exists(tags_filename):

      ignored_tags = json.loads(file(tags_filename, 'r').read())
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

  print blips      
  return blips

def queue():
  
  from models import Blip
    
  blips =  [ (i.blip, i) for i in Blip.objects.filter(imported__exact=False)]
    
  print 'q,', blips
  return blips
  
  
def robmar(blipname, blippassword):

  import stat

  if DEBUG:
    print 'Importing %s...' % blipname
    
  ROBMAR = 'get-blip-archive.sh'
  
  from tempfile import mkdtemp
  from shutil import copy
  
  tmpdir = mkdtemp(suffix=blipname)
  
  copy(os.path.join(SRC_DIR, ROBMAR), tmpdir)
  
  os.chdir(tmpdir)
  try:
    os.chmod(ROBMAR, stat.S_IRUSR| stat.S_IWUSR | stat.S_IXUSR)
    result = subprocess.check_output(['bash','./%s' % ROBMAR, ':'.join((blipname, blippassword))])
    print result
  except subprocess.CalledProcessError:
    # os.rmtree(tmpdir)
    print result
    
    # TODO zipping
    
  return tmpdir

  
if __name__ == '__main__':

  file('/var/tmp/blip.test','w').write(str(os.getpid()))
  
  r = set(check_running())

  print r  
  if len(r) < JOBS+2:
    blips = queue()
    q = set([i[0] for i in blips])
    print q
    waiting=list(q-r)

        
    if waiting:
      job = dict(blips).get(waiting[0])    
      username = job.user.user.username
      blipname = job.blip
      pid = os.getpid()
      pidfilename = os.path.join(RUN, 'blip.%s' % blipname)
      file(pidfilename, 'w').write(str(pid))
      
      WORKDIR = robmar(blipname, job.password)
          
      print WORKDIR
      
      update_account (username, blipname)
      #os.remove(pidfilename)
      
      # TODO zipping
      
  

  

  print "This file should be run as a part of PLIB."
#  update_account('alex', 'alex')
  sys.exit(1)