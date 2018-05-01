#!/usr/bin/python

import collectd
import pwd
import os
import re

###THIS IS THE DATA GATHERING FUNCTION
def get_hits_by_domain():
  """ Function to Get Domain Hits """
  
  #PUT THIS HERE TO TRY AND RUN THE PYTHON SCRIPT AS ROOT, DIDN'T WORK
  uid = pwd.getpwnam('root')[2]
  os.setuid(uid)

  #DEFINE VARS
  nlogdir = '/var/log/nginx/'
  alogdir = '/var/log/httpd/'
  hits_by_domain = {}

  try:
    #GET NGINX LOGS
    nfiles = [f for f in os.listdir(nlogdir) if re.match(r'^(?!default)(.+access.log)$', f)]

    for i, s in enumerate(nfiles):
      nfiles[i] = os.path.join(nlogdir, s)

    #GET APACHE LOGS
    afiles = [f for f in os.listdir(alogdir) if re.match(r'^(?!.+_)(.+\.access.log)$', f)]

    for i, s in enumerate(afiles):
      afiles[i] = os.path.join(alogdir, s)

    #COUNT NGINX HITS
    for f in nfiles:
      nregex = "("+str(nlogdir)+")(.+?)(.access.log)"
      domain = re.search(nregex, f)
      count = 0
      for line in open(f).xreadlines():
        count +=1
      hits_by_domain[domain.group(2)] = count

    #COUNT APACHE HITS
    for f in afiles:
      aregex = "("+str(alogdir)+")(.+?)(.access.log)"
      domain = re.search(aregex, f)
      count = 0
      for line in open(f).xreadlines():
        count +=1
      hits_by_domain[domain.group(2)] = count

    return hits_by_domain

  except Exception as e:
    collectd.info(str(e))
    return

###THIS DOESN'T REALLY DO ANYTHING; COLLECTD NEEDS IT I GUESS
def config_callback(config):
  collectd.info('hits_by_domain Successfully Loaded')

###THIS CALLS THE DATA GATHERING FUNCTION AND DISPATCHES IT
def read_callback(data=None):
  """ Callback function for dispatching data into collectd """

  hits_by_domain = get_hits_by_domain()

  if not hits_by_domain:
    collectd.info('hits_by_domain not collected successfully')
    pass
  else:
    for key in hits_by_domain:
      metric = collectd.Values()
      metric.plugin = 'hits_by_domain'
      metric.type = 'count'
      metric.type_instance = key
      metric.values = [hits_by_domain[key]]
      metric.dispatch()

###REGISTER FUNCTIONS WITH COLLECTD SO THAT IT'LL DO THE THINGS
collectd.register_config(config_callback)
collectd.register_read(read_callback)
