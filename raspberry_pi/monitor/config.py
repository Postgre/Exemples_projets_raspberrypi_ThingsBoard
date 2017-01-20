#!/usr/bin/env python
import sys
import time


'''
========================================================================================================
SYNOPSIS
    'config.py' holds all the information needed to run the 'monitor.py' script to publish telemetry
        and attributes to a Thingsboard IoT server.
    
DESCRIPTION
    This script contains all the necessary configuration settings to gather telemetry information and
        submit to a Thingsboard server.  This file is heavily commented to make sure that you understand
        the different options, and their purposes.

REQUIRES
    The following requirements must be met
        Thingsboard Server      As configured in config.py, it is the destination
                                to which information is sent.  You can get a demo
                                account at http://demo.thingsboard.io
        Thingsboard Device      The "authkey" as defined in config.py is a unique key
                                for each device in Thingsboard, and defines the target
                                to which telemetry and attribute information will be published.
        Required libraries      See top of script for the list of python libraries needed, and their use
        
AUTHOR
    Bob Perciaccante - Bob@perciaccante.net
    
VERSION
    1.4 - 1/15/2017 - Initial publication
========================================================================================================
'''

me = {
    'ver': '1.5',
    'name': 'config.py'
    }
'''
========================================================================================================
Connection Configuration:
---------------------
This section defines how your host will connect to the Thingsboard server.

*Note* you will need to have an account on the Thingsboard Demo server, located at http://demo.thingsboard.io
    or you will need to have a local installation of Thingsboard.

In order to support the publication of telemetry and attributes via HTTP through a proxy, if necessary you can
    define the proxy needed below.  The actual hosts will be ignored if 'proxy' is set to 0
========================================================================================================
    
'''
conn = {
    'server': '[YOUR SERVER HERE]',              # IP or hostname of manager    
    'port': 1883,                                 # MQTT server port number (MQTT transport not yet supported in this script)
    'method': "http",                             # Method used to send data to TB server
    'proxy': 0,                                   # (0,1) If you need to go through a proxy, set to 1
    'proxy_http': '[HTTP://YOUR HTTP SERVER:PORT]',
    'proxy_https': '[HTTPS://YOUR HTTP SERVER:PORT]'
    }

settings = {
         'debug': 0
         }

# These values are used for HTTP POST operations, and supporting the use of proxies easily in functions in
#    'common.py'

http_headers = {'Content-Type': 'application/json'}
proxies = {
     'http': conn['proxy_http'],
     'https': conn['proxy_https']
    }
'''
========================================================================================================
Sensor Configuration:
---------------------

The sensor definitions are broken up into four sections: notes, settings, attributes, and telemtry (sources).

** Note ** the 'id' value must be unique for each sensor definition.  As of version 1.5, the 'id' value allows
    the script to process multiple local sensor devices, and associate them with a single device, or the
    inverse, take data from the same sensor and publish it to several different devices.  If you are going
    to post multiple sensor data to the same device, be careful not to overlap device attributes!  Simply
    exclude the duplicate attributes in the second sensor definition.

Notes:
    Since it can become confusing keeping track of different sensors based primarily on device auth token,
        this section is completely free-form, and is not used for any processing.  This should allow you to
        include many sensors and potentially a complex deployment, with relative ease.

Settings (settings):
    Settings are required - and define how the device is handled
    |-----------------------------------------------------------------------------------------|
    |      Key     |  Value |                        Notes                                    |
    |-----------------------------------------------------------------------------------------|
    | active       | 0 or 1 | If enabled, device will be processed - otherwise will be ignored|
    |--------------|--------|-----------------------------------------------------------------|
    | sys_info     | 0 or 1 | If enabled, local machine stats will be collected. CPU Temp not |
    |              |        |   available on Win32                                            |
    |--------------|--------|-----------------------------------------------------------------|
    | cache_on_err | 0 or 1 | If enabled, telemetry will be cached if connection errors occur |
    |--------------|--------|-----------------------------------------------------------------|
    |              |        | If enabled, script will try to push cache files to server for   |
    |  clearcache  | 0 or 1 |    this sensor, even if localonly is set.  This will cause the  |
    |              |        |    last record to be cached for a period of time before being   |
    |              |        |    published - useful for troubleshooting                       |
    |--------------|--------|-----------------------------------------------------------------|
    | localonly    | 0 or 1 | If enabled, script will not try to publish, but will cache      |
    |              |        |    locally only.  Does not override clearcache                  |
    |--------------|--------|-----------------------------------------------------------------|
    
Attributes (attr):
    Attributes are free-form.  The values in the attr dictionary block are passed as-is as device
        attributes.  Note - betware that these values do not contain characters that could be
        interpreted by the server as operators - for example, use '_' instead of '-'
    
Telemetry (tele):
    Telemetry keys are where the processing of sensor data takes place.  Currently supported
        options are below:
    |-----------------------------------------------------------------------------------------|
    |      Key     |                                 Notes                                    |
    |-----------------------------------------------------------------------------------------|
    |  type        | defines the function to be used to process the 'device' key.  Functions  |
    |              |     should be added to the common.py file to keep standardized           |
    |-----------------------------------------------------------------------------------------|
    |              | defines the device or target asset to gather the appropriate telemetry.  |
    |  device      |     ds18b20: /sys/bus/w1/devices/28*/w1_slave is an example              |
    |              |     weather: incude the ZIP code of the area you want to gather telemetry|
    |              |         information on                                                   |
    |-----------------------------------------------------------------------------------------|
    |              | defines the label used to reflect that specific sensor, a temperature    |
    |              |    sensor would be sent as telemetry value 'temp[label]'.  This allows   |
    |  label       |    for more than one sensor to be installed on a single system.  This    |
    |              |    is ignored for API called telemetry, as the labels if needed will come|
    |              |    from the API data itself.                                             |
    |-----------------------------------------------------------------------------------------|

========================================================================================================
   '''
