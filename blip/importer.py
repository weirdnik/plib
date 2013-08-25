#! /usr/bin/env python

'''Blip importer based on Robert Maron's scripts.
'''

import os
import sys
import re
import json
import subprocess
import zipfile
import string
import random

from cockpit.views import notify
from settings import MEDIA_ROOT

from shutil import rmtree
global WORKDIR

DEBUG = True
RUN = '/var/tmp'
WORKDIR = '/srv/www/plib.hell.pl/plib'
SRC_DIR = (lambda p:'/'.join(p.split('/')[:-1]))(os.path.abspath(__file__))

JOBS = 2

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
  
    for suffix in ('jpg', 'png', 'gif'):
      path = os.path.join(datadir(),'avatar-%s.%s' % (username, suffix))
      if os.path.exists(path):
        return path

  def import_month (user, year, month):
    '''Reads single month data dump and puts into the database.'''
    
    from cockpit.models import Status, Tag, TAG_RE, MESSAGE_RE
    from models import Info
      
    path = os.path.join(datadir(), str(year), '%02d'% month)  
    if os.path.exists(path):
      
      print 'Importing %s/%s' % (month, year)
      notify (user, 'Importowanie %s/%s.' % (month, year))
      flist=  [ os.path.join(path,f) for f in os.listdir(path) if RE.match(f) ]
      print flist
      for f in flist:
        print f
        blip = json.loads(file(f).read())      
        text = blip.get('body', None)
        date = blip.get('created_at', None)
        blip_id = blip.get('id', None)
        blip_type = blip.get('type', None)
        transport = blip.get('transport_description', '')
        likes = blip.get('likes_count', 0)
        liked = blip.get('likes_user', tuple())

        status, created_status = Status.objects.get_or_create(owner=user,
          text=text, date=date) # blip=info)
          
        status.save()
          
        info, created_info = Info.objects.get_or_create(blip=blip_id, type=blip_type,
          transport=transport, likes=likes, liked=','.join(liked), status=status)
 
        if not created_info and not created_info:
          if DEBUG:
            print 'status and info exist, skipping'
          continue # status and info already exist
          
        tag_result = TAG_RE.findall(status.text)
        status.tagged = True if tag_result else False
                    
        status.text = escape(status.text) # SECURITY !!!!! DO NOT REMOVE!!!

        core='-'.join(f.split('-')[:-1])
        for suffix in ('jpg', 'png', 'gif'):
          filename = '.'.join((core, suffix))
          if os.path.exists(filename): # jest obrazek
            try:
              if os.stat(filename)[6]:
                if DEBUG:
                  print filename
                status.image.save(filename, File(file(filename)))
            except TypeError:
              if DEBUG:
                print 'bad image file %s' % filename
        
        status.save()       

        info.status = status
        info.save()        
           
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
    else:
      print 'tags fail'

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
    else:
      print 'tags fail'

  from django.shortcuts import get_object_or_404
  from django.contrib.auth.models import User as User
  from django.utils.html import escape
  from django.core.files import File
    
  from profile.models import User as Profile
  
  user = get_object_or_404(User, username__exact=username)
  profile = get_object_or_404(Profile, user__exact=user)

  update_profile(profile, blipname)

  for year in YEARS:
    for month in MONTHS:
      import_month(profile, year, month)
  
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

def zipdir(workdir, blip):
  from settings import MEDIA_ROOT

  slug = ''.join([ random.choice(string.letters) for s in xrange(64) ])
  
  blip.slug=slug
  blip.save()
  
  directory = os.path.join(MEDIA_ROOT,'backups',slug)
  if not os.path.exists(directory):
    os.makedirs(directory)
  zipfilename = os.path.join(directory, 'blip-%s-archive.zip' % blip.blip)

  os.chdir(workdir)  
  zip = zipfile.ZipFile(zipfilename, 'w')
  for root, dirs, files in os.walk('.'):
    for file in files:
      zip.write(os.path.join(root, file))
  zip.close()

def unpack(blip):
  
  if blip.slug:
    zipfilename = os.path.join(MEDIA_ROOT,'backups', blip.slug,
      'blip-%s-archive.zip' % blip.blip)
    if os.path.exists(zipfilename):
      from tempfile import mkdtemp
      tmpdir = mkdtemp(suffix=blip.blip)
      os.chdir(tmpdir)     
      zip = zipfile.ZipFile(zipfilename,'r')
      print 'namelist, ', zip.namelist()
      for name in zip.namelist():
        print name
        (dirname, filename) = os.path.split(name)
        print "Decompressing " + filename + " on " + dirname
        if name:
          if not os.path.exists(dirname) and dirname:
            print dirname
            os.makedirs(dirname)
          fd = open(name,"w")
          fd.write(zip.read(name))
          fd.close()
           
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
    print waiting
    if waiting:
      job = dict(blips).get(waiting[0])    
      username = job.user.user.username
      blipname = job.blip
      pid = os.getpid()
      pidfilename = os.path.join(RUN, 'blip.%s' % blipname)
      file(pidfilename, 'w').write(str(pid))
      notify (job.user,'Pobieranie z Blip.pl.')      

      WORKDIR = unpack(job)
      if not WORKDIR:
        if DEBUG:
          print 'no archive to unpack, calling robmar'    
        WORKDIR = robmar(blipname, job.password)        
        if DEBUG:
          print WORKDIR
        zipdir (WORKDIR, job)      
      update_account (username, blipname)
      
      job.imported = True
      job.save()
              
      rmtree(WORKDIR)
      notify (job.user,'Import zakonczony.')  
      os.remove(pidfilename)

  print "This file should be run as a part of PLIB."
#  update_account('alex', 'alex')
  sys.exit(1)