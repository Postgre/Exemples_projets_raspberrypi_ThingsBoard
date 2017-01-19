// Based on the sample provided by Thingsboard.io
//   https://thingsboard.io/docs/samples/esp8266/temperature/

#include "DHT.h"
#include <PubSubClient.h>
#include <ESP8266WiFi.h>

#define WIFI_AP "[YOUR SSID HERE]"
#define WIFI_PASSWORD "[YOUR PASSWORD HERE]"

#define TOKEN "[YOUR AUTH KEY HERE]"

// DHT
#define DHTPIN 2          // Which GPIO Pin is sensor connected to
#define DHTTYPE DHT11     // Which sensor type - DHT11 or DHT22

char thingsboardServer[] = "[YOUR THINGSBOARD SERVER HERE]";

// Define operation settions
int unit_f = 1;          // Set this to 1 to convert temp reading to f
char temp_label[] = "\"temp_kitchen\"";
char humidity_label[] = "\"humidity_kitchen\"";
int poll_time = 10000;   // Number of milliseconds between readings



// Define device attributes. Keys are defined in getAndSendTemperatureAndHumidityData()
//  and matching values added here.  Make sure that you include escaped " at the beginning and end
//  of each string to ensure JSON is properly formatted before publication 
//  ** NOTE ** - The may length of a payload is 90 bytes - see the library documentation for more
//  details at http://pubsubclient.knolleary.net/api.html#configoptions.  Debug information
//  included to help troubleshoot
char a_name[] = "\"IoT Board\"";
char a_serialno[] = "\"20171801001\"";
char a_platform[] = "\"ESP8266\"";
char a_purpose[] = "\"T\/H Sensor\"";

WiFiClient wifiClient;

// Initialize DHT sensor.
DHT dht(DHTPIN, DHTTYPE);

PubSubClient client(wifiClient);

int status = WL_IDLE_STATUS;
unsigned long lastSend;

void setup()
{
  Serial.begin(115200);
  dht.begin();
  delay(10);
  InitWiFi();
  client.setServer( thingsboardServer, 1883 );
  lastSend = 0;
  Serial.print("Polling period ");
  Serial.print(poll_time);
  Serial.print(" milliseconds\n");
  if (unit_f == 1)
    {
      Serial.print("Temp to be displayed in *F\n");
    } 
  else 
    {
      Serial.print("Temp to be displayed in *C\n");
    }
 
}

void loop()
{
  //int poll_timem = poll_time * 1000;
  if ( !client.connected() ) {
    reconnect();
  }

  if ( millis() - lastSend > poll_time ) { // Update and send only after 1 seconds
    getAndSendTemperatureAndHumidityData();
    lastSend = millis();
  }

  client.loop();
}

void getAndSendTemperatureAndHumidityData()
{
 //String attr = "{\"name\":\"test\",\"foo\":1351824120}";  
  
  Serial.println("\nCollecting temperature and humidity data.");

  // Reading temperature or humidity takes about 250 milliseconds!
  float h = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  if (unit_f == 1)
      {
        t = ((int)round(1.8*t+32));
      }


  Serial.print("Humidity: ");
  Serial.print(h);
  Serial.print(" %\t");
  Serial.print("Temperature: ");
  Serial.print(t);
  Serial.print(" *F ");
  Serial.print("\n");

  String temperature = String(t);
  String humidity = String(h);


  // Just debug messages
  Serial.print( "Sending telemetry and attributes :\n" );


  // Prepare a JSON message string for telemetry data
  String message = "{";
  message += temp_label; message += ":"; message += temperature; message += ",";
  message += humidity_label; message += ":"; message += humidity;
  message += "}\n";

  // Prepare a JSON message string for attribute data
  String attr = "{";
  attr += "\"name\": "; attr += a_name; attr += ",";
  attr += "\"pur\": "; attr += a_purpose; attr += ",";
  attr += "\"sn\": "; attr += a_serialno; attr += ",";
  attr += "\"plat\": "; attr += a_platform;
  attr += "}\n"; 


  // Send messages
  char attributes[90];
  char telemetry[90];
  message.toCharArray( telemetry, 90 );
  attr.toCharArray( attributes, 90 );
  
  // Help debug managing payload size limitations
  Serial.print("Attr payload length: ");
  Serial.print(attr.length());
  Serial.print("\n");
  Serial.print("Message payload size: ");
  Serial.print(message.length());
  Serial.print("\n");
  Serial.print("Telemetry -> ");
  Serial.print( telemetry );
  Serial.print("Attributes -> ");
  Serial.print( attributes );
  Serial.print("\n");

  // Make sure that the telemetry and attribute data fits limitations, and if so, publish
  if (attr.length() > 90 )
      {
        Serial.print("\n** Attribute payload exceeds 90 bytes (");
        Serial.print(attr.length());
        Serial.print(") and will not be transmitted.  Check JSON output and shorten as necessary\n\n");
      } else {
        client.publish( "v1/devices/me/attributes", attributes );
      }
  if (message.length() > 90 )
      {
        Serial.print("\n** Telemetry payload exceeds 90 bytes (");
        Serial.print(message.length());
        Serial.print(") and will not be transmitted.  Check JSON output and shorten as necessary\n\n");
      } else {
          client.publish( "v1/devices/me/telemetry", telemetry );
      }
}

void InitWiFi()
{
  Serial.println("Connecting to AP ...");
  // attempt to connect to WiFi network

  WiFi.begin(WIFI_AP, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Connected to AP");
}


void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    status = WiFi.status();
    if ( status != WL_CONNECTED) {
      WiFi.begin(WIFI_AP, WIFI_PASSWORD);
      while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
      }
      Serial.println("Connected to AP");
    }
    Serial.print("Connecting to Thingsboard node ...");
    // Attempt to connect (clientId, username, password)
    if ( client.connect("ESP8266 Device", TOKEN, NULL) ) {
      Serial.println( "[DONE]" );
    } else {
      Serial.print( "[FAILED] [ rc = " );
      Serial.print( client.state() );
      Serial.println( " : retrying in 5 seconds]" );
      // Wait 5 seconds before retrying
      delay( 5000 );
    }
  }
}




