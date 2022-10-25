#include "collectData.h"

// BME680

Adafruit_BME680 bme(BME_CS, BME_MOSI, BME_MISO, BME_SCK);

void sensorSetup()
{
    // BME_setup();
    Serial1.println("GPS");
    GPS_setup();
}

void GPS_setup(){
    Serial.begin(9600);
    Serial.print("aaa");
    DEV_Set_Baudrate(115200);
    L76X_Send_Command(SET_NMEA_OUTPUT);
    L76X_Send_Command(SET_NMEA_BAUDRATE_9600);
    DEV_Delay_ms(500);

    // L76X_Send_Command(9600);
    DEV_Set_Baudrate(9600);
    DEV_Delay_ms(500);
    L76X_Send_Command(SET_NMEA_OUTPUT);
    Serial.println("GPS ready");
}

GNRMC GPS_read(){
    // Serial.print("GPS");
    return L76X_Gat_GNRMC();
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
