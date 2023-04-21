#ifdef GROUND
#include <station.h>

char packetBuf[RH_RF95_MAX_MESSAGE_LEN], serialBuf[RH_RF95_MAX_MESSAGE_LEN];
int packetLen = sizeof(packetBuf), serialLen = sizeof(serialBuf);
RH_RF95 rf95(RFM95_CS, RFM95_INT);
double Lon = 0, Lat = 0;

void radioSetup()
{
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

void preparePacket()
{

    char *Lon_ch = (char *)&Lon;
    char *Lat_ch = (char *)&Lat;

    strncpy(packetBuf, Lon_ch, sizeof(Lon));
    strncpy(packetBuf + sizeof(Lon), Lat_ch, sizeof(Lat));
}

void sendPacket()
{
    preparePacket();
    uint8_t *data = (uint8_t *)packetBuf;
    rf95.send(data, sizeof(data));
    rf95.waitPacketSent();
    Serial.println("Sent a reply");
}

void recvPacket()
{
    if (!rf95.available())
    {
        return;
    }
    if (rf95.recv((uint8_t *)packetBuf, (uint8_t *)&packetLen))
    {
        //   RH_RF95::printBuffer("Received: ", packetBuf, packetLen);
        Serial.print("Got: ");
        Serial.println((char *)packetBuf);
        // Serial.print("RSSI: ");
        // Serial.println(rf95.lastRssi(), DEC);

        // Send a reply
        sendPacket();
    }
    else
    {
        Serial.println("Receive failed");
    }
}

void recvSerial()
{
    Serial.readBytesUntil('\n', serialBuf, serialLen);
}

void decodeSerial()
{
    Lat = *((double *)serialBuf[0]);
    Lon = *((double *)serialBuf[sizeof(Lat)]);
}
#endif
