//#include <ICMPPing.h> 
// is this needed to receive ping also? I do not think so, check.
#include <util.h>
#include <SPI.h>
#include <Ethernet.h>
#include <dht11.h>
#include <LiquidCrystal.h>
#define DHTPIN 8    
#include <stdlib.h>

// Temperature sensor
dht11 dht;
const int tempSoglia = 30;
//LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
// 10-13 are used by the eth shield.
LiquidCrystal lcd(9, 6, 5, 4, 3, 2);
// pin used for the relay. Do we need it?
const int relay = 7;
// Auto-assigned ip address and mac.
byte mac[] = { 0x90, 0xA2, 0xDA, 0xEF, 0x23, 0x5D }; 
byte ip[] = { 130, 192, 147, 17 };
// Web client and server.
EthernetClient client;
// We send heartbeats and tell to send alert email to tungsteno.
//IPAddress web_server(130, 192, 147, 6);
byte web_server[] = { 130, 192, 147, 6 };

int sendMail(float ftemp)
{
    // I really do not like a busy loop so instead of a while a will skip a loop in some cases
    /*
    if (!client) {
        Ethernet.begin(mac, ip); //dns, gateway, subnet
        delay(30000);
	if (!client) {
	    return(0);
	}
    } */
    int reconnected = 0;
    int res = 0;
    if (!client.connected()) {
      client.stop();
      res = client.connect(web_server, 8000);
      reconnected = 1;
    } else {
        if (!reconnected or res) {
            // Make a HTTP POST:
            client.println("POST /TermostatinoHandler HTTP/1.1");           
            client.println("Host: 130.192.147.6"); // bad hardcoded
            client.println("Content-Type: application/x-www-form-urlencoded");
            client.println("Connection: keep-alive");
            client.println("User-Agent: Arduino/1.0");
            client.print("Content-Length: ");
            char ctemp[10]; // FIXME 
            dtostrf(ftemp, 6, 2, ctemp);
            String temp = String(ctemp);
            String post = "temp=" + temp;
            client.println(post.length());
            Serial.println(temp);
            Serial.println(post.length());
            client.println();
            client.print(post);
            client.println();                                           
            // http://forum.arduino.cc/index.php?topic=155218.0
            //client.flush();
            //client.stop();
            return(1);
        } else {
            // if you didn't get a connection to the server:
            Serial.println("connection with web server failed, POST");
            Serial.println(res);
            return(0);
        }
    }
}

void setup() 
{
    Serial.begin(9600);
    lcd.begin(16, 2);
    pinMode(relay, OUTPUT);
    lcd.print("Setup");
    // We connect.
    Ethernet.begin(mac, ip); //dns, gateway, subnet
    delay(30000);
}

void loop() 
{
    int chk = dht.read(DHTPIN);
    float h = dht.humidity;
    float t = dht.temperature;
    if (isnan(t) || isnan(h)) {
        Serial.println("Failed to read from DHT");
        switch (chk) {
            case DHTLIB_OK: 
                Serial.println("The sensor is misbehaving seriously"); 
                break;
            case DHTLIB_ERROR_CHECKSUM: 
                Serial.println("Checksum error"); 
                break;
            case DHTLIB_ERROR_TIMEOUT: 
                Serial.println("Time out error"); 
                break;
            default: 
                Serial.println("Unknown error"); 
                break;
        }
    } else {
        lcd.setCursor(0,0);
        lcd.print("Temp=");
        lcd.print(t);
        lcd.print(" *C");
        lcd.setCursor(0,1);
        lcd.print("Humidity=");
        lcd.print(h);
        lcd.print("% ");
        if(t > tempSoglia) {
            digitalWrite(relay, HIGH);
        } else {
            digitalWrite(relay, LOW);
        }
        int chk_m = sendMail(t);
        if (!chk_m) {
            Serial.println("Failed to send mail");
        }
    }
    // We read a value every 10 seconds.
    delay(10000);
}

