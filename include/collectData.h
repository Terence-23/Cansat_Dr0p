

// BME680
#ifndef collectData_

#define collectData_
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_Sensor.h>
#include "Adafruit_BME680.h"
#include "L76X.h"

// FIXME after deciding proper pin numbers, change data accordingly
#define BME_MOSI -1
#define BME_MISO -1
#define BME_SCK -1
#define BME_CS -1

extern Adafruit_BME680 bme;
extern unsigned long endTime;
// GPS Serial connected on pins 0, 1
extern GNRMC GPS;

#define SEALEVELPRESSURE_HPA (1013.25)

void sensorSetup();

void GPS_setup();

GNRMC GPS_read();

void BME_setup();

void BME_read();

bool BME_is_reading();

#endif
