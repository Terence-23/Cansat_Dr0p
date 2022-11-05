#ifndef station_
#define station_
#ifdef GROUND
#include <RH_RF95.h>


#define RFM95_CS 8
#define RFM95_RST 4
#define RFM95_INT 3
#define RF95_FREQ 433

extern char packetBuf[RH_RF95_MAX_MESSAGE_LEN];
extern int bufLen;
extern char serialBuf[RH_RF95_MAX_MESSAGE_LEN];
extern int serialLen;

extern double Lon, Lat;
extern double dLon, dLat, dTemp, dHum;
extern uint32_t dPress;

void radioSetup();
void preparePacket();
void sendPacket();
void recvPacket();
void prepareSerial();
void sendSerial();
void recvSerial();
void decodeSerial();

#endif
#endif
