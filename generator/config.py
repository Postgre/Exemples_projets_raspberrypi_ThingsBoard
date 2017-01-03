#!/usr/bin/env python
import sys
import time
import random

'''
####################################################################
SYNOPSIS
    'config.py' is a configuration script that is used in conjunction with
    'sim_mon-http.py to generate device and sensor data for use with ThingsBoard IoT platform
    
DESCRIPTION
    This script defines bulk sensor data that is used in 'sim_mon-http.py'. As configured,
    it generates the following:

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
        Temp is generated in the 'sim_mon-http.py' script, generating a random number between
            the "temp_low" and "temp_high" values for each sensor.

    In the event you would like to only generate cached records, you can do so by setting
        the "localonly" and 'caching' options in config.py to '1'.  This will write the
        telemetry data only to the specified cache directory in a format that can be used
        to import the data at a later time, preserving the event time stamp.

    It is possible to extend the attributes or telemetry values by adding them to the below
        configurations, and adding them to the appropriate line in 'sim_mon-http.py'

REQUIRES
    The following requirements must be met
        Thingsboard Server      As configured in config.py, it is the destination
                                to which information is sent.  You can get a demo
                                account at http://demo.thingsboard.io
        Thingsboard Device      The "authkey" as defined in the below configuration is the
                                device authentication key from the Thingsboard device.  This
                                device must be defined prior to running this script, or it
                                reject the requests to publish.
        
AUTHOR
    Bob Perciaccante - Bob@perciaccante.net
    
VERSION
    1.0.1 - 1/3/2017 - Initial publication
####################################################################
'''

# Connection information to the ThingsBoard server
conn = {
    'server': 'demo.thingsboard.io',              # IP or hostname of manager    
    'method': 'http',                             # Method used to send data to TB server
    }

sensors = [
    {'authkey': '[YOUR DEVICE #1 KEY HERE]',       # Use the device auth key as created in your Thingsboard server
        'active': 1,                               # (0,1) If not 1 then sensor will be ignored
        'Type': 'Freezer - Reach In',              # Descriptive device type
        'Disk Size': '8GB',                        # Amount of installed DISK
        'Platform': "Raspberry Pi Zero",           # Platform information - what type of device is it
        'Name': 'Main Lab Freezer',                # Name of the sensor, descriptive
        'Location': 'NYC Office',                  # Common name of location
        'Address': ' 350 5th Ave, New York, NY 10118',                 # Street address where device is located
        'Lattitude': 40.748441,                    # Used for Google Maps geolocation
        'Longitude': -73.985664,                   # Used for Google Maps geolocation
        'Contact': 'Main Security',                # Primary contact responsible for area being monitored
        'Contact Email': 'security@tld.net',       # Primary contact email address
        'Contact Phone': '201-555-1212',           # primary contact phone
        'temp_low': -5,
        'temp_high': 10},
    {'authkey': '[YOUR DEVICE #2 KEY HERE]',       # Use the device auth key as created in your Thingsboard server
        'active': 1,                               # (0,1) If not 1 then sensor will be ignored
        'Type': 'Fridge - Reach In',              # Descriptive device type
        'Disk Size': '8GB',                        # Amount of installed DISK
        'Platform': "Raspberry Pi Zero",           # Platform information - what type of device is it
        'Name': 'Main Lab Fridge',                # Name of the sensor, descriptive
        'Location': 'NYC Office',                  # Common name of location
        'Address': ' 350 5th Ave, New York, NY 10118',                 # Street address where device is located
        'Lattitude': 40.748441,                    # Used for Google Maps geolocation
        'Longitude': -73.985664,                   # Used for Google Maps geolocation
        'Contact': 'Main Security',                # Primary contact responsible for area being monitored
        'Contact Email': 'security@tld.net',       # Primary contact email address
        'Contact Phone': '201-555-1212',           # primary contact phone
        'temp_low': 33,
        'temp_high': 39}
        ]


logs = {
        'caching': 1,                # (0,1) If enabled, telemetry will be cached locally,
        'localonly': 1,              # (0,1) If enabled, telemetry will be cached and not published
        'cachedir': 'cache/',        # Location where cache files will be stored
        'logging': 1,                # (0,1) If enabled, system will keep logged messages
        'logdir': 'logs/',           # where log files will be kept
        'logfile': time.strftime("%Y-%m-%d") + '_messages.log'     # log file name
    }

# This section will pull together values above to make references in code easier
http_headers = {'Content-Type': 'application/json'}
