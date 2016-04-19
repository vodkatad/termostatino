#include <ICMPPing.h> 
// is this needed to receive ping also? I do not think so, check.
#include <util.h>
#include <SPI.h>
#include <Ethernet.h>
#include <dht11.h>
#include <LiquidCrystal.h>
#define DHTPIN 8    

// Temperature sensor
dht11 dht;
const int tempSoglia = 20;
//LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
// 10-13 are used by the eth shield.
LiquidCrystal lcd(9, 6, 5, 4, 3, 2);
// pin used for the relay. Do we need it?
const int relay = 7;
// Auto-assigned ip address and mac.
byte mac[] = { 0x90, 0xA2, 0xDA, 0x00, 0x23, 0x5D }; 
byte ip[] = { 130, 192, 140, 199 };
// Web client and server.
EthernetClient client;
EthernetServer server;

void setup() 
{
	Serial.begin(9600);
    lcd.begin(16, 2);
    pinMode(relay, OUTPUT);
    lcd.print("Setup");
    // We connect.
    Ethernet.begin(mac, ip); //dns, gateway, subnet
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
			int chk_m = sendMail(t);
			if (!chk_m) {
				Serial.println("Failed to send mail");
			}
      	} else {
        	digitalWrite(relay, LOW);
      	}
	//sendHeartbeat();
	// We read a value every 10 seconds.
	delay(10000);
	}
}


/* Can we use a server inside arduino or not? Having the server waiting is not an option...
int sendHeartbeat()
{
}
*/

int sendMail(temp)
{
	IPAddress web_server(130, 192, 147, 6);
	if (client.connect(server, 80)) {
		// Make a HTTP POST:
    	client.println("POST /termostatino/send_mail.php HTTP/1.1");           
	    client.println("Host: 130.192.140.199"); // bad hardcoded
    	client.println("Content-Type: application/x-www-form-urlencoded");
    	client.println("Connection: close");
	    client.println("User-Agent: Arduino/1.0");
	    client.print("Content-Length: ");
	    client.println(temp.length());
	    client.println();
	    client.print(String("temp=" + temp));
	    client.println();                                           
		// http://forum.arduino.cc/index.php?topic=155218.0
		return(1);
	} else {
		// if you didn't get a connection to the server:
   		Serial.println("connection with web server failed");
		return(0);
  }
}
