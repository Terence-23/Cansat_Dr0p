#ifdef CANSAT
#include "CanComm.h"

char packetBuf[RH_RF95_MAX_MESSAGE_LEN];
uint8_t len = sizeof(packetBuf);
RH_RF95 rf95(RFM95_CS, RFM95_INT);
String fName = "";
File myFile;

void commsSetup()
{
    radioSetup();
    sDSetup();
}

void radioSetup()
{
    pinMode(SD_CS, OUTPUT);
    digitalWrite(SD_CS, 1);
    pinMode(RFM95_RST, OUTPUT);
    digitalWrite(RFM95_RST, HIGH);

    while (!Serial)
    {
        delay(1);
    }

    delay(100);

    Serial.println("Feather LoRa TX Test!");

    // manual reset
    digitalWrite(RFM95_RST, LOW);
    delay(10);
    digitalWrite(RFM95_RST, HIGH);
    delay(10);

    while (!rf95.init())
    {
        Serial.println("LoRa radio init failed");
        Serial.println("Uncomment '#define SERIAL_DEBUG' in RH_RF95.cpp for detailed debug info");
        while (1)
            ;
    }
    Serial.println("LoRa radio init OK!");

    // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
    if (!rf95.setFrequency(RF95_FREQ))
    {
        Serial.println("setFrequency failed");
        while (1)
            ;
    }
    Serial.print("Set Freq to: ");
    Serial.println(RF95_FREQ);

    // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on

    // The default transmitter power is 13dBm, using PA_BOOST.
    // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then
    // you can set transmitter powers from 5 to 23 dBm:
    rf95.setTxPower(20, false);
}

void sDSetup()
{
    // if(root.isOpen()) root.close();
    int a = 0;
    try
    {
        SD.end();
        while (!SD.begin(SD_CS))
        {
            Serial.println(F("SD CARD FAILED, OR NOT PRESENT!"));
            Serial.println(a);
            ++a;
            // while (1); // don't do anything more:
            // delay(1000);
        }
        Serial.println("SD ready");
    }
    catch (const char *exc)
    {
        Serial.println(exc);
    }
    int i = 0;

    char fTmp[13] = "log";
    itoa(i, fTmp + 3, 10);

    while (SD.exists(fTmp))
    {
        itoa(i, fTmp + 3, 10);
        ++i;
    }
    fName = fTmp;
}

void preparePacket(float temp, int32_t press, float humidity)
{

    // 250 bytes
    char buf[RH_RF95_MAX_MESSAGE_LEN];

    buf[0] = '1';
    // temp(f), press(i32), humidity(f), GPS_lon, GPS_lat;

    // char tempbuf[4]
    char *tempbuf = (char *)(&temp);
    char *pressbuf = (char *)(&press);
    char *humiditybuf = (char *)(&humidity);

    for (int i = 0; i < 4; ++i)
    {
        buf[1 + i] = tempbuf[i];
    }
    for (int i = 0; i < 4; ++i)
    {
        buf[5 + i] = pressbuf[i];
    }
    for (int i = 0; i < 4; ++i)
    {
        buf[9 + i] = humiditybuf[i];
    }

    strcpy(packetBuf, buf);
}

void writeSDPacket()
{

    myFile = SD.open("arduino.txt", FILE_WRITE);
    myFile.println(packetBuf);
    myFile.close();
}

void sendPacket()
{
    rf95.send((uint8_t *)packetBuf, 20);

    //   Serial.println("Waiting for packet to complete...");
    delay(10);
    rf95.waitPacketSent();

    if (rf95.waitAvailableTimeout(500))
    {
        // Should be a reply message for us now
        if (rf95.recv(recvBuf, &len))
        {
            Serial.print("Got reply: ");
            Serial.println((char *)recvBuf);
            Serial.print("RSSI: ");
            Serial.println(rf95.lastRssi(), DEC);
            decode((char *)recvBuf);
        }
        else
        {
            Serial.println("Receive failed");
        }
    }
    else
    {
        Serial.println("No reply, is there a listener around?");
    }
}
void decode(char *packet)
{
    // GPS_lon, GPS_lat
    GPS_lat = *((double *)&packet[8]);
    GPS_lon = *((double *)&packet[0]);
}
#endif
