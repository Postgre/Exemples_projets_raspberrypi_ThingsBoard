# Thingsboard
To learn more about Thingsboard, visit the website at http://thingsboard.io<br><br>
Join the Thingsboard Users Group on Facebook at https://www.facebook.com/groups/thingsboardusers/<br><br>
The contents of this repo are a collection of tools and scripts written to help folks interested in the 
Internet of Things (IoT) and learning how the different pieces of information throughout our lives can be
brought together into a single place where data turns into information.

Each of the folders in this repo represent different tools or techniques for gathering telemetry information,
presenting that information into ThingsBoard, as well as having a set of tools that you can use to better help
learn overall.

Currently, the repo contains:

generator/<br>
- A tool to generate traffic to a Thingsboard server to help learn the platform.  This will generate device 
    (client) attributes as well as basic telemetry data to give you a starting point.

raspberry_pi/monitor<br>
- A framework for managing multiple sesnsors on one or more devices.  The modular framework will allow you to
     read many differnt sources and send to many different TB devices.  If network connections are down, then the 
     script will cache telemetry information until the network connection returns.  You can also tell the sensors
     to cache only, allowing you to create telemetry information completely offline, to be imported at a later date
     (timestamps of initial datapoints are retained in the cached records). Heavily commented, I expect that there
     will be many different use cases that this might help address, at least as a starting point
    
Open Warning:<br>
    I will do my best to document and test my code, but it is presented here as a "best-effort", and is not to
    be considered for production use.
    
Feedback, comments, and assistance are always appreciated!
