#!/usr/bin/python

import collectd
import subprocess

tps_array = []

###CONFIG CALLBACK
def config_callback(config):
  api_key_accepted = False
  
  try:
    for node in config.children:
      key = node.key.lower()
      val = node.values[0]

      if key == 'log_file':
        global log_file
        log_file = val
        log_file_provided = True
      
      if key == 'user':
        global user
        user = val
        user_provided = True

    if api_key_accepted:
      collectd.info('minecraft_tps plugin successfully initialized with log_file')
    else:
      collectd.info('minecraft_tps plugin requires log_file to be configured')

    if user_provided:
      collectd.info('minecraft_tps plugin successfully initialized with user')
    else:
      collectd.info('minecraft_tps plugin requires user to be configured')

  except Exception as e:
    collectd.info(str(e))

###DATA FUNCTION
def get_tps():
  tps_array = []
  tps_data = {}
  
  try:
    subprocess.call(["sudo", "-u", user, "screen", "-X", "stuff", "tps\015"])

  except Exception as e:
    collectd.info(str(e))

  try:
    with open(log_file, 'r') as rh:
      for line in rh:
        if 'TPS' in line and '#' in line:
          tps_value = line.split()
          tps_array.append(tps_value[0])
    
    tps_data['result'] = tps_array[-1]
    return tps_data

  except Exception as e:
    collectd.info(str(e))

###READ CALLBACK
def read_callback(data=None):
  tps_data = get_tps()

  try:
    if not tps_data:
      collectd.info('minecraft_tps plugin was not able to gather data for some reason')
      pass
    else:
      for key in tps_data:
        metric = collectd.Values()
        metric.plugin = 'minecraft_tps'
        metric.type = 'gauge'
        metric.type_instance = key
        metric.values = [tps_data[key]]
        metric.dispatch()

  except Exception as e:
    collectd.info(str(e))

###REGISTER FUNCTIONS
collectd.register_config(config_callback)
collectd.register_read(read_callback)
