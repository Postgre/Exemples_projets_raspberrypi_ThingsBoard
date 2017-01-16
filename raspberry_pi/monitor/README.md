This set of scripts is intended to help you get started with telemetry gathering on a Raspberry Pi, and send it to 
   a Thingsboard server for graphing, alerting, and archiving.  While Thingsboard supports both publish and subscribe,
   this particular set of scripts is intended to simply publish telemetry and API call data through HTTP, making it
   ideal for use behind corporate proxy servers.  Future iterations will incorporate not only subscription through
   HTTP, but also the use of MQTT for publication and subscription, making your devices truly interconnected.

The following transport methods are supported:
- HTTP - supports using HTTP as transport as well as supporting HTTP proxy configurations

The following hardware sensors are supported with native functions:
- ds18b20
- local system statistics (disk, memory, CPU, temp)

The following external API calls are natively supported
- OpenWeatherMaps
- Weather Underground

The following features are also in place:
- Offline caching - cache telemetry to a file that can be imported later
- Net-down caching - when network connectivity is lost, events are cached until connectivity restored

Coming soon:<br>
--------------------------------------------------<br>
Sensor support:
- DHT22
- serial GPS (for location tracking)
- water sensor
- door contact switches

Transport Support
- HTTPS (encryption)
- HTTPS (authentication)
- MQTT
