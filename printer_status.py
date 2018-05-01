#!/usr/bin/python

###IMPORT LIBRARIES
import collectd
import json
import urllib2

###CONFIG CALLBACK
def config_callback(config):
  api_key_accepted = False
  
  try:
    for node in config.children:
      key = node.key.lower()
      val = node.values[0]

      if key == 'api_key':
        global api_key
        api_key = val
        api_key_accepted = True

    if api_key_accepted:
      collectd.info('printer_status plugin successfully initialized with api_key')
    else:
      collectd.info('printer_status plugin requires api_key to be configured')

  except Exception as e:
    collectd.info(str(e))

###DATA FUNCTION
def get_printer_data():
  printer_api = 'http://localhost/api/printer'
  printer_data = {}

  request = urllib2.Request(printer_api)
  request.add_header('X-Api-Key',api_key)

  try:
    response = urllib2.urlopen(request)
    body = json.loads(response.read())

    #get state
    if body['state']['flags']['printing'] == True:
      printer_data['printing'] = 1
    else:
      printer_data['printing'] = 0

    #get bed actual
    printer_data['bed_actual'] = body['temperature']['bed']['actual']

    #get bed target
    printer_data['bed_target'] = body['temperature']['bed']['target']

    #get tool actual
    printer_data['tool_actual'] = body['temperature']['tool0']['actual']

    #get tool target 
    printer_data['tool_target'] = body['temperature']['tool0']['target']

    return printer_data

  except Exception as e:
    collectd.info(str(e))

###READ CALLBACK
def read_callback(data=None):
  printer_data = get_printer_data()

  try:
    if not printer_data:
      collectd.info('printer_status plugin was not able to gather data for some reason')
      pass
    else:
      for key in printer_data:
        metric = collectd.Values()
        metric.plugin = 'printer_status'
        metric.type = 'gauge'
        metric.type_instance = key
        metric.values = [printer_data[key]]
        metric.dispatch()

  except Exception as e:
    collectd.info(str(e))

###REGISTER FUNCTIONS
collectd.register_config(config_callback)
collectd.register_read(read_callback)
