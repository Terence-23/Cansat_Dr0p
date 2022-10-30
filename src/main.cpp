#include <Arduino.h>


// #define CANSAT
#define GROUND
// #define CLEAR

#ifdef CANSAT
#include "collectData.h"
#include "CanComm.h"
#include <stdio.h>


void GPS_out(){

    GNRMC GPS1 = GPS_read();
    // char* text = (char*)malloc(30);
    Serial.print("\nGPS status:"); Serial.println(GPS1.Status);
    // Serial.printf("Lat: %G, Lon: %G\n", GPS1.Lat, GPS1.Lon);
    Serial.print("Lat: "); Serial.print(GPS1.Lat, 5); Serial.print(" Lon: "); Serial.println(GPS1.Lon, 5);

}

void SDTest(){
    preparePacket(22.3, 1013, 60);
    writeSDPacket();
}

void setup()
{
    Serial.begin(115200);
    commsSetup();
    Serial.println("SENSOR");
    sensorSetup();
    Serial.println("Ready to go");

}

void loop()
{
    // GPS_out();
    SDTest();
    delay(100);
}
#endif
#ifdef GROUND
#include <station.h>

    void setup(){
        Serial.begin(115200);
        radioSetup();


    }
    void loop(){

    }

#endif
#ifdef CLEAR
    
    void setup(){
        Serial.begin(115200);
        Serial.println("Clear build");
        Serial.end();
    }
    void loop(){
        delay(1000000);
    }

#endif
