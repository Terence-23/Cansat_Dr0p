#include "collectData.h"
#include "CanComm.h"
#include <Arduino.h>

void setup()
{
    Serial.begin(115200);
    radioSetup();
    sensorSetup();

}

void loop()
{

}
