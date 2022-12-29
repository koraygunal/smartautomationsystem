////////////////////////////////////////////////////////////////////
// AUTOR: Isidro Calvo&Koray Günal
// 
// DATE: 09/12/2022

////////////////////////////////////////////////////////////////////



#include <PubSubClient.h>

#include <SPI.h>
#include <WiFiNINA.h>

#include "arduino_secrets.h" //CONFIG.H
#include <PubSubClient.h>

#include <ArduinoJson.h>

#include <Wire.h>
#include <HIH61xx.h>
#include <AsyncDelay.h>
#include <MHZ19.h>
// MHZ-19B
MHZ19 myMHZ19;
int CO2;

HIH61xx<TwoWire> hih(Wire);
AsyncDelay samplingInterval;

#define Pintxo "192.168.88.100"


#define DEBUG  //para mostrar información en el puerto serie. Comentar esta linea para no mostrar.
#define LED

int ARDUINO_ID = 3;  //Change for every Arduıno, Definir ID del arduino.
#define IP_ADDRESS IPAddress(192, 168, 88, 155)
#define ARDUINO_CLIENT "arduinoClient32"

//Direcciones IP
#define BROKER_IP Pintxo  //(arduino_secrets.h)

#define AC_LOAD 5 // For Valve
#define AC_LOAD_ACTIVAR digitalWrite(AC_LOAD, LOW) // For Valve
#define AC_LOAD_DESACTIVAR digitalWrite(AC_LOAD, HIGH) // For Valve



//Conexión WIFI
char ssid[] = SECRET_SSID;    //Wifi NAME (arduino_secrets.h)
char pass[] = SECRET_PASS;    //Wifi Password (arduino_secrets.h)
int status = WL_IDLE_STATUS;  //Wifi Status
int command1 = 1 ; //Valve command


WiFiClient mqttClient;            //client wifi
PubSubClient client(mqttClient);  //client mqtt



void reconnect()  //function for when the MQTT connection has been lost
{
  // Loop until we're connected
  while (!client.connected()) {
//intentar conectar
#ifdef DEBUG
    Serial.print("Attempting MQTT connection...");
#endif  //DEBUG
    //define MQTT client name. Example: arduinoClient1 (it has to be different for each arduino, otherwise when connecting one throws the other)
    if (client.connect(ARDUINO_CLIENT))  //if it connects.
    {
#ifdef DEBUG
      Serial.println("connected");
#endif  //DEBUG
      suscribirseTopics();
    } else {
#ifdef DEBUG
      Serial.print("failed, rc=");
      Serial.println(client.state());
#endif  //DEBUG
    }
  }
}

void setup() {
  Wire.begin();  //Init I2C manually
  hih.initialise();
  samplingInterval.start(3000, AsyncDelay::MILLIS);
  Serial.begin(9600);
  while (!Serial) continue;
  //MHZ19B -> CO2
  Serial1.begin(9600);
  myMHZ19.begin(Serial1);
  myMHZ19.autoCalibration();
  pinMode(AC_LOAD,OUTPUT);
  AC_LOAD_DESACTIVAR;
 


  //CONFIG COMMUNICATIONS
  client.setServer(BROKER_IP, 1883);  //define MQTT server (RPi)
  client.setCallback(callback);       //define what the callback function will be
  if (WiFi.status() == WL_NO_MODULE)  //if you are not connected to wifi
  {
#ifdef DEBUG
    Serial.println("Communication with WiFi module failed!");
#endif  //DEBUG
    // don't continue
    while (true)
      ;
  }
  // try to connect to Wifi network:
  while (status != WL_CONNECTED)  //if you are connected to wifi
  {
#ifdef DEBUG
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
#endif                                //DEBUG
    WiFi.config(IP_ADDRESS);          //define the ip of the arduino
    status = WiFi.begin(ssid, pass);  //connect to the indicated wifi network
#ifdef DEBUG
    printWifiStatus();
#endif  //DEBUG
  }
  //END COMMUNICATIONS
  // Led to indicate when reading
  pinMode(LED_BUILTIN, OUTPUT); // It's not so important line.We can run the programme without this line.
}

void ReadSensors(){
  // Read CO2 sensor
  // Read TMP
}

