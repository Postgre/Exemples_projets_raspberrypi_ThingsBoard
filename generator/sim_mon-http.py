#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import random
import time
import requests
import config as cfg         # Bring in shared configuration file

'''
####################################################################
SYNOPSIS
    'sim_mon-http.py' is a script that generates device and sensor data
    for use with ThingsBoard IoT platform
    
DESCRIPTION
    This script looks for the file "config.py" which contains the sensor
    details.  As configured, it generates the following:

    Attributes:
        Type            Descriptive field that allow for common groupings
        Disk Size       Amount of disk on endpoint devices - for monitoring resources
        RAM Installed   Amount of RAM on endpoint devices - for monitoring resources
        Platform        Decription of the source device (Raspberry Pi, NodeMCU, etc)
        Name            Common descriptive name, such as "Lab Freezer"
        Location        Descriptive name, such as "Main Campus"
        Address         Street address
        Lattitude       Lattitude, for Google Maps pin placement - use www.latlong.net
        Longitude       Longitude, for Google Maps pin placement - use www.latlong.net
        Contact         Person to be contacted in the event of failure, alarms, etc
        Contact Email   Email of the primary owner or alarm destination
        Contact Phone   Phone number of the primary owner

    Telemetry:
        Temp            Generated as a random number between the temp_low and temp_high
                        attributes
        CPU Temp        Temp of the CPU
        CPU Used        Percentage of CPU used
        Disk Used       Percentage of installed Disk being used
        RAM Used        Percentage of RAM being used

    In the event you would like to only generate cached records, you can do so by setting
        the "localonly" and 'caching' options in config.py to '1'.  This will write the
        telemetry data only to the specified cache directory in a format that can be used
        to import the data at a later time, preserving the event time stamp.

REQUIRES
    The following requirements must be met
        python-requests        Used to generate HTTP Post to Thingsboard server
        Thingsboard Server     As configured in config.py, it is the destination
                               to which information is sent.  You can get a demo
                               account at http://demo.thingsboard.io
        
AUTHOR
    Bob Perciaccante - Bob@perciaccante.net
    
VERSION
    1.0.1 - 1/3/2017 - Initial publication
####################################################################
'''

me = {
    'type': 'Simulated',
    'wait': 600              # Number of seconds between runs
    }

def writeevt(_record,_type,_sev,_authkey):
    #############################################################################
    # Function: writeevt                                                        #
    # Purpose: Acts as centralized logging facility - creates logs, records, and#
    #          cache files                                                      #
    # @param        _record           message payload                           #
    # @param        _type             log, cache, record                        #
    # @param        _sev              log severity (WARN, INFO, etc)            #
    # @param        _authkey          authkey when used for caching telemetry   #
    #                                                                           #
    #       @return none                                                        #
    #############################################################################
    if _type == 'cache':
        if cfg.logs['caching'] == 1:
            _outfile = cachefile = cfg.logs['cachedir'] + _authkey + '-' + time.strftime("%Y-%m-%d") + '.cache'
            _entry = _record
        else:
            return
    elif _type == 'log':
        if cfg.logs['logging'] == 1:
            _outfile = cfg.logs['logdir'] + '/' + cfg.logs['logfile']
            _entry = time.strftime("%Y-%m-%d %H:%M:%S") + " - " + _sev + ": " + str(_record)
        else:
            return
    else:
        print('Wrong message type ' + _type + ' check your code and try again')
    
    try: 
        outfile=open((_outfile),"a")
        outfile.write(_entry)
        outfile.write("\n")
        outfile.close()
    except:
        print('Error writing events to cache')
        return None

def main():
    writeevt('Started processing at ' + time.strftime("%Y-%m-%d %H:%M:%S"),'log','START','')
    while True:
        s_count=0

        telemetry = {
            'sensorcount': len(cfg.sensors),
            }

        for (id) in cfg.sensors:
            if cfg.sensors[s_count]["active"] == 1:
                url = {
                    'attr': cfg.conn['method'] + '://' + cfg.conn['server'] +'/api/v1/'+cfg.sensors[s_count]['authkey'] +'/attributes',
                    'tele': cfg.conn['method'] + '://' + cfg.conn['server'] +'/api/v1/'+cfg.sensors[s_count]['authkey'] +'/telemetry' }

                attributes = {
                    'Type': cfg.sensors[s_count]['Type'],
                    'Platform': cfg.sensors[s_count]['Platform'],
                    'Name': cfg.sensors[s_count]['Name'],
                    'Location': cfg.sensors[s_count]['Location'],
                    'Address': cfg.sensors[s_count]['Address'],
                    'Lattitude': cfg.sensors[s_count]['Lattitude'],
                    'Longitude': cfg.sensors[s_count]['Longitude'],
                    'Contact': cfg.sensors[s_count]['Contact'],
                    'Contact Email': cfg.sensors[s_count]['Contact Email'],
                    'Contact Phone': cfg.sensors[s_count]['Contact Phone']
                    }

                telemetry = {
                    'Temp': random.randrange((cfg.sensors[s_count]['temp_low']),(cfg.sensors[s_count]['temp_high']),1),
                    'CPU Temp': random.randrange(100,120,1),
                    'RAM Used': random.randrange(60,80,1),
                    'Disk Used': random.randrange(60,80,1),
                    'CPU Used': random.randrange(25,28,1)
                    }
                
                if cfg.logs['localonly'] != 1:
                    r_tele = requests.post(url['tele'], data=json.dumps(telemetry), headers=cfg.http_headers)
                    r_attr = requests.post(url['attr'], data=json.dumps(attributes), headers=cfg.http_headers)

                    if r_attr.status_code != 200 or r_tele.status_code != 200:
                        print('Error posting data - check your code')

                _cache = '{"ts":' + str(time.time() * 1000) + ', "values":' + json.dumps(telemetry) + '}'
                writeevt(_cache,'cache','',cfg.sensors[s_count]['authkey'])
                s_count = s_count + 1

        writeevt('Posted ' + str(s_count) + " records at " + time.strftime("%Y-%m-%d %H:%M:%S"),'log','INFO','')
        time.sleep(me['wait'])
    
if __name__ == '__main__':
    main()



