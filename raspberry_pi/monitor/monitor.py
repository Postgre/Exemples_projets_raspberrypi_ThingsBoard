#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json                  # Used for data manipulation
import time                  # Usef for timestamps, etc
import requests              # Used to generate HTTP GET and POST actions
import config as cfg         # Bring in config.py configuration file
import common as com         # Bring in common.py shared functions
import logging

'''
========================================================================================================
SYNOPSIS
    'monitor.py' is the script that gathers sensor configuration from the sensors as defined in
        'config.py', processes the necessary information prior to publishing it to a ThingsBoard
        server.  In the event data cannot be published, there are options to cache telemetry locally
        until the server becomes available again.
    
DESCRIPTION
    This script in effect acts as a conduit between configuration information stored in 'config.py'
        and the functions defines in 'common.py'.  This script gathers the configuration information
        and determines what steps need to be taken to convert the configuration settings into data
        to be published to the Thingsboard server.

    To the degree possible, I have attempted to make this as painless as possible, relying heavily
        on reuable functions in common.py that allow for extensibility and managability.  I am always
        looking for feedback, so please feel free to email me at the email address below.

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
    
========================================================================================================
'''

me = {
    'version': '1.5',
    'wait': 10,              # Number of seconds between polling runs
    'sleep_poll': 10         # Number of seconds between individual sensor runs
    }


def main():
    # Set basic logging configuration
    if cfg.settings['debug'] == 1:
        logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s - [%(levelname)s] [%(threadName)s] (%(module)s:%(lineno)d) %(message)s",
                        filename=cfg.logfile)
    elif cfg.settings['debug'] == 0:
        logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] [%(threadName)s] (%(module)s:%(lineno)d) %(message)s",
                        filename=cfg.logfile)
    else:
        logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s - [%(levelname)s] (%(module)s:%(lineno)d) %(message)s")
    
    # Before starting everything, make sure that the cache and log directories are available
    #     since these are critical to operation
    if os.path.exists(cfg.logs['logdir']) != True or os.path.exists(cfg.logs['cachedir']) != True:
        logging.warn('unable to write to logfile')
        return

    # Send initial information to the logfile to facilitate 
    logging.info('=================================================================')
    logging.info('Started processing at ' + time.strftime("%Y-%m-%d %H:%M:%S"))
    logging.info('Sensor readings collected every ' + str(me['wait']) + ' seconds')
    logging.info('Currently configured sensors:')
    
    # Gather information on configured sensors and log
    sensors = {
        'active': 0,
        'total': 0
        }
    for item_i in cfg.sensors:
        set_i = item_i['settings']
        attr_i = item_i['attr']
        sensors['total'] = sensors['total'] + 1

        # Gather the information that is set per sensor, and log the status of the environment to logfile
        sens_state = 'ID: %s - "%s": Active: %s, LocalOnly: %s, Cache on Error: %s, Include SysInfo: %s, Clear cache: %s'  % \
          (item_i['id'],
           attr_i['name'],
           str(set_i['active']),
           str(set_i['localonly']),
           str(set_i['cache_on_err']),
           str(set_i['sys_info']),
           str(set_i['clearcache'])
           )
        if set_i['active'] == 1:
            sensors['active'] = sensors['active'] + 1
        logging.info(sens_state)
        
    logging.info('Total Sensors Configured: ' + str(sensors['total']) + ', Active: '+str(sensors['active']))

    # Run through the sensor information, and process where configured as "active'
    while True:
        logging.debug('Running sensor poll')
        com.chk_cache()
        logging.debug('Checking cache status')
        for item in cfg.sensors:
            message = {}
            set = item['settings']

            # If the sensor is configured to clear exsiting cache, check and run
            if set['clearcache'] == 1:
                logging.debug('Preparing to clear cache files')
                com.clear_cache(item['authkey'])

            # Check to see if the device is configured to be active - if not, then skip
            if set['active'] == 1:
                attr = item['attr']
                tele = item['tele']
                
                # Get system information (CPU, Ram, etc) if configured
                if set['sys_info'] == 1:
                    sys_info = com.read_sys_stats()
                    for key, value in sys_info['attr'].items():
                        attr[key] = value
                    for key, value in sys_info['tele'].items():
                        message[key] = value

                # Gather sensor data and add to the telemetry data
                conditions = com.read_sensor(tele['device'],tele['type'],tele['label'])

                # Since not all sensors will not add attributes, if there are none returned, then continue
                try:
                    for key, value in conditions['attr'].items():
                        attr[key] = value
                except:
                    None
                for key, value in conditions['tele'].items():
                    message[key] = value

                pub_status = com.publish(attr,message,item['authkey'],set['cache_on_err'],set['localonly'])
                time.sleep(me['sleep_poll'])

        logging.debug('Completed sensor poll')            
        time.sleep(me['wait'])

if __name__ == '__main__':
    main()