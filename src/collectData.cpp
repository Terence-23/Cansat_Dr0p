#include "collectData.h"

// BME680

Adafruit_BME680 bme(BME_CS, BME_MOSI, BME_MISO, BME_SCK);

void sensorSetup()
{
    BME_setup();
}

void BME_setup()
{
    if (!bme.begin())
    {
        Serial.println(F("Could not find a valid BME680 sensor, check wiring!"));
        while (1)
            ;
    }

    // Set up oversampling and filter initialization
    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme.setGasHeater(320, 150); // 320*C for 150 ms
}

void BME_read()
{
    // temp - celsius
    // press - Pa
    // humidity - %
    // possible altitude calculation - bme.readAltitude(SEALEVELPRESSURE_HPA) - meters
    endTime = bme.beginReading();
}

bool BME_is_reading()
{
    if (!bme.endReading())
    {

        return true;
    }
    return false;
}
