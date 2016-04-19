#include <ICMPPing.h>
#include <util.h>
#include <SPI.h>
#include <Ethernet.h>
#include "dht11.h"
#include <LiquidCrystal.h>
#define DHTPIN 8    
dht11 dht;
int tempSoglia=20;
//LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
// 10-13 are used by Ethernet
LiquidCrystal lcd(9, 6, 5, 4, 3, 2);
const int relay = 7;
byte mac[] = { 0x90, 0xA2, 0xDA, 0x00, 0x23, 0x5D }; 
byte ip[] = { 130, 192, 140, 199 };
char Data_RX;
//Server ArduinoServer(80);
void setup() {
    Serial.begin(9600);
    lcd.begin(16, 2);
    pinMode(relay,OUTPUT);
    int lcdp = lcd.print("Setup");
    //inizializza lo shield con il mac e l’ip
    Ethernet.begin(mac, ip);
    //inizializza l’oggetto server
    //ArduinoServer.begin();
}

void loop() {
    int lcdp = lcd.print("Loop");
    Serial.println("loop");
    Serial.println(lcdp);
    dht.read(DHTPIN);
    //float h = dht.readHumidity();
    //float t = dht.readTemperature();
    float h = dht.humidity;
    float t = dht.temperature;
    if (isnan(t) || isnan(h)) {
      Serial.println("Failed to read from DHT");
    } else {
      lcd.setCursor(0,0);
      lcd.print("Temp=");
      lcd.print(t);
      lcd.print(" *C");
      lcd.setCursor(0,1);
      lcd.print("Humidity=");
      lcd.print(h);
      lcd.print("% ");
      Serial.println("PRe if");
      if(t > tempSoglia) {
        Serial.println("if 1");
        digitalWrite(relay, HIGH);
      } else {
        Serial.println("else");
        digitalWrite(relay, LOW);
      }
      delay(5000);
   }
}


