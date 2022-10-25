#include "collectData.h"
#include "CanComm.h"
#include <Arduino.h>

void setup()
{
    Serial.begin(115200);
    radioSetup();
    Serial.println("SENSOR");
    sensorSetup();
    Serial.println("Ready to go");

}

void loop()
{
    GNRMC GPS1 = GPS_read();
    Serial.print("\nGPS status:"); Serial.println(GPS1.Status);
    Serial.printf("Lat: %G, Lon: %G\n", GPS1.Lat, GPS1.Lon);
}