void loop() {
  if (!client.connected()) {  //if no MQTT connection -> reconnect
    reconnect();
  }
  client.loop();
  delay(10000);
  hih.read();    //Read the sensor's measurements.
  // Fetch and print the results
  //Read CO2 
  CO2 = myMHZ19.getCO2(); // Request CO2 (as ppm)
  Serial.print("CO2 (ppm): ");
  Serial.println(CO2);
  int8_t Temp;
  Temp = myMHZ19.getTemperature();// Request T (as Celsius)
  //Serial.print("Temperature (C): ");
  //Serial.println(Temp);
  //Serial.print("Relative humidity: "); 
  //Serial.print(hih.getRelHumidity() / 100.0);  //We have humidity measurements like that "1700,1800,1900" so we should divide by 100
  //Serial.println(" %");
  //Serial.print("Ambient temperature: ");
  //Serial.print(hih.getAmbientTemp() / 100.0);  //same as humidity.
  //Serial.println(" deg C");
  //Serial.print("Status: ");
  //Serial.println(hih.getStatus());
        


  
  
  StaticJsonDocument<200> doc;

  
  //doc["sensor"] = "T&H";    //Convert the measurements to json.Json provide that readable for every idle to us.
  //doc["location"] = "firstfloor"; //location information
  doc["TMP"] = hih.getAmbientTemp() / 100 ;
  doc["HUM"] = hih.getRelHumidity() / 100 ;
  doc["CO2"] = myMHZ19.getCO2();


  JsonArray temperature = doc.createNestedArray("HUM"); //Along the bottom 6 lines ; we convert the values and then add to information as json format. 
  temperature.add(hih.getRelHumidity()/ 100.0 ); // Temperature is added in here
  JsonArray humidity = doc.createNestedArray("TMP"); 
  humidity.add(hih.getAmbientTemp()/ 100.0); // Humidity is added in here
  JsonArray CO2 = doc.createNestedArray("CO2");
  CO2.add(myMHZ19.getCO2()); // CO2 is added in here
  
  serializeJson(doc, Serial);  //serializeJson() serializes a JsonDocument to create a minified JSON document, i.e. a document without spaces or line break between values.

  Serial.println();


  serializeJsonPretty(doc, Serial); //If you want a prettified JSON document, use serializeJsonPretty()
  
  char buffer[256];
  

  serializeJson(doc, buffer);

  client.publish("values/n3", buffer); // Informations is published here.
  
  


}


void callback(char* topic, byte* payload, unsigned int length) {
  //Convertir topic y payload a string
  String strTopic = topic;             //convert from char* to string
  payload[length] = '\0';              //define where the payload ends
  String strPayload = (char*)payload;  //convert from byte* to string
#ifdef DEBUG
  Serial.print("Mensaje recibido. Topic: ");
  Serial.print(strTopic);
  Serial.print("; Payload: ");
  Serial.println((char*)payload);
  if (strPayload == "OPEN WINDOW") {
    Serial.println("Window is Opening");
  } 
  else if (strPayload == "CLOSE WINDOW"){
    Serial.println("Window is closing");
    AC_LOAD_ACTIVAR;
    delay(5000);
    AC_LOAD_DESACTIVAR;
    delay(5000);
    //Here the function measure and send should be called
    
    

    //THE LOGIC OF THIS PART WHEN TEMPERATURE WILL INCREASE , PYTHON WILL DETECT THIS DIFFERENCE OF TEMPERATURE AND THEN VIA MQTT , WILL SEND MESSAGE TO ARDUINO FOR "CLOSE WINDOW". 
  }
}
#endif  //DEBUG



void suscribirseTopics() {
  client.subscribe("open/n1");  //Subscribe to topic='open/n1' for when the RPi orders to take measures
  client.subscribe("take");  //Subscribe to topic='take' for when the RPi orders to take measures
 

}

void leerSensores() { //ReadSensors()
  Serial.println("Here should go the code to read the TMP37 sensor");
}


void printWifiStatus() {
  //show data about wifi connection (will only be done if DEBUG is defined)
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}

void blinkLed() {
  // Esta función puede utilizarse para debugado. Hace que parpadée el led en la placa Arduino.
  digitalWrite(LED_BUILTIN, HIGH);  // turn the LED on (HIGH is the voltage level)
  delay(500);                       // wait for half a second
  digitalWrite(LED_BUILTIN, LOW);   // turn the LED off by making the voltage LOW
}
