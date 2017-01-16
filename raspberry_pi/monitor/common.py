#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os                           # Used for local system information gathering
from subprocess import PIPE, Popen  # Used for local system information gathering
import requests                     # Used to gather HTTP POST and GET data
import json                         # used for processing data
import psutil                       # Used for local system information gathering
import platform                     # Used for local system information gathering
import datetime
import netifaces as ni              # Used for local system information gathering
import config as cfg                # Bring in shared configuration file
import humanize                     # Convert data to more easily read formatts
import sys
import time

'''
========================================================================================================
SYNOPSIS
    'common.py' is the script that holds all the functions used in 'monitor.py'
    
DESCRIPTION
    This script contains all the functions used to process sensor configuration information from 'config.py'
        and executed by 'monitor.py'

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
    'ver': '1.4',
    'name': 'common.py',
    'cpu_wait': 2             # how long to wait after read_sys_stats is called and CPU usage is measured
    }


def chk_cache():
    #############################################################################
    # Function: chk_cache                                                       #
    # Purpose:  Check for local cache files that indicate that connectivity to  #
    #           server has been lost and that records are waiting to be sent to #
    #           the common server.                                              #
    # @param    none         this function looks for all cache files            #
    #                                                                           #
    # @return # of records (lines) and # of files (cache_ct)                    #
    #############################################################################
    cache_ct = 0
    lines = 0
    err = 1
    try:
        for file in os.listdir(cfg.logs['cachedir']):
            with open(cfg.logs['cachedir']+file) as f:
                lines = lines + sum(1 for _ in f)
            cache_ct = cache_ct + 1
            err = 0
    except:
        print('Unable to read from '+cfg.logs['cachedir']+' in chk_cache: - '+ str(sys.exc_info()[0]))
        writeevt('Unable to read from '+cfg.logs['cachedir']+' in chk_cache: - '+ str(sys.exc_info()[0]),'log','WARN','','')
        return None
    if err == 0:    
        if cache_ct != 0 or lines != 0:
            writeevt('Current cache status: ' + str(cache_ct) + ' files containing '+ str(lines) + ' records.','log','INFO','',"")

    return (cache_ct, lines)


def clear_cache(_authkey):
    ##############################################################################
    # Function: clear_cache                                                      #
    # Purpose:  Looks for files in the cache directory, and if it finds them, it #
    #           tries to send them to the server.  It counts the lines in the    #
    #           file, and passes them to the server one by one.  It counts the   #
    #           number of HTTP:200 responses, and if the line count is the same, #
    #           then it will delete the file.  Telemetry will be sent to the     #
    #           appropriate device based on the cache file name                  #
    #                                                                            #
    # @param    authkey     Used to define which cache files are cleared so that #
    #                       that specific caching can be defined per sensor or   #
    #                       device without affecting others on the same system   #
    #                                                                            #
    # @return   none                                                             #
    ##############################################################################
    ct_files = 0                  # used to count files in cache directory
    ct_lines = 0                  # used to count records in cache files
    ct_200 = 0                    # counts successful posting of cache records
    try:
        for file in os.listdir(cfg.logs['cachedir']):
            authkey = (file.split('_'))
            if _authkey == authkey[0]:
                _tele = cfg.conn['method'] + '://' + cfg.conn['server'] +'/api/v1/'+_authkey +'/telemetry'
                
                with open(cfg.logs['cachedir']+file) as f:
                    for line in f:
                        ct_lines = ct_lines + 1
                        try:
                            if cfg.conn['proxy'] == 1:
                                r_cache = requests.post(_tele, data=line, headers=cfg.http_headers, proxies=cfg.proxies)   
                            else:
                                r_cache = requests.post(_tele, data=line, headers=cfg.http_headers)
                            if r_cache.status_code == 200:
                                ct_200 = ct_200 + 1
                            err = 0
                            
                        except:
                            writeevt('Unexpected error in clear_cache: - '+ str(sys.exc_info()[0]),'log','WARN','',"")
                            writeevt('Unable to connect to server to clear cache.  No action taken','log','WARN','',"")
                            err = 1
                        
                if err == 0:
                    ct_files = ct_files + 1
                    if ct_lines == ct_200:
                        os.remove(cfg.logs['cachedir']+file)
                        writeevt('Cache successfully cleared or device ' + authkey[0] +'. '+ str(ct_200) + ' records submitted','log','INFO','',"")
                    else:
                        print("Unexpected error in clear_cache:", sys.exc_info()[0])
                        writeevt('Unexpected error in clear_cache: - '+ sys.exc_info()[0],'log','WARN','',"")
    except:
        print('Unable to read from '+cfg.logs['cachedir']+' in clear_cache: - '+ str(sys.exc_info()[0]))
        writeevt('Unable to read from '+cfg.logs['cachedir']+' in clear_cache: - '+ str(sys.exc_info()[0]),'log','WARN','','')
        return None
    return

def read_ds18b20(_device,_label):
    #############################################################################
    # Function: read_ds18b20                                                    #
    # Purpose:  Reads the temperature as reported by the Dallas Semiconductor   #
    #           ds18b20 1-Wire temperature  sensor, and returns the temp        #
    # @param    _device    Defines the local 1-Wire device to be polled for     #
    #                      current temperature.                                 #
    # @param    _label     appended to the temp value to differentiate between  #
    #                      more than one sensor on a single device              #
    #                                                                           #
    # @return   ds18b20    current temperature in *F                            #
    #############################################################################
    try:
        fileobj = open(_device,'r') #read the file for this specific temp probe
        lines = fileobj.readlines()
        fileobj.close()
        err = 0

    except:
        print("Unexpected error in read_ds18b20:", sys.exc_info()[0])
        writeevt('Unexpected error in read_ds18b20: - '+ str(sys.exc_info()[0]),'log','WARN','',"")

        err = 1

    if err == 0:
        readraw = lines[1][0:]				       # read the second line, beginning to end
        temp_c = readraw.split("t=",1)[1]		# split everything from t= into temp_c
        temp_c = float(int(temp_c))				    # temp_c is read as string, convert to int then float
        temp_c=temp_c/1000				       # values is in 1,000's -- divide to bring to degree units
        temp_f=(temp_c * 9.0/5.0 + 32)
        temp = float(temp_f)
        ds18b20 = { 'tele': {
                        'temp'+_label: round(temp,1)
                        }}
    elif err == 1:
        ds18b20 = { 'tele': {
                        'temp_'+_label: 'error'
                        }}

    
    return ds18b20

def read_owmapi(_device,_label):
    #############################################################################
    # Function: read_owmapi                                                     #
    # Purpose:  Connects to OpenWeatherMaps service and downloads the current   #
    #           conditions for the ZIP code defined in _device.  Once obtained, #
    #           it is parsed into more easily consumed data                     #
    # @param    _device    Defines the location ZIP code to be polled for       #
    #                      current conditions.                                  #
    #                                                                           #
    # @return   conditions    current conditions as list of dictionaries        #
    #############################################################################
     # Connect to OpenWeatherMaps and get information for the defined ZIP code
     try:
         if cfg.conn['proxy'] == 1:
            f = requests.get(cfg.owm_url+'&zip='+_device, proxies=cfg.proxies)
         else:
            f = requests.get(cfg.owm_url+'&zip='+_device)
         if f.status_code != 200:
            writeevt('Connection to weather data failed, returned code:'+f.status_code,'log','WARN','','')
            temp = 'na'
            err = 1
         else:
            err = 0
     except:
        writeevt('Error in gathering weather information in read_owmapi: - '+ str(sys.exc_info()[0]) + ' ','log','WARN','','')
        err = 1
        conditions = { 'tele': {
                           'temp'+_label: 'error'
                           }
                       }
     
     if err == 0:
        parsed_json = json.loads(f.text)

        temp = int(((parsed_json['main']['temp'])*9/5.0)-459.67)
        if int(parsed_json['wind']['speed']) >=3 and int(temp) <= 50:
            T = temp
            V = int(parsed_json['wind']['speed'])
            windchill = int(35.74 + (0.6215*T) - 35.75*(V**0.16) + 0.4275*T*(V**0.16))
        else:
            windchill = temp
            
        conditions = { 'tele': {
                          'temp'+_label: temp,
                          'humidity': int(parsed_json['main']['humidity']),
                          'wind_speed': parsed_json['wind']['speed'],
                          'wind_direction': parsed_json['wind']['deg'],
                          'wind_chill': windchill,
                          'visibility': parsed_json['visibility'],
                          'pressure': int(parsed_json['main']['pressure'])
                          },
                       'attr': {
                           'latitude': parsed_json['coord']['lat'],
                           'longitude': parsed_json['coord']['lon']
                           }
                       }
     return conditions

def read_sensor(_device,_type,_label):
    #############################################################################
    # Function: read_sensor                                                     #
    # Purpose:  Reads the type of sensor that is being requested, and calls the #
    #           appropriate function for that device.                           #
    # @param    _device    Defines the device that is to be queried by the      #
    #                      appropriate function                                 #
    # @param    _type      Used to determine the appropriate function to process#
    #                      the device in _device                                #
    # @param    _label     value appended temp value key (temp_[_label]         #
    #                                                                           #
    # @return   conditions  current conditions as list of dict                  #
    #############################################################################
    if _type == 'ds18b20':
        conditions = read_ds18b20(_device,_label)
    
    elif _type == 'owm':
        conditions = read_owmapi(_device,_label)

    elif _type == 'wund':
        conditions = read_wund(_device,_label)

    else:
        conditions = { 'tele': {
                           'temp': 'error'
                           },
                        'attr': {
                            _type + '_error': _device
                            }
                        }
    return conditions

def read_sys_stats():
    #############################################################################
    # Function: read_sys_stats                                                  #
    # Purpose:  Gathers information on the local system to be used for tracking #
    #           resource use and to be able to head off issues before they cause#
    #           a loss of attribute/telemetry feeds                             #
    # @param    none                                                            #
    #                                                                           #
    # @return   sys_stats  current system conditions as list of dict            #
    #############################################################################
    time.sleep(me['cpu_wait'])
    cpu_usage = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    
    disk = psutil.disk_usage('/')
    disk_total = disk.total / 2**30     # GiB.
    disk_used = disk.used / 2**30
    disk_free = disk.free / 2**30
    disk_percent_used = disk.percent
    
    if os.name == 'posix':
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        output, _error = process.communicate()
        temp_c = float(output[output.index('=') + 1:output.rindex("'")])
        temp_f = 9.0/5.0 * temp_c + 32
        cpu_temp = round(temp_f,1)
    else:
        cpu_temp = 'N/A'
    
    lastboot = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    c = time.time() - psutil.boot_time()
    days =  int(c // 86400)
    hours = int(c // 3600 % 24)
    minutes = int(c // 60 % 60)
    uptime = (str(days) + 'days, ' + str(hours) + 'hrs, '+ str(minutes) + "mins.")

    sys_stats = { 'tele': {
            'cpu_temp': cpu_temp,
            'cpu_used': psutil.cpu_percent(interval=1, percpu=False),
            'ram_used': mem.percent,
            'disk_used': disk.percent
            },
        'attr': {
             'disk_total': humanize.naturalsize(disk.total, binary=True),
             'ram_total': humanize.naturalsize(mem.total, binary=True),
             'os_type': os.name,
             'os_platform': platform.system(),
             'os_release': platform.release(),
             'last_boot': lastboot,
             'uptime': uptime
          }
       }

    # Get a list of the local network interfaces, and their IP addresses
    ifaces = ni.interfaces();
    for x in ifaces:
        try:
            ip = ni.ifaddresses(x)[2][0]['addr']
            sys_stats['attr'][x] = ip
        except:
            sys_stats['attr'][x] = "none"

    return sys_stats

def read_wund(_device,_label):
    #############################################################################
    # Function: read_wund                                                       #
    # Purpose:  Connects to WeatherUnderground service and downloads the        #
    #           current conditions for the ZIP code defined in _device.  Once   #
    #           obtained it is parsed into more easily consumed data            #
    # @param    _device    Defines the location ZIP code to be polled for       #
    #                      current conditions.                                  #
    #                                                                           #
    # @return   conditions    current conditions as list of dictionaries        #
    #############################################################################
    try:
         if cfg.conn['proxy'] == 1:
            f = requests.get(cfg.wund_url+_device+'.'+cfg.wund_settings['wund_format'], proxies=cfg.proxies)
         else:
            f = requests.get(cfg.wund_url+_device+'.'+cfg.wund_settings['wund_format'])
         if f.status_code != 200:
            writeevt('Connection to weather data failed, returned code:'+conditions.status_code,'log','WARN','','')
            temp = 'na'
         else:
             err = 0
    except:
        writeevt('Error in gathering weather information in read_wund: - '+ str(sys.exc_info()[0]) + ' ','log','WARN','','')
        wund = { 'tele': {
                           'temp'+_label: 'error'
                           },
                        'attr': {
                            'weather_status': 'error'
                            }
                       }
        err = 1

    if err == 0:
        parsed_json = json.loads(f.text)
        wund = { 'tele': {
                          'temp'+_label: parsed_json['current_observation']['temp_f'],
                          'humidity': int(parsed_json['current_observation']['relative_humidity'].strip('%')),
                          'wind_speed': parsed_json['current_observation']['wind_mph'],
                          'wind_direction': parsed_json['current_observation']['wind_degrees'],
                          'wind_chill': int(parsed_json['current_observation']['windchill_f']),
                          'wind_gusts': int(parsed_json['current_observation']['wind_gust_mph']),
                          'visibility': float(parsed_json['current_observation']['visibility_mi']),
                          'pressure': int(parsed_json['current_observation']['pressure_mb']),
                          'precip_today': float(parsed_json['current_observation']['precip_today_in']),
                          'dewpoint': int(parsed_json['current_observation']['dewpoint_f']),
                          'uv_index': int(parsed_json['current_observation']['UV'])
                          },
                       'attr': {
                           'latitude': parsed_json['current_observation']['observation_location']['latitude'],
                           'longitude': parsed_json['current_observation']['observation_location']['longitude']
                           }
                       }
        
    return wund

def writeevt(_record,_type,_sev,_authkey, _name):
    #############################################################################
    # Function: writeevt                                                        #
    # Purpose: Acts as centralized logging facility - creates logs, records, and#
    #          cache files                                                      #
    # @param        _record           message payload                           #
    # @param        _type             log, cache, record                        #
    # @param        _sev              log severity (WARN, INFO, etc)            #
    # @param        _authkey          authkey when used for caching telemetry   #
    # @param        _name             name of the device in question, for log   #
    #                                                                           #
    #       @return none                                                        #
    #############################################################################
    if _type == 'cache':
        _outfile = cfg.logs['cachedir'] + _authkey +"_" + time.strftime("%Y-%m-%d") + '.cache'
        _entry = _record
    elif _type == 'log':
        _outfile = cfg.logfile
        _entry = time.strftime("%Y-%m-%d %H:%M:%S") + " - " + _sev + ": " + str(_record)
    else:
        print('Wrong message type ' + _type + ' check your code and try again')
        return
    try: 
        outfile=open((_outfile),"a")
        outfile.write(_entry)
        outfile.write("\n")
        outfile.close()
    except:
        print('Unable to write to '+_outfile+': - '+ str(sys.exc_info()[0]))
        return None

def publish(_attr, _message,_authkey,_cache_on_err):
    ##############################################################################
    # Function: publish                                                          #
    # Purpose:  Take attribute and telemetry and publish it to the server.  If   #
    #           configured to do local only, or if it is unable to connect to the#
    #           server, it will write to cache files                             #
    # @param    _attributes        client side attributes to be published        #
    # @param    _message           client-side telemetry to be published         #
    # @param    _method            transportation method to the server           #
    # @param    _cache_on_err      if connection down, cache to disk             #
    #                                                                            #
    #       @return status             indicator of status - temp                #
    ##############################################################################
    
    url = {
    'attr': cfg.conn['method'] + '://' + cfg.conn['server'] +'/api/v1/'+ _authkey +'/attributes',
    'tele': cfg.conn['method'] + '://' + cfg.conn['server'] +'/api/v1/'+ _authkey +'/telemetry',
    }

    if cfg.conn['method'] == 'http':
        _cache = '{"ts":' + str(time.time() * 1000) + ', "values":' + json.dumps(_message) + '}'
        try:
            if cfg.conn['proxy'] == 1:
                r_attr = requests.post(url['attr'], data=json.dumps(_attr), headers=cfg.http_headers, proxies=cfg.proxies)
                r_tele = requests.post(url['tele'], data=json.dumps(_message), headers=cfg.http_headers, proxies=cfg.proxies)   
            else:
                r_tele = requests.post(url['tele'], data=json.dumps(_message), headers=cfg.http_headers)
                r_attr = requests.post(url['attr'], data=json.dumps(_attr), headers=cfg.http_headers)
            if r_attr.status_code != 200 or r_tele.status_code != 200:
                _event = 'Unable to push data to server, returned codes: Attributes: '+ str(r_attr.status_code) +', Telemetry: ' + str(r_tele.status_code)
                writeevt(_event,'log','WARN','',"")
                if _cache_on_err == 1:
                    writeevt(_cache,'cache','',_authkey,'')
                else:
                    writeevt('Record not written to cache due to configuration','log','WARN','',"")
                status = 0
            else:
                
                status = 1
        except:
            writeevt('Unable to publish record to server due to error: - '+ str(sys.exc_info()[0]) + ' ','log','WARN','','')
            if _cache_on_err == 1:
                writeevt(_cache,'cache','',_authkey,'')
            else:
                writeevt('Record not written to cache due to configuration','log','WARN','',"")
            status = 0
    else:
        return "wrong method"
    return status