sensors = [
    { 'id': 1,
      'authkey': '[YOUR AUTHKEY HERE]',
         'notes': {
             'notes': '[YOUR DESCRIPTION HERE]',
             },
         'settings': {                
            'active':       1,
            'sys_info':     1,
            'cache_on_err': 0,
            'clearcache':   0,
            'localonly':    0
             },
         'attr': {
            'platform':      '[PLATFORM NAME]',
            'name':          '[DESCRIPTIVE NAME]',
            'location':      '[LOCATION NAME]',
            'address':       '[YOUR ADDRESS HERE]',
            'lattitude':     '[LATTITUDE - GET FROM LATLONG.NET]',
            'longitude':     '[LONGITUDE - GET FROM LATLONG.NET]',
            'contact':       '[CONTACT NAME]',
            'contact_email': '[CONTACT EMAIL]',
            'contact_phone': '[CONTACT PHONE]',
            'temp_low':      33,
            'temp_high':     39
             },
         'tele': {
            'type':          '[DEVICE TYPE]',
            'device':        '[DEVICE LOCATION]',
            'label':         '[LABEL]'
             }
     },
    { 'id': 1,
      'authkey': '[YOUR AUTHKEY HERE]',
         'notes': {
             'notes': '[YOUR DESCRIPTION HERE]',
             },
         'settings': {                
            'active':       1,
            'sys_info':     1,
            'cache_on_err': 0,
            'clearcache':   0,
            'localonly':    0
             },
         'attr': {
            'platform':      '[PLATFORM NAME]',
            'name':          '[DESCRIPTIVE NAME]',
            'location':      '[LOCATION NAME]',
            'address':       '[YOUR ADDRESS HERE]',
            'lattitude':     '[LATTITUDE - GET FROM LATLONG.NET]',
            'longitude':     '[LONGITUDE - GET FROM LATLONG.NET]',
            'contact':       '[CONTACT NAME]',
            'contact_email': '[CONTACT EMAIL]',
            'contact_phone': '[CONTACT PHONE]',
            'temp_low':      33,
            'temp_high':     39
             },
         'tele': {
            'type':          '[DEVICE TYPE]',
            'device':        '[DEVICE LOCATION]',
            'label':         '[LABEL]'
             }
      }
]

'''
========================================================================================================
Logging configurations go here and both define logging destinations, as well as assemble variables into
    more usable format in the functions called
========================================================================================================
'''
logs = {
        'cachedir': 'cache/',                                      # Location where cache files will be stored
        'logdir': 'logs/',                                         # where log file will be kept
        'logfile': time.strftime("%Y-%m-%d") + '_messages.log'     # log file name
    }
logfile = logs['logdir'] + logs['logfile']
cachefile = logs['cachedir']


'''
========================================================================================================
Custom configuration settings can be added below this point for different sensor types, add-on services,
    etc.
========================================================================================================
'''

# Settings spefically for OpenWeatherMaps integration.  To use OpenWeatherMaps, you will need an API key
#    specific to your installation.  You can get more information on API keys on their website at:
#    https://openweathermap.org/api

owm_settings = {
    'owm_api': '[YOUR OWM API HERE]',
    'owm_format': 'json',
    'owm_url': 'http://api.openweathermap.org/data/2.5/weather?us&APPID=',
    'temp_units': 'f',
    }
owm_url = owm_settings['owm_url']+owm_settings['owm_api']+'&mode='+owm_settings['owm_format']

# Settings spefically for WeatherUnderground integration.  To use WeatherUnderground, you will need an API key
#    specific to your installation.  You can get more information on API keys on their website at:
#    https://www.wunderground.com/weather/api/
wund_settings = {
    'wund_api': '[YOUR WEATHER UNDERGROUND API HERE]',
    'wund_format': 'json'
    }
wund_url = 'http://api.wunderground.com/api/'+wund_settings['wund_api']+'/geolookup/conditions/q/'
